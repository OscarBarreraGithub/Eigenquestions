# Lab Notebook

## Now

- **Project/question:** Eigenquestions — can a conversation select useful, reproducible local views of a physics graph/vector space, with about five directions at a time?
- **Known:** V1 is live at [eigenquestions.com](https://eigenquestions.com). Questions recompute real graph/vector neighborhoods and five-direction charts. Final acceptance: 23 local tests, 19 browser checks, 9 deployed asset hashes and 32 retired-route checks. Independent agent use succeeds with deliberate context recovery.
- **Limits:** Source-level 2D distances remain lossy; suggestions need source checking. The tested Chromium requires loopback permission for public-page attachment; same-origin local agent updates and graceful fallback are verified.
- **Unfinished/running:** V1 implementation and acceptance are complete. No research jobs remain and no owner input is required. This completion checkpoint preserves the evidence; release verification is checked before reporting completion.
- **Next:** Review a scientist-guided journey and record the next substantive request here. Stronger semantic retrieval and richer scientific relations are future research, not claims of this v1.
- **Git:** Implementation checkpoints are on `agent/question-conditioned-navigation`; the validated release is fast-forwarded and pushed to `main` in `OscarBarreraGithub/Eigenquestions`. Coordinator: `/root`.

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

## 2026-11-06 UTC — Q-001: Freeze a version for independent browser acceptance

**Question.** Does the full agent-to-browser chain work beyond Node-level tests?

**Tried/contributors.** `/root` verified 20 passing tests and all 41 shard hashes, committed the Astra implementation as `47374b8812649a758ff891833ab4ca389864cfcc`, pushed the working branch and checked the remote SHA. A Git archive with matching local/cluster SHA-256 was submitted as Slurm job `58185518` under `randall_lab`. The job builds that exact source and runs Astra protocol's real MCP/browser journey tests without browser-security bypasses.

**Observed/next.** Submission succeeded; browser results are pending. A separate fresh Astra skill trial found that selecting a long extraction can dilute the scientific question; explicit question/source anchors recovered the intended axion/EDE route. A bounded comparison of shorter direction queries is underway before deciding whether to change that behavior. [Job receipt](docs/evidence/Q-001-browser-job.json) · [local validation](docs/evidence/Q-001-prototype-validation.json).

## 2026-11-06 UTC — Q-001: Full browser chain passes; preserve the limits

**Question.** Are the integrated navigation behavior and portable skill useful outside their implementers' tests?

**Observed.** Slurm job `58185518` completed in 27 seconds with exit 0. Its 12 browser checks passed, including real MCP-driven owner and held-out journeys, current-render acknowledgements, five markers/source overlay, replay/import, reload and mobile overflow; no page errors occurred. Root inspected both screenshots. The desktop view was readable; narrow-screen chart labels were too small despite the overflow test, so Astra site is correcting that. The public-origin probe was blocked while the old site was live; it does not establish the replacement's policy behavior. [Browser report and screenshots](docs/evidence/browser-v1/browser-acceptance.json).

**Independent trial/decision.** Fresh Astra agent `/root/fresh_navigator_trial` used the skill for eight axion/WGC/EDE steps, inspected actual papers and saved a replayable session. It recovered context drift with explicit physical questions and source anchors. A proposed generic first-sentence shortening failed to improve EDE, KK and entropy comparisons; retain full source queries and teach deliberate physical-context recovery. Paper reading also exposed a lattice-WGC counterexample caveat absent from a short nomination. These are reasons to preserve evidence access, not claims of a new physics discovery. [Trial](docs/evidence/fresh-agent-trial.md) · [session](docs/evidence/fresh-agent-session.json) · [failed alternative](tests/geometry/selection-query-results.json).

**Next.** Complete the small mobile/instruction changes, publish the static replacement and test the actual public renderer. No scientific correctness claim is inferred from passing transport or browser checks.

## 2026-11-06 UTC — Q-001: Turn visual and independent-agent findings into checks

**Change.** Astra site preserves the same projected coordinates on mobile while using readable numbered markers and full direction cards. Astra protocol now checks marker/font/tap-target sizes, clicks a real marker and restores Back, and separately tests public browser computation even if public-to-localhost attachment is blocked. The portable skill now explicitly preserves the physical application after following a mathematical method.

**Observed/next.** All 21 local tests and 41 shard checks pass. The engine and corpus remain unchanged, so the earlier independent session is still replayable. The earlier screenshot and failed query-shortening experiment remain preserved. Run the amended browser check on a frozen checkpoint before release; then verify public asset identity and retirement of the old routes.

**Submission.** Corrected snapshot `f9e4e50718ef6c04b9517de804a920d15780b1b6` is pushed and remotely verified. Slurm job `58187676` received its exact Git archive with matching SHA-256; see [second browser receipt](docs/evidence/Q-001-browser-v2-job.json).

## 2026-11-06 UTC — Q-001: Release gate passed

**Observed.** Slurm job `58187676` completed in 27 seconds with all 14 checks passing, including readable mobile marker/font/tap dimensions and an actual marker selection followed by exact Back restoration. Root inspected the [mobile viewport screenshot](docs/evidence/browser-v2/mobile-chart-viewport.png); the fixed chart is readable. The engine/corpus still match the independent fresh-agent session. [Full result](docs/evidence/browser-v2/browser-acceptance.json).

**Decision/next.** Release this validated static v1 using the configured GitHub main workflow. Public deployment and new-origin behavior are not yet claimed; verify exact served hashes, retired routes and a clean public-browser journey after the workflow succeeds.

## 2026-11-06 UTC — Q-001: Replace the public application

**Observed.** Main was fast-forwarded to `ad144254b51f103d89e0080f67e0a60097ee29e9`, pushed and remotely verified. The existing [GitHub deployment run](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42161918681) completed successfully, including build/tests and static asset deployment. The actual domain matches all nine checked entrypoint/module/manifest hashes; all 32 GET/POST checks for former quiz, taste, explorer, voting and management routes return the expected retired status. The old database was not modified. [Deployment receipt](docs/evidence/Q-001-deployment.json) · [publication evidence](docs/evidence/Q-001-publication.json).

**Next.** Slurm job `58188305` runs the published-origin test and an independent clean public-browser session. Its outcome will distinguish public attachment compatibility from the already verified local companion. [Job receipt](docs/evidence/Q-001-public-browser-job.json).

## 2026-11-06 UTC — Q-001: Public browser works; inspect beyond pass/fail

**Observed.** Public-browser job `58188305` completed in 31 seconds, passing 17 checks with no local or public page errors. The clean public page loaded/verified its corpus, computed a new contextual query, changed ranked evidence for ON versus USING, followed a direction and restored Back, then exported/imported/reloaded the same state. Direct public-origin attachment to loopback still failed with `TypeError`; the live response has no CSP header, so a bounded diagnostic will distinguish browser policy from an implementation failure. [Public result](docs/evidence/public-v1/browser-acceptance.json).

**Visual finding/next.** Root inspected the [public screenshot](docs/evidence/public-v1/public-static-view.png): one recent-USING chart label overlapped its numbered marker. Astra site is fixing label placement without changing point coordinates. A passing navigation test alone did not establish legibility. Preserve this screenshot and verify the revised view before completion.

## 2026-11-06 UTC — Q-001: Preserve coordinates while repairing legibility

**Tried/contributors.** Astra site added deterministic text placement using measured SVG bounds, obstacles around every marker, and label collision checks. Labels are omitted if no safe slot exists; numbered markers render above them. The point coordinates and numerical engine are unchanged. A regression uses the exact public recent-USING session that exposed the issue. Astra protocol added actual-browser overlap/paint-order assertions plus sanitized diagnostics and blocked-attachment recovery checks.

**Observed/next.** All 23 local tests and 41 corpus shard checks pass. Release this bounded correction, then run the full public-browser check against its exact source before closing the audit.

**Release/submission.** Corrected source `90fcdd239adb5c0b32eb083d6f60fffcfdb2ace6` is remotely verified and deployment [42162700961](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42162700961) succeeded. The first public comparison found only a build-info mismatch: local `dist/` predated the last documentation edit. Rebuilding from the exact commit resolved it, with all 9 asset hashes and 32 route checks passing. The [failed comparison](docs/evidence/Q-001-publication-v2-stale-local-build.json) and [correct comparison](docs/evidence/Q-001-publication-v2.json) are retained. Final browser job `58190279` received the exact source archive; [receipt](docs/evidence/Q-001-public-browser-v2-job.json).

## 2026-11-06 UTC — Q-001: Identify the browser permission boundary

**Observed.** Job `58190279` passed its 14 local checks, then failed the new blocked-launch message assertion. Its sanitized browser console identifies the attachment cause: Chromium 145 denied a request into the loopback address space while local-network permissions remained `prompt`; no CSP or permission override was used. [Failed run and diagnostics](docs/evidence/public-v2/browser-acceptance.json).

**Interpretation/repair.** The harness reused an already loaded public page and changed only its fragment; that is a same-document navigation, so application startup did not read the launch token or try attaching. Astra protocol corrected the test to open the printed launch URL in a genuinely fresh tab and retained all assertions. No runtime code changed. Job `58191305` runs the patched, hash-verified script against the same published source; [receipt](docs/evidence/Q-001-public-browser-v3-job.json).

## 2026-11-06 UTC — Q-001: Complete the connected v1

**Observed.** The corrected fresh-launch test completed in job `58191305` (32 seconds, exit 0), passing all 19 browser checks. The blocked public launch renders an independent browser session and visibly directs the user to the local companion, without claiming an agent connection. The exact recent-USING public view has five labels and five numbered markers with no label/marker or label/label overlap; root inspected the resulting screenshot. Public query/intent changes, selection, backtracking, export/import and reload all pass with no page errors. [Final browser evidence](docs/evidence/public-v3/browser-acceptance.json) · [public view](docs/evidence/public-v3/public-static-view.png).

**Meaning.** Conversation interpretation, reproducible context, global graph/vector retrieval, dynamic directions and affine charts, and the displayed state now form one tested path. The independent axion trial and failed alternatives keep its scientific limits visible. The literal public-to-localhost connection is permission-blocked in the tested Chromium; the verified local renderer is the supported live-agent path. No permissions were silently granted or browser protections disabled.

**Save/resume.** This ordinary Git checkpoint records completion of the bounded Q-001 v1; its push and configured deployment are verified before the completion report. The [40-requirement plan](docs/Q-001-plan.md) and [independent audit](docs/requirements-audit.md) identify evidence and limits; no cluster jobs remain running. Resume with expert-guided usage feedback rather than repeating completed extraction or geometry experiments.
