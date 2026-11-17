# Q-025 recovery successors v1 — ready for root verification

This separate lineage preserves the five failed leaf turns, two failed parent
turns, and all original failed/blocked campaign states. Preparation makes no model
calls. It changes neither the scientific admission rules nor the frozen runners.
Raw source packets, native replies and execution configuration remain in ignored
`full-pass/native-local/recovery-successors-v1/`; only code, hashes and receipts
are public here.

There are **34 new source-only Astra xhigh turns**: two challenge-only turns,
three missing-component completions with independent challenges, and proposal /
challenge pairs for 13 blocked ancestor families. The partial parent recovery
makes 14 parent families total. Six jobs are presently materializable; 28 wait
for exact child or proposal receipts. No completed unaffected review is repeated.

| Original failure | Successor |
| --- | --- |
| leaf `55a2311c12b246ddbd15`, validator timeout | Exact complete 32-unit reply revalidates in 0.027 s. New independent challenge only. |
| leaf `90980b7a8339256bfea7`, validator timeout | Exact complete 40-unit reply revalidates in 0.027 s. New independent challenge only. |
| parent `8d2b5fd7cc13cefc77fe`, challenge reference | Reuse complete challenge after registering its single `pf28` citation as the exact supplied historical/rejected prior annotation. Raw reply, original references and factor definition remain unchanged. It is never primary evidence. |
| leaf `54e3e83d0ccbf2700b0f`, interrupted output | Reuse the completed 42-unit `leaf-recovery-v4` pair; no new turn. |
| parent `076a8e988b123c215a92`, whitespace loop | Preserve all 14 complete values, including the complete fields of its partial first card. Complete only the missing content, then challenge. Five contrast units / ten excerpts; inherited descendants are not claimed as reread. |
| leaf `ce36cae0274019373c8a`, output cap | Preserve 31 complete latest unit rows plus the complete fields of row 31, cards and factors. Complete the remaining 20 rows and tail. Review all 27 complete earlier alternatives, then challenge independently. 51 units / 26 excerpts. |
| leaf `ce2e0c80657f40e352ee`, output cap | All 39 latest unit rows, cards, factors, identities and reviews are already complete. Preserve them and 20 complete links; request only the missing tail and all 29 earlier-alternative reviews, then challenge. 39 units / 25 excerpts. |

Earlier complete alternatives remain explicit scientific candidates with source
byte ranges and hashes. A completion cannot overwrite a selected complete value.
Conflicts and unresolved alternatives remain explicit; deterministic derivation
does not admit any question, relation or membership. The prompt represents each
selected value once rather than repeating archival copies. A regression checks
that every locked value and every earlier variant is still visible.

Affected branches, converging on `5eef7911f1a80cb73c18`:

- `54… → 73840… → e216… → b7f8…`; `909… → 3e5e… → b7f8…`;
  `55… → 0f74… → ede3… → b7f8…`.
- `076… → 1732… → 4fde…`; adopted parent `8d2b… → 4fde…`.
- `ce36… → 8fae… → 6695… → c877…`;
  `ce2e… → c0a1… → 6695… → c877…`.
- `b7f8…`, `4fde…` and `c877…` feed the root, which also retains its original
  unaffected fourth child. Exact dependencies and all sibling references are
  in [manifest.json](manifest.json).

Validation: nine Python tests and five Node tests pass. The exact dispatch
materializer successfully compiled six ready prompts in isolated preflight
directories, verified every supplied excerpt and archived source hash, and left
the actual job directories unmaterialized. Their conservative combined context
estimates are **96,053–137,018 tokens**, below the 220,000-token guard. The estimate
includes the exact prompt, exact output schema, all 120,000 response characters
at three characters per token, and 16,000 reasoning/protocol tokens. Future
dependency-bearing prompts remain unmeasured until their actual child receipts
exist; the same hash and budget guards run before each dispatch. See
[preflight-run-002.json](preflight-run-002.json). Run 001 is preserved as earlier
preflight evidence before lossless duplicate-wrapper removal.

Every native turn uses the same 1,800-second deadline, 120,000 total output
characters, no per-string limits, and 4,096 outside-string whitespace guard.
There are no automatic retries. A failed child blocks its ancestors without
omitting coverage. Explicit quota exhaustion immediately writes the shared pause
marker; root acknowledgement is required. Three consecutive contract failures
pause this campaign. The two validator timeouts do not reproduce under isolated
deterministic validation; this is an execution failure observation, not proof of
a particular root cause or a claim of scientific correctness.

Root owns native launch and the total concurrency cap of 48. This campaign is
disabled by default, starts with at most two active turns, and permits at most
eight. Root must account for every other campaign before increasing that value.

```sh
node research/q025/evaluation/full-pass/recovery-successors-v1/runner.mjs --verify
# Root only, after verifying READY.json and global concurrency:
node research/q025/evaluation/full-pass/recovery-successors-v1/runner.mjs --run --enable
```

Do not rerun `prepare.py` after launch or reuse an existing runner state. A new
failure requires a separately inspected successor; originals remain immutable.
The current cohort was checked against the original campaigns immediately before
the READY receipt. The immutable dependency guard also runs before every start.
