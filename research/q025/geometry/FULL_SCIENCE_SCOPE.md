# Scientific objects beyond the question/method projection

The numerical question atlas is an organizational projection of a much richer
existing source graph. It is not the full scientific graph. The frozen foundation
has281,128 source objects,400,435 edges,392,553 evidence objects and296,130 retrieval
facets. Its objects include36,131 claims,52,438 assumptions,33,160 conventions,
18,893 control regimes,4,110 bounded derivations and47,728 limitations.

The edge census distinguishes274,650 structural edges,14,499 source-local
assertions,1,069 extraction inferences,609 local nominations and109,608 unvalidated
identifier mentions. The97 separately reviewed cross-paper relations are an
additional sparse layer. Their endpoints do not exactly match any question-view
node; mapping them through papers is context association, not a verified relation
between all questions in the two papers.

Exact joins are available now:

- Question unit `node_ids` → scientific `nodes.id`.
- Scientific edge `source` / `target` → those exact objects; preserve edge type,
  direction, semantic status, source record and evidence IDs.
- `has_assumption`, `has_convention`, `has_control_regime`, `has_derivation` and
  related property edges qualify their actual parent scientific object.
- Retrieval facet `node_id` → scientific object; facet `id` → vector index rows,
  question input facets and original embedding rows.
- Scientific node `evidence_ids` → exact archived evidence; preserve direct versus
  inherited-parent-context evidence scope and source reading limits.

Only2,408 of8,473 question units have incident noncontainment local source edges.
All have source-record context. A source record can be a deep section or a broad
whole-paper extraction, so co-record objects must be presented as context rather
than silently treated as the question's premises. The scientific evaluator's
`../evaluation/rich-context-joins.json` gives the detailed census and examples.

The full MiniLM release also has57,822 paper×facet vectors. Each row records the
exact input facet IDs. Round3 reuses result, applicability and mathematical-structure
views as separate candidate context signals; it does not encode new text. Result
context covers6,476 papers, applicability6,477, while mathematical structure covers
only486 papers. That last layer has pronounced extraction-depth missingness and
must not be interpreted as proof that other papers have no mathematical structure.

Round3 emits deduplicated source objects, retained local edges, exact property
paths, and separately marked same-extraction context. These can support lazy
source-card loading without shipping296,130 vectors to a browser. Paper-facet
similarity affects only an explicitly named experimental geometric construction;
it does not establish question-specific assumptions, implications or equivalence.
