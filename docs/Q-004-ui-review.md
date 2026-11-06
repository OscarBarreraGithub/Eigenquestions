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

## First quiet implementation: source review

Reviewed the revised `web/index.html` and component-organized `web/styles.css`
after `/root/quiet_ui_sol` completed presentation work. No static layout blocker
found. The marketing layers and colored bands are removed, search options are
collapsed at all widths, New path stays visible, and 17px blue scientific
direction text has a clear selected treatment. The initial heading/input are
neutral. The full-view file/link controls form one secondary disclosure.

The phone Sources action now sits in the metadata row rather than consuming a
64px text rail. Its 44px-high target begins just below the scientific title;
the metadata reserves 66px on the right. The 320px header should fit from the
specified font sizes and padding. These are source-based expectations, not
measured browser results.

Concrete recommendations sent to the owners:

- Set a 44px minimum width on Agent and short path buttons, which currently
  have only a minimum height. The 320px header has room for this.
- Inset the direction button's focus outline so the scroll column does not
  clip its outer edge.
- After a row's Sources action, focus the visible Sources tab. The previous
  destination, `reading-heading`, is now visually hidden.
- Remove the repeated “Choose a direction” instruction from the dynamically
  generated step label and the repeated direction count beside column arrows.
  During initial loading, avoid giving the same progress message four places.

These are bounded corrections. Real screenshots at 320/390px and desktop widths,
plus keyboard and delayed-startup behavior, remain the next acceptance evidence.
