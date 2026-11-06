# Q-001 — Reproducible question-conditioned geometry

The browser and local agent run the same dependency-free ESM engine,
[`lib/geometry/index.mjs`](../lib/geometry/index.mjs). It retrieves from the whole
frozen corpus on every operation, derives five directions from the current
neighborhood, and fits a new affine plane to their source-vector means. There is
no topic tree, saved sequence of screens, or special KK → dark-matter route.

## Frozen data and provenance

[`data/navigation/manifest.json`](../data/navigation/manifest.json) pins every
input and output file, encoder revision, dimensions, ordering and transformation.
The catalog contains **6,478 papers**, of which **6,477** have navigation vectors:
8,473 physical-question facets and 17,937 method facets. One catalog-only record
is not a retrievable vector. The snapshot is dated **2026-11-05**, with catalog
years 1969–2026; individual records have arXiv month precision or year precision.
“Recent” means recent within these inputs, never a live literature search.

Vectors are the existing 384-dimensional float32
`sentence-transformers/all-MiniLM-L6-v2` vectors at revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. The upstream encoder averaged all
254-token windows with 24-token overlap, then normalized; the organization build
L2-normalized the selected facet vectors. The adapter copies these values exactly,
without re-encoding, whitening, quantization or mixing encoder spaces. Maximum
source norm error is below 3.1×10⁻⁸. The question and method layers share that encoder
fingerprint but retain their separate original graph layers.

The build checks source hashes against upstream `INPUTS.json`, the text hashes,
and **exact equality** of `neighbors.json.unit_ids` to the `units.jsonl` line order
that binds each vector row. It preserves source facet/node/record IDs, original
embedding rows, text/source hashes, evidence-anchor IDs, review status and reading
scope. Unit descriptions are source-scoped extractions, not quotations or
independently established physics. Repeated reading scopes are losslessly
content-addressed in `scopes.json` and restored by `getEvidence` and view nodes.
Unused paper abstracts are omitted from the navigation distribution.

The public data are about **85 MB uncompressed**, with no file over 3 MiB. Runtime
loading verifies byte lengths and SHA-256 for **every** JSON and vector shard,
then checks row IDs, graph indices and finite vector entries. Inputs use only
root-relative public provenance paths. The original archives remain untouched.
The all-at-once loader is a desktop-oriented v1: it downloads both layers and
builds a local index before the first computation. A local Node measurement after
GC retained about 105 MB JavaScript heap plus 41 MB vector buffers; process RSS
was about 504 MB after allocation. These are not browser or mobile benchmarks.

Rebuild from the original archive with:

```sh
python3 scripts/data/build-corpus.py /path/to/physics-atlas-swampland
node scripts/data/pin-engine.mjs
node --test tests/geometry/*.test.mjs
node scripts/data/evaluate.mjs
node scripts/data/compare-direction-charts.mjs
```

## The graph and selection

The original affinity matrix is a self-tuning, paper-mass-balanced text-similarity
kernel. Its weights already contain source-unit mass factors. The adapter does
**not** multiply them by paper mass again. It retains each unit's strongest 16
neighbors from distinct other papers, preserving their original weights. This
reduces 984,116 original stored matrix entries to 422,560 directed retained edges.
Directed truncation is declared; it is not silently represented as a new symmetric
physical graph. Selected-view edges are typed `retrieval_affinity`. Same-paper
incidence across the two layers is typed `same_paper`. No reviewed scientific
implication/equivalence edge is imported or promoted in this v1.

A nonempty question first retrieves source facets with a length-normalized,
IDF-weighted lexical score and query-token coverage factor. A small documented
acronym normalizer includes KK/Kaluza–Klein; it is not a route table. At most 18
source anchors, one per paper, form a weighted mean of **actual** source vectors.
A selected focus supplies an additional real-vector centroid. There is no invented
query embedding and no online model call. Unsupported terminology with no source
match and no focus produces an empty result with a warning.

Refinement jointly conditions on the new question and focus. It extracts at most
six terms present in at least 60% of the focus source/title descriptions, combines
their evidence score with cosine to the focus centroid, and uses that context to
weight both anchor selection and candidate scores. This general operation resolved
the observed pronoun drift. The protocol refreshes focus from the current top-five
sources on each refinement; an external agent can instead supply explicit source
IDs. A pivot clears focus. History never confines the search to descendants.

Every legal unit is then scored from query-evidence matching (weight 0.44), squared
positive cosine to the anchored query (0.40), and personalized graph diffusion
(0.16). Three diffusion steps restart 65% of mass at query/focus anchors. Remaining
flow is 85% along row-normalized original affinities and 15% through same-paper
incidence. Missing outgoing graph edges retain their flow. Per-paper anchor caps
and a two-facet-per-paper display cap bound extraction-density bias. These rules
are organization heuristics, not calibrated scientific probabilities.

`derive` favors method facets and generic calculation/equation/proof cues.
`phenomenology` favors generic observation/measurement/constraint cues. No dark
matter, compactification or other domain concept is injected by an intent. Domain
concepts must come from the question, explicit focus or source descriptions.
`recent` adds a bounded age prior to relevance rather than returning unrelated
new papers. `workRelation:'on'|'using'|'either'` is independent: question facets
provide evidence of work **on** a subject, method facets of work **using** it.
At least half the query terms must match the relevant facet to assign that role;
other semantic neighbors are marked ambiguous. This evidence proxy cannot certify
an author's methodological role or replace reading the cited source.

Negation and logical conditions are not generally parsed from prose. The external
agent should resolve pronouns, use explicit excluded IDs/date constraints and
inspect evidence. The six-thousand-paper scope and lexical source-anchor coverage
remain substantial limitations, even though the subsequent geometry is real.

## Five directions and the affine plane

The 64 selected facets are grouped dynamically. Greedy MMR chooses up to five
representatives by a relevance/diversity tradeoff; each selected facet joins its
closest representative in the original normalized-vector metric. This is a new
local grouping for each question. It is not an inherited community partition.
Each direction uses an actual representative source description as its next
question, with source IDs and group membership available for inspection. A
currently selected source is not immediately offered again as the same query.
An agent should refine the scientific question rather than treat source selection
as guaranteed progress toward an infinitely deep hierarchy.

For source vectors \(x_i\) and positive retrieval weights \(w_i\), group \(g\) has
mass \(m_g=\sum_{i\in g}w_i\), centroid
\(z_g=m_g^{-1}\sum_{i\in g}w_i x_i\), and squared within-group spread
\(s_g^2=m_g^{-1}\sum_{i\in g}w_i\|x_i-z_g\|^2\).
The group means are **not** renormalized. They remain in the original 384-dimensional
Euclidean ambient space. Mass means selected retrieval importance, not evidence
strength, posterior probability or population size; `sourceCount` is separate.

The chart center is \(c=(\sum_g m_g)^{-1}\sum_g m_g z_g\). Weighted PCA fits two
orthonormal directions \(b_1,b_2\) to the five centroids about \(c\). Fixed
initialization, 64 power iterations, orthogonal deflation and deterministic sign
fixing make the fit reproducible. Degenerate and near-degenerate variance
boundaries are reported. An axis with no supported variance becomes zero rather
than a fabricated direction. The implemented comparison method constrains the
first axis to the query-anchor direction and uses PCA in its orthogonal complement;
it performed worse and is retained only for experiments.

The actual affine plane is
\(\Pi=\{c+\alpha b_1+\beta b_2\}\). A source or centroid projects to
\((b_1^T(x-c),b_2^T(x-c))\), divided by a common RMS scale for display. Its residual
\(r(x)=\sqrt{\|x-c\|^2-\|B^T(x-c)\|^2}\) is the distance to that plane in the
original metric. **Projection is not intersection.** The chart also defines a
finite thickness from the 80th-percentile centroid residual; `inSlab` is the
separate test \(r(x)\leq\text{thickness}\). The optional source overlay uses this
same plane and scale, so many sources legitimately lie outside that thin slab.

The main fidelity metrics describe **five centroids only**. The chart separately
reports `sourceDiagnostics` for the 64 source projections, including variance,
pairwise-distance stress, 1/5-neighbor retention and residuals. Direction cards
expose mass, source count and within-group RMS spread. Group means, memberships,
weights, center, basis and scale are all in the view object. Broad within-group
spread and poor nearest-neighbor preservation are not hidden by the coarse map.
No orientation, metric or apparent closeness is a physical observable or a
scientific implication.

## Identity, replay and bounded failure

`computationId` combines engine version, SHA-256 of the actual engine source,
SHA-256 of default parameters and SHA-256 of the exact manifest bytes. The manifest
pins every data file. `identity.mjs` is generated by `pin-engine.mjs`; a test rejects
stale code/parameter pins. Sessions store this identity and reject changed
computation inputs. Experimental direct calls may override documented numerical
parameters; full effective parameters are recorded in diagnostics. Public
protocol states use the frozen defaults.

The same-runtime replay tests require exact JSON equality. Across JavaScript
runtimes, floating-point geometry is intended to agree within 10⁻⁹ for fixed inputs;
that cross-browser tolerance is a numerical expectation, not a completed
cross-browser benchmark. IDs, candidate order and groups must remain identical.
When a corpus/engine upgrade changes identity, create a new session or explicitly
review/recompute the old state; do not call it an unchanged replay.

Tests cover empty/unknown queries, stale corpora/computation IDs, exclusions,
nonfinite/misaligned data, metadata corruption, disconnected and zero-rank geometry,
source selection, contextual refinements, non-KK intents and a second small,
explicitly synthetic adapter fixture. Empirical scientific and numerical limits are
recorded in [geometry-experiments.md](geometry-experiments.md).
