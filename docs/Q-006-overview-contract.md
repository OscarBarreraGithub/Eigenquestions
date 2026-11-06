# Q-006: fixed global overview contract

Status: architectural proposal, 2026-11-06. No overview runtime or dataset has been added by this audit. The question-conditioned explorer and its frozen numerical identity remain unchanged. The coordinator's Q-006 plan determines implementation scope; this document records the integration boundary and acceptance requirements.

## Separate page and independent state

Use a standalone `web/overview.html`, dedicated `overview.js` and `overview.css`, and a compact, versioned static dataset. A visible **Global overview** link should open the page in another browser tab, with that behavior stated accessibly. Keeping the existing explorer document alive preserves its exact, in-memory authored-history snapshots; returning from a full-page navigation cannot promise the same result.

The overview does not import `app.js`, `compute-worker.js`, the geometry engine or session controller. It does not read or write explorer storage, connect a companion, apply a navigation action, or consume `#view`, `#focus` or launch-token fragments. Its only mutable state is presentation: camera, selected topic/source and optional local text lookup. A lookup may highlight or center a known item; it must not regroup, relabel or rearrange the fixed map. An initial demo does not need camera persistence or a second machine-action API.

The existing explorer's query-dependent geometry remains a separate feature. A map point is a source-scoped question description, not necessarily a distinct paper. Any later explicit handoff into the explorer must identify that transition and retain its source/context; it is outside this minimal overview.

## Existing data and scientific meaning

The data auditor found the already pinned source artifact at `physics-atlas-swampland/graph-design/20261105-v1/publication-v1/map-data.json`, SHA-256 `a6cb5cdb6d955d3ca33b9297be0a301ea50c6c8c75ba2294999adac8163d765b`. Its `minilm-leiden:physical_question:reviewed` view is a bounded first demo: 8,473 question facets covering 6,477 papers, 12 topic records including the root, and 42 displayed topic links. IDs, text hashes and lenses match the frozen explorer corpus according to the independent data audit.

The supplied coordinates are the first two stored diffusion modes at time four, standardized within the connected component. All 8,473 question facets occupy one component. Coordinates are reused across candidate cluster algorithms; they are display coordinates, not physical distances, and are not comparable between different encoders or lenses. Preserve the actual supplied coordinates; pan and zoom change only their screen transform.

The hierarchy is shallow, depth zero through two, and must remain shallow in the demo. It includes an unresolved-membership bucket, overlapping direct homes and a source assigned directly to an internal topic. Ten facets have two direct homes. Topic names and sampled reviews are organization aids; neither the labels nor every member were comprehensively scientifically reviewed. Do not turn them into an exclusive or fully validated taxonomy.

The 42 links are coarse text affinities, computed as `C = Hᵀ W H` from the fixed source-affinity graph and reviewed direct memberships. The supplied display includes the union of each topic's six strongest positive incident off-diagonal affinities. These are not citations, physical implications or source-to-source edges. Preserve their kind and weight; expose that meaning in the map legend/details.

Each facet has paper-balanced mass `mᵢ = 1 / nₚ`, divided equally among its distinct direct homes. The stored `topic_membership_weights` therefore sum to the facet's mass, not necessarily to one. Preserve all homes and exact weights. A primary paint color, if used, must be a documented drawing choice rather than a change to membership.

## Static payload

Do not ship the complete 144,689,193-byte upstream publication file. It contains multiple layouts, extensive extracted text, experiments and provenance beyond the needs of one overview, and exceeds the site's 25 MiB per-file build bound.

The data owner should export one reproducible projection with these logical fields; columnar/indexed encoding is acceptable:

| Record | Required meaning |
| --- | --- |
| Manifest | Format version, fixed view ID, upstream SHA-256, corpus ID, dated scope, node/topic/link counts, layout description, membership/link rules, derived-file hashes |
| Topic | Stable ID, existing label, parent/children, supplied x/y, counts/mass, review status and limitations |
| Facet | Stable unit ID, paper ID, supplied x/y/component, mass, every direct topic home and weight |
| Topic link | Stable endpoint references, supplied affinity weight and `text_similarity` kind |
| Source details | Genuine paper title, source URL and exact question text for an inspected facet, with a deterministic mapping back to the unit ID |

The data auditor measured a complete compact projection in memory: indexed geometry/memberships, genuine paper titles/URLs, topic descriptions/provenance, links and layout metadata total **1,865,240 bytes raw / 731,009 bytes gzip**. Including all source question texts would increase the raw payload to 3,676,860 bytes. Prefer 17 aligned text shards of at most 512 records instead: the measured largest shard is 115,426 bytes. This gives a complete initial map/catalog below 2 MB raw and an inspected source at no more than about 116 KB extra. The earlier 1.16 MB estimate omitted the paper catalog. The existing `papers.json` alone is 2,772,900 bytes and need not be loaded.

Keep derived-file hashes and source-ID/text-hash verification in the export audit; a second text hash per point is not necessary if exact alignment and every detail shard are pinned and checked. Equal direct-home weights may be reconstructed from the preserved facet mass and complete home list only after the exporter verifies that this exactly represents the upstream weights. Report final produced bytes separately from these in-memory measurements. A 2 MiB initial raw budget is a feasible target, not a browser limit or measured performance claim.

Source descriptions may load on selection, but the map must show a clear pending/error state and retain the selection. No embeddings, 384-dimensional vectors, source-affinity matrix or dynamic clustering code are needed in the browser. Do not create text or URLs absent from the source artifact. Render strings as text and permit only safe HTTP(S) source links.

## Rendering and interaction

Canvas 2D is a suitable first implementation for approximately 8,500 fixed marks; avoid one interactive DOM element per facet. Keep semantic topic buttons, search results and selected-source details in the DOM for keyboard and assistive access. A small SVG or HTML overlay can hold the visible labels.

At the initial scale, show the few meaningful coarse topic labels. As the camera approaches a region, reveal only genuine existing child-topic labels and a bounded number of source labels. Zoom is not evidence of additional hierarchy: never invent intermediate levels. Use measured label bounds, deterministic priority, collision rejection and a hard visible-label cap; selected/hovered labels take priority. Full labels and source descriptions remain available in the details panel even when no map label fits. Avoid drawing thousands of complete extracts or resizing scientific coordinates to make labels fit.

Schedule at most one redraw per animation frame, cull off-screen marks, cap the canvas backing-store device-pixel ratio and reuse a spatial hit-test index. Continuous force simulation, WebGL and a new worker are not requirements for this fixed first demo. Measure the actual renderer before adding machinery.

Provide drag pan, pointer-centered zoom, visible zoom-in/zoom-out/reset controls and keyboard equivalents. Main touch controls should be at least 44 CSS pixels. A topic selection should highlight its actual members and show its genuine neighbors/description; it should not move the underlying points. Use safe camera bounds and a visible reset to recover from excessive zoom. Prevent page overflow at 320 and 390 CSS pixels without shrinking controls or labels into illegibility.

## Build, routes and privacy

`scripts/build-site.mjs` already recursively copies `web/`; dedicated overview assets there require no framework or backend. Put generated data in a separate `data/overview/` source directory with an explicit build copy into `dist/data/overview/`, or place the finalized small artifact under `web/` with a clear generated-file provenance. Do not modify `data/navigation/manifest.json`, its 41 pinned files, or the engine identity for this feature.

The physical entry asset `overview.html` satisfies the existing exact-file root-link check and the local static server. With the existing Cloudflare `html_handling = "auto-trailing-slash"`, production redirects `/overview.html` to `/overview`, which serves that file. Test the explicit asset and canonical public URL; do not disable global HTML handling to avoid this redirect. [Cloudflare HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/).

Leave `run_worker_first` restricted to `/api/views` and `/api/views/*`. Other matching static assets follow asset-first routing, so the overview needs no Worker computation or storage binding. [Cloudflare selective Worker routing](https://developers.cloudflare.com/workers/static-assets/routing/worker-script/).

Keep the 32 retired GET/POST route checks, including `/explore/` and `/explore/tree/`. Do not reuse those names or enable an SPA fallback. Add the new HTML, code, styles and bounded dataset to build/publication identity checks. If this contract is linked publicly, add it explicitly to the build's documentation allowlist. Add only the genuine overview entry to the sitemap.

The overview makes ordinary same-origin static GET requests. Pan, zoom, selection and local lookup stay in the browser; no search text or camera state is sent to a server. No analytics, CDN script, external font, LLM or dynamic API is required. An external paper opens only after the user's link action. This does not claim that ordinary hosting access logs disappear.

## Observable acceptance

1. Direct overview load fetches only its own static assets; it never fetches `app.js`, `compute-worker.js`, geometry/vector shards, companion endpoints or `/api/views`.
2. A fixed dataset hash, source IDs, memberships, coordinates and topic names remain unchanged after pan, zoom, selection, reload and independent explorer searches. Verify overlapping homes and the unresolved bucket explicitly.
3. Every displayed topic and inspected source resolves to the frozen artifact. Source title, exact text and safe URL are reachable; link legend and limitations match the actual affinity/layout semantics.
4. Opening and operating the overview preserves explorer local/session storage and the original live page's exact capsule, draft and authored-history behavior. The overview link does not silently navigate that page away.
5. Real pointer, wheel/touch and keyboard actions pan/zoom/select/reset. Measure feedback latency, frame intervals and long tasks separately from initial download/parse; record browser/environment limits instead of claiming guaranteed 60 fps.
6. Desktop, 390-pixel and 320-pixel screenshots show readable labels, visible controls and no page overflow. Selected-label placement and nearby label collisions get actual-browser bounds checks and visual review.
7. Static/public asset hashes match the frozen source. Retired routes retain their expected statuses, native explorer regression suites pass, and no numerical/corpus identity changes appear in the diff.

Suggested ownership: data auditor exports and verifies the fixed projection; Sol owns the overview visual design and renderer plus the minimal entry link; protocol/integration owns isolation, input and browser acceptance checks; root owns the atomic plan, notebook, freeze, Slurm execution and release. These are recommendations pending the coordinator's assignment, not parallel authorization to edit runtime files now.
