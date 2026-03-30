"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";

const SYMPTOM_OPTIONS = [
  "Fatigue",
  "Headache",
  "Dizziness",
  "Nausea",
  "Muscle Pain",
  "Joint Pain",
  "Bloating",
  "Insomnia",
  "Anxiety",
  "Brain Fog",
  "None",
];

const ENERGY_EMOJIS = ["😴", "😟", "😐", "😊", "🔥"];
const MOOD_EMOJIS = ["😢", "😕", "😐", "🙂", "😄"];

function todayStr(): string {
  return new Date().toISOString().split("T")[0];
}

interface JournalEntry {
  logged_date: string;
  energy_level: number;
  mood: string;
  symptoms: string[];
  notes: string;
}

export default function JournalPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [date, setDate] = useState(todayStr());
  const [energy, setEnergy] = useState(0);
  const [mood, setMood] = useState(0);
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pastEntries, setPastEntries] = useState<JournalEntry[]>([]);
  const [loadingEntries, setLoadingEntries] = useState(true);

  useEffect(() => {
    async function init() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        setUserId(user.id);
        loadPastEntries(user.id);
      }
    }
    init();
  }, []);

  // Pre-fill form when date changes and an existing entry exists for that date
  useEffect(() => {
    const existing = pastEntries.find((e) => e.logged_date === date);
    if (existing) {
      setEnergy(existing.energy_level || 0);
      setMood(typeof existing.mood === "string" ? parseInt(existing.mood) || 0 : existing.mood || 0);
      setSymptoms(existing.symptoms || []);
      setNotes(existing.notes || "");
      setSaved(false);
    } else {
      // Reset form for a new date
      setEnergy(0);
      setMood(0);
      setSymptoms([]);
      setNotes("");
      setSaved(false);
    }
  }, [date, pastEntries]);

  const loadPastEntries = async (uid: string) => {
    setLoadingEntries(true);
    try {
      const data = await apiFetch<JournalEntry[]>(
        `/api/symptom-log?user_id=${uid}&limit=7`
      );
      setPastEntries(Array.isArray(data) ? data : []);
    } catch {
      setPastEntries([]);
    } finally {
      setLoadingEntries(false);
    }
  };

  const toggleSymptom = (s: string) => {
    if (s === "None") {
      setSymptoms((prev) => (prev.includes("None") ? [] : ["None"]));
      return;
    }
    setSymptoms((prev) => {
      const without = prev.filter((x) => x !== "None");
      return without.includes(s)
        ? without.filter((x) => x !== s)
        : [...without, s];
    });
  };

  const canSave = energy > 0 && mood > 0;
  const isEditing = pastEntries.some((e) => e.logged_date === date);

  const handleSave = async () => {
    if (!userId || !canSave) return;
    setSaving(true);
    setError(null);
    setSaved(false);

    try {
      await apiFetch("/api/symptom-log", {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          energy_level: energy,
          mood: mood,
          symptoms,
          notes,
          logged_date: date,
        }),
      });
      setSaved(true);
      loadPastEntries(userId);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to save entry.");
    } finally {
      setSaving(false);
    }
  };

  const formatEntryDate = (dateStr: string) => {
    const d = new Date(dateStr + "T00:00:00");
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (d.toDateString() === today.toDateString()) return "Today";
    if (d.toDateString() === yesterday.toDateString()) return "Yesterday";
    return d.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
    });
  };

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Daily Journal
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Track how you feel each day
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-5">
          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Date
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              max={todayStr()}
              className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {/* Energy Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Energy Level
            </label>
            <div className="flex gap-2">
              {ENERGY_EMOJIS.map((emoji, idx) => (
                <button
                  key={idx}
                  onClick={() => setEnergy(idx + 1)}
                  className={`w-12 h-12 rounded-xl text-2xl flex items-center justify-center transition-all ${
                    energy === idx + 1
                      ? "bg-emerald-100 dark:bg-emerald-900/40 ring-2 ring-emerald-500 scale-110"
                      : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
            {energy > 0 && (
              <p className="text-xs text-gray-400 mt-1">
                {energy}/5
              </p>
            )}
          </div>

          {/* Mood */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Mood
            </label>
            <div className="flex gap-2">
              {MOOD_EMOJIS.map((emoji, idx) => (
                <button
                  key={idx}
                  onClick={() => setMood(idx + 1)}
                  className={`w-12 h-12 rounded-xl text-2xl flex items-center justify-center transition-all ${
                    mood === idx + 1
                      ? "bg-emerald-100 dark:bg-emerald-900/40 ring-2 ring-emerald-500 scale-110"
                      : "bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
            {mood > 0 && (
              <p className="text-xs text-gray-400 mt-1">
                {mood}/5
              </p>
            )}
          </div>

          {/* Symptoms */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Symptoms
            </label>
            <div className="flex flex-wrap gap-2">
              {SYMPTOM_OPTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => toggleSymptom(s)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                    symptoms.includes(s)
                      ? s === "None"
                        ? "bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 ring-1 ring-green-400"
                        : "bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 ring-1 ring-red-400"
                      : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="Anything else you want to note..."
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
            />
          </div>

          {/* Error / Success */}
          {error && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-sm">
              {error}
            </div>
          )}
          {saved && (
            <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300 text-sm">
              Entry saved successfully!
            </div>
          )}

          {/* Save */}
          <button
            onClick={handleSave}
            disabled={saving || !canSave}
            className="w-full py-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-medium text-sm transition-colors flex items-center justify-center gap-2"
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
              isEditing ? "Update Entry" : "Save Entry"
            )}
          </button>
          {!canSave && (
            <p className="text-xs text-gray-400 text-center mt-1">
              Select energy and mood to save
            </p>
          )}
          {isEditing && canSave && (
            <p className="text-xs text-amber-500 text-center mt-1">
              Editing existing entry for this date
            </p>
          )}
        </div>

        {/* Past 7 Days Timeline */}
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Past 7 Days
          </h3>

          {loadingEntries && (
            <div className="flex items-center justify-center py-8">
              <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {!loadingEntries && pastEntries.length === 0 && (
            <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-6">
              No entries yet. Start logging today!
            </p>
          )}

          {!loadingEntries && pastEntries.length > 0 && (
            <div className="space-y-2">
              {pastEntries.map((entry, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 px-4 py-3 flex items-center gap-4"
                >
                  <div className="flex-shrink-0 text-center min-w-[60px]">
                    <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {formatEntryDate(entry.logged_date)}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {entry.energy_level > 0 && (
                      <span className="text-lg" title={`Energy: ${entry.energy_level}/5`}>
                        {ENERGY_EMOJIS[(entry.energy_level || 1) - 1]}
                      </span>
                    )}
                    {entry.mood && Number(entry.mood) > 0 && (
                      <span className="text-lg" title={`Mood: ${entry.mood}/5`}>
                        {MOOD_EMOJIS[(Number(entry.mood) || 1) - 1]}
                      </span>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    {entry.symptoms && entry.symptoms.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {entry.symptoms.map((s: string) => (
                          <span
                            key={s}
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              s === "None"
                                ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400"
                                : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                            }`}
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                    {entry.notes && (
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">
                        {entry.notes}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}