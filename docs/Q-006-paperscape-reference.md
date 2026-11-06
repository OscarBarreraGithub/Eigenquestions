# Q-006 — The actual IAIFI Paperscape reference

Read-only reference audit by `/root/quiet_ui_review_sol` (Sol), 2026-11-06.
No Eigenquestions frontend files changed. Browser execution remains reserved for
Slurm; the saved local IAIFI screenshots were inspected with `view_image`.

## Source identity

The user's actual public project is
[OscarBarreraGithub/IAIFI-Paperscape](https://github.com/OscarBarreraGithub/IAIFI-Paperscape),
whose GitHub `main` resolved through the connector to
[`e3d55af51b4e3f996a22bb7364d342391b97bb0c`](https://github.com/OscarBarreraGithub/IAIFI-Paperscape/commit/e3d55af51b4e3f996a22bb7364d342391b97bb0c).
The executable files are at the repository root, not under `web/`.

A local copy exists at `/Users/emmy/Documents/PocketPostdoc/Code/IAIFI`. It is
inside the parent PocketPostdoc checkout, not an independent Git repository.
The parent origin is `OscarBarreraGithub/PocketPostdoc`, branch `main`, HEAD
`6c79f478d85de3794d0693055e8568e9ae080575`. Scoped Git status contains only
untracked screenshots, `.venv` and notebooks; no tracked IAIFI source changes.
More decisively, local file Git-blob hashes exactly match the published IAIFI
commit:

| Local file | Published path | Matching blob SHA |
|---|---|---|
| `web/scatter.js` | `scatter.js` | `c4524a947f1d2b931ed53d8ff696607549703d3b` |
| `web/index.html` | `index.html` | `b582d71126ce83999f1596a936319518dc58027d` |
| `web/style.css` | `style.css` | `656d65be65161cc529f55dd9a8f4ba92adc98e7e` |
| `web/data/papers.json` | `data/papers.json` | `4af08f7ef1bf4cea54ce855668ca60fda53e3596` |
| `web/data/abstracts.json` | `data/abstracts.json` | `f763c0750ed6789be83f6b16c008db9d4175338b` |

Use this pinned executable source as the reference. The local README's
regl-scatterplot description is stale: the published
[renderer](https://github.com/OscarBarreraGithub/IAIFI-Paperscape/blob/e3d55af51b4e3f996a22bb7364d342391b97bb0c/scatter.js#L1)
is plain **Canvas 2D with zero external dependencies**.

## What the actual map does

The frozen payload contains 9,322 papers (553 IAIFI and 8,769 background),
218 clusters, and fixed paper coordinates. Paper records carry `id,x,y,t,a,yr`,
categories, cluster ID and nearest-neighbor IDs; cluster records carry
`id,label,cx,cy,size`. The main JSON is 4.3 MB, with 12.1 MB of abstracts split
out and fetched shortly after initial rendering. No layout or clustering runs
in the browser. Local pipeline code uses SPECTER2, PCA-50 and standard UMAP
(`n_neighbors=40`, `min_dist=.08`, cosine, seed 42), with HDBSCAN leaf clusters.
The HTML's DensMAP wording is not supported by that pipeline call.

The visual character is a dark, almost full-window constellation of colored
paper dots over a faint background population. There is no always-visible edge
hairball. Draws are batched by color, offscreen points are culled, and a 128×128
spatial grid supports point picking. A selected dot receives a clear ring;
title/authors/abstract/arXiv link and neighbors live in a separate paper panel.
These patterns come from the published
[draw and picking code](https://github.com/OscarBarreraGithub/IAIFI-Paperscape/blob/e3d55af51b4e3f996a22bb7364d342391b97bb0c/scatter.js#L376).

Wheel zoom preserves the data location under the pointer; drag pans. Touch
supports drag and pinch. A logarithmic zoom slider and Fit control provide an
explicit escape back to the map. Search finds paper titles/authors and pans to
the selected existing point without changing its coordinates. The detail panel
provides exact source text instead of putting paragraphs on the canvas.
[Interaction source](https://github.com/OscarBarreraGithub/IAIFI-Paperscape/blob/e3d55af51b4e3f996a22bb7364d342391b97bb0c/scatter.js#L808).

Cluster labels are drawn at exported centroids, sorted by cluster size. Only
36 clusters meet the frontend's size≥40 cutoff. Label budgets progressively
increase through 3, 5, 8, 15, 25 and all eligible labels, with measured bounding
boxes and 6–12px collision margins. This is the important zoom behavior to
match: more detail appears within one stable map, rather than recomputing a
query-conditioned slice.
[Label source](https://github.com/OscarBarreraGithub/IAIFI-Paperscape/blob/e3d55af51b4e3f996a22bb7364d342391b97bb0c/scatter.js#L698).

## Minimal Eigenquestions demonstration

Use a separate `/overview.html` with its own stylesheet, renderer and frozen
overview data. An ordinary **Overview map ↗** link can open it in a new browser
tab; collaborators can use that direct URL. This is cleaner isolation than
adding a new mode to the contextual controller. Opening, searching, zooming or
selecting a paper on this page must not readjust the contextual view, write its
session keys or change its corpus/computation identity.

Match the IAIFI map's spatial interaction and restrained dot/label presentation:
one broad map, a few readable cluster labels at fit, more labels on zoom, pan,
zoom-in/out, Fit, a small paper search and a source detail panel. Keep dataset
date and the projection's approximate nature visible. The current explorer's
quiet page shell can remain white while the separate map uses the IAIFI dark
canvas. Theme/category/year/citation controls are unnecessary for this first
demonstration unless the actual overview data requires them.

Do **not** copy two weaknesses of the reference. Its label font shrinks from
18px to 9px as zoom grows, and cluster labels disappear beyond zoom factor 25.
For the requested legibility, hold visible labels near 13–14 CSS pixels, measure
collisions in screen coordinates, and keep the selected paper title readable at
deep zoom. Also retain 44px explicit controls and a keyboard-operable result/list
route; tiny canvas dots alone are insufficient navigation targets.

The data owner should freeze positions, groups and reviewed source-grounded
labels offline, with enough provenance to reproduce them. Use Eigenquestions'
actual data and embedding identity; IAIFI's SPECTER2 geometry is a reference
pattern, not interchangeable scientific data. Search may highlight or pan within
the fixed map. It must not move points, relabel clusters or introduce the
contextual question engine. Planned hexbin code in the IAIFI source is not used
by the published renderer and is not needed for a minimal implementation.

The first visual gate should inspect fit, cluster zoom and paper selection at
desktop and phone widths, verify readable nonoverlapping labels, and confirm
that the contextual explorer's saved state is identical before and after opening
the map. No new renderer has been implemented or visually accepted by this audit.
