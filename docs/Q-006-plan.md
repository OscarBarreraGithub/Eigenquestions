# Q-006 — A fixed overview for a collaborator demo

Request summary: add one overarching navigable cluster map, in the style of the
owner's IAIFI paperscape. Zoom to see clusters and papers clearly. Keep it in its
own tab, fixed rather than query-updated, and keep the existing explorer intact.
This is a minimal demonstrable overview, not a new dynamic navigation algorithm.

Owner clarification (summary): IAIFI supplies the UI style only. The map's cuts,
connections, layout and especially its topics must be specific to the Swampland
collection. Reuse no IAIFI data, coordinates, memberships or topic taxonomy.

## Requirements and decisions

1. Use a separate static document, `/overview.html`, opened by an ordinary clearly
   labeled new-tab link. Preserve the live explorer and its authored-history
   cache. The overview must not read or write explorer session/local storage,
   attach a companion, or invoke its query/embedding engine.
2. Match the actual [IAIFI reference](Q-006-paperscape-reference.md): a quiet dark
   dot map, pointer-centered zoom, pan, Fit, progressive collision-aware labels,
   local find/highlight and readable details. Keep labels at least 13 CSS pixels,
   controls at least 44px, selected context obvious and motion restrained.
3. Use one existing reviewed question layout from the pinned publication map:
   8,473 question facets covering 6,477 papers, with its actual hierarchy and
   coordinates. Preserve overlapping memberships and the unresolved group.
   Dots are question excerpts, not necessarily one dot per paper. Do not invent
   deeper clusters when the stored hierarchy ends.
4. The five broad groups provide the opening view. Show supported finer groups
   as zoom reveals them and allow inspection of individual source excerpts and
   linked papers. Keep source titles, paper counts and excerpt counts distinct.
   Cluster captions may be made concise or corrected by Astra for faithful
   presentation, with original labels and a short rationale preserved.
5. Ship a deterministic compact export with pinned input hash, source IDs,
   hierarchy, exact memberships, coordinates and graph-link provenance. Aim for
   under 3 MB initial JSON; fetch excerpt details in bounded static shards.
   Avoid bundling the 145 MB source release or the numerical query corpus.
6. Explain the fixed layout briefly in About: text-affinity geometry, provisional
   agent-proposed topic labels, limited hierarchy, and the chosen single connected component. Actual coarse affinity links are not citations or
   physical implications. This context should not compete with the map.
7. Keep camera interaction smooth and deterministic on desktop and phone. Resize,
   wheel/pinch, dragging, Fit, cluster selection, point details and search must
   remain legible. A sidebar/list should provide a reliable text route to the
   same groups when labels cannot all fit on the canvas.
8. Verify data coverage/provenance and browser behavior, inspect real screenshots
   at wide and narrow widths, and check that returning to the original tab leaves
   its accepted view/history untouched. No local Mac browser; use Slurm Chromium.
9. Preserve the notebook, ordinary Git checkpoints and actual public verification.
   Keep Q-005's release independently recorded before publishing this addition.

## Ownership and shared boundary

- Astra `/root/stored_view_backend`: reproducible data export, caption/provenance
  review, fixed JSON/detail shards and meaningful data checks.
- Astra `/root/navigator_protocol`: standalone Canvas renderer, camera/hit testing,
  local search/details interactions, shared data contract and browser acceptance.
- Sol `/root/quiet_ui_review_sol`: standalone HTML/CSS, IAIFI visual reference,
  accessible controls and independent screenshot review. Add the one explorer
  link only after the root confirms the Q-005 publication identity is captured.
- `/root`: integrated mathematical/product review, notebook, request plan, Git,
  cluster browser jobs and release. Coordinate schemas before parallel edits.

No application code is shared with the contextual controller. The fixed map is
an independent useful picture of the same research collection; its shallow
stored hierarchy and provisional labels must remain honest.
