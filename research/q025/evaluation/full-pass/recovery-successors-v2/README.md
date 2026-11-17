# Q-025 recovery successors v2 — ready for root verification

This additive campaign repairs two new terminal failures without changing v1 or
the original leaf/parent campaigns. It contains **15 native turns**: one challenge
of an already complete 51-unit proposal, one missing-component completion and
challenge for a 32-unit proposal, and six blocked parent proposal/challenge pairs.
Two jobs are ready now; thirteen wait for exact dependencies. No models were
launched during preparation. Root controls launch and the global limit of 48.

The v1 `ce36cae0274019373c8a` completion failed only because three assessments of
earlier empty lists had empty scientific-reference arrays. The reconstructed
51-unit proposal passes the unchanged scientific validator. All 27 earlier
variant assessments are retained. The three empty `identityGroups`, `cardReviews`
and `groupReviews` arrays, together with the absence of input prior cards/groups,
are now cited as **artifact structure**. The derived record pins the actual input,
prefix and raw reply paths/hashes and exact field paths. It invents no primary
citation and changes no scientific field. Empty refs remain invalid for other
variants or material-conflict judgments. The original failure and raw reply
remain byte-for-byte unchanged. Only a new independent challenge is needed.

The original leaf `27b96c79f67176367791` reached its 1,800-second deadline in a
whitespace loop: 86,363 retained characters, one JSON attempt, fourteen complete
values through its partial first card. No complete unit assessment was emitted.
The successor locks those values and completes only missing components for all
32 units and 24 supplied excerpts, then challenges independently. The new
outside-string whitespace guard detects the original retained loop in a test.

The six replacement parent families are:

- `ce36… → 8faef27ce1cad100b7fe → 6695e767a08bf35f78fe → c8776465ed44d9e65c4c`
- `27b9… → e8d0c428c737a887a324 → 0b9505226b0fcc606395 → c8776465ed44d9e65c4c`
- `c8776465ed44d9e65c4c → 5eef7911f1a80cb73c18`

Every unaffected child uses its existing latest lineage, including ongoing v1
successors. Completed readings are not rerun. Failed or missing children block
their ancestors; they are never omitted from coverage. Exact dependencies and
immutable inputs are in [manifest.json](manifest.json).

Eight Python and six Node tests pass. Both currently ready packets were compiled
in isolated preflight directories through the real dispatch materializer, with
every supplied excerpt and archived source file hash verified. Combined context
estimates are 148,136 tokens for the 51-unit challenge and 95,570 for the 32-unit
completion. Both include the exact prompt/schema, all 120,000 possible response
characters at three characters per token, and 16,000 reasoning/protocol tokens.
The limit remains 220,000. Future dependency-bearing packets are measured only
after their actual child receipts exist. See [preflight-run-001.json](preflight-run-001.json).

Limits are unchanged: source-only Astra xhigh, read-only sandbox, 1,800 seconds,
120,000 total output characters, no per-string cap, 4,096 consecutive outside-string
whitespace characters, no automatic retries. Explicit quota exhaustion pauses
new starts through the shared marker. This campaign is disabled by default with
two active turns initially and an authorized maximum of eight; root must account
for other campaigns before raising that value. Deterministic validation and
typed artifact inspection do not constitute scientific admission.

```sh
node research/q025/evaluation/full-pass/recovery-successors-v2/runner.mjs --verify
python3 -m unittest discover -s research/q025/evaluation/full-pass/recovery-successors-v2 -p 'test_*.py' -v
node --test research/q025/evaluation/full-pass/recovery-successors-v2/runner.test.mjs
# Root only, after checking READY.json and total active concurrency:
node research/q025/evaluation/full-pass/recovery-successors-v2/runner.mjs --run --enable
```

Do not rerun preparation after launch or relaunch existing state. Raw source text,
replies and execution configuration remain private in ignored `native-local`.
Public checkpoint files contain code, hashes and bounded evidence only. Existing
campaigns continue independently; [health-snapshot.json](health-snapshot.json)
records the final monitoring observation rather than a promise of future success.
