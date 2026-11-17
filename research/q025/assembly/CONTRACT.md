# Accepted organization → prepared package

This directory owns the single reproducible assembler. Evaluation owns scientific agreement/admission artifacts; integration owns installation in `data/atlas` and the site. Neither the 186-bin numerical proposal nor a raw reviewer verdict is an accepted atlas.

## Admission packet

The input schema tag is `q025-accepted-atlas/1`:

* `corpus: {corpusId, contentHash}` identifies the frozen navigation corpus.
* `originalCandidate: {candidateId, regionsSha256}` pins all 241 original region records (186 terminal bins). The assembler separately checks every exact member ID and preserves per-bin member hashes and ancestry. These are historical provenance, not a constraint that new regions inherit old boundaries.
* `acceptance: {status: accepted_for_assembly, receipt: {path, sha256}}` references an external admission receipt. That receipt binds `acceptedContentSha256` to the packet with its `acceptance` field omitted. No `usable_with_limits` or `needs_revision` verdict substitutes for this.
* `reviewRegistry` identifies hashed, immutable source-review artifacts. `decisions[].sourceReviewIds` must resolve here.
* `destinations` contain explicit reviewed IDs, kind, title, question, summary, scope, scientific status, reading coverage, representative source-unit IDs, original-bin references and `scopeDecisionId`.
* `placements` name exact `unitId`, `destinationId`, role (`member`, `overlap`, `context`), placement status (`accepted`, `provisional`, `unresolved`), basis and `decisionId`. Nonaccepted placements require a reason and an admitted broad region. They cannot quietly create a canonical question identity.
* `relations` are admitted destination navigation with rationale, source-unit evidence and decision IDs. Their decision must declare `relationUse: public_navigation` and `relationType` equal to the exported type. `narrower` defines containment. Method/application/comparison connections do not imply containment. Source-object scientific relations remain in the independently typed source-context pack.
* `provenanceRelations` retain review-batch links separately: `{id, sourceReviewId, sourceRef, targetRef, proposedType, interpretation: review_batch_provenance, decisionId, evidenceRefs}`. A `provenance_link` decision declares `relationUse: provenance_only` and binds `provenanceRelationContentSha256` using the exported helper. Native `narrows`/`method` spelling is preserved as `proposedType`; it does not become public navigation, containment or geometry. No interpretation is inferred from prose by a regular expression.
* `aliases` require an explicit conflict-free canonical identity group, described below. No merge follows from a shared paper, source ID, factor label or embedding proximity.

Every scope admission binds `scopeContentSha256`. The exported `scopeContentHash` helper hashes `JSON.stringify({kind,title,question,summary,scope,scientificStatus,readingCoverage,evidenceIds})` in that key order, retaining nested object and array order. Evaluation consumes this helper rather than introducing a second convention. A supported-as-written decision cannot survive an unrecorded rewrite. Explicit coordinator adjudication may instead bind the exact new scope through its verified receipt.

## Typed source contributions

`sourceContributions` is a separate table of `{unitId, destinationId, role, basis, evidenceRefs, decisionId, qualification?}`. Roles are `addresses`, `instantiates`, `specializes`, `method`, `boundary` and `comparison`; basis is `description_checked` or `source_excerpt_checked`. Description evidence binds the exact frozen unit/text hash; source evidence binds the unit's paper and exact primary locator. Excerpt basis requires primary evidence. `qualification`, when present, is retained unchanged.

Each row needs an accepted `source_contribution` decision with exact subjects, `scopeContentSha256`, `contributionContentSha256`, `challengerAgreement: independently_agreed`, and `reviewAgreement: {proposalReviewId, challengeReviewId}` resolving to distinct hashed artifacts. `sourceContributionContentHash(row, scopeHash)` hashes the unit, destination, role, basis, evidence refs and scope hash, followed by optional qualification. Use this exported helper rather than duplicating its ordering.

The output adds exact paper/lens/source/browser rows and three explicit nonassertion qualifiers: no direct home, no equivalence, no method applicability. Contributions create no membership, allocation, navigation or USING result, and do not propagate to ancestors. They reside in lazy destination details; the initial catalog has only a count/hash inventory. Scope agreement, contribution role agreement, placement, factor annotations and fine identity remain separate judgments.

## Coverage, ambiguity and methods

Every frozen question must have one or more explicitly supplied direct homes. `allocationPolicy` is either `equal_across_explicit_homes` or `explicit_normalized_weights`; each question's direct organizational weights sum to one. They are not relevance or scientific confidence scores. The assembler invents neither a catch-all region nor a label for an unavailable review.

Containment is a DAG. Ancestor membership is the union of admitted descendant membership; primary child members must be a true subset of primary parent members. Original source IDs, text hashes, lens rows and browser vector rows are verified. All 26,410 source records remain inspectable. Papers without vector-covered units remain explicit inventory records; availability is not inferred.

The admitted method-context policy may associate methods from a region's exact source papers. Such rows have `associationScope: same_paper_context`, `placementStatus: context_only`, `role: evidence`, exact paper/source-question join provenance, and method lens. Runtime excludes these from primary membership, containment proofs and USING results. Method/derive views can inspect them as context. Only explicitly supported associations may become actual use relations. Six deterministic, paper-diverse contextual method examples may appear in `contextSourceIds`; the full associations remain paginated.

## Fine identity is separate from overview cards

Three to eight broad cards per reviewed bin are navigation summaries, not a resolution cap. Evaluation is adding compact per-unit fine identity states: a proposed own-unit singleton, unresolved identity, or a named group. Named groups carry representative source, short reviewed title/reason and defining differences; members derive from exact row assignments. A group becomes an agreed equivalence only through its separate accepted identity decision.

The assembler must preserve fine source/question access and those identity dispositions without copying complete source conditions into each card. Exact source records and the lazy source context are reused. Fine questions need not all appear in the global chart; region-level geometry and deeper text navigation can coexist. `fine-identities.mjs` consumes the frozen compact packet/reply mapping. It checks every exact description, text hash, paper and source-unit ID, preserves proposed singleton/unresolved/group states, and does not merge candidate groups.

Optional `identityResolution` contains a pinned authoritative comparison `registry: {path, sha256}`, `records: [{id, contentSha256}]`, `comparisons`, and explicit `canonicalGroups`. The registry file's complete records/comparisons must exactly match the supplied tables. Each comparison has `{id, operation, members, target, definingDifferences, sourceReviewIds, evidenceRefs}`. Operations mirror canonical review: `same_scoped_question`, `common_target`, `specializes`, `shared_parent_distinct`, `method_bridge`, `comparison`, `different`, `unresolved`.

Positive pair components are computed only to detect conflicts. They never create a canonical group. If A=B and B=C conflict with A≠C, specialization, unresolved identity or changed defining premises, the component enters `unresolvedConflicts`; any attempted group touching it is rejected. Common-target grouping does not enter equivalence components. Overlapping explicit canonical groups are rejected rather than joined transitively.

A canonical group `{id, destinationId, memberIds, decisionId}` must bind one already admitted question scope. Its independent whole-group `question_equivalence` decision names every exact member and canonical destination, declares unchanged scoped equivalence, and binds `scopeContentSha256`, `identityInventorySha256` and `identityGroupContentSha256`. Use `identityInventoryHash` and `canonicalIdentityGroupHash` from `fine-identities.mjs`. Distinct proposal/challenge artifacts are required. A changed/new canonical scope needs its own ordinary scope admission. Alias rows name `identityGroupId` and `sourceRecordId` in addition to destination, alias and the group decision ID. These are reusable scoped-question identities; exact source-statement equivalence is not asserted. Historical conflicts cannot be silently removed from a supplied inventory; a newly adjudicated inventory must receive its own pinned assembly admission.

## Geometry and delivery

`geometry-input.json` records Q-only direct allocations, exact source rows/text hashes, per-paper source mass, accepted containment and explicitly chosen base regions. Context membership rows do not enter those Q-only allocations. The pinned retrieval operator retains the proposal-basis mixture (0.5 MiniLM question, 0.3 Qwen question, 0.2 same-paper method-context affinity), explicitly as retrieval geometry. Typed scientific assertions remain separately navigable and available for semantic validation.

The planned coarse flow is `C = Hᵀ F H`, where `H` allocates each question across its explicit base-region homes. `F` is a reversible flow on the pinned multiview retrieval graph with stationary mass `m_i = 1 / questions_in_paper(i)`: for symmetric off-diagonal affinity `W`, use `F_ij = W_ij min(m_i/d_i, m_j/d_j)` and put remaining mass on the diagonal. This Metropolis correction conserves exactly one unit of source mass per represented paper, including isolated sources. It does not make paper counts scientific truth.

Layout is computed only after resulting accepted memberships exist, with graph/membership hashes, component information and measured two-dimensional distortion. Ancestors share the same chart through membership-based centroids; no arbitrary position defines membership, science or identity. Distortion is reported separately for computational atom positions and the actual displayed region centroids. Parents spanning disconnected components are flagged because their screen centroid inherits nonmetric display packing. The separately pinned all-physics classification chart remains a different coordinate space.

The prepared output is validated using the shared `validateAtlas`, `loadAtlas` and `createAtlasNavigator` interfaces. Source-context assets remain versioned references with an installation plan, avoiding a second copy of the 190 MB pack inside every assembly experiment. Integration performs the one final public-data installation.

## Executable checks and QA preview

`node --test research/q025/assembly/accepted.test.mjs` exercises conservation, overlapping mass, source balancing, meaningful unresolved-family retention, source/context semantics, admission integrity, unreviewed aliases, cycle rejection and scientific-layer separation using explicitly synthetic fixtures.

`preview.mjs` packages the existing four unchanged draft cards with the frozen 211-node classification chart and explicit hep-th portal. Its v2 method-context variant has five unchanged primary memberships plus thirteen contextual method associations. Both packages are visibly provisional, have no invented detailed geometry, and are not accepted release data. `handoff.json` records exact source and package hashes for browser QA.


## Lazy transport and full-scale proof

`lazy-package.mjs` is a representation of the same complete logical atlas. The compiler first checks admission, exact source coverage and containment, then calls shared `validateAtlas` on the full logical package. It serializes bounded shared detail/membership files and verifies an exact round trip of every membership and navigation relation. A checksummed `partition-validation.json` records the result; no transport step changes scientific membership or graph geometry.

The manifest uses schema `1.1.0`; the initial catalog has `storage: lazy-destinations-v1`, a `detailShards` dictionary, bounded destination indexes, and zero source/membership rows. Each index has exact primary/context/paper/connection counts and `detail: {shardId}`. Lossless `indexTemplates` eliminate repeated fields; absent question text means the identical full title. A full detail contains the reviewed destination, at most 30 primary and 6 contextual membership examples, representative source records, a complete membership descriptor, and all incident fine-question links. Materialized `memberIds` live in the complete membership file, with their hash retained in detail coverage.

Fine source-question indexes and source-access links are deferred. `fineIndex` loads for explicit global search; `fineLookup` partitions exact `source-question:<64-hex>` IDs by their first two hash characters for direct URLs. A prepared known family obtains local fine neighbors from its own detail, so ordinary deep navigation does not download the global fine index. Complete selected memberships load before filtering or paging. The default sample and pinned counts stay independent of cache history.

`delivery-assets.json` enumerates every generated lazy asset and external context asset with a hash and byte count. The manifest pins that inventory. The build fails above 25 MiB per file or a projected 20,000 assets including one static page per destination and a 500-file ordinary-site reserve. Installation still belongs to integration.

The frozen diagnostic at `outputs/full-scale-delivery-fixture` uses the actual 26,410 source records, original 186-leaf/55-parent proposal, a clearly unaccepted all-source parent, all 8,473 exact source-question destinations and the pinned classification chart. It is not scientific acceptance. `full-scale-delivery-manifest.json` pins its files; `lazy-scale-diagnostic.json` records 783,784 initial index bytes, a 2,390-byte entrance detail, 48,264-byte maximum direct fine lookup, 580,281-byte maximum detail and 15,029,623-byte maximum complete-membership file. Exact checks pass for 171,694 membership rows, 8,928 destinations and 8,946 relations. The file-count envelope including 1,488 possible later cards and the ordinary-site reserve is 18,167. Final accepted memberships, scopes and file counts must be rechecked; unavailable reviewed cards are not fabricated in this probe.

The targeted command is `node --test research/q025/assembly/*.test.mjs`. It includes typed contribution, provenance/navigation and transitive identity-conflict checks. The full-size diagnostic is reproduced with `node research/q025/assembly/profile-lazy.mjs --write-fixture`, followed by `node research/q025/assembly/freeze-delivery-fixture.mjs`. Do not overwrite the frozen QA fixture during an active browser run.
