# Q-003 — A contextual view is the object; a URL is a carrier

Status: architecture proposal and measurements, **not an implemented new API**.
Read with the [original vision](requests/Q-001-original.md) and the one
[Lab Notebook](../Lab%20Notebook.md). Q-002's verified interface is live.

## The scientific object

Let D denote the versioned graph, source records and embedding representations.
Let C be the explicit scientific context, and a an accepted navigation action.

\[
C_{t+1}=T(D,C_t,a_t),\qquad V_t=F(D,C_t).
\]

The context can include the physical goal, assumptions, application, anchors,
exclusions, chosen perspective and relevant earlier decisions. It need not be a
full transcript, but its sufficiency must be tested against future transitions.
A query plus five anchors is sufficient for today's algorithm by construction;
it is not proof that this summary preserves the broader intended meaning.

The complete contextual view contains:

- Selected source identities, roles, order and relevant weights.
- Groups or an overlapping cover, memberships, names and descriptions.
- Relations with types and evidence; an affinity edge is not a physical theorem.
- Proposed next actions bound to their originating view and context.
- Evidence links, scope, uncertainty and construction provenance.
- A projection/layout definition or computed positions, when needed.
- The context and supported transition implementation needed to continue.

Source identities, view-local group identities and exploration history are
different things. A refinement may split, merge or reinterpret groups and add
sources outside the previous selection. Its selected set need not be a subset
of the old one. Depth is relative to an exploration, not a permanent property of
a concept. The protocol must accommodate these operations rather than encode a
fixed tree or a main-node-plus-zoom model.

For an affine geometric view, a center mu and an orthonormal D-by-2 basis B give
coordinates y_i = B^T(x_i - mu). A slab also needs its thickness and residual rule.
This describes geometry after selection; it does not determine scientific
groupings, names or meaning. Keep the geometry representation explicitly typed
so future nonlinear layouts or multiple local charts remain possible. Arbitrary
stretching changes distances and must not silently become a scientific metric.

## Three promises, checked separately

| Promise | What must survive |
|---|---|
| Display this view | Actual labels, memberships, relations, evidence, order and layout |
| Recompute this view | Available pinned data, code, effective inputs, parameters and deterministic rules |
| Continue this exploration | Explicit context and transition capabilities for the next action |

Store accepted agent-authored decisions. A model name and random seed do not
guarantee that rerunning the model reproduces a grouping or a label. Record
concise scientific decisions and provenance, not private reasoning transcripts.
Declare whether numerical comparison is exact or uses a stated tolerance;
pixel-identical rendering is a separate issue.

## Transport recommendation

The authoritative object is a versioned contextual view plus continuation
context. A compact recipe is an optimization when its reconstruction is proven.
Do not force the scientific representation to fit a URL budget.

1. Reference immutable corpus items by stable IDs; do not retransmit paper titles,
   source text or vectors already available in the identified dataset.
2. Encode all new decisions: custom labels, group memberships, changed relation
   semantics, context commitments and any genuinely new geometric parameters.
3. Omit a derived result only when the identified builder can reconstruct it.
   Do not silently replace agent-authored organization with today's grouping.
4. Embed the bounded compressed object in a URL fragment if it fits the tested
   transport budget. Otherwise deliver the same object through the existing
   local bridge or a file. A shareable content-reference URL additionally needs
   a real retrievable artifact; a digest alone is not its contents or location.

The browser decodes and validates data, invokes known versioned routines, and
updates the explorer using its existing worker. It does not execute code from a
URL. The page shell and loaded data can stay in place while the view updates.
Initial load, fragment changes and browser history need one consistent loader,
with latest-intent and revision protection preserved from Q-002. Encoder and
decoder limits must agree, including decompressed size.

Creating a link does not notify an existing tab. An agent must navigate a tab it
can control, apply the object through a supported browser interface, or provide
the link for the user to open. No server-side query computation is necessary.
No-install access still depends on the agent having the required browser or code
execution capabilities and obtaining the data needed for its computation.

## Orientation and independent research

Separate read-only orientation from committing a visible navigation step. An
agent should be able to inspect a computed neighborhood without moving the
human's path or overwriting a draft. Its ordinary reasoning, searches and original
paper checks continue; the graph supplements those methods and does not define
the only admissible sources. Unsupported topics should fall back to ordinary
research rather than force an unrelated graph route.

Publish concise discoverable instructions and capability metadata. Crawling is
discovery/fallback, not the primary graph interface. A browser machine interface
and the existing local MCP adapter can carry the same scientific object. Optional
[WebMCP](https://developer.chrome.com/docs/ai/webmcp) registration can wrap it where
supported; current experimental availability is not a universal prerequisite and
was not tested in the Chromium 145 environment used for Q-002.

## What exists, and what remains to establish

Today's engine receives query, intent, relation, lens, constraints and source
anchors. It performs retrieval, grouping and representative-text labeling, emits
affinity/same-paper edges, and fits a plane to five group means. The browser
receives a full view, not just a matrix. The agent cannot yet publish an arbitrary
contextual grouping/relations object through a general portable importer.

Share focus carries normalized current state, not the full path or result. It is
base64url encoding, not compression. Its fragment is parsed only at startup;
there is no hashchange loader. Its encoder lacks the decoder's size bound.
Export view includes the result, but import restores the session and recomputes.

Required next checks before choosing a new encoding:

- Two routes reaching the same words preserve their different scientific tasks.
- Display round trips retain every accepted group, label, relation and source.
- A repeated next action after reopening retains the required continuation state.
- Splits, merges, overlaps and entry from outside the previous neighborhood work.
- Missing data/builders degrade honestly; old identities do not archive assets.
- Real encoded sizes stay within an explicit budget, with a usable larger-object
  fallback. No compression scheme guarantees arbitrary views/history fit.
- Browser loading and computation are measured separately from rendering. Q-002
  verified the current corpus and UI; it did not establish scaling to all physics.

## Measured payloads (2026-11-06)

Astra protocol measured eight actual KK/DM/decay and axion/method/EDE views,
using compact JSON, raw DEFLATE level 9 and Brotli quality 11. The figures below
include base64url encoding and a 35-byte illustrative URL prefix. No compressed
URL loader has been implemented. The 4/8/16 KiB comparisons are engineering
budgets, not universal browser limits.

| Artifact | Raw JSON bytes | Brotli + base64url URL bytes |
|---|---:|---:|
| Current-state recipes, eight views | 518–999 | 451–781 |
| Four-state sessions | 3,706–3,772 | 1,149–1,381 |
| Existing nine-state agent session | 7,034 | 1,922 |
| Complete computed views | 281,278–330,086 | 80,850–102,746 |
| Lean source-referencing axion view | 118,797 | 29,027 |
| Four complete visited views | 1,178,352–1,226,154 | 271,139–311,149 |

The lean object retains 64 selected sources/order, five exact groups, 134 edges,
dynamic scores/roles, full-precision center/basis, diagnostics and current state.
It omits repeated static paper/facet metadata and source evidence recoverable by
ID, reconstructable group-centroid vectors, and previous path/UI revision.
Hydration exactly reproduced the original view without rerunning retrieval/PCA.
It is not a theoretical minimum or a self-contained full history.

All eight compact recipes exactly reproduced the view JSON with an independent
navigator in the same Node process. Different histories ending in the same
current state yielded identical views. This demonstrates today's deterministic
replay, while exposing the limitation: information absent from current state
cannot influence its output. It does not prove that the broader context-dependent
scientific navigation is represented adequately.

[Full measurements](evidence/q003/size-study/report.json) ·
[Lean retention/omission audit](evidence/q003/size-study/lean-result.json) ·
[Reproduction script](evidence/q003/size-study/measure.mjs) ·
[Session supplement](evidence/q003/size-study/supplement.mjs) ·
[Lean experiment](evidence/q003/size-study/lean.mjs).

The archived scripts retain their actual local project and temporary-directory
paths. Run them in order (measure, supplement, lean) after adapting those paths
and creating the output directory; they regenerate the intermediate snapshots.
The full raw snapshots are recoverable from those scripts and the pinned corpus,
so they are not duplicated in this research record.
