import { getCloudflareContext } from "@opennextjs/cloudflare";
import { calculateElo } from "./elo";
import type { QuestionRow, StatsResponse, SubmissionRow } from "./types";

async function getDb(): Promise<D1Database> {
  const { env } = await getCloudflareContext({ async: true });
  return env.DB;
}

export async function getAllQuestions(): Promise<QuestionRow[]> {
  const db = await getDb();
  const result = await db.prepare("SELECT * FROM questions").all<QuestionRow>();
  return result.results;
}

export async function getQuestionById(
  id: number
): Promise<QuestionRow | null> {
  const db = await getDb();
  return db.prepare("SELECT * FROM questions WHERE id = ?").bind(id).first<QuestionRow>();
}

export async function recordVote(
  winnerId: number,
  loserId: number
): Promise<{ newWinnerRating: number; newLoserRating: number }> {
  const db = await getDb();

  const winner = await db
    .prepare("SELECT * FROM questions WHERE id = ?")
    .bind(winnerId)
    .first<QuestionRow>();
  const loser = await db
    .prepare("SELECT * FROM questions WHERE id = ?")
    .bind(loserId)
    .first<QuestionRow>();

  if (!winner || !loser) {
    throw new Error("Question not found");
  }

  const { newWinnerRating, newLoserRating } = calculateElo(
    winner.elo_rating,
    loser.elo_rating
  );

  // Use batch for atomic operations (D1's equivalent of transactions)
  await db.batch([
    db
      .prepare(
        `UPDATE questions
         SET elo_rating = ?, times_shown = times_shown + 1, times_won = times_won + 1, updated_at = datetime('now')
         WHERE id = ?`
      )
      .bind(newWinnerRating, winnerId),
    db
      .prepare(
        `UPDATE questions
         SET elo_rating = ?, times_shown = times_shown + 1, updated_at = datetime('now')
         WHERE id = ?`
      )
      .bind(newLoserRating, loserId),
    db
      .prepare(
        `INSERT INTO votes (winner_id, loser_id, winner_elo_before, loser_elo_before, winner_elo_after, loser_elo_after)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
      .bind(
        winnerId,
        loserId,
        winner.elo_rating,
        loser.elo_rating,
        newWinnerRating,
        newLoserRating
      ),
  ]);

  return { newWinnerRating, newLoserRating };
}

export async function getLeaderboard(): Promise<{
  questions: QuestionRow[];
  totalVotes: number;
}> {
  const db = await getDb();
  const questionsResult = await db
    .prepare("SELECT * FROM questions ORDER BY elo_rating DESC")
    .all<QuestionRow>();
  const countResult = await db
    .prepare("SELECT COUNT(*) as count FROM votes")
    .first<{ count: number }>();
  return {
    questions: questionsResult.results,
    totalVotes: countResult?.count ?? 0,
  };
}

export async function getStats(): Promise<StatsResponse> {
  const db = await getDb();
  const qResult = await db
    .prepare("SELECT COUNT(*) as count FROM questions")
    .first<{ count: number }>();
  const vResult = await db
    .prepare("SELECT COUNT(*) as count FROM votes")
    .first<{ count: number }>();
  return {
    totalQuestions: qResult?.count ?? 0,
    totalVotes: vResult?.count ?? 0,
  };
}

export async function createSubmission(text: string): Promise<number> {
  const db = await getDb();
  const result = await db
    .prepare("INSERT INTO submissions (text) VALUES (?)")
    .bind(text)
    .run();
  return result.meta.last_row_id as number;
}

export async function getPendingSubmissions(): Promise<SubmissionRow[]> {
  const db = await getDb();
  const result = await db
    .prepare(
      "SELECT * FROM submissions WHERE status = 'pending' ORDER BY submitted_at ASC"
    )
    .all<SubmissionRow>();
  return result.results;
}

export async function approveSubmission(
  id: number
): Promise<{ questionId: number; startingElo: number }> {
  const db = await getDb();

  const submission = await db
    .prepare("SELECT * FROM submissions WHERE id = ?")
    .bind(id)
    .first<SubmissionRow>();

  if (!submission) {
    throw new Error("Submission not found");
  }

  if (submission.status !== "pending") {
    throw new Error("Submission already reviewed");
  }

  const medianRow = await db
    .prepare(
      "SELECT elo_rating FROM questions ORDER BY elo_rating LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM questions)"
    )
    .first<{ elo_rating: number }>();

  const startingElo = medianRow ? medianRow.elo_rating : 1500;

  // Use batch for atomicity
  const batchResults = await db.batch([
    db
      .prepare("INSERT INTO questions (text, elo_rating) VALUES (?, ?)")
      .bind(submission.text, startingElo),
    db
      .prepare(
        "UPDATE submissions SET status = 'approved', reviewed_at = datetime('now') WHERE id = ?"
      )
      .bind(id),
  ]);

  const insertResult = batchResults[0];
  const questionId = insertResult.meta.last_row_id as number;

  return { questionId, startingElo };
}

export async function rejectSubmission(id: number): Promise<void> {
  const db = await getDb();

  const result = await db
    .prepare(
      "UPDATE submissions SET status = 'rejected', reviewed_at = datetime('now') WHERE id = ? AND status = 'pending'"
    )
    .bind(id)
    .run();

  if (result.meta.changes === 0) {
    const existing = await db
      .prepare("SELECT * FROM submissions WHERE id = ?")
      .bind(id)
      .first();
    if (!existing) {
      throw new Error("Submission not found");
    }
    throw new Error("Submission already reviewed");
  }
}

export { getDb };
