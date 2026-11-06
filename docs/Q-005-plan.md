# Q-005 — Clear entry and understandable choices

Request summary: explain and fix the unsolicited opening to the long KK one-loop
method description, its repeated appearance, and the unclear adjacent choices at
each visited level. This refines Q-001's contextual navigation and Q-004's quiet
text interface; it does not introduce a fixed topic tree.

## Atomic requirements

1. A bare homepage opens a neutral new path. Offer an explicit, clearly labeled
   Resume for a saved exploration without overwriting it merely by opening home.
2. Explicit view, focus and companion links still open their intended destination.
   An old local session must not override an explicit destination.
3. Keep navigation labels concise and intelligible. Retain the full query and
   source evidence, including scientific qualifiers, in an accessible location.
   Display shortening must not change the canonical scientific computation.
4. Each visited step shows its actual available choices, marks the choice taken,
   and allows a branch from an earlier alternative. A typed refinement is labeled
   as such, rather than falsely marking a source direction as selected.
5. Current choices and earlier alternatives are visibly distinct. Make previous
   steps easy to inspect on phone and desktop, with legible text and large targets.
6. Diagnose actual source/group repetition as well as repeated UI text. Do not
   hide distinct evidence or call method descriptions physical questions. Record
   the limitations of representative-source labels and any unresolved semantic
   redundancy rather than pretending the static renderer synthesizes topics.
   An exact native return to an already visited state must be recognized as a
   revisit, not appended as apparent additional depth. Keep the scientifically
   relevant direction/evidence available and label its destination honestly.
7. Preserve exact authored capsule views and history, unknown-builder safety,
   stale-request guards, user drafts, source links, optional graph orientation,
   frozen corpus hashes, and scientific computation identity. Do not substitute
   newly computed groups for unavailable historical authored groups.
8. Reproduce the reported 1303.2661 method path. Verify bare startup with saved
   data, explicit Resume, direct destinations, selected and unselected historical
   alternatives, branching, New path, full evidence and phone/desktop rendering.
9. Save meaningful findings and failures in the one notebook, commit intended
   changes, push and verify the published version after the browser gate passes.

## Ownership and evidence

- `/root/navigator_protocol` (Astra): controller, display/history helpers and
  focused regression harness. Coordinate DOM names with Sol before editing.
- `/root/quiet_ui_review_sol` (Sol): HTML/CSS and visual review. Quiet text-first
  design, no scientific engine changes.
- `/root/stored_view_backend` (Astra): independent real-data repetition and
  alternatives audit, read-only runtime review.
- `/root`: integrated behavior review, notebook, Git checkpoints, Slurm browser
  validation and existing authorized GitHub release.

Browser checks run through the existing authorized FASRC/Slurm route. Hosted
storage activation remains a separate, previously recorded access prerequisite.

## Initial findings (not completed validation)

The route loader restores local capsule/session/companion state on a bare initial
visit. Q-004 removed the initial KK flash but retained that implicit restoration.
Native direction selection sets the next query to the full representative source
description. The same query is displayed in the input, heading, path and history.
The reported paragraph occurs in the frozen corpus as one method unit for paper
1303.2661. The user's actual browser storage has not been inspected.

An earlier experiment shortening scientific selection queries did not improve
context retention; do not repeat that as an untested display fix. Historical
groups must be the ones actually accepted, not a reconstruction from today's
current selection. Completion evidence will be linked here after validation.

The independent audit subsequently reproduced two-state cycles after repeated
native direction selection. This is a second defect, beyond duplicate rendering.
The bounded repair should reuse identical canonical history states and label
returns; suppressing source evidence or changing retrieval to manufacture novelty
is not justified by this finding. [Audit](Q-005-navigation-audit.md).

## Release gate

All nine requirements are implemented at the stated source-based scope. The
10-check focused browser suite covers the reported method, exact returns,
authored-history protection, explicit entry and stable phone/desktop navigation.
The 14-check stored-view and 19-check interaction suites pass, as does the amended
14-check legacy/MCP/geometry suite (57 browser checks in total). All 35 local tests
and 41 corpus-shard checks pass. Sol and root accept the screenshots. See
[evidence](evidence/q005/browser-v3/), [legacy completion](evidence/q005/legacy-final/)
and [visual review](Q-005-ui-review.md). Public release verification follows.

The fix identifies exact state returns and distinguishes representative source
facets; it does not claim optimal semantic clusters or synthesized research
question labels. Old scientific sessions are preserved, with recorded returns
identified in their presentation.

Public release `f0e782d` is verified: deployment 42278851870 succeeded, all 17 asset
hashes and 32 retired routes match, and public Slurm job 58370368 passed all 43 checks
(focused 10, full-view 14, legacy/public 19). Q-005 is complete at this scope.
[Public evidence](evidence/q005/public-v1/) · [receipt](evidence/q005/public-v1-job.json).
