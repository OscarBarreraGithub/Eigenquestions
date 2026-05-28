"use client";

import { useState, useEffect, useCallback } from "react";

interface LeaderboardEntry {
  rank: number;
  id: number;
  text: string;
  eloRating: number;
  timesShown: number;
  timesWon: number;
  winRate: number;
}

interface UseLeaderboardReturn {
  entries: LeaderboardEntry[];
  totalVotes: number;
  isLoading: boolean;
  error: string | null;
  retry: () => void;
}

export function useLeaderboard(): UseLeaderboardReturn {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [totalVotes, setTotalVotes] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/leaderboard");
      if (!res.ok) throw new Error("Failed to load leaderboard");
      const data = await res.json();
      setEntries(data.questions);
      setTotalVotes(data.totalVotes);
    } catch {
      setError("Failed to load leaderboard. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const retry = useCallback(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  return {
    entries,
    totalVotes,
    isLoading,
    error,
    retry,
  };
}
