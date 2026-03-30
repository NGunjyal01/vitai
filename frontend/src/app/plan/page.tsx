"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface PlanItem {
  key: string;
  text: string;
  completed: boolean;
}

interface CategoryItems {
  diet: PlanItem[];
  exercise: PlanItem[];
  lifestyle: PlanItem[];
  supplements: PlanItem[];
  retest: PlanItem[];
}

interface Plan {
  id: string;
  plan_data: any;
  retest_target_date: string | null;
  created_at: string;
  completions?: string[];
}

const CATEGORY_META: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  diet: {
    label: "Diet",
    icon: "M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25",
    color: "text-orange-500",
  },
  exercise: {
    label: "Exercise",
    icon: "M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z",
    color: "text-blue-500",
  },
  lifestyle: {
    label: "Lifestyle",
    icon: "M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z",
    color: "text-pink-500",
  },
  supplements: {
    label: "Supplements",
    icon: "M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5",
    color: "text-green-500",
  },
  retest: {
    label: "Retest",
    icon: "M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3",
    color: "text-purple-500",
  },
};

function parsePlanData(planData: any, completions: string[]): CategoryItems {
  const categories: CategoryItems = {
    diet: [],
    exercise: [],
    lifestyle: [],
    supplements: [],
    retest: [],
  };

  if (!planData) return categories;

  // Handle plan_data as either an object with category keys or a flat structure
  const data = typeof planData === "string" ? JSON.parse(planData) : planData;

  for (const catKey of Object.keys(categories) as (keyof CategoryItems)[]) {
    const items = data[catKey];
    if (Array.isArray(items)) {
      categories[catKey] = items.map((item: any, idx: number) => {
        const text = typeof item === "string" ? item : item.text || item.description || JSON.stringify(item);
        const key = `${catKey}_${idx}`;
        return {
          key,
          text,
          completed: completions.includes(key),
        };
      });
    }
  }

  return categories;
}

export default function PlanPage() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(true);
  const [noPlan, setNoPlan] = useState(false);
  const [toggling, setToggling] = useState<string | null>(null);
  const [completions, setCompletions] = useState<string[]>([]);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) return;
      setUserId(user.id);

      try {
        const data = await apiFetch<any>(
          `/api/plan?user_id=${user.id}`
        );
        if (!data || data.error) {
          setNoPlan(true);
        } else {
          setPlan(data);
          setCompletions(data.completions || []);
        }
      } catch {
        setNoPlan(true);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleToggle = async (itemKey: string) => {
    if (!plan || !userId || toggling) return;
    setToggling(itemKey);

    try {
      await apiFetch("/api/plan/complete", {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          plan_id: plan.id,
          item_key: itemKey,
        }),
      });
      setCompletions((prev) =>
        prev.includes(itemKey)
          ? prev.filter((k) => k !== itemKey)
          : [...prev, itemKey]
      );
    } catch (err) {
      console.error("Failed to toggle plan item:", err);
    } finally {
      setToggling(null);
    }
  };

  const categories = plan
    ? parsePlanData(plan.plan_data, completions)
    : null;

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && noPlan && (
          <div className="text-center py-20">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-emerald-600 dark:text-emerald-400"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 3h-3a2.25 2.25 0 00-2.15 1.586m0 0A48.41 48.41 0 006.226 3.916"
                />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              No plan yet
            </h2>
            <p className="text-gray-500 dark:text-gray-400 mt-2 mb-6 max-w-sm mx-auto">
              Chat with your coach to generate a personalized health plan based
              on your lab results.
            </p>
            <Link
              href="/coach"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
                />
              </svg>
              Talk to Coach
            </Link>
          </div>
        )}

        {!loading && plan && categories && (
          <>
            {/* Retest date banner */}
            {plan.retest_target_date && (
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-4 flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/40 flex items-center justify-center flex-shrink-0">
                  <svg
                    className="w-5 h-5 text-purple-600 dark:text-purple-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"
                    />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-purple-800 dark:text-purple-200">
                    Retest Target
                  </p>
                  <p className="text-lg font-bold text-purple-900 dark:text-purple-100">
                    {formatDate(plan.retest_target_date)}
                  </p>
                </div>
              </div>
            )}

            {/* Category sections */}
            {(
              Object.keys(CATEGORY_META) as (keyof CategoryItems)[]
            ).map((catKey) => {
              const items = categories[catKey];
              if (!items || items.length === 0) return null;
              const meta = CATEGORY_META[catKey];

              return (
                <div
                  key={catKey}
                  className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden"
                >
                  <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center gap-3">
                    <svg
                      className={`w-5 h-5 ${meta.color}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d={meta.icon}
                      />
                    </svg>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {meta.label}
                    </h3>
                    <span className="ml-auto text-xs text-gray-400">
                      {items.filter((i) => i.completed).length}/{items.length}
                    </span>
                  </div>

                  <ul className="divide-y divide-gray-100 dark:divide-gray-800">
                    {items.map((item) => (
                      <li key={item.key} className="px-5 py-3 flex items-start gap-3">
                        <button
                          onClick={() => handleToggle(item.key)}
                          disabled={toggling === item.key}
                          className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                            item.completed
                              ? "bg-emerald-500 border-emerald-500"
                              : "border-gray-300 dark:border-gray-600 hover:border-emerald-400"
                          }`}
                        >
                          {item.completed && (
                            <svg
                              className="w-3 h-3 text-white"
                              fill="none"
                              viewBox="0 0 24 24"
                              strokeWidth={3}
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M4.5 12.75l6 6 9-13.5"
                              />
                            </svg>
                          )}
                        </button>
                        <span
                          className={`text-sm ${
                            item.completed
                              ? "line-through text-gray-400 dark:text-gray-500"
                              : "text-gray-700 dark:text-gray-300"
                          }`}
                        >
                          {item.text}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}

            {/* Plan creation date */}
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 pb-4">
              Plan created {formatDate(plan.created_at)}
            </p>
          </>
        )}
      </div>
    </AppShell>
  );
}
