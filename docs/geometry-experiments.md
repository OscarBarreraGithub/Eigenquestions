# Q-001 — Geometry experiments and decisions

The machine-readable evidence is
[`tests/geometry/results.json`](../tests/geometry/results.json),
[`direction-chart-results.json`](../tests/geometry/direction-chart-results.json),
and [`failures.json`](../tests/geometry/failures.json). The first file pins engine
and manifest SHA-256. These experiments use the real source-linked MiniLM corpus;
the separate low-rank test fixture is explicitly synthetic. Source relevance
checks inspect frozen descriptions and source IDs. They do not independently
reproduce the papers' calculations.

## Contextual retrieval: a real failed prototype and its repair

The first prototype blended a weak (0.24 mass) focus-vector centroid into an
otherwise new question. On KK towers → “what if they are dark matter?”, it put
1511.06768 (*Nonthermal production of dark radiation and dark matter*) first and
1207.5582 (*Observational constraints on variable equation of state parameters…*)
second. 2209.09249 (*Dark dimension gravitons as dark matter*) appeared third, but
the follow-up “how do they decay?” drifted to generic axion/modulus decay papers.
This failed the requested conversational behavior. The saved failure contains the
actual IDs, descriptions and scores, rather than an invented failure example.

The repair combines focus-source consensus terms and the focus-vector centroid
with **both** source-anchor selection and global candidate scoring. It also
refreshes focus from the latest view rather than retaining KK anchors forever.
No concept-specific dark-matter/decay rule was added. The coordinator separately
caught domain-loaded intent cues in the early prototype; these were replaced by
generic calculation/observation cues before acceptance testing.

The repaired pronoun sequence yields:

| Step | Leading source examples and relevant evidence |
|---|---|
| KK towers | 2312.03184: flux/uplift, KK masses and bubble transitions; 2609.00119: KK-species backreaction; 2003.06274: KK/AdS scale separation |
| What if they are dark matter? | 2607.27314: axion KK towers, dark-dimension production/fragmentation; 2311.05318: repeated decays of a DM KK-graviton tower and CMB/BAO/lensing; 2212.08527: dark-dimension cosmology; 2411.07029: neutrino KK weak decays and photon bounds |
| How do they decay? (derive) | 2209.09249: daughter-channel gravitational intra-tower decay estimate; 2610.01825: cascade overlap/completeness and near-threshold suppression; 2307.01100: KK Fourier modes and summed radion/graviton decay channels |

Dark Dimension mentions in the top ten rise from **0 to 5** in this exact sequence;
the global corpus is never filtered to forbid that concept earlier. Generic “dark
matter” and the KK-conditioned follow-up have **zero top-ten source-ID overlap**.
Fresh versus stale KK focus at the decay step has only **40% overlap**, supporting
the need to update active context. Results remain suggestions, not a claim that
all KK dark matter realizes the Dark Dimension.

Changing KK intent produces source-grounded derivations (e.g. Fourier
diagonalization in hep-ph/0205237, KK sums in 1303.2661) and distinct observational
questions. Recent ON versus USING changes the selected layer and evidence:
2512.09052 explicitly integrates the sterile-neutrino KK tower in its method
facet, while recent ON examples ask about KK tower thresholds/backreaction.
Ambiguous semantic neighbors are not certified as method use. Recency is confined
to the dated frozen catalog.

A held-out geometry-owner sequence, black-hole entropy → higher-derivative
corrections, retains black-hole/Wald/attractor content rather than drifting to
unrelated correction calculations. A separate inflation/tensor intent comparison
checks that generic `derive`/`phenomenology` cues do not inject KK or dark matter.
The protocol owner independently tests another route without providing its
expected IDs for engine tuning.

Vector and graph ablations matter: removing the vector score changes 3/10 top
source IDs for KK; removing graph weight changes 1/10, as well as rank/weights.
This is not a lexical list whose vectors only decorate the screen. The graph has a
bounded contribution, so it cannot drown out explicit question evidence.

## Chart constructions on identical source neighborhoods

We compared a query-anchor constrained first axis plus orthogonal PCA against
unconstrained weighted PCA for nine contexts. Candidate IDs and weights were held
fixed within each comparison.

| Source-level chart | Captured variance | Distance stress | 5-neighbor retention |
|---|---:|---:|---:|
| Anchor-constrained plane | 8.0–11.3% | 0.734–0.773 | 16.3–25.0% |
| Weighted PCA | 12.5–16.1% | 0.664–0.701 | 20.9–31.6% |

Weighted PCA consistently uses its two dimensions better. The explicit radial
query axis consumed variance with little useful source-neighborhood preservation.
Even the better method is a **poor source-level metric map**: most variation is
omitted. That finding caused a further change, rather than being hidden behind a
visually plausible scatterplot.

The default now fits weighted PCA to the five dynamically computed direction-group
means in the same 384-dimensional space, without renormalizing the means. Across
seven owner/held-out contexts:

| Question | Group variance captured | Group distance stress | Group 1-neighbor retention |
|---|---:|---:|---:|
| KK towers | 64.1% | 0.393 | 40% |
| KK derivation | 66.9% | 0.297 | 80% |
| KK phenomenology | 64.8% | 0.259 | 100% |
| KK → dark matter | 62.3% | 0.333 | 80% |
| Dark matter → decay | 70.2% | 0.266 | **20%** |
| Black-hole entropy | 69.2% | 0.341 | 80% |
| Inflation/tensor phenomenology | 58.9% | 0.331 | 40% |

This is substantially better for a five-direction overview, but it **does not**
make those percentages source-level fidelity. The optional source overlay has its
own lower variance/neighbor retention in that exact group-fitted plane. Within-
group RMS spread is retained and often large: the groups are retrieval directions,
not cleanly separated ontological kinds. The poor 20% decay nearest-neighbor result
is a specific warning against reading the closest direction as a scientific
relationship, even when aggregate variance looks good.

Fixed-state replay is exact in the tested Node runtime. Varying power-iteration
seed 17→53 in the source anchor-plane comparison leaves candidates unchanged;
most plane projector differences are below 2×10⁻⁵, with a 0.043 Frobenius difference
for inflation/tensors. Production fixes the seed, sign rules, iteration count and
all parameters. Cutoff-gap diagnostics flag a potentially unstable variance
boundary; deterministic output is not a claim of statistical stability.

## Grouping and graph choices

Greedy MMR representatives were compared with three deterministic weighted-medoid
updates on the same neighborhoods. MMR had lower representative cosine redundancy
in seven contexts and tied in two; medoids tended to return more central, similar
representatives. For KK USING, mean pairwise representative cosine was **0.354
(MMR) versus 0.460 (medoids)**. The v1 keeps MMR to expose different next questions;
its groups are recomputed after every query. It does not claim an optimal
clustering or a globally valid hierarchy.

The upstream graph already balances paper mass. We retained those weights and
added only bounded directed neighbor truncation, row-normalized restarted
traversal, same-paper cross-layer incidence, and per-paper retrieval/display caps.
We did not double-apply paper masses or promote text affinities into physics
relations. A richer scientific-relation graph, a stronger query encoder, judged
retrieval benchmarks and uncertainty-aware labeling remain future work; the
current source-vector and retrieval failures do not justify claiming those are
already solved.

## Verification and practical bounds

Run `node --test tests/geometry/*.test.mjs` for the committed invariants, including
real-data contextual retrieval, source roles, mathematical diagnostics, corrupted
JSON rejection and engine/data identity. Source-chart and five-centroid comparison
scripts regenerate the linked evidence. Local full-load/index time was about
0.3 seconds from disk; individual source retrieval/chart operations were roughly
0.06–0.15 seconds in this environment. The distribution is approximately **85 MB
raw** after lossless reading-scope deduplication, down from 111 MB. These are local
measurements; the site owner separately verifies browser transfer, rendering and
live-agent updates. Public-browser compatibility and scientific reading quality
are integrated acceptance gates, not inferred from these numerical tests.
