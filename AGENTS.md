# Eigenquestions

This is a question-conditioned physics explorer with a static frontend. Browser
and local agent share the deterministic geometry engine and canonical session.

- Read `Lab Notebook.md` and the active request/plan before resuming work.
- Use Node 22 or newer. `npm ci`, `npm run build`, `npm test`, and
  `npm run check:site` are the normal verification sequence. `npm start` serves
  the built site at `http://127.0.0.1:4173`.
- `web/` owns rendering; `lib/geometry/` owns retrieval and chart construction;
  `lib/protocol/` owns session transitions and the local bridge. Keep their shared
  contract in `docs/navigation-contract.md`. Do not implement a second engine.
- `data/navigation/` is the frozen, source-linked corpus. Preserve hashes,
  provenance, row alignment and dated scope when changing data.
- Q-003 now authorizes a bounded upload/read API and R2 storage for immutable
  contextual-view files. Keep scientific/model computation in the agent/browser;
  serve static assets directly. Activate storage only through authorized access,
  with explicit size/admission limits and no unapproved retention policy.
  Do not revive an old voting/quiz/submission route. The retired app is
  preserved at Git commit `9b7305541ca18ffd34bbe3786ee0cce75dea5633`; its existing
  D1 database must not be modified as part of this replacement.
- Coordinate owned files for the active request with the root agent. Root owns the one
  notebook, request plan, commits, checkpoint pushes and release. Implementation
  agents report evidence and blockers without committing or deploying separately.
- Record meaningful changes in the notebook with the request ID and evidence.
  Checkpoint commit bodies include the active request (currently `Request: Q-009`),
  the agent tag and contributors.
  Preserve unrelated work and verify the remote SHA after each authorized push.
- Browser QA limitations must remain explicit. A successful HTTP check does not
  establish browser behavior or public HTTPS-to-loopback compatibility.
