# Agent interface

The external agent interprets conversation. The shared local engine selects real
source facets, runs graph diffusion and vector geometry, and returns the exact
object rendered by the browser. The static website does not run a language model.

## Start a live session

Requirements: this repository, its frozen `data/navigation/` corpus, and Node 22
or newer. From the repository root:

```sh
npm run build
node bin/navigate.mjs serve --port 4317 --connection /tmp/eigenquestions-session.json
```

Keep that process running. It prints two browser links: a loopback link to the
same static renderer, and an `eigenquestions.com` link with bridge attachment data
in its fragment. Open the local link for the robust same-origin path. Public
HTTPS → loopback access depends on browser policy and permission; a server CORS
allowlist cannot override those policies. If public attachment fails, open the
printed local link. Session tokens are local access secrets and do not belong in
papers, exported sessions, Git, or shared screenshots.

In another terminal, agent operations immediately update attached browsers:

```sh
node bin/navigate.mjs navigate --query 'KK towers' --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs refine --query 'KK towers as dark matter' --intent phenomenology --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs refine --query 'How do those dark matter gravitons decay?' --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs state --connection /tmp/eigenquestions-session.json
```

Each result exposes resolved state, history, the first 12 ranked source candidates,
evidence IDs, directions, geometric diagnostics and warnings. `--full` returns
all points, provenance and the full chart basis/center. A subsequent `state` call
reports `browserStatus.acknowledgedCurrent` once an attached browser has rendered
that exact revision; a successful action alone does not prove a render. `search`
and `evidence` inspect without navigation:

```sh
node bin/navigate.mjs search --query 'KK towers' --intent recent --relation using --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs evidence --ids 'unit:ID_FROM_SEARCH' --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs select --direction 'direction:ID_FROM_CURRENT_VIEW' --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs back --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs replay --index 1 --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs export --out navigation-session.json --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs import --file navigation-session.json --connection /tmp/eigenquestions-session.json
```

Commands without `--connection` use the connection file printed by `serve` when
started without that option. Use the same explicit file for all commands when
running multiple sessions. `node bin/navigate.mjs help` lists flags. For local
artifact-only use, `compute --query 'KK towers' --out snapshot.json` emits a full
deterministic snapshot; it does not claim to update an unattached browser. An
exported session is portable to the static site's import control and recomputes
against the matching corpus. The bridge's local HTML is the live view artifact.

## MCP adapter

Any MCP client supporting local stdio servers can launch this configuration;
replace the paths with this checkout and its connection file:

```json
{
  "mcpServers": {
    "eigenquestions": {
      "command": "node",
      "args": ["/absolute/path/Eigenquestions/bin/mcp-navigator.mjs", "--connection", "/tmp/eigenquestions-session.json"]
    }
  }
}
```

Start the bridge first. Tools are `navigator_state`, `navigator_search`,
`navigator_evidence`, `navigator_navigate`, `navigator_export` and
`navigator_import`. The navigation tool accepts the action object in the
[shared contract](navigation-contract.md). It talks to the existing bridge, so
MCP and CLI operations update the same browser and history. The adapter follows
the [MCP newline-delimited stdio transport](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
and [tools protocol](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).
The browser SSE API is an internal bridge transport, not an MCP HTTP endpoint.

The skill at [`skills/physics-navigator/SKILL.md`](../skills/physics-navigator/SKILL.md)
can be copied to the agent's skill directory or loaded directly. The agent still
needs this checkout's executable interface and data; installing the skill alone
does not install Node, the corpus, a server, or browser access.

## Intent and context

Use `derive` for mechanism/mathematics, `phenomenology` for consequences or tests,
and `recent` with independent `workRelation: on|using|either`. ON/USING is a
retrieval classification inferred from question/method facets, not a certified
classification of every paper. It is exposed per source, including ambiguous
neighbors. “Recent” means recent within the frozen manifest date.

`refine` refreshes source anchors from the current chart, preserving evolving
context through pronouns without concatenating all ancestor queries. Prefer a
self-contained resolved query in agent calls. Supply `focusIds` for precise
source anchors; use `pivot` for a new topic and `broaden` to release anchors and
exclusions. All these operations recompute, rather than zoom a fixed tree.

## Tested behavior and limits

`node --test tests/integration/navigation.test.mjs` exercises the owner journey
with a deeper decay question, distinct derivation/phenomenology and recent
ON/USING views, a held-out black-hole journey, back/replay/import, empty and
unsupported queries, another corpus fixture, and actual MCP → bridge → SSE.
HTTP tests verify exact allowed origins, authentication and private-network
preflight. They do **not** establish browser permission behavior; browser results
are tracked separately in the acceptance evidence. The final authorized Chromium
run on 2026-11-06 passed **19 actual-browser checks**: MCP-driven owner/held-out
journeys and render acknowledgements; mobile readability and real marker clicks;
public-site computation, changed ON/USING evidence, selection/back/export/import/
reload; non-overlapping desktop labels; and recovery after blocked attachment.

The permission boundary is observed, not hypothetical. Headless Chromium
145.0.7632.6 reported that permission was denied to access the loopback address
space. Its permission states remained `prompt`, no CSP was present, and the test
granted no permissions or security exceptions. A fresh public launch link then
recovered to **Browser session**, computed five directions and showed the local
companion guidance when agent details were opened; it never claimed an agent
connection. Chrome documents this [Local Network Access permission boundary](https://developer.chrome.com/docs/modern-web-guidance/guides/security/local-network-access).
Successful public attachment after a permission grant was not tested. Use the
printed same-origin local link for the verified live-update path; the public
site remains independently usable without the bridge.

The v1 corpus is Swampland-centered. Query anchors are retrieved source vectors;
no new query embedding is invented. The primary 2D view fits five dynamic direction
means, with source vectors overlaid in the same plane. Group and source variance,
residuals and within-group spread are reported separately: high group fidelity
does not mean all source variation is preserved. Adjacency is retrieval
affinity or same-paper incidence, not a theorem or physical causal link. An
independent agent completed an eight-step axion journey but observed drift after
selecting a long method description; explicit application wording and source
anchors recovered it. Read competing sources' roles before treating a direction
as a continuation of the same physical application. Session
state is process-local until exported; restarting the bridge creates a fresh
token and requires reattachment. Export before stopping to retain navigation.
