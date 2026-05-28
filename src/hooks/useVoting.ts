"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface Question {
  id: number;
  text: string;
}

interface UseVotingReturn {
  questionA: Question | null;
  questionB: Question | null;
  isLoading: boolean;
  isVoted: boolean;
  selectedWinnerId: number | null;
  winnerNewElo: number | null;
  loserNewElo: number | null;
  error: string | null;
  sessionVotes: number;
  vote: (winnerId: number) => void;
  skip: () => void;
  retry: () => void;
}

interface PairResponse {
  questionA: Question;
  questionB: Question;
}

interface VoteResponse {
  success: true;
  winnerNewElo: number;
  loserNewElo: number;
}

export function useVoting(): UseVotingReturn {
  const [questionA, setQuestionA] = useState<Question | null>(null);
  const [questionB, setQuestionB] = useState<Question | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isVoted, setIsVoted] = useState(false);
  const [selectedWinnerId, setSelectedWinnerId] = useState<number | null>(null);
  const [winnerNewElo, setWinnerNewElo] = useState<number | null>(null);
  const [loserNewElo, setLoserNewElo] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sessionVotes, setSessionVotes] = useState(0);

  const prefetchedPair = useRef<PairResponse | null>(null);
  const isVoting = useRef(false);

  const fetchPair = useCallback(async (): Promise<PairResponse | null> => {
    try {
      const res = await fetch("/api/pair");
      if (!res.ok) throw new Error("Failed to load questions");
      const data: PairResponse = await res.json();
      return data;
    } catch (err) {
      throw err;
    }
  }, []);

  const loadPair = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setIsVoted(false);
    setSelectedWinnerId(null);
    setWinnerNewElo(null);
    setLoserNewElo(null);

    try {
      const data = await fetchPair();
      if (data) {
        setQuestionA(data.questionA);
        setQuestionB(data.questionB);
      }
    } catch {
      setError("Failed to load questions. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [fetchPair]);

  useEffect(() => {
    loadPair();
  }, [loadPair]);

  const vote = useCallback(
    async (winnerId: number) => {
      if (isVoting.current || !questionA || !questionB) return;
      isVoting.current = true;

      const loserId =
        winnerId === questionA.id ? questionB.id : questionA.id;

      setIsVoted(true);
      setSelectedWinnerId(winnerId);

      try {
        const [voteRes, nextPair] = await Promise.all([
          fetch("/api/vote", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ winnerId, loserId }),
          }),
          fetchPair().catch(() => null),
        ]);

        if (!voteRes.ok) throw new Error("Failed to record vote");

        const voteData: VoteResponse = await voteRes.json();
        setWinnerNewElo(voteData.winnerNewElo);
        setLoserNewElo(voteData.loserNewElo);
        setSessionVotes((prev) => prev + 1);

        prefetchedPair.current = nextPair;

        // Show ELO reveal for 1200ms, then swap
        setTimeout(() => {
          if (prefetchedPair.current) {
            setQuestionA(prefetchedPair.current.questionA);
            setQuestionB(prefetchedPair.current.questionB);
            prefetchedPair.current = null;
            setIsVoted(false);
            setSelectedWinnerId(null);
            setWinnerNewElo(null);
            setLoserNewElo(null);
            isVoting.current = false;
          } else {
            // Prefetch failed; fetch a fresh pair
            isVoting.current = false;
            loadPair();
          }
        }, 1200);
      } catch {
        setError("Failed to record vote. Please try again.");
        setIsVoted(false);
        setSelectedWinnerId(null);
        isVoting.current = false;
      }
    },
    [questionA, questionB, fetchPair, loadPair]
  );

  const skip = useCallback(() => {
    if (isVoting.current) return;
    loadPair();
  }, [loadPair]);

  const retry = useCallback(() => {
    loadPair();
  }, [loadPair]);

  return {
    questionA,
    questionB,
    isLoading,
    isVoted,
    selectedWinnerId,
    winnerNewElo,
    loserNewElo,
    error,
    sessionVotes,
    vote,
    skip,
    retry,
  };
}
