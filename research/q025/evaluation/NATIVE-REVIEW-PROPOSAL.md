# Isolated Q-025 source review proposal

No native request has been launched by this agent. The old graphdesign runner, queues, credentials, controls and snapshots are unchanged.

The existing `components/graph_design_review/shared-runner.mjs` uses one native app-server and separate ephemeral threads, pins model/effort to request metadata, supplies frozen prompt/schema/source images, records events and outputs per job, and rejects attempted tool use. It currently hardcodes the upstream root and accepts only the `graphdesign` namespace. Running it unchanged would mutate the completed round. Copying it is not sufficient until those roots and namespace guards are changed and tested.

Use a new root-owned `research/q025/native-review/` runtime with a strict `q025` namespace, source packets under immutable hash names, a separate inbox/claimed/status/control directory and job output directories. Permit reads of the frozen upstream only. Keep source-only policy, model/effort check, per-job deadlines/output bounds, event logs and explicit terminal status. Log tool-use attempts as failure; detection is not a guarantee a capability was absent. Existing account access stays in the native account helper; do not serialize credentials or environment into receipts. Root controls launch and resource limits.

## Bounded batch

Prepare eight candidate families, prioritizing the giant compactification leaf's distinct questions, plus weak ordinary-exploration regions. Each family gets three separately executed stages:

1. **Propose:** Read eight paper cases: three central, two boundary, two strong excluded neighbors, one paper-balanced random. Source roles guide sampling but are not truth labels. Return a common question/scope, up to 1–15 justified directions, overlap or split proposals, per-sample dispositions, precise evidence IDs and missing context. A mixed family may legitimately fail to support one useful card.
2. **Challenge:** A separate Astra xhigh thread receives the same pinned evidence and proposal. Test its most consequential boundary, regime, identity and relation assumptions. Record disagreements rather than silently rewrite source content. This is proposal-visible review, not blind adjudication.
3. **Unused-source check:** Six papers not used in the two stages, earlier 45-topic proposal/challenge/fresh samples, development journeys, or tuning. Give the candidate scope plus original source excerpts without original cluster assignment or expected disposition. Ask what belongs, what is missing, and whether the next choices are scientifically informative.

Maximum planned batch: 24 requests and 112 paper-case slots (eight original plus six new per family). Repeated papers across families remain identified, so this is not 112 independent papers. Start with two mixed compactification families (six requests). Root reviews integrity, reading sufficiency, disagreement and readability before releasing the remaining eighteen. No automatic retries or prompt paraphrase fishing; preserve failed outputs and log any materially revised question as a new lineage.

The first six compactification scope axes are effective-action reduction; flux-vacuum/source obstructions; stabilization/stability/control; asymptotic moduli limits/towers; geometric gauge realization/anomaly conditions; and phenomenological sectors/couplings. They are proposed lenses with overlaps, not six forced disjoint classifier labels. Prior evidence is in `ordinary-exploration.json` O01–O03 and the precise scope critique in `geometry-critique.md`.

## Receipt and acceptance

Pin source PDF hashes, original evidence IDs, sample/unit identities, actual supplied/omitted pages, image bytes if used, candidate membership/definition hash, prompt/schema bytes, native model/effort/thread/turn, proposal/challenge hashes, complete status, exposure and reading limits. No reviewer can convert geometric affinity into a scientific implication. Admit only the scope actually supported; keep unresolved proposed changes visible. Fresh failure is evidence to revise scope or construction, not a reason to discard that example.

This batch supplies sampled scientific review and readable cards. It cannot certify all 6,477 papers, canonicalize every question globally, or replace full graph coverage tests. The 12 visible journeys and eight ordinary probes are development/challenge material; reserve a final fresh set until candidate selection is frozen.
