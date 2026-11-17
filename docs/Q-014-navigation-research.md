# Q-014 — One scientific navigation operation for paragraphs and clicks

2026-11-16. Synthesis by `/root`, with `/root/navigation_mathematics`,
`/root/navigation_semantics`, and `/root/navigation_research_audit`.

**Status:** research recommendation supported by a source/code audit, primary
literature, and a synthetic mathematical check. The proposed construction has
not been implemented or tested on the corpus. Existing production behavior is
unchanged. This refines Q-010/Q-012 and supplies the scientific object transported
by Q-013; it does not replace those requests.

## Decision

Build a **question-conditioned organization of a recorded scientific region**.
Both paragraphs and clicks specify that region through the same operation. Use
an automatically constructed, overlapping atlas at several scales for stable
orientation, graph diffusion for relevance and discovery, and explicit scope
changes for refinement. Generate a small number of source-supported next actions.
Compute the drawing after these scientific decisions.

This is a stronger recommendation about the architecture than about a particular
clustering algorithm. Which propagation and grouping choices work best is still
an empirical question. Neither a fixed tree nor repeatedly clustering a small
search result satisfies the whole requirement.

## What the operation consumes and returns

Conceptually, there is one function:

    navigate(versioned_graph, scientific_state, action)
      -> new_state, evidence, next_actions, display

The graph retains source objects, paper incidence, embeddings, and typed relations.
Similarity, citation, method use, analogy and conditional scientific support must
remain distinguishable. A transition used for discovery is not an assertion of
scientific implication. Honor final review/withholding status when admitting edges.

The scientific state records the question, resolved referents, assumptions and
restrictions, lens/task, complete region membership, canonical source seeds and
construction version. Membership is separate from relevance and camera position.
The top 64 displayed objects cannot stand in for the complete region.

The agent translates prose into this state/action, resolves scientific roles and
checks supporting evidence. Code executes the recorded numerical operations.
A click already carries a region reference and an explicit action; it must not
rerun a search using its display label. Labels can change without changing targets.

Ordinary clicks on cached regions should be immediate. Novel question-conditioned
views can require agent computation, with the existing view remaining usable.
Accepted region/action objects can be cached, shared and revisited without another
model invocation. Computational compression and lazy loading are compatible with
this design as long as they preserve source references and declared approximations.

## The four operations inside a view update

### 1. Resolve the scientific question

Keep a paragraph's aspects separate: subject, target question, method, application,
assumptions/regime, exclusions, and desired evidence. Start with a small supported
clause vocabulary and explicit region references, not a universal physics ontology.
Retrieve candidate source facets for each aspect, then check their roles in context.

For example, “using instanton calculus to constrain multi-axion field ranges” is
different from studying instanton solutions. Averaging two embedding vectors or
two seed distributions does not express their logical conjunction or relationship.
For any fixed linear diffusion K, K(a s + b t) = a K s + b K t: this is superposition,
not AND, NOT, or “method A addresses question B.” Unknown assumptions remain unknown;
mere mention of a forbidden assumption is not proof that the paper relies on it.
Apply regime and assumption restrictions to source-linked claims/settings before
aggregating to papers: one paper can discuss both sides of a distinction.

Several plausible readings can be kept as alternatives. A novel question may
create a region spanning existing topics; atlas labels must not limit what can
be asked. Multi-aspect scientific representations are motivated by
[ASPIRE](https://arxiv.org/abs/2111.08366); the dated
[NevIR study](https://aclanthology.org/2024.eacl-long.139/) motivates explicit
negation tests, not a claim about every current model.

### 2. Find evidence and nearby connections

The first propagation candidate is personalized PageRank on a pinned transition
matrix P, with normalized source seeds s and restart alpha:

    p = alpha s + (1-alpha) P^T p.

Restart keeps relevance tied to the interpreted question. Compare it against no
graph term before attributing gains to diffusion. Heat diffusion is a useful
contender, exp[-t(I-P^T)]s, compared at matched expected walk length
t=(1-alpha)/alpha. [Local heat-kernel research](https://arxiv.org/abs/1403.3148)
supports testing this family; it does not establish scientific relevance here.

Keep unnormalized membership m_i in [0,1] separately. Within-region ranking can use
q_i=m_i p_i / sum_j(m_j p_j), when the denominator is nonzero. Retain exterior
relevance as a diagnostic and as candidates for explicit connections. Membership
weights are organizational choices, not probabilities that scientific claims are
true. Declared hard exclusions must also be respected during candidate construction
and propagation under an explicit boundary rule.

Do not silently renormalize an induced subgraph at every click: that reflects flow
at the new boundary and can manufacture apparent communities. For the first
comparison, preserve global dynamics and restrict the visible scope; later measure
a local-with-halo approximation. Source and paper balancing, hub bias, graph layers,
and dangling-node behavior remain explicit. The original symmetric affinity graph
and the browser's directed strongest-neighbor truncation are different inputs.

### 3. Offer roughly five meaningful next directions

Start from automatically found regions at several resolutions. Preserve their
memberships, overlaps and uncertainty. Stable broad landmarks provide the physics
overview, while contextual questions can cut across them. Multiscale flow stability
is one principled candidate criterion; independently optimized resolutions need not
be nested. [Markov stability](https://arxiv.org/abs/0812.1811).

For each view, propose next directions from intersections with these saved regions,
typed facet/assumption selectors, and relevant scientific relations. Where these
provide no useful subdivision, propose a bounded local clustering and record the
objective, resolution, boundary treatment and complete memberships. Compare that
fallback separately; do not initially change every component at once.

Select directions for relevance, useful coverage, distinctness, source support and
stability. An agent reads representative and boundary evidence to name them and
write the actual questions. Inspect omitted witnesses too, so a fluent summary of
the center does not hide an incorrect boundary. Keep questions to investigate
distinct from assertions of an open problem or an established answer.

Preflight each proposed action before displaying it: resolve its target, verify
supporting evidence and retained constraints, and detect empty or unchanged states.
A fluent question without a useful executable target is not a navigation result.
An unchanged region is acceptable for an explicit lens change or return, but must
not appear as a further scientific refinement.

Five is an attention budget, not a physical law. Two good distinctions are preferable
to five arbitrary groups. A valid narrow research question need not be a large,
low-conductance community. A leaf can offer papers, methods or connections without
pretending to have more hierarchical depth.

Each choice has a clear meaning:

| Choice | Scientific operation |
| --- | --- |
| A narrower topic/question | Restrict membership and retain relevant assumptions |
| Derivations, methods, applications, recent work | Change lens/task and follow the appropriate source incidences or filters |
| A related topic or cross-field connection | Explicitly pivot/bridge, potentially outside the current region |
| Broaden | Remove specified restrictions rather than forgetting context indiscriminately |
| Back | Restore the accepted state, rather than reconstructing it from prose |

A true child can use an idempotent intersection, such as
m_child=min(m_parent,h_child). Repeating the same selector then cannot silently
manufacture depth. Recompute relevance from canonical seeds and context. Repeatedly
diffusing the last result is not refinement: heat kernels obey K_s K_t=K_(s+t),
which extends the walk and can spread relevance farther.

### 4. Draw and deliver the accepted organization

Create the text view and optional 2D layout from the same region/action objects.
Camera zoom, grouping resolution, and diffusion locality are three different
controls. Coordinate them intentionally; do not let a camera gesture silently
change the scientific question. Preserve orientation where useful, but source
membership and relationships determine scientific identity, not screen coordinates.

The Q-013 snapshot/recipe carries the accepted state, complete memberships or
versioned references, evidence, action targets and layout. Saved or live transport
does not need to infer these from a hash or recompute language interpretation.
Researcher work markings attach to scientific references and scope, so they can
appear in several views rather than belonging to one pixel or one tree branch.

## What “text and clicks reach the same place” can mean

If both inputs resolve to the same canonical state/action on the same graph version,
require exact agreement. Explicit region references guarantee replay. For independent
free prose, evaluate agreement in scientific scope, assumptions and supporting
evidence; do not promise perfect semantic parsing or identical pixels.

An illustrative route is KK towers → dark-matter applications → tower evolution
and decays. A direct paragraph retaining those scientific restrictions should reach
comparable evidence and useful next questions. “How do they decay?” in that context
should differ from a fresh generic dark-matter question. A mathematically different
approach to the same subject may legitimately present different next directions.

No finite fixed tree can expose every possible combination a researcher can write.
The answer is to let prose create a new region and then make that accepted region
clickable and shareable. The desired equivalence is in the underlying scientific
operation, not a claim that a fixed menu exhausts language.

## What the audit changes about our starting point

The current search and overview are not yet this common construction. Search uses
lexical vector anchors, a small diffusion contribution, top-64 retrieval and five
representative-based groups. Overview uses a separate frozen hierarchy. Clicks in
the search view use source prose and anchors rather than persistent membership.

The upstream atlas is much richer than the browser export, but reviewed cross-paper
relations cover only 120 pairs/160 papers. Its 97 accepted relation outcomes include
50 analogies and 30 method uses, with explicit withholding affecting some outcomes.
This is not a comprehensive graph of established physical implications. We can test
the navigation construction now while retaining these coverage limits.

The all-physics overview will initially have shallower evidence than Swampland.
Connect coarse paper-level regions to detailed source facets by paper incidence and
show coverage depth. Do not let dense Swampland extraction inflate its apparent
share of physics. Coarse affinity H^T W H preserves total one-step flow under the
stated allocation convention, but does not automatically preserve multistep walks;
measure the approximation. Expert input remains optional refinement.

## Smallest experiment that can decide the next implementation

Freeze the 12 source-supported cases in the audit memo before tuning. They include
known KK/axion drift, exact replay and renaming, genuine versus missing children,
and four scientific navigation holdouts with qualified source evidence.

1. Replay the current baseline. Establish shared action/state semantics with identical
   seeds and constraints, separating that change from algorithm changes. Include a
   minimal paragraph-to-state interpreter to test both entry modes; manually supplied
   states can isolate the kernel but cannot establish that paragraph input works.
2. Compare no graph contribution with declared restart propagation, holding input
   states, candidate budget and grouping fixed. Predeclare sensitivity settings;
   compare heat only as a separate alternative at matched locality.
3. On identical scored candidates, compare existing representative grouping, saved
   atlas intersections and recorded local splits. Test the same subsequent follow-up
   from text and click routes, not just initial top-paper overlap.
4. Only then compare stronger paragraph encoders and semantic interpreters. Keep
   source roles, negation and out-of-corpus limitations in the evaluation.

Judge witness recall, scientific scope/constraint violations, useful distinct next
questions, coverage, stability and actual latency/memory. High source overlap alone
does not establish a correct interpretation. Do not use inherited cluster labels as
scientific gold, or tune on all cases and call them held out.

The team checked alternatives including a fixed hierarchy, fresh local clustering,
overlapping communities, diffusion wavelets/coarsening, and summary-tree retrieval.
Those tools address parts of the problem; none alone supplies semantic navigation.
No new corpus-level result is claimed. Root independently reproduced the small
three-node heat calculation in the mathematics memo: outside-parent mass rose from
0.03870453 to 0.09989410 after a second equal diffusion, with semigroup residual
1.11e-16; the linear seed-mixture identity also held to the tested precision.
These synthetic checks establish the stated failure mechanism, not physics quality.

## Evidence and resume

- [Mathematical alternatives, equations, boundary/coarsening caveats and toy code](research/Q-014-mathematics.md).
- [Semantic contract, route equivalence, counterexamples and amendment](research/Q-014-semantics.md).
- [Current data/code audit, twelve cases and controlled comparisons](research/Q-014-audit.md).
- [Integrated vision and progress](../Lab%20Notebook.md); [view delivery](Q-013-agent-browser-design.md).

Next: implement the shared region/action baseline and freeze the evaluation cases
before changing graph weights or embeddings. This research checkpoint changes only
documentation. Q-007 remains paused; no site release, new cluster/model job or
storage activation occurred. Publication remains pending because this checkout also
contains explicitly local-only artifacts; do not push its branch wholesale.

### Q-016 clarification, 2026-11-16: actual query inference is required

The current lexical selection of existing source vectors is a baseline, not a
substitute for encoding an arbitrary paragraph. The semantic prototype must pass
new questions/aspects through a compatible query encoder, with explicit model,
preprocessing and query/document conventions. Corpus vectors are precomputed;
per-query inference handles only new text. Reranking and agent evidence checks
address relationships and conditions that a single similarity score can miss.

The query model may run in a browser, the agent environment or an optional service.
Retrieval can use a different representation from the organization graph through
exact source-ID joins; do not directly compare coordinates from different models.
Q-016 in the notebook records model-size/index arithmetic and the existing Qwen
evaluation's limits. These are design clarifications, not implemented inference
or measured query latency. Q-014's staged comparison should include this real
paragraph entry path from its initial semantic prototype, holding a chosen encoder
fixed while isolating later graph/grouping changes.
