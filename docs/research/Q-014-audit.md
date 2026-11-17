# Q-014 — Evidence audit and a falsifiable navigation experiment

2026-11-16. Research audit by `/root/navigation_research_audit`. This is a
read-only assessment of the saved construction and experiments, plus a proposed
experiment. No new algorithm, corpus embedding, hierarchy, or production behavior
was implemented or validated for this memo.

**Finding:** there is enough frozen data to compare navigation operations now.
There is not yet evidence that the current text search, overview hierarchy, and
scientific relation atlas are one coherent navigable object. The next experiment
should establish that shared state and isolate the benefit of graph propagation
before changing the embedding, semantic compiler, grouping, and labels together.

## What is actually available

| Representation | Existing evidence | Consequence for the proposal |
| --- | --- | --- |
| Current browser/local navigation | 6,478 catalog records; 6,477 represented papers; 8,473 question and 17,937 method descriptions; 384-dimensional MiniLM vectors | Source-linked, multi-facet retrieval exists. It is not a learned independent concept space. |
| Navigator graph | 422,560 directed retained affinity entries; strongest 16 distinct-paper neighbors per unit, plus same-paper incidence between lenses | Textual affinity and co-occurrence can guide retrieval. No reviewed scientific implication/equivalence links are imported here. |
| Current query representation | Lexical source retrieval supplies up to 18 real-vector anchors; no online query encoder | A new Qwen query vector cannot be compared with these MiniLM vectors. Unsupported terminology and logical conditions remain representation/compiler problems. |
| Current grouping | Top 64 facets; up to five MMR representatives; nearest-representative groups; PCA of group means | The next choices are temporary source-description groups. They are not children of the reviewed overview, nor automatically scientific questions. |
| Reviewed overview | Frozen MiniLM Leiden question hierarchy; overlapping organizational memberships and sampled review amendments | Useful reusable landmarks, not a complete or uniquely correct taxonomy. Alternative MiniLM/Qwen hierarchies have different memberships. |
| Richer upstream atlas | 281,128 scientific/paper objects and 296,130 retrieval vectors; selective cross-paper reviews | This is richer than the shipped two-facet engine. Its availability does not establish all-paper scientific edge coverage. |
| Reviewed cross-paper coverage | 120 pairs involving 160 papers; 97 accepted relation outcomes, 10 accepted no-relation, 9 deferred, 4 rejected | The 97 include 50 analogy-only, 30 uses-method, 9 supports-under-assumptions, 3 specializes, 3 same-result-under-dictionary, and 2 apparent-tension. These cannot be combined as undirected implication edges. |

The upstream wrap-up also records five explicitly withheld current outcomes.
Import must honor final status, publication/admission flags, scope, and withholding;
an intermediate validator's acceptance is insufficient. For example, the
extremality/repulsion dossier is deferred and promotion-withheld despite an
accepting validation stage. Cross-paper review does not cover all 6,477 papers.

Sources: [navigator construction](../geometry.md),
[upstream construction](/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/publication-v1/CONSTRUCTION.md),
[publication report](/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/publication-v1/REPORT.md),
[atlas wrap-up](/Users/emmy/Developer/physics-atlas-swampland/atlas-final-wrapup.json),
[withheld dossier](/Users/emmy/Developer/physics-atlas-swampland/atlas-relations/results/dossier-wgc-extremality-repulsion.json).

The current navigation manifest totals **84,970,640 uncompressed bytes**:
40,565,760 vector bytes, 30,949,732 unit-description bytes, 8,283,526 graph bytes,
2,772,900 paper metadata bytes, and 2,398,722 scope bytes. Units, vectors, and
graphs each have 13 shards. The existing loader loads everything. Saved Node
measurements report about 105 MB retained JS heap plus 41 MB vector buffers and
about 504 MB process RSS after allocation. These are not browser/mobile results.
The proposed first experiment can reuse this corpus and small result artifacts;
loading the entire richer atlas or launching a new encoder is unnecessary.

## Failures that the next design must retain as tests

1. **Context is not a small centroid adjustment.** A former 0.24 focus blend let
   KK → “what if they are dark matter?” retrieve generic dark matter, followed by
   axion/moduli drift on “how do they decay?”. Joint context-conditioned anchoring
   and scoring repaired that observed route. The contextual and generic dark
   matter runs had zero top-ten source-ID overlap; refreshing versus retaining
   stale KK focus changed the decay result substantially. A query string alone
   does not identify a destination.
2. **A long source description is not a reliable navigation command.** Selecting
   paper 2203.05575's axion-WGC/EDE method kept that source first but offered generic
   instanton/cosmology material next. Truncating its 266-character description to
   the first sentence lost the EDE application and did not repair the drift.
   Label shortening and target selection must be separate operations.
3. **Attractive coarse geometry can hide poor local geometry.** Weighted PCA
   preserved only 20.9–31.6% of source 5-nearest-neighbor relationships in the saved
   comparison. The decay five-centroid chart explained 70.2% of between-group
   variance but retained only 20% of centroid nearest neighbors. Coordinates
   cannot serve as semantic membership or claim-validation evidence.
4. **Missing children are sometimes missing data, not hidden buttons.** The
   compactification and inflation local splits failed the saved seed-stability
   gate; the neutrino region was below the mass threshold and was not attempted.
   The rejected memberships were not saved. Other stored hierarchies cannot be
   grafted in as exact children because their memberships cross these parents.
5. **The overview's diffusion label needs qualification.** Its two eigenfunctions
   are multiplied by eigenvalue-to-the-fourth factors and then standardized per
   axis/component; the positive factors cancel. It is effectively a standardized
   two-eigenfunction layout, not a faithful time-four diffusion-distance map.
6. **“Unresolved” means placement unresolved.** Thirteen descriptions were removed
   after two review stages agreed they were outside their sampled topic's scope.
   That does not mean their papers or claims are low confidence.

Evidence: [geometry experiments](../geometry-experiments.md),
[saved route results](../../tests/geometry/results.json),
[selection experiments](../../tests/geometry/selection-query-results.json),
[direction-chart results](../../tests/geometry/direction-chart-results.json),
[hierarchy audit](../Q-007-hierarchy-audit.md).

## What should count as the same place

The stable overview and a question-conditioned map answer different questions.
The overview supplies repeatable landmarks; a question highlights, combines, or
refines evidence around them. Making every new query repartition the world loses
orientation. Forcing every question into one existing branch loses cross-cutting
physics. An overlapping, versioned cover can support both, with explicit local
proposals when the stored cover is too coarse.

A navigation state must distinguish at least:

- **Membership:** the saved source-ID set or soft region membership, including
  non-displayed members. Top-64 displayed evidence is not the region itself.
- **Relevance:** question-dependent weights over sources, computed from canonical
  seeds, conditions, lens, and a declared propagation rule.
- **Scientific context:** the question, retained referents, constraints,
  assumptions, and whether the action refines, pivots, or changes a lens.
- **Scale:** organizational granularity, query-locality, and camera zoom. These
  are separate quantities.

A click must carry a canonical action/region identifier and context update.
Its human-readable label is presentation. Exact click/text equivalence is possible
when text explicitly names that action or the agent sends its ID. For arbitrary
paraphrases, the achievable claim is agreement on scientifically appropriate
evidence and context, not identical coordinates or an identical ID in all cases.
Ambiguous paragraphs can legitimately refer to multiple regions. The same words
in different histories can legitimately select different evidence.

An explicit **refine** can intersect retained membership and preserve constraints;
applying the same refinement again should not silently narrow it further. A
**pivot**, **bridge**, or **change of lens** can leave that region, with the change
recorded. A method/application relation is not automatically a child-topic
relation. Repeatedly using the previous relevance vector as a new diffusion seed
would change the state even for the same command; recomputation from canonical
seeds avoids that accidental history dependence. This does not require the
numerical relevance distribution itself to be an idempotent diffusion operator.

Diffusion can select relevant neighborhoods. It cannot determine that two
assumptions are compatible, infer a novel research question, or certify a
scientific implication. Source-grounded question descriptions require an
additional interpretive step. Existing claim/method/assumption records are inputs
to that step, with their original uncertainty and scope intact.

## A bounded comparison that separates the causes

Do not first replace the encoder, introduce an LLM compiler, add diffusion, change
grouping, and write better labels, then attribute the improvement to geometry.
Use these successive comparisons:

| Comparison | Fixed inputs | Only change | What it resolves |
| --- | --- | --- | --- |
| 0. Replay baseline | Frozen engine and saved requests | Nothing | Preserve observed regressions and current strengths. |
| 1. State/action baseline | Same source-ID seeds, explicit constraints, corpus, candidate budget, labels | Canonical actions versus label-to-query roundtrip | Whether shared state repairs route identity and repeated-action drift. |
| 2. Graph ablation | Identical compiled states, seeds, lexical/vector terms, allowed IDs, grouping | No graph term versus declared personalized propagation | Whether graph propagation adds useful evidence after context is already correct. |
| 3. Grouping comparison | Identical relevance scores and candidates | MMR versus scored intersections with the stored cover versus a recorded local partition | Whether alternatives produce more useful, less redundant next steps. |
| 4. Language entry | Same downstream operator and independently frozen task evidence | Current lexical anchors versus stronger retrieval/compiler | Whether missing terminology or reasoning is the bottleneck. |

For comparison 2, the existing 0.65 restart is a concrete initial parameter, not
a recommended universal constant. Predeclare two sensitivity settings and the
number/tolerance of iterations. State whether propagation uses the original
directed navigator graph or the upstream symmetric graph; these are different
operators. Apply explicit exclusions throughout selection and traversal. Measure
the graph's incremental witness recall and topic leakage, not just smoothness.

For comparison 3, “membership threshold plus local clustering” is still too
underspecified. A candidate must declare: the membership convention; complete
region versus truncated retrieval window; edge boundary treatment; objective and
resolution; seed; child size/stability gates; treatment of overlap; and behavior
when no split qualifies. Initially, saved cover intersections are a cheaper,
more inspectable baseline than inventing a new partition. Five is a display
budget, not evidence that five disjoint scientific children exist. A leaf can
offer source material, alternate lenses, or explicit pivots without fabricated
hierarchical depth.

Boundary treatment is material. Restricting a walk to an induced subgraph and
renormalizing creates reflecting boundaries and can manufacture apparent
communities. Record original boundary conductance or retain a halo, and declare
whether flow is reflected, killed, or restarted. Likewise, conserving total edge
mass in a coarse graph does not establish equivalent multi-step diffusion: exact
compatibility requires a lumpability/intertwining condition such as `P H = H Q`
for the chosen coarse transition matrix. Measure coarse/fine discrepancy rather
than asserting it from `Hᵀ W H` alone. These mathematical review points were
contributed independently by `/root/navigation_mathematics`.

## Twelve source-supported evaluation cases

Freeze these cases before tuning. This is a small **falsification set**, not a
statistical certification of all physics. Cases 1–8 include protocol checks and
known regressions; they must not be advertised as newly held-out successes.
Cases 9–12 use existing audited scientific examples not used in the saved
navigation evaluations, so they can serve as navigation holdouts. Their old
scientific assessments remain qualified evidence, not independent gold truth.

| # | Task and evidence witness | Check and failure criterion |
| --- | --- | --- |
| 1 | Select a saved direction, export/import its exact action; rename its display label without changing the action. Use any frozen KK direction in `results.json`. | Exact IDs, context, membership, exclusions, and computation version roundtrip. Cosmetic text must not change the target. Explicitly excluded witness IDs must never return through graph propagation. |
| 2 | Compare “what if they are dark matter?” with KK context against a fresh generic-dark-matter query. Witness 2311.05318 versus generic 1511.06768 in the saved route. | Context must matter; do not demand identical results merely because the words overlap. Inspect unsupported referent resolution explicitly. |
| 3 | Reach KK-tower dark matter by paragraph and by clicking an equivalent prepared card. Witnesses 2311.05318 and 2212.08527. | Agreement on the intended evidence/context; exact equality only for identical canonical action. No forced numerical equality for independently interpreted paraphrases. |
| 4 | After KK dark matter, ask how the tower decays. Witness 2209.09249's coupled KK Boltzmann method; compare with deliberately stale KK focus. | Preserve the current dark-matter referent and retrieve the decay mechanism, not generic moduli/axion decay. Repeated identical refine should not cause further drift. |
| 5 | Select the axion-WGC/EDE method of 2203.05575 and continue on that application. | Preserve the EDE restriction; first-sentence truncation is the known failed baseline. Generic instanton neighbors are not sufficient evidence of successful refinement. |
| 6 | Start at black-hole entropy, then seek higher-derivative corrections. Witnesses 1003.2850, 2305.10489, and 1901.11535 from saved non-KK runs. Compare with an explicit generic higher-derivative pivot. | Distinguish a contextual lens/refinement from a global pivot. Do not represent imported Wald/attractor results as newly derived by the citing paper. |
| 7 | Open the 3,260-facet compactification region and request smaller directions. | Report that the frozen nine-child proposal failed stability; any new children need new recorded memberships and source-grounded meaning. A label over an arbitrary top-64 grouping is not an existing reviewed child. |
| 8 | Open the 132-facet neutrino region and ask for more detail. | Distinguish “not attempted below mass threshold” from “physics has no substructure.” Offer genuine evidence/lenses or a declared new partition; do not fabricate five children to satisfy UI depth. |
| 9 | Ask whether an integrated internal-curvature scale establishes a lightest spin-2 KK mass bound. Witness pair 1512.00457 and 2104.12773. | Retrieve the curvature/spectrum distinction and geometric-control caveat. Do not convert textual adjacency into an accepted theorem or pretend the deferred relation is settled. |
| 10 | Ask whether an inclusive lattice-WGC convex-hull condition ensures strictly positive-energy decay. Witness pair 1402.2287 and 1509.06374. | Preserve normalization, spectrum, boundary/strictness, and charge-quantization distinctions. The source pair is deferred; returning a blanket equivalence fails. |
| 11 | Ask when extremality and repulsive-force criteria coincide, varying massless scalars and single-particle versus full-spectrum conditions. Witness 1509.06374 and 1906.02206. | Show the scoped distinction; honor the dossier's promotion-withheld status. Similarity must not erase the hypotheses or strong pairwise-repulsiveness issue. |
| 12 | Locate 0803.3295's gravity-dual-of-superconductivity question after its removal from EFT consistency. | Keep it findable without treating its unresolved placement as low scientific confidence. The audit supports the removal, not a gold alternative home. Allow a qualified candidate home or explicit unresolved placement. |

For precise saved source IDs, case 3 includes
`be7aae21bb2419d0869faff0e2d1c1e653b0e8e75d40ce2e657fb8fb7495284a`
(2311.05318); case 4 includes
`d3887234965b5e3e9d140318aad409dd55443ac72acf08c7f898c784033142e5`
(2209.09249); case 5 includes
`3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`
(2203.05575). Other saved IDs and texts are in the linked navigation results.

Holdout evidence: [curvature/spectrum pair](/Users/emmy/Developer/physics-atlas-swampland/atlas-relations/results/pilot-ads-curvature-spectral-bounds.json),
[convex-hull pair](/Users/emmy/Developer/physics-atlas-swampland/atlas-relations/results/pilot-wgc-convex-hull-reduction.json),
[extremality/repulsion dossier](/Users/emmy/Developer/physics-atlas-swampland/atlas-relations/results/dossier-wgc-extremality-repulsion.json),
and [removed-placement audit](../Q-007-hierarchy-audit.md).
Those scientific claim objects are not all exposed by the current two-facet
navigator. A holdout failure may therefore identify missing representation or
provenance access rather than a bad diffusion operator. Record that separately.

## What to measure, and what not to claim

Report exact protocol success separately from semantic navigation. For each
scientific case retain witness recall, judged relevance of a small blinded
candidate pool, assumption/constraint violations, paper diversity, and the
reason a suggested next direction is useful. Report paraphrase agreement using
weighted source overlap plus scientific judgment; neither exact source equality
nor high overlap alone is semantic correctness. Judge representative, boundary,
and omitted witnesses, not only the first attractive card.

Measure repeatability under small seed/edge perturbations, depth/coverage versus
redundancy, and the difference between membership and displayed evidence. Report
layout stress/neighbor retention separately from retrieval quality. Record
latency, asset bytes, and peak memory on the actual target runtime before making
browser responsiveness claims. Unsupported or out-of-corpus questions should
produce a scoped limitation or an independent-search handoff, not an invented
region presented as knowledge coverage.

The corpus freeze, source scope, review state, chosen operator, seeds, and effective
parameters should accompany each experimental view. This is reproducibility
metadata, not a new tracing service. The existing notebook and ordinary Git
checkpoints are sufficient to preserve consequential decisions.

## Useful primary-source baselines

- [BEIR](https://arxiv.org/abs/2104.08663) gives a reason to retain a strong lexical
  baseline and compare retrieval families on out-of-domain tasks. It does not
  establish which model works best for these physics extractions.
- [G-Retriever](https://arxiv.org/abs/2402.07630) formulates textual-graph retrieval
  using a prize-collecting Steiner-tree objective. It supplies a concrete optional
  connected-subgraph baseline for bridge questions. Forcing connectivity can also
  add irrelevant intermediate nodes when a query is genuinely multimodal; a
  connected graph is not proof of a coherent scientific argument.
- [GraphRAG](https://arxiv.org/abs/2404.16130) supports considering cached community
  summaries for broad corpus questions. Its reported global summarization results
  do not establish local navigation equivalence or a latent physics metric.
- [BRIGHT](https://arxiv.org/abs/2407.12883) motivates testing reasoning-dependent
  retrieval rather than assuming a stronger text encoder solves all interpretation
  problems. Its benchmark is not validation on this corpus.
- [Fortunato and Barthélemy](https://arxiv.org/abs/physics/0607100) and
  [Kumpula et al.](https://arxiv.org/abs/cond-mat/0610370) explain why modularity-type
  resolution choices do not supply a universal scientific granularity. The
  project's actual stability/depth gates remain explicit design decisions.

**Recommended next action:** freeze the 12-case evidence set, define canonical
membership/relevance/action semantics, and run comparisons 0–2 with identical
seeds and unchanged embeddings. Only after that result should local partition
objectives and source-grounded question labels be compared. No transport or
projection choice can substitute for these semantic and scientific checks.
