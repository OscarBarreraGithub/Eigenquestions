"use client";

import { useState } from "react";
import Link from "next/link";
import LoadingTable from "./LoadingTable";

interface LeaderboardEntry {
  rank: number;
  id: number;
  text: string;
  eloRating: number;
  timesShown: number;
  timesWon: number;
  winRate: number;
}

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
  isLoading: boolean;
}

export default function LeaderboardTable({
  entries,
  isLoading,
}: LeaderboardTableProps) {
  const [search, setSearch] = useState("");

  if (isLoading) {
    return <LoadingTable />;
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-[var(--color-chalk-gray)] text-sm mb-4">
          No votes yet. Be the first!
        </p>
        <Link
          href="/"
          className="text-[var(--color-chalk-yellow)] border border-[var(--color-chalk-yellow)]/30 rounded-sm px-4 py-2 hover:bg-[var(--color-chalk-yellow)]/10 transition-colors text-sm"
        >
          Start voting
        </Link>
      </div>
    );
  }

  const filtered = search
    ? entries.filter((e) =>
        e.text.toLowerCase().includes(search.toLowerCase())
      )
    : entries;

  return (
    <div className="w-full">
      <input
        type="text"
        placeholder="Search questions..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-transparent border border-[var(--color-chalk)]/25 rounded-sm px-4 py-2 text-sm text-[var(--color-chalk)] placeholder-[var(--color-chalk-gray)]/50 focus:outline-none focus:border-[var(--color-chalk)]/50 mb-6"
      />

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full table-fixed">
          <thead>
            <tr className="text-xs uppercase tracking-wider text-[var(--color-chalk-gray)] border-b border-[var(--color-chalk)]/15">
              <th className="py-3 px-3 text-left w-12">Rank</th>
              <th className="py-3 px-3 text-left break-words">Question</th>
              <th className="py-3 px-3 text-right w-20">ELO</th>
              <th className="py-3 px-3 text-right w-24 hidden md:table-cell">
                Win Rate
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((entry) => (
              <tr
                key={entry.id}
                className={`border-b border-[var(--color-chalk)]/8 hover:bg-[var(--color-chalk)]/3 transition-colors ${
                  entry.rank === 1 ? "bg-[var(--color-chalk-yellow)]/5" : ""
                }`}
              >
                <td
                  className={`py-3 px-3 text-sm font-mono ${
                    entry.rank <= 3
                      ? "text-[var(--color-chalk-yellow)] font-semibold"
                      : "text-[var(--color-chalk-gray)]"
                  }`}
                >
                  {entry.rank}
                </td>
                <td
                  className={`py-3 px-3 text-sm font-serif break-words overflow-wrap-anywhere ${
                    entry.rank === 1 ? "text-[var(--color-chalk-yellow)]" : "text-[var(--color-chalk)]"
                  }`}
                >
                  {entry.text}
                </td>
                <td className="py-3 px-3 text-sm text-right font-mono tabular-nums text-[var(--color-chalk)] opacity-80">
                  {entry.eloRating}
                </td>
                <td className="py-3 px-3 text-sm text-right text-[var(--color-chalk-gray)] hidden md:table-cell">
                  {(entry.winRate * 100).toFixed(0)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && search && (
        <p className="text-center text-[var(--color-chalk-gray)] text-sm py-8">
          No questions match your search.
        </p>
      )}
    </div>
  );
}
