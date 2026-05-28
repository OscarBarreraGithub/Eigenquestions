import { NextResponse } from "next/server";
import { getAllQuestions } from "@/lib/db";
import type { PairResponse, ErrorResponse } from "@/lib/types";

function weightedRandomIndex(weights: number[]): number {
  const total = weights.reduce((sum, w) => sum + w, 0);
  let r = Math.random() * total;
  for (let i = 0; i < weights.length; i++) {
    r -= weights[i];
    if (r <= 0) return i;
  }
  return weights.length - 1;
}

export async function GET() {
  try {
    const questions = await getAllQuestions();

    if (questions.length < 2) {
      return NextResponse.json(
        { error: "Not enough questions in database. Need at least 2." } satisfies ErrorResponse,
        { status: 503 }
      );
    }

    // Select Question A: weight = 1 / (timesShown + 1)
    const weightsA = questions.map((q) => 1 / (q.times_shown + 1));
    const indexA = weightedRandomIndex(weightsA);
    const questionA = questions[indexA];

    // Select Question B from remaining: weight = (1/(1+|eloA-eloB|/400)) * (1/(timesShown+1))
    const remaining = questions.filter((_, i) => i !== indexA);
    const weightsB = remaining.map(
      (q) =>
        (1 / (1 + Math.abs(questionA.elo_rating - q.elo_rating) / 400)) *
        (1 / (q.times_shown + 1))
    );
    const indexB = weightedRandomIndex(weightsB);
    const questionB = remaining[indexB];

    const response: PairResponse = {
      questionA: { id: questionA.id, text: questionA.text },
      questionB: { id: questionB.id, text: questionB.text },
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error("Error fetching pair:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
