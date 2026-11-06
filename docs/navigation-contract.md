# Navigation contract v1.0.0

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

Action `type` is `navigate|refine|pivot|broaden|select|back|forward|replay|reset`; it may supply `query,focusIds,intent,workRelation,lens,constraints`. `refine` deterministically refreshes focus from the top five current-view nodes before replacing the query, unless explicit `focusIds` are supplied. Refreshing carries the latest context through deeper follow-ups without locking all descendants to the first topic. This stores resolved context in the new state even for a pronoun follow-up from a UI-created query. The external agent should also resolve pronouns into a self-contained query. `select` uses `directionId` from the current recomputed view; stale choices fail. `replay` selects existing `index`. `pivot` clears inherited focus unless supplied; `broaden` clears focus and exclusions unless supplied. `back`, `forward` and `replay` restore exact states. A new action after backtracking truncates forward history. State IDs exclude navigation position, enabling stable replay checks.

## Transport and browser update

The Node CLI and stdio MCP server use the same modules. A local bridge binds only `127.0.0.1`, serves `dist/`, and holds one process-local session. Agent commands act on this bridge; successful mutations emit an SSE event. Browser event data and `GET /api/session` return `{session,view,revision}`. `POST /api/action` accepts an action object and returns that snapshot. JSON never contains code; UI treats text as text.

Snapshots additionally expose `browserStatus`: `acknowledgedCurrent`, `acknowledgingViewers`, `knownViewers`, and `lastRenderedStateId`. After rendering, a browser sends authenticated `POST /api/viewer` with its random tab-scoped `viewerId`, `stateId`, and `revision`. Stale acknowledgements are rejected. This is process-local confirmation of a past render, not proof that a user is still viewing the tab; it is not part of exported/reproducible state. Agent summaries show the first 12 ranked sources and up to 20 edges, with full counts; `navigator_state {full:true}` returns the entire object. MCP never claims that an SSE subscriber alone rendered a view.

Every API request needs the unpredictable session token: `Authorization: Bearer TOKEN` for fetch, or `?token=TOKEN` for EventSource. Tokens stay in URL fragments in browser launch links. The server accepts its exact loopback origin and configured exact public origins, by default `https://eigenquestions.com`; it rejects arbitrary origins and non-loopback Host headers. API clients without Origin still need the token. Requests and bodies are bounded. Static files never expose arbitrary filesystem paths.

Public HTTPS pages may be blocked from loopback by browser private-network/mixed-content permissions. The interface attempts explicit attachment and reports failure; a link to the **same-origin local renderer** is the supported fallback. A network unit test does not establish browser compatibility. Public-origin success/blocking and same-origin browser behavior must be recorded separately in acceptance evidence.
