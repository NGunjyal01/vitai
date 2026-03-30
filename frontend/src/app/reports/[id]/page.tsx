"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import MetricCard from "@/components/MetricCard";
import { apiFetch } from "@/lib/api";
import { formatDate, statusColor, statusLabel } from "@/lib/utils";

interface Metric {
  name: string;
  value: number;
  unit: string;
  status: string;
  range_low: number;
  range_high: number;
  percent_of_range: number;
}

interface ReportDetail {
  id: string;
  file_name: string;
  uploaded_at: string;
  status: string;
  report_type: string;
  lab_name: string;
  metrics: Metric[];
}

export default function ReportDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reportId = params.id as string;

  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchReport() {
      try {
        const data = await apiFetch<ReportDetail>(`/api/reports/${reportId}`);
        setReport(data);
      } catch {
        setError("Failed to load report.");
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, [reportId]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center py-20">
          <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (error || !report) {
    return (
      <AppShell>
        <div className="max-w-3xl mx-auto px-4 py-6">
          <div className="text-center py-20">
            <p className="text-red-600 mb-4">{error || "Report not found"}</p>
            <button
              onClick={() => router.push("/reports")}
              className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
            >
              Back to Reports
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  function reportStatusBadge(status: string) {
    switch (status) {
      case "processed":
        return "text-emerald-700 bg-emerald-50 border-emerald-200";
      case "processing":
        return "text-amber-700 bg-amber-50 border-amber-200";
      case "failed":
        return "text-red-700 bg-red-50 border-red-200";
      default:
        return "text-gray-700 bg-gray-50 border-gray-200";
    }
  }

  // Group metrics by status for summary
  const abnormalCount = report.metrics?.filter(
    (m) => m.status !== "normal"
  ).length ?? 0;

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Back button */}
        <button
          onClick={() => router.push("/reports")}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
          Back to Reports
        </button>

        {/* Report header */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {report.file_name}
              </h1>
              <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                <span>{formatDate(report.uploaded_at)}</span>
                {report.lab_name && (
                  <>
                    <span className="text-gray-300">|</span>
                    <span>{report.lab_name}</span>
                  </>
                )}
                {report.report_type && (
                  <>
                    <span className="text-gray-300">|</span>
                    <span className="capitalize">{report.report_type}</span>
                  </>
                )}
              </div>
            </div>
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium border ${reportStatusBadge(
                report.status
              )}`}
            >
              {report.status === "processed" ? "Processed" : report.status}
            </span>
          </div>

          {/* Summary bar */}
          {report.metrics && report.metrics.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-100 flex items-center gap-4 text-sm">
              <span className="text-gray-500">
                <span className="font-semibold text-gray-900">{report.metrics.length}</span> parameters
              </span>
              {abnormalCount > 0 && (
                <span className="text-red-600">
                  <span className="font-semibold">{abnormalCount}</span> need attention
                </span>
              )}
              {abnormalCount === 0 && (
                <span className="text-emerald-600 font-medium">All normal</span>
              )}
            </div>
          )}
        </div>

        {/* Metrics grid */}
        {report.metrics && report.metrics.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {report.metrics.map((metric, i) => (
              <MetricCard
                key={i}
                name={metric.name}
                value={metric.value}
                unit={metric.unit}
                status={metric.status}
                rangeLow={metric.range_low}
                rangeHigh={metric.range_high}
                percentOfRange={metric.percent_of_range}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-10 text-gray-500 text-sm">
            {report.status === "processed"
              ? "No metrics found in this report."
              : "Report is still being processed..."}
          </div>
        )}
      </div>
    </AppShell>
  );
}
