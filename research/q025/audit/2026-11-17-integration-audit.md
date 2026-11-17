# Q-025 independent integration audit

Auditor: `/root/atlas_integration_audit`. Worktree: `agent/atlas-integration-q025`.
HEAD observed during audit: `041f808c88a718d8e6e3fc0a76a59b09ddcd9a40`.
Runtime files were in progress; the integration owner repaired the findings below
during this review. The auditor changed only this report, made no commits, and
did not read reserved semantic holdout material or contact hosting services.

Read: `AGENTS.md`, notebook Now/latest Q-025 entries, delivery requirements, lazy
contract, relevant assembler/runtime/controller/static-discovery code, and existing
synthetic fixtures. This is a code and executable synthetic audit, not certification
of the unaccepted full-scale atlas or a new real-browser acceptance run.

## Four verified findings, in priority order

1. **Cold local-agent connection reads omitted available destinations.**
   `lib/protocol/runtime.mjs`, `connections`, originally returned the current
   in-memory adjacency without preparing the requested destination. With the
   existing `lazy-atlas.test.mjs` fixture, prepare only the root, construct a
   runtime, and request `connections({destinationId:'coarse'})`: total was **1**.
   After `prepareDestination('coarse')`, the identical read returned **2**.
   A direct cold fine-source ID instead threw `unknown destination`. The browser
   API prepared the target correctly, so local MCP/CLI and browser reads disagreed
   and were cache-dependent. The owner added preparation and bridge awaiting.
   **Auditor verification:** the new cold coarse/fine, repeat-read, unchanged-session
   regression passes. Real MCP-to-browser QA on the repaired snapshot remains due.

2. **Required reading qualifications were absent from the browser panel.**
   Accepted assembly requires and exports `readingCoverage`
   (`research/q025/assembly/accepted.mjs`), but `web/atlas-panel.mjs` rendered only
   `readingLimit`. Rendering an accepted-style synthetic record with
   `readingCoverage: 'Only descriptions were read; derivation in section 4 remains unread.'`
   produced its scientific status but no qualification text. Static pages already
   supported both fields. Preview cards using `readingLimit` concealed the mismatch.
   The owner now renders both forms without duplicate text.
   **Auditor verification:** the focused DOM regression passes. Check actual
   accepted records visually before release; reading limits must remain visible.

3. **A partial declared atlas could produce a successful static build.**
   `scripts/build-site.mjs` caught any `ENOENT` around the entire atlas-generation
   block, treating a missing required file like an absent optional installation.
   In a temporary tree, an index declaring `fixture/v1` with no manifest exited
   **0**, while `/atlas/index.html` claimed no catalog was installed. A second
   synthetic reproduction supplied a metadata root, then a child source with a
   declared but missing `ab` source-context bucket: build still exited **0**,
   generated `root.html`, omitted `child.html`, and retained the false index page.
   The atlas-specific `check:site` checks require the entrance, manifest and catalog,
   so that second partial state was not covered by those checks. This is a
   demonstrated build failure mode, not a claim that a broken release was deployed.
   The owner narrowed optional absence handling to the top-level atlas index.
   **Auditor verification:** rerunning the missing-manifest reproduction now exits
   **1** with an explicit `ENOENT` manifest error. The updated static-discovery
   test also rejects missing context buckets and manifests. The owner additionally
   added context-file checksum checks and requires every static destination page
   in `site-check`; this latter full-site path was inspected but not executed by
   this auditor. Final installed assets still need the complete build/site checks.

4. **Private-note export failed precisely when its fallback was needed.**
   `web/atlas-panel.mjs` exported `download(..., save())`; `save()` first wrote
   `localStorage`. With `setItem` throwing `QuotaExceededError`, the input handler
   promised that the buffered edit could be exported, but clicking Export note
   raised the same error and created no download. This was reproduced with the
   actual module and a minimal DOM stub. The owner separated capture from durable
   persistence so export uses the buffered note independently.
   **Auditor verification:** the storage-failure/export DOM regression passes.
   Real-browser note export/import and exclusion from shared views remain release
   checks; the audit used only synthetic private-note text.

## Verification and scope

Auditor rerun after the owner's edits:

```sh
node --test tests/integration/lazy-atlas.test.mjs \
  tests/integration/static-atlas-discovery.test.mjs \
  tests/integration/work-note-fallback.test.mjs
```

Result: **8 passed, 0 failed**. The missing-declared-manifest check was also rerun
independently in a disposable temporary tree, with the expected nonzero exit.
These are verified local repairs, not merely reported fixes. No claim is made
that the next frozen QA archive or public browser has passed them yet.

After the owner's additional build/checker changes, the same targeted suite was
rerun: **8/8 passed again**. Hashes below were identical before and after that
run. They identify the checked working files, rather than implying that HEAD
alone contains the fixes. Hashing `site-check.mjs` does not mean its full check
was executed by the auditor.

```text
03c806ac40159cf7102142266e6c462742fe7063df79b54fc12975714460267a lib/protocol/runtime.mjs
df61f4520d788c512e52e9895313c4f358637459ab43810982fce2f1e5b0be92 lib/protocol/bridge.mjs
d06f3339a277fa467b4194cf5982c75ad8d853088a843d2fe53f4f4877d3e54b web/atlas-panel.mjs
64af4c544c6c7b00973094c2c88c7576943c58356f21362001dd8193bd7a453a scripts/build-site.mjs
9a3f68e0297ccbe149ac7364c7db4618654454cb768e3f8d2d05b92affca713e scripts/site-check.mjs
8601a1b64150bbab3e2f1d5310369ab966ac23547f0fe5064f70c3a6971ed27b tests/integration/lazy-atlas.test.mjs
a827c8bb7432f56bbee3d41ffea271502ef5cc6d646bcdafe23581c39a522f2a tests/integration/static-atlas-discovery.test.mjs
96de19c17c7115e1e4c40010570c1aaf36e84feaba9cc7e8ffe1b003a7bd4659 tests/integration/work-note-fallback.test.mjs
```

The inspected design keeps source-question access separate from canonical
equivalence: fine source IDs remain exact extracted facets, candidate groups do
not create aliases automatically, same-paper methods remain contextual, and
scientific source edges retain a separate layer. The lazy implementation uses
pinned default samples and exact counts; complete memberships precede filtering
or paging. Synthetic tests cover route/cache invariance, corruption rejection and
stale-action rejection. Those mechanisms do not establish final scientific
coverage, useful cross-field routes, or equivalence of differently worded questions.

The accepted full scientific atlas is not installed. Independent click/agent
journeys, including cross-field return paths and changed-premise distinctions,
must be repeated on accepted data. Static discovery, compact URL reload/Back,
manual capsule continuity, visible reading limits, and private-note export belong
in that release gate. Hosted arbitrary-view durable save/open remains blocked and
must not be described as activated. The already-known QA06 hidden-summary
assertion and QA07 hydration/route-guard work were not counted as new findings.
