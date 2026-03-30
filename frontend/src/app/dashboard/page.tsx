"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, ChevronDown, ChevronUp, CheckCircle2, Circle, Upload } from "lucide-react";
import AppShell from "@/components/AppShell";
import HealthScore from "@/components/HealthScore";
import InsightBanner from "@/components/InsightBanner";
import JourneyProgress from "@/components/JourneyProgress";
import PrivacyBanner from "@/components/PrivacyBanner";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";
import { formatDate, cn } from "@/lib/utils";

interface ScoreData {
  overall_score: number;
  grade: string;
}

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

const journeyStepsDefault = [
  { label: "Onboarded", completed: false },
  { label: "First Insights", completed: false },
  { label: "First Report", completed: false },
  { label: "7-Day Streak", completed: false },
  { label: "Plan Created", completed: false },
];

export default function DashboardPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [scoreData, setScoreData] = useState<ScoreData | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [reports, setReports] = useState<Report[]>([]);
  const [todayAction, setTodayAction] = useState<ActionItem | null>(null);
  const [actionDone, setActionDone] = useState(false);
  const [insightsExpanded, setInsightsExpanded] = useState(false);
  const [journeySteps, setJourneySteps] = useState(journeyStepsDefault);
  const [loading, setLoading] = useState(true);

  // Get user ID
  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      if (data.user) {
        setUserId(data.user.id);
      }
    });
  }, []);

  // Fetch data when userId is available
  useEffect(() => {
    if (!userId) return;

    async function fetchData() {
      setLoading(true);

      // Fetch all data in parallel, handle failures gracefully
      const [scoreRes, insightsRes, reportsRes] = await Promise.allSettled([
        apiFetch<ScoreData>(`/api/score?user_id=${userId}`),
        apiFetch<Insight[]>(`/api/insights?user_id=${userId}`),
        apiFetch<Report[]>(`/api/reports?user_id=${userId}`),
      ]);

      if (scoreRes.status === "fulfilled") {
        setScoreData(scoreRes.value);
      }

      if (insightsRes.status === "fulfilled" && Array.isArray(insightsRes.value)) {
        setInsights(insightsRes.value);
      } else {
        // Placeholder insights when endpoint is not ready
        setInsights([
          {
            id: "placeholder-1",
            title: "Insights coming soon",
            body: "Upload a health report to get personalized insights powered by AI.",
            severity: "info",
          },
        ]);
      }

      if (reportsRes.status === "fulfilled" && Array.isArray(reportsRes.value)) {
        setReports(reportsRes.value);
      }

      // Derive journey progress
      const hasReports =
        reportsRes.status === "fulfilled" &&
        Array.isArray(reportsRes.value) &&
        reportsRes.value.length > 0;
      const hasInsights =
        insightsRes.status === "fulfilled" &&
        Array.isArray(insightsRes.value) &&
        insightsRes.value.length > 0;
      const hasScore = scoreRes.status === "fulfilled";

      setJourneySteps([
        { label: "Onboarded", completed: true },
        { label: "First Insights", completed: hasInsights },
        { label: "First Report", completed: hasReports },
        { label: "7-Day Streak", completed: false },
        { label: "Plan Created", completed: false },
      ]);

      setLoading(false);
    }

    fetchData();
  }, [userId]);

  const primaryInsight = insights[0] || null;
  const additionalInsights = insights.slice(1);

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Privacy Banner */}
        <PrivacyBanner />

        {/* Health Score Ring */}
        <section className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 flex flex-col items-center">
          {scoreData ? (
            <HealthScore
              score={scoreData.overall_score}
              grade={scoreData.grade}
              size="lg"
            />
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
      </div>
    </AppShell>
  );
}
