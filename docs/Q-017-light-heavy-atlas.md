# Q-017 — A detailed scientific atlas with light and heavy compute modes

2026-11-17. Recommendation by `/root`. This is a design and implementation sequence,
not a deployed backend, new embedding run or measured performance result.

## The decision

Build the best validated source-backed representation once, and expose it through
one viewer with two execution modes. A light user must still be able to inspect a
heavy-computed view in full detail. Additional compute buys new retrieval, checking
and organization, rather than permission to read already computed scientific detail.

Use a local GPU, FASRC allocation or optional hosted backend through the same tool
contract. Cluster access is useful for building the corpus and doing substantial
new analysis; it is not inherently necessary for browsing or even every difficult
query. The website can remain static. The owner's existing external agent can
interpret questions and inspect sources independently of the numerical worker.

## What scientific resolution means

Measure whether the system distinguishes different statements, hypotheses, methods,
regimes and conventions and can retrieve their supporting passages. Dense vectors,
token-level representations and graph links are complementary access structures.
Neither more dimensions nor more clusters establishes greater scientific resolution.

Keep source-linked objects for questions, claims/results, methods, assumptions,
regimes, conventions and derivation steps, with links back to contextual source
passages/equations. The richer upstream atlas already contains many of these objects;
inventory and sample their evidence before exposing them. The browser currently
exports only question and method facets. Partial extraction and uncertain scientific
relations remain marked. Original source context is necessary when an extraction
omits a qualification; no embedding can recover information absent from its input.

Preserve mathematical notation alongside descriptions; retrieve equations with
their variable definitions and conventions. Use exact/lexical matching as well as
learned similarity. A symbolic equivalence or a valid derivation requires separate
checking and cannot be inferred from nearby equation embeddings. Conditional
relations need their premises, as Q-015 illustrates.

## Recommended retrieval structure

Precompute broad summaries/landmarks, facet embeddings, and source-passage indexes
on the same stable source IDs. Keep full-resolution data; derive smaller retrieval
packages only after measuring what compression loses.

For a new contextual question:

1. Preserve the complete question and resolve its referents/constraints. Encode it
   and a few aspects using the query conventions paired with each document index.
2. Combine lexical, dense and graph-seeded retrieval to collect a diverse candidate
   set. Search the broad corpus as well as the local region so early routing does
   not permanently exclude a cross-field answer.
3. Compare finer matching: a token-level late-interaction model and a cross-encoder
   reranker are candidates for different stages. Late interaction keeps multiple
   vectors within a passage and scores detailed matches; it does not by itself
   enforce negation or logical entailment. This differs from our existing multiple
   scientific-facet vectors per paper. [ColBERTv2](https://arxiv.org/abs/2112.01488).
4. Let the agent inspect a bounded set of source passages for the actual assumptions,
   evidence roles and disagreements. Missing metadata remains unknown. Expand the
   search if these checks show missing evidence; do not ask the reranker to rescue
   material the first stage never retrieved.
5. Construct the Q-014 region, its complete recorded membership and roughly five
   executable next directions. Apply Q-013 delivery to the resulting accepted view.

Qwen 4B and 8B are available starting candidates for dense retrieval, not a declaration
of the best physics encoder. Their previous comparison tested selected passage and
relation tasks and did not establish a universal winner. Add a compatible reranker
and a late-interaction comparison on a bounded pilot before broad production runs.
Keep ablations so increased model size, representation detail and additional checking
are not credited interchangeably. A compact model can be preferable if measured
scientific performance is equal.

## Light and heavy behavior

| Capability | Light mode | Heavy mode |
| --- | --- | --- |
| Browse atlas, papers, saved views | Same scientific IDs and accepted evidence | Same |
| Query encoding | Compact local/browser encoder with its own compatible index, or agent-provided encoding | Validated larger encoder(s), potentially several aspects |
| Retrieval | Compressed/sharded index and bounded graph work | Wider candidate search, full vectors and optional token-level matching |
| Checking | Stored qualifications and available agent checks | More candidate/source checks and reranking; targeted derivation checks when requested |
| Next directions | Cached regions plus inexpensive recomputation | New context-dependent regions and source-supported questions |
| Output | Shared versioned region/view format | Same format, with computation and evidence provenance |

These are execution budgets, not two competing taxonomies. Different retrievers may
nominate different evidence; preserve the change and allow an explicit comparison.
Heavy results must not silently erase the current path or user markings. A pending
job leaves the accepted view usable. New results can be applied against their original
state revision or opened as a branch if that state has changed.

Matryoshka-trained encoders allow testing shorter output vectors for early retrieval
and fuller vectors later. This reduces vector/index storage and search cost; it does
not make the underlying encoder smaller or guarantee hierarchical scientific meaning.
A small independent encoder requires its own document index unless explicitly trained
and validated to share a space. [Matryoshka Representation Learning](https://arxiv.org/abs/2205.13147),
[Qwen model dimensions and query conventions](https://huggingface.co/Qwen/Qwen3-Embedding-8B).

## FASRC execution profile

Use the existing cluster connection and account configuration. A bounded native SSH
check succeeded during this review; the cached SWA report was read separately. No
new job, allocation, model download, storage change or service was started.

There are two useful workloads:

- **Batch construction:** encode and index the corpus, compute candidate regions,
  cache source-backed descriptions and publish immutable verified data bundles.
  Several independent shards can use job arrays; each writes isolated outputs and
  a coordinator verifies IDs/hashes before assembling a release.
- **Active research session:** one time-bounded GPU allocation loads the chosen
  model/index once and handles a short series of requests. Use an existing allocated
  worker when available; avoid a new Slurm submission and model reload for each click.
  Queue wait remains visible and separate from inference latency. Use batch requests
  when no active session is justified and release idle resources.

Inference and numerical indexing run on compute nodes. Agent-side SSH/CLI submission
and result-file transfer are sufficient for a first adapter; no public cluster web
server is required. The browser does not need FASRC credentials. Authentication must
use the owner's existing sign-in; shared read access to datasets does not grant access
to another person's compute account. [FASRC job guidance](https://docs.rc.fas.harvard.edu/kb/running-jobs/),
[login-node responsibilities](https://docs.rc.fas.harvard.edu/kb/responsibilities/).

A sensible **benchmark allocation**, not a measured requirement, is one GPU with
40–80 GB of memory for an 8B encoder plus 8B reranker and modest batches. Their nominal
16-bit weights alone sum to about 32 GB. Sequential loading or quantization can make
smaller GPUs viable; actual peak memory depends on input length, batch size, runtime
and index placement. CPU/RAM can handle much of index search and sparse graph work;
do not request GPU time solely for unrelated CPU construction. A frontier external
agent's reasoning compute is separate from these embedding/reranker weights.

The portable agent instructions should specify how to: detect capabilities and
current allocations; verify corpus/model versions; choose a backend; submit a bounded
request with unique output paths; monitor progress/failure without duplicate work;
resume from checkpoints; verify returned evidence and source IDs; and deliver the
view through the existing controller. Site-specific account, paths and partitions
belong in a local execution profile, not in a universal published skill. Preserve
independent literature search as an additional research channel.

## Implementation order and acceptance

1. **Define the resolution test.** Reuse Q-014's twelve regressions/holdouts and add
   independently constructed questions about assumptions, convention changes,
   overlapping topics, equations and out-of-corpus requests. Avoid choosing all
   witnesses from the prior MiniLM pool. Freeze splits before tuning. Small pilot
   results are falsification evidence, not certification of all physics.
2. **Build the heavy reference path on one region.** Include actual paragraph
   encoding, rich source retrieval, controlled model/reranker comparisons, checking,
   and one accepted region with clickable continuation. This establishes a measurable
   quality target before optimizing delivery. It needs one worker, not a new swarm
   reprocessing every paper.
3. **Produce and measure the light path.** Compare a compact encoder and/or index
   compression to that reference. Measure witness recall, constraint violations,
   unsupported claims, useful next directions, text/click agreement, missing coverage,
   memory, download size and cold/warm latency. Report heavy quality independently;
   agreement with heavy is not truth. Keep exact source checks on sampled searches.
4. **Package the agent/backend adapter and scale.** Verify local and FASRC execution,
   interrupted jobs, stale results, replay and browser application. Then batch-encode
   missing rich facets, shard larger corpora and distribute accepted artifacts for
   ordinary browsing. Expand to all physics only with explicit coverage depth and
   global re-entry, preserving autonomous organization and optional expert overlays.

This setup keeps Q-010's shared research atlas, Q-014's region mathematics, Q-015's
optional scientific overview and Q-013's delivery in one system. It proposes no new
mandatory hosting subscription or default model winner. Next implementation is the
bounded heavy reference journey and evaluation, followed by a measured light version.

## Priority amendment after Q-018, 2026-11-17

The owner proposed a simpler primary interaction: an agent routes a long question
through a deeply prepared atlas and returns a compact state URL. Adopt the
[Q-018 neighborhood/routing pilot](Q-018-precomputed-navigation.md) ahead of the
heavy-query reference pilot above. This path can use the agent's understanding of
region descriptions without a separate query encoder. Heavy computation still
builds the atlas; on-demand retrieval/reorganization remains an optional escalation
when existing regions cannot express the request. The earlier recommendation is
retained as history and a possible advanced path, not the current first task.
