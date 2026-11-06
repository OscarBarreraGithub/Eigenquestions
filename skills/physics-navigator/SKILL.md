---
name: physics-navigator
description: Use the physics graph from Eigenquestions for optional source-linked orientation, contextual exploration, authored view sharing, or a navigation journey. Prefer its installed browser object when available; local CLI/MCP and HTTP-only reading are capability-dependent fallbacks. Always supplement with independent research.
---

# Physics navigator

Use the real navigation object as a supplement to independent research and native
reasoning. The frozen graph must not constrain what physics questions or outside
sources you consider. For an ordinary answer, start cheaply: one read-only
orientation and a few relevant source links, then return to the underlying task.
Do not move the human's path merely to gather background.

Read [the interface reference](references/interface.md) for the available mode:

- **Browser execution:** open `https://eigenquestions.com/`, read its agent
  instructions, and use `window.eigenquestionsNavigator`. No repository, skill
  install or companion is required. `orient` is read-only; `apply` and `navigate`
  explicitly commit to the shared page/UI. Respect the browser tool's execution
  permissions; a page object does not grant capabilities the tool lacks.
- **HTTP only:** read the manifest, source-linked static descriptions, or an
  existing saved capsule. This mode cannot run an arbitrary native query or
  update someone else's browser. Continue independent research, explain the
  boundary, and supply a source-grounded authored capsule/file if useful.
- **Local companion:** use the existing Node22 CLI or stdio MCP when a checkout
  and corpus are available. Locate them from user context or
  `EIGENQUESTIONS_DIR`; the copied skill alone installs neither data nor tools.

Bare home intentionally starts neutral. Resume the saved view or reconnect the
companion explicitly when that is the intended context; do not assume a reload
restored it. Read the machine object after choosing. Visible titles are concise
excerpts; full authoritative context/query/evidence remain in the capsule. A
native choice labeled Return to step N revisits an identical active-prefix state,
not a deeper topic. Method/Question metadata describes its representative source.

## Resolve the conversation

- Inspect page `read()` (or local `navigator_state`/CLI `state`) first: current question, active
  history, corpus scope/date, evidence IDs, warnings and proposed directions.
- Translate pronouns and shorthand into a self-contained query. For “what if
  they are dark matter?” after KK towers, use “KK towers as dark matter” with
  `intent: phenomenology` and `type: refine`. Preserve explicit user constraints.
- Use `derive` for mathematical mechanism, `phenomenology` for consequences or
  tests, and `recent` for dated work. ON and USING are independent of recency:
  `intent: recent, workRelation: using` differs from recent work `on` a concept.
- Clarify only if ambiguity changes the scientific neighborhood substantially:
  for example, an acronym with competing meanings and no context, or whether a
  requested “connection” means a derivation or phenomenological compatibility.
  Otherwise state a brief assumption and compute a reversible view. An empty
  query means no supported semantic anchor: ask what to explore or offer a few
  examples grounded in the stated corpus scope.

## Navigate and explain

1. Search or inspect evidence to resolve the requested concept into source IDs.
   `refine` refreshes top-five anchors from the *current* view on each turn unless
   you supply explicit `focusIds`; this supports deeper contextual follow-ups.
   Use `pivot` for an unrelated topic, `broaden` to release focus/constraints,
   `select` with a current direction ID, or `back/replay` to revisit a state.
   After selecting a method-specific direction, retain the user's physical
   application explicitly in the next resolved query and source anchors. Inspect
   whether competing sources address that application or merely share a method;
   the five choices are nearby proposals, not a guaranteed deeper topic hierarchy.
2. Invoke the interface and wait for its computed result. Never invent embedding
   vectors, affine planes, retrieval edges or evidence, and never hand-edit a
   native state ID. The same pinned engine/data/state must reproduce native math.
   Agent-authored names, overlapping groups and typed interpretive relationships
   may be supplied in a full capsule; distinguish them from computed results.
   Omit geometry if no real projection was computed, or explicitly type an
   authored display layout. Preserve evidence separately from interpretation.
3. Inspect ranked sources and about five directions, then read evidence for the
   connection you describe. Distinguish the source's claim, your interpretation,
   and an unanswered question. Cite stable paper/source links. Extracted facets
   are indexed descriptions, not guaranteed verbatim quotations; consult the
   actual paper before asserting a derivation or a decisive physical result.
4. Explain a small number of useful next choices in the user's terms. Similarity
   and same-paper edges are discovery aids, never proof of equivalence, causation
   or consistency. Report low coverage, high residuals or low retained variance
   when they affect interpretation. The default chart fits five dynamic direction
   means, with source vectors overlaid in that affine plane. Distinguish group
   fidelity from source-overlay fidelity and within-group spread; retained group
   variance does not certify source-level geometry. Slab thickness is not a
   physical scale.
5. For a requested visible update, re-read the page revision immediately before
   `apply`/`navigate`; preserve a newer state on conflict, rather than blindly
   retrying. Confirm `read().renderedRevision === read().revision` after the
   accepted update. The local bridge instead reports
   `browserStatus.acknowledgedCurrent` only after a browser acknowledges that
   state/revision. This confirms a past render, not that the user still sees the
   tab. Otherwise report that the update was computed but its display is not
   confirmed. A JSON result without attachment is only an artifact.
   Export the full capsule when the user wants to retain authored names, groups,
   explicit context and evidence. A canonical session alone supports native
   replay, not arbitrary authored grouping. Publish only when a saved/shareable
   view is part of the task; saved links are public and unlisted. If storage is
   unavailable/full, preserve the file and report that no durable link was made.

## Preserve the full view's meaning

Display, recompute and continue are different capabilities. Import/apply must
show the exact supplied capsule, including an unknown builder's groups. Do not
replace it by silently recomputing a small recipe. The displayed author question
may be broader than the canonical native seed query. For continuation, resolve
that question into an explicit native query plus genuine anchors; richer prose
context is preserved data, not automatically an input to the current math.

Follow only supported recorded actions. A custom group ID cannot be passed to
native `select`; use the author's explicit `refine`/`pivot` query and source IDs.
An unsupported builder remains a readable snapshot. The browser retains 24 full
accepted capsules in memory for exact authored Back/branch behavior; after reload
or eviction, reopen the exported view instead of substituting native labels.

A saved URL identifies a full object. Sending the URL alone does not notify an
already-open tab: open it, change that tab's route, or apply through its controller.
Files and gzip files use the same capsule. Keep connection tokens and unrelated
private conversation data out of exports and public uploads.

## Scope and recovery

“Latest” is bounded by the manifest snapshot. Say so; if genuinely current work
is requested, use available literature tools separately and label those findings.
Do not silently inject papers or fabricated embeddings into a frozen corpus.
For an unsupported/out-of-corpus question, report the gap, try a precise synonym
or source ID, and offer a corpus pivot. Do not return a confident unrelated map.

On stale direction IDs, re-inspect the current view and choose from its current
directions. On corpus/computation/version/ID mismatch, retain the export and load the matching
data or start a new session; do not patch IDs to make validation pass. Missing or
corrupt vector shards require repairing the dataset, not generated substitutes.
On a context-drift concern, inspect focus IDs and evidence, retry with an explicit
resolved query/anchors, then compare with a pivot; preserve the failed state as
history so the difference is inspectable.

A public HTTPS page may be unable to reach loopback. Use the same-origin local
link printed by `serve`; do not disable browser security or claim a CORS header
guarantees connectivity. After a bridge restart, reattach with its new token and
import the saved session. Tokens are local session secrets; exclude them from
exports, shared logs and citations. Stop after a clear repeated connection/data
failure and report the missing prerequisite; do not loop on speculative fixes.
