export default function LoadingTable() {
  return (
    <div className="w-full space-y-3 animate-pulse">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 py-3 px-4 rounded-sm"
        >
          <div className="h-4 w-8 bg-[var(--color-chalk)]/10 rounded-sm" />
          <div className="h-4 flex-1 bg-[var(--color-chalk)]/10 rounded-sm" />
          <div className="h-4 w-16 bg-[var(--color-chalk)]/10 rounded-sm" />
          <div className="h-4 w-16 bg-[var(--color-chalk)]/10 rounded-sm hidden md:block" />
        </div>
      ))}
    </div>
  );
}
