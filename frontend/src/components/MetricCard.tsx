"use client";

import { statusColor, statusLabel } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface MetricCardProps {
  name: string;
  value: number;
  unit: string;
  status: string;
  rangeLow: number;
  rangeHigh: number;
  percentOfRange: number;
}

export default function MetricCard({
  name,
  value,
  unit,
  status,
  rangeLow,
  rangeHigh,
  percentOfRange,
}: MetricCardProps) {
  const router = useRouter();

  // Clamp marker position between 0 and 100
  const markerPos = Math.max(0, Math.min(100, percentOfRange));

  // Bar color based on status
  const barBg =
    status === "normal"
      ? "bg-emerald-100"
      : status === "borderline_low" || status === "borderline_high"
      ? "bg-amber-100"
      : "bg-red-100";

  const markerColor =
    status === "normal"
      ? "bg-emerald-500"
      : status === "borderline_low" || status === "borderline_high"
      ? "bg-amber-500"
      : "bg-red-500";

  const handleAskCoach = () => {
    const question = `Tell me about my ${name} level of ${value} ${unit}. Is this something I should be concerned about?`;
    router.push(`/coach?q=${encodeURIComponent(question)}`);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition">
      <div className="flex items-start justify-between mb-2">
        <div>
          <h4 className="font-semibold text-gray-900 text-sm">{name}</h4>
          <p className="text-lg font-bold text-gray-800 mt-0.5">
            {value}{" "}
            <span className="text-sm font-normal text-gray-500">{unit}</span>
          </p>
        </div>
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border ${statusColor(
            status
          )}`}
        >
          {statusLabel(status)}
        </span>
      </div>

      {/* Range bar */}
      <div className="mt-3">
        <div className={`relative h-2 rounded-full ${barBg}`}>
          {/* Marker */}
          <div
            className={`absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full ${markerColor} border-2 border-white shadow-sm`}
            style={{ left: `${markerPos}%`, transform: `translate(-50%, -50%)` }}
          />
        </div>
        <div className="flex justify-between mt-1.5">
          <span className="text-xs text-gray-400">
            {rangeLow} {unit}
          </span>
          <span className="text-xs text-gray-400">
            {rangeHigh} {unit}
          </span>
        </div>
      </div>

      {/* Normal range text + Ask Coach */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-400">
          Normal: {rangeLow} - {rangeHigh} {unit}
        </p>
        <button
          onClick={handleAskCoach}
          className="text-xs font-medium text-emerald-600 hover:text-emerald-700 transition flex items-center gap-1"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
          </svg>
          Ask Coach
        </button>
      </div>
    </div>
  );
}
