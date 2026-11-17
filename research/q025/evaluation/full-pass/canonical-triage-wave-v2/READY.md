# Ready for root launch

The 117 single-pass requests use the validated screening contract, with an explicit scope-level evidence limit. Every view has at most 40 scopes and 100 comparisons. The exact 375 completed pilot comparisons are excluded; 18 prior rich-pilot nominations remain separately accounted. The continuation covers 7,907 unique pending comparisons and 7,923 original workload IDs from the combined old and registry-v4 inventory.

Each supplied scientific definition and whole source description was checked against its pinned sidecar, and every comparison against its exact source-scope endpoints. Reserved-paper descriptions remain excluded. Per-unit attribution notes and primary excerpts are deliberately absent; downstream decision packets retrieve them only when needed. Screening admits no scientific scope, identity, relation or source home.

Actual preflight materialized all 117 prompts in a separate private directory. The largest prompt is 283,186 characters including instructions; the largest conservative combined bound is 151,039 tokens, including the 120,000-character response allowance and 16,000 reasoning/protocol tokens. The default 272,000-token window and 220,000 dispatch guard are retained. The response limit has one request-rendered source; no per-string caps apply. Streaming output, failed receipts, cancellation, quota supervision and stop-on-repeated-validation-failure behavior are retained from the validated pilot. No automatic scientific retries or quota recovery are inferred.

The control starts disabled at eight workers, with an authorized ceiling of 32. Root may increase to 24 after valid new results and controls the combined account concurrency. No model has been launched by preparation.

```sh
python3 -m unittest discover -s research/q025/evaluation/full-pass/canonical-triage-wave-v2 -p 'test_*.py'
node --test research/q025/evaluation/full-pass/canonical-triage-wave-v2/runner.test.mjs
node research/q025/evaluation/full-pass/canonical-triage-wave-v2/runner.mjs --verify
node research/q025/evaluation/full-pass/canonical-triage-wave-v2/runner.mjs --run --enable
```

Five Python tests, three Node tests and request verification pass. Runtime is `full-pass/native-local/canonical-triage-wave-v2/`; its `state.json`, `status.json`, `control.json`, per-job receipts and bounded private quota records are the supervision surfaces. The manifest and `READY.json` pin the selected index and public implementation. The compiler uses only its 117 listed families, never a directory glob containing diagnostic packets.
