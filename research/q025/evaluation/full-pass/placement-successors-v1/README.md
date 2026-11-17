# Unstarted placement successor

READY for root verification, with zero native starts. This explicit successor contains exactly the 140 never-started requests left in the paused original continuation: 67 new proposal/challenge pairs plus six independent challenges using completed, hash-pinned original proposals. The already completed pair is not repeated. The two failed proposals and their blocked challenges remain excluded for a separate bounded tail-recovery queue. Original jobs, requests, receipts and states are unchanged.

The scientific validator is imported unchanged from frozen placement-continuation-v1. The sole representation change allows `revisesRef` to be null or omitted for an explicitly new scope; normalization records that marker as the old empty no-revision marker. It never infers a revised target. A real revision still requires its exact nonempty q*/n* reference. Unknown targets, overwritten IDs, duplicate definitions, missing rows/assessments, changed retained allocations, invalid weights and incomplete coverage remain rejected. Raw replies retain their original representation; normalization receipts list every marker derivation. Evaluation independently read and approved this narrow change.

Every source view, both historical annotations, scope definition and canonical binding is reused unchanged. Preparation verified 2,777 files. Exactly 73 source families remain here; all original state outcomes are recorded in partition.json. This queue admits no science. New scopes still require the global inventory lookup; compound unions and revised/unresolved placements remain coordinator exceptions.

The inherited dispatcher uses source-only Astra xhigh ephemeral threads, a single 120,000-character total reply budget, no per-string limits, UTF-8-safe framing, outside-string whitespace guard, 30-minute deadline, shared quota pause and no automatic retries. Initial concurrency is 8; root may raise it to 32 only within the combined 48-task ceiling. Original control must remain disabled. Before every start, request verification rejects a resumed original pool or an original job that acquired a dispatch file, preventing duplicate execution.

All 140 jobs were synthetically materialized without native calls. Every new proposal dependency uses the maximum permitted 120,000-character prior reply; the six completed external proposals use their exact immutable actual replies. Worst conservative combined context is 164,761 tokens against the 220,000 guard. All 18 Python and 8 Node checks pass, plus request verification. The matching whitespace stop before revisesRef motivated the explicit representation, but causality is not proven and no guaranteed model completion is claimed.

Verify from repository root:

```sh
python3 -m unittest discover -s research/q025/evaluation/full-pass/placement-successors-v1 -p 'test_*.py'
node --test research/q025/evaluation/full-pass/placement-successors-v1/runner.test.mjs
node research/q025/evaluation/full-pass/placement-successors-v1/runner.mjs --verify
```

Only root launches after verifying READY, quota, original-pool pause and combined concurrency:

```sh
node research/q025/evaluation/full-pass/placement-successors-v1/runner.mjs --run --enable
```

Private runtime remains under ignored `native-local/placement-successors-v1`. Its control starts disabled with maxActive 8. Source calls are never launched by this preparation. Failed tail completions are not represented as success and do not block this independent unstarted queue.
