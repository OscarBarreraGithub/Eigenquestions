"use client";

interface QuestionCardProps {
  question: { id: number; text: string };
  onSelect: () => void;
  disabled: boolean;
  isWinner: boolean | null;
  position: "left" | "right";
  revealedElo?: number;
}

export default function QuestionCard({
  question,
  onSelect,
  disabled,
  isWinner,
  position,
  revealedElo,
}: QuestionCardProps) {
  const animationClass =
    position === "left" ? "animate-slide-in-left" : "animate-slide-in-right";

  const boxImage = position === "left" ? "/images/chalk-box1.png" : "/images/chalk-box2.png";

  let extraClasses = "";
  let overlayOpacity = 0.85;

  if (isWinner === true) {
    extraClasses = "scale-[1.02]";
    overlayOpacity = 1;
  } else if (isWinner === false) {
    extraClasses = "opacity-40 scale-[0.98]";
    overlayOpacity = 0.5;
  }

  return (
    <button
      onClick={onSelect}
      disabled={disabled}
      aria-label={`Vote for: ${question.text}`}
      className={`
        ${animationClass}
        relative p-6 md:p-8 cursor-pointer min-w-0 overflow-hidden
        transition-all duration-200 flex-1 text-left flex flex-col justify-between gap-4
        ${!disabled && isWinner === null ? "hover:-translate-y-1 hover:brightness-110" : ""}
        ${disabled ? "cursor-default" : ""}
        ${extraClasses}
        group
      `}
    >
      {/* Chalk box border image */}
      <div
        className="absolute inset-0 pointer-events-none transition-opacity duration-200"
        style={{
          backgroundImage: `url(${boxImage})`,
          backgroundSize: "100% 100%",
          backgroundRepeat: "no-repeat",
          opacity: overlayOpacity,
        }}
      />

      <p className="font-question text-xl md:text-3xl leading-relaxed text-[var(--color-chalk)] relative z-10 break-words overflow-wrap-anywhere">
        {question.text}
      </p>
      {revealedElo !== undefined && (
        <div className="flex items-center justify-end relative z-10">
          <span className="text-xs font-mono bg-[var(--color-board-dark)] px-2 py-1 rounded-sm text-[var(--color-chalk-gray)] animate-fade-in">
            ELO: {revealedElo}
          </span>
        </div>
      )}
    </button>
  );
}
