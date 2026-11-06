# Q-001 independent requirements audit

Auditor: Astra `navigator_protocol`. Authority: [original request](requests/Q-001-original.md).
This audit distinguishes owner requirements from implementation choices; status is not a claim of completion.

| Distinct request clause | Plan coverage | Interpretation / acceptance risk |
|---|---|---|
| Most topics are deep; about five directions on screen | R07, R08 | Limit *choices*, not necessarily evidence points. Depth must arise from context, not prewritten stages. |
| Explore different ways of collecting directions | R21, R22 | Compare grouping and chart alternatives with recorded failures; one successful screenshot is insufficient. |
| Start broadly at KK towers in a much larger physics space | R07, R14–16, R32 | Existing Swampland corpus is a scoped v1. Do not imply complete physics coverage. |
| Ask what the person wants: derivation or phenomenological implications | R09–11, R24 | Structured intent is selected from conversation; clarify only when materially ambiguous. |
| Recent work **on** towers or **using** towers | R12, R39 | Recency and relation are independent fields. Both must affect retrieval and preserve dated evidence, not merely change a label. |
| Towers as dark matter → Dark Dimension → Swampland Dark Dimension | R13, R20, R33 | Verify source-grounded contextual emergence. Dark Dimension may occur earlier at low rank; arbitrary hiding would overconstrain the request. |
| Slice changes iteratively with questions; not fixed zoom and clustering | R17–19, R40 | Demonstrate candidate changes and recomputed geometry from the same focus under changed intent. |
| Tell an agent the steps; agent has instructions to carry them out | R09, R23, R24 | An external agent must translate dialogue into operations with usable schema, evidence access, and recovery instructions. |
| Run code locally to construct the 2D hyperplane and HTML or equivalent | R17, R18, R26 | A portable renderer input is allowed by “or whatever”; actual local deterministic execution remains required. |
| Domain renders with browser and updates as agent navigates | R27–30 | JSON output alone fails. Demonstrate agent operation → displayed view without manual JSON editing. |
| Agent-native object through MCP or suitable alternative | R16, R23 | MCP is preferred, not mandatory; object operations must not depend on simulated UI clicks. |
| Conversation makes deep connections through actual graph and latent vectors | R14–20, R25 | Semantic proposal by agent, numeric execution by engine, citations by stable IDs. Similarity is not physical proof. |
| Ensure sensible intersections of 2D hyperplane | R18, R20 | Explain projection vs affine plane and finite thickness honestly; a literal exact intersection of discrete vectors is usually empty. |
| Teach anyone's agent rules, questions, navigation, math, avoidance, troubleshooting | R24, R31 | Portable skill and documented commands, tested outside implementation context. No dependency on one assistant's hidden memory. |
| Figure out graph/vector navigation, transforms, improve graph itself | R15–22, R32 | Evaluate graph construction; justify retained pieces or bounded changes with evidence. |
| Iterate toward a sensible tool | R06, R20–22, R31, R33 | Cross-field/held-out checks and failure handling must drive real revisions. |
| Save prompt, actionable atomic plan, double-check all details | R01, R02, R40 | This clause-level audit accompanies the saved request and plan. |
| Prevent delegated pieces from breaking broader idea | R05, R33, R34, R40 | Shared contract early and engine → interface → browser integration gates. |
| Find source, take down old domain app, overhaul into one static v1 | R03, R28, R29 | Preserve rollback while retiring old functionality. “Take down” is fulfilled by replacing it, not requiring avoidable downtime. |
| Set goal and loop until working | R06 | Release and known limits belong in goal completion criteria. |
| Astra agents implement; coordinator mostly audits whole product and steers | R05, R34 | Explicit file ownership and central requirement review. |
| One concise notebook in actual project | R03, R04, R38 | Existing/new notebook confirmed against repository context. |
| Short Now: question, knowns, unfinished/jobs/attention, next step | R04, R37 | Keep current without copying logs. |
| Dated progress: question, attempt/contributors, observations/evidence, meaning/next | R04, R35, R38 | Preserve useful failures; distinguish plans, observations, interpretations. |
| Links rather than raw logs; dated corrections rather than silent historical rewrite | R04, R37, R38 | Coordinator owns notebook updates. |
| Request ID and labeled summary, no whole conversation copied into notebook | R01, R04, R35 | Q-001 exact prompt separately; summary once in notebook. |
| Ordinary Git checkpoints, save before pause/handoff/completion | R35, R37 | Intended changes and notebook together; no per-tool commits. |
| Outcome subject; Request/Agent body; contributors and validation; preserve unrelated work | R35 | Coordinator integration responsibility. |
| Push when configured/authorized; verify remote; honest save status | R36 | Local commit is not evidence of publication. |
| Recover from Now and dated entries; inspect jobs, changed assumptions | R37 | Resume existing work, don't repeat blindly. |
| Small overhead, researcher-readable, no new tracing/memory system | R38 | Session history is product navigation data, not an extra project logging service. |
| Lead replies with research outcome and save status; disclose failures | R35–40 | Reporting obligation applies at checkpoints/completion. |

## Findings before implementation

No owner clause is absent from R01–R40. The important under-specified detail was orthogonality of recency and **on/using** relation; the shared state makes these separate fields. Contextual emergence does not require suppressing relevant papers in earlier views. Approximately five refers to next choices. The plan's 3–6 range, preservation of the old database, exact schema/API, HTTPS origin controls, and paired construction experiment are defensible implementation/acceptance choices, not verbatim owner requirements. A literal geometric intersection is not promised: chart output must state the metric, affine plane, residual and finite thickness.

## Completion audit

### Historical protocol checkpoint — 2026-11-06 UTC, before browser/fresh-agent trials

The independent [integration suite](../tests/integration/navigation.test.mjs)
passes six tests against the real corpus and common geometry engine. It verifies:

- KK towers → pronoun dark-matter refinement → deeper decay refinement → Dark
  Dimension; fresh anchors on each refinement, source-grounded emergence and
  changed candidate IDs/coordinates, plus exact back/replay/export/import.
- Distinct derivation, phenomenology, recent ON and recent USING computations,
  including different bases and ranked neighborhoods; the `using` shorthand is
  consistent across CLI and canonical session operations.
- An independently chosen held-out route, black-hole evaporation → information
  paradox → islands/replica wormholes, with new sources entering from outside the
  first chart. Its expected papers were not supplied as tuning targets.
- Honest empty/unsupported query results, malformed/stale state rejection,
  computation-fingerprint mismatch rejection, and another small subfield fixture
  using the same engine and protocol.
- A spawned stdio MCP process invokes the loopback bridge; the resulting SSE
  event and subsequent state inspection agree exactly. Authentication, rejected
  foreign origins, allowed public-origin preflight and explicit renderer
  acknowledgements have automated checks.

These are technical acceptance results, not independent validation of every
indexed physics claim. The portable [skill](../skills/physics-navigator/SKILL.md)
passed the skill validator; fresh-agent behavioral evaluation was then a separate
pending gate. [Agent setup](agent-interface.md) documents the commands and limitations.

Two useful failures changed the implementation. The initial weak focus blend
ranked generic dark-matter sources ahead of the intended contextual connection
and drifted toward generic moduli on a decay follow-up. Refreshed current-view
anchors plus the geometry owner's joint context scoring resolved the tested
journey. The initial source-vector 2D chart retained only about 10% of source
variation on the owner path; the revised primary chart fits dynamic direction
means and explicitly separates group fidelity from the source overlay and
within-group spread. This avoids presenting an attractive projection as faithful
source-level geometry.

The full product chain is now represented by executable interfaces: an agent
resolves dialogue into query/intent/relation; immutable session transitions store
bounded active source context; the frozen graph/vector engine computes candidates,
five directions and an affine chart; CLI or MCP publishes a snapshot through the
local bridge; the static renderer consumes it and acknowledges the rendered
state/revision. The public app can independently run the same modules in a worker.

The [browser acceptance script](../tests/integration/browser_acceptance.py) is
prepared for the authorized Slurm Playwright environment. It checks actual visible
updates, five direction markers and optional full source overlays, a deeper owner
journey, held-out navigation, import/replay, reload reattachment, render
acknowledgements, mobile overflow and a real HTTPS-public-origin loopback probe.
An HTTP test that merely sends an Origin header is not counted as browser-policy
evidence. At that checkpoint the browser run, fresh-agent skill test, final
computation pin, public replacement and remote Git verification were pending.

### Independent acceptance update — 2026-11-06 UTC, before public replacement

The authorized Slurm Chromium run (job 58185518, exit 0) completed all **12 actual
browser checks**, with zero page errors. The [machine-readable result](evidence/browser-v1/browser-acceptance.json)
records MCP → geometry → visible renderer changes with current-state render
acknowledgements across the owner and held-out journeys, five primary directions
and the optional source overlay, backtracking, export/import and reload
reattachment. The coordinator visually inspected the screenshots. This establishes
the same-origin local fallback end to end; it is no longer merely a prepared test.

The old public origin's loopback fetch returned `TypeError`. That result does not
isolate browser private-network restrictions from the old site's CSP or network
policy. The new deployed origin still needs its own probe. The first mobile view
passed overflow checks but its screenshot exposed tiny labels; the site owner
revised mobile markers and labels, and the test now measures marker diameter,
touch area, number font size and retained direction-card text. That visual fix
still requires its rerun at this update.

The [fresh-agent trial](evidence/fresh-agent-trial.md) is a qualified success:
an independent agent loaded the portable instructions, used the real CLI for
eight axion/WGC/EDE/axion–dilaton navigation actions, inspected source evidence,
compared a same-query pivot and saved a [portable nine-state session](evidence/fresh-agent-session.json).
It did not test first-time installation or browser rendering, and correctly
reported its absent viewer acknowledgement. Those limits are distinct from the
separate browser pass.

The trial found a residual quality failure: selecting a long EDE method paragraph
let generic instanton methods dominate subsequent context. Explicit application
wording plus source anchors recovered a useful path; both changed, so the trial
does not isolate one as the cause. A [separate query-length comparison](geometry-experiments.md)
found that blindly shortening selections to their first sentence could erase the
physical application and worsen retrieval. The engine is therefore unchanged;
the skill now tells an agent to retain the physical application explicitly after
a method selection and distinguish shared-method neighbors from application
evidence. Directions are useful nearby proposals, not a certified ontology or
curriculum, and the engine does not automatically diagnose scientific topic drift.

Source reading also exposed a substantive caveat missing from a short nomination:
the evaluator found that 1605.05311's added note reports counterexamples to its
precise lattice-WGC formulation. Its nomination is therefore not a proof of a
universal axion bound. This observed example supports the existing requirement to
read original papers before making consequential physics claims. In the fresh
trial, group retained variance was 66.3–75.1%, while source-overlay retention was
12.6–21.1%; a high five-group recall@5 is trivial and not independent validation.

The engine and full data fingerprint are now pinned. Coordinator checkpoint
`47374b8812649a758ff891833ab4ca389864cfcc` was pushed and verified. Remaining release
gates are the mobile rerun, replacing the public app, an independent public-browser
compute/UI journey even if loopback is blocked, exact deployed asset hashes,
GET/POST retirement of old routes, and release-branch remote verification. The
[publication helper](../tests/integration/publication_check.mjs) performs bounded
hash/route checks after deployment; its fixture test detects both stale modules
and a surviving legacy API. It does not publish anything or substitute for a
browser run.

Scientific limits are explicit: this is a frozen Swampland-centered corpus, ON vs
USING is inferred from question/method facets, extracted descriptions require
paper checks for substantive claims, source anchors substitute for a live query
encoder, and proximity/group membership does not prove a physical relationship.
The local bridge is process-local and exports sessions for durable replay;
public HTTPS access may require permissions or the same-origin fallback.

### Integrated R40 audit — 2026-11-06 UTC, validated release source; public check pending

The corrected [second browser run](evidence/browser-v2/browser-acceptance.json)
(Slurm job 58187676, exit 0) passes **14 checks** with zero page errors. In addition
to the earlier complete agent journey, it measures readable mobile markers and
touch targets, clicks an actual marker, and restores the exact prior state with
Back. The coordinator inspected the [viewport screenshot](evidence/browser-v2/mobile-chart-viewport.png).
Source `ad144254b51f103d89e0080f67e0a60097ee29e9` is verified on remote `main`;
runtime source is unchanged from the tested `f9e4e50` checkpoint. The deployment
workflow is running; this statement is not yet a claim about served public bytes.

The implemented behavior satisfies the owner's broader picture through one
connected path, rather than separate geometry and UI demonstrations:

1. **Conversation chooses the question.** A fresh external agent uses the skill
   to turn a request into query, intent, ON/USING relation and optional source
   anchors. Derivation, phenomenology and recent work are separate operations,
   with date and role limits exposed. The agent can ask a clarification where
   ambiguity matters; the public static site itself does not interpret dialogue
   with a model.
2. **Context becomes reproducible state.** Refine refreshes bounded source
   anchors from the current view, so KK towers → “what if they are dark matter?”
   → “how do they decay?” carries evolving context. Explicit anchors permit
   recovery; pivot and broaden release it. History, back/replay, portable exports
   and a computation fingerprint make the same resolved question recoverable.
3. **The graph and real vectors select new material.** Every operation searches
   the whole frozen corpus, combining source-term anchors, 384-dimensional
   embedding scores and graph diffusion. It does not restrict a child to an
   inherited cluster. Dark Dimension work becomes salient in the dark-matter
   context, and held-out black-hole questions bring in sources outside their
   initial chart. Removing vector or graph contributions changes retrieval.
4. **The local chart is recomputed.** About five representatives and their
   memberships are recomputed from that neighborhood. Weighted PCA fits their
   weighted means in the same ambient space; the optional source overlay uses
   the same affine plane. Changed intent changes both selected sources and the
   fitted basis. Metric, center, basis, residual thickness, distortion and
   source/group diagnostics remain inspectable. This is a question-conditioned
   local projection, not a unique global map or literal exact intersection of
   a plane with every discrete source vector.
5. **Agent operations reach the displayed object.** The CLI and actual stdio MCP
   tools call the same session/engine code as the browser. The local companion
   publishes the computed snapshot; the static renderer updates; an exact
   state/revision acknowledgement confirms the render. The 14-check browser run
   follows this complete route, including deeper refinement, held-out navigation,
   reload and a human selection. There is no manual JSON-editing handoff.

This is a useful v1 with bounded scientific reach. Five proposed directions are
not five guaranteed valid deductions or a pre-certified curriculum. Selection of
a mathematical method can drift away from the physical application; the fresh
trial demonstrated that failure and an explicit recovery. High direction-mean
fidelity does not remove large source-level distortion, and a source nomination
can omit consequential caveats. The dataset covers 6,478 catalogued papers,
6,477 with vectors, and 26,410 extracted facets in a Swampland-centered snapshot;
it is neither all physics nor a live latest-paper service. Another small fixture
demonstrates interface reuse, not validated relevance throughout every subfield.

No additional omitted clause was found on the final prompt/plan comparison.
R01–R28 and R31–R35 have implementation or process evidence at the scope stated
above. R29, the new-origin part of R30, the public part of R33, and final release
publication verification remain open until the coordinator supplies deployed
hashes/routes and the clean public-browser result. R36 has verified release-source
publication; the final evidence checkpoint still needs its ordinary Git save.

### Public replacement verified — 2026-11-06 UTC; public-browser run pending

The coordinator reports successful deployment workflow
[42161918681](https://github.com/OscarBarreraGithub/Eigenquestions/actions/runs/42161918681)
for remote-main source `ad144254b51f103d89e0080f67e0a60097ee29e9`. The independently
read [publication receipt](evidence/Q-001-publication.json) confirms **9/9 exact
public asset hashes** and **32/32 retired-route GET/POST checks** at
`https://eigenquestions.com`. The served entrypoint, renderer, worker, geometry,
protocol and corpus manifest match the expected release; old quiz/taste/explore,
voting/review/submission and other checked API routes return retired statuses.
R29's deployed-replacement condition is now met.

The clean public-browser job 58188305 has been submitted with `--public-ui` to
test browser-local computation and interactions independently of bridge access,
and to probe the new public origin's loopback behavior. Its result is still
pending at this update; exact served bytes alone are not counted as a public UI
or public-to-loopback browser pass.

### Public-browser result — 2026-11-06 UTC; bounded diagnostics still pending

Slurm job 58188305 completed with all **17 checks** passing and no local or public
page errors. The [public-browser result](evidence/public-v1/browser-acceptance.json)
adds clean public-site computation, contextual form submission, changed ON/USING
source rankings, direction selection, Back, export/import and reload to the
previous local-agent checks. Thus the static public product is demonstrated
independently of the local bridge.

The new public origin still returned `TypeError` for a loopback request. The
coordinator checked that this response has no CSP restriction, while the bridge
provides its expected CORS/private-network headers. The evidence currently
supports a tested public-site-to-loopback limitation, not a proven diagnosis or
a claim of universally working attachment. A final bounded browser run will read
permission states, retain sanitized console/network failures and test graceful
failed-attachment recovery without granting permissions or disabling browser
security. The same-origin live-update path is already verified.

Visual review of the public screenshot also found a desktop direction label
covering a marker. The site owner corrected label placement without changing
the computed geometry. Its source tests pass; the final browser run will measure
label/marker separation on the actual public USING view. These pending checks
are targeted follow-up to observed failures, not additional unbounded product
scope.
