interface VotingFeedbackProps {
  show: boolean;
}

export default function VotingFeedback({ show }: VotingFeedbackProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`text-sm text-[var(--color-chalk-gray)] flex items-center gap-2 justify-center transition-opacity duration-300 ${
        show ? "opacity-100 animate-chalk-write" : "opacity-0"
      }`}
    >
      <svg
        className="w-4 h-4 text-[var(--color-chalk-yellow)]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 13l4 4L19 7"
        />
      </svg>
      Vote recorded
    </div>
  );
}
