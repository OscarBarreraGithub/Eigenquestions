export default function OrDivider() {
  return (
    <>
      {/* Desktop: centered text */}
      <div className="hidden md:flex items-center justify-center px-3">
        <span className="font-[family-name:var(--font-pigment)] text-[var(--color-chalk-gray)] text-sm select-none">or</span>
      </div>

      {/* Mobile: centered text */}
      <div className="flex md:hidden items-center justify-center py-1">
        <span className="font-[family-name:var(--font-pigment)] text-[var(--color-chalk-gray)] text-sm select-none">or</span>
      </div>
    </>
  );
}
