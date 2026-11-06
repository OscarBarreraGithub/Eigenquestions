# Eigenquestions v2

[Eigenquestions](https://eigenquestions.com) is a static physics explorer. A
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
Sources/Geometry tabs and path scrolling remain available during computation.
The public page and local page use the same engine and corpus.
Computation runs in a browser worker; the first load downloads the corpus, so
watch the loading progress. There is no public database, chat server or model
credential.

Export a **session** to preserve the path, or a **view** to include its computed
coordinates and evidence. Import either file to validate and recompute it against
the matching frozen engine/data version. Share focus creates a URL fragment for
the current question and anchors, without uploading your navigation session.

## Navigate with your own agent

Read or install [`skills/physics-navigator/SKILL.md`](skills/physics-navigator/SKILL.md),
then start a local companion:

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
real navigation and replay. Wrangler dry-run checks assets-only packaging.
Browser rendering and live-domain behavior require their separate integration
checks.

The existing GitHub Actions workflow validates and deploys authorized pushes to
`main` to the `eigenquestions` Cloudflare Worker and `eigenquestions.com/*` route.
No worker entrypoint or database binding is deployed. Unknown paths return 404;
the former voting, leaderboard, submission, quiz, taste and fixed-tree app is
retired. Its source is preserved at Git baseline
`9b7305541ca18ffd34bbe3786ee0cce75dea5633`, and its D1 database is left intact.
See [site operations and limits](docs/site.md) for packaging and rollback.

## Project context

The owner's original request, atomic acceptance plan, experiments and current
status are linked from [`Lab Notebook.md`](Lab%20Notebook.md). That one notebook
and ordinary Git history are the project record. Implementation boundaries and
verification commands are documented in [`AGENTS.md`](AGENTS.md).
