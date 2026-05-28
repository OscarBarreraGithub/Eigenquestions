"use client";

import { useLeaderboard } from "@/hooks/useLeaderboard";
import LeaderboardTable from "@/components/LeaderboardTable";
import ErrorState from "@/components/ErrorState";

export default function LeaderboardPage() {
  const { entries, totalVotes, isLoading, error, retry } = useLeaderboard();

  return (
    <main className="max-w-3xl mx-auto px-4 pt-28 pb-12 w-full">
      <div className="mb-8">
        <h1 className="font-[family-name:var(--font-chalk-title)] text-3xl md:text-5xl text-[var(--color-chalk)] mb-3">
          Leaderboard
        </h1>
        <p className="text-sm font-[family-name:var(--font-pigment)] text-[var(--color-chalk-gray)]">
          Ranked by community vote
          {totalVotes > 0 && (
            <span className="ml-2 font-[family-name:var(--font-pigment)] text-[var(--color-chalk-gray)] opacity-60">
              ({totalVotes.toLocaleString()} total votes)
            </span>
          )}
        </p>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={retry} />
      ) : (
        <LeaderboardTable entries={entries} isLoading={isLoading} />
      )}
    </main>
  );
}
