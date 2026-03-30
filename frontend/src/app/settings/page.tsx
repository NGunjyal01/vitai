"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";

interface UserProfile {
  full_name: string;
  age: number | null;
  gender: string;
  height_cm: number | null;
  weight_kg: number | null;
  diet_type: string;
  health_goal: string;
  known_conditions: string;
  activity_level: string;
  sleep_hours: string;
  stress_level: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState<Partial<UserProfile>>({});
  const [saving, setSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function init() {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) {
        router.push("/login");
        return;
      }
      setUserId(user.id);
      setEmail(user.email || "");

      try {
        const data = await apiFetch<UserProfile>(
          `/api/profile?user_id=${user.id}`
        );
        setProfile(data);
      } catch {
        setProfile(null);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [router]);

  const startEditing = () => {
    setEditing(true);
    setEditData(profile ? { ...profile } : {});
  };

  const cancelEditing = () => {
    setEditing(false);
    setEditData({});
  };

  const handleEditChange = (field: string, value: string | number | null) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveProfile = async () => {
    if (!userId) return;
    setSaving(true);
    try {
      await apiFetch("/api/onboarding", {
        method: "POST",
        body: JSON.stringify({
          user_id: userId,
          ...editData,
        }),
      });
      setProfile({ ...profile, ...editData } as UserProfile);
      setEditing(false);
    } catch (err) {
      console.error("Failed to save profile:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async () => {
    if (!userId) return;
    setExporting(true);
    try {
      const data = await apiFetch(`/api/export?user_id=${userId}`);
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `vitai-data-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteData = async () => {
    if (!userId) return;
    setDeleting(true);
    try {
      await apiFetch(`/api/data?user_id=${userId}`, {
        method: "DELETE",
      });
      setProfile(null);
      setShowDeleteConfirm(false);
    } catch (err) {
      console.error("Delete failed:", err);
    } finally {
      setDeleting(false);
    }
  };

  const profileFields: { label: string; key: keyof UserProfile; type: string }[] = [
    { label: "Full Name", key: "full_name", type: "text" },
    { label: "Age", key: "age", type: "number" },
    { label: "Gender", key: "gender", type: "text" },
    { label: "Height (cm)", key: "height_cm", type: "number" },
    { label: "Weight (kg)", key: "weight_kg", type: "number" },
    { label: "Diet Type", key: "diet_type", type: "text" },
    { label: "Health Goal", key: "health_goal", type: "text" },
    { label: "Activity Level", key: "activity_level", type: "text" },
    { label: "Sleep Hours", key: "sleep_hours", type: "text" },
    { label: "Stress Level", key: "stress_level", type: "text" },
  ];

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto space-y-6">
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && (
          <>
            {/* Profile Section */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Profile
                </h3>
                {!editing ? (
                  <button
                    onClick={startEditing}
                    className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 font-medium"
                  >
                    Edit
                  </button>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={cancelEditing}
                      className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveProfile}
                      disabled={saving}
                      className="text-sm text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 font-medium disabled:opacity-50"
                    >
                      {saving ? "Saving..." : "Save"}
                    </button>
                  </div>
                )}
              </div>

              <div className="p-5">
                {/* Email (read-only) */}
                <div className="mb-4">
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                    Email
                  </label>
                  <p className="text-sm text-gray-900 dark:text-gray-100">
                    {email}
                  </p>
                </div>

                {/* Profile fields */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {profileFields.map((field) => (
                    <div key={field.key}>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">
                        {field.label}
                      </label>
                      {editing ? (
                        <input
                          type={field.type}
                          value={
                            editData[field.key] !== undefined && editData[field.key] !== null
                              ? String(editData[field.key])
                              : ""
                          }
                          onChange={(e) =>
                            handleEditChange(
                              field.key,
                              field.type === "number"
                                ? e.target.value
                                  ? Number(e.target.value)
                                  : null
                                : e.target.value
                            )
                          }
                          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                      ) : (
                        <p className="text-sm text-gray-900 dark:text-gray-100">
                          {profile?.[field.key] !== null &&
                          profile?.[field.key] !== undefined
                            ? String(profile[field.key])
                            : "--"}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Data Section */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  Data
                </h3>
              </div>
              <div className="p-5 space-y-3">
                <button
                  onClick={handleExport}
                  disabled={exporting}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
                >
                  <svg
                    className="w-5 h-5 text-gray-500 dark:text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
                    />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {exporting ? "Exporting..." : "Export my data"}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Download all your health data as JSON
                    </p>
                  </div>
                </button>

                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border border-red-200 dark:border-red-800 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-left"
                >
                  <svg
                    className="w-5 h-5 text-red-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                    />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-red-600 dark:text-red-400">
                      Delete all my data
                    </p>
                    <p className="text-xs text-red-400 dark:text-red-500">
                      This action cannot be undone
                    </p>
                  </div>
                </button>
              </div>
            </div>

            {/* About Section */}
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-800">
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                  About
                </h3>
              </div>
              <div className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Version
                  </span>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    0.1.0
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    Privacy Policy
                  </span>
                  <a
                    href="/privacy"
                    className="text-sm text-emerald-600 dark:text-emerald-400 hover:underline"
                  >
                    View
                  </a>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Delete Confirmation Dialog */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 max-w-sm w-full shadow-xl">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Delete all data?
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                This will permanently delete all your health data, reports,
                chat history, and profile information. This action cannot be
                undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={deleting}
                  className="flex-1 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteData}
                  disabled={deleting}
                  className="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white text-sm font-medium transition-colors"
                >
                  {deleting ? "Deleting..." : "Delete Everything"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
