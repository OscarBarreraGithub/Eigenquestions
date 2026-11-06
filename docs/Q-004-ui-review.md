# Q-004 — Independent interface review

Reviewed by `/root/quiet_ui_review_sol`, 2026-11-06. Read-only review of the
existing implementation and actual [desktop](evidence/q002/browser-v2/desktop-viewport.png)
and [mobile](evidence/q002/browser-v2/mobile-top-viewport.png) screenshots.
This records the baseline findings; it does not certify the revised interface.

The mobile screenshot places the first scientific direction roughly 540 pixels
below the top. Brand, promotional heading, search, options, status, path, current
question, context, column navigation and another step heading compete before
the useful text. The interface needs fewer layers, rather than smaller type.

- Keep a modest wordmark and a visible **New path** action. Replace the
  promotional heading with a plain search label. Collapse search options on
  desktop as well as mobile; do not put explanatory copy inside a large card.
- Show the current question once, with the actual path and dynamic Miller
  columns immediately nearby. Remove uppercase eyebrows, repeated direction
  counts, “Choose a direction” banners, and thick red rules. Use one quiet
  status line for loading/errors and source counts.
- Retain 16–17px direction text, comfortable line spacing, native-looking form
  controls, obvious keyboard focus and 44px targets. Use familiar link styling
  for actions and a modest selected-row treatment. Density should come from
  reducing chrome and gaps, rather than reducing scientific text.
- Bound or balance desktop column widths. The growing final column currently
  fills roughly 1,000px beside a 350px history column, producing long truncated
  strips rather than a readable Miller browser. A roughly 420–520px current
  column allows full labels to wrap. Preserve earlier columns and current-path
  selection; this is not a fixed taxonomy.
- The 64px Sources rail costs about one fifth of the mobile reading width.
  Consider a separate 44px-high text action near the row metadata. Following a
  direction and inspecting evidence must remain clearly distinct actions.
- Keep file import, contextual-view export/upload and persisted-link controls
  in one secondary save/open disclosure. An agent-setup dialog can explain the
  companion without becoming the primary page content.

The visible startup jump has a concrete cause: `web/index.html` names
Kaluza–Klein towers in both the input and current heading, while `boot()` waits
for asynchronous initialization before `render()` paints restored state.
`web/compute-worker.js` also supplies KK as its fresh-session default. Paint a
neutral shell until the actual URL/session target is known, or synchronously
paint validated saved context before loading the corpus. A stored-view URL
must take precedence over unrelated local state. Verify the pre-init DOM under
delayed loads, not only the final rendered state.
