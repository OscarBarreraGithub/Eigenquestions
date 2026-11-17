# Q-025 semantic assembly audit — 17 November 2026

Four reproducible findings remain in the inspected checkpoint. No production code, scientific admission, frozen payload, notebook, Git state or public deployment was changed by this audit. Audit artifacts are confined to this directory.

The 23 files in `research/q025/assembly/semantic-checkpoint-v1.json` matched every pinned SHA-256 and byte count. The existing assembly suite passed all 40 tests on Node v26.7.0. The runtime file used by the integration probe, `lib/geometry/prepared-atlas.mjs`, had SHA-256 `6b8be2aef476a544e0336bfcdedd57664367c11ec0032df5a5555c6156fff545`. The working branch was `agent/atlas-integration-q025`; HEAD when recorded was `bfbb7d68539aa9a21b85c8d86ecadb115b8086a7` with concurrent owner changes present.

Run from the repository root:

```sh
node research/q025/audit/semantic-v1/probes.mjs
node --test research/q025/assembly/*.test.mjs
```

The original observed outputs are preserved in [probe-results.json](probe-results.json) and [assembly-tests.txt](assembly-tests.txt). The probe script prints observations; it does not treat the observed incorrect acceptances as passing assertions. Rerunning after a repair should change those observations.

## 1. Canonical groups can introduce an unchecked transitive contradiction

**High priority before canonical identity admission.** `fine-identities.mjs:19–34` computes positive components only from inventory comparisons. At `fine-identities.mjs:41`, the proposed canonical group is checked for direct constraints among its members and for conflicts already present in those earlier components. Its own equalities never participate in that consistency check.

The `inheritedConstraint` probe supplies an inventory with `A same_scoped_question B` and `B different C`, where the latter records a changed physical regime. It then supplies a separately bound whole-group decision declaring `{A,C}` equivalent at one admitted question destination. Assembly accepts the group, publishes both aliases and reports `unresolvedConflicts: []`. The accepted group closes the path `B=A=C`, violating the retained `B≠C` constraint.

The group decision has the exact current inventory hash, group hash and scope hash, every required subject, `equivalent_as_scoped`, unchanged premises, and distinct proposal/challenge review IDs and hashes. This is not a stale-hash mutation or an automatic union from pair comparisons. The consistency gate needs to evaluate canonical group equalities together with existing positive paths and negative/specialization/premise constraints, while retaining the rule that positive paths alone do not create groups.

## 2. Disjoint groups can merge known specializations through one destination

**High priority before canonical identity admission.** `fine-identities.mjs:40` prevents repeated member IDs across groups but does not prevent separate groups from binding the same canonical destination. Constraint checking remains local to each group.

The `distinctGroupsSameCanonicalDestination` probe records `A specializes C` with the defining difference “C assumes an extra controlled limit.” It submits exact whole-group decisions for `{A,B}` and `{C,D}`, both targeting `destination:fine`. Assembly accepts both and exports `Alias A`, `Alias B`, `Alias C` and `Alias D` on that single canonical question, without a conflict. Thus a known specialization is lost through shared canonical-target identity, even though no membership overlaps between the input groups.

One final whole-group decision per canonical destination would make the combined member set and its constraints reviewable. Any alternative must still check the full equality implied by sharing that destination. Neither this case nor finding 1 requires merging source statements; both violate the narrower reusable scoped-question identity claim itself.

## 3. A claimed primary excerpt needs no exact primary locator

**Medium priority before contribution admission.** `accepted.mjs:70` treats any truthy `ref.id` on a primary reference with the matching paper ID as sufficient source evidence.

The `primaryEvidenceWithoutExactLocator` probe submits a `source_excerpt_checked` contribution whose entire evidence reference is:

```json
{"kind":"primary","paperId":"p2","id":"not-a-locator"}
```

Assembly accepts it as an `accepted_typed_contribution`. There is no source hash, text hash, context file, page/offset or resolved registry locator. Its exact contribution hash and distinct review-artifact hashes do not supply the missing locator. The shared runtime validator also does not resolve primary evidence references, and `runAssembly` pins the context manifest without checking these contribution references against its contents.

The contract promises the unit's paper and an exact primary locator. Require a supported locator representation and verify its exact target against pinned source context, or resolve a reference ID through a verified evidence registry before admitting excerpt basis. This audit did not test scientific relevance of any real excerpt; it demonstrated absence of the promised machine-checkable locator.

## 4. A question supported only by contributions fails lazy navigation

**High priority for integration of the new contribution semantics.** `lazy-package.mjs:63` and `:70` omit the complete membership descriptor when a destination has zero membership rows. The lazy runtime at `lib/geometry/prepared-atlas.mjs:287` permits that omission only for metadata destinations.

The `contributionOnlyQuestion` probe keeps every frozen synthetic Q in an explicit broad home, gives an admitted question one correctly bound description-based comparison contribution, and leaves that question with zero memberships. Its scope, evidence, contribution, containment and decisions remain explicit. Assembly succeeds; shared `validateAtlas` succeeds; `validatePartition` reports an exact successful round trip; all Q allocation errors are zero. Preparing that destination through the shared lazy navigator then fails with:

```text
Prepared atlas: nonmetadata destination lacks complete membership descriptor
```

This is a natural outcome of the contract's separation of contribution, scope and direct home. The transport/runtime must represent a pinned complete empty membership. Adding a membership merely to avoid the failure would incorrectly promote a typed contribution into a home or geometric allocation. The probe did not require a browser: it exercised the same shared `createAtlasNavigator.prepareDestination` boundary used by browser and agent navigation.

## Admission assumptions and limits

The identity and evidence probes use the existing explicitly synthetic fixture and `assembleAccepted`'s `fixture: true` mode. That mode skips the external top-level receipt/inventory verification, not the identity, source, review-agreement, scope, contribution or allocation checks described above. Each disputed component is internally hash-bound as required, with distinct synthetic review hashes. These are inconsistent or insufficiently evidenced *input admissions accepted by the semantic gate*, not a demonstration that an attacker can alter a previously signed packet unnoticed. The production CLI verifies immutable receipt and review bytes plus the complete supplied comparison inventory. It does not add another semantic consistency or primary-locator validation step. A real packet would still need an exact top-level assembly admission receipt before reaching these gates; no such packet was created or admitted here.

The contribution-only runtime probe uses actual assembler output, shared logical validation, actual lazy partitioning and partition validation, and the real shared navigator with an in-memory shard reader. It does not invoke the full production CLI, install an atlas, load public assets or establish browser rendering behavior. The shared runtime had concurrent owner modifications and is identified above by hash.

The audit read `AGENTS.md`, the notebook's current state and latest entries, the Q-025 delivery plan, the frozen assembly implementation/contracts/tests and the parent component/compatibility artifacts. The parent fragment's nine public direction candidates, six provenance-only records and the explicit statistical comparison correction remain distinct; no raw parent link inventory was treated as admitted navigation. The frozen suite and code inspection support that typed contributions do not supply allocations/USING, provenance links do not create containment, explicit Q homes conserve mass in the covered overlapping fixture, and proposed source singletons are not promoted to canonical uniqueness. No additional failure in those boundaries was reproduced.

No sealed holdout, private source packet, browser, cluster, model call, complete growing scientific registry, accepted full scientific atlas or public site was inspected. No claim about the scientific correctness of the real review decisions or final geometry follows from this bounded audit.
