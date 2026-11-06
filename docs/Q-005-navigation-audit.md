# Q-005 — Repeated excerpts and unclear adjacent choices

Read-only baseline audit, 2026-11-06, against source commit
`8a9a00de2d0ee751ed732d7524d469f07ffba796` (prior released runtime `7600613`).
Descriptions of current behavior below are **pre-repair observations**. The
audit did not change the engine or frozen corpus.
[Recorded states, representative sources, branches and measurements](evidence/q005/navigation-audit.json).

The complaint has two different causes: the interface repeats one selected
source in several places, and the navigation really can return to identical
earlier states while presenting those returns as additional depth. Shortening
the displayed paragraph addresses only the first problem.

## Why this method becomes the starting text

The reported source is
`unit:0b1a39f68a400ae50d1d97ab6a9bd3e1b087d101231f4ebe49d49088b10b5b81`,
paper `1303.2661`, vector row 10588, in `units-005.json`. Its frozen facet type is
**method**. Its 238-character text describes a KK one-loop sum and zeta
regularization, followed by what that calculation adds to the massless spectrum.
It is not itself a physical question. The paper's actual question concerns when
five-dimensional supergravity can come from circle reduction of an anomaly-free
six-dimensional theory; the corpus also has a separate question facet for that
task. [Paper abstract](https://arxiv.org/abs/1303.2661).

The native `directions()` function uses the representative source's first
sentence, truncated at 125 characters, as its label. Its underlying `query`
remains the full source text, up to 3,900 characters. `applyAction(select)` puts
that query and the representative seed into the canonical state. The browser
then uses the query/context question in its large heading, editable input and
path, while source evidence displays the original text again. The preceding
Miller column still shows the selected direction. These repeated renderings are
not separate scientific results.

Fresh empty initialization reproduced **zero sources**, not the KK method.
The browser's initial route loader restores saved view/session state; a selected
method can therefore return on reopening. This audit did not inspect the user's
browser storage, so restoration is the supported mechanism, not a proven account
of the user's particular tab. Stored links and companion attachment are other
explicit restoration paths.

## Genuine repetitions across selections

The study made six successive selections from each of four initial contexts.
For the first choice it selected the reported method when offered; afterward it
selected the first offered direction. This is a reproducible navigation stress
case, not a claim that all users follow the first choice.

| Initial context | Observed repeated native states |
|---|---|
| `KK towers`, Explore | Steps 3–6 alternate `state-423509484f4d9a8c` and `state-b0156bfff06b97cf` |
| `KK towers`, Derive | Steps 4 and 6 are `state-3220b08bb5fd1b37`, with `state-8a67e35be794135f` between them |
| `KK towers`, Derive, Methods | Steps 4 and 6 are `state-24f38edd77ed13f1`, with `state-c141eccd6aa583c9` between them |
| `Kaluza-Klein towers`, Physical question lens | Steps 2–6 alternate `state-12affc573b52789b` and `state-fc90ab846a64058c` |

The Explore loop alternates a method facet and a question facet from the same
paper, `1612.07672`: comparing large-gauge transformations/anomaly factors, then
asking about Chern–Simons corrections and related consistency conditions. The
Derive loops alternate methods from `1303.2661` and `2005.12935`. The
question-only loop alternates `2311.12113` and `2405.00083`, two related
black-hole/species-tower questions. Choosing a question-only lens therefore does
not solve revisits.

The immediate exact-self guard works for the cited source: it remains the first
ranked evidence item but is not offered as its own next direction. However,
three of its five next choices offer that exact original source again one level
later. The guard checks the currently focused exact text only. Retrieval does
not receive the whole visited path, and `select` currently appends a state even
when the normalized state already occurs earlier.

No identical direction labels occurred **within** the 28 measured views. That
does not establish semantic diversity: exact repeats occur across levels, and
different excerpts can still address closely related tasks. Direction IDs
include the originating state, so seed/source identity and canonical state
identity are the useful repeat checks.

## Are the five choices meaningfully different?

Immediately after the cited method, all five choices are **methods**, even under
Explore. Their distinguishing features are clearer in the full evidence than
in their first sentences:

| Representative source | Distinction supported by its frozen method text |
|---|---|
| [1612.07672](https://arxiv.org/abs/1612.07672) | One-loop Chern–Simons terms from parity-violating modes and regularized KK sums |
| [hep-th/0611102](https://arxiv.org/abs/hep-th/0611102) | Charged spectra, orbifold parity and one-loop determinants in flux compactification |
| [2406.06704](https://arxiv.org/abs/2406.06704) | Five-dimensional prepotential combining classical six-dimensional/Green–Schwarz terms and loops |
| [2507.02339](https://arxiv.org/abs/2507.02339) | Epstein/Hurwitz zeta resummation for compactification spectra and the one-loop potential |
| [2005.12935](https://arxiv.org/abs/2005.12935) | Comparing regulator prescriptions for parity-violating KK triangle amplitudes |

These descriptions summarize the selected facet, not every source assigned to
its group. They are audit explanations, not proposed universal automatic labels.
Primary abstracts were checked for the paper-level scopes; full derivations
were not independently reproduced.

The last distinction matters scientifically. The `2005.12935` abstract says its
anomaly result requires preserving six-dimensional Lorentz invariance and that
ordinary zeta regularization is insufficient. Its current first-sentence label
does not expose that contrast. Turning all of these into “KK loop calculations”
would remove useful meaning. [Anomaly/regulator discussion in the abstract](https://arxiv.org/abs/2005.12935).

The five representatives' pairwise embedding cosines range from 0.372 to 0.570;
that is not an equivalence test and does not justify deleting them as duplicate
science. Selecting them retains only 15.6–34.4% of the prior 64-source set, so
they really do change retrieval substantially. Nor are the resulting sets
guaranteed to be increasingly narrow descendants: every step scans the corpus
again. “Level” means a navigation step, not a proven scientific hierarchy.

The intended KK → dark matter → decays route still produces question facets:
after each of the last two explicit follow-up questions, all five choices in
this audit are question facets. Two exact source representatives recur across
those two contexts. That recurrence can be scientifically appropriate: the
same cosmology paper is relevant to both dark matter and decay. Reuse should be
identified, not automatically treated as an error.

## Bounded correction and remaining limitation

1. **Expose what the choice is.** Distinguish a representative method from a
   representative question, using the seed's evidence facet rather than the
   inherited session lens. Add paper context and make the full excerpt
   inspectable. Do not mechanically turn a method into a question by adding
   “How” or a question mark. The current five labels are representative excerpts,
   not five independently synthesized adjacent research questions.
2. **Separate display from the scientific retrieval input.** A compact heading
   or path title can improve scanning while retaining the full query and source
   anchor. Keep the distinction visible and preserve exact export/import. The
   [previous short-query experiment](../tests/geometry/selection-query-results.json)
   changed top-ten overlap to 0.5, 0.6 and 0.7, and first-sentence queries
   reoffered the selected source in all three cases. Changing retrieval wording
   is not a harmless formatting fix.
3. **Make exact returns explicit.** For native `select`, when the resulting
   normalized state already exists in the active history prefix, offer “Return
   to step N” and restore that step instead of appending misleading extra depth.
   Preserve the scientific source; do not remove it from evidence or globally
   exclude its paper. Compare corpus, computation and full normalized state as
   well as its ID. Do not unexpectedly reuse an abandoned forward branch.
4. **Protect authored views.** An agent can attach different scientific context,
   labels and groups to the same canonical native state. State-ID equality alone
   must not collapse these distinct authored objects. Use exact saved authored
   restoration when available; do not replace it with native recomputation.
   Limit the automatic repeat correction to the supported native selection path.

These corrections make the present choices and revisits honest and more legible.
They do not establish optimal semantic grouping or resolve all near-duplicate
questions. Higher-level choices such as “Does this regulator preserve the
anomaly information I need?” require an explicit contextual synthesis, evidence
and authored label/action pairing. The contextual-view capsule already carries
that authored result; inventing a universal scientific rewrite from an excerpt
prefix is not an adequate substitute.

Acceptance should cover the reported six-selection routes, exact return labels
and restored views, source type, a readable full-excerpt disclosure, unchanged
numerical inputs, the separate KK/DM/decay journey, and preservation of authored
views sharing a native state. Actual interface legibility still needs browser
inspection; this audit ran only Node and source checks.
