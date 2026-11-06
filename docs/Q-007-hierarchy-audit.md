# Q-007 — Which smaller clusters actually exist?

Read-only audit by `/root/stored_view_backend`, 2026-11-06. No hierarchy, source,
membership, layout or runtime was changed. The immediate UI repair can expose
the six supplied children and make leaf-source access explicit. Providing new
children under every broad region would require a separate organizational-data
revision; those missing children are not merely hidden by the renderer.

## Exact current availability

The source remains `minilm-leiden:physical_question:reviewed` in
`/Users/emmy/Developer/physics-atlas-swampland/graph-design/20261105-v1/publication-v1/map-data.json`,
SHA-256 `a6cb5cdb6d955d3ca33b9297be0a301ea50c6c8c75ba2294999adac8163d765b`.
The deployed overview's compact projection retains this source hierarchy exactly.

| Current broad region | Facets | Actual smaller clusters | Why the source stops |
| --- | ---: | ---: | --- |
| String compactifications | 3,260 | 0 | Nine proposed children failed the predeclared seed-stability gate |
| Quantum gravity, horizons & consistency | 1,992 | 6 | Local refinement passed the numerical gate; these six children are available now |
| Inflation & scalar dark-sector cosmology | 3,081 | 0 | Ten proposed children failed the predeclared seed-stability gate |
| Neutrino mass: origins & tests | 132 | 0 | Original parent was below the refinement mass threshold; no local split was attempted |
| Awaiting a better home | 13 | 0 | Explicit unresolved placements after sampled organizational review; no finer organization supplied |

The six available children are EFT consistency; de Sitter quantum gravity;
black-hole and holographic entropy; holographic quantum gravity; Euclidean
wormholes; and black-hole extremality/entropy as tests of weak gravity. Their
full original labels are preserved in the data. They are leaves in this snapshot.

## Exact refinement gate and evidence

The frozen producer is `components/graph_design_geometry/run.py` in the external
source repository. Its `PROTOCOL` sets broad Leiden resolution 0.5, seed 20261105,
and one induced-subgraph refinement at resolution 1.0. It attempts refinement
only for parent mass at least 160. A candidate is retained only with:

- Two through sixteen children.
- At least twenty units and mass twenty in **every** child.
- Minimum pairwise adjusted Rand index at least **0.7** across seeds 20261105,
  20261106 and 20261107.
- Maximum recorded refinement depth two.

These are declared construction choices, not universal scientific thresholds.
Paper-balanced mass is the sum of unit masses, not the raw number of descriptions.

| Original parent | Proposed children | Pairwise seed ARIs | Size/mass gate | Result |
| --- | ---: | --- | --- | --- |
| Compactifications | 9 | 0.656026, 0.658331, **0.608125** | Passed | Rejected for instability |
| Black-hole/QG umbrella | 6 | 0.713910, 0.889792, **0.707532** | Passed | Retained |
| Inflation/dark-sector cosmology | 10 | 0.615236, **0.460307**, 0.594070 | Passed | Rejected for instability |
| Neutrino region | Not attempted | — | Original parent mass **123.883333 < 160** | Stopped before fitting |

The original neutrino parent had 133 facets; the reviewed view has 132. Similarly,
the original QG umbrella had 1,999 facets and the reviewed umbrella has 1,992.
Use the original trial quantities when explaining its gate, and current reviewed
counts when displaying the map.

The inspected archive is
`graph-design/20261105-v1/observed-results/geometry-v1/trials/minilm/physical_question/`.
`navigation-tree.json`, `SUMMARY.json`, `r1.0-s20261105.json` and
`r2.0-s20261105.json` all matched their byte counts and SHA-256 entries in the
geometry run's completion `MANIFEST.json`.

Crucially, the producer's `leiden_tree` computes local seed assignments in memory
and creates child nodes only when the gate passes. Rejected local assignments
are not in the saved navigation tree or trial directory. Their proposed count,
ARIs and rejection reason survive. The saved `r1.0-*` and `r2.0-*` files are
**global** partitions, not those rejected within-parent assignments.

## Other already-computed hierarchies

The same pinned publication retains numerical alternatives:

| View ID | Topics including root | Maximum depth | Reuse limit |
| --- | ---: | ---: | --- |
| `minilm-ncut:physical_question` | 31 | 7 | Its 3,127-facet compactification-like branch also stopped for instability; its deeper cosmology tree has different memberships |
| `qwen-4b-raw-ncut:physical_question` | 91 | 8 | Deeper structure in several regions, from a different encoder and partition; automatic labels, not the current reviewed child tree |
| `qwen-4b-raw-leiden:physical_question` | 26 | 2 | Nine compactification-like children and eleven black-hole-like children, but different parent memberships; cosmology and axion/dark-matter refinements were rejected |

Exact membership comparisons found no alternative topic that could be inserted
unchanged as a proper child of the current inflation or neutrino region. For
compactifications, only two small Qwen normalized-cut leaves fit wholly inside
the current region: 71 facets labeled “supergravity; dimensional supergravity;
dimensional” and 51 labeled “defects; invertible; non invertible.” They cover only
122 of 3,260 facets and do not constitute an alternative complete child partition.
The MiniLM normalized-cut compactification-like leaf overlaps 2,931 current
facets but also contains 196 outside it. These cannot be relabeled as exact
children without explicitly changing or deriving memberships.

The archived MiniLM global resolution-1 trial has ten communities; resolution-2
has twenty-three. Their intersections with current compactifications produce
seven and sixteen groups of at least twenty facets; the corresponding inflation
intersections produce six and thirteen. Neutrinos still have just one group of
at least twenty under either trial. These intersections are possible inputs to
a new organizational experiment, not supplied nested clusters or reviewed
scientific labels. Resolution changes alone do not define ancestry.

For complete deeper navigation while retaining current broad memberships, new
work would need to define a recorded within-parent refinement policy, retain
every existing overlap and unresolved placement, inspect representative and
boundary source descriptions, assign qualified labels, and recompute the
appropriate aggregate links. Existing frozen vectors/affinities can support
that work without a new embedding model. It should not quietly relax the old
gate or promote a rejected partition because the UI expects more levels.

## Provenance of the thirteen unresolved descriptions

They are not thirteen low-confidence predictions or a thresholded noise class.
The source `publication-v1/provenance/CHANGES.json` contains exactly thirteen
`organizational_membership` edits for these thirteen distinct question units,
each with operation `remove_sample` and `source_text_changed: false`. Every
current unresolved unit has this region as its sole direct home.

The assembler's `supported_operations` applies removal only when proposal and
independent challenge both explicitly request removal of the same supplied
sample, both assess it as outside that topic's scope, the sample role matches,
and neither whole review reports insufficient evidence. Its `unresolved_topic`
and membership-edit code preserve the description and append the unresolved
home instead of dropping the unit. The decision is about a particular topic
placement, not the validity of the paper or its scientific claim.

For example, the question from paper 2004.00030 was removed from the entropy
region because both stages read its supplied context as scalar-potential slopes
and de Sitter admissibility, rather than an entropy question. Paper 0803.3295's
question was removed from the EFT-consistency region because its supplied target
was a gravity dual of superconductivity. Those are concrete scope judgments;
they do not establish an alternative full grouping automatically.

Appropriate user wording is: **“These descriptions were removed from a sampled
topic after two review stages agreed they were outside its scope. A replacement
home has not yet been supplied.”** Keep paper/source access available. Avoid
claiming that their scientific confidence is lower or that they failed a numeric
membership-probability test.

## Bounded Q-007 UI outcome

Selecting the one broad group with children should reveal its actual smaller
clusters as clickable destinations, with an obvious route back to the parent.
Selecting a leaf should lead to its source descriptions and explicitly state
that this snapshot supplies no finer clusters. This repairs discoverability and
continuation without changing the Swampland organization or promising invented
depth. No new hierarchy build is part of this feedback repair.
