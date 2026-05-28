// Database row types (snake_case, internal)
export interface QuestionRow {
  id: number;
  text: string;
  elo_rating: number;
  times_shown: number;
  times_won: number;
  created_at: string;
  updated_at: string;
}

export interface VoteRow {
  id: number;
  winner_id: number;
  loser_id: number;
  winner_elo_before: number;
  loser_elo_before: number;
  winner_elo_after: number;
  loser_elo_after: number;
  created_at: string;
}

// API types (camelCase, external)
export interface QuestionBrief {
  id: number;
  text: string;
}

export interface PairResponse {
  questionA: QuestionBrief;
  questionB: QuestionBrief;
}

export interface VoteRequest {
  winnerId: number;
  loserId: number;
}

export interface VoteResponse {
  success: true;
  winnerNewElo: number;
  loserNewElo: number;
}

export interface LeaderboardEntry {
  rank: number;
  id: number;
  text: string;
  eloRating: number;
  timesShown: number;
  timesWon: number;
  winRate: number;
}

export interface LeaderboardResponse {
  questions: LeaderboardEntry[];
  totalVotes: number;
}

export interface StatsResponse {
  totalQuestions: number;
  totalVotes: number;
}

export interface ErrorResponse {
  error: string;
}

export interface SubmissionRow {
  id: number;
  text: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_at: string;
  reviewed_at: string | null;
}

export interface SubmitRequest {
  text: string;
}

export interface SubmitResponse {
  success: true;
  id: number;
}

export interface SubmissionsResponse {
  submissions: SubmissionRow[];
}

export interface ApproveRequest {
  id: number;
}

export interface ApproveResponse {
  success: true;
  questionId: number;
  startingElo: number;
}
