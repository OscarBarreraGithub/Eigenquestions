# Eigenquestions v2

[Eigenquestions](https://eigenquestions.com) is a physics explorer with a static frontend. A
question selects a source-grounded neighborhood of real graph and embedding
objects; deterministic local code recomputes about five directions to consider
next. A live text-column explorer makes those choices and the path primary, with
source reading and an optional geometric view below. Refinement can introduce connections from
across the corpus. It is not a fixed topic tree or a language-model chatbot.

The first corpus is a frozen Swampland-centered collection of **6,478 papers**
and **26,410 extracted question/method descriptions**, dated **2026-11-05**.
Recent means recent within that collection. Source descriptions and retrieval
similarity are not independently verified physics claims.

## Run the static explorer

Requirements: Node 22 or newer and npm.

```sh
npm ci
npm run build
npm start
```

Open `http://127.0.0.1:4173`. Choose a concept, approach and perspective. Refine
keeps source context, pivot starts another focus, and back/path controls replay
prior views. **New path** clears the inherited context and focuses a fresh question.
Opening the bare homepage is always neutral. **Resume last view** explicitly
opens the previous exploration; explicit view/focus/companion links still open
their destinations. Short navigation excerpts leave the full **context** and
source text accessible. Earlier columns retain their actual choices and mark
the choice followed. An exact native revisit returns to its earlier step instead
of adding apparent depth. Method and question facets remain distinguishable;
these representative excerpts are not automatically synthesized topic names.
Sources/Geometry tabs and path scrolling remain available during computation.
The public page and local page use the same engine and corpus.
Computation runs in a browser worker; the first native query downloads the
corpus. Empty startup and complete saved views do not require that download.
The public service performs no model inference or scientific graph computation.

Export a **session** for native replay, or a **view** for the complete accepted
scientific object: context, groups, labels, sources, relationships and optional
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
