"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";

interface FieldConfig {
  label: string;
  parameter_name: string;
  unit: string;
  placeholder: string;
  min: number;
  max: number;
  step: number;
}

const FIELDS: FieldConfig[] = [
  {
    label: "Weight",
    parameter_name: "weight",
    unit: "kg",
    placeholder: "e.g. 70",
    min: 20,
    max: 300,
    step: 0.1,
  },
  {
    label: "Blood Pressure (Systolic)",
    parameter_name: "bp_systolic",
    unit: "mmHg",
    placeholder: "e.g. 120",
    min: 60,
    max: 250,
    step: 1,
  },
  {
    label: "Blood Pressure (Diastolic)",
    parameter_name: "bp_diastolic",
    unit: "mmHg",
    placeholder: "e.g. 80",
    min: 40,
    max: 160,
    step: 1,
  },
  {
    label: "Fasting Blood Sugar",
    parameter_name: "fasting_glucose",
    unit: "mg/dL",
    placeholder: "e.g. 90",
    min: 30,
    max: 500,
    step: 1,
  },
  {
    label: "Resting Heart Rate",
    parameter_name: "resting_heart_rate",
    unit: "bpm",
    placeholder: "e.g. 72",
    min: 30,
    max: 200,
    step: 1,
  },
  {
    label: "Sleep Hours",
    parameter_name: "sleep_hours",
    unit: "hours",
    placeholder: "e.g. 7",
    min: 0,
    max: 24,
    step: 0.5,
  },
];

export default function QuickCheckPage() {
  const router = useRouter();
  const [values, setValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (paramName: string, val: string) => {
    setValues((prev) => ({ ...prev, [paramName]: val }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }

      const filledFields = FIELDS.filter(
        (f) => values[f.parameter_name] && values[f.parameter_name].trim() !== ""
      );

      if (filledFields.length === 0) {
        router.push("/dashboard");
        return;
      }

      const promises = filledFields.map((f) =>
        apiFetch("/api/manual-entry", {
          method: "POST",
          body: JSON.stringify({
            user_id: user.id,
            parameter_name: f.parameter_name,
            value: parseFloat(values[f.parameter_name]),
            unit: f.unit,
          }),
        })
      );

      await Promise.all(promises);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to save entries. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white dark:bg-gray-900 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-800 p-6 md:p-8">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 flex items-center justify-center">
            <svg
              className="w-6 h-6 text-emerald-600 dark:text-emerald-400"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12h6m-3-3v6m-7.5 3.75A2.25 2.25 0 016.75 21h10.5a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 3h-3a2.25 2.25 0 00-2.15 1.586m0 0A48.41 48.41 0 006.226 3.916"
              />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Quick Health Check
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Enter any values you know. All fields are optional.
          </p>
        </div>

        {/* Fields */}
        <div className="space-y-4">
          {FIELDS.map((field) => (
            <div key={field.parameter_name}>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {field.label}{" "}
                <span className="text-gray-400 dark:text-gray-500 font-normal">
                  ({field.unit})
                </span>
              </label>
              <input
                type="number"
                min={field.min}
                max={field.max}
                step={field.step}
                placeholder={field.placeholder}
                value={values[field.parameter_name] || ""}
                onChange={(e) =>
                  handleChange(field.parameter_name, e.target.value)
                }
                className="w-full px-3 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors text-sm"
              />
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="mt-6 space-y-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-400 text-white font-medium text-sm transition-colors flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <svg
                  className="animate-spin w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Saving...
              </>
            ) : (
              "Save"
            )}
          </button>

          <button
            onClick={() => router.push("/dashboard")}
            disabled={saving}
            className="w-full py-3 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-medium text-sm transition-colors"
          >
            Skip -- I'll upload a report
          </button>
        </div>
      </div>
    </div>
  );
}
