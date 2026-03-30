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
  const svgSize = isLarge ? 200 : 100;
  const strokeWidth = isLarge ? 12 : 8;
  const radius = (svgSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = gradeColor(grade);

  useEffect(() => {
    const duration = 1000;
    const start = performance.now();

    function animate(now: number) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out quad
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
      <svg
        width={svgSize}
        height={svgSize}
        className="transform -rotate-90"
      >
        {/* Background ring */}
        <circle
          cx={svgSize / 2}
          cy={svgSize / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-gray-200 dark:text-gray-700"
        />
        {/* Progress ring */}
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

      {/* Score number centered over the ring */}
      <div
        className="flex flex-col items-center justify-center"
        style={{ marginTop: -svgSize / 2 - (isLarge ? 20 : 10), height: 0 }}
      >
        <span
          className={`font-bold ${
            isLarge ? "text-4xl" : "text-xl"
          } text-gray-900 dark:text-gray-100`}
        >
          {animatedScore}
        </span>
        <span
          className={`font-medium capitalize ${
            isLarge ? "text-sm mt-1" : "text-xs"
          }`}
          style={{ color }}
        >
          {grade}
        </span>
      </div>

      {/* Spacer so content below doesn't overlap */}
      <div style={{ height: isLarge ? svgSize / 2 - 20 : svgSize / 2 - 10 }} />
    </div>
  );
}
