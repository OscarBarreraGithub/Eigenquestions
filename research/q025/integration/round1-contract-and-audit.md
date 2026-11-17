# Q-025 integration: first contract and runtime audit

2026-11-17. Owner: `/root/atlas_product_integration`. Baseline runtime:
`origin/main` `40cf90b`; the copied Q-010–Q-024 research is design evidence, not
implemented behavior. Proposal for root/sibling review. No runtime edits,
deployment, publication or account operations in this round.

## Decision proposed

Add a prepared destination selector to the existing versioned session/action
contract. Resolve it through a small prepared-atlas adapter, render the resulting
view through the existing accepted-capsule controller, and use the same history,
file, page API and local CLI/MCP transports. Keep the native numerical engine and
its current corpus/identity valid for old sessions. Do not encode atlas identity
in a free-text query, infer destination identity from drawing coordinates, or
create a separate browser state machine.

Prepared atlas records describe accepted science. Numerical candidate regions
remain distinct artifacts with a `definitionStatus: numerical_candidate` until
source review accepts their scope. A canonical question can belong to several
regions and retain one question ID. A containment region need not itself claim
to be a canonical scientific question.

## Minimal common data agreement

**Manifest.** `schemaVersion`, `kind: eigenquestions-atlas`, immutable `atlasId`
and `version`, `corpusId`, corpus manifest/content hashes, dated scope/limitations,
construction/review provenance, and checksummed file references for destinations,
memberships, relations, evidence summaries and optional chart assets. Exact source
unit IDs and vector row bindings stay unchanged. Atlas construction can consume
the existing graph and latent vectors without requiring a newly trained encoder.

**Destination.** `id`, `kind: question|region|method|landmark`, `title`, `question`,
`scope: {assumptions, includes, excludes, regimes, conventions}`, `summary`,
`whyItMatters`, `aliases`, `evidenceIds`, exact versioned membership reference,
`methods`, `scientificStatus`, `placementStatus`, `readingLimit`, and `provenance`.
Required fields may be empty when not claimed; omission must not fabricate a
review. Question IDs are scoped scientific identities. Candidate membership-hash
region IDs are not substitutes for canonical question IDs.

**Membership.** Exact rows `{destinationId, unitId, weight, role}`. Preserve
`sourceRow`, lens, and `browserVectorRow` when exported from numerical construction.
Weights are membership/relevance conventions, never probabilities of truth.
Representative evidence is a sample and must not silently stand in for complete
membership. Large memberships may be sharded; ordinary page loads need only small
summary/evidence records.

**Relation.** `{id, source, target, type, evidenceIds, rationale, status,
assumptions?, provenance}`. Keep `narrower`, `uses_method`, `application`,
`related_question`, and explicit scientific `implies|supports|tension|…` distinct.
Geometric affinity is separately typed and not a scientific assertion. Containment
is acyclic and may have several parents. Browsing an incoming relation does not
reverse its scientific direction. Every destination exposes all admitted incident
relations irrespective of approach path; a default ordered list may foreground
roughly 1–15 choices, with the rest accessible. A leaf may have no narrower choice.

**Chart.** Optional, independently declared `display-layout` or computed
`affine-plane` with pinned inputs/method and appropriate diagnostics. Plot proximity
does not create adjacency. Shared chart coordinates aid orientation; scientific
relations and graph/vector distance retain their separate meanings. Existing
capsule geometry validation already supports these two chart meanings.

**Work note.** Local/exportable bounded JSON with note ID, atlas/version,
destination IDs and/or source/relationship IDs, text, optional source URLs, and
created/modified timestamps. It is not embedded in ordinary public prepared URLs
or automatically uploaded with a view. Share the public destination address;
export/import the note separately. Any later public note publish must be explicit.

## State/action agreement to freeze before implementation

Candidate field: `selector: {kind: 'atlas-destination', atlasId, atlasVersion,
destinationId}` in the next session schema. Preserve the exact old v1 normalizer
and replay behavior for v1 sessions. Prepared state uses the canonical question in
`query`; the original paragraph belongs in local capsule context, not the canonical
ID. `intent`, `workRelation`, `lens`, and supported constraints remain explicit.
Unknown/unsupported restrictions fail or are explicitly reported, not ignored.

The concrete schema version and dispatch signature need root agreement. The
preferred implementation is a backwards-compatible extension of
`lib/protocol/session.mjs` with a prepared adapter sharing `computeView`, `search`
and `getEvidence`; no second action/history implementation. The adapter's identity
pins atlas assets and its rendering/default-neighborhood algorithm. Native
`computationId` remains unchanged. Prepared and native transitions must state
which computation is active; there is no silent recomputation of authored views.

`navigate` accepts an explicit selector; `select` resolves a recorded current
direction to the exact target selector; `back`, `forward`, `replay`, `reset`
retain their existing semantics. Native exploratory search is still available.
Atlas name matching is labeled lookup, not paragraph understanding. A connected
agent reads scope and evidence before accepting a mapping. An unmatched or
assumption-incompatible question yields a gap or explicit alternate proposal.

Prepared address candidate:
`/#atlas=VERSIONED_ATLAS_ID&destination=ID&lens=physical_question&intent=explore`.
All scientific/display restrictions are encoded or version-pinned. Path is
optional presentation metadata and cannot change canonical identity or adjacency.
Ordinary addresses require no upload. New arbitrary memberships, authored groups,
long context and scientific annotations continue to use the exact existing
contextual-view capsule. Old atlas snapshots/IDs must remain resolvable; missing
versions produce an honest unavailable-version result, never today's substitute.

One destination/perspective has one default neighborhood regardless of path.
`current path` means the actual accepted history; `new path` starts neutral and
keeps the last nonempty saved exploration; browser Back and in-app Back must be
tested separately. Original paragraph and the resolved canonical destination are
both inspectable. Private text must not leak through a copied address.

## What already works in this checkout

| Existing component | Verified implementation and bounded significance |
|---|---|
| Frozen corpus | `data/navigation/manifest.json` pins 26,410 question/method units, 6,478 papers, 384-dimensional MiniLM, hash/alignment provenance, source metadata and retrieval affinities. No new corpus work is prerequisite. |
| Shared transitions | `lib/protocol/session.mjs` validates fields and identity, implements immutable history, exact active-prefix selection replay, stale direction rejection, Back/forward/replay and native export/import. It currently rejects any destination/atlas field. |
| Numerical engine | `lib/geometry/index.mjs` is shared by browser worker and local runtime; no new query encoder. Its dynamic source direction groups are not the prepared atlas. |
| Accepted browser object | `web/app.js` has one `activeCapsule` and `window.eigenquestionsNavigator` with `ready/read/orient/evidence/apply/navigate/export/publish/subscribe`. Read-only orientation does not commit; apply/navigate check UI revisions. |
| Exact views | Shared capsule validator supports unknown builders, overlapping authored groups, explicit continuation, optional plane/layout geometry and bounded JSON/gzip. Manual file picker/drop, view export, session export, `#view`, `#focus` exist. |
| History/UI | Neutral home, explicit resume/reconnect, New path, accepted sibling choice columns, actual followed markers, exact authored-cache restoration and draft preservation already exist. Text sources precede optional geometry. |
| Local connected agent | `bin/navigate.mjs`, stdio MCP, runtime and loopback bridge share the engine/session. SSE delivers committed revisions; browser sends state/revision acknowledgement after rendering. Same-origin local browser is the established route. |
| Public discovery | `web/llms.txt`, agent docs, portable skill, schemas, manifest and shards are static readable assets. The no-JS page currently offers no useful browsable topic catalog. |
| Storage | `backend/views.mjs`, `budget.mjs`, `budget-object.mjs` already implement bounded exact public/unlisted save/read, byte retry identity, durable reservation, immutable R2 semantics and honest unavailable results. Historical 503 is not a fresh account test. |

## Concrete gaps and repairs

1. No runtime canonical catalog, prepared selector, deep accepted graph, source-backed
   region descriptions, compact atlas URL or equivalent manual/agent destinations.
   Native `query` participates in state identity and is not semantic normalization.
2. The independent fixed overview explicitly has no controller or storage. Its
   strict map format models one parent per topic and `text_similarity` links. It
   cannot be treated as today's shared scientific graph. Add prepared destination
   links and a declared common selection contract without falsifying its chart.
3. Native views normally expose five choices. Prepared menus should use actual
   admitted distinctions and roughly 1–15 foreground choices; do not change native
   numerical settings or pretend old group diagnostics validate new menus.
4. No work statements attached to stable referents, local note import/export, or
   cross-route recovery. Build local first. Shared destination URL is distinct
   from publicly publishing unpublished notes.
5. No hosted live pairing/relay exists. Existing page controller or same-origin
   companion can demonstrably update the browser now; immutable link alone cannot.
   Hosted relay is a later coherent wave/root-owned backend decision, not a reason
   to block prepared URLs. Public-to-loopback behavior requires real browser QA.
6. Skill step 5 currently says to reread revision immediately before applying.
   Correct this: capture parent revision before computation and keep it; do not
   restamp a stale result with a new revision. On conflict preserve draft/proposal.
7. Static discovery needs small HTML/Markdown destination descriptions and index,
   stable direct data links, exact selectors and clear scope/gaps so read-only
   agents can orient without downloading tens of MiB or installing tools.
8. Coarse all-physics entrance is not present. Add a separately labeled overview
   entrance with honest detailed-vs-metadata-only coverage, then source metadata
   in the later construction wave. Do not label Swampland a complete physics map.

## Bounded integrated waves and ownership proposal

**Wave A — contract and scientific material.** Root freezes schema/ownership;
geometry supplies candidate regions/membership/diagnostics under its research
folder; evaluation supplies independent journeys and current admitted relation
ledger; root/evaluation accept destination definitions. Integration prepares
validator and native-compatible selector adapter, with strict legacy fixtures.

**Wave B — one complete prepared journey.** Integration owns new
`lib/protocol/atlas.mjs` (or agreed equivalent), session/capsule/runtime/worker
adaptation, page controller/rendering, compact routes, static discovery and local
CLI/MCP adapter extensions. Scientific atlas content/build inputs remain owned
by root/geometry/evaluation, with a single deterministic product export into an
agreed `data/atlas/VERSION/` tree. Add contract/schema docs only after root assigns
those paths. Runtime edits begin only after agreement.

**Wave C — whole-product completion.** Integrate separate overview entry and
common destination links, source/method/assumption reading, local note export and
cross-route recovery, polished quiet text-first UI, and full browser acceptance.
Root owns hosted storage activation, any live hosted session work, deployment,
notebook, commits and push. No secrets or private work in product builds.

## Initial acceptance cases

- Old native session/capsule fixtures reproduce unchanged; frozen source hashes,
  row mapping and old overview artifacts stay intact.
- Exact atlas selector and all its paraphrase acceptances lead to one destination
  ID; changed defining assumptions yield a distinct destination or explicit gap.
  Consume evaluation's `journeys.json` without choosing expected answers from
  whichever numerical candidate wins.
- Extra dimensions → KK towers → KK dark matter → evolution/decays → observational
  questions proceeds without root reset when source-supported. Cosmology approach
  reaches the same target and same default incident relation set.
- Narrower/method/application/tension relation labels and direction are honest;
  geometric proximity creates no unsupported relation. All admitted cross-links
  remain accessible beyond foreground menu limits.
- Manual selection, direct prepared URL, static-agent-selected ID, page API and
  connected local MCP/CLI action produce the same prepared destination/view key.
- Current path, New path, in-app Back, browser Back, reload, shared opening and
  replay restore accepted destination/perspective; stale action leaves newer state.
- Render acknowledgement confirms a real connected browser change. A read-only
  agent is never reported as connected; a URL alone never counts as delivery.
- Source excerpts, provenance, assumptions, methods and dated recent/on/using
  semantics remain inspectable. Unsupported detail says why it is unsupported.
- Local work note attaches to canonical IDs, is recoverable via both routes,
  exports/imports, and never appears in a copied public prepared URL or upload by
  default. Arbitrary authored capsule still round-trips exactly.
- Prepared startup avoids loading native vector corpus; text and controls remain
  responsive. Coarse physics entrance clearly distinguishes scope and coverage.

## First verification result

`npm test` invoked on Node `v26.7.0` with no runtime edits. Backend test immediately
reported missing package `miniflare`; other suites were still running when this
draft was written. No dependency install or full baseline success is claimed.
Final test output will be recorded separately. Browser behavior has not been
retested in this round.
