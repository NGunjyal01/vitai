"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import ReportUpload from "@/components/ReportUpload";
import { apiFetch } from "@/lib/api";
import { supabase } from "@/lib/supabase";
import { formatDate, statusColor, statusLabel } from "@/lib/utils";

interface Report {
  id: string;
  file_name: string;
  uploaded_at: string;
  status: string;
  report_type: string;
}

export default function ReportsPage() {
  const router = useRouter();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      if (data.user) {
        setUserId(data.user.id);
        fetchReports(data.user.id);
      }
    });
  }, []);

  async function fetchReports(uid: string) {
    setLoading(true);
    try {
      const data = await apiFetch<Report[]>(`/api/reports?user_id=${uid}`);
      setReports(data);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }

  function handleUploadComplete(reportId: string) {
    setShowUpload(false);
    if (userId) fetchReports(userId);
    router.push(`/reports/${reportId}`);
  }

  function statusBadgeColor(status: string) {
    switch (status) {
      case "processed":
        return "text-emerald-700 bg-emerald-50 border-emerald-200";
      case "processing":
      case "text_extracted":
      case "analyzed":
        return "text-amber-700 bg-amber-50 border-amber-200";
      case "failed":
        return "text-red-700 bg-red-50 border-red-200";
      default:
        return "text-gray-700 bg-gray-50 border-gray-200";
    }
  }

  function statusText(status: string) {
    switch (status) {
      case "processed":
        return "Processed";
      case "processing":
        return "Processing";
      case "text_extracted":
        return "Extracting";
      case "analyzed":
        return "Analyzing";
      case "failed":
        return "Failed";
      case "uploaded":
        return "Uploaded";
      default:
        return status;
    }
  }

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
            <p className="text-sm text-gray-500 mt-1">
              Your uploaded blood test reports
            </p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className={`rounded-xl px-4 py-2.5 text-sm font-medium shadow-sm transition focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              showUpload
                ? "bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-400"
                : "bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500"
            }`}
          >
            {showUpload ? "Close" : "Upload Report"}
          </button>
        </div>

        {/* Upload area */}
        {showUpload && userId && (
          <div className="mb-6">
            <ReportUpload
              userId={userId}
              onComplete={handleUploadComplete}
              onCancel={() => {
                setShowUpload(false);
                if (userId) fetchReports(userId);
              }}
            />
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {/* Empty state */}
        {!loading && reports.length === 0 && (
          <div className="text-center py-20">
            <svg
              className="w-16 h-16 mx-auto text-gray-300 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-gray-700 mb-1">
              No reports yet
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Upload your first blood test PDF to get started
            </p>
            <button
              onClick={() => setShowUpload(true)}
              className="rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-emerald-700"
            >
              Upload Your First Report
            </button>
          </div>
        )}

        {/* Report list */}
        {!loading && reports.length > 0 && (
          <div className="space-y-3">
            {reports.map((report) => (
              <button
                key={report.id}
                onClick={() => router.push(`/reports/${report.id}`)}
                className="w-full text-left bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md hover:border-emerald-200 transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center flex-shrink-0">
                      <svg
                        className="w-5 h-5 text-emerald-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                        />
                      </svg>
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate text-sm">
                        {report.file_name}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-gray-400">
                          {formatDate(report.uploaded_at)}
                        </span>
                        {report.report_type && (
                          <>
                            <span className="text-gray-300">&#183;</span>
                            <span className="text-xs text-gray-400 capitalize">
                              {report.report_type}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border flex-shrink-0 ${statusBadgeColor(
                      report.status
                    )}`}
                  >
                    {statusText(report.status)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}