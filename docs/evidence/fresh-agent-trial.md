# Independent fresh-agent navigation trial

Observed 2026-11-06 UTC. Evaluator: `/root/fresh_navigator_trial`. Bounded trial: eight navigation actions using the actual companion CLI. No implementation, skill, corpus, notebook, Git, deployment, credentials, or browser state was changed. The only output files are this report and `fresh-agent-session.json`.

**Verdict:** The portable skill and CLI are sufficient for an attentive fresh agent to perform a useful axion → axion-WGC derivation → early-dark-energy consequence → axion-dilaton mechanism journey. It is a qualified success for conversational retrieval, with a material context-drift limitation. It is not an end-to-end browser pass: final state inspection reports no viewer and no rendering acknowledgement.

The supplied request was: “I am interested in axions and why quantum gravity might constrain them. Help me go from that broad idea toward how the constraints are derived, then toward a phenomenological consequence. Follow a useful deeper branch, compare a pivot, and preserve the useful journey.”

Read the skill, its interface reference, repository AGENTS.md, Lab Notebook.md and Q-001 plan. Used the already-running companion rather than exercising first-time installation/build. Skill portability therefore means successful use from documented instructions with a known checkout and connection receipt; a separate-machine setup was not tested. The receipt was consumed by the CLI only; no token was printed or added to these artifacts.

**Observed successes and limits.** `state`, `search`, `evidence`, `action` and `export` worked without a failed call. All eight computed views offered exactly five source-linked directions and retained stable source IDs. Derive/method and phenomenology/combined transitions materially changed rankings and directions. Final history preserves the initial state and all eight actions; no failed intermediate state was erased. Search/evidence explicitly label descriptions as retrieval nominations and expose source reading scope. The skill correctly instructs an agent to verify real papers and to distinguish source fidelity from direction-centroid fidelity.

The clearest failure is steps 3–4. Selecting the EDE mathematical direction copies its entire indexed paragraph into the query. The selected source survives, but nearby generic instanton methods dominate. The following phenomenology refinement automatically inherits those top-five sources and keeps generic instanton terms as context, despite a self-contained EDE query. The tool does not flag scientific topic drift; the agent must notice it. This is a navigation-quality limitation rather than a blocker for this bounded journey: the documented explicit-anchor recovery worked. Step 5 changes both query wording and anchors, so it does not isolate which change caused recovery. Step 6 holds the recovered query fixed and tests a true pivot.

Direction labels are long excerpts, sometimes truncated mid-thought; their full `query` is available. They offer nearby questions rather than a scientifically ordered curriculum. Diversified choices can be useful but also include remote neighbors. Treating all five as equally pertinent or as logical consequences would be misleading.

**Source checks, separate from indexed descriptions.** The original paper text supports a useful scientific route, with important qualifications:

- [1605.05311, introduction and §2.1](https://arxiv.org/html/1605.05311v1): connects the ordinary WGC to avoiding global-symmetry limits and black-hole discharge, then discusses an axion/instanton generalization. This motivates constraints; it is not a proof of a universal axion bound. The paper's added note reports counterexamples to its precise lattice-WGC formulation. That caveat is absent from the short indexed nomination and illustrates why opening the source matters.
- [2203.05575, §§II–V](https://arxiv.org/html/2203.05575v1): adopts fS/k ≤ c M_Pl, defines f_eff=f/k and m_chi²=Lambda_UV⁴ exp(-S)/f_eff², then eliminates S to get a logarithmic bound. With its chosen coefficient, m_chi≈10^-27 eV and Lambda_UV≈10^16 GeV, it reports f_eff≲0.008 M_Pl. Its model-dependent cosmological translation gives roughly f_EDE≲0.004 for n=2,3. The instanton satisfying the conjecture must be tied to the potential for that direct inference; the paper discusses the extra-instanton loophole and uncertain coefficient. These are conditional paper claims, not established exclusions of all EDE models. For n>1, m_chi is a mass parameter, not the small-oscillation mass. The HTML text's §IV inequality sign disagrees with Eq. (11), so the equation and discussion were used rather than silently promoting that sentence.
- [1904.08912, abstract](https://arxiv.org/abs/1904.08912): confirms the proposed axion-dilaton destabilization mechanism, a fast-roll phase with w=1, and dilution as a^-6. This confirms the proposed consequence, not observational success today or satisfaction of every WGC assumption. Its indexed numerical-method description was inspected through `evidence`, but its numerical calculation was not reproduced.

Source access was text/HTML only. No paper figure or browser UI was visually inspected. No new embeddings were generated, and no claim is made that every source in a group supports its representative's physical argument. Newer neighboring papers shown by the frozen corpus were not independently verified.

**Geometry and scope.** Corpus `swampland-navigation-20261105-minilm-v1`, frozen 2026-11-05: 6,478 papers, 6,477 with vector coverage, 26,410 units, publication scope 1969–2026-11. The chart fits five direction centroids in 384-dimensional embedding space. Across this trial, group retained variance is 66.3–75.1%; source-overlay retained variance is only 12.6–21.1%, and source five-neighbor recall is 20.9–31.9%. Warnings about omitted source variation are present in every nonempty view. Five-group recall@5=1 is not persuasive geometry validation because there are only four other groups. Distances and slab thickness are embedding/display quantities, not physical scales or proof of implication. Exact metrics below are observed engine outputs.

**Display and preservation.** After the last action, a separate `state` call returned revision 8, state `state-bb0cdb0c74474bb0`, `acknowledgedCurrent:false`, zero known/acknowledging viewers, and `lastRenderedStateId:null`. The updates were computed; their display is unconfirmed. Browser automation was not attempted. Export succeeded to [fresh-agent-session.json](fresh-agent-session.json), a portable session with corpus/computation identifiers and nine history entries. Export contains no token/authorization keys. It has not been imported into another process or renderer in this trial.

**Actual supporting commands.** All CLI commands ran from `/Users/emmy/Documents/Eigenquestions`, using `--connection /private/tmp/eigenquestions-q001-review.json`. The receipt path is not its secret token.

```sh
node bin/navigate.mjs state --connection /private/tmp/eigenquestions-q001-review.json
node bin/navigate.mjs search --query 'axions quantum gravity constraints' --limit 8 --connection /private/tmp/eigenquestions-q001-review.json
node bin/navigate.mjs evidence --ids 'unit:f5dec9b2d4dc6384ca412c8833621f00443379b3fc52ef04d918abd3d1972b9f,unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439' --connection /private/tmp/eigenquestions-q001-review.json
node bin/navigate.mjs evidence --ids 'unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3,unit:16a885b2c87f070aa6068db72bb5a37f8f4d5c7359c691cf319f911561656abb' --connection /private/tmp/eigenquestions-q001-review.json
node bin/navigate.mjs state --connection /private/tmp/eigenquestions-q001-review.json
node bin/navigate.mjs export --out docs/evidence/fresh-agent-session.json --connection /private/tmp/eigenquestions-q001-review.json
```

**Action evidence.** Source titles below are ranked retrieval results, not independent source verification. Full state queries and focus IDs are retained in the portable export; selected IDs and current directions are preserved here. Replaying an exported history index should recompute the larger view on the matching frozen engine/corpus.

### Step 1: state-4c2912c8f5d8cf38

Broad entry: lattice WGC, natural inflation, and EDE are intelligible options; the vacuumon is a more remote option.

```sh
node bin/navigate.mjs action --json '{"type":"navigate","query":"axions quantum gravity constraints","intent":"explore","workRelation":"either","lens":"combined"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: []. Focus IDs: 0.

Top five ranked sources:

1. [1605.05311: Axion Experiments to Algebraic Geometry: Testing Quantum Gravity via the Weak Gravity Conjecture](https://arxiv.org/abs/1605.05311) — `unit:f5dec9b2d4dc6384ca412c8833621f00443379b3fc52ef04d918abd3d1972b9f`
2. [1412.3457: Natural Inflation and Quantum Gravity](https://arxiv.org/abs/1412.3457) — `unit:5f5acebe2dc1df1ad97272a28776c9bcc2f118e8fffa0fc2ae81cccdc7831a69`
3. [2008.00523: String-Inspired Running Vacuum—The “Vacuumon”—And the Swampland Criteria](https://arxiv.org/abs/2008.00523) — `unit:bd93d46488fbbc9c42f355ea3a14896f6ffdc1b855a6975e7925107e0cc737df`
4. [hep-th/0605264: On the Geometry of the String Landscape and the Swampland](https://arxiv.org/abs/hep-th/0605264) — `unit:8e5c5554af6775f98a05e3a2939e55c5b69c696c4b65a4959508d21281b6f986`
5. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`

Five computed directions:

- `direction:5108eafd` — Can a stronger, lattice-wide weak-gravity requirement characterize consistent quantum gravity and yield testable… Seed: `unit:f5dec9b2d4dc6384ca412c8833621f00443379b3fc52ef04d918abd3d1972b9f`.
- `direction:0a543a19` — Can natural inflation with a parametrically large effective axion range be realized in a controlled higher-dimensional… Seed: `unit:5f5acebe2dc1df1ad97272a28776c9bcc2f118e8fffa0fc2ae81cccdc7831a69`.
- `direction:a9ff8db9` — Which geometric restrictions distinguish continuous moduli spaces of consistent quantum gravity from those of… Seed: `unit:8e5c5554af6775f98a05e3a2939e55c5b69c696c4b65a4959508d21281b6f986`.
- `direction:7bf4c25e` — Does satisfying conjectured quantum-gravity constraints make the vacuumon a faithful quantum description of… Seed: `unit:bd93d46488fbbc9c42f355ea3a14896f6ffdc1b855a6975e7925107e0cc737df`.
- `direction:33323f14` — Can axion models of early dark energy be embedded in quantum gravity, and how strongly does the axion weak gravity… Seed: `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`.

Group/source retained variance: 68.78% / 13.78%; source neighbor recall@5: 25.94%.

### Step 2: state-77cb1f5d5905dad1

Derive intent/method lens: instanton-action, axion-string, warped-brane and EDE methods appear. This is a useful change in evidence type.

```sh
node bin/navigate.mjs action --json '{"type":"refine","query":"How does the axion weak gravity conjecture constrain axion decay constants through instanton actions?","intent":"derive","lens":"method"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["quantum","constraint","inflation"]. Focus IDs: 5.

Top five ranked sources:

1. [1605.05311: Axion Experiments to Algebraic Geometry: Testing Quantum Gravity via the Weak Gravity Conjecture](https://arxiv.org/abs/1605.05311) — `unit:862146f06a32a0342980194e6b2456779bbf59ce7f90edc163b08189ae2da0d8`
2. [2108.11383: The Weak Gravity Conjecture and axion strings](https://arxiv.org/abs/2108.11383) — `unit:c6186ab72e52e30e39e2ce551ab5c9eca699ce2b21ab18e6f597f01ffc6aa0d6`
3. [1509.07049: Warping the Weak Gravity Conjecture](https://arxiv.org/abs/1509.07049) — `unit:58501667eefd3129683875189bc901b5f4f48811769812dde733e78e036e35f9`
4. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`
5. [2508.08346: Quantum gravity and entanglement in particle physics and gravitation](https://arxiv.org/abs/2508.08346) — `unit:900aed08eb53fd792866322bef4286d9846a42352e6d9453e55cf6884293c3b9`

Five computed directions:

- `direction:dc6e06af` — Translate weak-gravity bounds into instanton-action constraints, CFT charge/dimension conditions, and wrapped-brane… Seed: `unit:862146f06a32a0342980194e6b2456779bbf59ce7f90edc163b08189ae2da0d8`.
- `direction:43cc3b88` — Combine the electric axion WGC, an assumed gauge-instanton action, and the WGC for the dual two-form to bound string tension. Seed: `unit:c6186ab72e52e30e39e2ce551ab5c9eca699ce2b21ab18e6f597f01ffc6aa0d6`.
- `direction:ab39a368` — Dimensionally reduce the D-brane DBI action to obtain the four-dimensional gauge coupling and axion kinetic term. Seed: `unit:58501667eefd3129683875189bc901b5f4f48811769812dde733e78e036e35f9`.
- `direction:284d89f9` — The instanton action is related to the potential amplitude through mχ²=ΛUV⁴e^(−S)/feff². Seed: `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`.
- `direction:662adb0a` — The axion–gravity effective action contains Einstein gravity, a massive pseudoscalar and a coupling −AbRCS. Seed: `unit:900aed08eb53fd792866322bef4286d9846a42352e6d9453e55cf6884293c3b9`.

Group/source retained variance: 66.27% / 17.71%; source neighbor recall@5: 27.81%.

### Step 3: state-a4cd95a34eba617b

Selected EDE method: EDE remains rank 1, but generic quantum-cosmology instantons become rank 2 and the leading direction. A neutrino/NEDE direction is also remote from the intended question.

```sh
node bin/navigate.mjs action --json '{"type":"select","directionId":"direction:284d89f9"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["early","dark","constraint","energy"]. Focus IDs: 1.

Top five ranked sources:

1. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`
2. [2302.04962: Quantum cosmology, eternal inflation, and swampland conjectures](https://arxiv.org/abs/2302.04962) — `unit:b71a5fde1aec94b5c4ced257ba094ee3eeb0db525fbcd83a214ace6d4cd7a467`
3. [1910.08691: Electroweak Quintessence Axion as Dark Energy](https://arxiv.org/abs/1910.08691) — `unit:89c11e984279e463a2196487ec3b176a82228ea20efc9f0cd9206abfaa4cb64f`
4. [0912.1341: Dante's Inferno](https://arxiv.org/abs/0912.1341) — `unit:a475d818f1c31ee98e50542f55ae3970b1244a87a1ed6fd525b6a8b1fb7904ee`
5. [hep-th/0607086: Cosmological Constant and Axions in String Theory](https://arxiv.org/abs/hep-th/0607086) — `unit:1fd372a9d25d5ba0727c825ad6565298601e8f6610f6ecb188e1071c95d8c356`

Five computed directions:

- `direction:aa83dc07` — Leading semiclassical instanton comparison using P_nuc ∝ exp(−|S_E|), so the smallest action magnitude dominates. Seed: `unit:b71a5fde1aec94b5c4ced257ba094ee3eeb0db525fbcd83a214ace6d4cd7a467`.
- `direction:189bb6f6` — Combine the electric axion WGC, an assumed gauge-instanton action, and the WGC for the dual two-form to bound string tension. Seed: `unit:c6186ab72e52e30e39e2ce551ab5c9eca699ce2b21ab18e6f597f01ffc6aa0d6`.
- `direction:fcbb2b31` — Combine the thermal-equilibrium lower bound on λ with the imported neutrino-streaming constraint gs < 10⁻⁷/κ², the… Seed: `unit:ed34dd36f4e48c4e43ca5686752969d62855b65f0d8dcfe11ab0401bb0bd3514`.
- `direction:07195388` — Constrained-instanton calculus estimates the electroweak vacuum energy after inserting higher-dimensional B+L-violating… Seed: `unit:89c11e984279e463a2196487ec3b176a82228ea20efc9f0cd9206abfaa4cb64f`.
- `direction:85d06569` — Dimensional reduction of higher-form kinetic terms on normalized harmonic forms estimates axion decay constants; wrapped… Seed: `unit:1fd372a9d25d5ba0727c825ad6565298601e8f6610f6ecb188e1071c95d8c356`.

Observed indexed descriptions for the top five sources (retrieval descriptions, not quotations from verified papers):

1. The instanton action is related to the potential amplitude through mχ²=ΛUV⁴e^(−S)/feff². Substitution into the axion WGC produces an n-independent inequality involving feff and a logarithm of ΛUV⁴/(feff²mχ²). The bound is evaluated for representative EDE parameters.
2. Leading semiclassical instanton comparison using P_nuc ∝ exp(−|S_E|), so the smallest action magnitude dominates. Near the transition, a domain-wall ansatz and illustrative quartic potential supplement the negative-mode argument.
3. Constrained-instanton calculus estimates the electroweak vacuum energy after inserting higher-dimensional B+L-violating operators. The instanton-size integral is dominated by small instantons near the assumed Planck cutoff.
4. Estimate instanton amplitudes through Λ⁴ proportional to e^(−SED1), and assess decay-constant hierarchies using cycle geometry and warping. Compare induced D3 charge and NS5 worldvolume KK masses parametrically with the single-axion monodromy construction.
5. Dimensional reduction of higher-form kinetic terms on normalized harmonic forms estimates axion decay constants; wrapped worldsheet, membrane and D-brane actions connect these constants to instanton suppression.

Group/source retained variance: 67.39% / 13.44%; source neighbor recall@5: 20.94%.

### Step 4: state-5da855e8ad8a6074

Explicit phenomenology wording with default inherited anchors: first four sources remain instanton/geometry methods, and contextTerms are instanton, estimate, action. The desired EDE question is rank 6. This is the clearest drift.

```sh
node bin/navigate.mjs action --json '{"type":"refine","query":"What phenomenological constraints does the axion weak gravity conjecture impose on early dark energy and its energy fraction?","intent":"phenomenology","lens":"combined"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["instanton","estimate","action"]. Focus IDs: 5.

Top five ranked sources:

1. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`
2. [hep-th/0607086: Cosmological Constant and Axions in String Theory](https://arxiv.org/abs/hep-th/0607086) — `unit:1fd372a9d25d5ba0727c825ad6565298601e8f6610f6ecb188e1071c95d8c356`
3. [1910.08691: Electroweak Quintessence Axion as Dark Energy](https://arxiv.org/abs/1910.08691) — `unit:89c11e984279e463a2196487ec3b176a82228ea20efc9f0cd9206abfaa4cb64f`
4. [0912.1341: Dante's Inferno](https://arxiv.org/abs/0912.1341) — `unit:a475d818f1c31ee98e50542f55ae3970b1244a87a1ed6fd525b6a8b1fb7904ee`
5. [2609.16165: Instanton Interactions and the Axion Weak Gravity Conjecture](https://arxiv.org/abs/2609.16165) — `unit:c6c86df782561dcce60ac528d3d4dc67d6575ad8ad7091b986a1faf68f273f77`

Five computed directions:

- `direction:a3b78ac9` — The instanton action is related to the potential amplitude through mχ²=ΛUV⁴e^(−S)/feff². Seed: `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`.
- `direction:25086cbb` — Dimensional reduction of higher-form kinetic terms on normalized harmonic forms estimates axion decay constants; wrapped… Seed: `unit:1fd372a9d25d5ba0727c825ad6565298601e8f6610f6ecb188e1071c95d8c356`.
- `direction:78677100` — For phenomenological interactions between dark matter and dark energy, how restrictive is the scalar-excursion condition… Seed: `unit:67512e703aacb45fc69bfd223366b9ff12a1f3c9ae78c3f93be4d1bd795503fd`.
- `direction:e3f22fdf` — Can the axionic Weak Gravity Conjecture be formulated sharply through nonbinding long-distance interactions of identical… Seed: `unit:c6c86df782561dcce60ac528d3d4dc67d6575ad8ad7091b986a1faf68f273f77`.
- `direction:730575fa` — Constrained-instanton calculus estimates the electroweak vacuum energy after inserting higher-dimensional B+L-violating… Seed: `unit:89c11e984279e463a2196487ec3b176a82228ea20efc9f0cd9206abfaa4cb64f`.

Observed indexed descriptions for the top five sources (retrieval descriptions, not quotations from verified papers):

1. The instanton action is related to the potential amplitude through mχ²=ΛUV⁴e^(−S)/feff². Substitution into the axion WGC produces an n-independent inequality involving feff and a logarithm of ΛUV⁴/(feff²mχ²). The bound is evaluated for representative EDE parameters.
2. Dimensional reduction of higher-form kinetic terms on normalized harmonic forms estimates axion decay constants; wrapped worldsheet, membrane and D-brane actions connect these constants to instanton suppression.
3. Constrained-instanton calculus estimates the electroweak vacuum energy after inserting higher-dimensional B+L-violating operators. The instanton-size integral is dominated by small instantons near the assumed Planck cutoff.
4. Estimate instanton amplitudes through Λ⁴ proportional to e^(−SED1), and assess decay-constant hierarchies using cycle geometry and warping. Compare induced D3 charge and NS5 worldvolume KK masses parametrically with the single-axion monodromy construction.
5. Can the axionic Weak Gravity Conjecture be formulated sharply through nonbinding long-distance interactions of identical instantons, and under which scalar-field assumptions does that condition imply a bound on the axion decay constant and instanton action?

Group/source retained variance: 74.90% / 21.12%; source neighbor recall@5: 28.75%.

### Step 5: state-50de20ed029fb909

Recovery with two explicit EDE anchors and a shorter resolved cosmology query: EDE returns rank 1, axion-dilaton EDE rank 4; current directions again include useful cosmology choices.

```sh
node bin/navigate.mjs action --json '{"type":"refine","query":"axion early dark energy energy fraction Hubble tension observational consequences","intent":"phenomenology","lens":"combined","focusIds":["unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439","unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3"]}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["conjecture","weak","gravity","constraint"]. Focus IDs: 2.

Top five ranked sources:

1. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`
2. [2604.09141: Bounding axion dark energy](https://arxiv.org/abs/2604.09141) — `unit:b103a72317a3c5ecb8c828815acd3dd69bc83e0a13264ece829351c5f896fac4`
3. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:3fa3b7d19670eb7682119b977121ccbfae92ca74387fefb633cc52010086e3c3`
4. [1904.08912: Axion-Dilaton Destabilization and the Hubble Tension](https://arxiv.org/abs/1904.08912) — `unit:bc7bff207a8fc2a36917d1a6ae207475e1385d03234ecf8234f4d507af650454`
5. [1910.08691: Electroweak Quintessence Axion as Dark Energy](https://arxiv.org/abs/1910.08691) — `unit:f292ab0dcc1705ec766ea8e97e3f4cb614ca8f3332f6da09002666ca9e7dc5da`

Five computed directions:

- `direction:cdbcd475` — Can axion models of early dark energy be embedded in quantum gravity, and how strongly does the axion weak gravity… Seed: `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`.
- `direction:458d05ac` — Can WGC-motivated bounds on canonical scalar excursions be reformulated using the defining infrared cutoffs of… Seed: `unit:270509d2f6c30cfbc0ac906eb6624ce3f328f39bfaa9cc482579bd831a6d7266`.
- `direction:3bb3eff1` — Can the order-one coefficient in the axion WGC be sharpened, and can supersymmetry impose stronger instanton and… Seed: `unit:73cbff6e91a5b915cae72adbfa11a71e5fee228ec0bb99a41bdc972f52aa7504`.
- `direction:133ef31f` — How do constant dark-energy equation of state and present matter abundance jointly determine the expansion history and… Seed: `unit:17ce6a8c558247f5d1babb1f7b675efcc62a404687ac8380c8458f643cfa24b9`.
- `direction:a13b5830` — Can an interacting axion–dilaton system realize early dark energy that dissipates near recombination, providing a… Seed: `unit:bc7bff207a8fc2a36917d1a6ae207475e1385d03234ecf8234f4d507af650454`.

Group/source retained variance: 75.05% / 20.76%; source neighbor recall@5: 31.87%.

### Step 6: state-5e5953fbe0a178ef

Same-query pivot: anchors clear, axion-dilaton EDE rises to rank 1, and more cosmological directions appear. This is a genuine, interpretable change.

```sh
node bin/navigate.mjs action --json '{"type":"pivot","query":"axion early dark energy energy fraction Hubble tension observational consequences","intent":"phenomenology","lens":"combined"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: []. Focus IDs: 0.

Top five ranked sources:

1. [1904.08912: Axion-Dilaton Destabilization and the Hubble Tension](https://arxiv.org/abs/1904.08912) — `unit:bc7bff207a8fc2a36917d1a6ae207475e1385d03234ecf8234f4d507af650454`
2. [2203.05575: Constraints on early dark energy from the axion weak gravity conjecture](https://arxiv.org/abs/2203.05575) — `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`
3. [2511.22559: Cosmology of axion dark energy in supersymmetric models and constraints on high-scale parameters](https://arxiv.org/abs/2511.22559) — `unit:a906166395971cdb66386e0ee3031e4be29023efcd39235f1c737d287fa0d0c7`
4. [2112.09128: Early dark sector, the Hubble tension, and the swampland](https://arxiv.org/abs/2112.09128) — `unit:b815dd160e57fb55e9ea389a7553227ab4c02b2e181a7da62dd08571b2dab756`
5. [2005.14053: Unified framework for early dark energy from $\alpha$-attractors](https://arxiv.org/abs/2005.14053) — `unit:4d0e750899a2c52abc9884da3304caa54be49c5b95056a41fc82de7ce3b0eee4`

Five computed directions:

- `direction:6de41fc5` — Can an interacting axion–dilaton system realize early dark energy that dissipates near recombination, providing a… Seed: `unit:bc7bff207a8fc2a36917d1a6ae207475e1385d03234ecf8234f4d507af650454`.
- `direction:ce4cf460` — Can axion models of early dark energy be embedded in quantum gravity, and how strongly does the axion weak gravity… Seed: `unit:a63af1f399a818071def931852f274e26e4b6ba1a36b770c5f7fbf6187291439`.
- `direction:bbfe8006` — Can a single axionic dark-energy field with multiple cosine harmonics and a Lagrangian interaction with scalar dark… Seed: `unit:a906166395971cdb66386e0ee3031e4be29023efcd39235f1c737d287fa0d0c7`.
- `direction:a031a81c` — Can cosmological bounds on a scalar-dependent dark-matter mass challenge an SDC-motivated early-dark-energy model when… Seed: `unit:b815dd160e57fb55e9ea389a7553227ab4c02b2e181a7da62dd08571b2dab756`.
- `direction:796bdf5a` — Can minimally coupled α-attractor scalar potentials provide a common framework for different early-dark-energy injection… Seed: `unit:4d0e750899a2c52abc9884da3304caa54be49c5b95056a41fc82de7ce3b0eee4`.

Group/source retained variance: 75.07% / 16.21%; source neighbor recall@5: 27.50%.

### Step 7: state-a8ff1fcc5316d994

Select the axion-dilaton branch: nearby axio-dilaton models and an original-paper numerical method appear, while the WGC/EDE paper remains in view at rank 8.

```sh
node bin/navigate.mjs action --json '{"type":"select","directionId":"direction:6de41fc5"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["destabilization"]. Focus IDs: 1.

Top five ranked sources:

1. [1904.08912: Axion-Dilaton Destabilization and the Hubble Tension](https://arxiv.org/abs/1904.08912) — `unit:bc7bff207a8fc2a36917d1a6ae207475e1385d03234ecf8234f4d507af650454`
2. [2512.13544: The Serendipitous Axiodilaton: A Self-Consistent Recombination-Era Solution to the Hubble Tension](https://arxiv.org/abs/2512.13544) — `unit:00d5751423da07ea4f6eb13b7ef6de7fcdedc730b926e15d3e51bb9b1ca9c720`
3. [2410.11099: A Minimal Axio-dilaton Dark Sector](https://arxiv.org/abs/2410.11099) — `unit:84f7837aaa838b43f86ca0b1f9d246a71640b984dfd2992b32e26429618e4fcc`
4. [2505.05450: Screened axio-dilaton cosmology: novel forms of early dark energy](https://arxiv.org/abs/2505.05450) — `unit:678f966692576be2ec931aa2c4536661f2cbe091382aeed5e55a22031bc8cd15`
5. [1808.08967: De Sitter vs Quintessence in String Theory](https://arxiv.org/abs/1808.08967) — `unit:3e128e2c27707a02e0bdeac7f67e0c0dbf99dcf847fc8a5389cab4ad4912c1cc`

Five computed directions:

- `direction:6c596dc2` — Can a dynamical axio-dilaton dark sector alleviate the Hubble tension through correlated changes in particle masses,… Seed: `unit:00d5751423da07ea4f6eb13b7ef6de7fcdedc730b926e15d3e51bb9b1ca9c720`.
- `direction:c25f195d` — Can a minimal axio-dilaton pair supply both dark matter through axion oscillations and dark energy through the dilaton,… Seed: `unit:84f7837aaa838b43f86ca0b1f9d246a71640b984dfd2992b32e26429618e4fcc`.
- `direction:bc1f1289` — Coupled-field numerical examples follow axion oscillations, dilaton destabilization, and wφ as a function of redshift. Seed: `unit:16a885b2c87f070aa6068db72bb5a37f8f4d5c7359c691cf319f911561656abb`.
- `direction:3701cd19` — Can transient pre-recombination Early Dark Energy reconcile sound-horizon-calibrated and direct determinations of H0… Seed: `unit:5fc4d96969fb3009992757a37a3b13de55ace9d448c8215f4b59ef29296a5f14`.
- `direction:d59b1114` — Can an axio-dilaton model with locally screened dilaton forces produce viable dynamical dark energy, and what early dark… Seed: `unit:678f966692576be2ec931aa2c4536661f2cbe091382aeed5e55a22031bc8cd15`.

Group/source retained variance: 71.45% / 12.60%; source neighbor recall@5: 23.44%.

### Step 8: state-bb0cdb0c74474bb0

Deeper mechanism refinement: original-paper coupled-field numerical method is rank 1; a fluid/coarse-graining method is rank 2. A redshift-survey paper at rank 3 and distant screening direction show residual keyword/neighbor noise.

```sh
node bin/navigate.mjs action --json '{"type":"refine","query":"How do axion oscillations destabilize the dilaton in early dark energy, and why does its energy redshift as a^-6?","intent":"derive","lens":"method"}' --connection /private/tmp/eigenquestions-q001-review.json
```

Context terms: ["axio","hubble"]. Focus IDs: 5.

Top five ranked sources:

1. [1904.08912: Axion-Dilaton Destabilization and the Hubble Tension](https://arxiv.org/abs/1904.08912) — `unit:16a885b2c87f070aa6068db72bb5a37f8f4d5c7359c691cf319f911561656abb`
2. [2505.05450: Screened axio-dilaton cosmology: novel forms of early dark energy](https://arxiv.org/abs/2505.05450) — `unit:bf8042b53ecb5d1fb367e5fd317f0f53c4b5f85ffbe0c6da5be9582d72b4d344`
3. [astro-ph/0606533: Can A Galaxy Redshift Survey Measure Dark Energy Clustering?](https://arxiv.org/abs/astro-ph/0606533) — `unit:d8103cee63d464e941c873dd56e31204523c0d9230ce178ff07799d486ca5ae1`
4. [2104.09923: The stochastic axiverse](https://arxiv.org/abs/2104.09923) — `unit:92d58d7184801935c9099b5d8c52371335b7420f3237e1955722d1175608d8b0`
5. [2310.05901: Trans-Planckian censorship constraints on properties and cosmological applications of axion-like fields](https://arxiv.org/abs/2310.05901) — `unit:a61eda7c5a92cdd65a242105b5c1a4be135ce94281af5f9dbcbf36ed167e5ed2`

Five computed directions:

- `direction:b4d021f8` — Coupled-field numerical examples follow axion oscillations, dilaton destabilization, and wφ as a function of redshift. Seed: `unit:16a885b2c87f070aa6068db72bb5a37f8f4d5c7359c691cf319f911561656abb`.
- `direction:914ee386` — Coarse-grain the action over rapid axion oscillations, introduce Madelung density and phase variables, and derive… Seed: `unit:bf8042b53ecb5d1fb367e5fd317f0f53c4b5f85ffbe0c6da5be9582d72b4d344`.
- `direction:8ac87086` — Uses imported fitting prescriptions for dark-energy and matter transfer functions, including neutrino-dependent growth. Seed: `unit:d8103cee63d464e941c873dd56e31204523c0d9230ce178ff07799d486ca5ae1`.
- `direction:8968a010` — Quintessence simulations evolve classical axions from zero velocity at early redshift with dust-like matter. Seed: `unit:a61eda7c5a92cdd65a242105b5c1a4be135ce94281af5f9dbcbf36ed167e5ed2`.
- `direction:e365f329` — Minimize the combined interior axion/dilaton gradient energy and exterior dilaton energy over an integration constant,… Seed: `unit:b36807210278d5b0fb25cb1de8d3b7543971e574f17d88a21a1f2360b3253500`.

Group/source retained variance: 75.04% / 18.39%; source neighbor recall@5: 30.00%.

The independent findings above were frozen before seeing the geometry owner's proposed query-length comparison. No engine tuning was performed as part of this evaluation.

