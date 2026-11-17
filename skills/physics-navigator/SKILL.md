---
name: physics-navigator
description: Use Eigenquestions for source-linked physics orientation and shared browser/agent navigation. Resolve installed scoped destinations first; native query exploration and authored capsules are explicit alternatives. Supplement the atlas with independent research.
---

# Physics navigator

Use the atlas to orient independent research, not to limit which questions or
outside sources you consider. For background, make read-only queries; do not move
the human's path unless a visible update is part of the request. Read the
[interface reference](references/interface.md) for exact calls and capabilities.

## Navigate the prepared atlas

1. Read the current browser object with `window.eigenquestionsNavigator.read()`,
   or use `navigator_state` / CLI `state`. Inspect the selector, question, history,
   corpus date and warnings. Capture the browser parent revision **before**
   interpretation or computation. Bare home opens the installed all-physics
   entrance; saved paths and companion reconnection are explicit choices.
2. Resolve the user's intended scoped destination. Use browser `lookup`,
   `describe` and `connections`; with MCP use `navigator_search`,
   `navigator_connections` and the linked static destination record for its full
   scope. `/atlas/index.html` and `/data/atlas/index.json` support discovery without
   installing tools. Lookup matches titles and aliases only: the agent interprets
   prose and checks premises, regime, conventions and intent. A changed defining
   assumption may require another record. Similar embeddings or shared region
   membership do not establish canonical question equivalence.
   Break prose into the physical system, target or mechanism, and defining regime.
   If the first search finds only broad orientation, try one bounded second search
   emphasizing the specific target rather than repeating model names.
   Inspect the full scope and distinguish a canonical question from a source-specific facet.
3. Inspect paginated `sources`, exact paper links and reading limits before using
   a claim. Request `collection:"contributions"` through the same source reader
   for reviewed method, boundary, comparison and other typed contributions. These
   roles are separate from membership, equivalence and USING; retain their
   qualifications. A question can have contributions and zero primary members.
   `context` returns bounded pages of source objects, relations, evidence locators
   or assessments (default 20 objects). Read applicable withheld reader notes.
   Exact incidence and same-paper context do not establish universal premises or
   applicability; absence from a page or filter does not establish absence in
   physics. Extracted descriptions are not guaranteed verbatim quotations.
   On a relations page, `sourceRoutes` lists only exact mapped source endpoints.
   To inspect one visibly, submit its returned `inspect-source` action with the
   captured revision. The physics destination stays fixed; source inspection
   creates no home, equivalence or USING claim. Preserve the recorded direction
   and conditions even when inspecting the source endpoint. Unmapped endpoints
   remain readable without a follow action. `close-source` returns to the question;
   Back/replay and a full capsule preserve the inspection history.
4. For an authorized visible update, use `navigate({type:'navigate',selector})`
   or `select` with a current direction ID. Use `back` / `replay` to revisit a path.
   Every visible mutation, including import, must supply the parent revision captured
   before interpretation: browser `{expectedRevision: parent.revision}`, MCP
   `expectedRevision: parent.revision`, or CLI `--expected-revision N`. Zero is valid.
   Never restamp an old proposal with a newly read revision. Preserve the proposal
   and newer state on conflict, then reconsider the request against that state.
   Legacy callers may omit the guard, but this skill requires it.
   The same accepted destination ID is shared across
   paraphrases and entry paths; do not duplicate it merely to fit the conversation.
5. Verify `read().renderedRevision === read().revision` after browser acceptance.
   The local companion instead reports `browserStatus.acknowledgedCurrent` for
   the exact state/revision. A computation or JSON response alone does not prove
   that a browser displayed it. Explain useful next choices in the user's terms,
   normally about 1–15 scientific directions; classifications may expose more.
   Check all recorded connections, not only the route used to arrive here.

Keep source claims, agent interpretation and unanswered questions distinct, with
stable citations. Broad metadata-only fields describe a classification vocabulary,
not detailed paper coverage. A displayed sample is not complete membership. Graph
position, similarity and same-paper associations are discovery aids, not proofs of
equivalence, causation or consistency. Clarify only when ambiguity materially
changes the scientific scope; otherwise state a reasonable assumption and inspect
it through read-only calls.

## Available interfaces

- **Browser execution:** use the installed `window.eigenquestionsNavigator` when
  the browser tool permits page JavaScript. `orient(query,{selector})` is read-only;
  `navigate` or `apply` commits to that page. No repository, companion or skill
  installation is required. A page object does not grant missing tool permissions.
- **HTTP only:** read static destination pages, manifests, source references and
  saved capsule bytes. Supply a compact prepared link for an installed destination;
  it needs no upload. HTTP reading cannot update another person's open browser.
- **Local companion:** use Node22 CLI or stdio MCP with an existing checkout and
  the selected atlas (`serve --atlas data/atlas/ID/VERSION`). Locate it from user
  context or `EIGENQUESTIONS_DIR`; the copied skill installs neither data nor tools.
  Open the connection link and keep the companion running for visible updates.

A public HTTPS page may require ordinary permission to contact apps on the device.
If connection is unavailable, use the same-origin local link printed by `serve`
or a compact prepared URL. Do not disable security or claim a CORS header proves
connectivity. Keep session tokens out of exports, reports and public links.

## Optional native exploration

Use native exploration explicitly when the recorded atlas does not represent the
question. Export the prepared capsule before switching so its path and context
remain recoverable; do not silently reinterpret a selector as a query.

Resolve pronouns into a self-contained query, such as “KK towers as dark matter,”
and preserve the user's physical application and constraints. Native `refine`
refreshes the top five anchors from the current view unless explicit `focusIds`
are supplied. `pivot` clears inherited anchors; `broaden` also releases constraints.
Select a current direction or use `back/replay` for exact states. Nearby native
choices are proposals, not a guaranteed topic hierarchy. `derive`, `phenomenology`
and `recent` express mechanism, implications and dated work; ON/USING is independent
of recency. Empty or unsupported queries must not produce invented anchors.

The native chart fits five dynamic direction means and overlays source vectors.
Distinguish group fidelity from source-overlay fidelity and within-group spread.
Report low coverage or retained variance when relevant; slab thickness is not a
physical scale. Never invent embeddings, retrieval edges, projections or state IDs.
The pinned engine/data/state must reproduce computed geometry. Continue independent
literature research for current or out-of-corpus material and label it separately.

## Preserve authored views and recover

Use a full capsule for authored names, groups, interpretations or context beyond an
installed destination. Preserve evidence separately from interpretation; omit
geometry if none was computed or identify an authored display layout explicitly.
Import/apply displays the supplied object exactly, including an unknown builder.
Do not replace it by a silently recomputed recipe. Only supported recorded actions
can continue it; a custom group ID is not a native direction ID. Unsupported
builders remain readable snapshots. The browser retains 24 accepted full capsules
in memory; after reload or eviction, reopen the export for exact authored context.

Prepared links exclude private work notes. Notes export separately. Full JSON/gzip
capsules retain authored content; a session alone does not retain arbitrary groups.
Publish only when a saved/shareable view is requested; saved links are public and
unlisted. If storage fails, preserve the file and say no durable link was created.
A saved URL alone does not notify an open tab: open the route or apply through its
controller, then verify the render.

On stale directions, inspect the current view again. On corpus, computation or
version mismatch, retain the export and load matching data; never patch IDs or
invent replacement vectors. After a bridge restart, reattach using its new token
and import the saved session. Stop after a clear repeated connection/data failure
and report the missing prerequisite instead of looping on speculative fixes.
