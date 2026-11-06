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
