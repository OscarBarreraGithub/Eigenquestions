# Q-002 — Text-first arXiv-style v2

Authority: [original request](requests/Q-002-original.md). Baseline is the verified
v1 at `4e14ab82e113df1c8052c1f9ef039c032ff409db`. Work on
`agent/arxiv-text-explorer-v2`, publish through the existing main workflow after
visual and interaction acceptance. The single project notebook remains the
research record. Astra implements; root coordinates, reviews and releases.

## Atomic requirements

| ID | Requirement | Observable acceptance | Owner / status |
|---|---|---|---|
| V2-01 | Restore the old text viewer as the primary navigation experience. | Historical Miller-column viewer is inspected; current dynamic directions appear as readable text rows before any chart. | Site / implementing |
| V2-02 | Keep the new computation and make labels update with search. | A new question changes actual direction IDs/text and evidence through the shared frozen engine; no static topic tree is introduced. | Site + protocol / pending |
| V2-03 | Use arXiv's palette and typography across the entire site. | Reference evidence and chosen classic burgundy/white/blue-link, sans-serif scholarly style are consistent through controls, rows, path, sources and dialogs. Own Eigenquestions branding retained. | Design + site / reference review |
| V2-04 | Make the visual result clean, sharp and deliberate. | Desktop, narrow desktop and mobile screenshots receive independent visual review; no marketing hero, tiny labels, overlaps, clipped controls or uncontrolled whitespace. | Design + root / pending |
| V2-05 | Make presentational interactions immediate. | Tabs, disclosures, typing and path scrolling work during delayed computation; no full-page blocking overlay or unnecessary recomputation for view toggles. Measure input feedback/long tasks without claiming universal frame rates. | Site + protocol / pending |
| V2-06 | Handle computational waiting clearly. | Existing usable content remains while computation has a visible status; stale responses, duplicate SSE and transport changes cannot overwrite the active intent. | Site + protocol / pending |
| V2-07 | Preserve drafts while results arrive. | Typing a new question is not replaced by delayed worker or agent responses; submitting applies the intended draft and settings. | Site + protocol / pending |
| V2-08 | Make the current exploration path easy to understand and navigate. | Selected/current steps are clear; Back, replay and branch selection use canonical state; history labels do not fabricate uncomputed branches. | Site + protocol / pending |
| V2-09 | Make starting a new path obvious and easy. | Prominent New path works during computation, clears old scientific focus/history through reset, focuses an empty question input, and preserves the active transport. | Site + protocol / pending |
| V2-10 | Make buttons, toggles and options large and discoverable. | Primary interactive targets are at least 44 CSS px; visible focus, selected and disabled states; comfortable readable labels and keyboard operation. | Site + protocol / pending |
| V2-11 | Make the layout responsive. | Screens at 1440, 1024 and 390 px (plus narrow overflow check) retain readable current choices/path and accessible controls without page-level horizontal overflow. | Site + protocol / pending |
| V2-12 | Preserve source access and optional geometry. | Source rows/provenance remain accessible; geometry is a secondary view using the same computed result, with its limitations intact. | Site / pending |
| V2-13 | Preserve standalone and agent-driven navigation. | Both a public worker session and actual MCP/companion updates exercise v2 rows/path; revision acknowledgements and established permission fallback remain valid. | Protocol / pending |
| V2-14 | Preserve import/export and v1 computational identity. | Existing sessions replay; corpus/engine/schema are unchanged unless an independently justified correction is coordinated. | Protocol / pending |
| V2-15 | Call this v2 and deploy it to the existing domain. | Product shows v2, current domain serves the checked renderer, previous retired routes stay retired; no new hosting project or identity. | Site + root / pending |
| V2-16 | Keep a concise record and verified Git checkpoints. | Q-002 summary, meaningful decisions/failures, evidence and final state are in the one notebook; intended changes committed/pushed with Request/Agent credit and remote/deployment verification. | Root / active |

## Design and integration decisions

The old viewer already uses the familiar classic arXiv-like burgundy, white,
blue links and Helvetica family. Current arXiv styles are evolving; v2 deliberately
uses that classic visual language rather than claiming byte-for-byte identity
with the current arXiv website. The user explicitly allows layout changes and
creative liberties. Do not copy Cornell/arXiv identity marks or imply affiliation.

The primary view is a dynamic Miller strip and a legible current path. Historical
columns may cache only views actually received for that state/computation. After
reload, an uncached past step is a query with Restore, not an invented list of
children. The current column normally offers about five genuine next directions.
The chart is secondary. Presentation and history controls should not wait for
unrelated computation; deferred work must have explicit latest-intent semantics.

File ownership: site owner has `web/`, site build/check scripts, `tests/site/`,
README and site docs. Protocol owner has integration/browser tests and the v2
acceptance document. Design reviewer has reference/critique docs and bounded
reference-capture script. Root owns request/plan/notebook, Git and release.
No numerical engine, corpus or session-schema change is planned.

## Release gates

1. Inspect old viewer and primary arXiv references; record the visual choice.
2. Implement dynamic text UI and robust async interactions; audit all clauses above.
3. Run real browser journeys, delayed-computation/race checks, keyboard/mobile
   tests and visual review; revise only for observed shortcomings.
4. Commit the verified version, deploy via existing GitHub workflow, verify exact
   public assets and interaction behavior, and close the notebook/audit.

## 2026-11-06 integration amendment

The UI's latest-submission behavior requires rebasing from the last visibly
accepted session when an earlier unseen action has advanced the bridge. Root
identified a race with external MCP updates. A bounded optional `If-Match`
revision guard for browser import/action is authorized; stale mutations return
409 with the current snapshot, which the UI must preserve along with its draft.
The check occurs after parsing the request body and immediately before mutation.
This is a transport correction, not a change to the engine, corpus or scientific
session schema. Protocol owns the guard and its real-MCP interleaving test; site
owns the conflict presentation.
