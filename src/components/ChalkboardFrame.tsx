export default function ChalkboardFrame() {
  return (
    <div
      className="fixed inset-0 top-14 z-[9998] pointer-events-none"
      style={{
        borderWidth: "clamp(10px, 2vw, 28px)",
        borderStyle: "solid",
        borderImage: `linear-gradient(
          155deg,
          #312420 0%,
          #2a1f1a 20%,
          #2f231d 40%,
          #261c16 60%,
          #2d211c 80%,
          #2a1f1a 100%
        ) 1`,
        boxShadow: `
          inset 0 0 15px 5px rgba(0,0,0,0.4),
          inset 0 0 3px 1px rgba(0,0,0,0.6),
          0 0 10px 2px rgba(0,0,0,0.3)
        `,
      }}
    />
  );
}
