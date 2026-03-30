"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import HealthScore from "@/components/HealthScore";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface CategoryScore {
  label: string;
  color: string;
  score: number | null;
  assessed: boolean;
  parameters: any[];
}

interface ScoreData {
  total_score: number;
  base_score: number;
  lifestyle_modifier: number;
  grade: string;
  categories_assessed: number;
  total_categories: number;
  category_scores: Record<string, CategoryScore>;
  calculated_at: string;
}

interface ScoreHistory {
  total_score: number;
  calculated_at: string;
  grade: string;
}

const IMPROVEMENT_TIPS: Record<string, string[]> = {
  metabolic_health: [
    "Reduce refined carbohydrate and sugar intake",
    "Include more fiber-rich foods like vegetables, legumes, and whole grains",
    "Regular walking after meals helps regulate blood sugar",
  ],
  heart_health: [
    "Increase omega-3 rich foods (fish, flaxseed, walnuts)",
    "Reduce saturated fat and processed food consumption",
    "Aim for 150 minutes of moderate cardio per week",
  ],
  blood_health: [
    "Include iron-rich foods like spinach, lentils, and lean meats",
    "Pair iron-rich foods with vitamin C for better absorption",
    "Consider B12 supplementation if vegetarian/vegan",
  ],
  thyroid_function: [
    "Ensure adequate iodine and selenium intake",
    "Manage stress levels as cortisol affects thyroid function",
    "Avoid excessive consumption of raw cruciferous vegetables",
  ],
  kidney_function: [
    "Stay well hydrated throughout the day",
    "Moderate protein intake to reduce kidney strain",
    "Monitor blood pressure regularly",
  ],
  liver_function: [
    "Minimize alcohol consumption",
    "Include liver-supportive foods like garlic, turmeric, and leafy greens",
    "Maintain a healthy weight to reduce fatty liver risk",
  ],
  vitamins: [
    "Get 15-20 minutes of sunlight daily for vitamin D",
    "Include diverse fruits and vegetables for micronutrient coverage",
    "Consider targeted supplementation based on deficiencies",
  ],
  electrolytes: [
    "Stay hydrated with water and electrolyte-rich fluids",
    "Include potassium-rich foods like bananas and sweet potatoes",
    "Moderate sodium intake",
  ],
  inflammation: [
    "Increase anti-inflammatory foods: berries, fatty fish, turmeric",
    "Prioritize quality sleep (7-9 hours)",
    "Regular moderate exercise reduces chronic inflammation",
  ],
  hormones: [
    "Prioritize sleep quality and duration",
    "Manage stress through meditation or breathing exercises",
    "Strength training helps maintain healthy hormone levels",
  ],
  muscle_recovery: [
    "Ensure adequate protein intake after workouts",
    "Allow proper rest days between intense training",
    "Stay hydrated and include magnesium-rich foods",
  ],
};

export default function ScorePage() {
  const [scoreData, setScoreData] = useState<ScoreData | null>(null);
  const [scoreHistory, setScoreHistory] = useState<ScoreHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) return;

      try {
        const data = await apiFetch<ScoreData>(
          `/api/score?user_id=${user.id}`
        );
        setScoreData(data);

        // Also load score history
        try {
          const history = await apiFetch<ScoreHistory[]>(
            `/api/score/history?user_id=${user.id}&limit=10`
          );
          setScoreHistory(Array.isArray(history) ? history : []);
        } catch {
          setScoreHistory([]);
        }
      } catch {
        setScoreData(null);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Deduplicate score history by date (keep latest entry per date)
  const uniqueHistory = scoreHistory.reduce<ScoreHistory[]>((acc, entry) => {
    const date = entry.calculated_at.split("T")[0];
    const existing = acc.find((e) => e.calculated_at.split("T")[0] === date);
    if (!existing) acc.push(entry);
    return acc;
  }, []);
  const showHistory = uniqueHistory.length >= 2;

  // Sort categories: assessed first (by score ascending), then unassessed
  const sortedCategories = scoreData
    ? Object.entries(scoreData.category_scores).sort((a, b) => {
        const aAssessed = a[1].assessed && a[1].score !== null;
        const bAssessed = b[1].assessed && b[1].score !== null;
        if (aAssessed && !bAssessed) return -1;
        if (!aAssessed && bAssessed) return 1;
        if (aAssessed && bAssessed) return (a[1].score ?? 0) - (b[1].score ?? 0);
        return 0;
      })
    : [];

  // Find the lowest-scored assessed categories for tips
  const lowestCategories = scoreData
    ? Object.entries(scoreData.category_scores)
        .filter(([, cat]) => cat.assessed && cat.score !== null)
        .sort((a, b) => (a[1].score ?? 0) - (b[1].score ?? 0))
        .slice(0, 3)
        .filter(([, cat]) => (cat.score ?? 0) < 80)
    : [];

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && !scoreData && (
          <div className="text-center py-20">
            <p className="text-gray-500 dark:text-gray-400">
              No health score available yet. Upload a report or enter your
              health data to get started.
            </p>
          </div>
        )}

        {!loading && scoreData && (
          <>
            {/* Health Score Header */}
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">Health Score</h1>

            {/* Score Ring */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 flex flex-col items-center">
              <HealthScore
                score={scoreData.total_score}
                grade={scoreData.grade}
                size="lg"
              />
              <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                <span>
                  Base: <strong className="text-gray-700 dark:text-gray-300">{scoreData.base_score}</strong>
                </span>
                <span>
                  Lifestyle:{" "}
                  <strong
                    className={
                      scoreData.lifestyle_modifier >= 0
                        ? "text-green-600"
                        : "text-red-600"
                    }
                  >
                    {scoreData.lifestyle_modifier >= 0 ? "+" : ""}
                    {scoreData.lifestyle_modifier}
                  </strong>
                </span>
                <span>
                  {scoreData.categories_assessed}/{scoreData.total_categories}{" "}
                  categories
                </span>
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Category Breakdown
              </h3>
              <div className="space-y-2">
                {sortedCategories.map(
                  ([key, cat]) => {
                    const scoreBg =
                      cat.assessed && cat.score !== null
                        ? cat.score >= 80
                          ? "bg-green-50 dark:bg-green-900/10"
                          : cat.score >= 60
                          ? "bg-amber-50 dark:bg-amber-900/10"
                          : "bg-red-50 dark:bg-red-900/10"
                        : "";
                    return (
                    <div key={key} className={`flex items-center gap-3 rounded-lg px-3 py-2 ${scoreBg}`}>
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: cat.color }}
                      />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-28 sm:w-40 flex-shrink-0 truncate">
                        {cat.label}
                      </span>
                      {cat.assessed && cat.score !== null ? (
                        <div className="flex-1 flex items-center gap-3">
                          <div className="flex-1 h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${cat.score}%`,
                                backgroundColor: cat.color,
                              }}
                            />
                          </div>
                          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100 w-16 text-right">
                            {cat.score}/100
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400 dark:text-gray-500 italic">
                          Not assessed
                        </span>
                      )}
                    </div>
                    );
                  }
                )}
              </div>
            </div>

            {/* Score History */}
            {showHistory && (
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  Score History
                </h3>
                <div className="flex items-end gap-2 h-32">
                  {uniqueHistory
                    .slice()
                    .reverse()
                    .map((entry, idx) => {
                      const height = Math.max(
                        (entry.total_score / 100) * 100,
                        4
                      );
                      const barColor =
                        entry.total_score >= 80
                          ? "#22c55e"
                          : entry.total_score >= 60
                          ? "#f59e0b"
                          : "#ef4444";
                      return (
                        <div
                          key={idx}
                          className="flex-1 flex flex-col items-center gap-1"
                        >
                          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                            {entry.total_score}
                          </span>
                          <div
                            className="w-full max-w-[32px] rounded-t-md transition-all"
                            style={{
                              height: `${height}%`,
                              backgroundColor: barColor,
                            }}
                          />
                          <span className="text-[10px] text-gray-400 dark:text-gray-500">
                            {formatDate(entry.calculated_at).replace(
                              /\s\d{4}$/,
                              ""
                            )}
                          </span>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* How to Improve */}
            {lowestCategories.length > 0 && (
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  How to Improve
                </h3>
                <div className="space-y-4">
                  {lowestCategories.map(([catKey, cat]) => {
                    const tips =
                      IMPROVEMENT_TIPS[catKey] || [];
                    if (tips.length === 0) return null;
                    return (
                      <div key={catKey}>
                        <div className="flex items-center gap-2 mb-2">
                          <div
                            className="w-2.5 h-2.5 rounded-full"
                            style={{ backgroundColor: cat.color }}
                          />
                          <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                            {cat.label}{" "}
                            <span className="text-gray-400 font-normal">
                              ({cat.score}/100)
                            </span>
                          </span>
                        </div>
                        <ul className="ml-5 space-y-1">
                          {tips.map((tip, idx) => (
                            <li
                              key={idx}
                              className="text-sm text-gray-600 dark:text-gray-400 list-disc"
                            >
                              {tip}
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}