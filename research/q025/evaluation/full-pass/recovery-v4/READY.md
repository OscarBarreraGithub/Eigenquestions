# Explicit42-unit recovery

The original proposal failed in a native whitespace loop:120505stream characters,
115056tabs and0of42unit-assessment records. Its complete broad region is only a
proposal. The original failed receipt and partial stream remain immutable. This
separate two-call proposal/challenge campaign uses the exact same source packet;
it does not claim a deterministic recovery of missing science or a successful
original turn.

The new contract retains strict source/unit/type coverage, removes per-string
caps, requests compact JSON including every required field, and preserves streamed
output. A new early guard stops more than4096consecutive literal whitespace
characters OUTSIDE JSON strings. It respects string/escape state across deltas;
normal formatted JSON and escaped or literal source-string whitespace are not
classified as the failure. No automatic retry follows.

Two Python tests and three Node tests pass; both requests verify. Actual proposal
preflight conserves all42rows. Root launch:
`node research/q025/evaluation/full-pass/recovery-v4/runner.mjs --run --enable`

Runtime: `full-pass/native-local/leaf-recovery-v4/`, initial1maximum2.

Eight old parent jobs (four parent pairs) are already explicitly blocked along
73840db6800ed57ab471 → e216581a59d87c4cff7a → b7f81485b7d06aed5b64 →
5eef7911f1a80cb73c18. Their historical states will not be edited. After a valid
recovery pair, a small separate parent continuation will pin this challenge as
the replacement dependency, reuse all completed unaffected sibling artifacts,
and run only those four missing parent pairs in dependency order. No completed
parent is reread, no source member is omitted, and no failed receipt becomes valid.
