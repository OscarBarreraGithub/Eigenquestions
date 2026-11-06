# Q-004 — A quieter text-first explorer

The owner asks for a familiar, reliable, minimal interface: sharp readable text,
less competing attention, and scientific navigation before visual treatment.
Q-001's question-dependent geometry and Q-003's complete contextual views remain
the foundation. This is a presentation change, not a new scientific hierarchy.

## Baseline and concrete reduction

The [previous desktop](evidence/q002/browser-v2/desktop-viewport.png) and
[phone](evidence/q002/browser-v2/mobile-top-viewport.png) screenshots show the
problem: a large colored masthead, subtitle and version badge, promotional
heading, search settings, status, path, current-question eyebrow, context,
direction count and another step heading all precede the research text. On the
390px phone image the first direction starts around 540px down the page.

The new shell uses one compact wordmark with visible Agent and New path actions.
The search field leads directly to a small Search options disclosure, the status,
and the path. Search settings are collapsed at every width, while the current
approach remains available beside the disclosure. The accepted current question
is the only visible page heading above the navigator. The HTML initially shows a
neutral loading state; restoring a saved focus must not flash a hardcoded topic.

The navigator stays a dynamic Miller-column browser. Directions use readable
17px linked text with simple gray rules. The chosen row has a modest gray fill,
left rule and stronger text. The wide screen keeps the separate Sources action;
on a phone it sits beside the source count below the question, returning the
full row width to the scientific label. The primary action and its Sources action
remain separate keyboard targets, each at least 44px high. Current direction text
has a readable line-length limit without changing its computed label.

Sources and optional geometry follow the navigator as plain tabs, without a
second promotional heading. Source descriptions use 17px Georgia with generous
line spacing; paper titles, dates and provenance remain legible. The palette is
black/gray text with familiar blue links, neutral borders and white space. There
are no colored masthead bands, tinted current-column headers or decorative cards.

Save, load and share is one collapsed disclosure below the source reading area.
It contains the coordinated Save link, Download view, Download session, Share
focus and Open file actions, the returned-link field and status, and a file-drop
button. Links are shown only after the protocol reports a durable save. Snapshot
or continuation limits have a dedicated status beside the current context.

## Preservation and verification

Existing selector IDs and tab semantics are preserved. The search options use the
existing keyboard-operable button and aria-expanded contract. Focus outlines,
44px primary targets in both dimensions, scrollable paths, mobile columns and
reduced-motion rules remain. Direction focus outlines are inset so column clipping
does not hide them. The favicon is a plain monochrome E.

HTML/CSS own presentation; the protocol agent owns startup restoration, imports,
stored-view upload and actual scientific state. The static-site smoke test now
checks the neutral startup shell instead of the removed promotional heading.
The coordinator will build after the coordinated freeze and run real Chromium
QA on Slurm at 320/390px and 1024/1440px. The standalone
[`q004_visual_capture.py`](../tests/integration/q004_visual_capture.py) fixture
requires `SLURM_JOB_ID`, uses the actual prior engine/companion with frozen new
HTML/CSS, and captures KK, dark matter, empty path, settings, agent instructions
and source reading. That early fixture does not establish the new startup or
stored-view behavior. No local Mac browser was used. Browser layout and
drop/import behavior remain unverified until their evidence is saved.
