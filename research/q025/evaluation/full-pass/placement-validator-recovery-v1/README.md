# One validator-timeout successor

The exact completed proposal for placement family 0041 revalidates against the unchanged scientific validator in under one millisecond: 31 placements, no new scopes. Its original failure was `spawnSync python3 ETIMEDOUT`. The original failed receipt, raw reply and blocked challenge remain unchanged. A separate derived proposal receipt records the deterministic validation, identical logical content and original native failure; it does not claim another reading or scientific admission.

Only one independent challenge is prepared. It receives the exact original scientific packet and derived completed proposal through an explicit hash-bound dependency. Source descriptions, both old annotations, scope definitions and all referenced input receipts remain unchanged. No proposal is repeated. Source-only Astra xhigh, a single 120,000-character whole reply limit, no string caps, 30-minute deadline, lossless framing, shared quota pause and no automatic retries are inherited unchanged. Initial/maximum concurrency is one, within root's combined 48 ceiling.

Four Python tests confirm exact validator parity, full source coverage, unknown-target rejection and preserved failure lineage. Eight Node checks cover request/pin verification, framing, whitespace, quota, concurrency and budget guards. The exact dependent packet plus maximum challenge output estimates 118,206 tokens against 220,000; no model call occurred during preparation.

From repository root:

```sh
python3 -m unittest discover -s research/q025/evaluation/full-pass/placement-validator-recovery-v1 -p 'test_*.py'
node --test research/q025/evaluation/full-pass/placement-validator-recovery-v1/runner.test.mjs
node research/q025/evaluation/full-pass/placement-validator-recovery-v1/runner.mjs --verify
```

Only root launches after checking READY and shared concurrency:

```sh
node research/q025/evaluation/full-pass/placement-validator-recovery-v1/runner.mjs --run --enable
```

Private runtime and adopted full artifacts remain under the matching ignored native-local lane. This successor cannot resume the paused original pool or redispatch an original request.
