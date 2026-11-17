# Complete recorded source context, compact paper catalogs

The v3.1 pack exposes **all 400,435 native source-graph edges plus 97 admitted reviewed relations**, with 281,127 source nodes, for the 6,477 papers represented by all 26,410 browser question/method entries. Every exact unit anchor resolves. This replaces the earlier question-selected export as the complete recorded-connection candidate; it does not upgrade extraction objects or mention edges into independent scientific evidence.

Native statuses remain separate: 274,650 structural edges, 14,499 source-local assertions, 1,069 extraction inferences, 609 local nominations and 109,608 unvalidated mentions. The 97 admitted cross-paper relations retain their exact direction, applicability, conventions, receipt hashes and reader notes. All 31 nonpositive outcomes remain inactive assessments, including all five mandatory withheld reader notes. The exact method view reaches 51 admitted relations, with both endpoints represented for 50. No question equivalence is inferred.

The old pack omitted 22,224 noncontainment/nonmention incident method edges and one method anchor. The audit is preserved under `source-index-v2/`; v3.1 includes every such edge. Native noncontainment/nonmention local relations occur for 2,408/8,473 questions and 2,485/17,937 methods. Other units retain exact source anchors and honest window/paper context; lack of extracted local relations is not absence of assumptions in the source.

The only excluded native node is `paper:d27c5a2cd841f6565a2a:unavailable`, an unavailable-paper stub with no browser entry or incident edge. No PDF is inferred for this record. There are zero excluded native edges.

## Payload and lookup

Slurm **61429408** completed in 2m24s under `randall_lab/test`, four CPUs/16 GiB; reported peak RSS was 2,850,664 KiB. Input hashes, output hashes and invariants are in `pack/manifest.json`; local verification independently checked all 6,735 referenced payload/index/summary files and all unique unit IDs.

| Artifact | Size |
| --- | ---: |
| Initial context index | 33,678 bytes |
| 256 lazy unit-index buckets | 21,614,396 bytes total; 105,580 maximum |
| 6,477 paper gzip payloads | 190,188,023 bytes total; 799,573 maximum |
| Maximum decompressed paper payload | 6,155,746 bytes |
| Optional plain paper summary | 5,619,971 bytes |
| Combined referenced files | 217,456,068 bytes |

Opening a context loads the root index, one unit-ID bucket and one paper payload. The full plain summary is optional, not part of the initial view. Unit descriptors include plain source-page locators and exact evidence IDs for static/agent readers. Source summaries, conditions and quote-free page locators remain in bounded gzip payloads. No source PDF, page image, original paper abstract or full source packet is exported.

Both lenses use the reference override policy in `source-index-v2/context_override.py`. Direct attachment means exact graph incidence, **not scientific support**; structural containment and literal mentions retain their status. A shared numbered extraction window requires exact paper/record/window identity. Whole-paper records remain paper context. Each source-local edge's extracted reading scope, where available, is preserved at `provenance.attributes.scope`.

## Retained diagnostic export

The first complete-graph attempt, job **61425938**, produced 305.6 MB. Inspection caught that native catalog paper-node `text` contains original abstracts, unlike the extracted summaries in scientific objects. This candidate is explicitly diagnostic-only and must not be published. Its script, receipt and measurements remain under `source-context-v3/`.

V3.1 projects paper nodes to exact identity, title, year/version/authors, source URL/hash, record provenance and native coverage; it omits original abstracts and verbose repeated internal review bookkeeping. Scientific object text, assumptions, conventions, regimes, limitations and every typed edge are preserved. The versioned native graph remains pinned as the full original metadata source. This correction reduced payload size by 115.5 MB without deleting graph connections or scientific object conditions.

The pack is an integration candidate, not a claim that all physics has been ingested or every extracted scientific claim certified. Publication and browser performance acceptance belong to the coordinated release process.
