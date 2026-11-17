# Final frozen-data acceptance allocation

Prepared, not launched. This reuses QA23's browser/MCP core and the existing passive agent observer. The final geometry handoff, accounting receipt and bound cases are still required. There is no new navigation service, model campaign or deployment step.

The scientific gate accounts for every source and keeps unresolved identity as an explicit discoverable facet with zero semantic H mass and a reason. It does not force a home. Rendered access reachability and the narrower DAG are separate checks. The final compiler supplies the accounting receipt; this runner verifies its exact bytes rather than inferring scientific completion.

The application must be a complete pinned Git archive plus a declared runtime/data overlay, not a handpicked checker dependency subset. `final-input.json` lists archive hashes and every member's path/bytes/hash, the version directory, exact manifest hash, accounting-receipt path/hash, and external assets from the final `asset-plan.json`. The external source-context pack is already on authorized Randall scratch. Keep its private source paths out of published files. `stage.py` checks all inputs while unpacking/copying once into node-local temporary storage; build and browser execution remain there. Reports and screenshots are compact shared-scratch outputs. No repeated source-pack copy or hash walk is added beyond the build's required integrity checks.

After the full handoff and root gate, bind `cases.json` to the exact manifest, overview entry/portal/click target and scientific routes, then seal the complete repository plus declared delivery files:

```sh
python3 research/q025/integration/final-acceptance/prepare.py \
  --candidate "$FINAL_PACKAGE" --cases "$FROZEN_CASES" \
  --accounting "$FINAL_ACCOUNTING_RECEIPT" --output "$NEW_QA_ENVELOPE" \
  --commit "$FROZEN_COMMIT" --manifest-sha "$FINAL_MANIFEST_SHA256" \
  --with-observer
```

The packager rejects partial packages, mismatched cases and uncommitted application changes. It uploads no duplicate source-context pack: those exact files are verified once while copied from the existing scratch location. Transfer the resulting envelope through the established SSH/rsync connection, verify its hashes, then submit:

```sh
# On the existing authorized cluster connection; paths bound to the frozen receipt.
sbatch --export=ALL,Q025_RUN_DIR="$FROZEN_RUN_DIRECTORY" \
  --output="$FROZEN_RUN_DIRECTORY/slurm-%j.out" \
  --error="$FROZEN_RUN_DIRECTORY/slurm-%j.err" \
  "$FROZEN_RUN_DIRECTORY/run.sbatch"
```

The allocation is four CPUs, 16GB, 45 minutes in `randall_lab`, within the existing authorization. It uses `$SLURM_TMPDIR` or a private `/tmp` directory and preserves compact failure receipts. No owner browser is used.

The `phases` list uses the existing argument contracts:

- `research/q025/integration/final-acceptance/browser.py`, output `browser`, args `['--cases','{PROJECT}/research/q025/integration/final-acceptance/cases.json']`.
- `research/q025/integration/agent-browser-observer.py`, output `observer`, args `['--atlas','{ATLAS}','--minutes','30']`.
- After publication, `research/q025/integration/public-bridge-acceptance.py` in separate default and consent phases, with `--atlas {ATLAS}`, a frozen real `--destination`, and the corresponding `--permission-mode`. Only the default phase may record a policy failure and continue, with its nonzero exit preserved in `phase-results.json`.
- The public independent-agent observer is a separate phase/allocation using `--public-origin https://eigenquestions.com --permission-mode consent` when normal scoped consent is needed. Default-policy behavior remains its own result.

The 10-check browser core is inherited from passing QA23, now parameterized for final cases and supplemented by the actual overview tab: all17 field controls and the fixed classification graph, a detailed Swampland zoom and plotted-marker click, plus desktop/mobile screenshots. The final handoff binds the real detail entry and target; no fake coordinates or arbitrary depth are supplied. Bind the actual broad→KK production→threshold→linear routes, canonical aliases, largest incident collection, scientific preview, BH→RG application route and exact reviewed source-method endpoint. No IDs are supplied to the fresh agent. Complete the final membership/filter, contribution-only, path/Back/replay, note, fine-URL/static-discovery and presentation checks from `accepted-release-path.md` on that same frozen package; the core alone is not the whole acceptance claim.

The observer sends no navigation commands. Root starts fresh Astra contexts only after `observer/ready.json` reports actual render acknowledgement; use the exact `agent-run.json` paths and CLI wrapper in `agent-acceptance-plan.md`. Each agent reads the portable skill, captures revision before interpretation, chooses destinations from actual tools and verifies the rendered acknowledgement. Stop through `observer/stop.json`. Agent transcripts, scripted MCP checks and browser screenshots have separate evidential meanings.

Current preparation checks: three ingress tests (accounted unresolved facets, partial/home mismatch rejection, archive integrity/path rejection), Python syntax and shell syntax. The new overview check is prepared but not yet executed. QA23's original scripts and receipts remain unchanged. A final frozen-input preflight must validate archive closure, all cases/route proofs and the final asset envelope before submission. No final success is claimed by preparation.

The final cases also bind one approved `compound` placement: `destinationId`, `unitId`, exact `targetCoverage`, full `sourceText` and its pinned `sourceOffset` in the default membership ordering. Preflight chooses a mapped home where that unit is in the visible source sample. The added check compares the unchanged source/map in MCP and the browser, checks the concise notice and initially collapsed provenance, and saves `compound-source-desktop.png`. This is a scripted coverage check, not an additional scientific review or fresh-agent routing hint. It has not run before the final data freeze.

For the dated final package, supply geometry's final case wrapper explicitly:

```sh
node research/q025/integration/final-acceptance/preflight-cases.mjs \
  "$FINAL_PACKAGE" "$NEW_PREFLIGHT_DIRECTORY" \
  research/q025/assembly/final-release-v1/acceptance-cases.json
```

This binds the unchanged route fixtures plus the six post-test source notices to
the actual new manifest. The final browser pass checks one supplied notice and its
unchanged reason in the initially collapsed placement disclosure, saving
`placement-notice-desktop.png`. It does not interpret these scripted fixtures as a
new independent routing test or supply them to a fresh navigator.
