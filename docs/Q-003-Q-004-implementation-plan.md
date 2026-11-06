# Stored scientific views and a quieter explorer

Requests: Q-003 (authorized implementation), Q-004 (startup and visual refinement).
Coordinator: `/root`. Implementers: Astra protocol/backend; Sol interface and independent review.

## The complete journey

A researcher asks their agent a physics question. The agent consults this graph
for orientation **in addition to** its ordinary independent research. It constructs
a contextual view using deterministic code on the graph/embeddings and records
its scientific decisions. A complete file preserves labels, sources, groups,
relations, evidence and continuation context; geometry is only one part of it.
The agent uploads this file, receives a small shareable URL, and navigates the
browser to it. The browser displays those accepted decisions without rerunning
a model. The same file can be opened manually. Neither a URL nor a matrix alone
is assumed to encode arbitrary scientific organization.

This remains question-dependent navigation, not a fixed hierarchy. A new question
can introduce a previously absent concept, change grouping or change the depth
of an idea. About five meaningful directions is a presentation target, not a
claim that physics is a five-way tree. Embedding proximity is not physical proof.

## Atomic requirements and checks

| ID | Requirement | Evidence required |
|---|---|---|
| S01 | Versioned, bounded complete contextual-view contract | Schema/validator and roundtrip tests |
| S02 | Preserve authored labels, overlapping groups, members, relations and evidence | Authored fixture survives file and HTTP roundtrip exactly |
| S03 | Separate display, recomputation and continuation | Unknown builder readable; unsupported continuation explicit |
| S04 | Optional typed geometry, no executable uploaded code | Safe text rendering and malformed-input tests |
| S05 | Manual import/export and drop use the same file | Browser roundtrip, error recovery, unchanged accepted view on failure |
| S06 | POST commits immutable storage before returning link | Worker tests for durable success, failure, retry and conflict |
| S07 | Share URL loads the exact stored object | Fresh-tab and same-document route tests |
| S08 | Browser stays usable during fetch/upload/compute | Latest-action/draft/back/transport regression tests |
| S09 | No hardcoded topic flash | Delayed cold start, saved state and route-precedence tests |
| S10 | Neutral first use; explicit route outranks saved state | Empty first path and valid/invalid route checks |
| S11 | Agent discovery and browser API agree with runtime | Instructions and supported command examples checked |
| S12 | Graph orientation supplements independent research | Instruction review; no claims that crawling executes compute |
| S13 | Bounded free-tier deployment; no hidden expiry | Size/admission enforcement, limits and activation notes |
| S14 | Existing public assets/retired routes preserved | Build/site checks and public asset/route verification |
| U01 | Familiar, text-first visual hierarchy | Actual desktop and phone screenshots reviewed by Sol |
| U02 | Fewer simultaneous headings/controls | Compare first scientific choice position and screenshot hierarchy |
| U03 | Sharp type, wrapping scientific labels, restrained rules/links | Narrow and wide layout inspection |
| U04 | Readable large controls, easy New path and clear current path | Mobile target/layout and keyboard checks |
| U05 | Dynamic labels and contextual paths remain functional | Retained scientific navigation and history tests |
| D01 | Record vision and concise mechanism showcase | This plan plus showcase note, clearly distinguishing shipped/pending |
| D02 | Preserve useful failures and reproducible evidence | One notebook, checked source/job receipts, ordinary Git checkpoints |

## Integration boundaries

`navigator_protocol` owns the capsule, browser controller and agent instructions;
`stored_view_backend` owns upload/read, binding/build configuration and Worker
tests; `quiet_ui_sol` owns HTML/CSS; `quiet_ui_review_sol` provides independent
visual critique. Root audits the whole journey, maintains the notebook, runs
verification and manages release. Owners agree on one capsule before integration.
No implementation owner separately deploys or commits.

## Release sequence and current constraint

1. Agree contract and implement a faithful local file journey, neutral startup,
   quieter interface and bounded storage service.
2. Run Node/Worker checks; freeze and push a reproducible checkpoint.
3. Run real browser tests in the existing authorized Slurm setup; review actual
   screenshots and repair observed failures without weakening checks.
4. Publish via the existing GitHub workflow and verify the public version.
5. Activate R2 only through authorized access; verify real save/open durability
   before describing hosted sharing as live.

On 2026-11-06 the Cloudflare connector rejected account discovery with
“MCP tool call requires approval, but approval policy is never.” No alternate
credential path will be used. Implementation/testing and the existing authorized
site deployment can proceed. Hosted upload activation remains a separate final
step until the restriction is resolved; no subscription has been changed.
