"use client";

import { Info, AlertTriangle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface InsightBannerProps {
  title: string;
  body: string;
  severity: "info" | "warning" | "urgent";
  action?: string;
}

const severityConfig = {
  info: {
    border: "border-l-blue-500",
    bg: "bg-blue-50 dark:bg-blue-900/20",
    icon: Info,
    iconColor: "text-blue-500",
  },
  warning: {
    border: "border-l-amber-500",
    bg: "bg-amber-50 dark:bg-amber-900/20",
    icon: AlertTriangle,
    iconColor: "text-amber-500",
  },
  urgent: {
    border: "border-l-red-500",
    bg: "bg-red-50 dark:bg-red-900/20",
    icon: AlertCircle,
    iconColor: "text-red-500",
  },
};

export default function InsightBanner({
  title,
  body,
  severity,
  action,
}: InsightBannerProps) {
  const config = severityConfig[severity];
  const Icon = config.icon;

  return (
    <div
      className={cn(
        "rounded-lg border-l-4 p-4",
        config.border,
        config.bg
      )}
    >
      <div className="flex gap-3">
        <Icon className={cn("w-5 h-5 mt-0.5 shrink-0", config.iconColor)} />
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {body}
          </p>
          {action && (
            <button className="mt-2 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:underline">
              {action}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
