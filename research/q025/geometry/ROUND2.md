# Targeted local refinement and paired relation audit

Job61411183 finished all numerical candidates and comparisons, then failed in
the final progress-marker serialization (duplicate `elapsed` keyword). Its Slurm
state remains **FAILED**, 6m52s, exit1, peak RSS616,768KiB. The original runner and
traceback are retained under `failures/round2-v1/`. All resulting source alignment,
membership conservation, source coverage and containment checks pass. No numerical
rerun was needed. The corrected completion path has an executed regression check.

This round refines the inherited 3,127- and 936-unit stopped regions. It is a
targeted experiment, not a requirement that the final atlas inherit those parents.
Local normalized-adjacency eigenvalues choose between 2–12 groups by the largest
eigengap; clustering uses the corresponding full spectral subspace. Small proposed
groups remain explicit candidates with source access. They do not cause every
sibling to disappear. Boundary-neighbor suggestions are stored separately from
containment, without promoting them to scientific relations or memberships.

| Construction | Direct regions | Units min / median / max | Leaf depth min / median / max | Giant dropout ARI at level2 / leaves |
|---|---:|---|---|---|
| Local MiniLM spectral | 88 | 11 / 46 / 731 | 2 / 5 / 7 | .936 / .790 |
| Local MiniLM/Qwen mutual-boosted spectral | 106 | 7 / 45 / 731 | 3 / 5 / 8 | .951 / .671 |
| Qwen within inherited MiniLM parents | 16 unchanged | 44 / 350.5 / 3,127 | 1 / 6 / 7 | No successful refinement |

The Qwen failure is informative: a few units have all their Qwen neighbors outside
the inherited MiniLM parent. The conservative isolation gate stopped the whole
parent. Its ARI1 is trivial, not a success. The next round exports the existing
global Qwen hierarchy and the isolated sources' strongest external neighbors to
test whether the ancestry itself needs revision or overlap.

The successful local constructions retain broad distinctions under edge dropout,
but disagree about fine organization. Inside the giant, MiniLM versus consensus
leaf ARI is .167, whereas whole-corpus ARI is .888 because much of the atlas was
not changed. Whole-corpus scores would conceal this disagreement. For dropout,
unit-weighted best-cluster Jaccard is .605 for MiniLM and .640 for consensus.
The archived `bestMatchCoreCoverage` is a **directional** maximum-overlap statistic;
it can be trivially1 when many fine groups map to one coarse group, and must not be
read as a certified stable-core fraction or semantic accuracy.

| Witness | Inherited home size | Local MiniLM | Local consensus |
|---|---:|---|---|
| KK dark-matter production / phenomenology / linear signatures | 936 each | 46 / 46 / 47 | 18 each |
| Three tilted-torus questions | 3,127 each | 159 / 147 / 159 | 42 / 71 / 42 |
| Physical-charge projection | 3,127 | 32 | 113 |
| Finite moduli-space volume | 442 | 442 | 442 |
| Holographic superconductor | 721 | 721 | 721 |

These source-visible gains warrant review; small homes alone do not prove a good
scientific distinction. The last two witnesses lie outside the targeted parents.
Cross-field routes must retain all explicit links and the full affinity graph,
including connections not foregrounded in a short menu. Candidate excerpts and
counterexamples are being independently examined by the scientific evaluator.

## What the paired relation experiment establishes

Two seeds were each run with no added relation attraction, all97 admitted records,
and only the six same-result-under-dictionary/specialization records. All runs
retain the original scoped typed edges separately. The attraction test is a
paper-projected numerical ablation; it does not assert a relation between every
question in those papers.

| Comparison | Level1 ARI | Leaf ARI |
|---|---|---|
| Base seed variation | .911 | .435 |
| All-type attraction, paired seed1 / seed2 | .952 / .977 | .586 / .554 |
| All-type attraction seed variation | .920 | .434 |
| Result/specialization attraction, paired seed1 / seed2 | .971 / .987 | .376 / .468 |
| Result/specialization attraction seed variation | .929 | .423 |

Broad structure persists more strongly than fine boundaries. These two paired
seeds do not support a claim that all-type injection is exceptionally destabilizing
relative to baseline variation. The semantic reason to avoid indiscriminate
attraction is separate: analogy, method transfer, tension, specialization and
conditional support are different relationships.

`typed-relation-review-constraints.json` provides the alternative: preserve each
category/direction and the receipt, require the actual dictionary or premises,
and explicitly abstain when the reviewed claim endpoint has not been mapped to
a question node. No relation category automatically canonicalizes question identity.

Machine measurements: `round2/comparison.json`,
`round2/spectral-cross-encoder-comparison.json`, `round2/paired-relation-audit.json`,
`round2/artifact-audit.json`. Complete candidate files remain local and on Slurm;
compact evidence and hashes are eligible for the coordinator's checkpoint.
