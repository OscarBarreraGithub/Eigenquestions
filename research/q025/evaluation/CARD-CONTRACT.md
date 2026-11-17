# Q-025 scientific cards and identity

This is the evaluation contract for the shared catalog proposed by integration. It is not a second engine or a claim that the existing 8,473 question descriptions are canonical questions.

## Catalog records

Keep `destinations`, `sources`, `memberships`, and `relations` separate. A destination has `id`, `kind: question|region`, `title`, `question`, `scope`, `aliases`, `provenance`, and evidence references. Memberships carry exact destination/unit IDs and organizational weights. A source-scoped extraction node remains immutable; a canonical question may collect several of these nodes without merging their provenance.

For a **question**, `scope` states the physical system, target being asked about, defining hypotheses, regime, and relevant convention choices. These are semantic identity fields. Include `includes`, `excludes`, and `assumptions`; add `regimes` and `conventions` where material. A **region** explains a family of questions and their differences; it does not pretend all members ask one question. Its complete memberships or exact frozen selector must be available even when the browser displays samples.

The readable card should answer, in order:

1. **What is being asked?** One clear question and two or three sentences about why the distinction matters.
2. **What can I do next?** Between one and fifteen meaningful visible directions, with extra connections accessible through explicit groupings. Each direction names its actual operation: narrower question, method, application, comparison, or neighboring evidence. A leaf may stop rather than invent children.
3. **How is it studied?** The method and the quantities it computes, not a list of keywords. Link method sources separately from the result they are used to establish.
4. **Under what conditions?** Hypotheses, approximation/control regime, conventions and exclusions needed to understand the statement.
5. **What supports this page?** Sources with exact unit/node/evidence IDs, paper identifiers, relevant pages/locators, dated coverage and reading limits. Distinguish representative, boundary and omitted evidence.
6. **What remains unsettled?** Separate placement status, scientific relation status, extraction/review coverage, and question-identity status. None is a scalar scientific confidence score.

Do not make every card equally long. The core question and scope should be readable immediately; derivations, premise lists, convention dictionaries, full memberships and audit lineage can be expanded. A source link alone is insufficient when the card makes a qualified claim but hides its qualification.

## Relation types and direction

| Layer | Suitable types | What it licenses |
| --- | --- | --- |
| Organization/navigation | `narrows`, `member_of`, `method_for`, `application_of`, `related_question` | An authored navigation proposal with source rationale. `narrows` must actually restrict the parent's scientific scope. |
| Retrieval | `text_affinity`, `same_paper_incidence`, `literal_identifier_mention` | A way to discover evidence. It does not establish dependence or truth. |
| Source-local science | Existing `assumes`, `derived_from`, `supports`, etc. | What an extraction attributes within that source and its recorded reading scope; not independent validation. |
| Reviewed cross-paper science | `uses_method`, `specializes`, `supports_under_assumptions`, `same_result_under_dictionary`, `analogy_only`, `apparent_tension` | Exactly the current reviewed assertion, direction, premises, conventions and limitations from `current-relation-ledger.json`. |

A method/application connection is not containment. An accepted analogy is not an implication. An accepted same-result dictionary does not merge source objects or certify the entire papers. `supports_under_assumptions` needs its conjunction of premises; do not convert it to an unqualified arrow. No generic `implies` export is justified by renaming all admitted edges.

Browsing may follow an incoming edge. Its scientific arrow remains unchanged, and the inverse navigation label must read accordingly (for example “method used by”). The same atlas, canonical question and explicit perspective have the same shared adjacency irrespective of entry route. Breadcrumb history may help interpret “they,” but it cannot remove cross-field exits.

## Concrete identity decisions

**Merge as aliases, not duplicated destinations.** J01's two prompts asking for linear cosmological signatures of repeated intra-tower KK-graviton decays should identify one question under the simplified nonrelativistic Dark Dimension setting of 2311.05318. The destination is unchanged when approached from extra dimensions or cosmology. The source question is `unit:be7aae21bb2419d0869faff0e2d1c1e653b0e8e75d40ce2e657fb8fb7495284a`. Its primary evidence includes `ev:bbf52e208ce8497a6b71719219ba7d85` (p1), `ev:2fad585ea0fd6a9e881beb23831ceaa7` (p5), and `ev:2493ceddf3c0cd5eec29592d377901eb` (p6). This is an author-drafted alias decision to challenge, not an automatically certified corpus merge.

**Split a shared physical setting by target.** The initial production/abundance question in 2209.09249 (`unit:d5031ab16d8b871bddd917aa4e9de3e7203c9cda1499e4fcfe9a5f463cd4a4ac`) and the linear-signature question in 2311.05318 share KK dark matter. They should remain distinct linked questions. A broad “KK dark matter cosmology” region may contain both. Their relationship is not established merely by a high embedding cosine; source passages establish the production/evolution distinction.

**Split inclusive geometry from strict kinematics.** Inclusive convex-hull coverage and strict positive-mass-release decay are different questions. Current `pilot-wgc-convex-hull-reduction/context-1.json` admits method use only. A spectrum saturating extremality can satisfy an inclusive comparison while failing strict decay. Retain the matching extremality coordinates, particle spectrum and integer charge conditions; the original context's deferred status is historical, not the current result.

**Do not merge via a shared word or paper.** Three 1812.09714 units ask about torus/brane spectrum, one-loop vacuum-energy stability, and orientifold-compatible brane positions. The same source and overlapping vocabulary do not establish identical targets. In particular, the metric-entry/inverse-entry question differs from whether the one-loop Wilson-line Hessian is non-tachyonic.

**Split a changed regime; keep a changed perspective.** Adding massless scalar forces can materially change the extremality/repulsion comparison of 1509.06374 and 1906.02206. It is not merely an alternative visual lens. In contrast, viewing the same defined comparison through a method lens changes emphasis without changing its ID. The dossier remains promotion-withheld.

**Specialization is not equivalence.** The accepted relation between 1911.12640 and 2009.03347 is restricted to linear bosonic round-AdS5×S5 fluctuations with identity scalar dressing. Do not merge these papers' entire KK algorithms, scopes or destination identities. Preserve the coordinator's exact scope note.

## Changes and expert input

An accepted equivalent formulation becomes an alias. A later merge records redirects from prior destination IDs while keeping their old snapshots. A split records the earlier scope and explicit successor choices; do not redirect an ambiguous old ID arbitrarily to one child. Source IDs never change as a side effect of organization. Experts can correct any of these decisions; their absence does not block autonomous drafting and challenge.
