"use client";

import { useState } from "react";

const MAX_CHARS = 500;

export default function SubmitPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<
    "idle" | "submitting" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const trimmed = text.trim();
    if (!trimmed) return;

    setStatus("submitting");
    setErrorMessage("");

    try {
      const res = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: trimmed }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.error || "Something went wrong");
      }

      setStatus("success");
      setText("");

      // Reset to idle after a few seconds so they can submit another
      setTimeout(() => setStatus("idle"), 4000);
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Something went wrong"
      );
    }
  }

  return (
    <main className="max-w-2xl mx-auto px-4 pt-28 pb-12 w-full">
      <div className="mb-8">
        <h1 className="font-[family-name:var(--font-chalk-title)] text-3xl md:text-5xl text-[var(--color-chalk)] mb-3">
          Submit a Question
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Textarea with chalk-box2 border */}
        <div className="relative">
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: "url(/images/chalk-box2.png)",
              backgroundSize: "100% 100%",
              backgroundRepeat: "no-repeat",
              opacity: 0.85,
            }}
          />
          <textarea
            value={text}
            onChange={(e) => {
              if (e.target.value.length <= MAX_CHARS) {
                setText(e.target.value);
              }
            }}
            placeholder=""
            rows={3}
            className="relative z-10 w-full bg-transparent text-[var(--color-chalk)] font-[family-name:var(--font-chalk-sprouts)] text-lg leading-relaxed p-5 md:p-6 resize-none outline-none placeholder:text-[var(--color-chalk-gray)] placeholder:opacity-50"
          />
        </div>

        {/* Character count + Submit button on same row */}
        <div className="flex items-center justify-between">
          <button
            type="submit"
            disabled={!text.trim() || status === "submitting"}
            className="relative px-6 py-2 cursor-pointer transition-all duration-200 hover:brightness-110 disabled:opacity-40 disabled:cursor-default group"
          >
            <div
              className="absolute inset-0 pointer-events-none transition-opacity duration-200"
              style={{
                backgroundImage: "url(/images/chalk-box1.png)",
                backgroundSize: "100% 100%",
                backgroundRepeat: "no-repeat",
                opacity: 0.85,
              }}
            />
            <span className="relative z-10 font-[family-name:var(--font-pigment)] text-sm uppercase tracking-widest text-[var(--color-chalk)] group-hover:text-[var(--color-chalk-yellow)] transition-colors">
              {status === "submitting" ? "Submitting..." : "Submit Question"}
            </span>
          </button>
          <span className="text-xs text-[var(--color-chalk-gray)] font-[family-name:var(--font-pigment)]">
            {text.length}/{MAX_CHARS}
          </span>
        </div>

        {/* Success message */}
        {status === "success" && (
          <p className="text-[var(--color-chalk-yellow)] text-sm font-[family-name:var(--font-pigment)] animate-fade-in">
            Question submitted! It will appear after review.
          </p>
        )}

        {/* Error message */}
        {status === "error" && (
          <p className="text-[var(--color-chalk-red)] text-sm font-[family-name:var(--font-pigment)] animate-fade-in break-words">
            {errorMessage}
          </p>
        )}
      </form>
    </main>
  );
}
