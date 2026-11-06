# Q-002 visual reference and independent review

Reviewer: `/root/v2_design_review`. Initial source inspection: 2026-11-06 UTC.
This document distinguishes observed reference facts from proposed Eigenquestions
design choices. Reference screenshots and computed styles were captured in the
authorized Slurm environment and independently inspected; no local browser was
launched. Product screenshot review is pending.

## References inspected

- Historical Eigenquestions source at commit
  `9b7305541ca18ffd34bbe3786ee0cce75dea5633`, especially
  `public/explore/tree/{index.html,style.css,app.js}` (read using `git show`).
- Read-only local prototype:
  `/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/text-explorer-v4/`.
- Actual arXiv [recent list](https://arxiv.org/list/hep-th/recent),
  [search](https://arxiv.org/search/?query=quantum+gravity&searchtype=all), and
  [abstract](https://arxiv.org/abs/2209.09249), retrieved through HTTP and web tools.
  Stylesheets below are the files linked by the live pages, not recalled styling.

## What to recover from the old viewer

The historical viewer presents an almost continuous sheet: heading and search,
path, a horizontally scrolling column strip, then a centered document-like
detail area. One selected row has a thin accent edge and a pale fill. Blue text
signals a destination. Rules separate columns and sections without raised cards.
Choosing a row retains the previous column and opens the next; selecting an
earlier path segment rebuilds the corresponding columns. The active rightmost
column scrolls into view. The point is the visible relationship between choices.

The old deployed source uses white, `#222222` text, `#6b6b6b` secondary text,
`#dddddd` rules, `#1a0dab` links, and `#b31b1b` accent. Controls use Helvetica Neue
with Helvetica/Arial fallbacks; explanatory prose uses Georgia. Its 13px body,
tiny controls, and single-line truncated rows should **not** be restored.

The v4 prototype already fixes the important long-label failure: labels wrap,
columns are 380px rather than 312px, column headings remain visible, and mobile
columns occupy 88vw. It uses real anchors and exposes the current row. These are
better starting details than the older clickable `div` rows.

The old hierarchy is not the new semantic model. In v2, a column should mean
“directions available at this point in this path,” not a permanent taxonomy level.
Historical columns must preserve their actual choices and selection. If an old
step has no cached view, show its real question and a Restore control; do not
invent reconstructed choices. A new context produces a new current column.
About five substantive choices should be
visible without a wall of giant cards or a plot taking over the workspace.

## What live arXiv actually supplies

The current shared header is dark ink rather than the familiar legacy red.
Its current design system defines white canvas, ink `#1c1a17`, muted `#6b6459`,
blue links `#1565c0`, pale-blue accent `#a5d6fe`, rules `#dad8d6`, and control
boundaries `#89837a`. It names IBM Plex Sans as its sans family. Header minimum
height is 52px. Its spacing follows 4px steps, and it differentiates decorative
rules from stronger interactive boundaries. These are observations of the
[live component CSS](https://static.arxiv.org/static/design-system/latest/design-system-components.css)
and [font declarations](https://static.arxiv.org/static/design-system/latest/fonts.css).

The live list body still specifies Lucida Grande/Helvetica/Arial/Verdana, white
background and black text. Titles are bold with authors and smaller subject
metadata below. These are stacked bibliographic entries, with weight and spacing
carrying hierarchy rather than containers.
[Browse CSS](https://arxiv.org/static/browse/0.3.4/css/arXiv.css?v=20260318).

The abstract page explicitly retains its classic Lucida Grande/Helvetica/Arial
body and bold title. Its abstract has no colored block or left-border quotation
decoration. The title, author line, prose, source details, and supporting actions
have distinct roles.
[Abstract CSS](https://arxiv.org/static/base/1.0.1/css/abs.css).

Search uses Open Sans with Lucida Grande/Helvetica Neue/Helvetica/Arial
fallbacks, a 1.5 body line height, and blue links. Its typographic hierarchy and
plain results list matter more than reproducing every form widget.
[Search base CSS](https://static.arxiv.org/static/base/1.0.0a5/css/arxivstyle.css).

Therefore there is no single exact arXiv font/palette across these live surfaces.
The familiar red belongs to the requested historical visual lineage; describing
it as a measured match to the current header would be inaccurate.

## Proposed Eigenquestions treatment

The coordinator selected familiar classic arXiv color qualia with Eigenquestions'
own wordmark: a quiet burgundy anchor, white reading surface, blue destinations,
gray metadata, and precise thin rules. This follows the user's old-viewer context
and creative-layout request; it is not an exact copy of the current arXiv header.
Use the Lucida Grande/Helvetica/Arial family throughout, including source prose.
Georgia belonged to old Eigenquestions, not the inspected arXiv abstract body.
Do not add arXiv or Cornell logos, affiliated language, decorative illustrations,
or imitation institutional navigation.

| Role | Proposed value or behavior |
| --- | --- |
| Main surface | White; avoid an all-over beige or gray app background |
| Primary text | `#222222` or `#1c1a17`, used consistently |
| Secondary text | `#626262` or `#6b6459`; readable, not faint |
| Brand/current selection | `#b31b1b`, with a very pale red selected-row fill |
| Source/destination links | `#1565c0`, underlined on hover/focus |
| Decorative rules | `#dddddd`; stronger borders for inputs/buttons |
| UI and direction labels | Lucida Grande, Helvetica Neue, Helvetica, Arial, sans-serif |
| Reading size | 16px body and controls; 16–17px direction label, 1.4–1.5 line height |
| Metadata | 13–14px; never encode a necessary action solely in this size |
| Current question heading | 26–30px desktop, 22–26px mobile; not a marketing hero |
| Prose | 16–17px, 1.55–1.65 line height, maximum about 75 characters |
| Control geometry | At least 44px tall; obvious border/fill; 2–4px corner radius |
| Column rows | 52–80px typical, content-driven height; full row clickable |
| Column width | Approximately 330–380px desktop; 86–92vw mobile |

The numbers in this table are design recommendations, not claims that arXiv
implements these exact accessible control sizes everywhere.

The first desktop viewport should answer four questions in order: what is this
site, what am I asking, where am I on my path, and what can I choose next?
Keep the Eigenquestions heading modest and the search/refinement input prominent.
Put “New path” beside the current-path heading or at the end of that same toolbar,
with a plainly visible 44px target. “Back” must also look like a control. Tiny text
links to these central actions would miss the request even if keyboard-accessible.

Give the path its own narrow horizontal band, with short, legible labels and
separators. Allow a long path to scroll within that band; never stretch the page.
Keep the current segment stronger and use real buttons or links for history.
Do not repeat the full question in every breadcrumb and every column heading.
A short label can have the full question in its accessible name or revealed
detail. On narrow screens keep the current location and New path accessible
without requiring a sideways hunt.

The column strip is the main exploration workspace. Historical column headings
can show a step number and short contextual label; the latest column should
clearly say that these are the next directions. Each row needs a number, a
scientific label, and a directional affordance. One concise supporting line is
enough. Keep full source descriptions in the evidence area below, not in every
navigation row. Avoid five visually unrelated cards, full-width pastel blocks,
rainbow direction identities, or a large empty frame around five tiny items.

The map is a secondary view of the same computed directions. Its toggle should
be visible, but the default screen should remain the text viewer. Switching
views must preserve the path and question. Evidence should read like a paper
list: title or extracted question first, source link next, then smaller scope
metadata. Keep provenance readable while moving engine internals, revision
hashes, connection diagnostics, import/export, and detailed projection caveats
into deliberate secondary disclosures. Essential corpus scope belongs in a
short visible sentence; extensive implementation exposition does not belong
between the user and the next choice.

Search must distinguish starting a new path from refining the current physical
context. Clear verbs and short helper text are preferable to two equally large
forms. Submitting a new question should preserve focus and report progress near
the input; result arrival should make the changed current column obvious without
unexpectedly scrolling the whole document. Keyboard focus needs a visible outline
on all rows, path segments, mode controls, and disclosures.

On mobile, maintain the column idea with a deliberate horizontally scrollable
strip and a small glimpse of the adjacent column. Avoid horizontal page overflow
and a forced desktop overview shrunk to fit. Labels should wrap naturally rather
than disappear behind ellipses. The latest column should be brought into view;
the breadcrumb provides a second, easy route back. Keep any source panel below
the active choices, not permanently beside them on a phone.

## Independent visual acceptance

The forthcoming review should use actual desktop and mobile screenshots of a
fresh start, a multi-step KK/dark-matter path, a long scientific label, search,
source evidence, and map mode. A passing overflow test alone does not establish
good design. Review the following visible outcomes:

1. The text-column viewer is unmistakably the default primary interaction.
2. Five choices are readable at normal scale and share a compact list rhythm.
3. New path, Back, question entry, and mode changes are obvious and at least 44px.
4. The path is elegant and comprehensible after several steps; it does not become
   a stack of repeated full questions.
5. The same palette, type, spacing, rule treatment, and control language govern
   every part of the page, including expanded panels and error states.
6. Evidence has bibliographic hierarchy and does not bury the source link.
7. Mobile keeps 16px input text, readable labels, and deliberate column scrolling.
8. The screen communicates dynamic context, not a frozen ontology.

The bounded capture helper is
[`tests/design/reference_capture.py`](../tests/design/reference_capture.py).
It refuses browser launch outside Slurm, records public page status and computed
styles, and captures 1440×1000 and 390×844 viewports. Historical viewers are
optional loopback URLs staged by the coordinator. HTTP/CSS inspection is complete;
rendered-reference inspection is complete; product aesthetic acceptance remains
pending.

## Captured reference inspection and pre-screenshot product review

The coordinator's Slurm job `58203240` produced eight successful reference visits
(three arXiv pages and the archived tree, each at desktop/mobile size), all HTTP
200, with no recorded page errors. The [capture report](evidence/q002/references/reference-capture.json)
preserves computed styles and dimensions. The v4 prototype was inspected as
source; it was not included in this rendered capture.

Independently inspected images include the old desktop/mobile path, arXiv
desktop list, desktop/mobile abstract, and desktop/mobile search. The
[old desktop path](evidence/q002/references/old-tree-desktop-path.png) puts the
column strip at approximately y=124 and the detail area after y=464. The
[old mobile path](evidence/q002/references/old-tree-mobile-path.png) exposes the
active column immediately under the path. It also demonstrates defects to avoid:
tiny controls, clipped path text, and an unnecessarily empty lower column region.
The continuity and readable active selection are useful; its exact density is
not a standard to copy.

The arXiv captures confirm the CSS reading: the newer dark header coexists with
a compact classic sans-serif body. Its
[abstract](evidence/q002/references/arxiv-abstract-desktop.png) and
[list](evidence/q002/references/arxiv-list-desktop.png) use confident title weight,
plain blue links, sparse decoration, and clear supporting metadata. The
[mobile abstract](evidence/q002/references/arxiv-abstract-mobile.png) shows that
large obvious actions can coexist with a sober scholarly document. The
[search page on mobile](evidence/q002/references/arxiv-search-mobile.png) has a
long control preamble; this is not a reason to bury Eigenquestions' primary
navigator below its first viewport.

Read-only inspection of `web/index.html`, `web/styles.css`, and the rendering
functions in `web/app.js` found the chosen palette, uniform sans family, ruled
rows, cached historical columns, and text-first reading order consistent with
the requested direction. Three points should guide the first product screenshot
review. These are source-based risks, not claims of observed rendering failures:

1. **Phone header fit.** The masthead and action group have no wrap rule while
   containing an unbreakable wordmark, Connect your agent, and New path. Confirm
   their combined intrinsic widths fit 390px and 360px. If needed, use a deliberate
   second action row; do not solve this by making labels microscopic.
2. **Directions in the initial viewport.** Masthead, search heading, input,
   four selectors, status, path, and current-question heading all precede the
   strip. Confirm a phone shows useful choices without a long control-only
   preamble. A collapsed optional-search-controls disclosure could recover
   space if necessary while preserving readable controls and their values.
3. **Explicit source inspection.** A row's source button currently filters the
   reading area without bringing it into view or focusing/announcing that
   destination. Because it sits below the column strip, a click could appear
   ineffective. The `↗` mark also usually suggests external navigation. Prefer
   a clear Sources label at a readable size and reveal/focus the relevant
   reading heading after this explicit action. Keep ordinary direction selection
   spatially stable.

Root and the site owner received these findings before the product screenshots.
No web code, integration test, or runtime behavior was changed by the reviewer.
