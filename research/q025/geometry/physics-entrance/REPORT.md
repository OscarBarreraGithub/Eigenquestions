# Broad physics classification entrance

The selected artifact is `layout-v2/orientation.json`, paired with `results/destinations.json`. It provides 17 active disciplines and 194 directly assigned Research Areas as a 211-node visual entrance. The synthetic `classification:physics` destination is a metadata-only header/root, not a plotted point. Disciplines have depth 0; areas have depth 1. Shared areas have one canonical source-derived ID and multiple classification parents.

The source is the [APS classification vocabulary release v2.8.0](https://physh.org/releases), pinned to [Git commit 04b9cec3e633aa1abf68f2a09868fdc56be12e60](https://github.com/physh-org/PhySH/tree/04b9cec3e633aa1abf68f2a09868fdc56be12e60). The single JSON-LD download has compressed SHA-256 `4030abdc5ab09afbe67e4f3f8b3aa840f570e5c3a2bbe7e7af9bd0c6692171bf`. The scheme is available under [CC0](https://physh.org/licensing); attribution here identifies the source, not a new product branding or APS endorsement. No API crawl or paper ingestion was performed.

There are 3,910 source entities. Of 19 discipline-typed records, one is the universal scheme and one is deprecated General Physics; the remaining 17 form the frontier. The 194 coarse areas are exactly those directly assigned to an active discipline and to the Research Areas facet. Their broader/narrower descendant closure spans 2,246 nondeprecated concepts. Other facets and all source entity labels/relationships remain inspectable in the pinned download and `results/taxonomy.json`; the plotted chart is deliberately a research-area overview, not every taxonomy facet at once.

## Coordinates and the failed first layout

Let `H[c,r]` indicate that concept `c` is in the recorded narrower-descendant closure of coarse area/discipline `r`. Normalize each membership column; its Gram matrix gives shared-concept cosine affinity. These values measure classification overlap, not paper similarity, scientific dependence, research volume or importance. Exact discipline-to-area assignments are separately exported as 211 directed classification edges.

The first construction used two nonconstant lazy-diffusion modes of this affinity graph. Slurm **61430828** completed in five seconds, but the 197-node main component retained only 3.5% of nonconstant spectral energy and collapsed most disciplines near the center. Its within-diffusion-space distance stress was 0.829 and top-five neighbor recall 0.096. The baseline is retained under `results/`; it is not the selected chart.

The selected construction uses shortest-path distances on the same positive affinity graph, with display edge length `1/sqrt(cosine)`, then metric stress minimization in two dimensions. This monotone length mapping is an explicit display choice with no empirical physics units. Classical initialization and four fixed random starts are compared; the lowest-stress result is retained. Slurm **61432371** completed in 11 seconds. Source memberships, IDs and classification edges are unchanged.

| Same graph-distance target | Diffusion baseline | Selected stress layout |
| --- | ---: | ---: |
| Main-component normalized stress | 0.679 | 0.206 |
| Main-component top-five neighbor recall | 0.226 | 0.263 |
| Education-component normalized stress | 0.564 | 0.348 |

The remaining distortion is substantial: visible proximity is only a browsing aid. Tied graph distances use fixed source order in neighbor diagnostics. The education component contains 14 nodes and is disconnected from the 197-node component under this particular shared-descendant construction. Components are uniformly scaled and packed on a deterministic grid; **between-component display distances have no meaning**. This is not evidence that education is scientifically isolated from other physics.

## Navigation contract

`orientation.kind` is `classification_graph`, with fixed recorded coordinates, exact classification links and source provenance. `entryDestinationId` is `classification:physics`; the explicit frontier lists all 17 disciplines. Nodes resolve to metadata-only destinations. No source-paper membership is fabricated for these classifications.

The detailed Swampland source chart remains `catalog.overview` in a different coordinate system. Portal nominations are curator navigation links from Particles & Fields, Gravitation/Cosmology/Astrophysics and Strings & branes; they are not APS taxonomy equivalences or new scientific assertions. `results/portal-nominations.json` deliberately leaves the final detailed destination binding to the assembler. An arXiv hep-th card may be an intermediate curator landmark, with its own category provenance. Switching chart spaces must be explicit and retain the same canonical destination/session machinery.

The broad chart does not claim an empirical all-physics paper geometry. The two coordinate systems must never be overlaid or compared as one global metric.
