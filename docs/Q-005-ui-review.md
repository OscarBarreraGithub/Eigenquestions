# Q-005 — Clear entry and choices at each step

UI owner/reviewer: `/root/quiet_ui_review_sol` (Sol). Runtime, display excerpts
and scientific history are owned by `/root/navigator_protocol` (Astra). Root owns
the plan, notebook, integration and release.

The reported long one-loop paragraph was displayed as an input value, page
heading, breadcrumb and historical heading, then repeated among directions.
Opening the bare site also restored that last view automatically. Those behaviors
made a selected representative source look like the site's permanent subject.
Shorter text alone cannot repair a repeated scientific state or reconstruct
missing historical alternatives.

## Presentation and controller contract

- Bare home shows a modest **Explore physics** heading and search. It offers
  **Resume last view** with an extractive description of saved context rather
  than silently opening it. A saved companion has a separate **Reconnect agent**
  action. Existing explicit view/focus/companion URLs remain controller-owned.
- `home-heading` is visible only on home. `resume-prior`, `resume-label`,
  `resume-view` and `resume-companion` form the explicit resume section.
  `exploration-workspace` starts hidden and contains the path, current focus,
  actual step choices and literature. Save/load remains outside it and reachable.
- The current focus is one concise display excerpt. The query input is a new
  draft, not another copy of the accepted paragraph. `full-question-details`
  is labeled **Full context** and exposes the complete authoritative question or
  method description once through `full-question-text`.
  `full-question-source` links the representative paper when one is known.
  Evidence descriptions and canonical queries are never shortened by CSS.
- Each column holds the real choices accepted at that visited step. Prior
  columns and current choices have distinct headings. A **Followed** marker
  identifies a selected historical direction beyond color; **Return to step N**
  can identify an exact cycle. A typed refinement must remain distinguishable
  from a selected source direction. Runtime supplies these facts.
- Native rows can include a quiet genuine paper title and **Method**/**Question**
  facet. These source facts distinguish choices whose description excerpts begin
  similarly, without inventing synthesized topic names. Supplied groups retain
  their authored labels and are identified as such.
- `navigator-note` explains that the path/arrows revisit earlier choices and
  permit branching. The controller hides it for a single scientific step.
  On phones the 44px arrows remain inside the column header and the note precedes
  the frame, making earlier alternatives discoverable before horizontal scrolling.

The quiet white/gray and familiar blue-link treatment is retained. Historical
columns use roughly 300–320px widths and current choices roughly 380–400px before
using available space. Compact rows retain 17px text and separate source actions.
The complete text remains available in the full-focus disclosure and evidence;
there is no line clamp hiding source passages.

## Verification so far

Read [the Q-005 plan](Q-005-plan.md) and coordinated the DOM before changing owned
files. A parser check confirms balanced HTML, 74 unique IDs and all agreed new
selectors. No Mac browser was used. Full runtime checks and Slurm screenshots
are pending; these source changes are not visual acceptance evidence yet.

The shared `lib/protocol/presentation.mjs` is now explicitly copied and required
by the static build, and included among 17 deployed asset hash checks. The
publication regression verifies the built copy matches source and rejects a
stale presentation helper even when all other 16 assets and 32 retired-route
checks pass. A fresh `npm run build`, `npm run check:site` (71 assets, 41 verified
corpus shards), and the targeted publication test all pass. This does not replace
the pending browser/visual acceptance.
