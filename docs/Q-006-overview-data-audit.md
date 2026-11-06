# Q-006 — Fixed overview data audit

Read-only discovery by `/root/stored_view_backend`, 2026-11-06. This records
existing artifacts and a proposed compact projection. No source corpus, layout,
membership, runtime, or deployment was changed; no browser was launched locally.

## Recommendation

Use **one fixed physical-question view** from the existing reviewed atlas for the
initial collaborator demo. It contains 8,473 extracted question descriptions from
6,477 papers, twelve hierarchy nodes including the root and an unresolved region,
and 42 aggregate topic-affinity links. Each dot is a description, not necessarily
a distinct paper. The same paper can contribute several descriptions and occur
in several regions.

The existing layout already produces a legible broad overview; the archived
`publication-v1/qa/desktop-overview.png` was inspected as an image. A new renderer
can borrow the IAIFI Paperscape camera, label-reveal, and inspection interaction
without changing this dataset. This is separate from the question-conditioned
explorer. Neither camera zoom nor selecting an overview region should compute a
new contextual view or replace a saved exploration.

The supplied hierarchy is shallow. Four substantive broad regions and one
unresolved region appear at the top; only the black-hole umbrella has six supplied
children. Zoom can reveal those children and individual descriptions, but it must
not imply that every region has further scientific subdivisions. The method view
has more subregions but organizes operations rather than the scientific-question
story. It is an alternative for a later choice, not needed for this one-view demo.

## Exact reusable source

The external source root is
`/Users/emmy/Developer/physics-atlas-swampland/`.

| Artifact | Purpose |
| --- | --- |
| `graph-design/20261105-v1/publication-v1/map-data.json` | Final reviewed memberships, labels, source units, fixed coordinates, catalog, and recomputed topic links |
| `graph-design/20261105-v1/publication-v1/MANIFEST.json` | Closed release inventory and source hashes |
| `graph-design/20261105-v1/publication-v1/CONSTRUCTION.md` | Precise affinity, Leiden, refinement, overlap, coarsening, and display conventions |
| `graph-design/20261105-v1/publication-v1/REPORT.md` and `TOPICS.md` | Sampled-review scope, unresolved concerns, and reviewed topic index |
| `graph-design/20261105-v1/publication-v1/coarse/COARSE.json` | Exact current-membership coarse-affinity provenance |
| `components/graph_design_geometry/run.py` and `README.md` | Frozen geometry exporter and predeclared experiment |
| `components/graph_design_coarse/run.py` and `README.md` | Membership-preserving recomputation of aggregate links |
| `graph-design/20261105-v1/text-explorer-v4/PROVENANCE.json` | Independent prior presentation of the same reviewed source snapshot |

The map is **144,689,193 bytes** with SHA-256
`a6cb5cdb6d955d3ca33b9297be0a301ea50c6c8c75ba2294999adac8163d765b`.
Its release manifest has SHA-256
`907ab3ff3ce99744908d97ab185aaee34ab7f6a869a9b854b2cd302b3b3a7414`.
The manifest's map entry matches both the byte count and computed hash.

This is already an input pinned by Eigenquestions
[manifest](../data/navigation/manifest.json) and
[corpus builder](../scripts/data/build-corpus.py). The active corpus imports its
paper catalog but does not currently import its global hierarchy or coordinates.
The source snapshot ID is `swampland-graph-design-20261105-v1`.

The proposed view ID is `minilm-leiden:physical_question:reviewed`.
The alternative is `minilm-leiden:method:reviewed`. All **26,410** unit IDs across
these two views match the current frozen corpus exactly; every stored text hash
and lens also matches. There are no missing current unit references. All point
coordinates are finite, hierarchy parents resolve, and no parent cycles or
unknown direct topic homes were found. This verifies identity and structure,
not scientific correctness.

## What the clusters and plane mean

The original graph uses normalized MiniLM text vectors. Each paper contributes
total base mass one in a lens: a unit from a paper with `n_p` descriptions has
`m_i = 1/n_p`. The original construction selects up to 24 distinct-other-paper
neighbors, excludes same-paper edges, applies the declared cosine threshold,
and union-symmetrizes a self-tuning affinity:

`W_ij = m_i m_j exp[-d_ij²/(sigma_i sigma_j)]`.

The fixed candidate used Leiden's configuration-model objective with resolution
0.5 and seed 20261105, chosen before the trials. Explicit induced-subgraph
refinement at resolution 1 supplies the nested second level. It was retained
only under the documented size and three-seed stability criteria: parent mass
at least 160, 2–16 children, at least 20 units and mass 20 per child, and pairwise
ARI at least 0.7. Separate resolution runs were not treated as a nested tree.
These are organizational choices and stability checks, not a physical taxonomy.

The displayed coordinates reuse two stored nonconstant diffusion modes of the
lazy graph walk, multiply by eigenvalue to power four, then standardize each
axis within its connected component. That standardization cancels a nonzero
positive time factor. The display is therefore effectively a standardized
two-eigenfunction plane, **not a faithful time-four diffusion-distance plot**.
The question view has one connected component containing all 8,473 units, with
no fallback packing. Axes are not comparable between question and method views;
proximity does not establish equivalence or implication. Reuse the supplied
coordinates, without paper averaging or a new projection.

Topic labels and membership edits came from sampled agent proposals, independent
challenges, and fresh-paper applicability checks. The final source status of all
45 named topic cards is `agent_proposed`; the root is `draft`, and the unresolved
region is `deferred`. Four question cards and sixteen method cards carry explicit
fresh-source concerns. The source's phrase “reviewed view” describes the review
process; it does not upgrade these cards to validated or authoritative topics.
Preserve the qualified summaries, status, limits, and concern flags when deriving
an overview. Do not attach a universal “validated” badge.

## Membership and edge fidelity

The question view has 8,463 units with one direct home and ten with two homes.
The method view has 17,905 with one home and 32 with two. One question unit and
two method units have a direct home in an internal node. Derive ancestor
membership from the hierarchy, but retain these direct homes rather than forcing
every unit into a single leaf.

An important field convention: `topic_membership_weights` sums to the unit's
**base mass**, not to one. A unit with `h` direct homes contributes `m_i/h` to each
home. This equality holds exactly for every inspected unit. The normalized
membership matrix used for coarsening instead has `H_iC = 1/h`. These are
organizational weights, not membership-confidence or truth probabilities.
Topic paper counts overlap and must not be added to produce corpus coverage.

The unresolved question region retains thirteen descriptions from thirteen
papers. The method unresolved region retains 57 descriptions from 56 papers.
Those sources were not rejected as scientific claims. Keep them visible and
inspectable rather than silently dropping them as noise.

The 42 question links and 164 method links connect **topics**, not individual
papers, citations, or source statements. They are computed from the full pinned
affinity after the reviewed membership edits as `C = Hᵀ W H`. The archived full
matrix includes its diagonal and conserves total affinity. The displayed links
are the union of each topic's six strongest positive off-diagonal links; a topic
can therefore have more than six displayed links. Every stored display link is
`kind: text_similarity`, with
`membership_basis: current_reviewed_memberships`.

Keep that link type explicit. A cluster-outline or ancestry connector is a
different graphical relation. The active contextual graph keeps only sixteen
other-paper neighbors per unit, so recomputing these coarse links from its
truncated shards would not reproduce the supplied overview. Reuse the 42 stored
links and their provenance if displaying edges.

## Actual question hierarchy

Counts are stored facet counts and distinct-paper counts for each region. Region
counts can overlap; they are not disjoint corpus partitions.

| Top-level region | Facets | Papers | Supplied children |
| --- | ---: | ---: | ---: |
| String compactifications: effective theories, vacuum constraints and moduli limits | 3,260 | 2,568 | 0 |
| Black-hole response and entropy: model dependence and quantum-gravity constraints | 1,992 | 1,706 | 6 |
| Inflation and scalar dark-sector cosmology: observations and theoretical consistency | 3,081 | 2,407 | 0 |
| Neutrino mass origins and tests: symmetries, extra dimensions and quantum gravity | 132 | 128 | 0 |
| Descriptions awaiting a better home | 13 | 13 | 0 |

The black-hole umbrella's exact children are:

| Child region | Facets | Papers |
| --- | ---: | ---: |
| Quantum-gravity consistency of effective field theories | 663 | 574 |
| De Sitter quantum gravity: horizons, observables and consistency | 149 | 135 |
| Black-hole and holographic entropy: origins and consistency | 258 | 234 |
| Holographic quantum gravity: boundary descriptions, information bounds and consistency | 352 | 331 |
| Euclidean wormholes: quantum consistency, couplings and cosmological saddles | 135 | 129 |
| Black-hole extremality and entropy as tests of weak gravity | 439 | 406 |

The breadth of those children is another reason to preserve provisional wording.
This audit did not rename the umbrella or claim its current membership is an
ideal scientific classification.

## Method alternative, for comparison

The method view has 17,937 descriptions from 6,474 papers and 37 hierarchy nodes:
one root, six top-level nodes including unresolved, and thirty second-level nodes.

| Top-level region | Facets | Papers | Supplied children |
| --- | ---: | ---: | ---: |
| Radiative stability and perturbative cutoffs in effective field theory | 3,745 | 2,454 | 12 |
| Scalar cosmology: slow-roll predictions and field trajectories | 4,233 | 2,410 | 10 |
| Reduced equations for gravitational backgrounds and scalar equilibria | 4,114 | 2,625 | 0 |
| Building scalar potentials and testing vacua in supersymmetric theories | 1,787 | 1,336 | 8 |
| Geometry, charge lattices and form-field reduction in compactifications | 4,014 | 2,291 | 0 |
| Descriptions awaiting a better home | 57 | 56 | 0 |

The twelve radiative-stability children are: Effective couplings: canonical
normalization, running, cutoff estimates and conditional bounds; Dispersion and
factorization methods for scattering constraints with gravity; Computing
renormalization flows and quantum effective actions; Spectral positivity and
moment constraints in scattering EFTs; Functional determinants and heat kernels
for effective actions and free energies; Heavy-field reduction and radiative
corrections in effective theories; Integral and series methods for amplitudes,
spectra and geometry; Correlation-function methods in cosmology, holography and
string worldsheets; Mode methods for cosmological spectra, clockwork masses and
boson-star stability; Mode reduction and source matching in gravity; Calculating
compactification vacuum energy: Casimir sums and string modular integrals; Tower
spectra, species cutoffs and effective-action matching.

The ten scalar-cosmology children are: Slow-roll inflation: dynamics, perturbation
normalization and consistency checks; Slow-roll scalar cosmology: trajectories,
spectra and stabilization; Finding and testing scalar-potential vacua;
Cosmological parameter inference, reconstruction and model comparison; Evolving
cosmological backgrounds with Friedmann, scalar and fluid equations;
Post-inflationary histories: epoch matching and relic-abundance calculations;
Euclidean bounce methods for vacuum decay; Neutrino mass calculations and
conditional constraints; Methods for inflationary dynamics and primordial
fluctuations; Axion kinetic normalization, masses and conditional light-field
reduction.

The eight supersymmetric-vacuum children are: Supersymmetric effective actions:
superfields, compensators and vacuum constraints; Kähler effective-action methods
for moduli potentials, masses and couplings; Constructing scalar potentials and
analyzing vacua in supergravity; Killing-spinor methods for supersymmetric
backgrounds; Constructing scalar potentials and testing vacua in 4D N=1
supergravity; Mass-matrix methods for vacuum stability, AdS spectra and
interactions; Effective supergravity: reduction, symmetry and vacuum analysis;
Embedding-tensor methods for constructing and analyzing gauged supergravity.

## Compact artifact bounds

Do not ship the 145 MB source release to the browser. An in-memory, standard-JSON
projection of the **question view only** measured the following sizes. These are
schema estimates, not produced or deployed product files or browser timings.

| Projection | Raw UTF-8 bytes | gzip bytes |
| --- | ---: | ---: |
| Indexed geometry, topic prose/status/limits, 42 links, layout/coverage, and all 6,477 paper IDs/titles/URLs | 1,865,240 | 731,009 |
| The same plus all 8,473 exact question texts | 3,676,860 | 1,282,820 |

The first estimate used points encoded as
`[unitId, paperIndex, x, y, mass, directHomeIndices]`, preserving original
floating-point coordinates and exact IDs. Topic membership weights are recoverable
exactly as `mass / numberOfDirectHomes` for this source. Paper rows were
`[paperId, title, url]`. The metadata kept exact topic IDs/parents/children, labels,
summary, status, limits, counts, coordinates and representative source IDs. A final
artifact should also carry the source/view hashes, concern flags, field schema,
and source-text shard inventory; these were not all in the size estimate.

The text array alone is 1,811,611 bytes. Splitting its existing source order into
512-record arrays gives seventeen detail shards, each at most 115,426 bytes.
Fetch the matching shard only on point inspection and verify its hash. An initial
payload below 3 MB raw is therefore feasible while every point has exact title,
source URL, question text and identity available without loading vectors or the
contextual computation engine. Keep source row IDs or an explicit row binding so
that shard alignment cannot silently drift.

Review dossiers total approximately 9 MB across 45 proposal/challenge and 45
fresh-check files, plus page images. Do not accidentally import those or retain
broken relative `review_url` links. A minimal overview can preserve qualified
summary/status/concern fields and source-paper links, with exact full dossiers
archived in the original release. If the product offers a review-dossier action,
it must package or link a real reachable dossier.

## Alternatives discovered but not recommended for this first view

`atlas-embeddings/20261104-minilm-v1/layout.json` supplies 6,478 paper coordinates
from UMAP with seed 42, cosine metric, 20 neighbors and minimum distance 0.12.
Its metadata reports a sampled local trustworthiness of 0.8846 on 1,000 points.
Those are a different paper-level chart, not the reviewed source-unit diffusion
plane. Combining it with the reviewed facet hierarchy would introduce a new
aggregation/display interpretation; it is unnecessary for the bounded demo.

The older `organization-public/20261104-v1/` bundle contains normalized-cut trees,
affinities, diffusion coordinates and automatic unreviewed labels. Eight raw
MiniLM/Qwen and normalized-cut/Leiden alternatives remain in the final map. Keep
them as provenance and comparison material; selecting more variants is not
required to present one good fixed view.

The IAIFI reference source is
`/Users/emmy/Documents/PocketPostdoc/Code/IAIFI/`; Sol owns its independent visual
audit. Its clustering and paper coordinates are a different corpus and should
not replace or rename these Swampland memberships.

## Remaining verification before a demo claim

The proposed compact producer should verify source hashes, exact unit/paper ID
binding, text hashes, membership/ancestry conservation, unresolved coverage, and
finite coordinates. Then test the standalone overview in Slurm Chromium at
desktop and phone widths: fixed initial camera, readable zoom labels, actual
point/source inspection, overlap disclosure, and repeatable region zoom. Confirm
the contextual page, saved state, computation identity and network-loading policy
remain unchanged. The present audit establishes data reuse and a feasible size
bound; it does not claim that the new overview has been built or browser-tested.
