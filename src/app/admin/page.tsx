"use client";

import { useCallback, useEffect, useState } from "react";
import type { SubmissionRow } from "@/lib/types";

export default function AdminPage() {
  const [submissions, setSubmissions] = useState<SubmissionRow[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">(
    "loading"
  );
  const [errorMessage, setErrorMessage] = useState("");
  const [fadingIds, setFadingIds] = useState<Set<number>>(new Set());

  const fetchSubmissions = useCallback(async () => {
    setStatus("loading");
    setErrorMessage("");
    try {
      const res = await fetch("/api/admin/submissions");
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.error || "Failed to load submissions");
      }
      const data = await res.json();
      setSubmissions(data.submissions);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to load submissions"
      );
    }
  }, []);

  useEffect(() => {
    fetchSubmissions();
  }, [fetchSubmissions]);

  async function handleAction(id: number, action: "approve" | "reject") {
    try {
      const res = await fetch(`/api/admin/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.error || `Failed to ${action}`);
      }

      // Fade out then remove
      setFadingIds((prev) => new Set(prev).add(id));
      setTimeout(() => {
        setSubmissions((prev) => prev.filter((s) => s.id !== id));
        setFadingIds((prev) => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
      }, 300);
    } catch (err) {
      alert(err instanceof Error ? err.message : `Failed to ${action}`);
    }
  }

  const pendingCount = submissions.length;

  return (
    <main className="max-w-3xl mx-auto px-4 pt-20 pb-12 w-full">
      <div className="mb-8">
        <h1 className="font-[family-name:var(--font-chalk-title)] text-3xl md:text-5xl text-[var(--color-chalk)] mb-3">
          Admin
        </h1>
      </div>

      {status === "loading" && (
        <p className="text-[var(--color-chalk-gray)] text-sm font-[family-name:var(--font-pigment)]">
          Loading...
        </p>
      )}

      {status === "error" && (
        <div className="flex flex-col items-center justify-center gap-4 py-16 text-center">
          <p className="text-[var(--color-chalk-red)] text-sm">{errorMessage}</p>
          <button
            onClick={fetchSubmissions}
            className="text-[var(--color-chalk-yellow)] border border-[var(--color-chalk-yellow)]/30 rounded-sm px-4 py-2 hover:bg-[var(--color-chalk-yellow)]/10 transition-colors text-sm cursor-pointer"
          >
            Try again
          </button>
        </div>
      )}

      {status === "ready" && (
        <>
          <p className="text-sm text-[var(--color-chalk-gray)] font-[family-name:var(--font-pigment)] mb-6">
            {pendingCount} pending submission{pendingCount !== 1 ? "s" : ""}
          </p>

          {pendingCount === 0 ? (
            <p className="text-[var(--color-chalk-gray)] text-sm font-[family-name:var(--font-pigment)] py-16 text-center">
              No pending submissions
            </p>
          ) : (
            <div className="space-y-4">
              {submissions.map((submission) => (
                <div
                  key={submission.id}
                  className={`relative p-6 md:p-8 transition-all duration-300 ${
                    fadingIds.has(submission.id)
                      ? "opacity-0 scale-95"
                      : "opacity-100"
                  }`}
                >
                  {/* Chalk box border */}
                  <div
                    className="absolute inset-0 pointer-events-none"
                    style={{
                      backgroundImage: "url(/images/chalk-box2.png)",
                      backgroundSize: "100% 100%",
                      backgroundRepeat: "no-repeat",
                      opacity: 0.85,
                    }}
                  />

                  <div className="relative z-10">
                    <p className="font-[family-name:var(--font-chalk-sprouts)] text-lg md:text-xl leading-relaxed text-[var(--color-chalk)] mb-4 break-words overflow-wrap-anywhere">
                      {submission.text}
                    </p>

                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <span className="text-xs text-[var(--color-chalk-gray)] font-[family-name:var(--font-pigment)]">
                        {new Date(submission.submitted_at).toLocaleDateString(
                          "en-US",
                          {
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          }
                        )}
                      </span>

                      <div className="flex items-center gap-4">
                        <button
                          onClick={() =>
                            handleAction(submission.id, "approve")
                          }
                          className="text-[var(--color-chalk-yellow)] text-sm font-[family-name:var(--font-pigment)] uppercase tracking-widest hover:brightness-125 transition-all cursor-pointer"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() =>
                            handleAction(submission.id, "reject")
                          }
                          className="text-[var(--color-chalk-red)] text-sm font-[family-name:var(--font-pigment)] uppercase tracking-widest hover:brightness-125 transition-all cursor-pointer"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </main>
  );
}
