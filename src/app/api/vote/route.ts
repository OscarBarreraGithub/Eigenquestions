import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { recordVote } from "@/lib/db";
import type { VoteRequest, VoteResponse, ErrorResponse } from "@/lib/types";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as Partial<VoteRequest>;

    const { winnerId, loserId } = body;

    if (
      typeof winnerId !== "number" ||
      typeof loserId !== "number" ||
      !Number.isInteger(winnerId) ||
      !Number.isInteger(loserId)
    ) {
      return NextResponse.json(
        { error: "winnerId and loserId must be integers" } satisfies ErrorResponse,
        { status: 400 }
      );
    }

    if (winnerId === loserId) {
      return NextResponse.json(
        { error: "winnerId and loserId must be different" } satisfies ErrorResponse,
        { status: 400 }
      );
    }

    const { newWinnerRating, newLoserRating } = await recordVote(winnerId, loserId);

    const response: VoteResponse = {
      success: true,
      winnerNewElo: Math.round(newWinnerRating),
      loserNewElo: Math.round(newLoserRating),
    };

    return NextResponse.json(response);
  } catch (error) {
    if (error instanceof Error && error.message === "Question not found") {
      return NextResponse.json(
        { error: "Question not found" } satisfies ErrorResponse,
        { status: 404 }
      );
    }
    console.error("Error recording vote:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
