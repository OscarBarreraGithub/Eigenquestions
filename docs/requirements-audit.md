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

### Observed protocol checkpoint — 2026-11-06 UTC

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
passes the skill validator; fresh-agent behavioral evaluation remains a separate
gate. [Agent setup](agent-interface.md) documents the commands and limitations.

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
evidence. At this checkpoint that browser run, fresh-agent skill test, final
computation pin, public replacement and remote Git verification remain pending
under the coordinator's plan.

Scientific limits are explicit: this is a frozen Swampland-centered corpus, ON vs
USING is inferred from question/method facets, extracted descriptions require
paper checks for substantive claims, source anchors substitute for a live query
encoder, and proximity/group membership does not prove a physical relationship.
The local bridge is process-local and exports sessions for durable replay;
public HTTPS access may require permissions or the same-origin fallback.
