import { useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { apiFetch } from "@/lib/api";

// Hook to get current user ID
export function useUserId() {
  const { data: userId } = useQuery({
    queryKey: ["userId"],
    queryFn: async () => {
      const { data } = await supabase.auth.getUser();
      return data.user?.id ?? null;
    },
    staleTime: Infinity, // user ID doesn't change
  });
  return userId;
}

// Hook to fetch health score
export function useScore(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["score", userId],
    queryFn: () => apiFetch(`/api/score?user_id=${userId}`),
    enabled: !!userId,
  });
}

// Hook to fetch reports
export function useReports(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["reports", userId],
    queryFn: () => apiFetch(`/api/reports?user_id=${userId}`),
    enabled: !!userId,
  });
}

// Hook to fetch insights
export function useInsights(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["insights", userId],
    queryFn: () => apiFetch(`/api/insights?user_id=${userId}`),
    enabled: !!userId,
  });
}

// Hook to fetch profile
export function useProfile(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["profile", userId],
    queryFn: () => apiFetch(`/api/profile?user_id=${userId}`),
    enabled: !!userId,
  });
}

// Hook to fetch score history
export function useScoreHistory(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["scoreHistory", userId],
    queryFn: () => apiFetch(`/api/score/history?user_id=${userId}&limit=10`),
    enabled: !!userId,
  });
}

// Hook to fetch symptom logs
export function useSymptomLogs(userId: string | null | undefined) {
  return useQuery({
    queryKey: ["symptomLogs", userId],
    queryFn: () => apiFetch(`/api/symptom-log?user_id=${userId}&limit=7`),
    enabled: !!userId,
  });
}

// Hook to invalidate queries after mutations
export function useInvalidate() {
  const queryClient = useQueryClient();
  return (keys: string[]) => {
    keys.forEach(key => queryClient.invalidateQueries({ queryKey: [key] }));
  };
}
