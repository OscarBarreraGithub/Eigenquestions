export const K_FACTOR = 32;
export const DEFAULT_RATING = 1500;
export const RATING_FLOOR = 100;

export function calculateElo(
  winnerRating: number,
  loserRating: number
): { newWinnerRating: number; newLoserRating: number } {
  const expectedWinner =
    1 / (1 + Math.pow(10, (loserRating - winnerRating) / 400));
  const expectedLoser = 1 - expectedWinner;

  const newWinnerRating = Math.max(
    RATING_FLOOR,
    winnerRating + K_FACTOR * (1 - expectedWinner)
  );
  const newLoserRating = Math.max(
    RATING_FLOOR,
    loserRating + K_FACTOR * (0 - expectedLoser)
  );

  return { newWinnerRating, newLoserRating };
}
