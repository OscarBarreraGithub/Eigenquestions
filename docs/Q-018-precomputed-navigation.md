# Q-018 — Agent navigation through a precomputed scientific atlas

2026-11-17. `/root`. Design recommendation following the owner's proposed
simplification; no new hierarchy, agent runtime or browser release is implemented.

## Decision and change in priority

Make agent-assisted navigation through a deeply prepared atlas the primary v1 path.
Compute the scientific organization ahead of time. A connected agent interprets a
paragraph, inspects existing region descriptions and selects stable destinations,
lenses and related regions. The browser displays a deterministic view of that state.

This materially changes Q-017's proposed first pilot: first demonstrate navigation
through a strong precomputed structure and a compact reproducible URL. On-demand
embedding, reranking and newly computed regions become optional escalation paths.
Heavy batch construction remains valuable and benefits all viewers.

Q-016 remains correct for *vector retrieval*: an actual new query vector requires a
compatible encoder. Agent routing need not perform vector retrieval at all. An LLM
can read a menu of well-described child/related regions, choose IDs and check their
evidence using ordinary tools. Its own model inference still occurs in the user's
agent; the static site need not host that inference. Unconnected browser search must
continue to distinguish name matching from agent interpretation.

## Two operations with different purposes

**Q-024 clarification, 2026-11-17:** The owner's O(5) means roughly 1–15 visible
directions, not five communities or a fixed branching factor. References below
to about five describe the earlier shorthand. Scientific groups and depth must
follow the existing geometry, source evidence and tested distinctions; the
interface count is not a clustering objective. The current runtime's five-direction
setting is unchanged by this design clarification.

**Offline construction:** encode source-linked questions, results, methods and other
facets; use affinities, typed relations and existing candidate hierarchies to propose
regions and neighbors. Agents read representative, boundary and omitted evidence,
define scope and useful subdivisions, and review confusing distinctions. Preserve
memberships and graph versions. Reviewers can improve the structure later, but human
curation is not required to produce the first complete navigable release.

**Online routing:** retain the user's complete question, inspect region descriptions,
follow a few plausible routes, check the candidate destinations and select an
appropriate scope/depth. Read more than just a child title. Backtrack or jump using
search when early choices are wrong; do not force all routes from a single root or
greedily discard relevant alternatives. About five displayed directions and roughly
ten decisions are design targets, not guarantees for every research question.

The existing graph is not yet a sufficiently deep atlas: the reviewed overview has
six children in its QG branch while other major branches stop, with specific stability
or size-gate reasons. Alternatives have deeper numerical trees but different
memberships and unreviewed labels. [Saved hierarchy audit](Q-007-hierarchy-audit.md).
New offline organizational work is needed; enabling buttons alone cannot supply it.

## What every navigable region needs

Use a small shared record rather than a new ontology service:

- Stable ID and version, a concise title, and a clear scientific scope.
- What belongs here, important distinctions/exclusions, and source-backed examples.
- Complete recorded membership or an exact versioned selector; displayed samples
  remain samples.
- Useful narrower regions and their differences, plus separately typed methods,
  applications and cross-topic connections.
- Representative evidence, unresolved coverage/placement, and provenance of reviews.

A containment hierarchy can have multiple parents: a region may be reachable through
KK physics, cosmology and quantum-gravity constraints. Keep genuine containment
acyclic and keep cross-links separately typed. A method lens, an application and a
logical implication are not automatically parent/child relations. This preserves
context-dependent routes and apparent depth without precomputing a separate tree
for every possible question.

Aim for a clear primary region plus related regions where appropriate. A finite
taxonomy cannot give every possible paragraph a unique exact leaf. A conjunction of
known regions and supported filters may be represented by a compact composed state.
If the question exceeds the stored structure, show the nearest useful regions and
the gap; optionally request heavy analysis. The underlying scientific graph and
sources remain richer than the navigation menus.

## SwampWiki's role

Root previously read all files at `cda0fd3af9c800555a9679e98476452e05ebe183` and
rechecked the repository's main SHA on 2026-11-17; it is unchanged. It contains 19
named claim nodes and 24 typed scientific relations, with statements, references,
editorial grades and rationales. [Source nodes](https://github.com/sr-744/swampwiki/blob/cda0fd3af9c800555a9679e98476452e05ebe183/swampwiki/data/conjectures.json)
and [relations](https://github.com/sr-744/swampwiki/blob/cda0fd3af9c800555a9679e98476452e05ebe183/swampwiki/data/relations.json).

Its names can serve as useful landmarks in the Swampland portion of the atlas.
Connect each to detailed source regions covering its formulations, evidence,
methods, assumptions, challenges and applications where the literature supports
those distinctions. They need not all appear as five fixed headings at every node.
Q-015's citation/premise findings must be resolved before those records are treated
as verified anchors. Grades remain attributed editorial judgments.

SwampWiki's scientific relationship graph supplies part of the scientific story.
The precomputed atlas adds a navigational organization and detailed evidence beneath
and across those landmarks. Preserve both meanings; do not convert an `implies` edge
into a category relation or assume a proposed claim map is the only valid taxonomy.
The general method should discover useful landmarks in other fields too.

An illustrative destination is KK-tower dark matter / cosmological evolution and
decays. It could be reached from extra dimensions, dark matter, or Dark Dimension.
Stable destination IDs allow these routes to converge. Retained scientific filters
or intent can still make different evidence relevant at the same destination.

## When a short URL is sufficient

When the browser already has or can load the versioned atlas, a URL can identify
the destination, lens, supported filters and optionally a path. The final destination
can be even shorter than encoding every decision. Illustrative syntax only:

    /#atlas=swamp-v2&region=kk-dm-decays&lens=methods&via=kk,dm

No such new route is implemented. IDs resolve to precomputed membership, labels,
neighbors and layouts; the URL is a structured address, not a compressed embedding
matrix or executable program. Deterministic view selection supplies the same result
for a manual click and an agent-generated state on the same atlas version.

Every condition that changes the view must be encoded or referenced. A short URL
does not preserve arbitrary unpublished annotations or all the meaning of a long
question. Preserve original prose in the agent conversation or a saved artifact;
use Q-013's stored-view mechanism for novel memberships, long context or authored
scientific objects that cannot be reconstructed from the static atlas. That mechanism
becomes optional for ordinary precomputed views.

Pin atlas versions and retain old snapshots/ID redirects so a shared link does not
silently change meaning. A URL can reproduce a view, but it does not automatically
notify another open tab. Existing browser-control/apply paths can navigate to it;
optional paired delivery remains a separate capability. Applying a late result still
needs to respect the user's current state. No public write API is needed to produce
the ordinary compact navigation URL.

## Next bounded implementation

1. Build one sufficiently deep, overlapping navigation neighborhood from actual
   sources, using SwampWiki's relevant named landmarks and autonomous candidate
   regions. Define evidence-backed cards, narrower choices and cross-links; preserve
   uncertain placement and meaningful stopping points.
2. Give an agent only the navigational interface and unseen long questions. Test
   whether it reaches the right scope/depth, retains constraints, recognizes gaps and
   supports the next follow-up. Compare with manual selection and alternative routes.
3. Encode accepted states in small versioned URLs; test reload, Back, shared opening,
   equal destination through different routes and context preservation. No per-query
   reclustering or embedding service is required for this first path.
4. Expand the atlas and solicit expert corrections of wording, boundaries, omissions
   and scientific relations. Keep repeatable source tests for changes. Introduce
   heavy query-time tools only where routing failures demonstrate a need.

This is a priority amendment to Q-014/Q-017, not a claim that the earlier dynamic
construction was impossible. It preserves the broader shared physics atlas,
optional human refinement, detailed evidence, researcher markings and agent/browser
interoperability while making ordinary navigation cheaper and easier to reproduce.

## Q-020 correction, 2026-11-17: a unique destination with contextual surroundings

The owner clarified that a unique destination is a requirement. The earlier advice
to settle for a primary region or a small related set was too weak. A unique
scientific destination is compatible with multiple parents, several approach paths
and different surrounding questions. Root had conflated unique location with unique
classification ancestry.

Separate two objects:

    destination = canonical scientific question, including defining scope
    view = display(destination, navigation context, atlas version)

Each accepted question has one stable identifier. Equivalent formulations and
different routes should resolve to that same identifier. A navigation context selects
which neighboring questions, prerequisite explanations, methods or supporting
literature to foreground. It does not change the destination's meaning or invent new
scientific relations. If an assumption materially changes the scientific question,
that belongs in the destination's defining scope and may require a distinct linked
question. A purely presentational perspective belongs in the view.

For example, the illustrative question “How does a decaying KK tower evolve as dark
matter?” can have one destination reached through KK physics or dark matter. The
first route can foreground spectra/couplings and the second abundance/observational
questions. Those are examples of navigation context, not new validated relation
edges or claims that existing code implements them.

At Swampland scale, canonicalizing the represented literature's questions is a
reasonable concrete research/engineering target. The current export contains 8,473
question descriptions covering 6,477 papers; they are input candidates, not 8,473
already distinct or complete canonical questions. Cluster/retrieve candidates, inspect
their source scopes, merge genuine paraphrases, retain meaningful variants and build
typed links between canonical records. SwampWiki supplies broad landmarks, while
the question catalog supplies finer destinations. Expert edits can correct merges,
splits and relations with versioned redirects and preserved prior snapshots.

Assigning an ID or choosing a nearest centroid is not evidence of semantic correctness.
Validate equivalence using paraphrases and independent routes, and validate distinction
using changed hypotheses, targets and regimes. Unresolved interpretation can remain
an internal provisional state; the accepted navigation result should identify one
destination. A genuinely new question can later receive an explicit scoped record
instead of being silently conflated with an unrelated known question. This does not
require precomputing every conceivable question before a useful first release.

The next pilot should therefore test roughly 20–30 canonical destinations with
alternative routes and contrastive/paraphrased prompts, in addition to reading quality.
Require the same destination ID for equivalent accepted questions; permit different
neighborhoods only when their recorded context differs. A small URL carries the
destination plus context and atlas version. No implementation or corpus-level
canonicalization has been completed by this correction.

## Q-021 clarification, 2026-11-17: routes never fence off connections

The owner requires navigation from extra dimensions into dark-matter cosmology
regardless of the approach path. Each canonical destination has one shared set of
recorded scientific connections. Context may emphasize a subset, but it must not
remove valid connections or confine navigation to descendants of the entry branch.

Use a common default neighborhood for the same resolved question and perspective.
History helps interpret an incomplete follow-up and supplies breadcrumbs; it does
not independently redefine adjacency. Explicit perspective changes may reorder or
group choices. The roughly-five-choice interface must still expose the remaining
connections through clear groupings or further choices, including cross-field exits.

Test extra dimensions -> KK towers -> KK dark matter -> cosmological evolution and
observational questions without returning to the root, and access the shared
destination's connections after entering through cosmology. These are proposed
navigation tests, not implemented or source-validated new edges. Navigation can
inspect incoming as well as outgoing scientific relations while retaining their
actual direction; browsing backward must not imply a converse theorem.

Q-020's contextual-neighborhood wording concerns presentation of the shared graph,
not different scientific graphs for different approach paths. No new runtime or
atlas data is changed by this clarification.
