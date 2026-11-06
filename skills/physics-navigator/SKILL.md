---
name: physics-navigator
description: Navigate the Eigenquestions physics graph and source embeddings from a conversation, compute deterministic local views, and update its browser through the local CLI or MCP interface. Use for contextual exploration, source comparison, or a requested navigation journey; not as proof of a physics claim or a live literature index.
---

# Physics navigator

Use the real navigation object. Interpret the conversation into a current
question, intent, source focus and constraints; let the engine compute candidates,
directions and coordinates. Read [the command reference](references/interface.md)
when connecting or choosing an operation. A copied skill needs a separate
Eigenquestions checkout with Node and its corpus; locate it from user context or
`EIGENQUESTIONS_DIR`, and ask for its location only if it cannot be found.

## Resolve the conversation

- Inspect `navigator_state` (or CLI `state`) first: current question, active
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
2. Invoke the interface and wait for its computed result. Never invent vectors,
   chart coordinates, basis directions or graph edges, and never hand-edit a
   state ID. The same frozen corpus and state must reproduce the chart.
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
5. Confirm the render with a subsequent state inspection: the bridge reports
   `browserStatus.acknowledgedCurrent` only after a browser acknowledges that
   state/revision. This confirms a past render, not that the user still sees the
   tab. Otherwise report that the update was computed but its display is not
   confirmed. A JSON result without attachment is only an artifact.
   Export the session before stopping when the user wants to retain the journey.

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
