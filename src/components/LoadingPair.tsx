export default function LoadingPair() {
  return (
    <div className="flex flex-col md:flex-row gap-4 md:gap-8 items-stretch max-w-5xl w-full">
      <SkeletonCard />
      <div className="hidden md:flex flex-col items-center justify-center px-2">
        <div className="w-px flex-1 bg-[var(--color-chalk)]/15" />
        <span className="text-[var(--color-chalk-gray)] opacity-40 text-sm py-3">or</span>
        <div className="w-px flex-1 bg-[var(--color-chalk)]/15" />
      </div>
      <div className="flex md:hidden items-center gap-4 py-2">
        <div className="h-px flex-1 bg-[var(--color-chalk)]/15" />
        <span className="text-[var(--color-chalk-gray)] opacity-40 text-sm">or</span>
        <div className="h-px flex-1 bg-[var(--color-chalk)]/15" />
      </div>
      <SkeletonCard />
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="bg-[var(--color-board-light)] border border-[var(--color-chalk)]/15 rounded-sm p-8 flex-1 flex flex-col gap-4 animate-pulse">
      <div className="h-5 bg-[var(--color-chalk)]/10 rounded-sm w-full" />
      <div className="h-5 bg-[var(--color-chalk)]/10 rounded-sm w-4/5" />
      <div className="h-5 bg-[var(--color-chalk)]/10 rounded-sm w-3/5" />
      <div className="mt-auto pt-4">
        <div className="h-3 bg-[var(--color-chalk)]/10 rounded-sm w-16" />
      </div>
    </div>
  );
}
