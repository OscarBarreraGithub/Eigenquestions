# Independent recheck of the four semantic repairs

All four original findings are repaired in the tested code. No additional semantic failure was reproduced in this bounded recheck. The original `REPORT.md`, `probes.mjs`, `probe-results.json` and baseline test output remain unchanged. Only new audit evidence was written here; no production or owner files were edited.

The unchanged original probes now reject the inherited canonical-identity contradiction, reject disjoint groups sharing one canonical destination, and reject the primary reference without an exact resolved locator. The contribution-only question passes assembly, logical validation, partition validation and lazy preparation with one typed contribution, zero primary members and zero Q allocation error. Results are in [repair-verification-probes.json](repair-verification-probes.json); a later rerun against the current runtime is preserved separately in [repair-current-probes.json](repair-current-probes.json). Their six original-checkpoint hash mismatches are expected repair changes, not edits to the frozen checkpoint.

All 13 owned files in the repair manifest matched their byte counts and hashes. The manifest itself matched `213a8c01419a0c5aa23d73d07c92c19e8ceea2ebdddbb28d1afdc0d06107053f`. During this recheck, the product owner added the root-requested read-only contribution collection API. The runtime therefore advanced from the repair manifest's `a2881945…` to `695eb4a412dc3ffb6b4bf672be6abcfc770f03b8df47b0ae1ac0f94875ea74c0`; the external contribution regression advanced to `9897edbc29862ac199980107cd5f6f7c33c0cd31d15ef9e3e2be982abe47511e`. Those two external pin differences are recorded explicitly in [repair-independent-results.json](repair-independent-results.json). They do not affect the unchanged 13-file assembly repair verification. The UI file exercised by the current rendering test has SHA-256 `16147cec31c271548177f8468af2201491957fefd27fece27c06c04ec8870f1f`.

Additional independent checks in [repair-independent-checks.mjs](repair-independent-checks.mjs) verified:

- Ten order-independent cases where two disjoint submitted groups together complete a positive path across a recorded `different`, `specializes`, `shared_parent_distinct`, `unresolved`, or changed-premise comparison constraint. Every inconsistent admission was rejected, with both group IDs present in the conflict explanation.
- A common-target link does not join two explicit canonical groups. The distinct destinations remain separate even with a retained cross-group distinction, and automatic unions remain zero.
- A conflict in an unrelated positive component remains visible without blocking a disjoint consistent admitted group.
- Combining all proposed members into one complete destination group still rejects a known specialization; the one-group-per-destination rule cannot bypass the underlying constraint.
- The 13 already-inspected, unsealed primary locators resolve against five pinned archive files and the source-context registry. Only locator fingerprints and counts are emitted; no raw primary text is exported. This verifies exact locator identity, not scientific relevance or a full-paper reading.

The focused suite passed all 48 assembly tests and both contribution integration/rendering tests, recorded in [repair-verification-tests.txt](repair-verification-tests.txt). Against the current `695eb4a4…` runtime, all 20 prepared/lazy/contribution/rendering tests passed, recorded in [repair-current-runtime-tests.txt](repair-current-runtime-tests.txt). These checks establish that a zero-membership question retains source evidence and typed contributions, contribution paging hydrates descriptions without mutating session/revision, default membership and USING totals remain zero, and membership filters cannot be applied to the contribution collection. Positive counts or contradictory nonempty samples still require a membership descriptor. The rendering check uses a DOM mock and verifies bounded contribution pages, role/qualification text and source-context callbacks; it is not a real-browser acceptance test.

Reproduce from the repository root:

```sh
node research/q025/audit/semantic-v1/probes.mjs
node research/q025/audit/semantic-v1/repair-independent-checks.mjs
node --test research/q025/assembly/*.test.mjs tests/integration/contribution-only-destination.test.mjs tests/integration/source-contributions-display.test.mjs
node --test tests/integration/prepared-atlas.test.mjs tests/integration/lazy-atlas.test.mjs tests/integration/contribution-only-destination.test.mjs tests/integration/source-contributions-display.test.mjs
```

The original fixture/admission limits still apply: synthetic semantic probes bypass external top-level admission receipts while exercising the repaired component gates. No complete production CLI assembly or accepted scientific atlas was created. No sealed evidence, new private review packet, browser, cluster, model call, public site or final scientific geometry was inspected. The production code now requires `assets.sourceArchiveRoot` when primary references need resolution; this was checked in the CLI implementation and actual locator verifier, not through a complete real assembly packet.
