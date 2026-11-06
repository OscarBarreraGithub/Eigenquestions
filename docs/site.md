# Eigenquestions v2 · live text explorer

Eigenquestions draws a new local view of source-linked physics descriptions for
each question. The v1 collection contains 6,478 papers and 26,410 extracted
question/method descriptions, frozen on 2026-11-05. It is centered on Swampland
research. It does not cover all physics, and “recent” means recent within these
dated inputs, not a live literature search.

Enter a concept or question, choose an approach, and follow one of approximately
five computed directions. **Refine this context** carries forward source anchors;
**Start a different focus** clears them. **Broaden** releases those anchors and
exclusions. The history path and **Back** restore exact prior states. The approach,
question/method perspective and on/using relation all enter the shared engine.
The browser performs deterministic retrieval; it is not a conversational language
model. Your own agent can resolve conversational references and navigate the
same object using the [agent interface](agent-interface.md).

V2 makes a live Miller-column text explorer the primary view. Each visited question
has a column of its actually computed directions; a selected row marks the path.
The rightmost column holds the current choices. Historical choices are cached only
from views received for the same state and computation identity. An uncached old
native step offers **Restore step**, which recomputes it through the canonical
session. An unavailable authored view must be reopened from its full file;
native recomputation would not recover the author's grouping.
Following an old choice restores that step before branching. The breadcrumb and
column arrow controls scroll within their own bands without moving the document.

Concise excerpts identify the current focus and path; **Full context** reveals
the unshortened authoritative question or method description. The search field
is a fresh draft, not another copy of the accepted description. Native choices
show the representative paper and whether the source facet is a **Method** or
**Question**. These are source-based directions, not synthesized research
questions. Historical columns mark a recorded **Followed** choice separately
from a typed follow-up. When a native selection returns to an identical state
already in the active path, **Return to step N** revisits it rather than appending
another level. Related but scientifically distinct sources remain available.

**New path** resets the canonical history, query, focus and constraints, and focuses
an empty question input. It preserves an attached companion and the last nonempty
saved view for explicit resumption. Sources are displayed
by default; **Geometric view** is a presentational tab that uses the existing view.
The source button beside a current direction narrows and reveals the reading list
immediately. On phones, **Search options** keeps the current approach and changed
setting count visible; opening it reveals full-width, readable controls. An empty
new path uses a compact entry page.
The quiet arXiv-inspired treatment uses white, gray, blue links and familiar
Helvetica/Arial text, with Eigenquestions' own identity.

Typing, tabs, disclosures and horizontal scrolling remain available during
computation. A newer browser submission replaces a pending submission using the
last visibly accepted session, so it cannot inherit an unseen intermediate focus.
Back targets the preceding visible history step. Delayed results from a superseded
intent or transport cannot overwrite the active view, and incoming results preserve
an edited search draft. The browser caches at most 24 computed views and 24 compact
historical column descriptions; these caches do not change the numerical engine.
Companion mutations/rebases use revision preconditions. If an agent advances the
session concurrently, the newer path is kept, the draft remains, and the UI asks
the user to review and resubmit instead of silently rewinding the agent's work.

The secondary **Geometric view** projects approximately five weighted direction-group centers
onto a local affine plane in the real embedding space. An optional overlay shows
the individual source descriptions in that same plane. Its caption separately
reports variation retained between group centers and among individual sources:
a useful overview of groups does not imply a faithful map of every paper. Group
spread, residual cutoff, neighborhood retention and distortion remain inspectable
in the computed view. Low source-level retention is a material limitation. Point proximity, retrieval-affinity edges and proposed
directions do not establish physical implications. The source panel labels
extracted descriptions and links to papers so claims can be checked.

## Portable sessions and agent updates

**Download session** writes the canonical path for deterministic native replay.
**Download view** writes the full contextual capsule: computed or authored group
names, overlapping memberships, explicit context, evidence and optional geometry.
Opening a view file preserves that exact object without first loading the corpus;
opening a session recomputes against its pinned engine/data. Unknown builders
remain readable snapshots with explicit continuation limits. **Share focus**
encodes only a native current state, while **Save link** uploads the full capsule
to bounded public, unlisted storage when enabled. Anyone with a saved link can
open it. A storage error leaves the view available for local download. See
[storage operations](stored-views-operations.md). Browser local storage keeps the
most recent full view when available. A shared route takes priority over saved
state. A bare visit, including a reload, starts with an empty question and offers
**Resume last view**. Opening home does not overwrite the saved exploration or
load its corpus. Explicit view/focus/companion links open their destinations.

The local companion serves the same app and publishes session changes through
Server-Sent Events. A companion launch link attaches automatically; subsequent
agent operations redraw the page. Its unpredictable token is
saved in tab-scoped session storage and removed from the address bar after
attachment. A bare reload offers **Reconnect agent**, rather than reconnecting
without an explicit action. Disconnect clears it. After a paint opportunity, the browser
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
uncompressed frozen assets on the first native query. A progress message remains visible;
loading, indexing and subsequent computations run in a module Web Worker to
keep the page responsive. Browser/edge HTTP caches may reduce repeat transfers.
The frontend uses no application runtime packages or remote model calls. Optional
stored-view sharing adds bounded storage validation and admission on a Worker;
it never computes the scientific view. The static preview does not emulate that
API. Use the local Worker tests for storage behavior and file import for a static
preview. [Storage contract and activation](stored-views-operations.md).

`scripts/build-site.mjs` copies only explicit app/engine/data/skill/schema/product
documentation inputs into `dist/`; original prompts, notebooks and release
planning documents are excluded. `check:site` validates shard hashes, product
links, selective Worker routing and asset sizes. The native Node tests also
exercise 404 responses for retired routes. Browser QA is a separate integration
gate: Node HTTP checks do not establish rendering or interaction correctness.

## Deployment and rollback

`wrangler.toml` keeps the existing `eigenquestions` Worker name and
`eigenquestions.com/*` route. Static assets are served directly; only
`/api/views` and `/api/views/*` require Worker execution. The default profile has
no storage bindings and reports 503 when asked to save or fetch a stored view.
File import and the static explorer remain usable before storage activation.
The separate `wrangler.views.toml` profile adds a dedicated R2 bucket and a small
SQLite Durable Object for admission. Neither profile has a D1 binding.
Unknown paths return the new 404 page;
there is no SPA fallback exposing a misleading successful old API path.
The old D1 database is left intact. Former voting, submissions, leaderboard,
quiz, taste and fixed-tree pages are not present in the build.

GitHub Actions validates and publishes the frontend and bounded API handler on
authorized pushes to `main`, using the repository's existing Cloudflare secrets.
The repository variable `ENABLE_STORED_VIEWS=true` selects the activated profile
on every subsequent deployment; without it, the unbound profile is selected.
Provisioning, quota review and a real account CPU test remain explicit activation
steps in the [operations guide](stored-views-operations.md). The coordinator owns
release. Stop uploads with `VIEW_UPLOADS_ENABLED=false` in the activated profile
while retaining its storage bindings, so existing reads continue.
`npm run deploy:check` performs local build/validation and Wrangler dry-run only.
It does not establish live-domain behavior or account permissions.

The old application is recoverable from Git baseline
`9b7305541ca18ffd34bbe3786ee0cce75dea5633`. Rollback should restore its source,
lockfile and deployment configuration together. Do not mutate or recreate the
database as a side effect of source rollback. After stored views are activated,
retain their R2 bucket and budget namespace during source rollback; removing
bindings disables existing link reads and is not a write-only pause.

Hosting follows Cloudflare's [static assets configuration](https://developers.cloudflare.com/workers/static-assets/binding/)
and [limits](https://developers.cloudflare.com/workers/platform/limits/): one
asset collection, at most 25 MiB per file, and a conservative 20,000-file build
limit. Existing Wrangler 4.95.0 is pinned explicitly. Current npm audit reports
development-tool transitive advisories in that version; none of those packages
ship in the public static runtime. A tooling upgrade is separate from this
hosting migration and should rerun the packaging checks.
