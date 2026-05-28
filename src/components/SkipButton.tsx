"use client";

interface SkipButtonProps {
  onSkip: () => void;
  disabled: boolean;
}

export default function SkipButton({ onSkip, disabled }: SkipButtonProps) {
  return (
    <button
      onClick={onSkip}
      disabled={disabled}
      aria-label="Skip this pair and load new questions"
      className="relative px-5 py-1.5 font-[family-name:var(--font-pigment)] text-2xl text-[var(--color-chalk-gray)] hover:text-[var(--color-chalk)] transition-all disabled:opacity-30 disabled:cursor-default group"
    >
      <div
        className="absolute inset-0 pointer-events-none opacity-60 group-hover:opacity-80 transition-opacity duration-200"
        style={{
          backgroundImage: "url(/images/chalk-box2.png)",
          backgroundSize: "100% 100%",
          backgroundRepeat: "no-repeat",
        }}
      />
      <span className="relative z-10">Skip</span>
    </button>
  );
}
