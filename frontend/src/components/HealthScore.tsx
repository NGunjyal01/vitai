"use client";

import { useEffect, useState } from "react";
import { gradeColor } from "@/lib/utils";

interface HealthScoreProps {
  score: number;
  grade: string;
  size?: "sm" | "lg";
}

export default function HealthScore({
  score,
  grade,
  size = "lg",
}: HealthScoreProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const isLarge = size === "lg";
  const svgSize = isLarge ? 180 : 90;
  const strokeWidth = isLarge ? 10 : 6;
  const radius = (svgSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = gradeColor(grade);

  useEffect(() => {
    const duration = 1000;
    const start = performance.now();

    function animate(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - (1 - progress) * (1 - progress);
      setAnimatedScore(Math.round(eased * score));
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    }

    requestAnimationFrame(animate);
  }, [score]);

  const offset = circumference - (animatedScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      {/* Ring container with centered text overlay */}
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
        <svg
          width={svgSize}
          height={svgSize}
          className="transform -rotate-90"
        >
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200 dark:text-gray-700"
          />
          <circle
            cx={svgSize / 2}
            cy={svgSize / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.1s ease-out" }}
          />
        </svg>

        {/* Centered text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {isLarge && (
            <span className="text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
              Health Score
            </span>
          )}
          <span
            className={`font-bold leading-none ${
              isLarge ? "text-3xl" : "text-lg"
            } text-gray-900 dark:text-gray-100`}
          >
            {animatedScore}
            <span className={`font-normal text-gray-400 dark:text-gray-500 ${isLarge ? "text-base" : "text-xs"}`}>
              /100
            </span>
          </span>
          <span
            className={`font-medium capitalize ${
              isLarge ? "text-xs mt-0.5" : "text-[10px]"
            }`}
            style={{ color }}
          >
            {grade}
          </span>
        </div>
      </div>
    </div>
  );
}