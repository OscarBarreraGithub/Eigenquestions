import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { approveSubmission } from "@/lib/db";
import type { ApproveResponse, ErrorResponse } from "@/lib/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const { id } = body;

    if (typeof id !== "number" || !Number.isInteger(id)) {
      return NextResponse.json(
        { error: "id must be an integer" } satisfies ErrorResponse,
        { status: 400 }
      );
    }

    const { questionId, startingElo } = await approveSubmission(id);

    const response: ApproveResponse = {
      success: true,
      questionId,
      startingElo,
    };

    return NextResponse.json(response);
  } catch (error) {
    if (error instanceof Error) {
      if (error.message === "Submission not found") {
        return NextResponse.json(
          { error: "Submission not found" } satisfies ErrorResponse,
          { status: 404 }
        );
      }
      if (error.message === "Submission already reviewed") {
        return NextResponse.json(
          { error: "Submission already reviewed" } satisfies ErrorResponse,
          { status: 400 }
        );
      }
    }
    console.error("Error approving submission:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
