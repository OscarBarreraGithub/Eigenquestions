"""Exact attachment override for immutable paper-scoped source-context shards."""
import re

POLICY = 'source_anchors_and_record_context_v1'

def resolve_override(unit_id, descriptor, payload):
    override = descriptor['attachmentOverride']
    if override.get('policy') != POLICY:
        raise ValueError('Unsupported attachment override policy')
    paper = descriptor['shardId']
    objects = {o['id']: o for o in payload['sourceObjects']}
    relations = {r['id']: r for r in payload.get('sourceRelations', [])}
    requested = set(override.get('anchorObjectIds', []))
    anchors = requested & objects.keys()
    missing = requested - objects.keys()
    # Exact identity is sufficient for attachment; a record match alone is not.
    direct_rel = {rid for rid, r in relations.items()
                  if r['source'] in anchors or r['target'] in anchors}
    direct_obj = set(anchors)
    for rid in direct_rel:
        direct_obj.update((relations[rid]['source'], relations[rid]['target']))
    record_ids = set(override.get('sourceRecordIds', []))
    record_ids.update(objects[n].get('provenance', {}).get('record', {}).get('record_id')
                      for n in anchors)
    record_ids.discard(None)
    windows = set()
    for o in objects.values():
        r = o.get('provenance', {}).get('record', {})
        window = r.get('source_unit_id', '')
        if o.get('paperId') == paper and r.get('record_id') in record_ids and re.fullmatch(r'w\d+', window or ''):
            windows.add((r['record_id'], window))
    window_obj = {o['id'] for o in objects.values()
                  if o.get('paperId') == paper and
                  (o.get('provenance', {}).get('record', {}).get('record_id'),
                   o.get('provenance', {}).get('record', {}).get('source_unit_id')) in windows}
    window_rel = {rid for rid, r in relations.items() if rid not in direct_rel and
                  r['source'] in window_obj and r['target'] in window_obj}
    # The frozen paper shard also includes the far endpoints of reviewed links.
    # Their presence is context, never applicability to every method in the paper.
    paper_obj = {o['id'] for o in objects.values() if o.get('paperId') == paper}
    paper_rel = {rid for rid, r in relations.items() if rid not in direct_rel | window_rel and
                 (r['source'] in paper_obj or r['target'] in paper_obj)}
    for rid in paper_rel:
        paper_obj.update((relations[rid]['source'], relations[rid]['target']))
    for assessment in payload.get('sourceAssessments', []):
        ids = set(assessment.get('nodeIds', []))
        if ids & paper_obj:
            paper_obj.update(ids)
    assert direct_obj <= objects.keys() and paper_obj <= objects.keys()
    attachments = []
    if direct_obj:
        attachments.append({'unitId': unit_id, 'scope': 'direct_record_relation',
                            'objectIds': sorted(direct_obj), 'relationIds': sorted(direct_rel),
                            'anchorObjectIds': sorted(anchors),
                            'statement': 'Exact source anchors and exported incident relations. Each relation retains its own direction, semantic status and applicability; no question equivalence is inferred.'})
    if window_obj - direct_obj or window_rel:
        attachments.append({'unitId': unit_id, 'scope': 'shared_extraction_window_context',
                            'objectIds': sorted(window_obj - direct_obj), 'relationIds': sorted(window_rel),
                            'recordWindows': [{'recordId': r, 'sourceUnitId': w} for r, w in sorted(windows)],
                            'statement': 'Same exact extraction record and numbered window only. Co-occurrence does not establish this method\u2019s premises.'})
    other = paper_obj - direct_obj - window_obj
    if other or paper_rel:
        attachments.append({'unitId': unit_id, 'scope': 'same_paper_context',
                            'objectIds': sorted(other), 'relationIds': sorted(paper_rel),
                            'statement': 'Additional paper context and named endpoints of source relations. Whole-paper first-pass records are not narrow extraction windows and do not establish applicability.'})
    return {'sourceAttachments': attachments, 'missingAnchorIds': sorted(missing),
            'attachmentOverridePolicy': POLICY,
            'coverage': {'exactAnchorCount': len(anchors), 'requestedAnchorCount': len(requested),
                         'directExportedRelationCount': len(direct_rel),
                         'directReviewedRelationCount': sum(relations[r]['semanticStatus'] == 'reviewed_scoped' for r in direct_rel),
                         'windowRecordCount': len(windows),
                         'description': 'Existing exported relations only. Zero exported incident relations is not evidence that the source has no method assumptions or relations. Shared-window and whole-paper context remain separately typed.'}}
