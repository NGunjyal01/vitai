"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, ChevronDown, ChevronUp, CheckCircle2, Circle, Upload } from "lucide-react";
import AppShell from "@/components/AppShell";
import HealthScore from "@/components/HealthScore";
import InsightBanner from "@/components/InsightBanner";
import JourneyProgress from "@/components/JourneyProgress";
import PrivacyBanner from "@/components/PrivacyBanner";
import { useUserId, useScore, useInsights, useReports, useProfile } from "@/lib/hooks";
import { formatDate, cn } from "@/lib/utils";

interface Insight {
  id: string;
  title: string;
  body: string;
  severity: "info" | "warning" | "urgent";
  action?: string;
}

interface Report {
  id: string;
  file_name: string;
  report_type: string;
  status: string;
  created_at: string;
}

interface ActionItem {
  id: string;
  text: string;
  completed: boolean;
}

export default function DashboardPage() {
  const userId = useUserId();
  const { data: scoreData, isLoading: scoreLoading } = useScore(userId);
  const { data: insightsRaw, isLoading: insightsLoading } = useInsights(userId);
  const { data: reportsRaw, isLoading: reportsLoading } = useReports(userId);
  const { data: profile } = useProfile(userId);

  const [todayAction] = useState<ActionItem | null>(null);
  const [actionDone, setActionDone] = useState(false);
  const [insightsExpanded, setInsightsExpanded] = useState(false);

  const loading = scoreLoading || insightsLoading || reportsLoading;

  // Normalise data with fallbacks
  const insights: Insight[] = Array.isArray(insightsRaw)
    ? insightsRaw
    : [
        {
          id: "placeholder-1",
          title: "Insights coming soon",
          body: "Upload a health report to get personalized insights powered by AI.",
          severity: "info" as const,
        },
      ];
  const reports: Report[] = Array.isArray(reportsRaw) ? reportsRaw : [];

  // Derive journey progress
  const journeySteps = [
    { label: "Onboarded", completed: profile?.onboarding_completed === true },
    { label: "First Report", completed: reports.length > 0 },
    { label: "First Insights", completed: Array.isArray(insightsRaw) && insightsRaw.length > 0 },
    { label: "7-Day Streak", completed: false },
    { label: "Plan Created", completed: false },
  ];

  const primaryInsight = insights[0] || null;
  const additionalInsights = insights.slice(1);

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Privacy Banner */}
        <PrivacyBanner />

        {/* Health Score Ring */}
        <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 flex flex-col items-center">
          {loading ? (
            <div className="flex flex-col items-center w-full animate-pulse">
              <div className="w-[200px] h-[200px] rounded-full bg-gray-200 dark:bg-gray-700 mb-4" />
              <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
              <div className="h-3 w-48 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
          ) : scoreData && scoreData.categories_assessed > 0 ? (
            <>
              <HealthScore
                score={scoreData.total_score}
                grade={scoreData.grade}
                size="lg"
              />
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {scoreData.categories_assessed} of {scoreData.total_categories ?? 11} categories assessed
              </p>
            </>
          ) : (
            <div className="flex flex-col items-center py-8 text-center">
              <div className="w-24 h-24 rounded-full border-4 border-dashed border-gray-300 dark:border-gray-600 flex items-center justify-center mb-4">
                <Upload className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-500 dark:text-gray-400 text-sm">
                Upload a report to see your health score
              </p>
              <Link
                href="/reports"
                className="mt-3 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:underline"
              >
                Upload your first report
              </Link>
            </div>
          )}
        </section>

        {/* Loading skeletons for cards */}
        {loading && (
          <div className="space-y-6 animate-pulse">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
              <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
              <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded" />
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
              <div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded mb-3" />
              <div className="space-y-2">
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
              </div>
            </div>
          </div>
        )}

        {!loading && (<>
        {/* Insights Section */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold">Insights</h2>
          {primaryInsight && (
            <InsightBanner
              title={primaryInsight.title}
              body={primaryInsight.body}
              severity={primaryInsight.severity}
              action={primaryInsight.action}
            />
          )}

          {additionalInsights.length > 0 && (
            <>
              <button
                onClick={() => setInsightsExpanded(!insightsExpanded)}
                className="flex items-center gap-1 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:underline"
              >
                {insightsExpanded ? (
                  <>
                    Hide insights
                    <ChevronUp className="w-4 h-4" />
                  </>
                ) : (
                  <>
                    See {additionalInsights.length} more insight
                    {additionalInsights.length > 1 ? "s" : ""}
                    <ChevronDown className="w-4 h-4" />
                  </>
                )}
              </button>

              {insightsExpanded && (
                <div className="space-y-3">
                  {additionalInsights.map((insight) => (
                    <InsightBanner
                      key={insight.id}
                      title={insight.title}
                      body={insight.body}
                      severity={insight.severity}
                      action={insight.action}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </section>

        {/* Today's Action Card */}
        <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
          <h2 className="text-base font-semibold mb-3">Today&apos;s Action</h2>
          {todayAction ? (
            <button
              onClick={() => setActionDone(!actionDone)}
              className="flex items-center gap-3 w-full text-left"
            >
              {actionDone ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-gray-400 shrink-0" />
              )}
              <span
                className={cn(
                  "text-sm",
                  actionDone && "line-through text-gray-400"
                )}
              >
                {todayAction.text}
              </span>
            </button>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No action plan yet.
              </p>
              <Link
                href="/coach"
                className="mt-2 inline-block text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:underline"
              >
                Chat with your coach to create a plan
              </Link>
            </div>
          )}
        </section>

        {/* Reports Timeline */}
        <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold">Reports</h2>
            <Link
              href="/reports"
              className="w-8 h-8 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white flex items-center justify-center transition-colors"
              aria-label="Upload new report"
            >
              <Plus className="w-4 h-4" />
            </Link>
          </div>

          {reports.length > 0 ? (
            <div className="space-y-3">
              {reports.slice(0, 5).map((report) => (
                <div
                  key={report.id}
                  className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">
                      {report.file_name || report.report_type || "Report"}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDate(report.created_at)}
                    </p>
                  </div>
                  <span
                    className={cn(
                      "text-xs font-medium px-2 py-0.5 rounded-full capitalize",
                      report.status === "processed"
                        ? "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400"
                        : report.status === "processing"
                        ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400"
                        : report.status === "failed"
                        ? "bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400"
                        : "bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                    )}
                  >
                    {report.status}
                  </span>
                </div>
              ))}

              {reports.length > 5 && (
                <Link
                  href="/reports"
                  className="block text-center text-sm text-emerald-600 dark:text-emerald-400 hover:underline pt-2"
                >
                  View all {reports.length} reports
                </Link>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
              No reports yet. Upload your first report to get started.
            </p>
          )}
        </section>

        {/* Journey Progress Bar */}
        <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
          <h2 className="text-base font-semibold mb-2">Your Journey</h2>
          <JourneyProgress steps={journeySteps} />
        </section>
        </>)}
      </div>
    </AppShell>
  );
}
