# Lab Notebook

## Now

- **Project/question:** Eigenquestions — can a conversation select useful, reproducible local views of a physics graph/vector space, with about five directions at a time?
- **Known:** Real 384-dimensional question/method vectors and graph layers drive contextual navigation. The selected chart shows five dynamic direction-group means; source overlays remain substantially distorted. Context refresh, exact replay and computation identity are implemented. Component/integration checks pass; the old public site remains until release validation.
- **Unfinished/running:** Astra geometry/protocol owners are finishing evidence; the site owner has delivered a stable build. A fresh Astra agent is independently trying the portable skill on an axion journey. Authorized Slurm browser acceptance is being prepared; no Q-001 cluster job submitted yet. Deployment remains pending via the existing GitHub workflow. No owner answer is required.
- **Next:** Save the working prototype checkpoint, run actual MCP → browser acceptance, inspect screenshots and the independent trial, then release after resolving observed defects.
- **Git:** Work on `agent/question-conditioned-navigation`, push checkpoints to `OscarBarreraGithub/Eigenquestions`; release to `main` after validation. Coordinator: `/root`.

## Requests

**Q-001 (summary):** Replace Eigenquestions with a static, conversation-guided physics explorer. An agent navigates the real graph and embeddings through a machine-readable interface; deterministic local code recomputes a question-dependent 2D view and about five next directions. Demonstrate KK towers → dark matter → Dark Dimension, support derivation/phenomenology/recent-work intents, provide portable agent instructions, and iterate under Astra implementation with central integration review. Keep this notebook and verified Git checkpoints. [Original prompt](docs/requests/Q-001-original.md) · [Atomic plan](docs/Q-001-plan.md).

## 2026-11-06 UTC — Q-001: Establish the project and the intended change

**Question.** Is this a deeper fixed hierarchy, or a different navigation model?

**Observation.** The owner explicitly describes a slice that changes with the questions asked, including concepts appearing after a contextual pivot. A precomputed hierarchy alone cannot satisfy that behavior. The local repository was clean at `40b476b`; its configured origin was ahead at `9b7305541ca18ffd34bbe3786ee0cce75dea5633`. The coordinator fast-forwarded to that remote version and created the working branch. Cloudflare configuration points at `eigenquestions.com/*`; pushes to `main` currently deploy through GitHub Actions. No suitable notebook existed.

**Decision/plan.** Preserve the exact request separately, audit an atomic plan, and share one navigation-state/view contract across geometry, agent controls and browser rendering. Use the existing Swampland data as the first corpus. Replace serving behavior when the new static application is verified; preserve the old source in Git and avoid deleting the old database. Astra agents implement; `/root` checks that complete user journeys work and handles integration/release.

**Evidence/resume.** [Requirements and gates](docs/Q-001-plan.md), [existing deployment workflow](.github/workflows/deploy.yml), [hosting configuration](wrangler.toml). Goal created for the full v1 and its public deployment. Next: independent requirement audit and a concrete shared contract.

## 2026-11-06 UTC — Q-001: Dispatch the integrated implementation

**Question.** Can three implementation owners work independently without losing the complete navigation behavior?

**Tried/contributors.** `/root` dispatched Astra xhigh owners for geometry/data, protocol/acceptance, and the static site with the same original prompt and R01–R40 plan. File ownership is disjoint; the protocol owner coordinates a common contract before the interfaces settle. Only the coordinator commits or releases.

**Observed.** Geometry found aligned real MiniLM vectors locally: 8,473 question descriptions and 17,937 method descriptions, each 384-dimensional, with existing graph affinities. Protocol's initial independent reading found coverage for every explicit clause and highlighted several interpretation hazards: “on” versus “using” a concept must change evidence, the five-choice target applies to directions, and a newly salient connection should not be artificially hidden earlier.

**Meaning/next.** Test genuine selection and geometry changes rather than a cosmetic zoom. Compare at least two mathematical constructions before choosing one. Preserve exact source scope and recent-within-corpus dates. The complete clause audit and contract will be linked here when ready; this entry records an initial report, not a completed validation.

## 2026-11-06 UTC — Q-001: Test context rather than a sequence of unrelated searches

**Question.** Does “what if they are dark matter?” retain KK towers, and does the next question about decays retain both?

**Tried/contributors.** Astra geometry ran real-data journeys; Astra protocol specified state transitions; `/root` reviewed their shared behavior. The first weak-centroid approach ranked generic dark-matter results ahead of the desired context and drifted toward generic moduli on the next step. A source-anchor refresh at each refinement and joint query/focus conditioning are being compared. Root also found domain-specific terms inside generic intent priors and requested their removal: a phenomenology intent should not silently inject dark matter into every subject.

**Observed.** The revised trial reported Dark Dimension cosmology and decaying-graviton work among the first results after the dark-matter refinement. That is encouraging, not a completed generalization test. Root separately checked that [Dark Dimension Gravitons as Dark Matter](https://arxiv.org/abs/2209.09249) and [Dark Dimension and Decaying Dark Matter Gravitons](https://arxiv.org/abs/2311.05318) support the scientific connection being used for this journey. Numerical proximity still does not establish a physical implication.

**Meaning/next.** History can stay outside the numerical function only if the current state carries its resolved scientific focus. Backtracking must restore that exact state. Preserve failed rankings, compare chart/grouping alternatives, and evaluate an independent route after the algorithm is fixed. [Shared contract](docs/navigation-contract.md) · [clause audit](docs/requirements-audit.md). Public-origin loopback behavior and local browser updates remain to be tested.

## 2026-11-06 UTC — Q-001: A good-looking projection is not enough

**Question.** Which local 2D construction preserves enough of the retrieved neighborhood to help navigation?

**Tried/contributors.** Astra geometry compared a query-anchor-constrained plane with weighted PCA across nine contexts. It also compared two ways to select five representative directions. Root reviewed the reported preservation measures against the owner’s five-direction interface.

**Observed (agent experiment report).** Weighted PCA captured about 12.5–16.1% of source-vector variance and retained about 21–32% of five-nearest-neighbor relationships; the anchor-constrained alternative was worse on both measures in all nine contexts. Representative diversification reduced redundancy relative to medoids in eight of nine contexts. These are measurements on extracted-text embeddings, not physical distances. The generic intent priors were revised to remove domain-specific dark-matter/compactification terms.

**Decision/next.** Retain the failed alternative and its diagnostics. Do not treat even the better source-point projection as a faithful map. Compare a chart of the five current direction-group centroids, explicitly separating coarse directional fidelity from within-group source spread. In parallel, test the implemented local agent bridge against the same static renderer. No final chart choice or public deployment is claimed yet.

## 2026-11-06 UTC — Q-001: Choose a coarse chart and connect actual navigation

**Question.** Can five directions be useful without implying a faithful paper-level map, and can an external agent operate the complete object?

**Tried/contributors.** Astra geometry fitted the affine plane to retrieval-weighted means of the five dynamic groups, in the original 384-dimensional space without renormalizing those means. Astra site made these the primary clickable chart, with individual source descriptions available as an optional overlay. Astra protocol connected CLI/MCP actions, immutable history, token-protected local transport and a renderer acknowledgement; `/root` requested computation identity checks and an independent fresh-agent trial.

**Observed.** Across seven comparison contexts, the centroid chart retained about 59–70% of between-group variance, versus about 13–17% for the source-point chart. Between-group nearest-neighbor retention still ranged from 20% to 100%; better coarse variance does not establish reliable adjacency. The site owner reports 16 passing tests, 41 verified corpus shard hashes, static route checks and a successful local hosting dry-run. These are not yet live browser or deployment results. [Numerical evidence](tests/geometry/direction-chart-results.json) · [navigation contract](docs/navigation-contract.md) · [agent skill](skills/physics-navigator/SKILL.md).

**Decision/next.** Use the five-group chart, disclose source distortion separately and keep labels/evidence central. Preserve prior unsuccessful approaches. A browser must acknowledge a specific rendered revision before an agent reports that its update was displayed. The first saved planning checkpoint is verified on the configured GitHub branch at `b28c9dbf8b09da4c2cafea4ecef49cdeac307f41`; the next checkpoint will preserve the working prototype before Slurm browser validation. The old public deployment baseline is recorded in [the release evidence](docs/evidence/Q-001-public-baseline.json).
