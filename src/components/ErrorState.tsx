"use client";

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
      <p className="text-[var(--color-chalk-red)] text-sm break-words">{message}</p>
      <button
        onClick={onRetry}
        className="text-[var(--color-chalk-yellow)] border border-[var(--color-chalk-yellow)]/30 rounded-sm px-4 py-2 hover:bg-[var(--color-chalk-yellow)]/10 transition-colors text-sm"
      >
        Try again
      </button>
    </div>
  );
}
