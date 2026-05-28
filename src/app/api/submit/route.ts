import { NextResponse } from "next/server";
import { NextRequest } from "next/server";
import { createSubmission } from "@/lib/db";
import type { SubmitResponse, ErrorResponse } from "@/lib/types";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const { text } = body;

    if (typeof text !== "string" || text.trim().length === 0) {
      return NextResponse.json(
        { error: "text must be a non-empty string" } satisfies ErrorResponse,
        { status: 400 }
      );
    }

    const trimmed = text.trim();

    if (trimmed.length > 500) {
      return NextResponse.json(
        { error: "text must be 500 characters or fewer" } satisfies ErrorResponse,
        { status: 400 }
      );
    }

    const id = await createSubmission(trimmed);

    const response: SubmitResponse = { success: true, id };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    console.error("Error creating submission:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
