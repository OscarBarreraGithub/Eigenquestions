"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const linkClass = (href: string) => {
    const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href);
    return isActive
      ? "font-[family-name:var(--font-pigment)] text-[var(--color-chalk-yellow)] text-base border-b border-[var(--color-chalk-yellow)]"
      : "font-[family-name:var(--font-pigment)] text-[var(--color-chalk)] opacity-70 hover:opacity-100 text-base transition-opacity";
  };

  return (
    <nav className="fixed top-0 w-full z-[9999] min-h-14 px-4 sm:px-6 flex items-center justify-between bg-[#1a120d] border-b border-[rgba(0,0,0,0.3)] overflow-hidden">
      <Link
        href="/"
        className="font-[family-name:var(--font-aldenburg)] text-[var(--color-chalk-pink)] text-2xl tracking-tight"
      >
        Eigenquestions
      </Link>
      <div className="flex items-center gap-3 sm:gap-6">
        <Link href="/" className={linkClass("/")}>
          Vote
        </Link>
        <Link href="/leaderboard" className={linkClass("/leaderboard")}>
          Leaderboard
        </Link>
        <Link href="/submit" className={linkClass("/submit")}>
          Submit
        </Link>
        {/* Static topic explorer (vanilla page under /public/explore). Plain <a> = full document navigation, not client routing.
            Link to the explicit index.html so relative assets resolve at /explore/* regardless of trailing-slash handling. */}
        <a href="/explore/index.html" className={linkClass("/explore")}>
          Explore
        </a>
      </div>
    </nav>
  );
}
