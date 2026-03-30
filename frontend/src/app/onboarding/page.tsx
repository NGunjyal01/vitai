"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Profile {
  full_name: string;
  age: number;
  gender: "male" | "female" | "other" | "";
  health_goal: string;
  height_cm: string;
  weight_kg: string;
  diet_type: string;
  training_type: string;
  training_frequency: string;
  training_experience: string;
  supplements: string[];
  goal_phase: string;
  conditions: string[];
  activity_level: string;
  sleep_hours: string;
  stress_level: string;
  family_history: string[];
}

interface InsightCard {
  title: string;
  body: string;
  action: string;
}

const INITIAL_PROFILE: Profile = {
  full_name: "",
  age: 25,
  gender: "",
  health_goal: "",
  height_cm: "",
  weight_kg: "",
  diet_type: "",
  training_type: "",
  training_frequency: "",
  training_experience: "",
  supplements: [],
  goal_phase: "",
  conditions: [],
  activity_level: "",
  sleep_hours: "",
  stress_level: "",
  family_history: [],
};

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const HEALTH_GOALS = [
  { value: "improve_energy", label: "Improve Energy", icon: "⚡" },
  { value: "manage_blood_sugar", label: "Manage Blood Sugar", icon: "🩸" },
  { value: "reduce_cholesterol", label: "Reduce Cholesterol", icon: "💓" },
  { value: "lose_weight", label: "Lose Weight", icon: "⚖️" },
  { value: "build_muscle", label: "Build Muscle", icon: "💪" },
  { value: "athletic_performance", label: "Athletic Performance", icon: "🏋️" },
  { value: "general_wellness", label: "General Wellness", icon: "🌿" },
];

const DIET_TYPES = ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian"];

const TRAINING_FREQUENCIES = ["2-3x/week", "4-5x/week", "6+x/week"];
const TRAINING_EXPERIENCES = ["Beginner", "Intermediate", "Advanced"];
const SUPPLEMENT_OPTIONS = [
  "Creatine",
  "Whey",
  "Pre-workout",
  "Multivitamin",
  "Omega-3",
  "None",
];
const GOAL_PHASES = ["Bulking", "Cutting", "Maintaining", "Recomp"];

const CONDITIONS = [
  "Diabetes",
  "Thyroid",
  "High BP",
  "High Cholesterol",
  "PCOS",
  "Anemia",
  "Vitamin D Deficiency",
  "None",
];

const ACTIVITY_LEVELS = [
  { value: "sedentary", label: "Sedentary", desc: "Little or no exercise" },
  { value: "lightly_active", label: "Lightly Active", desc: "1-3 days/week" },
  {
    value: "moderately_active",
    label: "Moderately Active",
    desc: "3-5 days/week",
  },
  { value: "very_active", label: "Very Active", desc: "6-7 days/week" },
];

const SLEEP_OPTIONS = [
  "Less than 5",
  "5-6",
  "6-7",
  "7-8",
  "More than 8",
];

const STRESS_LEVELS = [
  { value: "low", label: "Low", emoji: "😌" },
  { value: "moderate", label: "Moderate", emoji: "😐" },
  { value: "high", label: "High", emoji: "😰" },
  { value: "very_high", label: "Very High", emoji: "😫" },
];

const FAMILY_HISTORY_OPTIONS = [
  "Diabetes",
  "Heart Disease",
  "Thyroid",
  "High BP",
  "Cancer",
  "None/Don't Know",
];

const FITNESS_GOALS = ["build_muscle", "athletic_performance"];

/* ------------------------------------------------------------------ */
/*  Helper components                                                  */
/* ------------------------------------------------------------------ */

function ProgressDots({ current, total }: { current: number; total: number }) {
  return (
    <div className="flex items-center justify-center gap-2 mb-8">
      {Array.from({ length: total }, (_, i) => (
        <div
          key={i}
          className={`h-2.5 rounded-full transition-all duration-300 ${
            i === current
              ? "w-8 bg-emerald-500"
              : i < current
              ? "w-2.5 bg-emerald-300"
              : "w-2.5 bg-gray-200"
          }`}
        />
      ))}
    </div>
  );
}

function StepTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-2xl font-bold text-gray-900 mb-1 text-center">
      {children}
    </h2>
  );
}

function StepSubtitle({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-gray-500 text-sm mb-6 text-center">{children}</p>
  );
}

/* ------------------------------------------------------------------ */
/*  Main component                                                     */
/* ------------------------------------------------------------------ */

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [profile, setProfile] = useState<Profile>(INITIAL_PROFILE);
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState<InsightCard[]>([]);
  const [error, setError] = useState("");

  /* ---- helpers ---- */

  const patch = (updates: Partial<Profile>) =>
    setProfile((prev) => ({ ...prev, ...updates }));

  const toggleChip = (
    field: "conditions" | "family_history" | "supplements",
    value: string,
    noneValue: string
  ) => {
    setProfile((prev) => {
      const current = prev[field] as string[];
      if (value === noneValue) {
        return { ...prev, [field]: current.includes(noneValue) ? [] : [noneValue] };
      }
      const without = current.filter((v) => v !== noneValue);
      const toggled = without.includes(value)
        ? without.filter((v) => v !== value)
        : [...without, value];
      return { ...prev, [field]: toggled };
    });
  };

  /* ---- validation per step ---- */

  const isStepValid = (): boolean => {
    switch (step) {
      case 0:
        return profile.full_name.trim().length > 0 && profile.age > 0 && profile.gender !== "";
      case 1:
        return profile.health_goal !== "";
      case 2:
        return profile.diet_type !== "";
      case 3:
        return profile.conditions.length > 0;
      case 4:
        return (
          profile.activity_level !== "" &&
          profile.sleep_hours !== "" &&
          profile.stress_level !== ""
        );
      case 5:
        return profile.family_history.length > 0;
      default:
        return true;
    }
  };

  /* ---- submit ---- */

  const handleComplete = async () => {
    setLoading(true);
    setError("");
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) {
        router.push("/login");
        return;
      }

      const response = await apiFetch<{ insights: InsightCard[] }>(
        "/api/onboarding",
        {
          method: "POST",
          body: JSON.stringify({ user_id: user.id, ...profile }),
        }
      );

      setInsights(response.insights ?? []);
      setStep(6);
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const next = () => {
    if (step === 5) {
      handleComplete();
    } else {
      setStep((s) => s + 1);
    }
  };

  const back = () => setStep((s) => Math.max(0, s - 1));

  /* ---------------------------------------------------------------- */
  /*  Step renderers                                                   */
  /* ---------------------------------------------------------------- */

  /* --- Step 1: Basic Info --- */
  const renderBasicInfo = () => (
    <div className="space-y-6">
      <StepTitle>Let&apos;s get to know you</StepTitle>
      <StepSubtitle>Tell us a bit about yourself</StepSubtitle>

      {/* Full Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Full Name
        </label>
        <input
          type="text"
          value={profile.full_name}
          onChange={(e) => patch({ full_name: e.target.value })}
          placeholder="Enter your full name"
          className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition"
        />
      </div>

      {/* Age */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Age
        </label>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => patch({ age: Math.max(1, profile.age - 1) })}
            className="h-12 w-12 rounded-xl bg-gray-100 text-xl font-bold text-gray-600 hover:bg-gray-200 transition flex items-center justify-center"
          >
            -
          </button>
          <input
            type="number"
            value={profile.age}
            onChange={(e) =>
              patch({ age: Math.max(1, parseInt(e.target.value) || 1) })
            }
            className="w-20 text-center rounded-xl border border-gray-200 px-3 py-3 text-gray-900 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition"
          />
          <button
            type="button"
            onClick={() => patch({ age: Math.min(120, profile.age + 1) })}
            className="h-12 w-12 rounded-xl bg-gray-100 text-xl font-bold text-gray-600 hover:bg-gray-200 transition flex items-center justify-center"
          >
            +
          </button>
        </div>
      </div>

      {/* Gender */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Gender
        </label>
        <div className="flex gap-2">
          {(["male", "female", "other"] as const).map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => patch({ gender: g })}
              className={`flex-1 rounded-xl py-3 text-sm font-medium transition ${
                profile.gender === g
                  ? "bg-emerald-500 text-white shadow-md"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {g.charAt(0).toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  /* --- Step 2: Health Goal --- */
  const renderHealthGoal = () => (
    <div className="space-y-6">
      <StepTitle>What&apos;s your primary goal?</StepTitle>
      <StepSubtitle>We&apos;ll personalize your experience</StepSubtitle>

      <div className="grid grid-cols-2 gap-3">
        {HEALTH_GOALS.map((goal) => (
          <button
            key={goal.value}
            type="button"
            onClick={() => patch({ health_goal: goal.value })}
            className={`flex flex-col items-center gap-2 rounded-2xl border-2 p-4 transition ${
              profile.health_goal === goal.value
                ? "border-emerald-500 bg-emerald-50 shadow-md"
                : "border-gray-100 bg-white hover:border-gray-200"
            }`}
          >
            <span className="text-3xl">{goal.icon}</span>
            <span className="text-sm font-medium text-gray-800 text-center">
              {goal.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );

  /* --- Step 3: Body & Diet --- */
  const showFitnessFields = FITNESS_GOALS.includes(profile.health_goal);

  const renderBodyDiet = () => (
    <div className="space-y-5">
      <StepTitle>Body &amp; Diet</StepTitle>
      <StepSubtitle>Help us understand your lifestyle</StepSubtitle>

      {/* Height & Weight row */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Height (cm)
          </label>
          <input
            type="number"
            value={profile.height_cm}
            onChange={(e) => patch({ height_cm: e.target.value })}
            placeholder="e.g. 170"
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Weight (kg)
          </label>
          <input
            type="number"
            value={profile.weight_kg}
            onChange={(e) => patch({ weight_kg: e.target.value })}
            placeholder="e.g. 70"
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition"
          />
        </div>
      </div>

      {/* Diet Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Diet Type
        </label>
        <div className="grid grid-cols-2 gap-2">
          {DIET_TYPES.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => patch({ diet_type: d })}
              className={`rounded-xl py-3 text-sm font-medium transition ${
                profile.diet_type === d
                  ? "bg-emerald-500 text-white shadow-md"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {/* Conditional Fitness Fields */}
      {showFitnessFields && (
        <div className="space-y-4 rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4">
          <p className="text-sm font-semibold text-emerald-700">
            Fitness Details
          </p>

          {/* Training Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Training Type
            </label>
            <input
              type="text"
              value={profile.training_type}
              onChange={(e) => patch({ training_type: e.target.value })}
              placeholder="e.g. Powerlifting, CrossFit"
              className="w-full rounded-xl border border-gray-200 px-4 py-3 text-gray-900 placeholder-gray-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition bg-white"
            />
          </div>

          {/* Training Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Training Frequency
            </label>
            <div className="flex gap-2">
              {TRAINING_FREQUENCIES.map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => patch({ training_frequency: f })}
                  className={`flex-1 rounded-xl py-2.5 text-xs font-medium transition ${
                    profile.training_frequency === f
                      ? "bg-emerald-500 text-white shadow-md"
                      : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Training Experience */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Experience Level
            </label>
            <div className="flex gap-2">
              {TRAINING_EXPERIENCES.map((e) => (
                <button
                  key={e}
                  type="button"
                  onClick={() => patch({ training_experience: e })}
                  className={`flex-1 rounded-xl py-2.5 text-xs font-medium transition ${
                    profile.training_experience === e
                      ? "bg-emerald-500 text-white shadow-md"
                      : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
                  }`}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          {/* Supplements */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Supplements
            </label>
            <div className="flex flex-wrap gap-2">
              {SUPPLEMENT_OPTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => toggleChip("supplements", s, "None")}
                  className={`rounded-full px-4 py-2 text-xs font-medium transition ${
                    profile.supplements.includes(s)
                      ? "bg-emerald-500 text-white shadow-md"
                      : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Goal Phase */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Goal Phase
            </label>
            <div className="grid grid-cols-2 gap-2">
              {GOAL_PHASES.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => patch({ goal_phase: p })}
                  className={`rounded-xl py-2.5 text-xs font-medium transition ${
                    profile.goal_phase === p
                      ? "bg-emerald-500 text-white shadow-md"
                      : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  /* --- Step 4: Known Conditions --- */
  const renderConditions = () => (
    <div className="space-y-6">
      <StepTitle>Any known conditions?</StepTitle>
      <StepSubtitle>Select all that apply</StepSubtitle>

      <div className="flex flex-wrap gap-2 justify-center">
        {CONDITIONS.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => toggleChip("conditions", c, "None")}
            className={`rounded-full px-5 py-2.5 text-sm font-medium transition ${
              profile.conditions.includes(c)
                ? "bg-emerald-500 text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {c}
          </button>
        ))}
      </div>
    </div>
  );

  /* --- Step 5: Lifestyle --- */
  const renderLifestyle = () => (
    <div className="space-y-6">
      <StepTitle>Your Lifestyle</StepTitle>
      <StepSubtitle>Help us understand your daily routine</StepSubtitle>

      {/* Activity Level */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Activity Level
        </label>
        <div className="grid grid-cols-2 gap-2">
          {ACTIVITY_LEVELS.map((a) => (
            <button
              key={a.value}
              type="button"
              onClick={() => patch({ activity_level: a.value })}
              className={`rounded-2xl border-2 p-3 text-left transition ${
                profile.activity_level === a.value
                  ? "border-emerald-500 bg-emerald-50 shadow-md"
                  : "border-gray-100 bg-white hover:border-gray-200"
              }`}
            >
              <span className="block text-sm font-semibold text-gray-800">
                {a.label}
              </span>
              <span className="block text-xs text-gray-500 mt-0.5">
                {a.desc}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Sleep Hours */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Sleep (hours/night)
        </label>
        <div className="flex flex-wrap gap-2">
          {SLEEP_OPTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => patch({ sleep_hours: s })}
              className={`rounded-full px-4 py-2.5 text-sm font-medium transition ${
                profile.sleep_hours === s
                  ? "bg-emerald-500 text-white shadow-md"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Stress Level */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Stress Level
        </label>
        <div className="flex gap-2 justify-center">
          {STRESS_LEVELS.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => patch({ stress_level: s.value })}
              className={`flex flex-col items-center gap-1 rounded-2xl border-2 px-4 py-3 transition ${
                profile.stress_level === s.value
                  ? "border-emerald-500 bg-emerald-50 shadow-md"
                  : "border-gray-100 bg-white hover:border-gray-200"
              }`}
            >
              <span className="text-2xl">{s.emoji}</span>
              <span className="text-xs font-medium text-gray-700">
                {s.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  /* --- Step 6: Family History --- */
  const renderFamilyHistory = () => (
    <div className="space-y-6">
      <StepTitle>Family History</StepTitle>
      <StepSubtitle>Any conditions that run in your family?</StepSubtitle>

      <div className="flex flex-wrap gap-2 justify-center">
        {FAMILY_HISTORY_OPTIONS.map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => toggleChip("family_history", f, "None/Don't Know")}
            className={`rounded-full px-5 py-2.5 text-sm font-medium transition ${
              profile.family_history.includes(f)
                ? "bg-emerald-500 text-white shadow-md"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>
    </div>
  );

  /* --- WOW Moment --- */
  const renderWow = () => (
    <div className="space-y-6 text-center">
      <div className="space-y-2">
        <span className="inline-block text-5xl mb-2">🎉</span>
        <h2 className="text-3xl font-bold text-gray-900">
          Welcome, {profile.full_name.split(" ")[0]}!
        </h2>
        <p className="text-gray-500 text-sm">
          Here are some personalized insights based on your profile
        </p>
      </div>

      {insights.length > 0 && (
        <div className="space-y-3 text-left">
          {insights.map((insight, i) => (
            <div
              key={i}
              className="rounded-2xl border border-gray-100 bg-gradient-to-br from-white to-emerald-50/50 p-4 shadow-sm"
            >
              <h3 className="text-sm font-bold text-gray-900 mb-1">
                {insight.title}
              </h3>
              <p className="text-sm text-gray-600 mb-2">{insight.body}</p>
              <p className="text-xs font-medium text-emerald-600">
                {insight.action}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-3 pt-2">
        <button
          type="button"
          onClick={() => router.push("/dashboard")}
          className="w-full rounded-2xl bg-emerald-500 py-3.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/25 hover:bg-emerald-600 active:scale-[0.98] transition"
        >
          Upload a Report
        </button>
        <button
          type="button"
          onClick={() => router.push("/onboarding/quick-check")}
          className="w-full rounded-2xl border-2 border-emerald-500 py-3.5 text-sm font-semibold text-emerald-600 hover:bg-emerald-50 active:scale-[0.98] transition"
        >
          Enter Vitals Manually
        </button>
      </div>
    </div>
  );

  /* ---------------------------------------------------------------- */
  /*  Step map                                                         */
  /* ---------------------------------------------------------------- */

  const STEPS = [
    renderBasicInfo,
    renderHealthGoal,
    renderBodyDiet,
    renderConditions,
    renderLifestyle,
    renderFamilyHistory,
  ];

  const TOTAL_STEPS = STEPS.length;

  /* ---------------------------------------------------------------- */
  /*  Layout                                                           */
  /* ---------------------------------------------------------------- */

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="rounded-3xl bg-white shadow-xl shadow-gray-200/50 p-6 sm:p-8">
          {/* WOW screen has no progress dots / nav */}
          {step === 6 ? (
            renderWow()
          ) : (
            <>
              <ProgressDots current={step} total={TOTAL_STEPS} />

              {/* Step content with transition */}
              <div
                key={step}
                className="animate-[fadeSlideIn_0.3s_ease-out]"
              >
                {STEPS[step]()}
              </div>

              {/* Error */}
              {error && (
                <p className="mt-4 text-center text-sm text-red-500">
                  {error}
                </p>
              )}

              {/* Navigation */}
              <div className="mt-8 flex items-center gap-3">
                {step > 0 && (
                  <button
                    type="button"
                    onClick={back}
                    disabled={loading}
                    className="rounded-2xl border border-gray-200 px-5 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50 active:scale-[0.98] transition disabled:opacity-50"
                  >
                    Back
                  </button>
                )}

                {/* Skip button for body & diet */}
                {step === 2 && (
                  <button
                    type="button"
                    onClick={() => setStep(3)}
                    className="text-sm font-medium text-gray-400 hover:text-gray-600 transition"
                  >
                    Skip
                  </button>
                )}

                <button
                  type="button"
                  onClick={next}
                  disabled={!isStepValid() || loading}
                  className="ml-auto rounded-2xl bg-emerald-500 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-500/25 hover:bg-emerald-600 active:scale-[0.98] transition disabled:opacity-40 disabled:shadow-none disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <svg
                        className="animate-spin h-4 w-4"
                        viewBox="0 0 24 24"
                        fill="none"
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
                      Analyzing...
                    </>
                  ) : step === 5 ? (
                    "Finish"
                  ) : (
                    "Next"
                  )}
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Keyframe for fade-slide animation */}
      <style jsx global>{`
        @keyframes fadeSlideIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
