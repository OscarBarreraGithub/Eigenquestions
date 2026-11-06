# Lab Notebook

## Now

- **Project/question:** Eigenquestions, Q-005: why does home resume a long KK method, why is it repeated, and what alternatives were available along the path?
- **Known:** Bare startup restores saved state automatically; source selection uses the full method as its canonical query. That query is repeated by multiple UI elements. The reported paragraph is one method unit from paper 1303.2661. Actual user browser storage has not been inspected.
- **Unfinished/running:** Implementation and 35 local tests pass. The reported phone alignment is repaired. Final harness expectations are corrected and 35 local tests pass; the next integrated browser run is being prepared. Q-003 hosted storage remains inactive under the previously recorded connector approval restriction.
- **Next:** Freeze the repaired entry/choices/return behavior and verify the reported journey in a real browser, including authored-history safety and phone layouts. [Q-005 plan](docs/Q-005-plan.md).
- **Git:** Corrected prototype `bbea301` is pushed and verified on `agent/stored-views-quiet-ui`; the public site is still the earlier version. Coordinator `/root` owns checkpoints and release.

## Requests

**Q-001 (summary):** Replace Eigenquestions with a static, conversation-guided physics explorer. An agent navigates the real graph and embeddings through a machine-readable interface; deterministic local code recomputes a question-dependent 2D view and about five next directions. Demonstrate KK towers → dark matter → Dark Dimension, support derivation/phenomenology/recent-work intents, provide portable agent instructions, and iterate under Astra implementation with central integration review. Keep this notebook and verified Git checkpoints. [Original prompt](docs/requests/Q-001-original.md) · [Atomic plan](docs/Q-001-plan.md).

**Q-002 (summary):** Make v2 a polished, text-first successor to the old viewer, with labels supplied by the new dynamic computation. Use arXiv's familiar palette/type aesthetic, a clear current path, easy New path, large discoverable controls and exceptionally smooth interactions. [Original prompt](docs/requests/Q-002-original.md) · [Atomic plan](docs/Q-002-plan.md).

**Q-003 (summary):** Let agents consult the physics graph as an optional supplement to their ordinary independent research, discoverable by name and useful without a local installation when their tools permit it. Preserve the original agent → structured scientific object → deterministic computation → browser rendering model. Evaluate URL delivery of agent-computed views while retaining context-dependent grouping, labels, relations, changing depth and enough state to continue; do not assume a matrix or main node encodes the full organization. [Proposal](docs/Q-003-contextual-view-proposal.md).

**Q-004 (summary):** Implement Q-003's stored-view proposal, preserve the vision and a concise future showcase of the mechanism, fix the KK-to-restored-topic startup jump, and have Sol agents iterate toward a familiar, minimal, sharp text-first interface with less competing for attention. [Original request](docs/requests/Q-004-original.md) · [Joint atomic plan](docs/Q-003-Q-004-implementation-plan.md).

**Q-005 (summary):** Fix the unsolicited start at the long KK one-loop method, repeated copies of that paragraph, and unclear adjacent choices at each visited level. Keep full scientific context while making navigation concise and each branch understandable. [Atomic plan](docs/Q-005-plan.md).

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
