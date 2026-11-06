# Q-001 — Question-conditioned physics navigation

The owner’s [original request](requests/Q-001-original.md) is the authority. This is
an atomic implementation and acceptance plan; statuses below distinguish implementation checks from unfinished release gates. “Slice” means a
question-conditioned local chart computed from real vectors and graph structure;
the mathematical implementation must distinguish projection, an affine plane,
and a finite-thickness neighborhood. A fixed tree or precomputed slideshow does
not meet the request. The UI and agent must operate on the same state and engine.

## Requirements and acceptance evidence

| ID | Atomic requirement | Acceptance condition | Owner / status |
|---|---|---|---|
| R01 | Preserve the full request separately from the notebook. | Original prompt saved verbatim; notebook links to it. | Coordinator / saved |
| R02 | Audit this plan against every part of the request. | Independent Astra coverage audit maps clauses to IDs and finds/resolves omissions. | Protocol / clause audit complete |
| R03 | Confirm the actual Eigenquestions source and hosting. | Local Git remote, branch, deployment configuration and live domain checked. | Coordinator / source, hosting and replaced live domain verified |
| R04 | Maintain one concise notebook in the project. | Now, request summary, dated evidence/decisions and next actions stay current. | Coordinator / one notebook current through v1 completion |
| R05 | Delegate implementation to Astra; coordinate integration centrally. | Owned files, shared interface and integration gates; coordinator does not implement the product. | All / three Astra implementation owners plus independent Astra trial; root coordinated |
| R06 | Set an active goal and iterate until the v1 works. | Goal includes public deployment and end-to-end validation; unresolved requirements remain explicit. | Coordinator / scoped v1 implemented, validated, deployed and preserved in completion checkpoint |
| R07 | Make navigation deep without imposing a single fixed topic tree. | A multi-step context can refine, pivot, broaden, backtrack and branch without exhausting prewritten routes. | Protocol / multi-step actual browser journey passes |
| R08 | Show approximately five meaningful directions at each step. | Bounded choices (normally 3–6) derived from the current context; no unbounded topic wall. | Geometry + UI / five directions, readable mobile markers and nonoverlapping public labels verified |
| R09 | Retain conversation history as machine-readable navigation state. | Explicit intent, focus, lens, constraints, previous steps, snapshot and stable source IDs survive export/replay. | Protocol / state, history and replay tests pass |
| R10 | Support “how is it derived?” as a navigation intent. | KK-tower derivation intent retrieves source-grounded mathematical descriptions and changes the view. | Geometry / real derivation retrieval checked |
| R11 | Support physical/phenomenological implications as a distinct intent. | Same focus with changed intent yields an appropriately different ranked neighborhood and directions. | Geometry / intent counterfactual checked |
| R12 | Support recent work on a concept and work using it. | Explicit mode and dated corpus scope; citations and methods can distinguish subject from tool; ambiguous evidence is shown. | Geometry + protocol / role and date checks pass; role remains inferred |
| R13 | Implement the owner’s KK towers → dark matter → Dark Dimension journey. | Dark-matter context introduces relevant Dark Dimension work from real source records without hardcoded screen transitions. | All / real owner path passes through MCP and browser |
| R14 | Reveal context-relevant connections across previous topic boundaries. | Re-entry from the global corpus/graph is possible; child candidates are not restricted to an inherited cluster. | Geometry / global re-entry tests pass |
| R15 | Use real high-dimensional embeddings and graph data. | Exact encoder/normalization/dimensions, row IDs, corpus scope and hashes recorded; no invented vectors or silently mixed spaces. | Geometry / manifest, row alignment and 41 shard hashes verified |
| R16 | Specify the combined graph/vector object. | Typed relationships, source evidence, retrieval affinities, vector alignment and navigation state have shared schemas. | Geometry + protocol / shared schemas and typed evidence implemented |
| R17 | Execute slice construction deterministically. | Identical frozen data and state reproduce candidate IDs, weights, coordinates and basis diagnostics within declared tolerance. | Geometry / exact same-runtime replay and input pins tested |
| R18 | Define and validate the 2D construction mathematically. | Document center, metric, basis, conditioning, transformations, residual/thickness meaning and degeneracy behavior. | Geometry / affine mean-chart, source diagnostics and alternatives documented/tested |
| R19 | Let intent change both candidate selection and the chart. | Counterfactual tests distinguish genuine recomputation from camera zoom, recoloring or a cached fixed hierarchy. | Geometry + protocol / counterfactual ranks and planes checked |
| R20 | Check that the resulting slice makes scientific and geometric sense. | Source-grounded relevance checks, neighborhood/distortion diagnostics, confidence/coverage limits and failure behavior. | All / geometric diagnostics, source reading and independent drift/recovery evidence recorded |
| R21 | Explore alternative constructions and grouping methods. | At least two plausible methods compared on the same journeys; record failures, measured results and choice rationale. | Geometry / plane, grouping and centroid comparisons recorded |
| R22 | Improve graph construction where experiments justify it. | Assess graph bottlenecks, hubs, duplicate-paper bias and cross-field discovery; implement bounded improvements or document evidence for retaining a part. | Geometry / bounded graph changes and ablations recorded |
| R23 | Expose an agent-native navigation interface, preferably MCP or an equivalent demonstrated protocol. | An agent can inspect state, retrieve evidence, choose/refine intent, compute a view, backtrack and export without clicking UI. | Protocol / six MCP tools and transport tests pass |
| R24 | Provide portable agent instructions. | Installable/documented skill teaches the rules, useful clarifications, actions, math invocation, evidence limits and troubleshooting. | Protocol / skill validated and independently used; application-preservation guidance added |
| R25 | Ground connections in sources and separate similarity from physics claims. | View objects preserve provenance; the agent cannot promote geometric proximity to implication/equivalence without evidence. | All / provenance and evidence limitations implemented |
| R26 | Run navigation code locally and generate portable view artifacts. | CLI/agent operations produce valid JSON and an inspectable local HTML view or shared static renderer input. | Protocol + UI / local CLI artifacts, portable sessions and same static renderer verified |
| R27 | Update the browser from agent operations. | A real agent-interface operation updates the displayed state through a tested local bridge or equivalent, with no hidden manual JSON editing. | Protocol + UI / actual MCP-to-browser and render acknowledgement pass |
| R28 | Keep the public site static. | Browser renders the graph/view object; no public model secret, chat backend or database is necessary for navigation. | UI / actual public static deployment and independent browser computation pass |
| R29 | Replace the old eigenquestions.com application. | Domain serves the new v1; voting, quiz, taste and old API routes no longer deliver old functionality. Preserve rollback in Git; do not destroy the old database. | UI + coordinator / deployed; 9 exact asset hashes and 32 retired-route checks pass; Git rollback preserved |
| R30 | Explain and test local/public-site interaction constraints. | HTTPS/loopback/origin/session behavior tested; permission and reconnection behavior explicit; usable same-origin local fallback. | Protocol + UI / Chromium loopback permission denial diagnosed; fresh-launch recovery and same-origin live updates verified |
| R31 | Preserve reproducibility and sensible failure handling. | Invalid state, stale data, empty/ambiguous query, missing vectors, disconnected graph and low-rank geometry have tested outcomes. | Geometry + protocol / failure and identity tests pass |
| R32 | Make the object reusable across subfields. | Corpus-specific adapters/configuration separated from engine and skill; another small fixture exercises the same contract. | All / second small corpus fixture passes |
| R33 | Validate the broader product, not only isolated components. | Full owner journey plus an independently chosen held-out journey and converse/backtrack tests run through engine → agent interface → browser. | Coordinator / 19 final browser checks, held-out route and independent eight-step agent trial recorded |
| R34 | Monitor and steer the team. | Regular artifact/progress inspection, explicit resolution of contract mismatches and no unbounded agent loops. | Coordinator / observed context, geometry and visual failures steered and recorded |
| R35 | Commit meaningful checkpoints with notebook updates and agent credit. | Intended changes only; commit body includes Request and Agent, observed checks and contributors. | Coordinator / meaningful checkpoints saved with notebook, request ID and contributor credit |
| R36 | Push configured GitHub checkpoints and verify them remotely. | Working branch `agent/question-conditioned-navigation` pushed and its SHA verified; validated release merged/pushed to `main`. | Coordinator / completion checkpoint ed6381d verified on both remote branches; deployment 42163657269 and final public comparison pass |
| R37 | Save before pauses, handoffs and completion; recover from the notebook. | Now names unfinished work and jobs; useful failures retained; stale assumptions checked before reuse. | Coordinator / one current Now section, saved versions/jobs/failures and recovery instructions |
| R38 | Keep logging small and researcher-readable. | One notebook, ordinary Git history and linked evidence; no separate tracing/memory service. | All / one notebook with linked evidence; ordinary Git history |
| R39 | Distinguish existing evidence, interpretations and new discoveries. | Recent means recent within dated inputs unless refreshed; generated suggestions are not established physics results. | All / dated corpus, inferred roles, geometry and source-claim limits explicit |
| R40 | Explain how the final geometry satisfies the broad intended picture. | Completion audit explicitly traces conversation → focus/intent → graph/vector operation → contextual directions → updated browser, including where v1 is limited. | Coordinator + protocol / full conversation-to-chart-to-browser trace and bounded v1 limits audited |

## Shared architecture gate

Initial independent audit clarifications (Astra protocol owner): “about five”
constrains next directions, not the total evidence displayed. “On” versus “using”
a concept must change evidence/ranking when source evidence supports the distinction.
Dark Dimension work should become contextually salient after the dark-matter pivot;
do not hardcode its absence in earlier searches. A 2D plane in a high-dimensional
point cloud requires explicit projection or finite-thickness selection semantics.
The numerical 3–6 target, MCP choice and database preservation are implementation
choices, not quotations from the owner.

Before independent implementations diverge, the three Astra owners agree one
versioned navigation-state and view-result contract. A view is a computed chart
over source-linked objects, not a claim that physics has a unique 2D embedding.
Coordinate choice, neighborhood selection, direction proposals, evidence and
state transitions must stay inspectable. The agent interprets the conversation;
the common numerical engine performs the deterministic work.

The six-thousand-paper Swampland corpus is the v1 dataset, not a claim to cover all
physics. Other corpora use the same interface. Prefer the existing domain and
static assets deployment. A local bridge is a user-side optional companion, not a
new public backend; test cross-origin limitations rather than claiming they vanish.

## Checkpoints

1. Save and independently audit intent; agree the contract and experiment criteria.
2. Establish real-data navigation and compare slice/grouping constructions.
3. Connect agent operations to the same state and static browser renderer.
4. Run the owner journey and held-out journeys; revise from observed failures.
5. Replace the public site, verify deployed content and old-route retirement, then
   close the coverage audit. Each checkpoint includes a notebook update and Git push.

Implementation files are owned by the assigned Astra agents. The coordinator owns
the notebook, this plan, saved user request, Git integration and release decisions.
Agents report evidence and blockers promptly; they do not independently commit,
push, change credentials, publish, or modify another agent’s owned files.

## V1 completion evidence

The final [19-check browser run](evidence/public-v3/browser-acceptance.json),
[exact public asset/route check](evidence/Q-001-publication-v2.json),
[independent agent trial](evidence/fresh-agent-trial.md), and
[clause/R40 audit](requirements-audit.md) cover the connected product. The browser
run uses runtime source `90fcdd239adb5c0b32eb083d6f60fffcfdb2ace6` with the
separately pinned fresh-tab test repair. The same numerical engine/corpus identity
underlies the independent exported session.

This is a scoped, source-grounded navigation v1. It does not establish a unique
geometry of physics or certify every proposed connection. The permission-blocked
public-to-loopback path is explicitly distinguished from the verified local
companion and independent static public browser. First-time setup on every agent
platform and cross-browser numerical equivalence are not claimed.
