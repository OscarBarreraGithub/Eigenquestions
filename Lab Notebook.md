# Lab Notebook

## Now

- **Project/question:** Eigenquestions. Implement the authorized Q-003 stored-view journey and Q-004 quieter text interface. Can an agent's complete contextual view travel intact into a responsive browser?
- **Known:** Live v2 passed its public checks. The startup flash comes from hardcoded KK shell/default state before restoration. Independent Sol review found too many headings/controls before the scientific choices.
- **Unfinished/running:** Astra protocol/backend and Sol UI are implementing; Sol's initial review is saved. No cluster jobs submitted yet. Cloudflare account discovery is approval-blocked, so hosted storage activation is pending; no subscription/bucket changed.
- **Next:** Integrate the capsule, neutral startup, quiet layout and bounded upload API; then freeze a checkpoint for Worker and real-browser validation. Preserve exact authored scientific decisions.
- **Git:** Working branch `agent/stored-views-quiet-ui`, from remotely verified Q-003 research checkpoint `31aaa00`. Coordinator `/root`; agents own implementation. Existing main deployment remains authorized.

## Requests

**Q-001 (summary):** Replace Eigenquestions with a static, conversation-guided physics explorer. An agent navigates the real graph and embeddings through a machine-readable interface; deterministic local code recomputes a question-dependent 2D view and about five next directions. Demonstrate KK towers → dark matter → Dark Dimension, support derivation/phenomenology/recent-work intents, provide portable agent instructions, and iterate under Astra implementation with central integration review. Keep this notebook and verified Git checkpoints. [Original prompt](docs/requests/Q-001-original.md) · [Atomic plan](docs/Q-001-plan.md).

**Q-002 (summary):** Make v2 a polished, text-first successor to the old viewer, with labels supplied by the new dynamic computation. Use arXiv's familiar palette/type aesthetic, a clear current path, easy New path, large discoverable controls and exceptionally smooth interactions. [Original prompt](docs/requests/Q-002-original.md) · [Atomic plan](docs/Q-002-plan.md).

**Q-003 (summary):** Let agents consult the physics graph as an optional supplement to their ordinary independent research, discoverable by name and useful without a local installation when their tools permit it. Preserve the original agent → structured scientific object → deterministic computation → browser rendering model. Evaluate URL delivery of agent-computed views while retaining context-dependent grouping, labels, relations, changing depth and enough state to continue; do not assume a matrix or main node encodes the full organization. [Proposal](docs/Q-003-contextual-view-proposal.md).

**Q-004 (summary):** Implement Q-003's stored-view proposal, preserve the vision and a concise future showcase of the mechanism, fix the KK-to-restored-topic startup jump, and have Sol agents iterate toward a familiar, minimal, sharp text-first interface with less competing for attention. [Original request](docs/requests/Q-004-original.md) · [Joint atomic plan](docs/Q-003-Q-004-implementation-plan.md).

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
