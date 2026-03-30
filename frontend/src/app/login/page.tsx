"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handle OAuth redirect + existing sessions
  useEffect(() => {
    const hash = window.location.hash;
    const hasToken = hash.includes("access_token");

    // Listen for auth changes first (catches OAuth hash auto-detection)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session && (event === "SIGNED_IN" || event === "TOKEN_REFRESHED")) {
        // Check if user needs onboarding
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile?user_id=${session.user.id}`);
          if (res.ok) {
            const profile = await res.json();
            if (profile.onboarding_completed) {
              setTimeout(() => router.push("/dashboard"), 100);
            } else {
              setTimeout(() => router.push("/onboarding"), 100);
            }
          } else {
            // No profile yet — go to onboarding
            setTimeout(() => router.push("/onboarding"), 100);
          }
        } catch {
          setTimeout(() => router.push("/onboarding"), 100);
        }
      }
      // For INITIAL_SESSION, verify the user actually exists before redirecting
      if (session && event === "INITIAL_SESSION") {
        const { data } = await supabase.auth.getUser();
        if (data.user) {
          try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile?user_id=${data.user.id}`);
            if (res.ok) {
              const profile = await res.json();
              if (profile.onboarding_completed) {
                setTimeout(() => router.push("/dashboard"), 100);
              } else {
                setTimeout(() => router.push("/onboarding"), 100);
              }
            } else {
              setTimeout(() => router.push("/onboarding"), 100);
            }
          } catch {
            setTimeout(() => router.push("/onboarding"), 100);
          }
        } else {
          await supabase.auth.signOut();
          setCheckingAuth(false);
        }
      }
    });

    if (!hasToken) {
      // No OAuth hash — just show the login form immediately
      setCheckingAuth(false);
    }
    // If hasToken, keep showing spinner — onAuthStateChange will fire

    return () => subscription.unsubscribe();
  }, [router]);

  async function handleGoogleSignIn() {
    setError(null);
    setGoogleLoading(true);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin + "/login",
      },
    });
    if (error) {
      setError(error.message);
      setGoogleLoading(false);
    }
    // Don't reset loading — page will redirect
  }

  async function handleEmailAuth(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: window.location.origin + "/dashboard",
          },
        });
        if (error) throw error;
        setError("Check your email for a confirmation link.");
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        router.push("/dashboard");
      }
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  // Show loading screen while checking auth or processing OAuth redirect
  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600 text-sm font-medium">Signing you in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      <div className="w-full max-w-md px-4">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          {/* Logo & Tagline */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              VitaI
            </h1>
            <p className="text-gray-500 mt-2 text-sm">
              Your personal health companion
            </p>
          </div>

          {/* Google Sign-In */}
          <button
            onClick={handleGoogleSignIn}
            disabled={googleLoading}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {googleLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-gray-300 border-t-emerald-600 rounded-full animate-spin"></div>
                Redirecting to Google...
              </>
            ) : (
              <>
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18A11.96 11.96 0 0 0 0 12c0 1.94.46 3.77 1.28 5.4l3.56-2.77v-.54z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Continue with Google
              </>
            )}
          </button>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-gray-400">
                or continue with email
              </span>
            </div>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleEmailAuth} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm placeholder:text-gray-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition"
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm placeholder:text-gray-400 focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition"
              />
            </div>

            {error && (
              <div
                className={`rounded-lg px-4 py-3 text-sm ${
                  error.includes("Check your email")
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : "bg-red-50 text-red-700 border border-red-200"
                }`}
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:from-emerald-700 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Please wait...
                </span>
              ) : isSignUp ? (
                "Create Account"
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          {/* Toggle Sign In / Sign Up */}
          <p className="mt-6 text-center text-sm text-gray-500">
            {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
            <button
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError(null);
              }}
              className="font-medium text-emerald-600 hover:text-emerald-500 transition"
            >
              {isSignUp ? "Sign In" : "Sign Up"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}