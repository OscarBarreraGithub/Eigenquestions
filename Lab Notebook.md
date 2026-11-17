# Lab Notebook

## Now

- **Project/question:** Eigenquestions, Q-025: iteratively integrate the scientific graph and embeddings into a readable shared physics atlas, then deliver it through consistent browser/agent navigation and the public site. [Owner request, requirements and loop](docs/Q-025-atlas-delivery.md).
- **Known:** Existing corpus, extractions, MiniLM/Qwen representations, graph/hierarchy alternatives and sampled scientific reviews are inputs to reuse. Geometry and scientific relations remain distinct; roughly 1–15 directions is an interface range. Unique scoped destinations and cross-field reachability are required.
- **Running:** Three Astra xhigh agents are working on numerical alternatives, source-backed scientific evaluation and product/agent integration in separate `research/q025/` directories. A new sustained goal is active. Native FASRC SSH succeeded today; no new Slurm job submitted yet. Hosted arbitrary-view storage was inactive at last verification.
- **Next:** Agree a minimal common atlas contract, execute competing constructions, and challenge them with complete scientific journeys before selecting data for the integrated release. Root monitors progress and owns cross-component acceptance.
- **Save/release:** Active checkout `/Users/emmy/Documents/Eigenquestions-atlas`, branch `agent/atlas-integration-q025`, starts from live `origin/main` at `40cf90b`. It excludes the local-only Q-008 plot and paused Q-007 runtime draft. Prior checkout preserved. Approved project changes can be checkpointed and pushed on this clean branch; do not push the old branch wholesale.

## Requests

**Q-001 (summary):** Replace Eigenquestions with a static, conversation-guided physics explorer. An agent navigates the real graph and embeddings through a machine-readable interface; deterministic local code recomputes a question-dependent 2D view and about five next directions. Demonstrate KK towers → dark matter → Dark Dimension, support derivation/phenomenology/recent-work intents, provide portable agent instructions, and iterate under Astra implementation with central integration review. Keep this notebook and verified Git checkpoints. [Original prompt](docs/requests/Q-001-original.md) · [Atomic plan](docs/Q-001-plan.md).

**Q-002 (summary):** Make v2 a polished, text-first successor to the old viewer, with labels supplied by the new dynamic computation. Use arXiv's familiar palette/type aesthetic, a clear current path, easy New path, large discoverable controls and exceptionally smooth interactions. [Original prompt](docs/requests/Q-002-original.md) · [Atomic plan](docs/Q-002-plan.md).

**Q-003 (summary):** Let agents consult the physics graph as an optional supplement to their ordinary independent research, discoverable by name and useful without a local installation when their tools permit it. Preserve the original agent → structured scientific object → deterministic computation → browser rendering model. Evaluate URL delivery of agent-computed views while retaining context-dependent grouping, labels, relations, changing depth and enough state to continue; do not assume a matrix or main node encodes the full organization. [Proposal](docs/Q-003-contextual-view-proposal.md).

**Q-004 (summary):** Implement Q-003's stored-view proposal, preserve the vision and a concise future showcase of the mechanism, fix the KK-to-restored-topic startup jump, and have Sol agents iterate toward a familiar, minimal, sharp text-first interface with less competing for attention. [Original request](docs/requests/Q-004-original.md) · [Joint atomic plan](docs/Q-003-Q-004-implementation-plan.md).

**Q-005 (summary):** Fix the unsolicited start at the long KK one-loop method, repeated copies of that paragraph, and unclear adjacent choices at each visited level. Keep full scientific context while making navigation concise and each branch understandable. [Atomic plan](docs/Q-005-plan.md).

**Q-006 (summary):** Add a separate fixed overview map, styled after the owner's IAIFI paperscape, with zoomable clusters and legible labels for a collaborator demo. Preserve the current explorer; the overview does not update with queries. [Atomic plan](docs/Q-006-plan.md).

**Q-007 (summary):** Clicking a broad topic should reveal clickable smaller clusters. Clarify the “Awaiting a better home” bucket and keep it secondary. [Plan](docs/Q-007-plan.md).

**Q-008 (summary):** Very quickly count papers, authors and years in the current Swampland collection and show a local papers-per-year plot. Do not put it on the site.

**Q-010 (summary):** Recover the whole Eigenquestions vision across the owner's requests. Fit collaborators' high-level scientific maps and systematic two-way feedback into the paper/graph/embedding foundation, contextual agent navigation and researchers marking and sharing their work. Avoid turning each new prompt into a replacement project or an elaborate new subsystem.

**Q-011 (summary):** Given the confirmed integrated vision, identify the work needed to realize it and the decisions that require the owner's input.

**Q-012 (summary):** Start visualization at a coarse map spanning physics, including condensed matter, strings and photonics, then allow a route through hep-th into the detailed Swampland map. Identify suitable sources, improve clustering and depth, and investigate diffusion over a complex graph so arbitrary regions can receive clean natural-language descriptions and researchers can easily mark what they are working on.

**Q-013 (summary):** Determine the most general and easiest agent/browser communication approach, examining the original compute → upload → URL proposal and alternatives, including the subtleties needed for reliable screen updates and continued scientific exploration.

**Q-014 (summary):** Use a small research team to determine the operation an agent performs on the detailed graph so sentences/paragraphs and clickable clusters can reach the same scientific regions, update the view, and populate useful subclusters or niche questions. Consider alternatives carefully before recommending the construction.

**Q-015 (summary):** Inspect https://github.com/sr-744/swampwiki in the context of the physics atlas and current navigation research.

**Q-016 (summary):** Clarify how complex questions become compatible embedding vectors, what resolution/quality is needed, and whether the required computation must be hosted or can run in the browser or agent environment.

**Q-017 (summary):** Design the highest scientifically useful resolution viewer and encoder structure, including whether light/heavy modes and portable agent instructions for FASRC are the right setup, and identify the work required.

**Q-018 (summary):** Consider precomputing a very clear, deep subcategory graph so a connected agent routes a long question through roughly ten existing decisions, selects the right depth/destination and returns a compact URL. Explain the role of embeddings, expert feedback and the inspected SwampWiki repository in this construction.

**Q-019 (summary):** Assess whether the proposed atlas can actually be constructed in a form that is useful and readable, rather than merely technically navigable.

**Q-020 (summary):** Require a unique destination for a scientific question; what changes between views is the surrounding literature and especially the neighboring questions. Assess this as a solvable construction at Swampland scale.

**Q-021 (summary):** Preserve navigation from extra dimensions into dark-matter cosmology regardless of the approach path; contextual presentation must not trap users within their starting branch.

**Q-022 (summary):** Clarify what embedding/clustering work already exists, then pause new work and recover the full project story rather than treating each clarification as a separate project. Reconcile the original vision, later corrections and saved results.

**Q-023 (summary):** Identify the right next step toward the integrated atlas and recover earlier requests that should also be addressed, without restarting completed work or fragmenting the project.

**Q-024 (summary):** Interpret O(5) as roughly 1–15 directions and explain how the atlas's clusters will actually be determined, reusing completed embedding/clustering work.

**Q-025 (summary):** Run a sustained, centrally monitored effort with multiple Astra agents comparing many graph-plus-embedding constructions; iterate toward a scientifically useful atlas, then complete the remaining integrated features and synchronize eigenquestions.com. Use the cluster as appropriate, preserve the broad vision and use SwampWiki only as optional guidance. [Original request and requirements](docs/Q-025-atlas-delivery.md).

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

**Save verification amendment.** Completion checkpoint `ed6381d034dcb27103d1e7f7fc68700c2d525bc2` is verified on both remote branches; [deployment 42163657269](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42163657269) succeeded. The final public comparison again matched all 9 assets and 32 retired-route statuses. [Final receipt](docs/evidence/Q-001-final-publication.json). This closure corrects the audit's pre-save wording; it changes no runtime or public product asset. Q-001 is complete at the stated v1 scope.

## 2026-11-06 UTC — Q-002: Recover the old viewer's clarity without freezing its data

**Question.** What should return from the old interface, and what should remain dynamic?

**Tried/contributors.** Root inspected the historical Miller-column viewer and the saved text explorer, confirmed the clean v1 repository and opened the v2 branch. Astra site owns the interface; Astra protocol reviews interaction correctness; a fresh Astra reviewer checks arXiv references and visual quality.

**Observed/decision.** The old viewer supplies the intended text navigation structure. Use classic burgundy/white/blue links and familiar sans-serif typography, with more readable rows and larger controls. Current arXiv styling differs; the reference note will distinguish the classic choice from a claim of exact current-site copying. Keep the real engine/corpus and canonical sessions. Cache only actually computed historical directions; show Restore for uncached past steps. Geometry becomes secondary.

**Interaction finding/next.** Current results can overwrite typed drafts; busy guards can silently drop Back/Reset, and a late worker result can overwrite a newly attached agent state. These are concrete v2 requirements, not merely cosmetic changes. Fix and test those races alongside the new design. [Q-002 plan](docs/Q-002-plan.md).

**Reference capture.** Slurm job `58203240` captures the actual arXiv pages and archived old viewer at desktop/mobile sizes. [Receipt](docs/evidence/q002/reference-job.json). The original request, atomic plan and initial reference research are committed as `fe682dd`; implementation and visual acceptance remain unfinished.

## 2026-11-06 UTC — Q-002: Protect a newer agent path during rapid browser input

**Question.** Can the browser replace an unseen pending search without overwriting an intervening agent update?

**Tried/contributors.** Astra site uses the last visibly accepted session as the base for a newer search. Root identified that rebasing the bridge to this session could race with an external MCP action. Astra protocol reproduced the risk and added an optional revision precondition checked immediately before mutation, after the request body is read. Existing MCP behavior and the scientific engine/schema stay unchanged.

**Observed.** The protocol owner reports a passing real-MCP test: an import body held open across a newer agent update returns a conflict and retains that newer state. This server result still needs the integrated browser check. The UI must retain the draft and explain the conflict rather than rewind silently.

**Reference evidence.** Job `58203240` completed in 11 seconds, exit 0. Root inspected the archived text-column path and live arXiv abstract screenshots; these support the chosen flat rules, blue links and bibliographic typography. [Reference captures](docs/evidence/q002/references/reference-capture.json) · [receipt](docs/evidence/q002/reference-job.json). Next: validate the finished interface under delays and review actual product screenshots.

## 2026-11-06 UTC — Q-002: Freeze the text-first prototype for real browser review

**Change/contributors.** Astra site implemented dynamic Miller columns, a visible current path, prominent New path, source listings and optional geometry in the classic arXiv visual style. Historical columns store only accepted computations. Drafts, tabs and the last displayed scientific context survive delayed responses; the bridge uses Astra protocol's revision guard. Root reviewed the combined design and requested horizontal-only path scrolling to avoid moving a reader unexpectedly.

**Observed.** Root ran the complete local verification: 23 tests pass, the static build has 64 assets, and all 41 corpus shards match. The numerical engine/corpus/session schema are unchanged. This is a frozen prototype, not a visual acceptance claim. The design reviewer flagged possible mobile masthead crowding and vertical density to inspect in screenshots. [Validation](docs/evidence/q002/prototype-validation.json).

**Next.** Run the Q-002 delayed-interaction suite and the retained Q-001 geometry/agent suite on this exact checkpoint in Slurm. Review 1440, 1024, 390 and 320px layouts; revise observed problems before publication.

**Pre-browser design amendment.** The frozen source review led to two small repairs: the phone masthead now deliberately wraps, and a readable Sources button explicitly reveals its reading pane. Unsolicited incoming updates still preserve vertical reading position. Site build, static checks and all four site tests pass after these bounded changes. Prototype `99c91d7` was pushed and its remote SHA verified; the corrected checkpoint will be the browser input.

**Browser submission.** Corrected checkpoint `dfb26ff86c8d699015ce6ec06fb1114f18b5de16` is pushed and remotely verified. Job `58205898` runs both suites from its exact, hash-matched archive under `randall_lab`. [Receipt](docs/evidence/q002/browser-v1-job.json). No other cluster workload was modified.

## 2026-11-06 UTC — Q-002: Interactions pass; refine the space given to directions

**Observed.** Job `58205898` completed in 51 seconds, exit 0: all 16 v2 checks and 14 retained geometry/agent checks pass. Real delayed worker/bridge results preserve drafts and visible scientific context; an intervening MCP update survives a browser rebase conflict. No page errors occurred. Warm typing/tab measurements had a 28.5ms p95 next-frame opportunity and no observed long tasks in the sample; this is headless Slurm evidence, not a universal device guarantee. [V2 report](docs/evidence/q002/browser-v1/q002-browser-acceptance.json) · [retained checks](docs/evidence/q002/browser-v1-legacy/browser-acceptance.json).

**Visual interpretation.** Root inspected desktop and mobile screenshots. The flat document styling, source buttons and column structure are legible, but the control stack places the first desktop directions about 558px down and occupies too much of a phone screen. Narrow select labels also truncate. Passing interaction checks did not establish the best use of space.

**Next/contributors.** Astra site and the independent design reviewer are making a bounded compact-layout decision; Astra protocol will exercise the resulting phone disclosure and a real cached historical-choice branch. Preserve these screenshots as the before-state. No engine or corpus change is needed.

## 2026-11-06 UTC — Q-002: Give the research choices more room

**Decision/change.** Independent Astra review agreed with the screenshot finding. Astra site added a large phone Search options disclosure with a visible settings summary; opened selectors span the available width. It reduced surrounding spacing, removed the repeated current-column query and shortened the empty New path frame to 210px. Scientific text and main controls keep their readable size. The numerical construction is unchanged.

**Observed/next.** Root reran all 23 tests and the static/shard checks successfully. Astra protocol added actual historical-column branching, source reveal and mobile-disclosure checks without weakening the earlier assertions. Freeze this corrected version, inspect its true top-of-phone and desktop screenshots, then release if the visual and interaction gates pass. The first browser evidence checkpoint `3e8309f` is pushed and remotely verified.

**Second browser submission.** Compacted checkpoint `cb0b412a2cd64c8fbc96c76180a3e7967a54beb7` is pushed and remotely verified. Job `58207325` received its exact, hash-matched archive. [Receipt](docs/evidence/q002/browser-v2-job.json). While it runs, the owner added Q-003: make graph orientation an optional, discoverable supplement for agents, including no-install access. That addition does not cancel the v2 release.

## 2026-11-06 UTC — Q-002: Compacted layout passes real interaction checks

**Observed.** Job `58207325` completed in 52 seconds, exit 0. All 19 revised v2 checks pass, including actual historical branching, source reveal with unchanged path, and phone settings during delayed computation. Root inspected desktop and top-of-phone screenshots: the desktop column boundary moved from about 558px to 480px; five current directions fit the 1000px viewport. Phone options are readable and the first scientific choices appear earlier. No page errors; the 11 warm presentation samples had p95 29.1ms and no observed long tasks. [Report](docs/evidence/q002/browser-v2/q002-browser-acceptance.json) · [desktop](docs/evidence/q002/browser-v2/desktop-viewport.png) · [phone](docs/evidence/q002/browser-v2/mobile-top-viewport.png).

**Next.** Independent visual signoff and the saved retained-suite result complete the local release gate. Publish v2 through the existing main workflow, then verify the actual public renderer. Q-003 remains a separate addition; the owner clarified that its primary path must be agent actions on a shared machine-readable object, with deterministic computation and automatic browser rendering. Crawling is discovery/fallback, not a replacement for that object.

**Release decision.** The retained suite also passes all 14 checks. Independent Astra design review approves the compacted desktop, top-of-phone, narrow-phone and empty-path views with no remaining visual blocker. Release the verified v2; the primary browser/agent object remains the foundation for Q-003.

## 2026-11-06 UTC — Q-002: Publish the verified v2 interface

**Observed.** Main now contains `dbb7d0e7f00e23ef41e251b9577a622ee9110992`, verified remotely. [Deployment 42168891783](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42168891783) succeeded. The actual domain matches all nine checked assets; all 32 retired-route status checks pass. [Publication receipt](docs/evidence/q002/publication-v1.json).

**Next.** Public browser job `58208591` tests both suites against the actual domain. It reuses frozen `cb0b412` product source; the published checkpoint adds only notebook/audit/evidence files. [Job receipt](docs/evidence/q002/public-v1-job.json). No source/runtime changes are being mixed into this verification while Q-003 architecture is discussed.

## 2026-11-06 UTC — Q-002: Complete public v2 verification

**Observed.** Public job `58208591` completed in 2m06s, exit 0. All 19 v2 checks and 19 retained/public checks pass against the actual domain, including independent browser computation, guarded live-agent updates, replay/import, source reveal, historical branching, mobile settings, geometry legibility and permission-blocked companion recovery. The public first-load measurement was 9.285s; warm presentation p95 was 30.1ms with no observed long tasks in that sample. These are measurements on the tested headless environment, not promises for every connection. [V2 public report](docs/evidence/q002/public-v1/q002-browser-acceptance.json) · [retained/public report](docs/evidence/q002/public-v1-legacy/browser-acceptance.json).

**Outcome.** Q-002 is complete at the requested v2 scope: a live text-column explorer, classic arXiv visual treatment, clear path/New path, large controls and tested asynchronous behavior. All release assets and retired routes match. No cluster job is left running. Q-003 discussion continues separately; it must preserve the original agent → structured object → deterministic computation → rendered view architecture.

## 2026-11-06 UTC — Q-003: Correct the object before choosing its transport

**Question.** Can an agent compute a contextual view and send it through a URL without losing the nontrivial organization described in Q-001?

**Tried/contributors.** Root reread the original request. Astra protocol inspected actual state/view exports and measured real payloads; a separate Astra reviewer audited mathematical sufficiency and path dependence. Root first described selected nodes and an affine plane, then corrected that simplification after the owner emphasized names, clusters and context-relative depth.

**Observation/interpretation.** A plane only specifies geometry. A complete view also needs selected sources, possibly overlapping groups, labels, typed relations, evidence, available next actions and continuation context. A compact recipe is sufficient only when the pinned builder can reconstruct every omitted decision. Today's query/intent/source-anchor state exactly determines today's frozen algorithm; that fact does not establish adequate memory for the broader scientific navigator. Model-generated decisions must be captured as accepted outputs, not assumed reproducible by rerunning a model.

**Decision/proposal.** Make the complete contextual object authoritative. Distinguish display, deterministic reconstruction and continuation. Treat URL encoding as an optional transport/optimization; use reference-based compact objects when metadata already exists in the pinned corpus, and a full object/file or existing agent bridge when a URL cannot carry it. No arbitrary code belongs in the URL. The proposal remains unimplemented while this discussion settles the contract.

**Existing gaps.** Share focus encodes only current state and is read only at startup, so a fragment-only change in an already open tab currently does nothing. Encoding has no matching size check for the decoder's 16,000-character limit. Export view includes a computed result, but import restores its session and recomputes; there is no generic agent-authored contextual-view importer. These are recorded implementation findings, not completed repairs.

**Save context.** V2 closure `2929dd491d4f0c6476d1a5e9cfb0e5f86f2e0be6` is verified on remote main; [deployment 42169887099](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42169887099) succeeded. Q-003 adds no product changes yet.

## 2026-11-06 UTC — Q-003: Measure what a URL would have to carry

**Observed.** Astra protocol measured eight real views. Current recipes are 518–999 JSON bytes and 451–781 bytes as strongly compressed, URL-encoded payloads with a short prefix. Complete computed views require 80,850–102,746 encoded bytes; a lean source-referencing result still uses 29,027. A nine-state current-algorithm session fits 1,922 encoded bytes. All eight small recipes exactly replay today's view JSON in a second navigator; a lean result also hydrates exactly from the pinned corpus without repeating retrieval/PCA. [Measurements](docs/evidence/q003/size-study/report.json) · [retained/omitted fields](docs/evidence/q003/size-study/lean-result.json).

**Meaning.** These are measured examples, not lower bounds or universal URL limits. Small links work when shared data and a deterministic builder supply the omitted information. Arbitrary new labels, groups, relations or context cannot be recovered unless recorded or specified reproducibly. The independent audit distinguishes displaying a view, reconstructing it and continuing from it; only the last requires sufficient scientific continuation context. The authoritative representation must be the complete contextual object, with URL delivery optional. [Proposal and next checks](docs/Q-003-contextual-view-proposal.md).

**Status.** This checkpoint saves the discussion, failed matrix-only simplification, actual size evidence and bounded next steps. No new view protocol, agent-written grouping importer or URL update loader is claimed implemented.

## 2026-11-06 UTC — Q-003: Price stored views instead of forcing them into URLs

**Request refinement (summary).** The owner proposes automatic agent uploads or manual drag-and-drop, a stored full/reduced view on Cloudflare, a returned random durable link, and a responsive browser while upload completes. They ask how many queries/users the free tier can support. This extends the Q-003 transport proposal; it requests a calculation, not infrastructure provisioning.

**Tried/contributors.** Root used current Cloudflare documentation and the measured view payloads; Astra protocol independently audited quotas and arithmetic. The proposed route is a small upload Worker plus R2 object storage, with public/unlisted reads through a production R2 custom domain. Random-ID lookup needs no SQL database, and this flow needs no persistent socket.

**Observed/calculated.** At 128 KiB per compressed view, an 8 GB planning inventory holds 61,035 views. With 20% operation headroom and no caching assumed, direct R2 reads support roughly 26,666 new saves/day and 266,666 openings/day averaged over a 30-day month; these are quotas, not throughput benchmarks. One hundred daily users saving 20 views each day retain 7.864 GB after 30 days. Permanent links keep accumulating; at 500 such daily users the 8 GB target is reached in about six days. Extra R2 storage is inexpensive, but free allowance is not a hard spending cap.

**Meaning/next.** Storage retention, payload size and the distinction between saving and opening dominate the answer. Keep scientific computation/compression out of the 10 ms Free Worker CPU path, and measure a real lightweight upload endpoint before calling its capacity reliable. The account's remaining shared allowances were not inspected; no subscription, bucket or deployment was changed. [Capacity note](docs/Q-003-cloudflare-capacity.md) · [calculation inputs/results](docs/evidence/q003/cloudflare-capacity-20261106.json). Preserve existing links when planning storage growth rather than silently assuming a deletion policy.

## 2026-11-06 UTC — Q-003 / Q-004: Authorize implementation and remove the false starting topic

**Question.** Can the complete view travel intact while the interface becomes a quiet reading tool?

**Tried/contributors.** The owner authorized the stored-view proposal and requested Sol iteration on visual clarity. Root assigned Astra protocol and backend owners, Sol interface implementation and an independent Sol review. Root preserved the exact request, audited a joint atomic plan against the broader contextual-navigation vision and wrote [a concise future showcase](docs/contextual-view-showcase.md).

**Observed.** The initial UI review identifies repeated headings and settings before the scientific choices. Source inspection identifies hardcoded KK shell text and worker defaults before restoration as the startup jump's cause. These are findings; repairs are not yet verified. The proposed file keeps authored group labels, overlapping membership, relations, evidence and optional typed geometry; unknown builders remain readable without silently claiming full continuation support.

**Constraint.** Cloudflare account discovery through the configured connector returned “MCP tool call requires approval, but approval policy is never.” Root stopped that access path and did not use another credential route. Code, local Worker tests and the existing authorized GitHub site deployment can proceed; real R2 activation remains pending. No bucket, subscription or existing D1 data was changed.

**Next.** Integrate and test neutral startup, exact file/view roundtrips, route changes and delayed interactions. Inspect real desktop/phone screenshots after freezing source, then publish the verified interface. Hosted save/open must be tested after authorized activation before it is described as available. [Atomic plan](docs/Q-003-Q-004-implementation-plan.md) · [Sol baseline review](docs/Q-004-ui-review.md).

## 2026-11-06 UTC — Q-004: Isolate the first visual iteration

**Question.** Does the quieter layout actually put scientific text first at desktop and phone sizes?

**Tried/contributors.** Sol interface removed promotional headings, repeated labels, colored bands and exposed settings; kept a visible New path, plain links, readable rows and large controls. Independent Sol source review requested wider small targets and unclipped keyboard focus. Those bounded repairs are included. Root is freezing these UI files with the previously verified runtime for a fast visual experiment while Astra finishes the new view controller.

**Scope.** This checkpoint deliberately leaves in-progress protocol/backend files unstaged. Its capture utility uses real native scientific results and records screenshots/target sizes; it does not establish that new storage buttons work or that the prior runtime's startup default is repaired. Integrated acceptance comes later. No new browser was launched on the Mac.

**Next.** Capture and review 1440, 1024, 390 and 320px screens in authorized Slurm. Use observed visual faults to guide another Sol iteration. [Design choices](docs/Q-004-ui-design.md) · [capture utility](tests/integration/q004_visual_capture.py).

**Submission.** UI checkpoint `3a5f38f8d9a266b6b2b94248e2c5cb1837f3f923` is pushed and remotely verified. Slurm job `58236895` receives that exact archive; local and cluster SHA-256 match. [Receipt](docs/evidence/q004/visual-v1-job.json).

## 2026-11-06 UTC — Q-003 / Q-004: Test durability and inspect real screens

**Observed.** Visual job `58236895` completed in 1m14s, exit 0. The 18 captures have no page errors or horizontal overflow; the measured primary controls meet 44px targets. KK choices start at 384px on desktop and 383px on a 390px phone, versus roughly 480/540px in the earlier design. Root and independent Sol reviewed the actual screens. [Capture report](docs/evidence/q004/visual-v1/q004-visual-capture.json) · [desktop](docs/evidence/q004/visual-v1/kk-1440.png) · [phone](docs/evidence/q004/visual-v1/dark-matter-390.png).

**Interpretation/iteration.** The quieter reading hierarchy succeeds. An empty initial state still occupies a historical column, wasting space and implying a scientific step; the true empty page also repeats unavailable controls. These are bounded rendering corrections for the next integration, not grounds to change the scientific engine. Full meaningful breadcrumbs must survive as the context changes.

**Storage evidence/contributors.** Astra backend's five tests and root's independent rerun pass, including simultaneous identical saves, durable-write failure, lost receipts, immutable IDs and SQLite budget restart/concurrency. The complete Node suite passes 32 tests. Both default and storage-enabled profiles pass local packaging dry runs; neither dry run provisions resources. The selected admission design reserves exact bytes transactionally before R2, allows 2,000 new views/day and keeps an 8 GB inventory ceiling without expiring old links. This is an explicit launch cap, not the earlier theoretical quota calculation.

**Limits/next.** Representative local validation used about 2.85ms of Node process CPU; maximum-size input used about 7.38ms. These are not production Worker CPU measurements. The account's free allowance and actual hosted save/open still require authorized activation. [Benchmark evidence](docs/evidence/q003/stored-views-local-benchmark.json) · [operations and activation](docs/stored-views-operations.md). Freeze the integrated controller for real cold-start, file, URL and delayed-action tests next.

## 2026-11-06 UTC — Q-003 / Q-004: Preserve the scientific object through navigation

**Question.** Does the whole journey preserve the intended view, rather than merely pass isolated upload and display tests?

**Review/contributors.** Root and independent Astra backend review identified stale share routes after local changes, authored history being replaced by native groups, late file reads and save receipts crossing newer user actions, and previous assumptions leaking into an unrelated imported session. Root also found malformed optional metadata could fail during rendering after validation. Astra protocol repaired these boundaries and added browser regressions. Sol refined the observed phone heading and empty-page layout.

**Decision.** The complete capsule remains authoritative. Authored questions and groups display as supplied; a bounded in-memory history restores accepted authored views and their explicit next actions. Evicted authored results require reopening their file rather than pretending native reconstruction is equivalent. Independent loads start with independent assumptions. Saved views render without loading the full corpus; native continuation loads that data only when needed.

**Observed/next.** Root rebuilt and reran all 32 Node/Worker tests successfully; 70 product assets and all 41 frozen corpus shards pass site checks. No scientific engine/data change was made. This checkpoint freezes the integrated runtime for four real-browser suites, including delayed operations and exact authored-file roundtrips. Browser evidence is still pending; [local receipt](docs/evidence/q004/integration-node-validation.json).

**Submission.** Integrated checkpoint `3fe979f6e1ac48c2bbc957be62721628969e9218` is pushed and remotely verified. Slurm job `58241697` runs four suites from the exact, hash-matched archive. [Receipt](docs/evidence/q004/integrated-v1-job.json). Browser HTTP storage uses a deterministic adapter; actual durable storage is tested separately in local workerd, and production activation remains pending.

## 2026-11-06 UTC — Q-003 / Q-004: Integrated browser behavior passes

**Observed.** Job `58241697` completed in 1m07s, exit 0: 12 stored-view checks, 19 delayed-interaction checks, 14 retained geometry/agent checks and all 18 visual captures pass. Authored overlap, labels, evidence and context survive file/HTTP-adapter roundtrips; Back restores authored grouping; unrelated imports clear prior assumptions; late operations do not replace newer intent. Cold stored views load with no corpus requests and no fake KK state. [Stored-view report](docs/evidence/q004/integrated-v1/stored-artifacts/stored-views-browser-acceptance.json) · [interaction report](docs/evidence/q004/integrated-v1/interaction-artifacts/q002-browser-acceptance.json) · [retained report](docs/evidence/q004/integrated-v1/legacy-artifacts/browser-acceptance.json).

**Visual decision.** Root and independent Sol approve the revised ordinary interface at desktop, 390px and 320px. Phone controls fit the Step header without squeezing the question. The empty page is compact and the blank historical column is gone. [Final visual review](docs/Q-004-ui-review.md) · [phone](docs/evidence/q004/integrated-v1/visual-artifacts/dark-matter-390.png) · [empty path](docs/evidence/q004/integrated-v1/visual-artifacts/new-path-390.png).

**Final bounded correction.** An external continuation now checks that its source anchors actually exist before native computation; the native engine's warning-and-ignore behavior is insufficient for an authored scientific action. Authored snapshots also report source descriptions rather than inventing paper counts from missing IDs, and omit unavailable continuation instructions. The final harness adds actual drag-and-drop and invalid-anchor rejection. All 32 local tests/build/shard checks pass again. Recheck this bounded stored-view journey, then publish; no more visual redesign is planned.

**Final submission.** Checkpoint `a00c40eddb96da392f60f19dcd07b012c412a091` is pushed and remotely verified, including portable instructions and expanded publication checks. Job `58243580` runs the revised stored-view harness from its exact hash-matched archive. [Receipt](docs/evidence/q004/final-v1-job.json).

## 2026-11-06 UTC — Q-003 / Q-004: Approve the frontend release

**Observed.** Final job `58243580` completed in 24 seconds, exit 0; all 14 checks pass with no page errors. Actual drop, unavailable anchor rejection, exact authored history, no-corpus display, empty startup and guarded independent imports all pass. [Final report](docs/evidence/q004/final-v1/stored-views-browser-acceptance.json). The existing 19 interaction and 14 retained local checks remain valid; the final changes are limited to authored-view handling and tested wording.

**Release decision.** Publish the verified frontend through the existing main workflow, using the default profile with no storage bindings. This does not provision R2 or bypass the blocked connector. The live API must honestly report unavailable storage, while file import/export and page-agent navigation work. Verify the public assets, retired routes, actual API response and public browser behavior before closure. [Showcase note](docs/contextual-view-showcase.md) now distinguishes implemented/tested behavior from pending live sharing.

## 2026-11-06 UTC — Q-003 / Q-004: Publish the verified frontend

**Observed.** Release `af2aa86d3e1844535964299256bc948d4f545cd6` is verified on both remote branches; [deployment 42182497990](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42182497990) succeeded. The actual domain matches all 16 checked assets, including the new capsule codec/schema, discovery files and portable instructions. All 32 retired-route checks pass. [Publication receipt](docs/evidence/q004/publication-v1.json).

**Storage boundary.** The activation repository variable is absent. Actual POST and GET requests return HTTP 503 `storage_unavailable`, with useful file-import guidance and no cached error. This is expected and verified, not a live stored-sharing success. [Public API evidence](docs/evidence/q004/public-storage-status.json).

**Next.** Job `58244320` runs the three suites against the actual public renderer, using frozen `a00c40e` product/test source; the release adds only notebook/review/evidence changes. [Receipt](docs/evidence/q004/public-v1-job.json). Finish public verification, then request only the blocked account-access prerequisite for storage activation.

## 2026-11-06 UTC — Q-003 / Q-004: Public tests pass; correct unloaded metadata

**Observed.** Public job `58244320` completed in 1m16s, exit 0. All 52 checks pass: 14 full-view, 19 interaction and 19 retained/public checks. The empty public page became ready in 0.612s; the small warm presentation sample had p95 29.6ms and no observed long tasks. These headless observations are not device/network guarantees. [Public reports](docs/evidence/q004/public-v1).

**Visual finding/correction.** Root inspected the real public fresh-page screenshot after the tests passed. The unloaded corpus footer incorrectly displayed “0 papers” and unknown dates; the earlier empty-path capture had already loaded data and did not expose it. Astra protocol now preserves the known HTML corpus description while keeping the corpus lazy, and adds the missing fresh-page assertion. [Before screenshot](docs/evidence/q004/public-v1/stored-artifacts/empty-mobile-viewport.png). This is the only runtime change after the 52-check public pass; recheck the focused public view suite on the correction.

**Corrected release.** `7600613d7f04d444c6bd403037f7a7d846705265` is verified on both remote branches; [deployment 42183241426](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42183241426) succeeded. All 16 assets and 32 retired routes match again. [Receipt](docs/evidence/q004/publication-v2.json). Job `58245303` uses the exact committed harness, hash-verified on the cluster, against those public assets. [Job receipt](docs/evidence/q004/public-v2-job.json).

## 2026-11-06 UTC — Q-003 / Q-004: Close frontend work with a precise storage handoff

**Observed/outcome.** Final public job `58245303` completed in 13 seconds, exit 0; all 14 focused checks pass with no page errors. Root inspected the corrected [fresh phone page](docs/evidence/q004/public-v2/empty-mobile-viewport.png): known corpus scope remains visible, no false zero count or placeholder topic appears, and no corpus data is requested before a query. [Final report](docs/evidence/q004/public-v2/stored-views-browser-acceptance.json). Q-004 is complete. The full-view file/page-agent portion of Q-003 is implemented and publicly verified.

**What remains.** Hosted shared links are not active. The configured Cloudflare connector refused account discovery with “MCP tool call requires approval, but approval policy is never.” The implementation, admission limits, activation profile and verification procedure are ready; enabling connector access is the remaining owner-dependent prerequisite. After activation, test real durable storage and production CPU before claiming live/free-tier sharing. Existing D1 and unrelated cluster work were untouched; no job for this update remains running.

**Save.** The vision, exact latest request, atomic requirements, useful failed approaches, independent reviews and mechanism showcase are in the project. This ordinary Git checkpoint includes closure/evidence only; runtime assets are unchanged from the verified release. Push both agreed branches and verify their remote heads before reporting completion. [Showcase](docs/contextual-view-showcase.md) · [reproducible plan/status](docs/Q-003-Q-004-implementation-plan.md).

## 2026-11-06 UTC — Q-005: Separate source descriptions from navigation

**Question.** Is the repeated KK paragraph a hardcoded default, duplicated corpus evidence, or navigation state rendered in several places?

**Observed.** The bare-home route implicitly restores a saved capsule/session/companion. Native direction selection uses the representative source's full description as the next query; the renderer repeats it in several places. The exact paragraph is a method extraction for paper 1303.2661. We have not inspected the user's browser storage or yet established whether successive groups also repeat semantically.

**Amendment to Q-004.** The earlier startup correction removed the hardcoded first KK view and its subsequent jump. It did not remove automatic resumption on a bare visit. Q-005 changes that policy to explicit Resume; the earlier clean-profile tests did not cover this expectation.

**Tried/next.** `/root` assigned Astra controller/history work, Sol interface refinement and an independent Astra real-data audit with shared requirements. Preserve full queries and evidence while shortening their display, and show the actual alternatives and choice taken at each step. A prior failed query-shortening experiment rules out treating this as a casual scientific-input edit. [Plan](docs/Q-005-plan.md). No implementation or new browser validation is claimed at this checkpoint.

## 2026-11-06 UTC — Q-005: Find genuine navigation cycles

**Tried/contributor.** Astra `/root/stored_view_backend` ran real-data multi-step native selection routes starting from KK towers, including the reported one-loop method, and compared canonical state and source identities.

**Observed.** Repeated selections alternate between the same two canonical views on several routes. The immediate self-source guard does not prevent returning to an older source. The five choices after the quoted method are all method facets, not synthesized physical questions. [Audit evidence](docs/evidence/q005/navigation-audit.json).

**Decision/next.** Shorter text alone is insufficient. Recognize an identical native destination as a return to an earlier step, retaining the actual source-based choices rather than manufacturing new depth or deleting relevant evidence. Label representative facet types and exact revisits; preserve full source evidence and authored views. Astra protocol will implement and regress this shared browser/CLI behavior after checking history implications. Semantic topic synthesis is a separate agent-authored interpretation, not something the static renderer currently supplies.

## 2026-11-06 UTC — Q-005: Repair entry, choices and exact returns

**Tried/contributors.** Astra protocol separated display excerpts from scientific state, made saved-state resumption explicit and added shared exact-state return behavior to native selection. Sol supplied the neutral entry, full-context disclosure, paper/facet metadata and clear historical-choice markers. Astra audit supplied the real-data cycle and a focused browser regression. Root reviewed integrated semantics and required preservation of source provenance, exact authored returns and truthful action history during concurrent agent updates.

**Observed.** All 35 local Node/Worker/protocol tests pass, with 71 built assets and 41 verified corpus shards. Six real selections now retain five unique history states and recognize two return visits; full method text and numerical computation remain unchanged. A stale built helper initially failed the publication test; rebuilding resolved it. Build precedes tests in the documented verification order. [Local validation](docs/evidence/q005/local-validation.json).

**Meaning/next.** This fixes exact repetition and presentation, not all semantic redundancy or the synthesis of higher-level research questions. Preserve old session data and mark older recorded returns; do not rewrite scientific history. Freeze this prototype and run the reported path plus existing race/authored-view suites in Slurm Chromium, then inspect the screenshots before publishing.

**Browser submission.** Frozen source `d87bb2b0e2b6e88765e2d3158275fb49c5885684` is pushed and remotely verified. Its Git archive matched SHA-256 on FASRC before extraction; Slurm job `58361795` runs the new regression and three existing browser suites. No browser outcome is claimed yet. [Receipt](docs/evidence/q005/browser-v1-job.json).

## 2026-11-06 UTC — Q-005: Reject a visually misleading phone result

**Observed.** Job `58361795` finished in 74 seconds. Stored-view and interaction suites passed all 14 and 19 checks. The focused suite passed nine checks, including the quoted method, exact returns, authored-history protection and explicit Resume; its final initial-focus test mistakenly reused a same-document fragment navigation. The legacy suite reached eleven checks before an obsolete full-label assertion. Those test assumptions are being corrected without weakening source/context checks. [Run evidence](docs/evidence/q005/browser-v1/).

**Visual result.** Root and Sol accepted the neutral home and desktop source distinctions, but the phone captures show the current choices partly off-screen or an older column in their place. Outer-page overflow checks missed this. The cause may involve scroll-snap settling and resize anchoring; it is not yet established. The selected historical fourth choice also needs to remain discoverable inside its column. [Visual review](docs/Q-005-ui-review.md).

**Decision/next.** Withhold release. Astra will anchor the actual intended column reliably, Sol will bound the current breadcrumb, and the focused browser test will check column rectangles and settled arrow/resize behavior before capturing images. Preserve the failed pictures and source version rather than relabeling them as a pass.

**Repair ready for recheck.** Astra replaced horizontal CSS snapping with explicit column alignment after accepted navigation and resize; arrows target actual adjacent columns, while deliberate earlier-step browsing is retained. The historical followed row is revealed within its column, and renderer acknowledgements wait for alignment. Sol bounded the current breadcrumb. The focused harness now samples stable column rectangles and uses real arrows; screenshots no longer rely on direct scroll writes. The obsolete label assertion now also verifies exact underlying query and group data. All 35 local tests and static checks pass again. Browser results for this repair are pending.

**Second submission.** Corrected source `bbea3016642055722126cfa7584d24fec2cc9de2` is pushed and remotely verified. The second complete Git archive matched SHA-256 on FASRC. Job `58364357` runs all four browser suites with the stronger column checks. [Receipt](docs/evidence/q005/browser-v2-job.json).

## 2026-11-06 UTC — Q-005: Verify the distinction between view state and viewport

**Observed.** Job `58364357` passed the 14 stored-view and 19 interaction checks again. The reported method now has a fully visible phone column and a bounded breadcrumb; its stable geometry checks pass. Later, the focused test expected the current step after resizing while an earlier step was deliberately remembered. The renderer correctly preserved that earlier step. The legacy test also compared a full browser group against a compact MCP response that intentionally omits memberships. [Second-run evidence](docs/evidence/q005/browser-v2/).

**Amendment/next.** Correct those test expectations: first verify the remembered column survives resize, then use the real arrows to verify current; request the full MCP snapshot for exact group equality. Preserve the strong visibility and full-data assertions. At root’s request, Astra removed unreadable stemmed diagnostic tokens from the visible subtitle without changing exported diagnostics. Freeze a final candidate and rerun the integrated suites. These failures do not establish a new numerical or source-data defect.

**Third submission.** Job `58365554` received hash-matched source `e784d94e4d008aab3e116891a00ba1191598bd8f`, verified on the working GitHub branch. All four browser suites run again. [Receipt](docs/evidence/q005/browser-v3-job.json).

## 2026-11-06 UTC — Q-005: Approve the visible navigation and isolate the last test issue

**Observed.** Source `e784d94` passes all 10 focused checks, 14 full-view checks and 19 interaction checks. Root and Sol inspected the final desktop, 390px and 320px images: current columns are fully visible, earlier alternatives remain navigable, followed choices are visible within their columns, return labels are clear, and home offers explicit Resume. [Final visual review](docs/Q-005-ui-review.md) · [focused evidence](docs/evidence/q005/browser-v3/q005_navigation_acceptance/q005-navigation-acceptance.json).

**Last diagnostic.** The legacy chart test stopped after 13 checks when reading the long selected query. Job `58366743` proved the intended direction was selected and the canonical query, exported context and DOM text were all exact. Chromium returns empty `innerText` inside the closed Full context disclosure. Correct the test to open that disclosure before checking readable text, preserving exact data assertions. This is not missing scientific data. [Diagnostic receipt](docs/evidence/q005/legacy-diagnostic-job.json).

**Next.** Finish the isolated legacy test, publish the visually accepted runtime through the existing main workflow, and check actual public hashes and navigation. No numerical engine or frozen corpus changed during these repairs.

**Release gate passed.** The corrected isolated legacy suite completed in job `58367541` (17 seconds), with all 14 checks passing and no local browser errors. Together with the final focused, capsule and interaction suites, all 57 browser checks pass. The runtime remains `e784d94`; only test visibility handling changed. Publish this verified navigation repair before introducing the separately requested overview. [Legacy receipt](docs/evidence/q005/legacy-final-job.json).

## 2026-11-06 UTC — Q-006: Reuse an actual map and the owner's actual paperscape

**Question.** Can we show the collection's overall structure without rebuilding or entangling the contextual explorer?

**Observed/contributors.** Sol verified IAIFI-Paperscape GitHub main `e3d55af` against the local executable renderer and data; it uses Canvas2D with fixed coordinates and progressive labels, despite stale README wording. Astra found the already pinned publication map: reviewed question units match all current source IDs/text hashes, and the question view covers 8,473 facets from 6,477 papers. It has five root children and only one finer branch, with overlaps and unresolved entries; all topic cards remain agent-proposed. [Reference audit](docs/Q-006-paperscape-reference.md).

**Decision/next.** Use that one fixed question view, preserve its actual hierarchy and memberships, and avoid inventing deeper clusters. A compact initial export is estimated at 1.87 MB; full excerpts can load from small detail shards. Open the overview in its own browser tab so live authored history remains intact. Astra owns export/renderer, Sol owns the quiet paperscape interface, and root verifies the integrated demo. [Plan](docs/Q-006-plan.md). These are source findings and a plan, not a completed overview.

**Q-006 clarification (summary).** The owner confirmed that IAIFI is a UI-style reference only. The cuts, connections and topics must belong to the Swampland map. Root confirmed this boundary and passed it to all three implementers; the chosen Swampland publication artifact already meets it. Rendering patterns are the only part borrowed from IAIFI.

**Q-005 public release.** Main and the working branch are verified at `f0e782d7baecf6f45a5eb5fa59a9cdb328aa68a2`; deployment `42278851870` succeeded. All 17 published asset hashes and 32 retired-route checks pass. Slurm job `58370368` checks the actual published UI while Q-006 is developed separately. [Publication](docs/evidence/q005/publication-v1.json) · [public browser receipt](docs/evidence/q005/public-v1-job.json).

## 2026-11-06 UTC — Q-005 complete; Q-006 fixed export verified

**Q-005 outcome.** Public job `58370368` completed in 70 seconds with all 43 checks passing: focused 10, capsule 14 and legacy/public 19. The released repair is verified at the actual domain, including the exact quoted path, explicit Resume, real returns, source preservation and responsive columns. No validation jobs remain. [Public evidence](docs/evidence/q005/public-v1/).

**Q-006 progress.** Astra exported all 8,473 exact Swampland question facets, 6,477 papers, 42 topic affinities, 10 overlapping facets and 13 unresolved facets. The initial map plus manifest totals 1,858,219 bytes; all 19 files total 3,670,658 bytes, with individual detail shards below 116 KB. Quantiles show the central 98% covers roughly 86% of x extent and 81% of y extent; the existing preview shows distinct large regions rather than outliers compressing the map. Preserve exact coordinates and fit all sources. Renderer/UI integration and browser checks remain unfinished.

## 2026-11-06 UTC — Q-006: Complete the isolated overview candidate

**Tried/contributors.** Astra data exported and independently checked every question, membership, coordinate and affinity against the pinned Swampland source. Astra protocol implemented fixed Canvas rendering, local Find, progressive labels, camera controls and exact lazy source descriptions. Sol supplied the quiet standalone interface and the new-tab entry. Root checked the integrated boundary and requested full-member Fit rather than an arbitrary crop.

**Observed.** All 43 local tests pass, alongside 94 built assets, 41 original corpus shard hashes and 18 derived overview file hashes. Regeneration is byte-identical. Final initial JSON is 1,858,801 bytes; all 19 overview files total 3,671,240 bytes (amending the earlier preliminary manifest-size measurement). Topic captions preserve originals and rationales. No IAIFI scientific data or geometry is used. [Data audit](docs/Q-006-overview-data-audit.md) · [UI notes](docs/Q-006-ui-review.md).

**Meaning/next.** This is ready for real-browser inspection, not yet a public release. The owner requested immediate deployment; run the focused overview acceptance and existing navigation regression on a frozen snapshot, inspect the pictures, and publish through the existing workflow if they pass.

**Browser submission.** Source `50e58042101fab5ba1ad892b2b2ba1f6ac9d08f4` is pushed and remotely verified. Its archive matched SHA-256 on FASRC before extraction. Slurm job `58373333` runs the focused overview suite and the existing Q-005 navigation regression. [Receipt](docs/evidence/q006/browser-v1-job.json).

**First browser result.** Job `58373333` completed in 45 seconds. All 10 navigation regression checks pass and the overview loads all fixed data with five readable labels. The overview suite stops at its precise wheel-anchor assertion; protocol is checking the actual delivered pointer coordinates before deciding whether this is a renderer or input-test defect. The first desktop image is legible. Preserve this failure and rerun the focused suite after diagnosis. [Evidence](docs/evidence/q006/browser-v1/).

**Focused rerun.** Job `58374108` uses unchanged runtime `50e5804` and hash-matched harness `fa63bc6`. The harness captures the actual native WheelEvent position and pre-handler camera, retaining both requested and received coordinates; the strict anchor invariant remains in place. [Receipt](docs/evidence/q006/browser-v2-job.json).

## 2026-11-06 UTC — Q-006: Accept the real browser demo

**Observed.** Job `58374108` completed in 18 seconds with all 12 overview checks passing and no browser errors. Combined with the unchanged explorer's 10 passing regression checks, the demo covers desktop/390/320px, pan/wheel/pinch/keyboard/Fit, exact source descriptions, delayed-load races, overlapping/unresolved memberships and exact live authored-history preservation. Root inspected initial, fine-group, source and 320px views; labels and controls are legible. [Browser evidence](docs/evidence/q006/browser-v2/q006_overview_acceptance/q006-overview-acceptance.json).

**Amendment.** The first wheel failure was input quantization in the test, not a camera defect: the requested position (381.1, 295.84) arrived as (381, 295.515625). Both actual world-coordinate errors are exactly zero. The original runtime `50e5804` remains unchanged. One 75 ms initial long task and about 103 ms measured wheel feedback were observed in headless cluster Chromium; these are environment-specific measurements, not a frame-rate guarantee.

**Decision/next.** Publish the accepted minimal demo through the existing main-branch workflow, then verify actual public hashes and the overview browser journey. The map is a fixed, provisional organization of Swampland question excerpts; it does not claim a new scientific taxonomy.

**Release submitted.** Commit `edeb241d3e9232b0b037350d6175adffbc056ee5` is verified on the remote working branch and main. [Deployment 42282030920](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42282030920) is running; this is not yet a claim that the new overview is live. Sol also approved the final phone/source images; its completed review will be saved with the public verification checkpoint.

**Public identity verified.** Deployment `42282030920` succeeded. All 22 public asset hashes match the accepted build, including the canonical overview HTML/JS/CSS/data; all 32 retired-route checks pass. The live map is [eigenquestions.com/overview](https://eigenquestions.com/overview). Slurm job `58375066` exercises the actual public UI. [Publication evidence](docs/evidence/q006/publication-v1.json) · [public browser receipt](docs/evidence/q006/public-v1-job.json).

**Public browser finding.** Job `58375066` passed ten map/render/input checks, then stopped on the blanket assertion that all page-associated requests use GET. The public response advertises Cloudflare Network Error Logging, absent from the local server; the failed report did not retain the request trace. Add that trace and distinguish proven browser/platform reports from application data/API traffic, preserving all explorer-isolation assertions. No application runtime change is justified yet. [First public evidence](docs/evidence/q006/public-v1/).

**Public rerun.** Job `58376328` uses hash-matched harness `2a6fb89` against the unchanged live release. Network evidence is saved before assertions, and only a POST with Cloudflare NEL endpoint, declared document policy, correct MIME type and network-error-only payload is classified as a platform report. Unknown POSTs and any graph/API or explorer-state side effects still fail. [Receipt](docs/evidence/q006/public-v2-job.json).

**Amendment from the actual network trace.** Job `58376328` passed the same ten public UI checks. Its saved trace identifies Cloudflare Web Analytics, not NEL: an injected `static.cloudflareinsights.com/beacon.min.js` script POSTs JSON to the same-origin `/cdn-cgi/rum`. The source HTML and curl response do not include that injected script, so those checks alone did not reveal it. This is existing host telemetry, not graph computation or a submitted map view. Recognize only that proven script/endpoint combination in the browser harness and retain unknown-request/API/state checks. Do not change hosting configuration as part of this demo. [Trace](docs/evidence/q006/public-v2/q006_overview_acceptance/q006-overview-acceptance.json).

**Final public submission.** Job `58377007` received the hash-matched harness at `e3079b9`, with only the proven host-beacon classification added. Public runtime remains the visually accepted `50e5804` implementation deployed through `edeb241`. [Receipt](docs/evidence/q006/public-v3-job.json).

## 2026-11-06 UTC — Q-006 complete and publicly verified

**Outcome.** Final public job `58377007` completed in 17 seconds with all 12 checks passing and no browser errors. The actual domain preserves exact source descriptions, fixed coordinates, overlapping/unresolved homes, phone controls, native touch/keyboard behavior and the original explorer's draft, storage and authored-history restoration. Its observed Cloudflare beacon is recorded explicitly; no graph computation/API traffic occurs. [Final public report](docs/evidence/q006/public-v3/q006_overview_acceptance/q006-overview-acceptance.json).

**Meaning.** The minimal fixed overview is ready for collaborator use at [eigenquestions.com/overview](https://eigenquestions.com/overview), with a new-tab entry on the text explorer. It is a legible global picture of this Swampland collection, using its real shallow hierarchy and provisional labels. It does not replace the contextual navigation construction.

**Save/resume.** This closure changes only documentation, tests and saved evidence; runtime assets remain the publicly verified release. Preserve the failed wheel-coordinate and host-telemetry assumptions as useful reproducibility findings. No cluster job remains. The next substantive work is collaborator feedback, not another speculative UI rewrite.

## 2026-11-06 UTC — Q-007: Distinguish hidden controls from missing hierarchy

**Question.** Why does broad-topic selection not provide the expected next smaller choices?

**Observed.** The fixed export has six children under quantum gravity, while compactification, cosmology and neutrino branches are leaves. The renderer leaves its broad-topic list unchanged and puts child buttons below long details; retained sidebar scroll can further hide them. This is both an access problem and a shallow-data limitation.

**Tried/contributors.** Root assigned Astra protocol the contextual topic list and real parent path, Sol the small accessible UI changes, and Astra data a read-only audit of existing finer partitions. The unassigned bucket becomes a secondary display entry; underlying scientific records remain unchanged.

**Decision/next.** Expose actual children immediately and provide honest source browsing at leaves. Do not attach unstable rejected splits or unrelated alternative trees just to give every button another level. Record the exact data-stop reasons, test the repaired journey, and explain what the current map can and cannot do.

## 2026-11-06 UTC — Q-003 clarification: distinguish local browsing from an agent

**Owner question (summary).** Why does typing update the graph without first connecting an agent?

**Verified explanation.** Overview Find searches existing titles/IDs/topic names and changes camera/selection only. Submitting in the text explorer invokes deterministic browser retrieval: lexical source anchors, their existing vectors and graph neighbors, local direction grouping and a fitted 2D projection. It does not call a language model or freshly embed the typed question. A connected external agent supplies the interpretation, evidence review and an authored structured view through the separate protocol.

**Meaning.** A changing chart is not evidence of agent reasoning. Root explained this distinction directly; the local fallback remains useful, but the interface should distinguish it from agent-guided views. This question does not replace Q-007's active drilldown repair or authorize silently substituting browser heuristics for the broader agentic vision. [Construction](docs/geometry.md) · [Agent interface](docs/agent-interface.md).

## 2026-11-06 UTC — Q-007 paused; explain the current construction

**Owner direction.** “for now just leave it as it is. but explain” follows questions about whether agent updates work and the mathematical tool for the 2D plane. Root stopped the remaining implementation agent. The public site has not received any Q-007 changes.

**Saved state.** Protocol and Sol completed an unpublished contextual-child/parent-navigation draft, including secondary unassigned access. The current draft passed the existing 43 local checks and static build checks. Astra data's hierarchy audit is saved; revised browser tests were not written or run. Preserve this as a draft checkpoint, not as a completed repair.

**Verified explanation.** The page-object apply path and local same-origin companion/MCP path have passed actual browser tests, including exact authored views and render acknowledgements. Public HTTPS-to-loopback attachment was blocked by Chromium local-network policy in the recorded public tests; the local companion page is the tested fallback. Hosted stored-view URLs remain inactive. No claim is made that the owner's current browser tab is attached to an agent.

**Mathematics.** The native dynamic explorer fits weighted PCA to the retrieved direction-group centroids in the existing 384-dimensional MiniLM space. A center and two orthonormal eigenvectors define an affine plane; selected vectors are orthogonally projected and a residual/slab diagnostic is recorded separately. This is not literal intersection of the entire corpus with a plane, nor a learned universal physics coordinate system. The fixed overview instead uses the precomputed first two diffusion modes and never refits its coordinates on Find.

**Resume boundary.** No further implementation or publication until requested. Working-branch save only; leave main/live assets unchanged.

## 2026-11-06 UTC — Q-008: Local collection timeline

**Result.** The 6,477 distinct papers represented in the overview span 1969–2026 (57 years; 2026 incomplete). Their metadata contains 15,449 distinct author-name strings after Unicode/case/whitespace normalization, with no missing author lists. This is not identity-disambiguated people; large experimental collaborations contribute substantially (one ATLAS/CMS record lists 5,308 authors). The peak collection year is 2022, with 477 papers.

**Method/evidence.** Root joined the overview's paper IDs to the frozen navigation catalog, excluding the one catalog-only paper, and counted each ID once. Dates use arXiv year where available and catalog year otherwise. Includes foundational and adjacent literature; this does not certify each paper as a direct Swampland contribution. [Plot](analysis/local-stats-20261106/papers-per-year.png) · [CSV](analysis/local-stats-20261106/papers-per-year.csv) · [summary/input hashes](analysis/local-stats-20261106/summary.json) · [reproduction script](analysis/local-stats-20261106/plot.py).

**Save/boundary.** Rendered with Matplotlib and visually inspected. Saved locally only, outside public assets; no site deployment or GitHub push for this request. Q-007 remains paused.

## 2026-11-06 UTC — Q-009: Separately authorized label-only release

**Request (summary).** Quickly replace “Awaiting a better home” with a clearer label and keep the records tracked. This unpauses only that label change.

**Outcome.** Root used isolated worktree `/private/tmp/eigenquestions-label-fix` from live main `d93a402`, and Astra protocol made three display/search/About line changes. Release `de0cfa3` deployed successfully in workflow `42286692012`; 43 local tests, 22 public asset hashes and 32 retired-route checks pass. The visible label is “Uncategorized excerpts”; all 13 IDs/memberships remain unchanged and are recorded in main's `docs/evidence/q009/uncategorized-records.json`.

**Resume boundary.** This original checkout retains the paused Q-007 draft and local-only Q-008 plot. They were not published. Before resuming Q-007, reconcile with the new main label fix so its wording is not reverted. Q-009 publication evidence and release notebook are saved on main and `agent/uncategorized-label`. This local resume note is not pushed with the private/local plot artifacts.

## 2026-11-16 — Q-010: Recover the integrated research vision

**Question/tried.** Root reread the owner's conversation, the [original navigation request](docs/requests/Q-001-original.md), [contextual-view proposal](docs/Q-003-contextual-view-proposal.md), [showcase](docs/contextual-view-showcase.md), this notebook and the upstream atlas run/steering notes. The owner identified a recurring coordination failure: each new suggestion was becoming the center of a separate plan.

**Synthesis of the owner's intent, not a completed implementation.** Eigenquestions is a living atlas of physics in which people and their agents can understand a field, pursue questions, inspect the supporting science, locate current work and share their own investigations. Swampland is the first substantial test of a construction intended to work across subfields.

- The comprehensive paper collection and swarm supply scientific detail: questions, results, mathematical methods, conventions, assumptions, regimes, derivations and carefully qualified reproduction findings. Multiple vector representations and evidence-linked graph relations make this material navigable; neither similarity nor an audit candidate automatically establishes a physical relation or mistake.
- Collaborators contribute high-level structures and the scientific story of why they matter. Agents connect that picture to the detailed material. Disagreements can expose missing coverage, faulty extraction/geometry or a high-level picture worth improving. Experts should not be tasked with routine paper sorting or every clustering decision.
- A broad overview provides orientation. Contextual navigation reorganizes what is relevant as the question and path change, presenting roughly five useful directions at a time. A concept can have different apparent depth and neighbors along different routes; new relevant sources can enter. The expert picture must remain compatible with this behavior rather than becoming the only permitted tree.
- Researchers can mark and share the questions or connections they are investigating within the same scientific space. As a design interpretation, those markings should follow their scientific referents across views rather than remain tied to drawing coordinates. Detailed collaboration policies are still unspecified.
- A portable agent interface and a quiet, responsive, text-first browser expose the same underlying material. Agents use the atlas for orientation while continuing independent research, compute or author meaningful views, and deliver structured results that the browser can display and share. Scientific computation stays with the agent/browser; optional hosting stores views. A saved view must preserve the actual organization, not just a camera position.
- Research activity and expert/agent findings feed back into the atlas. Preserve sources, uncertainty, useful failures and the reasons for changes in this notebook. Repeat the same construction and evaluation process across subfields while allowing their scientific organization to differ.

**Interpretation/open research.** The unifying problem is how machine-extracted detail, expert organization and a researcher's evolving question jointly determine a useful view without losing evidence or context. Soft constraints, local charts and other geometric tools are candidates; the latest conversation did not select or validate a particular alignment algorithm. Sheaves and a universal physical metric are not established requirements or existing results. The recent expert-map proposal refines the original vision rather than replacing its dynamic navigation or collaborative purpose.

**Meaning/next.** Judge future tasks by whether these pieces work together in an actual scientific exploration, including paths that cross the initial expert boundaries. Root must preserve this whole-picture test when delegating and not infer end-to-end success from isolated subsystem checks. This entry is a conceptual correction only: no runtime change, launch or deployment. Q-007 remains paused. Save locally with the notebook; GitHub publication of this new entry remains pending because this branch also contains explicitly local-only artifacts.

## 2026-11-16 — Q-011: Deliver the confirmed vision through one integrated pilot

**Observed.** The owner explicitly endorsed the Q-010 synthesis and asked what work and personal decisions are needed. The following sequence and defaults are recommendations, not newly approved implementation or sharing policy.

**Proposed work.** (1) Inspect and connect the existing scientific records, relations, representations and viewers, identifying missing information that affects the pilot. (2) Compare ways of mapping an actual expert sketch onto those records while allowing overlaps, contextual reorganization and evidence-backed feedback on both the sketch and machine representation. (3) Complete one usable journey: explore, ask a contextual follow-up, inspect its evidence, mark ongoing work, and share it with another researcher who can continue from another perspective. Preserve the responsive text-first interface and optional independent agent use. Hosted sharing still requires storage activation through authorized access. (4) Use real collaborator work to correct the construction, record the repeatable method, and test transfer to another subfield. Focus deeper reproduction where it resolves consequential uncertain links or assumptions.

**Owner input.** Identify which collaborators' high-level maps are ready to start with; select two or three real scientific questions to judge usefulness; choose the audience for unpublished work markings. Recommended initial scope: existing Swampland collaborators, their active questions, and an explicitly chosen collaborator audience for unpublished activity while the literature map remains public. No unpublished activity will be published based on this recommendation alone.

**Coordinator responsibility/next.** Investigate encoders, alignment objectives, clustering/layout and transport within the accepted vision, reporting meaningful tradeoffs rather than asking the owner to select technical machinery prematurely. The success criterion is the complete scientific journey, not a polished map alone. No jobs, agents, runtime edits or deployment were started. Notebook-only checkpoint stays local on this branch to preserve the existing local-only artifacts; publication remains pending.

## 2026-11-16 — Q-011 amendment: Expert input is optional; preserve the autonomous foundation

**Owner correction (summary).** The delivery plan leaned too heavily on human curation. The system must work without it; expert organization should improve an already functioning atlas. This corrects the dependency implied in the preceding Q-011 plan, while preserving the integrated Q-010 vision.

**Checked evidence.** Root reread the upstream `graph-design/20261105-v1/publication-v1/REPORT.md`, `CONSTRUCTION.md`, and `HUMAN_DIRECTION.md`, plus the local [hierarchy audit](docs/Q-007-hierarchy-audit.md). The autonomous construction already has 8,473 physical-question units from 6,477 papers and 17,937 method units from 6,474 papers, separate MiniLM/Qwen neighborhood graphs, normalized-cut/Leiden alternatives, and eight numerical plus two reviewed views. Astra proposal, challenge and fresh-paper stages reviewed 45 topics. These are sampled organizational checks, not certification of all members. The saved owner direction explicitly placed agent organization before human feedback; no collaborator feedback was fabricated. Some current branches are shallow because proposed refinements failed stability gates; deeper alternative trees exist with different memberships.

**Corrected interpretation/next.** Autonomous organization and question-conditioned navigation are the core. Human maps, stories and corrections are optional inputs that can improve the same representation and receive evidence-backed feedback. Their absence must not block building, using or transferring the atlas to another subfield. Start from the existing emergent structure, investigate its weak regions and navigation behavior, then connect marking/sharing to that functioning core. Expert sketches and collaborator-supplied example questions are useful evaluation material, not required owner decisions before progress. The audience for unpublished work remains a real sharing choice when that feature is used. No new run or implementation is claimed; this is a dated planning correction, saved locally without publishing the private/local artifacts.

## 2026-11-16 — Q-012: Research a physics-wide overview and describable regions

**Question/tried.** Root checked primary documentation for OpenAlex, arXiv and APS PhySH, and the original papers on multiscale Markov stability and seeded heat-kernel communities. This connects the new visualization proposal to the autonomous graph, contextual navigation and research markings already requested; no new corpus or renderer has been built in this turn.

**Source recommendation.** Use [OpenAlex topics](https://help.openalex.org/data/topics/) and [work/reference metadata](https://help.openalex.org/data/works/citations/) as the broad literature substrate. Its topics were originally citation-clustered and labeled; assignments are inferred and citation coverage is incomplete. Use [arXiv categories](https://arxiv.org/category_taxonomy) as familiar navigation landmarks and [PhySH](https://physh.org/about) as a physics vocabulary/coverage cross-check, including systems, properties and techniques as well as research areas. These supplied classifications help bootstrap a coarse view; they do not dictate exclusive scientific ancestry. Audit adjacent engineering/materials topics for photonics and other interdisciplinary coverage rather than filtering only one nominal physics field. Start with cached topic metadata and a balanced literature sample, including reviews and recent work; quantify sampled coverage. Do not initiate full-text extraction across physics. For bulk arXiv metadata, [OAI-PMH is its preferred interface](https://info.arxiv.org/help/bulk_data.html). No API quota/cost estimate is made here.

**Proposed construction, not yet validated.** Two related diffusion operations serve different purposes. [Markov stability](https://arxiv.org/abs/0812.1811) evaluates communities at multiple diffusion times; persistent, source-coherent divisions are candidate zoom levels. [Seeded heat diffusion](https://arxiv.org/abs/1403.3148) identifies a weighted neighborhood around a question or selected region. With row-stochastic transition matrix P and column seed weights s, p(t) = exp[-t(I-P^T)]s. Test finite diffusion scales or restart to avoid losing specificity at equilibrium. Edge types/lenses and normalization must be explicit: citation, text affinity and checked scientific relations have different meanings. Compare with the existing frozen construction; diffusion does not establish semantic correctness, perfectly nested communities or a faithful 2D projection.

**Depth and rendering.** Provide a recognizable broad layout and progressive, legible labels. Reveal roughly five relevant local directions where stable distinctions and evidence support them; detailed Swampland areas can go deeper than metadata-only regions. Physics → high-energy theory → quantum gravity/string theory → Swampland is a useful route, not exclusive ancestry. Join broad and detailed layers through shared paper identifiers and explicit memberships; do not splice incompatible embedding coordinates or let extra Swampland extraction units inflate its global size. Smoothly anchored local charts and cached multiscale summaries should preserve orientation and responsive pan/zoom. Reorganization driven by a new question must remain explicit and distinct from a camera zoom.

**Describing and marking a region.** An agent reads representative and boundary evidence for a weighted region, writes a concise title plus its scientific question, methods and limitations, and exposes supporting sources. A mixed region may need several descriptions. Both selecting a region then requesting a description, and describing work then locating a candidate region, should be supported. A researcher accepts or adjusts the proposed region and attaches their work statement. Save source identities/weights, graph version and construction context with the annotation; drawing coordinates alone are insufficient. This creates a bridge from natural language to the existing graph, including regions spanning multiple named topics. Precompute ordinary overview descriptions; user-agent generation can handle new contextual regions without model calls on every pan/zoom. Expert maps remain optional refinements.

**Next experiment/meaning.** A bounded prototype should show the broad-to-Swampland route, one contextual route crossing a topic boundary, a source-backed description for a selected region, and a work marking recoverable from both routes. Measure stability, coverage, source support and interaction smoothness, retaining failures. This is a method recommendation and next experiment, not a claim of a completed physics-wide map. Notebook-only local checkpoint; no site deployment, cluster/model job or paid data acquisition was performed.

## 2026-11-16 — Q-013: Keep portable results and add optional live presentation

**Question/tried.** Root inspected the existing view schema, browser/controller contract, saved size experiments and storage code, and checked current primary Cloudflare, MCP and browser documentation using the Cloudflare skill/docs connector. No account resources were accessed or changed. A preceding read-only public check found app.js identical to release `40cf90b` (SHA-256 `e23816fbef99d8a44c0e2509b810f86d295753ca781f52c0b8ab470dca68d17d`) and the stored-view read endpoint still returning 503 `storage_unavailable`.

**Result/recommendation.** The original upload-and-link idea remains the portable baseline. A hash identifies bytes rather than reconstructing arbitrary scientific decisions. Preserve a versioned view snapshot plus an optional exact recipe, common data references and continuation context. Return an immutable random-ID read link after durable storage. Optionally pair an open browser with a session; agents make ordinary HTTPS calls, a small hosted relay notifies the browser, and it applies the same object and acknowledges the revision. R2 stores artifacts; a SQLite Durable Object per session coordinates revisions and hibernating WebSockets. MCP and page APIs are adapters to the same semantics. WebMCP remains an optional browser enhancement; read-only web access alone does not grant execution or write capability.

**Consequential subtleties.** Compare against the context at computation start, not a freshly read revision that launders a stale result. Store before committing a session pointer; external R2 I/O is not one transaction with session state. Distinguish saved/accepted/applied/rendered, reconnect from durable state, preserve human drafts and independent browsing, and make retries idempotent. Public/unlisted links do not provide private research sharing; presenting and publishing are separate permissions. Unknown builders may remain readable without claiming reproducibility. Cache immutable public artifacts but not session heads or failed/private reads. Existing size/CPU/admission limits remain explicit; no new cost claims or retention policies were adopted.

**Evidence/next.** [Design, alternatives, references and acceptance cases](docs/Q-013-agent-browser-design.md). Implement by completing authorized immutable storage activation, adding a minimal paired session, and wiring the new physics-wide renderer into the existing accepted-view controller. These are recommendations; no hosted relay, private-session path or new renderer was built. The notebook and design are checked and committed locally; GitHub publication remains pending to avoid pushing this branch's explicitly local-only artifacts.

## 2026-11-16 — Q-014: Unify paragraph and click navigation at the scientific region

**Question/tried.** Root coordinated three research agents: `/root/navigation_mathematics` compared graph operations and their mathematical limits; `/root/navigation_semantics` examined language, context and route equivalence; `/root/navigation_research_audit` inspected actual code, data and saved failures and proposed source-backed test cases. Root reviewed the combined proposal against the full Q-010 vision, checked primary literature and independently reproduced the small heat/linearity calculation. This round used three research agents, not a newly launched Astra/ShirAI corpus swarm.

**Observed.** Current text navigation groups top-64 results around five representatives, while overview uses a separate hierarchy; clicks do not preserve complete region membership. Diffusion alone does not supply logical conjunction, assumptions or question meaning. Repeated heat diffusion extends walk time and can spread influence farther: the synthetic three-node check increased outside-parent mass from 0.0387 to 0.0999. This is a mathematical failure demonstration, not a corpus result. The richer upstream atlas has selective reviewed scientific relations, not all-paper implication coverage.

**Recommendation/meaning.** Both input modes should call one recorded region/action operation. Maintain an automatic overlapping atlas for orientation; allow prose to create new cross-topic regions. Separate membership from relevance, use restart diffusion for evidence and connections, and populate about five source-supported refinements, lenses or explicit pivots. A true refinement narrows scope; a method/application connection need not. Clicks carry exact selectors, not label searches. Known region references replay exactly; arbitrary paragraphs require measured scientific agreement. Layout follows these decisions. This preserves optional human refinement, broad-to-detailed navigation, researcher markings and Q-013 view delivery without requiring a fixed exhaustive tree.

**Evidence/next.** [Synthesis, alternatives and bounded experiment](docs/Q-014-navigation-research.md), with linked mathematics, semantics and audit memos. Freeze twelve cases; first fix state/action equivalence on unchanged inputs, then isolate propagation and grouping gains, then evaluate language/encoder changes. No new corpus benchmark, runtime implementation, deployment or storage activation was performed. All three agents finished. Save only these research documents and this notebook locally; publication remains pending because the branch includes explicitly local-only Q-008 material and the paused Q-007 draft.

**Integration review.** The semantics agent checked the final synthesis against the whole request. Root incorporated three clarifications: preflight each displayed next question against an executable, evidence-supported target; apply assumptions to claims/settings before aggregating papers; and include a minimal paragraph interpreter in the initial state experiment, while deferring comparisons of stronger interpreters. Manual states alone cannot validate the paragraph entry path.

## 2026-11-16 — Q-015: Read SwampWiki as a proposed scientific overview

**Question/tried.** Root read all source/data files of private `sr-744/swampwiki` at `cda0fd3af9c800555a9679e98476452e05ebe183`, using the existing local GitHub login after the connector returned 404. Counted and checked graph IDs, read its navigation code, and checked four selected references against arXiv. No browser run or repository modification.

**Observed.** It contains 19 named claims, 24 typed relations and 33 distinct reference IDs, with editable statements, grade rationales and four assessment axes. Search selects existing nodes; layout is D3 force placement. It supplies no semantic paragraph search, dynamic subdivision or embedding construction. Three of the four checked citation labels mismatch their arXiv records. Some implication edges omit premises recorded in node prose; Dark Dimension is a concrete example. This is a limited source/metadata review, not a complete scientific audit of its claims or grades.

**Meaning/next.** Treat it as an optional authored high-level map to align with our detailed source-backed regions, allowing evidence to refine the proposed map in return. Preserve variants, premises and editorial attribution; do not turn grades into probabilities or impose the map as the atlas's only organization. [Review, precise citation findings and source links](docs/Q-015-swampwiki-review.md). Q-014's bounded navigation experiment remains the next implementation step; a matched SDC/ESC/ADC/Dark Dimension example can later test this alignment. Save this review locally only; no import, external message, public copy or deployment occurred.

## 2026-11-16 — Q-016: Identify the missing query encoder and separate compute costs

**Question/tried.** Root rechecked the browser manifest/engine, upstream encoder comparison and current primary model/runtime documentation. The owner correctly identified that semantic query retrieval needs model inference. The present browser averages existing vectors chosen through lexical matches; that shortcut does not establish comprehension of arbitrary paragraphs. [Current construction](docs/geometry.md).

**Observed.** The live corpus representation has 26,410 question/method vectors of dimension 384: 40.56576 MB of float32 values and 10,141,440 multiply-accumulate terms per exhaustive dot-product scan. These are calculated sizes/operation counts, not latency benchmarks. At 4,096 dimensions the same row count would occupy 216.35072 MB in float16, before index/metadata; a million such rows would occupy 8.192 GB. Broad-physics delivery therefore needs an index/loading strategy separately from model inference.

The [completed encoder comparison](/Users/emmy/Developer/physics-atlas-swampland/encoder-comparison/20261104-v1/publication/RESULTS.md) encoded 26,557 scientific descriptions per Qwen condition; the 296,130-facet full atlas remains MiniLM. Qwen improved selected passage-to-extraction controls while scoring worse on the small, MiniLM-selected relation benchmark. Neither result validates free-paragraph navigation or a universal geometry. Retrieval can use a different encoder from the organization graph by joining exact source IDs, while query/document vectors within a retrieval index must use the compatible model/revision/preprocessing and intended query/document prompts. Do not compare Qwen coordinates directly to MiniLM.

**Recommendation.** Encode the whole contextual question plus a few role-specific aspects, retrieve with lexical and vector signals, then rerank/check a bounded candidate set against the full question and source assumptions. Preserve negation, method/application roles and unknown conditions explicitly; extra dimensions alone do not establish semantic resolution. Precompute corpus embeddings; only new question/aspect vectors require per-query encoding. Repeated saved clicks need no fresh language-model inference. Query encoding is essential to the semantic prototype, with the old lexical-anchor route retained as a declared baseline.

**Compute placement.** A supported compact model can run in the browser through WASM/WebGPU; a capable local agent environment can run larger models; an optional embedding/reranking endpoint offers consistent access without each visitor downloading weights. Encoder weights, vectors/index and agent interpretation are separate workloads. Qwen's advertised 0.6B/4B/8B sizes imply roughly 1.2/8/16 GB for 16-bit weights alone; 4-bit storage is about one quarter before quantization overhead, and runtime memory is higher. These estimates are not tested device requirements. An agent must have an actual encoder tool or service, not invent vectors in prose. For the current corpus, CPU vector search is a reasonable candidate; browser responsiveness and quantized-model quality still require measurement. An all-physics index may be local, sharded or hosted. No hosting, paid service or new model run was selected or started.

**Sources/save.** [Qwen query/document conventions and model sizes](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), [retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html), [browser inference](https://huggingface.co/docs/transformers.js/v3.8.1/en/index). Save this clarification locally with Q-014's next experiment; the current branch remains unpublished for its existing local-only boundary.

## 2026-11-17 — Q-017: Share the detailed atlas across light and heavy execution

**Question/tried.** Root used the cluster-access skill, recovered the installed native guide and saved execution context, read SWA's dated cached connection/queue report, and separately verified native SSH with a bounded no-op command. The cached queue had no matching atlas/navigation job; that is not a fresh full scheduler audit. Read existing Slurm geometry scripts and primary references on late-interaction retrieval, Matryoshka representations, Qwen models and FASRC execution. No new allocation or model run.

**Recommendation/meaning.** Build a rich source-backed reference representation, then derive measured light retrieval packages. Both modes use the same IDs, region/action contract, browser and sharing format. Anyone can inspect a heavy-generated view; extra compute enables new questions, wider retrieval, checking and local organization. Preserve source passages and equations alongside scientific facets and conditional graph links. Test token-level late interaction and joint query/passage reranking as complements to dense retrieval, with explicit assumption checks. Truncated vectors reduce index cost but do not shrink encoder inference or automatically make scientific hierarchies.

**Execution decision proposed.** FASRC performs batch construction and optional bounded active research sessions. Load models once per active allocation; retain the accepted view while work queues/runs, release idle resources and return ordinary versioned artifacts. A capable local GPU or service can supply the same backend. The agent instructions should manage version checks, bounded jobs, isolated outputs, progress, resume and browser delivery using a separate local cluster profile. Shared data access must not imply shared compute credentials. The stated single-GPU memory target is a planning estimate, not a benchmark.

**Evidence/next/save.** [Design, tradeoffs, sources and four-step sequence](docs/Q-017-light-heavy-atlas.md). Start with a heavy reference journey and independent scientific cases; measure the light path against both source evidence and the reference. No new skills/backend, embeddings, site changes or production deployment were implemented. Retain this checkpoint locally under the existing publication boundary; Q-007 stays paused.

## 2026-11-17 — Q-018: Make precomputed atlas navigation the primary path

**Question/tried.** The owner proposed moving the difficult organization ahead of time: a connected agent reads a long query and navigates existing categories to the right scope/depth. Root compared this with Q-014/Q-017, reread the actual hierarchy audit and SwampWiki review, and verified SwampWiki main remains at the inspected `cda0fd3` revision.

**Recommendation/amendment.** Adopt this as the primary v1 experiment. Agent routing through well-defined region records need not encode the query into a retrieval vector; Q-016's encoder requirement applies when vector retrieval is actually used. Heavy computation primarily prepares memberships, descriptions, children and cross-links. Use an overlapping navigational hierarchy with distinct scientific relationships, so routes from different starting points can converge without losing context. A compact URL can reconstruct a precomputed view by atlas version, destination, lens and supported restrictions; arbitrary new scientific context still needs explicit state or Q-013's saved artifact.

**Observed limits and contribution.** The current overview is too shallow to deliver this simply by changing controls. SwampWiki contributes 19 named claim landmarks and 24 typed relations, but no deep category structure or semantic routing. Keep its implications/motivations/tensions separate from narrower-topic links and resolve Q-015's reference/premise issues before verified reuse. Aim for a useful primary location or small related set; a finite taxonomy cannot give every conceivable question a unique exact leaf. Expert correction remains an optional improvement to autonomous construction.

**Evidence/next/save.** [Concrete structure, URL semantics and four-step experiment](docs/Q-018-precomputed-navigation.md). Build one deep neighborhood; test an agent on unseen paragraphs and continued navigation; then verify compact URL replay/manual equivalence and scale the structure. This updates the priority in Q-017 rather than silently erasing its earlier rationale. No code, hierarchy, compute job or deployment changed. Save locally under the existing publication boundary.

## 2026-11-17 — Q-019: Make scientific readability the feasibility test

**Question/evidence.** Root reread the proposed navigation construction, saved hierarchy limitations and the upstream [five extraction examples](/Users/emmy/Developer/physics-atlas-swampland/showcase/20261104-v1/SWARM_SHOWCASE.md) and [earlier topic-card proposal](/Users/emmy/Developer/physics-atlas-swampland/showcase/20261104-v1/CLUSTERING_NEXT.md). The examples preserve concrete questions, methods and conditions with source anchors; they are selected examples, not average-quality measurements. Existing partitions and the 19-node SwampWiki sketch do not yet constitute a deep readable atlas.

**Assessment.** A useful Swampland atlas is technically achievable with the available material, but its editorial/scientific quality must be demonstrated. Author a small explanatory page at each region: its central question and motivation, a few meaningful next directions, representative evidence, and explicit limits. Numerical clusters propose neighborhoods; source review determines whether their commonality supports a useful scientific page. Permit overlap and different depth, and stop where further subdivision adds no understanding. Automated construction can draft/review these pages, with later expert feedback improving them; do not make human curation a prerequisite. A unique exhaustive hierarchy for every possible question is not the feasibility criterion.

**Next/acceptance.** Build roughly 20–30 pages across two connected neighborhoods before scaling. A reader should be able to explain the current region, predict what each next choice offers, recover supporting papers and qualifications, and follow several steps that add scientific specificity. A fresh agent should route unseen paragraphs, preserve context and recognize unmatched questions. Test boundary and omitted evidence as well as attractive examples. This is the next experiment, not a successful usability result. Coarse coverage of physics can precede comparable depth in every field. Notebook-only local checkpoint; no new model/cluster job, atlas content or release.

## 2026-11-17 — Q-020: Correct the uniqueness requirement

**Owner correction.** A unique destination is required. The surrounding scientific questions/literature can differ with context. Root's Q-018/Q-019 suggestion to accept a primary location or small related set weakened this requirement by conflating uniqueness of the question's address with uniqueness of its parent branch.

**Revised construction.** Maintain one canonical, scoped record per accepted scientific question; different formulations and entry routes resolve to that record. Separately select a contextual neighborhood around it. Defining hypotheses/targets belong to question identity; presentation/history belongs to the view unless it changes the scientific meaning. Overlapping classification and different apparent depth remain possible without duplicating destinations. Unique IDs alone do not establish successful semantic normalization.

**Assessment/next.** Canonicalizing questions represented in the bounded Swampland collection is a reasonable concrete goal. The 8,473 exported question descriptions provide candidate material for merging paraphrases and distinguishing substantive variants; they are not a completed canonical catalog. Build the 20–30-destination pilot with route/paraphrase equivalence and contrasting-assumption tests as explicit acceptance requirements. Preserve source evidence, scientific relations and expert merge/split corrections. [Dated design correction](docs/Q-018-precomputed-navigation.md). No new graph, model run, runtime or deployment; save locally under the existing publication boundary.

## 2026-11-17 — Q-021: Keep the shared graph traversable across branches

**Clarification.** The owner points out that extra dimensions must lead naturally into dark-matter cosmology from any approach. Each destination has shared recorded connections. Context changes emphasis, not which scientific connections exist or can be reached. Use the same default neighborhood for the same resolved question/perspective; route history alone must not hide alternative directions.

**Acceptance/next.** Add a cross-field journey without a root reset and inspect the same destination's connections from the opposite approach. Preserve access to additional connections beyond the approximately five foregrounded directions. Keep navigation direction distinct from implication direction. [Design amendment](docs/Q-018-precomputed-navigation.md). This refines the existing pilot; no code, data, jobs or deployment changed. Save locally under the existing publication boundary.

## 2026-11-17 — Q-022: Recover the whole project and reuse the completed foundation

**Question/tried.** The owner stopped further prompt-by-prompt work. Root reread the original request, Q-010's integrated vision and subsequent corrections, the upstream completion reports and mathematical construction, the encoder comparison, the hierarchy audit and the current geometry code. No agents or compute jobs were launched.

**Observed.** The earlier rounds already produced the 6,477-PDF collection and broad extractions, a 296,130-vector MiniLM atlas, Qwen comparisons, question/method affinity graphs, normalized-cut and Leiden alternatives, and Astra proposal/challenge/fresh-paper reviews of 45 topics. The browser uses 26,410 question/method vectors for retrieval and grouping; it does not encode new prose directly. Some alternative trees reach depth eight. The selected reviewed overview is shallower, and sampled reviews leave explicit organizational concerns. These are existing results, not future prerequisites. [Upstream completion account](/Users/emmy/Developer/physics-atlas-swampland/README.md), [encoder results](/Users/emmy/Developer/physics-atlas-swampland/encoder-comparison/20261104-v1/publication/RESULTS.md), [map results](/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/publication-v1/REPORT.md), [hierarchy audit](docs/Q-007-hierarchy-audit.md), [browser engine](lib/geometry/index.mjs).

**Correction/meaning.** Saying embeddings and clustering “should” be used made completed work sound hypothetical. The remaining integration problem is how the existing evidence, geometry and reviewed organization support a coherent research experience. The whole objective remains: broad physics orientation; deep Swampland exploration by clicks or conversation; one destination for each scoped question; connections accessible across entry routes; source inspection; and eventually researchers locating, marking and sharing their work. Roughly five clear directions and an arXiv-like text-first interface serve that experience. Precomputation makes ordinary navigation cheap; the agent can still use richer tools when needed and continues independent research. Expert maps improve the autonomous atlas rather than gate it. URLs and stored views deliver the same scientific state rather than define its organization.

**Resume boundary.** Stop new design and implementation for this catch-up. Do not restart corpus collection, embedding or clustering by default. On resumption, use existing artifacts and identify which concrete gaps prevent the complete journey; assess proposed work against that journey and the repeatable cross-subfield construction. No new algorithm was selected or validated, and no canonical catalog, physics-wide map, work-marking feature or release was built here. Notebook-only checkpoint, retained locally under the existing publication boundary.

## 2026-11-17 — Q-023: Make the next increment a connected atlas release

**Question/tried.** Root checked the original [requirements](docs/Q-001-plan.md), [view/interface requirements](docs/Q-003-Q-004-implementation-plan.md), and Q-010–Q-022 against the saved state. Existing v1 acceptance remains evidence for its bounded behavior; it does not validate the later canonical-destination/precomputed-atlas design.

**Recommendation.** Assemble a single readable Swampland navigation structure from the reviewed map, source records and existing candidate refinements. Repair identified weak regions rather than start a new global encoder comparison. Keep the full corpus accessible; use representative journeys to diagnose and test the construction, not hardcode a small demonstration. Give accepted scientific questions stable scoped identities, preserve cross-topic connections, and make manual choices and an agent reading the same records resolve to the same destinations. Connect this to the existing renderer/controller and compact versioned addresses. Test extra dimensions ↔ dark-matter cosmology plus independent source-backed journeys, paraphrase convergence, contrasting assumptions, evidence access, Back/reload and smooth interaction. Ordinary prepared destinations do not require hosted view uploads.

**Requests retained and sequencing.** Derivations, assumptions, methods, phenomenology and recent work on/using a concept must remain accessible, with dates bounded by corpus coverage. Keep quiet arXiv-like text, clear paths, large controls and the separate overview. Then extend the same atlas with a coarse all-physics entrance and work statements attached to stable scientific referents; no public sharing of unpublished work is assumed. Expert story/correction input remains optional and should preserve feedback to both human and machine organization. Agent discovery/readable records, independent research instructions, manual view import, and existing browser control remain part of the product. Hosted arbitrary-view storage still needs activation and live verification; its historical access failure is not a new account check. Retain extraction/steering showcases and the repeatable construction record. Sheaf machinery and another deep-reproduction campaign are not prerequisites for this increment.

**Status/save.** This is a bounded delivery recommendation, not a new implementation or successful acceptance run. No agents, jobs, model runs, resource changes or deployment. Notebook-only local checkpoint under the existing publication boundary.

## 2026-11-17 — Q-024: Let scientific structure determine the groups and depth

**Owner correction.** O(5) means approximately 1–15 directions. Earlier wording overemphasized five. This is an interface scale, not the number of communities to impose. Historical experiments and the current five-direction runtime retain their recorded settings until deliberately revised.

**Evidence/recommendation.** Root rechecked the existing [construction](/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/publication-v1/CONSTRUCTION.md) and [hierarchy audit](docs/Q-007-hierarchy-audit.md). Numerical candidates already come from paper-balanced embedding affinities, normalized cuts and Leiden at several resolutions, with seed/edge sensitivity checks. Use question organization as the primary candidate map and retain methods as a distinct, connected view. Source-backed descriptions, not whole papers assigned to one exclusive box, are the current units. Agents should inspect central, boundary, excluded-neighbor and fresh evidence; define a common scientific scope; challenge proposed memberships and distinctions; and test revisions on unused examples. This extends the earlier sampled proposal/challenge/fresh-paper process rather than replacing it with unconstrained label generation.

**Acceptance/limits.** Retain coherent useful subdivisions, repair or represent overlaps where needed, and stop where a split adds no scientific distinction. Numerical stability is evidence of repeatability, not proof of scientific meaning; a failed gate does not prove a field has no subtopics. Do not silently relax recorded gates or splice incompatible parent/child memberships. A genuine child narrows its parent's scope; related applications/methods can instead be explicit cross-links. Multiple region memberships reuse one canonical scientific destination. Cluster in the original graph/vector representations; derive the 2D display afterward. Freeze accepted definitions and memberships for ordinary click/agent navigation. No new partition, review or runtime change was performed here; local documentation checkpoint only.

## 2026-11-17 — Q-025: Start a coordinated research and delivery loop

**Question/tried.** The owner explicitly authorized a sustained multi-Astra goal and deployment. Root created that goal, reread cluster/hosting guidance, verified current native SSH access and fetched the existing Git remote. Managed worktree creation failed because the task root is outside the repository; a native Git worktree from the verified live main was created instead. The prior checkout, local-only plot and paused UI draft remain intact. Relevant continuity notes were copied; no source corpus or runtime was changed.

**Contributors/running.** Three Astra xhigh agents own isolated geometry, scientific-evaluation and integration directories. Their common brief requires executed alternatives, real source challenges, unique destinations, cross-field traversal, 1–15 readable choices, graph/vector distinctions and a shared browser/agent contract. No new model inference service or Slurm allocation has been launched by root. Existing scientific reviews remain qualified and withheld findings remain withheld.

**Meaning/next.** The next evidence must be comparative artifacts and complete-journey tests, not another general architecture memo. Root will reconcile the common contract, steer scientific/numerical disagreements, inspect failures and then assign implementation ownership. [Atomic requirements and iteration sequence](docs/Q-025-atlas-delivery.md). This clean branch is eligible for project checkpoint publication while the old branch remains protected; no new public release is claimed.

**Access amendment.** The Cloudflare connector's identity/spec reads succeeded, but its actual account-list call was rejected with “MCP tool call requires approval, but approval policy is never.” No alternate credential path was attempted. Existing authorized GitHub static deployment remains the release path; hosted arbitrary-view storage activation is blocked by this access restriction. Local/manual artifacts and prepared-state URLs can still be implemented and tested.
