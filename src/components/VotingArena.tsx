"use client";

import { useState } from "react";
import { useVoting } from "@/hooks/useVoting";
import QuestionCard from "./QuestionCard";
import OrDivider from "./OrDivider";
import SkipButton from "./SkipButton";
import VotingFeedback from "./VotingFeedback";
import LoadingPair from "./LoadingPair";
import ErrorState from "./ErrorState";

export default function VotingArena() {
  const {
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
  } = useVoting();


  if (error) {
    return (
      <main className="flex-1 flex items-center justify-center px-4 pt-14">
        <ErrorState message={error} onRetry={retry} />
      </main>
    );
  }

  if (isLoading) {
    return (
      <main className="flex-1 flex items-center justify-center px-4 pt-14">
        <LoadingPair />
      </main>
    );
  }

  if (!questionA || !questionB) {
    return (
      <main className="flex-1 flex items-center justify-center px-4 pt-14">
        <ErrorState message="No questions available." onRetry={retry} />
      </main>
    );
  }

  const getEloForQuestion = (qId: number): number | undefined => {
    if (!isVoted || winnerNewElo === null || loserNewElo === null) return undefined;
    if (qId === selectedWinnerId) return winnerNewElo;
    return loserNewElo;
  };

  return (
    <main className="flex-1 flex flex-col items-center justify-center px-4 pt-20 pb-4">
      <div className="flex flex-col items-center w-full max-w-4xl">
        {/* Header area */}
        <div className="mb-8 text-center">
          <h1 className="font-[family-name:var(--font-chalk-title)] text-4xl md:text-6xl text-[var(--color-chalk)] tracking-wide">
            Which direction is more interesting?
          </h1>
        </div>

        {/* Skip button */}
        <div className="mb-5">
          <SkipButton onSkip={skip} disabled={isVoted} />
        </div>

        {/* Cards — side by side on desktop, stacked on mobile */}
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-3 items-stretch w-full">
          <QuestionCard
            question={questionA}
            onSelect={() => vote(questionA.id)}
            disabled={isVoted}
            isWinner={
              selectedWinnerId === null
                ? null
                : selectedWinnerId === questionA.id
            }
            position="left"
            revealedElo={getEloForQuestion(questionA.id)}
          />

          <OrDivider />

          <QuestionCard
            question={questionB}
            onSelect={() => vote(questionB.id)}
            disabled={isVoted}
            isWinner={
              selectedWinnerId === null
                ? null
                : selectedWinnerId === questionB.id
            }
            position="right"
            revealedElo={getEloForQuestion(questionB.id)}
          />
        </div>

        {/* Feedback */}
        <div className="mt-4 h-6">
          <VotingFeedback show={isVoted} />
        </div>

      </div>
    </main>
  );
}
