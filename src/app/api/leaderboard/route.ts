import { NextResponse } from "next/server";
import { getLeaderboard } from "@/lib/db";
import type { LeaderboardEntry, LeaderboardResponse, ErrorResponse } from "@/lib/types";

export async function GET() {
  try {
    const { questions, totalVotes } = await getLeaderboard();

    const entries: LeaderboardEntry[] = questions.map((q, index) => ({
      rank: index + 1,
      id: q.id,
      text: q.text,
      eloRating: Math.round(q.elo_rating),
      timesShown: q.times_shown,
      timesWon: q.times_won,
      winRate: q.times_shown > 0 ? q.times_won / q.times_shown : 0,
    }));

    const response: LeaderboardResponse = {
      questions: entries,
      totalVotes,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error("Error fetching leaderboard:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
