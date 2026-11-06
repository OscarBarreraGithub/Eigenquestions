# Eigenquestions static explorer

Eigenquestions draws a new local view of source-linked physics descriptions for
each question. The v1 collection contains 6,478 papers and 26,410 extracted
question/method descriptions, frozen on 2026-11-05. It is centered on Swampland
research. It does not cover all physics, and “recent” means recent within these
dated inputs, not a live literature search.

Enter a concept or question, choose an approach, and follow one of approximately
five computed directions. **Refine this context** carries forward source anchors;
**Pivot to a new focus** clears them. **Broaden** releases those anchors and
exclusions. The history path and **Back** restore exact prior states. The approach,
question/method perspective and on/using relation all enter the shared engine.
The browser performs deterministic retrieval; it is not a conversational language
model. Your own agent can resolve conversational references and navigate the
same object using the [agent interface](agent-interface.md).

The primary chart projects approximately five weighted direction-group centers
onto a local affine plane in the real embedding space. An optional overlay shows
the individual source descriptions in that same plane. Its caption separately
reports variation retained between group centers and among individual sources:
a useful overview of groups does not imply a faithful map of every paper. Group
spread, residual cutoff, neighborhood retention and distortion remain inspectable
in the computed view. Low source-level retention is a material limitation. Point proximity, retrieval-affinity edges and proposed
directions do not establish physical implications. The source panel labels
extracted descriptions and links to papers so claims can be checked.

## Portable sessions and agent updates

**Export session** writes the canonical versioned session, including the complete
path. **Export view** adds the computed view to a snapshot. Either export can be
imported; the browser validates its session and recomputes from its own frozen
corpus. A foreign corpus/version is rejected. **Share focus** encodes only the
current state in the URL fragment; it includes anchors and intent but not the
full history. No session is uploaded to a public server. Browser local storage
keeps the most recent session when available.

The local companion serves the same app and publishes session changes through
Server-Sent Events. A companion launch link attaches automatically; subsequent
agent operations redraw the page. Its unpredictable token is
saved in tab-scoped session storage for reload and removed from the address bar
after attachment. Disconnect clears it. After a paint opportunity, the browser
acknowledges the current state/revision to the companion so the agent can inspect
whether a renderer has actually displayed its update. It is never included in exported
sessions or share links. The public HTTPS page offers explicit attachment to a
loopback companion, but browser mixed-content/private-network policy may block
it. The same-origin local companion page is the supported fallback. Browser
compatibility must be tested separately from HTTP transport checks; no universal
HTTPS-to-loopback guarantee is made.

## Build and run

Use Node 22 or newer:

```sh
npm ci
npm run build
npm test
npm run check:site
npm start
```

The static preview binds to `127.0.0.1:4173`. `PORT` or the first argument of
`scripts/site-serve.mjs` changes the port. The browser downloads about 85 MB of
uncompressed frozen assets on the first load. A progress message remains visible;
loading, indexing and subsequent computations run in a module Web Worker to
keep the page responsive. Browser/edge HTTP caches may reduce repeat transfers.
There are no application runtime packages or remote model calls.

`scripts/build-site.mjs` copies only explicit app/engine/data/skill/schema/product
documentation inputs into `dist/`; original prompts, notebooks and release
planning documents are excluded. `check:site` validates shard hashes, product
links, static hosting configuration and asset sizes. The native Node tests also
exercise 404 responses for retired routes. Browser QA is a separate integration
gate: Node HTTP checks do not establish rendering or interaction correctness.

## Deployment and rollback

`wrangler.toml` keeps the existing `eigenquestions` Worker name and
`eigenquestions.com/*` route, with an assets-only configuration. It has no Worker
entrypoint, application API or D1 binding. Unknown paths return the new 404 page;
there is no SPA fallback exposing a misleading successful old API path.
The old D1 database is left intact. Former voting, submissions, leaderboard,
quiz, taste and fixed-tree pages are not present in the build.

GitHub Actions validates and publishes `dist/` on authorized pushes to `main`,
using the repository's existing Cloudflare secrets. Implementation work stays on
`agent/question-conditioned-navigation`; the coordinator owns release.
`npm run deploy:check` performs local build/validation and Wrangler dry-run only.
It does not establish live-domain behavior or account permissions.

The old application is recoverable from Git baseline
`9b7305541ca18ffd34bbe3786ee0cce75dea5633`. Rollback should restore its source,
lockfile and deployment configuration together. Do not mutate or recreate the
database as a side effect of source rollback.

Hosting follows Cloudflare's [static assets configuration](https://developers.cloudflare.com/workers/static-assets/binding/)
and [limits](https://developers.cloudflare.com/workers/platform/limits/): one
asset collection, at most 25 MiB per file, and a conservative 20,000-file build
limit. Existing Wrangler 4.95.0 is pinned explicitly. Current npm audit reports
development-tool transitive advisories in that version; none of those packages
ship in the public static runtime. A tooling upgrade is separate from this
hosting migration and should rerun the packaging checks.
