# Q-014 — Mathematical construction for text and click navigation

Research memo, 2026-11-16. Contributor: `/root/navigation_mathematics`.
Status: source-based analysis and a small synthetic calculation; no corpus experiment,
new scientific clustering, runtime change, or deployment has been performed.

## Recommendation

Use an automatically constructed **multiscale overlapping atlas plus a common region
operator**. Text and clicks are two input languages for that operator. A view is a
source-linked region, its relevance distribution, and a small set of typed next
actions. Projection to two dimensions follows those decisions.

Diffusion is useful for relevance propagation and scale-dependent community proposals.
It is not, by itself, the meaning of refinement, a semantic parser, a hierarchy, or a
generator of scientific questions. The central design requirement is to distinguish:

1. **Scope/membership:** which objects belong to the current scientific region.
2. **Relevance:** which of those objects matter most for the current question.
3. **Organization:** which useful subdivisions or alternative directions to expose.
4. **Display:** how to draw them without destroying orientation.

This is an implementable hypothesis to compare against alternatives, not an empirical
claim that the proposed hybrid wins on Swampland.

## Existing baseline and its actual limitations

The current browser engine uses lexical source anchors, actual frozen MiniLM vectors,
a three-step restart diffusion contribution, top-64 facet selection, MMR representatives
and nearest-representative groups. Its labels are representative source descriptions;
its plane is weighted PCA of five group centroids. Negation/logic are not generally
parsed from prose, and no fresh paragraph embedding is computed. This is a useful
retrieval/navigation baseline, but it does not supply the full operation requested here.
[Local geometry specification](../geometry.md) and [observed experiments](../geometry-experiments.md).

The upstream graph experiment already has MiniLM/Qwen alternatives, normalized-cut
and Leiden partitions, sampled Astra reviews, and preserved failures. The original
full affinity graph is symmetric; the browser retains each node's strongest 16
neighbors and therefore has a directed truncation. Do not apply symmetric-graph
theorems to that truncation without qualification or quietly change the input graph.
Use the original full weights for a symmetric comparison and record its identity.

## Alternatives worth comparing

| Construction | What it gives | Main failure for this project |
| --- | --- | --- |
| A single recursive normalized-cut/Leiden hierarchy | Stable addresses, cached drilldown, clear containment | Scientific overlaps and arbitrary question combinations cannot all be represented as descendants; independent resolutions need not nest |
| Personalized PageRank/heat retrieval, followed by fresh local clustering | Flexible regions around text/seeds; bounded/local computation | Regrouping on every step can drift or jump; a scalar relevance field does not supply a stable ontology or child semantics |
| Multiscale overlapping atlas, with query-local diffusion and explicit refinement/pivot operations | Stable broad orientation plus custom cross-cutting questions; clicks and text share operations | Needs careful region identity, membership, action semantics and evaluation; recommended candidate rather than a proven winner |
| Link-community organization | Overlap is native because a node can participate through several incident links | Source-graph edge meaning and degree bias matter; a generic edge hierarchy does not generate scientific questions or paragraph semantics |
| Diffusion wavelets/spectral coarsening | Efficient multiresolution operator representation and approximate large-graph computation | Numerical basis functions/coarse nodes need not correspond to understandable topics; compression does not establish semantic navigation |

Relevant primary sources: [Andersen–Chung–Lang, local PageRank partitioning](https://www.cs.cmu.edu/~15859n/RelatedWork/local_partitioning_full.pdf),
[Kloster–Gleich, heat-kernel communities](https://arxiv.org/abs/1403.3148),
[Delvenne–Yaliraki–Barahona, Markov stability](https://arxiv.org/abs/0812.1811),
[Ahn–Bagrow–Lehmann, overlapping link communities](https://arxiv.org/abs/0903.3178),
[Coifman–Maggioni, diffusion wavelets](https://www.sciencedirect.com/science/article/pii/S106352030600056X),
[Loukas, spectral/cut-preserving reduction](https://www.jmlr.org/papers/v20/18-680.html).
The first two provide graph-theoretic local-community results under their respective
assumptions; none certifies scientific relevance of the constructed physics graph.

## A region has membership and relevance, not just a centroid

Let the pinned graph have atomic source-linked objects V. Define a navigation state

    R = (graph_version, intent, predicates, m, seeds, locality, lens, provenance).

Here `m_i` lies in [0,1] and is an **unnormalized membership/gating weight**. It is not
the probability that a physical claim is true. Separate it from normalized relevance
`p_i >= 0, sum_i p_i = 1`. The same scientific region can be ranked differently when
the task changes from derivation to phenomenology without changing its identity.
An empty scope is an explicit result, not a reason to return unrelated sources.

A parent and child can satisfy `m_child <= m_parent` pointwise. Their normalized
relevance distributions cannot generally satisfy that inequality: every nontrivial
child renormalization increases some entries. Therefore probability mass alone is
the wrong object for checking whether a click genuinely narrows the scope.

For a first implementation, clauses should resolve to explicit region IDs, source
seeds, metadata predicates and declared intent changes. Known region predicates can
compose using a documented fuzzy/set algebra. For unknown concepts, retrieval and
source inspection propose new membership; preserve that accepted proposal explicitly.
Do not call embedding similarity a logical truth evaluator. A source of unknown
supersymmetry status cannot automatically satisfy “without supersymmetry.”

## The diffusion operator and its scope

Let P be a row-stochastic transition matrix, with a specified dangling-node rule.
For nonnegative normalized seeds s, compare:

    PageRank: p = alpha*s + (1-alpha)*P^T*p, 0 < alpha <= 1;
    heat:     p(t) = exp[-t*(I-P^T)]*s.

PageRank averages walk lengths with geometric weights; heat uses Poisson weights:

    p_heat(t) = exp(-t) * sum_k [t^k/k!] * (P^T)^k*s.

They have different scale profiles, so test them with matched expected walk length
`t = (1-alpha)/alpha`; do not pretend equal parameter values mean equal locality.
For a symmetric affinity W, PageRank also has a useful regularization interpretation.
With D=diag(W1), S=D^(-1/2)WD^(-1/2), L=I-S, y=D^(-1/2)s and x=D^(-1/2)p,

    x = [I + ((1-alpha)/alpha)*L]^(-1)y

minimizes `||x-y||^2/2 + ((1-alpha)/(2*alpha))*x^T L x`.
This algebra explains the tradeoff between seed fidelity and graph smoothness; it
does not establish that graph smoothness equals scientific meaning. The symmetric
variational form does not automatically apply to every directed/multiplex walk.

The seed signal can come from paragraph clauses, selected regions or explicit papers.
A paragraph can have several semantic aspects; collapsing it into one averaged vector
can erase conjunctions, contrasts and exclusions. The agent resolves meaning; code
executes the recorded selection and propagation. Keep similarity, citation and checked
scientific relationships as typed layers. If a lens mixes row-normalized transitions,
record its layer weights and dangling rules. A contradiction edge can aid discovery
without becoming a positive scientific-support edge.

For ranking within the scope, one transparent candidate is

    p_visible(i) = m_i * p_i / sum_j(m_j*p_j).

Retain the discarded exterior mass as a diagnostic and source of separately labeled
bridge proposals. This is an explicit design choice, not a calibrated posterior.
The graph can remain global even when the visible scope is restricted.

## Why repeating diffusion is not zooming in

For an unchanged heat generator, `K_s K_t = K_(s+t)`. Diffusing the last displayed
distribution again simply increases diffusion time. It generally broadens influence
and can wash context into the stationary distribution. It does not implement a
more specific question. Repeated restart smoothing similarly compounds a graph
filter unless seeds and state are deliberately reset.

A genuine within-parent child should instead compile a scope constraint. For a
child gate h with entries in [0,1], a simple idempotent fuzzy intersection is

    m_child = min(m_parent, h), elementwise.

Product gating `m_parent*h` also ensures containment, but repeated application of
the same soft constraint squares its weights. Use a canonical, deduplicated selector
expression if product gating is chosen. Repeated selection of the same child should
not manufacture depth. Store its accepted membership/selector, resolve child seeds,
and recompute relevance from that canonical state with its declared locality.

A connection to material outside the parent is valuable but is an explicit **bridge
or pivot**, not a child. “Show derivations” is usually an intent/lens operation; it
may traverse question-to-method/source incidence rather than mean “smaller topic.”
Cards should carry these action types and the exact selector. Their prose is a label,
not executable semantics. Source facets and paper-level scope need an explicit
incidence mapping when changing lenses.

## Text/click equivalence: what is and is not attainable

Exact equivalence is an engineering invariant after both inputs compile to the same
state/action on the same graph. Clicking a region executes its stored selector;
typing an unambiguous name can resolve to that region ID and execute the same action.
Typing the exact displayed label should not require reconstructing the selection
from that string. A paragraph that does not match a canonical region can create a
new source-backed region, which can then be revisited by a click.

Equivalent meanings in free language require empirical evaluation. There is no
guarantee that arbitrary paraphrases resolve identically, or that every conjunction,
negation and novel question has a finite path through a fixed tree. Preserve ambiguity
and allow several plausible entry regions. Do not force a custom question into the
nearest named cluster just to claim text/click consistency.

“Same place” should mean comparable scientific scope and constraints, not identical
pixels or identical displayed ordering under different intents. Different route
histories should affect the result only through explicitly retained scientific
context. The breadcrumb is not itself an unbounded numerical input.

## Populate the next view from evidence and multiscale candidates

Offline, compute and retain communities at several resolutions/scales, along with
repeatability and source-review evidence. Markov stability supplies an objective
for persistence of flow at a given time; optimizing at different times imposes no
nesting constraint. Preserve overlaps/crossings in a region graph rather than invent
a unique parent. Membership identity and scientific label should remain distinct.

Online, gather candidates from this atlas and a bounded neighborhood around the
current scope. Restrict true child candidates through the parent membership. If
strong evidence requires crossing its boundary, propose a bridge instead. Locally
generate new candidate refinements when the saved atlas has no useful subdivision.
An agent describes representative and boundary evidence, then a separate review
checks whether the description applies. This can produce topic children and specific
questions, but not every useful question is a low-conductance community.

Select roughly five useful actions by coverage, scientific distinctness, evidence
support and user task. Five is an interface budget, not the number of communities
the graph must contain. Two coherent children are better than five artificial ones.
Stop splitting when distinctions are unstable, near-duplicate, unsupported or based
on too little independent evidence; offer papers or supported question directions.
Do not equate low conductance, label fluency or a long path with scientific depth.

Keep three parameters separate:

- **Community resolution:** what scale of candidate organization we expose.
- **Query locality:** how far the current seed relevance propagates.
- **Camera zoom:** visual magnification and label density, with no semantic change.

The interface can coordinate them deliberately, but they are not the same variable.

## Boundary, popularity and density problems

Cutting out an induced subgraph and renormalizing rows turns its boundary into a
reflecting barrier. That can create apparent retention and communities absent in
the full graph. Alternatives have different meanings: a killed walk loses exiting
mass; teleporting exits restarts it; a halo approximates exterior influence. Choose
and report the boundary rule. Preserve full-graph degrees/exterior conductance for
diagnostics. First compare global diffusion followed by scope restriction against
a local-with-halo approximation; do not silently switch dynamics at each click.

For a reversible undirected walk, long-time mass follows degree, so raw diffusion can
favor general reviews or popular hubs. Inspect ranking relative to stationary mass,
but a pure `p_i/pi_i` lift can over-favor tiny-degree outliers. Compare mass and lift
with source relevance, clipping/regularization and held-out evidence. Citation flow
also reflects age, field size and citation culture; semantic edges reflect encoder
choices and wording. Neither is an independent scientific validation.

Count unique papers and retain paper-balanced source weights so intensive Swampland
extraction does not inflate its share of the all-physics map. Existing W already
contains source-mass factors; do not multiply them into W again accidentally.

## Coarse/fine consistency is an approximation question

For nonnegative allocation H with H1=1, coarse affinity C=H^T W H preserves total
one-step flow. With d=W1 and Q=diag(H^T d)^(-1)C, Q is a stochastic coarse walk.
However, one-step conservation does not make repeated coarse steps equal aggregated
fine steps. Exact agreement for every seed requires the intertwining condition

    P H = H Q.

For hard partitions this is the familiar strong-lumpability condition: members of
a block must have identical total transition probability into each other block.
See [Spectral State Compression of Markov Processes](https://pmc.ncbi.nlm.nih.gov/articles/PMC7971158/).
For a soft allocation, the same matrix identity is a sufficient algebraic condition
for the displayed commutation, not a claim of an ordinary hard-partition process.

Measure the residual `||PH-HQ||` and, for actual navigation seeds/scales,

    || H^T exp[-t(I-P^T)]s - exp[-t(I-Q^T)]H^T s ||_1.

Spectral approximation can motivate a useful reduction without demanding exact
lumpability. If broad physics uses paper metadata/citations while Swampland uses
fine question/method affinities, these are different representations, not guaranteed
compressions of one transition matrix. Connect them through stable paper/incidence
identities, expose the change of evidence depth and measure retrieval consistency.
Do not claim exact geometry across the seam merely because the camera transition
looks smooth. Exact lumpability should not be a usability prerequisite.

## Small executed synthetic check, not corpus validation

On a three-node undirected path 0--1--2, start at node 0 and call {0,1} the parent.
Heat diffusion at t=.5 has mass .03870453043654388 outside that parent. Applying
the same diffusion again gives .099894100223432 outside, agreeing with direct t=1
to maximum absolute error 1.1102230246251565e-16. This demonstrates the semigroup
failure mode; it says nothing about which physics neighborhood is correct.

Reproduction script, executed with Python standard library on 2026-11-16:

```python
import math
P = [[0., 1., 0.], [.5, 0., .5], [0., 1., 0.]]
def step(v):
    return [sum(P[j][i]*v[j] for j in range(3)) for i in range(3)]
def heat(v, t):
    term = list(v)
    weight = math.exp(-t)
    result = [weight*x for x in term]
    for k in range(1, 100):
        term = step(term)
        weight *= t/k
        result = [a + weight*b for a, b in zip(result, term)]
    return result
s = [1., 0., 0.]
first = heat(s, .5)
twice = heat(first, .5)
direct = heat(s, 1.)
print(first, twice, direct)
print(max(abs(a-b) for a, b in zip(twice, direct)))
```

Observed first = `[.6452351901491773, .3160602794142789, .03870453043654388]`;
twice = `[.4677735413948743, .43233235838169354, .099894100223432]`.
Separately, parent membership `[1,1,0]` and child `[.5,.2,0]` satisfy containment,
but normalize to `[.5,.5,0]` and `[.7142857,.2857143,0]`, illustrating why normalized
probability entries cannot be used as the containment check.

## Minimal experiment before choosing the new production engine

Freeze the existing full graph and source records. Compare (A) current dynamic
MMR engine, (B) a fixed best-available saved hierarchy, and (C) the atlas/region
pipeline above. Within C, ablate heat versus PageRank at matched walk-length scales,
global propagation versus local halos, and mass versus regularized lift ranking.
Reuse the current encoders initially to isolate the navigation change.

Use several independent families: KK towers/scale separation/dark matter, WGC and
multi-charge arguments, entropy/higher derivatives, inflation/de Sitter, and one
method-driven route crossing physical topics. Freeze natural-language tasks before
tuning. Include paraphrases, explicit negation, multi-clause constraints, a query
that should stay broad, an unsupported query and a cross-boundary bridge. Generate
agent-reviewed relevance judgments from source evidence, not inherited memberships;
expert feedback is welcome but not needed to start.

Measure: deterministic equality for identical compiled actions; weighted region
overlap for independently expressed equivalent questions; child containment;
preservation of required constraints; new evidence reached by bridge actions;
source-backed quality and distinctness of offered next questions; stability under
small query/seed/edge perturbations; coverage lost at truncated neighborhoods; coarse/
fine diffusion discrepancy; and interaction cost. Inspect failures individually.
Do not optimize overlap alone: two equally generic answers can agree perfectly.

Require an actual text route and click route to reach a comparable scientifically
specific region, then support the same next refinement. Replay must preserve the
accepted membership and context. Only after that succeeds should a better-looking
2D chart count as progress toward the requested atlas.
