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

## First actual screenshots: accept home/desktop, withhold mobile signoff

Reviewed source `d87bb2b`, Slurm job `58361795`, Chromium 145.0.7632.6;
[job receipt](evidence/q005/browser-v1-job.json). Viewed the reported-method
desktop/390px captures, current and earlier columns at 390/320px, the longer
desktop path, and the saved neutral home. The
[runtime report](evidence/q005/browser-v1/q005_navigation_acceptance/q005-navigation-acceptance.json)
records nine passed checks before a separate direct-route harness assertion
failed; these screenshots do not constitute a fully passed run.

The [neutral home](evidence/q005/browser-v1/q005_navigation_acceptance/q005-saved-neutral-home-390.png)
is clear: search leads, the saved method is a meaningful optional resume entry,
and it is not silently selected. The
[desktop method](evidence/q005/browser-v1/q005_navigation_acceptance/q005-reported-method-1440-viewport.png)
has a blank new draft, concise current excerpt, one Full context disclosure, real
adjacent directions and useful paper-title/Method facets. The longer
[desktop history](evidence/q005/browser-v1/q005_navigation_acceptance/q005-1440-current-viewport.png)
distinguishes Choices then/Next choices, Followed and Return to step labels.
The displayed scientific evidence is more informative than a count alone.

**Material issue:** the
[reported-method phone](evidence/q005/browser-v1/q005_navigation_acceptance/q005-reported-method-390-viewport.png)
is captured between columns, with earlier text clipped on the left and only a
narrow sliver of the current list on the right. The
[390px current capture](evidence/q005/browser-v1/q005_navigation_acceptance/q005-390-current-viewport.png)
shows historical Step 2 rather than the current Step 5. The
[320px capture](evidence/q005/browser-v1/q005_navigation_acceptance/q005-320-current-viewport.png)
has the same alignment problem. Earlier-column captures are readable, with
obvious source facets and targets, so the underlying typography is sound.

Requested bounded runtime corrections: anchor a real visible column after
resize/programmatic navigation; wait for and assert settled current-column
geometry in the harness; keep the selected historical row visible below its
sticky heading. The fourth selected choice in the first desktop column is
otherwise below the viewport, hiding its Followed marker. Do not fix these by
shrinking text. The evidence cannot yet distinguish an intermediate snap
animation from a persistent resize defect; either requires a stable new capture
before mobile visual acceptance. No unrelated cosmetic changes requested.

The first phone capture also exposed an unbounded current breadcrumb inherited
from Q-004. Its beginning could be clipped when the strip was scrolled to its
end. The path now takes the remaining row width explicitly, and its current
button is bounded to that width (up to 300px), using an ending ellipsis. The
first words and 44px target remain available; full context is still in the
disclosure. Protocol was asked to verify the application's actual breadcrumb
alignment rather than relying on an arbitrary forced scroll position. This
small CSS correction awaits the next actual screenshots.
