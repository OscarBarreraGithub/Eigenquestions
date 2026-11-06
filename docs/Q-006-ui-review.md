# Q-006 — Standalone Swampland overview

UI owner/reviewer: `/root/quiet_ui_review_sol` (Sol). Astra owns the fixed
Swampland export and the standalone Canvas renderer. Root owns integration,
Slurm browser evidence and release.

The [verified IAIFI source](Q-006-paperscape-reference.md) supplies an interaction
and visual reference only. All coordinates, topics, links, memberships and source
details come from the pinned Swampland question view. The product title is
**Swampland overview**, with **8,473 question excerpts · 6,477 papers** stated
explicitly. The page explains that a paper can contribute more than one dot.

## First implementation

`web/overview.html` and `web/overview.css` are independent of the contextual
controller and its styles. The page has a compact white title/search/control
area, a dominant dark dot map, five broad-group buttons and a source-details
region. The map has no decorative glow, glass, shadows or continuous layout
animation. Actual group names and child relationships come from the dataset.
About explains the fixed text-affinity projection, provisional labels,
overlapping membership and the genuinely shallow stored hierarchy.

Desktop uses a map with a 300–340px adjacent text column; phone widths place the
map first and the same text route below it. The existing source title and exact
question excerpt are readable in the details region, with the paper link kept
separate from map navigation. Explicit zoom/Fit controls and topic/result buttons
have 44px minimum targets. Canvas label sizing, measured collision rejection,
camera interactions, selection and static shard loading belong to the renderer.
The agreed minimum for canvas labels is 13 CSS pixels.

The DOM contract includes `overview-stage`/`overview-canvas`, zoom/Fit buttons,
`overview-search`/`overview-find`, the topic and result lists, one live status,
and `overview-details` with a preserved `overview-selected-heading`. A keyboard
hint documents arrow-key pan, +/− zoom and Home to fit. Search changes only
highlight/selection/camera; it is not a physics query or a new grouping. Find
looks up paper titles, arXiv IDs and topic labels, not unloaded full excerpts.

The original explorer receives one small two-item navigation row immediately
below its masthead. Text explorer is the current noninteractive label;
**Global overview ↗** is an ordinary new-tab link with `noopener noreferrer` and
an accessible new-tab description. Its scoped CSS fits 320px without modifying
the existing search, path or runtime. The sitemap adds canonical `/overview`.

## Evidence and remaining gate

Read [the Q-006 plan](Q-006-plan.md), the shared contract and data audit before
editing. Coordinated all DOM IDs with the renderer owner. Parser checks confirm
balanced HTML and unique IDs in both documents, including every agreed map ID.
No Mac browser was used. Integrated build, actual Slurm desktop/phone screenshots,
label legibility, source selection and explorer-state isolation remain pending.
No visual acceptance is claimed from this source review.

## First actual fit view

Source `50e5804`, Slurm job `58373333`, Chromium 145.0.7632.6;
[job receipt](evidence/q006/browser-v1-job.json). Inspected the actual
[1440px fit view](evidence/q006/browser-v1/q006_overview_acceptance/overview-fit-1440.png).
The opening presentation is acceptable: five readable, nonoverlapping Swampland
captions; distinct excerpt/paper counts; a dominant quiet dark dot map; matching
group colors in the text list; and discoverable Find/zoom/Fit controls. There is
no borrowed IAIFI subject matter or decorative visual treatment.

No UI correction requested from this image. The focused browser run stopped at
a pointer-centered wheel-coordinate assertion after its initial load check;
the separate Q-005 suite passed ten checks. Fine-group/source and phone captures
are not yet available. This approves the desktop fit composition only, not the
whole map's interactions or final visual acceptance.

## Final actual visual acceptance

**Accepted as the minimal collaborator demo:** source `50e5804`, Slurm job
`58374108`, Chromium 145.0.7632.6. The wheel test was corrected to observe the
actual dispatched pointer coordinate; no runtime change was needed.

Inspected actual [390px](evidence/q006/browser-v2/q006_overview_acceptance/overview-390-map.png)
and [320px](evidence/q006/browser-v2/q006_overview_acceptance/overview-320-map.png)
map views, the [finer-group view](evidence/q006/browser-v2/q006_overview_acceptance/overview-finer-group-1440.png)
and [source selection](evidence/q006/browser-v2/q006_overview_acceptance/overview-source-1440.png).
Both phone widths retain readable, nonoverlapping captions and visible zoom/Fit
controls. The 320px view uses a leader line to place the crowded neutrino caption
clearly. Selecting a genuine finer group highlights its members and gives its
name priority. Deeper source labels remain legible; the selected paper title,
exact question description and original-paper link are readable in the text
panel. No material visual blocker or additional refinement requested.

The [focused browser report](evidence/q006/browser-v2/q006_overview_acceptance/q006-overview-acceptance.json)
passes all twelve checks. This signoff is for the fixed Swampland overview and
its separate entry; it does not upgrade provisional topic labels to verified
physics or change the contextual explorer's scientific behavior.
