"use client";

import { useState, useCallback, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { apiUpload, apiFetch } from "@/lib/api";
import { useInvalidate } from "@/lib/hooks";

interface ReportUploadProps {
  userId: string;
  onComplete: (reportId: string) => void;
  onCancel?: () => void;
}

interface ProcessingStep {
  label: string;
  status: "pending" | "active" | "done" | "error";
}

export default function ReportUpload({ userId, onComplete, onCancel }: ReportUploadProps) {
  const invalidate = useInvalidate();
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<ProcessingStep[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const currentReportId = useRef<string | null>(null);
  const cancelledRef = useRef(false);

  const updateStep = (index: number, status: ProcessingStep["status"]) => {
    setSteps((prev) =>
      prev.map((s, i) => (i === index ? { ...s, status } : s))
    );
  };

  const resetState = () => {
    setUploading(false);
    setError(null);
    setSteps([]);
    setFileName(null);
    currentReportId.current = null;
    cancelledRef.current = false;
  };

  const handleCancel = async () => {
    cancelledRef.current = true;

    // Delete the report from DB if one was created
    if (currentReportId.current) {
      try {
        await apiFetch(`/api/reports/${currentReportId.current}`, { method: "DELETE" });
        invalidate(["reports"]);
      } catch {
        // Ignore delete errors
      }
    }

    resetState();
    onCancel?.();
  };

  const pollReport = useCallback(
    async (reportId: string) => {
      const poll = async () => {
        if (cancelledRef.current) return;

        try {
          const report = await apiFetch<{ status: string; error_message?: string }>(
            `/api/reports/${reportId}`
          );

          if (cancelledRef.current) return;

          if (report.status === "text_extracted") {
            updateStep(1, "done");
            updateStep(2, "active");
          }

          if (report.status === "analyzed") {
            updateStep(2, "done");
            updateStep(3, "active");
          }

          if (report.status === "processed") {
            updateStep(2, "done");
            updateStep(3, "done");
            setUploading(false);
            invalidate(["reports", "score"]);
            onComplete(reportId);
            return;
          }

          if (report.status === "failed") {
            updateStep(
              steps.findIndex((s) => s.status === "active"),
              "error"
            );
            const errorMsg = report.error_message || "";
            const isRateLimit = errorMsg.includes("429") || errorMsg.includes("Too Many Requests") || errorMsg.includes("rate");
            setError(
              isRateLimit
                ? "AI service is rate-limited. Please wait 1-2 minutes and try uploading again."
                : "Processing failed. Please try again."
            );
            setUploading(false);
            return;
          }

          setTimeout(poll, 3000);
        } catch {
          if (!cancelledRef.current) {
            setError("Error checking report status.");
            setUploading(false);
          }
        }
      };

      poll();
    },
    [onComplete, steps]
  );

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setError(null);
      setFileName(file.name);
      setUploading(true);
      cancelledRef.current = false;

      const initialSteps: ProcessingStep[] = [
        { label: "File received", status: "active" },
        { label: "Extracting text...", status: "pending" },
        { label: "AI reading your report...", status: "pending" },
        { label: "Analyzing results...", status: "pending" },
      ];
      setSteps(initialSteps);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const result = await apiUpload<{ report_id: string }>(
          `/api/reports?user_id=${userId}`,
          formData
        );

        currentReportId.current = result.report_id;

        if (cancelledRef.current) {
          // User cancelled during upload — clean up
          await apiFetch(`/api/reports/${result.report_id}`, { method: "DELETE" }).catch(() => {});
          return;
        }

        updateStep(0, "done");
        updateStep(1, "active");

        pollReport(result.report_id);
      } catch (err) {
        if (!cancelledRef.current) {
          const message = err instanceof Error ? err.message : "Upload failed";
          setError(message);
          setUploading(false);
          updateStep(0, "error");
        }
      }
    },
    [userId, pollReport]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div className="w-full">
      {!uploading && steps.length === 0 && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition ${
            isDragActive
              ? "border-emerald-500 bg-emerald-50"
              : "border-gray-300 bg-gray-50 hover:border-emerald-400 hover:bg-emerald-50/50"
          }`}
        >
          <input {...getInputProps()} />
          <svg
            className="w-12 h-12 mx-auto text-gray-400 mb-3"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          <p className="text-gray-700 font-medium">
            Drop your blood test PDF here
          </p>
          <p className="text-gray-400 text-sm mt-1">or click to browse</p>
        </div>
      )}

      {/* Processing steps */}
      {steps.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          {fileName && (
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-500 truncate">
                Uploading: <span className="font-medium text-gray-700">{fileName}</span>
              </p>
              {uploading && (
                <button
                  onClick={handleCancel}
                  className="text-xs font-medium text-red-500 hover:text-red-700 transition"
                >
                  Cancel
                </button>
              )}
            </div>
          )}
          <div className="space-y-3">
            {steps.map((step, i) => (
              <div key={i} className="flex items-center gap-3">
                {step.status === "done" && (
                  <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  </div>
                )}
                {step.status === "active" && (
                  <div className="w-6 h-6 flex items-center justify-center flex-shrink-0">
                    <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
                {step.status === "pending" && (
                  <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <div className="w-2 h-2 rounded-full bg-gray-300" />
                  </div>
                )}
                {step.status === "error" && (
                  <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                )}
                <span
                  className={`text-sm ${
                    step.status === "done"
                      ? "text-emerald-700 font-medium"
                      : step.status === "active"
                      ? "text-gray-800 font-medium"
                      : step.status === "error"
                      ? "text-red-600 font-medium"
                      : "text-gray-400"
                  }`}
                >
                  {step.status === "done" && i === steps.length - 1
                    ? "Done!"
                    : step.label}
                </span>
              </div>
            ))}
          </div>

          {/* Retry button on failure */}
          {error && !uploading && (
            <button
              onClick={resetState}
              className="mt-4 text-sm font-medium text-emerald-600 hover:text-emerald-700 transition"
            >
              Try again
            </button>
          )}
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  );
}