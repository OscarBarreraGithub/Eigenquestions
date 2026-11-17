# Q-025 geometry experiments

This directory owns bounded numerical experiments, not accepted scientific labels or
canonical question merges. The source rows are paper-scoped descriptions with their
original unit IDs, text hashes, source-record IDs and embedding-row provenance.
No encoder is rerun. The historical upstream snapshots are read only.

Round 1 compares three materially different organizations of all 8,473 question
units. Each consumes the existing embedding-affinity graph; the multiview family also
uses the independent Qwen question graph and the 17,937-unit method graph.

1. **Inherited normalized cuts.** Preserve the existing nested partition, its
   recorded stops and parameters. This supplies the comparison, not an assumed truth.
2. **Restart diffusion overlap.** With inherited leaf indicator matrix H and the
   row-stochastic question graph P, solve X=(1-a)H+aPX for a in {0.35,0.65,0.85}.
   Retain memberships at least 20% of the largest row entry, then normalize each row.
   Thus each source has mass one across its direct homes. Ancestors aggregate those
   homes; overlapping siblings can expand the original scopes and require new review.
   This represents ambiguous boundaries without equating the connected questions.
3. **Encoder/method multiview hierarchy.** Form S(W)=D^-1/2 W D^-1/2. Let B connect
   each question to methods in its own paper, with method mass normalized within the
   paper. The proposal graph is 0.5 S(W_MiniLM)+0.3 S(W_Qwen)+0.2 S(B S(W_method) B^T).
   The method layer is co-paper context, not a verified logical relation. Recursive
   Leiden partitions induced subgraphs, using resolution 0.65 at root and 0.8 below,
   maximum depth six, parent mass at least 80, child mass at least 12, at least 12
   units per child, and 2–15 children. Rejected splits are archived with child sizes.
   Branching limits are provisional experimental gates, not the interface objective.
   Seed repeatability is measured rather than treated as scientific certification.

The weights above are declared experimental choices. Degree normalization changes
the relative influence of the inherited paper-balanced affinities; paper mass remains
explicit in diagnostics and memberships. This is not a universal metric of physics.

Scientific links come only from the independently audited current receipt ledger:
accepted_relation and not promotionWithheld, with original category, direction,
assertion, assumptions, dictionary and reader note. They are preserved separately
from the geometric graph. The relation-injection ablation deliberately adds 0.03 S(R),
where R symmetrizes paper-level endpoints. That is an artificial attraction used to
measure sensitivity, and is not a proposed interpretation of analogy, tension,
specialization or logical direction. All typed connections remain accessible even
when an affinity display retains only its strongest six edges per region.

Diagnostics include source/paper coverage, row-weight conservation, primary-home
conductance, fractional overlap, leaf sizes/depth, retained coarse flow, seed and
10% edge-dropout stability, scientific-edge preservation, and lexical KK/dark-matter/
cosmology probes. Lexical probes identify potential review cases; they do not validate
physics or guarantee a readable route. The full coarse adjacency is archived.

## Artifact interface

- `input-manifest.json`: input bytes, SHA-256 hashes, row hashes, software and code hash.
- `source-rows.jsonl`: complete aligned question units, with local and browser rows.
- `<candidate>/regions.json`: complete region membership, hierarchy, central source
  units and source-record evidence; titles/scopes remain explicitly unreviewed.
- `<candidate>/memberships.jsonl`: `unitId`, `sourceRow`, `browserVectorRow`, `regionId`,
  fractional `weight`, and `primary`. Weights are organizational mass, not relevance
  probabilities or truth confidence.
- `<candidate>/memberships.npz` and `column-ids.json`: the same sparse numerical data.
- `<candidate>/edges.jsonl`: typed geometric affinities and separately scoped scientific
  records. A paper endpoint does not become a claim about every question in that paper.
- `<candidate>/diagnostics.json`, `comparison.json`, `progress.json`: measurements and
  retained failures. Candidate region IDs do not establish canonical question identity.

Round 1 runs only in Slurm job 61409202, account randall_lab, partition test,
4 CPUs, 16 GiB and 30 minutes. No publication or deployment is part of this job.
