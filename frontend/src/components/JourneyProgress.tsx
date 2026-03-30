"use client";

import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface JourneyProgressProps {
  steps: { label: string; completed: boolean }[];
}

export default function JourneyProgress({ steps }: JourneyProgressProps) {
  // Find the first incomplete step index (the "current" step)
  const currentIndex = steps.findIndex((s) => !s.completed);

  return (
    <div className="w-full overflow-x-auto">
      <div className="flex items-start min-w-max px-2 py-4">
        {steps.map((step, idx) => {
          const isCurrent = idx === currentIndex;
          const isCompleted = step.completed;
          const isLast = idx === steps.length - 1;

          return (
            <div key={idx} className="flex items-start flex-1 min-w-0">
              <div className="flex flex-col items-center">
                {/* Circle */}
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors shrink-0",
                    isCompleted
                      ? "bg-emerald-500 border-emerald-500 text-white"
                      : isCurrent
                      ? "border-emerald-500 bg-white dark:bg-gray-900 text-emerald-500"
                      : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-400 dark:text-gray-500"
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <span className="text-xs font-semibold">{idx + 1}</span>
                  )}
                </div>

                {/* Label */}
                <span
                  className={cn(
                    "text-xs text-center mt-2 max-w-[80px] leading-tight",
                    isCompleted
                      ? "text-emerald-600 dark:text-emerald-400 font-medium"
                      : isCurrent
                      ? "text-gray-900 dark:text-gray-100 font-medium"
                      : "text-gray-400 dark:text-gray-500"
                  )}
                >
                  {step.label}
                </span>
              </div>

              {/* Connecting line */}
              {!isLast && (
                <div className="flex-1 flex items-center px-1 mt-4">
                  <div
                    className={cn(
                      "h-0.5 w-full rounded",
                      isCompleted
                        ? "bg-emerald-500"
                        : "bg-gray-300 dark:bg-gray-600"
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
