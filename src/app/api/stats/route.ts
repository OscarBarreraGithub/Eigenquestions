import { NextResponse } from "next/server";
import { getStats } from "@/lib/db";
import type { StatsResponse, ErrorResponse } from "@/lib/types";

export async function GET() {
  try {
    const stats: StatsResponse = await getStats();
    return NextResponse.json(stats);
  } catch (error) {
    console.error("Error fetching stats:", error);
    return NextResponse.json(
      { error: "Internal server error" } satisfies ErrorResponse,
      { status: 500 }
    );
  }
}
