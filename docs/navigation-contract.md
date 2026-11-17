# Navigation contract: native v1.0.0 and prepared v1.1.0

Shared agreement between geometry, protocol and site owners for Q-001. Schemas are in [`schemas/`](../schemas/). Engine computations are deterministic for an immutable corpus and normalized state. All IDs are stable source IDs; screen labels are never identifiers.

## Data and engine

`lib/geometry/index.mjs` exports `loadCorpus(base, {readJson, readBinary}?)` and `createNavigator(corpus)`. The loader defaults to browser fetch; Node supplies filesystem readers. A manifest names hashed JSON metadata and float32 vector shards. Corpus contains `manifest`, `papers`, `units`, `vectors`, `adjacency`. Full encoder, normalization, row alignment and snapshot metadata belong in the manifest. Scientific claims attach to evidence, not vector proximity.

`createNavigator(corpus)` returns synchronous `computeView(state)`, `search(query, options?)`, and `getEvidence(ids)`. Geometry ignores history and searches the global corpus at each step; focus conditions retrieval without locking descendants into an inherited cluster. `computeView` never mutates its input.

## State and result

State: `{schemaVersion:'1.0.0', id, corpusId, computationId, query, focusIds, intent, workRelation, lens, constraints}`. `intent` is `explore|derive|phenomenology|recent|using`; `workRelation` is independently `on|using|either` so recent work **on** and recent work **using** a subject differ. `lens` is `physical_question|method|combined`. Constraints contain `excludeIds`, optional `yearMin`, `yearMax`. Query records the current natural-language question; conversation interpretation is the external agent's responsibility. `computationId` pins the engine version, exact default parameter digest and corpus manifest digest. Both session import and action execution reject a different computation identity; algorithm changes require an engine-version bump. `id` is a deterministic digest of normalized state including this identity, never an invented physics coordinate.

View: `{schemaVersion,corpusId,computationId,stateId,query,nodes,edges,directions,chart,diagnostics,warnings}`. Nodes expose `id,paperId,title,label,x,y,score,residual,sourceUrl,evidence`. Edges expose `source,target,type,weight`. Direction objects expose `id,label,summary,seedIds,query,intent,lens,evidenceIds`, optional `workRelation`, plus `mass,massFraction,sourceCount,withinGroupRms,residual,inSlab` when grouped. Normally five, never more than six choices; low-coverage results may contain fewer. Directions are proposals supported by evidence, not established deductions.

The chart declares method, center, basis, dimension, metric, scale, thickness, explained variance and degeneracy. The selected default fits the five **dynamic direction means** in the original embedding ambient space; these weighted means are not renormalized. `chart.fitScope` names this choice, and `groupDiagnostics` and `sourceDiagnostics` separately report fidelity. Group variance must never be presented as variance retained for all source vectors. Source points are overlays projected into the same plane; within-group spread and source residuals remain visible. Residual means distance from the affine plane in the declared vector space; projection coordinates and group mass are not physical observables or scientific probabilities. Warnings/diagnostics communicate corpus recency, unsupported/empty queries, coverage and geometric failures rather than fabricating results. Engine-specific diagnostic fields may extend the object.

## Session and transitions

`lib/protocol/session.mjs` exports:

- `createSession({corpusId,computationId:navigator.computationId,...initialStateFields})` → `{schemaVersion,corpusId,computationId,states:[state],cursor:0}`.
- `currentState(session)` → the selected state.
- `applyAction(session, action, navigator)` → `{session,view}`; immutable operation.
- `exportSession(session)` → `{schemaVersion,kind:'eigenquestions-session',corpusId,computationId,session}`.
- `importSession(payload,{corpusId,computationId}?)` → validated session; rejects unknown versions, mismatched corpus/computation and executable/non-JSON values.

Action `type` is `navigate|refine|pivot|broaden|select|back|forward|replay|reset`; it may supply `query,focusIds,intent,workRelation,lens,constraints`. `refine` deterministically refreshes focus from the top five current-view nodes before replacing the query, unless explicit `focusIds` are supplied. Refreshing carries the latest context through deeper follow-ups without locking all descendants to the first topic. This stores resolved context in the new state even for a pronoun follow-up from a UI-created query. The external agent should also resolve pronouns into a self-contained query. `select` uses `directionId` from the current recomputed view; stale choices fail. The shared `selectionTarget(session,direction)` predicts its full normalized target. If that exact target already occurs in the active history prefix, native selection replays the earliest matching step instead of appending another copy. Equality compares the complete normalized state, including corpus/computation, query, anchors, intent and constraints, rather than trusting the short state ID alone. Abandoned forward history is not searched. This rule applies only to native `select`; a typed `refine` or an imported history is not silently collapsed. `replay` selects existing `index`. `pivot` clears inherited focus unless supplied; `broaden` clears focus and exclusions unless supplied. `back`, `forward` and `replay` restore exact states. A new appended action after backtracking truncates forward history; an exact selection return only moves the cursor and preserves the existing history. State IDs exclude navigation position, enabling stable replay checks.

## Transport and browser update

The Node CLI and stdio MCP server use the same modules. A local bridge binds only `127.0.0.1`, serves `dist/`, and holds one process-local session. Agent commands act on this bridge; successful mutations emit an SSE event. Browser event data and `GET /api/session` return `{session,view,revision}`. `POST /api/action` accepts an action object and returns that snapshot. JSON never contains code; UI treats text as text.

Snapshots additionally expose `browserStatus`: `acknowledgedCurrent`, `acknowledgingViewers`, `knownViewers`, and `lastRenderedStateId`. After rendering, a browser sends authenticated `POST /api/viewer` with its random tab-scoped `viewerId`, `stateId`, and `revision`. Stale acknowledgements are rejected. This is process-local confirmation of a past render, not proof that a user is still viewing the tab; it is not part of exported/reproducible state. Agent summaries show the first 12 ranked sources and up to 20 edges, with full counts; `navigator_state {full:true}` returns the entire object. MCP never claims that an SSE subscriber alone rendered a view.

Q-002 adds an optional transport precondition for `POST /api/action` and
`POST /api/import`: `If-Match: "REVISION"` (an unquoted nonnegative safe integer
is also accepted). The server parses the JSON body, then compares the revision
before preparing the mutation, and checks the same parent again before committing
after asynchronous shard loading. A stale
revision returns HTTP 409 with `{error:"Revision conflict",current:snapshot}`;
the caller must preserve that newer state and its own draft, report the conflict,
and avoid automatically retrying an old import against the new revision. An
invalid precondition returns HTTP 400 and changes nothing. An absent precondition
preserves explicit legacy unconditional behavior. CLI mutations expose
`--expected-revision N`; MCP `navigator_navigate` and `navigator_import` expose
`expectedRevision`. Both forward the exact captured value through `If-Match`,
including zero. The shared runtime also accepts `{expectedRevision}` for actions
and imports. Strict agents capture it before interpretation, retain their draft
and the returned newer state on conflict, and never automatically restamp.
CLI exits nonzero with a structured conflict; MCP returns `isError` and a compact
current state. Read-only calls are unchanged. CORS permits `If-Match`.
If a UI operation needs an import followed by an action, both requests must be
guarded using the revision returned by the preceding accepted operation. A prior
GET alone is not concurrency protection. Session schemas, engine/data identity
and the numerical computation are unchanged by this transport guard.

Every API request needs the unpredictable session token: `Authorization: Bearer TOKEN` for fetch, or `?token=TOKEN` for EventSource. Tokens stay in URL fragments in browser launch links. The server accepts its exact loopback origin and configured exact public origins, by default `https://eigenquestions.com`; it rejects arbitrary origins and non-loopback Host headers. API clients without Origin still need the token. Requests and bodies are bounded. Static files never expose arbitrary filesystem paths.

Public HTTPS pages may be blocked from loopback by browser private-network/mixed-content permissions. The interface attempts explicit attachment and reports failure; a link to the **same-origin local renderer** is the supported fallback. A network unit test does not establish browser compatibility. Public-origin success/blocking and same-origin browser behavior must be recorded separately in acceptance evidence.

## Q-003 full contextual-view capsule

`lib/protocol/capsule.mjs` is the shared browser/Worker validator and codec.
`schemas/contextual-view.schema.json` describes the JSON envelope; runtime checks
also verify graph references, coordinate types, plane orthogonality and budgets.

```
{schemaVersion:"1.0.0", kind:"eigenquestions-contextual-view",
 builder:{id,version}, context:{question,...explicitScientificContext},
 snapshot:{view,session?},
 continuation:{mode:"native-actions"|"snapshot-only",originStateId,
               description,actions:[{id,label,action}]}}
```

The snapshot is authoritative for display. Import must not discard it and run a
recipe in its place. Existing native view fields remain intact; groups can have
authored labels and overlapping `memberIds`, and typed edges may link sources or
groups. `evidenceIds` distinguish supporting source references from interpretation.
Extra bounded JSON context/provenance is preserved. This is data, never executable
code. Strings render as text and only HTTP(S) links become destinations.

`chart` is optional. `affine-plane` requires finite numeric `center`, two finite
orthonormal `basis` rows (explicit degeneracy allowed), dimension, metric, scale
and thickness. `display-layout` is an author's position layout, not an inferred
embedding plane. Every point in a supplied chart needs finite x/y. The native
centroid engine and its identity remain unchanged; the capsule wrapper adds its
explicit affine type.

Limits are 2 MiB decoded JSON, 512 KiB gzip/stored bytes, depth32, 100,000 visited
JSON values, 500 sources, 50 groups, 5,000 edges, 100 continuation actions and
2,048 projection dimensions. The backend additionally enforces storage budgets.
A valid capsule does not certify its physics or its author: unknown builders are
visibly identified and remain exportable even when numerical continuation is
unavailable. Native recomputation requires supported builder version1.0.0 and
exact computation identity. An author's `native-actions` continuation also needs
that matching canonical session; custom group IDs cannot be resolved by native
`select`. Record explicit query/anchors instead. The engine reads canonical
fields, not arbitrary prose assumptions; continuation is not a claim that richer
context was numerically folded into the current v1 method.

`createCapsule` wraps a native `{session,view}` without recomputation.
`validateCapsule` returns the same object without relabeling or normalization.
`encodeCapsuleBytes`/`decodeCapsuleBytes` use standard gzip streams and preserve
all data. `capsuleCapabilities` separates display, recompute and continue.

The installed `window.eigenquestionsNavigator` controller exposes read-only
`orient` separately from revision-checked committing `apply`/`navigate`.
`orient` uses the existing worker/engine without replacing its canonical session,
UI, history or draft. Full API and transport details are in the
[agent interface](agent-interface.md). Local CLI/MCP transport stays available;
the page object is not an HTTP MCP endpoint.

## Q-005 entry, labels and actual earlier choices

A bare browser URL accepts a neutral empty display object without downloading the
corpus, accepting a saved capsule, or contacting a saved companion. **Resume last
view** and **Reconnect agent** are explicit actions. Opening home or choosing New
path does not replace the last nonempty saved exploration with an empty one.
Malformed saved data remains stored and is described as unreadable; it is not
silently replaced by a different topic. Explicit `#view`, `#focus` and token links
retain precedence over saved state.

`lib/protocol/presentation.mjs` derives bounded display excerpts and representative
source metadata. It does not alter `context.question`, a canonical state query,
source evidence, direction membership, or engine inputs/identity. The complete
authoritative question is retained in the Full question disclosure and exported
capsule; an authored question may differ from its native continuation seed. The
search input is a draft, left blank after an accepted operation unless the user
has edited it during the operation. Native rows identify the representative seed's
actual Method/Question facet and paper title; they do not infer facet kind from
the direction's inherited retrieval lens. Author labels remain author statements.
These are source-based directions, not synthesized semantic topic clusters.

Historical columns retain the actual accepted sibling choices. A separate
compact presentation cache records accepted UI selection/refinement provenance
so a typed follow-up is not falsely marked as a clicked source direction. Known
selected rows show Followed; missing provenance is described as Follow-up. This
metadata never changes scientific state. Step numbers count visible nonempty
scientific steps while internal history indices remain canonical.

A current native choice that would replay an active-prefix state says Return to
step N. Exact authored snapshots at that canonical state use the existing exact
restore path; if only an authored cache reference remains, continuation rejects
and asks for the full file instead of replacing author groups with native groups.
Legacy native histories with duplicate states remain intact and export unchanged;
repeated entries can be labeled as returns for presentation. No claim is made
that different states or sources are semantically novel, or that all scientific
redundancy has been eliminated.

## Q-025 prepared destinations

`lib/geometry/prepared-atlas.mjs` adapts a pinned prepared atlas to the same
`computeView/search/getEvidence` interface. It performs lookup and deterministic
view assembly, not new embedding, clustering, scientific inference or paragraph
interpretation. The native engine, parameters, source rows, hashes and v1 state
normalization remain unchanged.

Prepared states use schema `1.1.0` and add exactly:

```json
{"selector":{"kind":"atlas-destination","atlasId":"ID","atlasVersion":"VERSION","destinationId":"ID"}}
```

Their `query` is the canonical recorded question and their `focusIds` are empty;
complete memberships are referenced through the selector. Original prose belongs
in capsule context. The scientific ID excludes route/history and original prose.
It includes the canonical destination, atlas/computation identity, intent, lens,
work relation and supported constraints. A changed scientific premise requires
the appropriate separately scoped destination, not an unrecorded prose override.

Each manifest pins atlas ID/version, source corpus/content hash, dated scope and a
checksummed catalog. Exact manifest bytes, catalog bytes and adapter-source hash
all enter `computationId`. Catalog arrays keep destinations, source descriptions,
memberships and relations distinct. Destination kind separates questions from
regions, methods and landmarks. Numerical cluster identity is never proof of
question equivalence. Membership records preserve source IDs, weight, role,
source/vector row binding, and year/lens/perspective metadata when filters use it.
Missing metadata for a requested filter fails explicitly. Distinct statuses
describe scientific reading, placement and membership coverage.

`narrower` relations form an acyclic graph with possible multiple parents. If both
parent and child declare complete enumerated membership, the child must be a
subset. A metadata-only broad parent does not make an empty-set containment claim.
Methods, applications, source-local science, reviewed scientific assertions and
geometric affinity retain their own typed relations and qualifications. Incoming
navigation preserves the scientific arrow. Same destination/perspective always
exposes the same incident relations irrespective of path.

The capsule still has schema `1.0.0`; its canonical session/view can be prepared
`1.1.0`. Builder `eigenquestions-prepared-atlas` version `1.0.0` permits the same
recorded `select` continuation when computation identity matches. Views expose up
to fifteen foreground directions (up to twenty for metadata classifications) and full incident relation metadata in
`view.atlas.connections`. Full memberships can exceed the capsule's 500-source
display bound. `membershipCount`, `matchingSourceCount`, membership status and
sample notices state what is represented. Context evidence and matching sources
are labeled separately. Metadata-only vocabulary sources never inflate paper
counts. Full source paging verifies the frozen JSON source/paper shard hashes and
row IDs without loading embedding arrays.

`navigate` with a selector, `select`, `back`, `forward`, `replay`, `reset`, export
and import use the existing shared session transitions. Prepared and native
sessions have distinct pinned computation identities; changing mode explicitly
branches through the same accepted-capsule controller and retains the prior path.
There is no silent reinterpretation of a prepared question as native search.

Prepared URLs pin atlas/version/destination/lens/intent/work relation and require
no upload. Unsupported filtered addresses require the full capsule; the UI clears
a stale prepared address rather than showing it for a differently filtered state.
Opening/reloading a compact URL reconstructs the prepared view. Browser history
retains a local canonical session for Back; the public address omits its path.
Arbitrary authored views continue to require their exact existing capsule.

Local work notes use `eigenquestions-work-note` schema `1.0.0`, a stable note ID,
target selector, text and timestamps. They persist on that browser and export or
import separately. They are excluded from normal view export, copied prepared URLs
and upload. A public destination link is not permission to publish private notes.

Static HTML destination pages and JSON manifests support read-only discovery.
The page controller additionally exposes `lookup`, `describe`, `connections` and
`sources`; these are read-only adapters, not a second state system. The connected
agent must preserve the parent revision captured before interpretation/computation.
A freshly read revision must never be used to launder an older result. Display
acknowledgement and public-to-loopback limitations remain as specified above.

Prepared source associations can carry `associationScope: same_paper_context`, `placementStatus: context_only`, `role: evidence`, `lens: method`, an exact `paperId` and `associationProvenance`. Such rows remain outside primary membership counts and complete-child subset proofs. Method/derive reading and explicit contextual paging may expose them, always with contextual counts and labels; they do not become a primary method membership or USING claim.


Prepared manifest `1.1.0` also supports `catalog.storage: lazy-destinations-v1`.
The initial index contains coarse destinations, exact counts and checksummed detail
locators. A direct fine-ID link loads one hash-prefix lookup bucket; local coarse
navigation loads its recorded fine children. Only explicit global lookup reads the
full fine-search index. `prepareDestination`, `prepareState`, `prepareAction` and
`prepareSources` load and verify required records before the existing synchronous
controller computes a view. Default views use an immutable bounded sample and exact
counts; filtering or paging requires the complete recorded membership. Cache history
must not change a view or state ID. Build validation expands all shards, checks
containment/conservation and requires every static destination page. Missing declared
files fail the build; only an absent optional top-level installed index is allowed.
See the [exact delivery contract](../research/q025/integration/LAZY-DATA-CONTRACT.md).

The installed `/data/atlas/index.json` may set `home` to
`{atlasId,atlasVersion,destinationId}` matching an installed entry destination.
A bare URL then opens that entrance without replacing the last meaningful saved
research path or reconnecting an agent. Explicit view/focus/atlas/token URLs take
precedence. Resume and New path preserve local branches and separately stored notes.
An installation without `home` retains the neutral native entrance.


An optional destination `sourceContributions` array records admitted `addresses`,
`instantiates`, `specializes`, `method`, `boundary` or `comparison` roles. Each row
pins the destination, source unit and frozen rows, reading basis, evidence refs,
review decision and scope hash; admitted qualifications remain unchanged. These
rows do not create membership, a primary placement, equivalence, navigation edges
or USING claims. They stay in the lazy full detail, with only aggregate inventory
metadata in the initial catalog. Browser disclosures read twenty rows at a time,
grouped by paper; static destination pages preserve the complete explicit list.

Typed contributions are also available through the existing source reader: `navigator_sources({destinationId, collection:"contributions", offset:0, limit:20})`, CLI `sources --destination ID --collection contributions`, or browser `sources(selector,{collection:"contributions"})`. Each page returns its exact role, reading basis, qualification, review/evidence references and hydrated excerpt. The default collection remains `membership`; membership filters such as USING cannot be combined with contributions. These reads do not change the session.

### Exact source-object inspection

Prepared states may carry `sourceInspection:{originUnitId,relationId,objectId,unitId}`.
`inspect-source` and `close-source` use the same transition/revision controller.
The canonical physical selector, query, perspective, membership and scientific
identity remain unchanged; the normalized view/history state includes this focus.
Ordinary destination navigation clears it. Back/replay/import restore it only
after the exact versioned source context and endpoint map are prepared.

Optional `manifest.files.sourceMethodRoutes` pins the small exact method-route map.
A route must agree with the reviewed source relation's ID, direction, type, receipt
and both exact endpoints. A selected method must contain that source-node anchor
and reproduce its frozen row/text hash. Missing mappings never use co-paper or
similarity fallback. Unmapped relations remain readable. A mapped route does not
create a destination, home, scientific alias, primary mass or USING applicability.
The source inspection snapshot retains the exact object, source description,
relation conditions and provenance within the bounded capsule; complete context
remains lazily readable. Captured-parent guards apply to all visible inspection
actions, including zero, and to asynchronous source reads before commit.
