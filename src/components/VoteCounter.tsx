"use client";

interface VoteCounterProps {
  count: number;
}

export default function VoteCounter({ count }: VoteCounterProps) {
  return (
    <div className="text-xs font-[family-name:var(--font-pigment)] text-[var(--color-chalk-gray)] opacity-50">
      <span key={count} className="font-mono tabular-nums animate-subtle-bounce inline-block">
        {count}
      </span>{" "}
      vote{count !== 1 ? "s" : ""} this session
    </div>
  );
}
