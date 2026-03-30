import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function statusColor(status: string): string {
  switch (status) {
    case "normal":
      return "text-green-600 bg-green-50 border-green-200";
    case "borderline_low":
    case "borderline_high":
      return "text-amber-600 bg-amber-50 border-amber-200";
    case "low":
    case "high":
      return "text-red-600 bg-red-50 border-red-200";
    default:
      return "text-gray-600 bg-gray-50 border-gray-200";
  }
}

export function statusLabel(status: string): string {
  switch (status) {
    case "normal":
      return "Normal";
    case "borderline_low":
      return "Borderline Low";
    case "borderline_high":
      return "Borderline High";
    case "low":
      return "Low";
    case "high":
      return "High";
    default:
      return "Unknown";
  }
}

export function gradeColor(grade: string): string {
  switch (grade) {
    case "green":
      return "#22c55e";
    case "amber":
      return "#f59e0b";
    case "red":
      return "#ef4444";
    default:
      return "#6b7280";
  }
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
