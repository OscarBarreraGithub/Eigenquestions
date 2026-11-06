# Agent interface

The external agent interprets conversation. The shared local engine selects real
source facets, runs graph diffusion and vector geometry, and returns the exact
object rendered by the browser. The static website does not run a language model.

## Use the physics graph from Eigenquestions

Open [eigenquestions.com](https://eigenquestions.com/) and read this interface.
The graph is an optional source of orientation. **Always supplement it with
independent research and native reasoning**; its frozen, Swampland-centered
collection must not limit the questions, sources or conclusions you consider.
A short orientation should usually take one query and inspection of a few source
IDs. Expand only when it helps the user's task.

A bare homepage starts a neutral path even when prior browser data exists.
Use **Resume last view** or **Reconnect agent** explicitly to recover a previous
exploration/companion. Opening home does not erase the saved view. An explicit
`#view`, `#focus` or companion token link opens its intended destination. After a
companion token has been removed from the address bar, reloading the bare page
requires explicit Reconnect; a saved token is not permission to reconnect silently.

An agent with permission and tools to execute JavaScript in the page can use
`window.eigenquestionsNavigator`. It shares the human UI's controller and worker;
there is no second engine, server computation, model backend or required install.
Use the structured object rather than depending on clicking UI coordinates:

```js
const graph = window.eigenquestionsNavigator;
await graph.ready();
const current = graph.read();
const orientation = await graph.orient('KK towers as dark matter', {
  intent: 'phenomenology', lens: 'combined', workRelation: 'either'
});
// orientation is a full contextual-view capsule. This did not move the UI,
// change its history, or replace the human's draft.
const sources = orientation.snapshot.view.nodes.slice(0, 5);
// When the task calls for a visible update, read the latest revision first:
const latest = graph.read();
graph.apply(orientation, {expectedRevision: latest.revision});
```

| Page method | Behavior |
|---|---|
| `ready()` | Promise for the first accepted display object; corpus computation may still be unloaded. |
| `read()` | Copy of `{apiVersion,revision,renderedRevision,busy,mode,capabilities,capsule}`. |
| `orient(query, options)` | Compute an ephemeral capsule in the same worker; never commit it or alter the draft. Options are canonical state fields except corpus/computation identity. |
| `evidence(ids)` | Inspect supplied current sources by ID; missing IDs require loading the native corpus. At most 100 IDs. |
| `apply(capsule,{expectedRevision})` | Validate and display the exact supplied result; replaces the page's active object and detaches a local companion. It does not recompute or silently discard custom groups. |
| `navigate(action,{expectedRevision})` | Commit a native action against the last visible canonical session, retaining existing race guards. Returns the accepted object or rejects on failure/supersession. |
| `export()` | Copy the complete capsule, including explicit context, groups, source links and continuation information. |
| `publish(capsule?)` | POST the explicit/current capsule as gzip to storage; returns a receipt only after durable save. Does not move the current path. |
| `subscribe(callback)` | Observe accepted object changes; returns an unsubscribe function. |

`revision` belongs to this page controller; it is not a scientific state ID or
the companion's server revision. Read it immediately before a mutation. A stale
`apply` rejects with `code: revision_conflict`; inspect `error.current` and
reconsider the operation instead of retrying blindly. Newer UI intents supersede
older pending computations. `renderedRevision === revision` acknowledges a past
render after animation-frame opportunities; it does not prove the tab is visible
to the human. `ready()` alone is not a render acknowledgement.

## Full contextual views and saved links

The authoritative exchange is the [contextual-view capsule schema](../schemas/contextual-view.schema.json),
implemented by the [pure validator/codec](../lib/protocol/capsule.mjs). A capsule
contains `builder`, explicit `context`, `snapshot.view`, optional canonical
`snapshot.session`, and `continuation`. Group names, overlapping memberships,
source evidence, typed relationships and order survive import/export exactly.
An absent projection is valid; geometry is unavailable for that view. An
`affine-plane` describes a real center and orthonormal basis; `display-layout`
only describes supplied display positions and makes no geometric claim.

Display, recompute and continue are separate capabilities. Unknown builders can
be displayed and exported without loading the native corpus. Recompute needs
the exact supported native builder/version and computation identity. Continue
needs a compatible canonical session and supported explicit actions. An authored
group ID is not necessarily a native direction ID: use a resolved `refine`/`pivot`
query plus genuine source `focusIds`, not `select` of an invented group ID.
Native continuation consumes the canonical query/anchors/options; preserving
broader context in the capsule does not make those fields part of the engine's
math. A new computed result can therefore differ from the author's grouping.
Do not promise semantic preservation beyond the recorded action.

For a saved link, send the same validated capsule:

```sh
curl --fail-with-body https://eigenquestions.com/api/views \
  -H 'Content-Type: application/json' --data-binary @view.json
# For a larger view, gzip it locally, then use Content-Type: application/gzip.
# Do not send a Content-Encoding header.
```

The JSON receipt is `{id,url,readUrl,sha256,bytes,createdAt}` (201 new, 200 identical
retry). GET `readUrl`, or `/api/views/ID`, returns the exact saved JSON/gzip bytes;
there is no `Content-Encoding` header, so decode gzip explicitly. Stored bytes
are limited to 512 KiB and decoded JSON to 2 MiB; the shared codec also limits
structure, source/group counts, projection dimensions and references. Save links
are **public and unlisted**: anyone with the link can read them. Keep private
connection tokens and unrelated conversation data out of capsules.

`/#view=ID` loads the full object directly. A changed hash loads a new object in
the existing page; stale requests cannot replace a newer route. A URL sent in
chat does not notify an already-open tab by itself. Opening the link, changing
that tab's route, or invoking the page object's `apply` is the concrete update.
Download/Open file and drag-and-drop use the same capsule, including `.json.gz`.
A full stored/file view renders before any corpus download. Native arbitrary
queries load and compute on the user's browser only. Storage may be inactive or
at capacity: preserve the capsule and use a file when saving returns an error;
see [storage operations and limits](stored-views-operations.md).

## Capability fallback and discovery

An HTTP-only agent can read these instructions, the [corpus manifest](../data/navigation/manifest.json),
linked paper metadata/source descriptions, and existing saved capsules. It can
upload a valid authored capsule built from its own source-based work. HTTP access
alone cannot execute the browser worker, compute an arbitrary native query, or
mutate another person's browser session. State that boundary; do not substitute
fabricated coordinates or imply a stored authored view is native computation.
Use source links for independent research, and offer a saved view/file where
helpful. The [discovery file](../llms.txt), robots and sitemap help find documents;
they confer no tool capability or permission. The page object is not an MCP
server or a claim of universal browser-agent integration.

## Optional local companion and MCP

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
can be copied to the agent's skill directory or loaded directly. The browser route needs no skill installation. The optional local companion needs
this checkout, Node and its corpus; installing the skill alone supplies none of
those capabilities.

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
exclusions. These operations use the actual computed source neighborhood rather than a fixed
tree. Native selection of an exactly matching active-prefix state returns to that
step without inventing another level; its source remains a valid offered choice.
The check uses the full normalized state and never removes evidence merely to
force novelty. Old exported histories remain intact. Short visible labels are
presentation excerpts only: use `capsule.context.question`, canonical state,
full direction queries and evidence for reasoning. Native row Method/Question
labels describe the representative source facet; they do not certify a newly
synthesized question cluster.

## Tested behavior and limits

`node --test tests/integration/navigation.test.mjs` exercises the owner journey
with a deeper decay question, distinct derivation/phenomenology and recent
ON/USING views, a held-out black-hole journey, back/replay/import, empty and
unsupported queries, another corpus fixture, and actual MCP → bridge → SSE.
HTTP tests verify exact allowed origins, authentication and private-network
preflight. They do **not** establish browser permission behavior; browser results
are tracked separately in the acceptance evidence. The earlier Q-001 authorized Chromium
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

The Q-003/Q-004 browser API, stored-capsule and startup changes have separate
acceptance coverage in `tests/integration/stored_views_browser_acceptance.py`;
current implementation and Node checks must not be mistaken for completed
public deployment or browser acceptance. Release evidence records those results.
