"use client";

import { useState, useEffect } from "react";
import { Shield, X } from "lucide-react";

const STORAGE_KEY = "vitai-privacy-banner-dismissed";

export default function PrivacyBanner() {
  const [dismissed, setDismissed] = useState(true); // start hidden to avoid flash

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored !== "true") {
      setDismissed(false);
    }
  }, []);

  const handleDismiss = () => {
    setDismissed(true);
    localStorage.setItem(STORAGE_KEY, "true");
  };

  if (dismissed) return null;

  return (
    <div className="flex items-center gap-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 px-4 py-3 mb-4">
      <Shield className="w-5 h-5 text-blue-500 shrink-0" />
      <p className="flex-1 text-sm text-blue-800 dark:text-blue-300">
        Your data is encrypted and never sold. Delete anytime in settings.
      </p>
      <button
        onClick={handleDismiss}
        className="p-1 rounded hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-colors"
        aria-label="Dismiss"
      >
        <X className="w-4 h-4 text-blue-500" />
      </button>
    </div>
  );
}
