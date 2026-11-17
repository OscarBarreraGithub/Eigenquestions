# Executed comparison: first geometry round

Slurm job **61409202** completed in 4m22s, exit 0, peak RSS 552,940 KiB.
All 8,473 question rows align exactly with the browser's source IDs, paper IDs,
text SHA-256 hashes and vector rows. All 6,477 represented papers remain covered.
The job reused MiniLM and Qwen question graphs and the MiniLM method graph; no
extraction or encoding was rerun. See `round1-job.json`, `CONSTRUCTION.md` and
`round1/input-manifest.json` for code, input and environment provenance.

| Construction | Direct regions | Primary units min / median / max | Measured behavior |
|---|---:|---|---|
| Inherited normalized cuts | 16 | 44 / 350.5 / 3,127 | Deepest leaf depth7, but giant stops at depth1 on instability |
| Restart diffusion, walk probability .35 | 16 | 44 / 350.5 / 3,127 | 234 overlapping units; no depth repair |
| Restart diffusion, walk probability .65 | 16 | 44 / 350.5 / 3,127 | 3,185 overlapping units from 2,501 papers; mean1.47 homes; dropout primary ARI1 |
| Restart diffusion, walk probability .85 | 16 | 16 / 279 / 3,729 | Rare-region erosion and largest-basin absorption; dropout ARI.979 |
| Encoder/method multiview hierarchy | 148 | 13 / 42 / 729 | Depth2–4; seed leaf ARI.435, dropout leaf ARI.337 |
| Multiview plus indiscriminate relation attraction | 145 | 13 / 44 / 667 | Only220 units touched; same-seed leaf ARI against base .586 |

The diffusion parameter is **walk continuation**, with teleport probability 1-alpha.
The .65 result suggests a boundary halo useful for cross-region navigation, but is
not a hierarchy fix. At .85, finite-moduli-volume and holographic-superconductor
witnesses move into the giant primary basin. Its complete overlapping membership
grows to 7,532 units. Presence alone therefore badly overstates useful coverage.
Tilted-torus and physical-charge projection witnesses stay buried inside the giant
at all three diffusion settings. Exact per-witness placements are retained in
`round1/artifact-audit.json`; these are development/navigation challenges, not a
blind accuracy benchmark.

The multiview hierarchy gives substantially finer candidates with sensitive fine
boundaries. Fine-leaf ARI alone does not establish whether broad structure, matched
cluster cores or source-defined distinctions remain useful. One 729-unit terminal
rejected a proposed split solely because one
child had paper mass11.45 below the threshold12; the other children had masses
72–140. Blanket rejection can hide substantial structure. The next experiment
will preserve adequately supported candidates and expose small uncertain sets
with source access, while testing a different local spectral objective inside
the 3,127-unit historical terminal. Historical gates remain unchanged.

The scientific-layer ablation does **not** show that scientific relations are
irrelevant to organization or unusually destabilizing. Its same-seed paired ARI.586
is higher than the seed-background ARI.435 and dropout ARI.337, so that single pair
does not establish exceptional causal sensitivity. Multiple paired seeds and
broad-level/core agreement are required. Separately, the semantic objection to
indiscriminate attraction remains: it treats analogy, method transfer, tension and
specialization as the same numerical relation. All97 admitted records remain separate directed,
scoped navigation links. Five withheld records and all other nonpositive outcomes
were excluded. Typed relations should guide edge-specific review/constraints:
same-result-under-dictionary and specialization are distinct from analogy,
method, conditional support and apparent tension. None automatically proves
equivalence of the corresponding question descriptions.

All full memberships, region IDs, retained numerical failures and complete coarse
edges remain in local `round1/` and the isolated cluster run. The publication-sized
evidence is the code, this account, job receipt, input manifest, diagnostics and
artifact audit. Raw candidate files are proposals, not a selected release.
