import { NextResponse } from "next/server";
import { getPendingSubmissions } from "@/lib/db";
import type { SubmissionsResponse, ErrorResponse } from "@/lib/types";

export async function GET() {
  try {
    const submissions = await getPendingSubmissions();

    const response: SubmissionsResponse = { submissions };

    return NextResponse.json(response);
  } catch (error) {
    console.error("Error fetching submissions:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
