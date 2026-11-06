# Q-002 interaction and acceptance review

Reviewer: Astra `navigator_protocol`. Implementation owner: `navigator_site`.
This is an observable acceptance contract and evidence record, not a claim that
unrun browser checks have passed. The unchanged Q-001 engine, corpus and agent
interface remain the scientific/computation baseline.

## Initial review findings

The v1 main thread already delegates mathematical computation to a worker, but
its interaction policy is unsuitable for the requested smooth text navigator:

- The `busy` guard silently discards Back, Reset and additional navigation.
- Every accepted response rewrites query/intent inputs. A worker response or
  unsolicited agent update can erase a draft being typed.
- Bridge revision checks reject older revisions but allow duplicate SSE/POST
  render passes. A response from an old standalone worker has no revision and
  can overwrite a newly attached agent session without a transport generation.
- Terminating/replacing a worker does not settle its outstanding promises.
- Protocol `reset` already clears focus, constraints and history; the existing
  UI resets to a hardcoded KK query. New path should use an empty reset, focus
  the query input promptly and preserve a valid companion attachment/token.

These are rendering/controller concerns. No change to scientific retrieval,
embeddings, computation identity or protocol reset semantics is indicated.

Root's concurrency review found one transport-level requirement: a UI rebase
through session import must not overwrite an external MCP mutation between its
revision check and import. The approved minimal fix adds optional `If-Match`
revision guards to action/import, atomically checked after body parsing. Stale
requests return 409 with the current snapshot; malformed guards return 400;
missing guards preserve existing MCP behavior. The real-MCP integration test
holds an import body open, commits a newer MCP state, then finishes the stale
import and verifies that the newer state survives. The UI must preserve its draft
and show a conflict, without silently retrying a rewind.

## Observable acceptance

| Check | Observable outcome |
|---|---|
| Text is primary | Miller columns and readable computed directions are the default; the chart is an optional detail tab. Approximately five current choices are visible without a giant blank chart/spinner. |
| Labels are computed | A new question changes direction IDs/labels and source evidence; the displayed current choices agree with the same engine's current view. No fixed topic tree is substituted. |
| Path is usable | Current step is identified; a direction adds a step; Back/replay restores the exact state; a historical-column selection branches from that displayed parent. Uncomputed historical directions are not invented. |
| New path is obvious | A prominent New path control empties the query, focuses it, clears inherited source focus/constraints/history and old columns, and preserves a connected companion. New path supersedes outstanding old responses. |
| Local actions stay responsive | Typing, reading tabs, column scrolling and details stay usable during delayed computation. Existing evidence stays visible with a compact pending indicator. A completed response does not erase an unrelated draft or reset a presentation tab. |
| Navigation is coherent | Rapid input has a defined serialized/latest-intent result. Back during computation follows the displayed path rather than disappearing. Old worker/transport responses cannot restore a superseded path. Duplicate or lower bridge revisions cannot overwrite newer state. |
| Agent and browser agree | Actual MCP actions update the text view and render acknowledgement; browser New path and later question submissions update the same canonical companion state. Reload/export/import remain reproducible and tokens stay outside exports. |
| Keyboard/mobile controls work | Main controls, directions and tab hit areas are at least 44 CSS pixels high; keyboard focus and Enter navigation work. Narrow screens retain readable columns/cards without page-level overflow. |
| Performance is measured honestly | Record warm input/click-to-next-frame timings and main-thread long tasks, separating corpus download/index/engine wait from local interaction work. Headless Slurm results describe that environment; they are not a universal 60 fps or device-performance guarantee. |

## Deterministic race tests

The browser suite delays **delivery of real worker results**, not their contents,
using a test-only Worker wrapper. The numerical engine still computes every
tested view. An analogous wrapper can delay return of a real `/api/action` fetch
response while newer MCP/SSE state arrives. This makes stale-result handling
observable without changing production code, inventing a result or adding a
public testing endpoint.

Under that delay, the suite types a new draft and switches detail tabs, invokes
Back and New path, and waits beyond the delayed delivery window. The accepted
state and input must still reflect the latest user intent. The previous content
must remain readable while pending. Measured interaction budgets are generous
acceptance ceilings for an unthrottled headless test; timings and long-task
distributions are retained so a passing ceiling cannot be mistaken for proof of
perfect animation.

The agreed latest-submit policy is explicit: if B is submitted while A is pending
and unseen, B replaces A from the last **visibly accepted** session. B's exported
history must omit A and its source focus must match that visible base. Back uses
the preceding visible history index. New path removes all queued old UI intents.
The suite also gates delivery, rather than merely hoping a sleep is long enough:
it releases A only after B is queued, and releases a real rebase import only after
an intervening MCP mutation has committed. The latter must yield an explicit
conflict and retain both the newer agent state and the user's draft.

## Agreed browser selectors

`#question`, `#intent`, `#lens`, `#work-relation`, `#transition`, `#back`, `#broaden`
remain stable. `#reset` is New path. Miller columns use
`.miller-column[data-state-id][data-history-index]`; the current column has
`data-current="true"` and contains `#directions .direction[data-direction-id]`.
`#view-sources` and `#view-geometry` switch a reading pane; `#chartpanel` is hidden
by default. `#browse-prev`/`#browse-next` scroll columns without recomputing.
`#pending-indicator` exposes pending work. Existing chart selectors remain usable
after opening Geometry, so Q-001 coverage can be retained without making that
chart the primary interaction again.

## Evidence status

The first authorized Slurm run, job `58205898`, passed all 16 Q-002 checks and
all 14 retained Q-001 checks against source
`dfb26ff86c8d699015ce6ec06fb1114f18b5de16`. The
[Q-002 report](evidence/q002/browser-v1/q002-browser-acceptance.json),
[retained suite](evidence/q002/browser-v1-legacy/browser-acceptance.json) and
[execution receipt](evidence/q002/browser-v1-job.json) record the result. Both
the actual standalone worker and MCP companion were exercised; the Q-002 page
reported no uncaught browser errors. Gated races verified that an unseen A
cannot contaminate B's history/focus and that a newer MCP mutation survives a
stale UI rebase, with the draft and explicit conflict message retained.

In Chromium `145.0.7632.6`, this unthrottled two-core headless run reached the
local initial view in 2.795 seconds. Eleven warm local input/tab samples had a
27.5 ms median and 28.5 ms p95 to a double-animation-frame opportunity, with no
observed main-thread long tasks in that measurement window. These are small,
environment-specific samples, not a guarantee about network loading, every
interaction, real display painting, mobile hardware or continuous frame rate.

Root's screenshot review requested a bounded mobile refinement: collapse Search
options to reduce the initial control stack while preserving easy access. The
final follow-up must exercise that disclosure, expanded targets, a top-of-page
mobile viewport, historical-column branching, and the added provenance/dialog
screenshots. Those additions were **not** in the first frozen archive and are
not covered by its passing receipt. Public v2 release and final visual acceptance
remain pending. Root owns execution, visual review, notebook and release; this
reviewer does not launch a local browser, SSH, commit, push or deploy.
