# Eigenquestions v2

[Eigenquestions](https://eigenquestions.com) is a source-backed physics atlas with a
static frontend. Prepared destinations carry versioned identities, scientific
scopes, reading limits and typed connections. The text explorer puts the current
question, roughly 1–15 useful next choices and the saved path first. Overlapping
topics and qualified cross-routes provide more than a fixed topic tree.

The separate overview combines a physics classification entrance with a schematic
of reviewed collection entries. Schematic distances have no scientific meaning.
An optional native source explorer uses the frozen graph and embeddings to
recompute a local view, normally with about five directions. That explicit mode
does not rename the prepared scientific destinations.

The underlying frozen Swampland-centered corpus has **6,478 cataloged papers**
(**6,477 with available source text**) and **26,410 extracted question/method
descriptions**, dated **2026-11-05**.
Recent means recent within that collection. Source descriptions and retrieval
similarity are not independently verified physics claims.

The source accounting approved on **2026-11-17** covers all **8,473 extracted
question descriptions**: **8,436** have reviewed topic placements and **37** remain
discoverable without an assigned precise placement, with individual reasons.
None remains reserved. These placements organize the collection; they do not
assert that every description is a unique canonical question or that all physics
is covered. The frozen independent routing diagnostic found useful broad
orientation but uneven fine-question resolution. The dated 43-source amendment
followed scoring and is not an independent retest. Final browser/public release
evidence is recorded separately from this scientific accounting.

## Run the static explorer

Requirements: Node 22 or newer and npm.

```sh
npm ci
npm run build
npm start
```

Open `http://127.0.0.1:4173`. With an installed atlas, the bare homepage opens the
all-physics entrance. Choose a field or a scientific destination, inspect its
sources and follow a recorded direction. **New path**, Back and replay preserve
explicit history; **Resume last view** opens a prior exploration. Explicit
prepared/view/companion links open their named destinations. Browser title/alias
lookup is lexical; an agent interprets prose and checks scope before selecting an
existing record.

The full question, source descriptions, methods, assumptions and review history
remain accessible in disclosures. Membership, typed source contributions and
same-paper method context have distinct meanings. Notes attach locally to exact
destination IDs and export separately. Compact prepared links need no upload and
contain no private notes. The browser and agent use the same state/controller;
visible agent updates require a captured parent revision and render acknowledgement.

Native refine/pivot and source-based local projections remain explicit options.
Their first query downloads the frozen vector corpus; prepared browsing does not.
The static service performs no model inference or scientific graph computation.

Export a **session** for native replay, or a **view** for the complete displayed
object: context, groups, labels, sources, relationships and optional
geometry. Import or drop a view file to display it exactly, including another
builder's authored groups. Compatible recorded actions can continue locally;
display does not imply that an outside builder can be reproduced. JSON and gzip
files use the same contract. Share focus creates a compact native recipe URL;
it does not preserve arbitrary authored organization.

The bounded upload service prepares immutable full-view links of the form
`/#view=ID`. **Hosted storage activation is currently pending:** Save link
reports unavailable storage and preserves the downloadable view. Local Worker
and browser-adapter tests pass; they are not a claim of live R2 activation.
See [storage operations](docs/stored-views-operations.md) and the
[mechanism showcase](docs/contextual-view-showcase.md).

## Navigate with your own agent

Ask an agent to “use the physics graph from Eigenquestions.” The public
[instructions](docs/agent-interface.md) and `/llms.txt` describe the supported
capabilities. A browser agent able to execute page JavaScript can use
`window.eigenquestionsNavigator`: `orient` computes without moving the human's
path; `apply` and `navigate` explicitly update it with revision guards. This
route needs no checkout or companion. HTTP-only agents can read sources and
capsules, but cannot execute arbitrary browser queries. Graph orientation always
supplements independent research and original-paper checking.

For optional local CLI/MCP access, read or install
[`skills/physics-navigator/SKILL.md`](skills/physics-navigator/SKILL.md), then start
a local companion:

```sh
node bin/navigate.mjs serve --port 4317 --connection /tmp/eigenquestions-session.json
```

Open its printed local browser link. Agent commands update that browser
immediately through the shared session:

```sh
node bin/navigate.mjs navigate --query 'KK towers' --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs refine --query 'What if those towers are dark matter?' --intent phenomenology --connection /tmp/eigenquestions-session.json
node bin/navigate.mjs state --connection /tmp/eigenquestions-session.json
```

The agent interprets conversation, checks sources and chooses actions. The engine
performs retrieval and geometry. CLI and stdio MCP operations support search,
evidence, navigation, replay and export. See the complete
[agent interface](docs/agent-interface.md) and [shared contract](docs/navigation-contract.md).
The companion token stays local; don't share its launch link or connection file.

The same-origin companion page is the reliable way to receive agent updates.
Connecting the public HTTPS site to a loopback HTTP companion may be blocked by
browser mixed-content or private-network policy. A server CORS allowlist does
not override browser policy. Use the local link if public attachment fails.

## Check and deploy

```sh
npm run build
npm test
npm run check:site
npm run deploy:check
```

The build copies explicitly selected product files to `dist/`. Checks verify
shard hashes, limits, links and retired routes; geometry/protocol tests exercise
real navigation, replay, full-view fidelity and bounded storage. Wrangler dry-run
checks local packaging without provisioning resources.
Browser rendering and live-domain behavior require their separate integration
checks.

The existing GitHub Actions workflow validates and deploys authorized pushes to
`main` to the `eigenquestions` Cloudflare Worker and `eigenquestions.com/*` route.
The default profile serves static assets directly and a small unbound storage
API. The separate activation profile adds a dedicated R2 bucket and a SQLite
budget coordinator; it is not enabled yet. Unknown paths return 404;
the former voting, leaderboard, submission, quiz, taste and fixed-tree app is
retired. Its source is preserved at Git baseline
`9b7305541ca18ffd34bbe3786ee0cce75dea5633`, and its D1 database is left intact.
See [site operations and limits](docs/site.md) for packaging and rollback.

## Project context

The owner's original request, atomic acceptance plan, experiments and current
status are linked from [`Lab Notebook.md`](Lab%20Notebook.md). That one notebook
and ordinary Git history are the project record. Implementation boundaries and
verification commands are documented in [`AGENTS.md`](AGENTS.md).
