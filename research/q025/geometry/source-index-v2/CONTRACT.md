# Additive question/method source-context lookup

Schema version remains `1.0.0`. The root index carries `policyVersion: q025-qm-context-index-v2` and `unitIndex: {kind: unit-hash-prefix, prefixLength: 2, shards: {ab: {path, sha256, bytes}}}`. The prefix is the first two hexadecimal characters after `unit:` in the exact canonical unit ID. Each checksummed plain JSON bucket has `units` and `shards` dictionaries. Paths are relative to the package root, not the bucket URL's directory. The existing flat `index.units` format remains valid.

A unit descriptor is `{shardId: paperId, lens: physical_question|method, attachmentOverride?: {...}}`. Resolve the compressed payload descriptor through the bucket's `shards[shardId]`; it has the existing `path`, compressed-byte `sha256`, `encoding: gzip`, and `uncompressedBytes` fields. Questions retain their stored source attachments. Methods use:

```json
{
  "policy": "source_anchors_and_record_context_v1",
  "anchorObjectIds": ["exact source node ID"],
  "sourceRecordIds": ["exact extraction record ID"]
}
```

`context_override.py` is the reference resolver and `fixtures.json` contains expected JSON outputs for reduced real-data examples. It uses only these existing provenance fields: `sourceObjects[].id`, `.paperId`, `.provenance.record.record_id`, `.provenance.record.source_unit_id`; exact `sourceRelations[].source/target`; and `sourceAssessments[].nodeIds`. No text similarity or suffix matching is used.

1. `direct_record_relation` contains exact present anchors and endpoints of exported edges incident to them. Preserve each edge's type, semantic status, direction, conditions and evidence. A mere record match is never direct applicability.
2. `shared_extraction_window_context` requires the same paper, exact record ID and a numbered source unit `wN`. Whole-paper first-pass values are explicitly excluded. Record IDs supplied by the browser unit are fallback context metadata even if an anchor is missing; they still cannot establish direct applicability.
3. `same_paper_context` holds the remaining paper objects plus explicitly named far endpoints of reviewed relations and assessments. It is contextual discovery, not a transfer of premises. Nonpositive assessments remain assessments.
4. `missingAnchorIds` lists each requested node absent from the payload. Coverage names the override policy and distinguishes requested/present anchors, exported local/reviewed relations and window records. Zero exported edges is not scientific absence.

The buckets avoid loading a full 26,410-entry map for one context request. The paper gzip payload remains bounded below the reader's 16 MiB decompression limit. The index-only export deliberately preserves old payload bytes and records any missing method-edge coverage; it is an audit candidate, not a claim of a complete source graph. A fuller versioned payload may replace descriptors after the census.
