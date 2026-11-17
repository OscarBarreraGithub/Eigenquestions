# Canonical questions as part of card construction

The 8,473 exported physical-question descriptions contain **zero exact duplicate
groups**, even after Unicode normalization, case folding and whitespace collapse.
Exact-text deduplication therefore performs no scientific merge in this corpus.
This does not imply all 8,473 questions are distinct; nor does high affinity prove
that two questions are equivalent.

The useful unit of construction is a readable, scoped scientific question card.
For example, “How do repeated decays in a KK-graviton dark-matter tower affect linear
cosmological perturbations?” can collect sources that calculate its mechanism,
instantiate a regime, or constrain its consequences. Those papers need not make
equivalent full statements. Source records remain distinct, and the card records
how each source contributes. A broad question can have several narrower questions
without calling them aliases of one another.

## Membership and identity are different decisions

Use separate contribution roles:

- `addresses`: a source directly investigates the defined question, possibly giving a partial answer.
- `instantiates`: a source investigates a specified example/model within the card's scope.
- `specializes`: a source or narrower question adds defining conditions; preserve its own scoped identity.
- `method`: a technique useful for the question, without claiming the technique asks the same question.
- `boundary` or `comparison`: evidence that helps explain the scope but is not a positive member.
- `alias_equivalent`: two **question formulations**, under a matched scope dictionary, denote the same target. This alone warrants identity merging; it does not merge scientific source objects.

These are navigation/contribution judgments unless an exact reviewed scientific
relation independently supports a stronger statement. Do not reuse the name
`specializes` to silently promote a navigation inclusion into a validated theorem.
Keep the layer explicit.

A card's scope signature records system/objects, target/observable, quantifiers,
defining hypotheses, control regime, and material convention choices. A method is
part of identity when the question specifically asks about that method; otherwise
it is usually a linked lens. A change of route never changes the signature. A
change from initial abundance to late-time linear signatures does. A changed
normalization can be a dictionary only if it preserves the asserted physics;
inclusive versus strict inequalities cannot be erased by relabeling.

## Conservative automatic operations

Automatically deduplicate repeated **representations of the exact same source
object**, pinned by source hash, extraction bundle/window and JSON pointer; retain
all retrieval facets and provenance. Normalize whitespace/punctuation for discovery
aliases only. A verified, literal existing destination ID resolves exactly. The same
accepted scope with a presentation-only lens change reuses the destination.

Do not automatically merge different source objects because their text, vectors,
paper ID, cluster or graph neighborhood matches. There are no exact text groups to
exploit here anyway. Source-local `addresses` links and reviewed method relations
can support contribution roles, but are not equivalence decisions.

## A bounded next construction, not an all-pairs service

After the current pilot, take six scientifically useful families (the two reviewed
families plus four selected ordinary-exploration families). Draft **two question
cards per family**, twelve cards total. Use existing source descriptions and richer
linked claims/assumptions/regimes to define what each asks. Generate candidate
support from the full question/method graph and embeddings; include relevant sources
outside the parent region. Inspect four central/supporting sources and two contrast
sources per card. Overlap is permitted.

For each card select at most **three consequential identity comparisons**: a very
close paraphrase candidate, a high-affinity changed-target/regime candidate, and a
source that contributes without being equivalent. This gives up to 36 explicit
identity/contribution decisions, not hundreds of thousands of pair reviews.
Frozen neighbor rankings nominate these candidates; they are not truth labels.
Record one positive alias pair written independently from the scope and one changed
hypothesis prompt. If no genuine merge is supported, keep the question records
separate and explain why.

The remaining proposed eighteen native requests can be used as six packets of two
cards each, with proposal, separate challenge and unused-source check. This combines
scientific organization, question definitions, source contribution roles and identity
checks in the same reading work. Root should decide this allocation after the
six-request pilot; no additional batch is launched here. The reserved final 24-paper
set remains untouched until selection is frozen.

Accept a question definition and its identity only when the source-backed scope and
consequential distinctions survive challenge. Save the exact support/contrast
memberships and all uncertainty. The rest of the corpus remains accessible as
source-described material and numerical neighborhoods; it must not be advertised
as an already canonical list of scientific questions. This permits useful accepted
questions immediately without claiming that every input description has been
normalized.

## Serving and corrections

A router can return one accepted question ID when the paragraph fits its scope. It
can return a broader accepted question only if it explicitly states the retained
scope and does not pretend the finer request has been answered. Unmatched or
underspecified requests keep a visible scope gap; they must not silently resolve
to a different known question. A source/question candidate may still be inspected
without being represented as an established canonical destination.

Alias merges preserve old IDs as versioned redirects and preserve each source's
identity. Splits preserve the old scope and offer explicit successor choices rather
than choose an arbitrary child. An accepted canonical question can occur in many
regions and be reached through many directions, but has one shared set of recorded
connections. Stable IDs and deterministic URLs establish address consistency;
source review and paraphrase/contrast tests establish whether the address means the
right question.

## Why extra scientific facets matter

`rich-context-joins.json` gives exact keys into all 281,128 objects, 296,130 retrieval
facets and 400,435 structural/source-local edges. Only 2,408 question units have an
incident noncontainment relation. Direct question-attached assumptions occur for
2,354 units, conventions for 1,679, regimes for 302 and derivations for 61. Thus a
missing direct edge is not evidence the paper lacks a premise or method; look at
shared extraction-window context, then same-paper material, retaining those weaker
attachment meanings. Do not apply every paper assumption to every question.

The geometry agent additionally reports zero exact question-unit endpoint matches
among the 97 reviewed cross-paper relations. Its prior relation-aware geometry
therefore used paper-context projection. That may nominate useful cross-links, but
it does not transfer the reviewed assertion to every question in either paper.
This distinction must remain visible in card construction and in the scientific
relation inspector.
