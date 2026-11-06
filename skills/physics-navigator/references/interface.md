# Local interface reference

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
towers' --out snapshot.json`. This creates a deterministic JSON artifact; to
update a browser, start/attach the bridge. Portable exports contain the session,
not executable code or session tokens, and can be imported into the static app.
