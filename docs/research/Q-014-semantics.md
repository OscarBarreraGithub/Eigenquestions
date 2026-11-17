# Q-014: One scientific state for text and click navigation

Author: /root/navigation_semantics. Date: 2026-11-16.
Status: research recommendation; no new navigation code, model run or evaluation.

## Main finding

Text and clicks should compile to the same **scientific region/state**, then invoke
the same region-construction and view-generation operators. A 2D coordinate, topic
label or paragraph embedding is not sufficient state. The useful meaning of “same
place” is comparable evidence and scientific scope; the nearby questions, chosen
lens and screen arrangement may differ with the research task.

There are two different guarantees:

1. **Exact reference resolution:** a clicked topic or explicit reference to a known
   region resolves its recorded identity, membership and construction state exactly.
2. **Semantic retrieval:** an arbitrary paragraph locates an approximately matching
   region. Agreement across paraphrases and routes is measurable, not guaranteed
   by a hash or clustering algorithm.

A short summary is a lossy description of a region. Generally, no inverse from
that summary back to the original membership exists. Preserve the region reference
behind a clickable label rather than searching again for the label's words.

## What exists and what it does not yet supply

The current [navigation contract](../navigation-contract.md) already pins data and
engine identities, distinguishes focus from global search, and supports exact
replay. The [geometry implementation](../geometry.md) retrieves lexical anchors,
mixes their real source vectors, adds three diffusion steps, selects 64 facets,
and groups them around five diversified representative facets. A clicked direction
is currently represented by a source-derived query and anchors. There is no general
logical/negation parser; arbitrary capsule context is not consumed by the math.

These choices explain why changing diffusion alone cannot deliver the requested
paragraph/click consistency. The existing machinery is a useful baseline, not a
complete semantic state or general generator of progressively narrower topics.

## Proposed state and operations

Let G_v be the pinned heterogeneous graph and U its source-linked scientific units.
Use a state C containing:

- Resolved subject(s), target question/result, and requested method or application,
  with their roles kept distinct.
- Explicit assumptions/regimes, positive requirements, exclusions and unresolved
  clauses; distinguish user stipulation from source-supported fact.
- Task/lens: derive, compare, test, applications, recent work, work on X or using X.
- A selected **focus region** rho over U, explicit anchors and their roles.
- Resolution, graph/metric/operator versions and a concise resolved context.

This is an internal representation of meaning, not a form the human must fill in.
The agent proposes it from text and exposes a readable interpretation for correction.
Ambiguous parses remain separate candidate interpretations; averaging them can
create a region corresponding to neither interpretation.

The common pipeline is

    text or clicked action → resolved context delta → region → local options → view.

Once the interpretation is accepted, deterministic code uses the pinned graph and
parameters. Model-generated descriptions are recorded outputs, not assumed to be
reproducible by rerunning the model. The path is provenance; its scientifically
relevant commitments must be explicit in C rather than buried in a transcript.

Keep two related supports: the selected focus/core and a discovery neighborhood
around it. A strict refinement can retain its exact selected core while its next
view reveals related material outside the old display. A new related source does
not silently become a member of the narrower topic merely because it was retrieved.

Each clickable option carries a typed action, not just prose:

| Action | Meaning |
| --- | --- |
| Locate a known region | Resolve its pinned region identity; optionally change viewpoint. |
| Refine within this region | Add a stated distinction/constraint and select a supported subregion. |
| Follow a relation / contextual pivot | Pursue a method, implication or application; support may expand outside the parent. |
| Change lens | Preserve the scientific subject/scope while changing how it is organized. |
| Broaden | Explicitly relax selected constraints or widen the region; do not erase unrelated commitments. |
| Back / restore | Restore the exact accepted state and view, not a fresh semantic guess. |

A strict subregion with soft membership a_j(i) can select a core proportional to
rho(i) a_j(i). This elementary operation is a design candidate, not a calibrated
posterior. After selecting it, the discovery operator can search the wider graph.
A contextual pivot is a different operator and must not be disguised as ancestry.

## Why a paragraph cannot be reduced to one seed mixture

For a fixed linear diffusion H, the identity

    H[lambda s_A + (1-lambda)s_B] = lambda Hs_A + (1-lambda)Hs_B

shows that mixing seeds superposes neighborhoods. It does not express conjunction,
exclusion, role direction or a requirement for evidence linking A to B. “Find A
and B,” “find A without B,” and “use A to study B” therefore need distinguishable
operators or evidence filters. A single similarity score can rank an A-only hit
above a weaker but genuinely joint A-and-B hit.

Use clause/facet retrieval to nominate candidate evidence, typed graph relations
to propose connections, and source checks/reranking to establish that a candidate
matches the requested role and conditions. A missing annotation is **unknown**, not
proof that a condition is absent. Excluding papers that merely mention a forbidden
assumption would also discard papers explicitly avoiding or challenging it.

This is a mathematical/semantic design argument, not evidence that a particular
compiler or reranker succeeds on physics. Relevant empirical findings motivate
the design: ASPIRE models scientific similarity through sentence-level aspects;
SciRepEval finds task-format-specific representations can outperform a single
representation; NevIR exposes failures on negation. These studies do not certify
our physics representations or select a current best encoder. [ASPIRE](https://arxiv.org/abs/2111.08366),
[SciRepEval](https://aclanthology.org/2023.emnlp-main.338/),
[NevIR](https://aclanthology.org/2024.eacl-long.139/).

## Populating the next view without making a fixed taxonomy

Use persistent multiscale communities as reusable landmarks and candidate regions,
then construct a small context-dependent cover of the selected neighborhood.
Overlaps and boundary connections remain explicit. A paragraph may specify a
region cutting across all the existing landmarks; it must not be forced into the
nearest pre-existing leaf. No finite fixed tree represents every conjunction of
subject, method, assumption and purpose.

Offer approximately five supported next actions, potentially drawn from two kinds:
actual finer scientific groupings and useful scientific questions/perspectives.
Label their action type. “Applications” is usually a lens/pivot; it is not evidence
of a nested community. “What fails without supersymmetry?” is a question to
investigate, not a claim that a theorem fails or that its answer is already known.

For each candidate, keep the target region/action, contrasting sibling scope,
representative evidence, boundary cases, and an indication of unsupported cases.
Generate a concise title and explanation from those materials; independently
challenge the title against held-out members and neighboring nonmembers. Reject
or qualify misleading descriptions. Summarizing a community is useful but does
not validate its boundaries or infer all cross-paper relations. GraphRAG provides
evidence for community summaries in global sensemaking, not proof of reversible
navigation or physically meaningful clusters. [GraphRAG](https://arxiv.org/abs/2404.16130).

Stop refinement when it no longer reveals stable, distinguishable, evidence-backed
choices. Show the sources, unresolved questions or lateral connections instead of
manufacturing another level. A well-supported narrow topic can be deeper than a
metadata-only branch; displayed depth is relative to this exploration.

## What to test before claiming that both routes work

**Exact tests.** A known region reached from two links has the same pinned focus
and scope. Back/export/import restore the accepted object. Rewording a display
label does not change the target action. Pure declarative filters A then B and B
then A commute when their final scope is identical and neither action adds path
commitments. Graph/version changes require explicit migration or a frozen replay.

**Semantic tests.** Compare independently written paragraph queries and click
journeys by scope agreement and weighted evidence overlap, not pixel positions.
For normalized focus weights p and q on shared source identities, report weighted
Jaccard sum(min(p,q))/sum(max(p,q)), plus constraint-violation rate, missing-scope
rate, evidence quality and next-action usefulness. High overlap alone can conceal
the same generic but wrong answer. Do not choose a success threshold after seeing
the favorite examples.

**Contrastive tests.** Hold the topic words fixed while changing a method's role,
negation, assumption or task. Results must respond appropriately rather than merely
remain stable. Distinguish a fresh standalone query from a follow-up: the same
words may legitimately resolve differently under different explicit context.

**Descriptions are tested one-way.** The recorded region must support its summary.
A separately parsed free-text summary should retrieve comparable evidence where
it retains sufficient information, but exact recovery is required only for the
explicit region reference, not arbitrary abbreviated prose.

Suggested held-out journeys (test prompts, not new scientific conclusions):

- Axions → instanton effects → constraints on multi-axion field ranges; compare
  with a paragraph preserving the multi-field scope and a contrastive single-field
  version. Add “using instanton calculus” versus “studying instanton solutions.”
- AdS compactifications → scale separation → KK spectral gaps; compare the
  curvature-based route with the spectral-method route. The final subject may
  coincide while evidence roles and next questions differ.
- Black-hole extremality → weak gravity → scalar forces; compare fixed-charge
  extremality with pairwise repulsion. Require explicit treatment of which
  assumptions distinguish the questions rather than merging shared vocabulary.
- Vacuum constructions → de Sitter → control of corrections; contrast “assuming
  supersymmetry” with “without assuming supersymmetry,” retaining unknown cases.
- Broad physics → photonics → topological transport; test honest metadata-level
  coverage and a bridge to condensed matter rather than fabricated deep detail.

## Smallest informative experiment

Freeze the existing graph and choose 8–12 tasks spanning those families. Compare:
(A) current engine; (B) paragraph embedding/seed diffusion alone; (C) explicit
role/constraint state plus diffusion, shared click actions and evidence checks.
Use independently authored direct paragraphs, paraphrases, click paths and
contrastive variants. Predeclare scope tests and sample representative/boundary
evidence. Evaluate two seed/resolution perturbations and a graph-version update.
Only add a stronger encoder in a second comparison so semantic-state improvements
are not confounded with model replacement. Existing static communities can supply
landmarks without waiting for human curation.

The target is a source-grounded, inspectable navigation operator whose entry
methods agree where their meanings agree. Universal semantic equivalence, a
unique physics geometry, and unlimited faithful depth remain unsupported claims.

## Amendment after team comparison: membership, relevance and minimum scope

The synthesis from /root/navigation_mathematics correctly separates raw region
membership m(i) in [0,1] from normalized retrieval importance p(i). This supersedes
the earlier illustrative use of normalized rho times a_j as the semantic definition
of refinement: repeated selection could otherwise sharpen weights merely because
the same choice was clicked twice. Store a deduplicated set of restrictions and
region references. An idempotent membership rule such as min(m_parent,h_child) is
a candidate; compute retrieval importance separately from canonical seeds and
context. Do not repeatedly diffuse the previous relevance distribution as if it
were an unchanged semantic region.

The proposed shared state, multiscale landmarks, local covers and post-selection
layout fit both entry methods provided a paragraph can create a new region crossing
the landmark cover. Landmark IDs must not become the compiler's only vocabulary.
Exact state resolution applies to explicit region references; natural-language
clause interpretation remains approximate and may produce competing hypotheses.

Three unresolved choices matter more than adding further architecture: (1) what
typed predicates/roles the current extraction can actually support, (2) how source
evidence distinguishes satisfied, contradicted and unknown constraints, and (3)
when a local cover merits five useful choices rather than fewer choices plus a
coverage warning. The first prototype needs a small inspectable clause vocabulary,
region references and evidence checks, not a universal formal ontology of physics.
Evaluate novel cross-topic regions, route agreement and contrastive failures before
adding further operators. The group labels remain summaries of recorded evidence;
neither their existence nor a coherent-looking 2D layout validates the construction.
