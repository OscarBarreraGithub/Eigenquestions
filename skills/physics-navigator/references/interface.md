# Interface reference

The maintained [agent interface](../../../docs/agent-interface.md) is published at
`https://eigenquestions.com/docs/agent-interface.md`. Read it for full schemas,
limits and capabilities. The browser controller is the primary no-install route
when your tool can execute JavaScript in that page:

```js
const graph = window.eigenquestionsNavigator;
await graph.ready();
const before = graph.read();
const orientation = await graph.orient('KK towers as dark matter', {
  intent: 'phenomenology', lens: 'combined', workRelation: 'either'
});
// Inspect orientation.snapshot.view.nodes/directions and original paper links.
// Independent research continues; orient did not move the human's path.
const latest = graph.read();
graph.apply(orientation, {expectedRevision: latest.revision}); // only for a visible update
const capsule = graph.export();
// When a saved link is requested: await graph.publish(capsule).
```

`read()` returns controller revision, renderedRevision, busy, capabilities and
capsule. `navigate(action,{expectedRevision})` uses the shared native worker and
canonical session. `evidence(ids)` inspects source IDs; `subscribe(callback)`
observes accepted changes. `apply` accepts a complete capsule exactly and
switches this page away from a local companion. Check the latest revision before
mutating; a stale operation must not replace a newer human/agent view.

Capsule fields are `schemaVersion`, `kind: eigenquestions-contextual-view`,
`builder`, explicit scientific `context`, `snapshot:{view,session?}`, and
`continuation:{mode,originStateId,description,actions}`. Never collapse an authored
capsule to just query/anchors and claim all meaning survived. Native actions use
canonical fields, not arbitrary assumptions or unimplemented builder algorithms.

An HTTP-only agent can GET saved view bytes at `/api/views/ID` and inspect static
source data from `/data/manifest.json`; it cannot execute the browser engine by
HTTP. POST `/api/views` accepts a validated capsule as `application/json` or raw
`application/gzip`, without `Content-Encoding`. The response contains
`{id,url,readUrl,sha256,bytes,createdAt}` after durable save. Limits:512KiB stored,
2MiB decoded; storage may be disabled or full. GET returns exact bytes, including
raw gzip when saved that way. Links are public/unlisted. JSON/gzip file import is
the fallback. No HTTP route computes arbitrary questions or mutates a user's tab.

## Optional local interface

Run from the Eigenquestions checkout, with Node 22+. First build its static
renderer (`npm run build`), then keep this process running:

```sh
node bin/navigate.mjs serve --connection /tmp/eigenquestions-session.json
```

Open the local browser link it prints. All subsequent CLI calls use the same
`--connection /tmp/eigenquestions-session.json`; omit that flag only when using
the default connection created by `serve` without a custom path.

MCP clients launch `node /absolute/checkout/bin/mcp-navigator.mjs --connection
/tmp/eigenquestions-session.json`. The server exposes:

| MCP tool | Arguments | CLI equivalent |
|---|---|---|
| `navigator_state` | `{}`; optional `full:true` for full basis | `state` |
| `navigator_search` | `{query, intent?, workRelation?, limit?}` | `search --query '…' --intent recent --relation using` |
| `navigator_evidence` | `{ids:[stableSourceId]}` | `evidence --ids 'unit:…'` |
| `navigator_navigate` | action below | `action --json '{…}'` |
| `navigator_export` | `{}` | `export --out session.json` |
| `navigator_import` | `{payload: exportedObject}` | `import --file session.json` |

Navigation action example:

```json
{
  "type": "refine",
  "query": "KK towers as dark matter",
  "intent": "phenomenology",
  "workRelation": "either",
  "lens": "combined"
}
```

Action types: `navigate`, `refine`, `pivot`, `broaden`, `select`, `back`,
`forward`, `replay`, `reset`. `select` needs `directionId`; `replay` needs
zero-based `index`. Optional `focusIds` are stable unit IDs, never titles.
`intent` is `explore|derive|phenomenology|recent|using`; `workRelation` is
`on|using|either`; `lens` is `physical_question|method|combined`.
`constraints` may contain `yearMin`, `yearMax`, and `excludeIds`.

`refine` defaults to the top five sources in the current view as refreshed
anchors. `pivot` clears inherited anchors. `broaden` also clears constraints.
New navigation after `back` truncates the forward branch; export first if both
branches matter. Empty/unknown queries yield warnings and no invented anchors.

The agent result contains `state`, `history`, the first 12 ranked `view.nodes`
with source evidence, `view.directions`, `view.chart`, `view.diagnostics`, and
`view.warnings`; full node/edge counts remain available. `browserStatus` reports
whether a browser acknowledged rendering the current revision. Inspect `state`
after an action to check that acknowledgement; do not infer a render from a
successful computation alone.
The full bridge result contains the canonical session and full numeric chart;
CLI `state --full` returns it. No browser click is needed for any agent operation.

To compute without a live bridge: `node bin/navigate.mjs compute --query 'KK
towers' --out snapshot.json`. This creates a deterministic JSON artifact that the page can open as a view.
To update an attached local browser automatically, use the bridge. Session
exports contain canonical native state; full contextual capsules preserve more
authored meaning. Neither format should contain executable code or session tokens.
