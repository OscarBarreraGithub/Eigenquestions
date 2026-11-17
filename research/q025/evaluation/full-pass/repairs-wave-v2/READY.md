Sixteen source-only Astra xhigh calls are prepared: eight proposal/challenge pairs cover exactly the46 remaining flagged cases. Batch sizes are8,4,7,3,6,6,8,4. The12 completed pilot cases are excluded. Each case retains original text, exact source locators, scope context and prior proposal/challenge hashes. No original field is rewritten in place.

The proven clause schema distinguishes supported clarification from an asserted missing fragment, preserves annotation-only versus premise/scope change, and requires independent case-by-case challenge. No string caps apply. The whole-response40k budget is rendered from each request, with a single-budget consistency check. Actual source-file/text hashes were preflighted; worst dependent context estimate remains below220k.

Five Python and two Node tests pass; `--verify` passes. Root launch:

```
node research/q025/evaluation/full-pass/repairs-wave-v2/runner.mjs --run --enable
```

Private runtime: `full-pass/native-local/clauses-wave-v2/`. Maximum active5, starts≤6/minute, minimum interval5seconds,30minute per-call deadline, no automatic retries. Root controls combined native concurrency and monitors quota. No model calls were started during preparation.
