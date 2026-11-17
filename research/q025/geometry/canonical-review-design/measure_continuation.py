"""Measure unlaunched continuation only; never overwrite frozen pilot inputs."""
import collections
import copy
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
E = ROOT / 'research/q025/evaluation'


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)),
                            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


# Load frozen data preparation and packing functions, stopping before every
# experiment/export write. The original script and frozen views stay unchanged.
old_script = B / 'measure_packings.py'
source = old_script.read_text()
assert source.count('results=[];packets={}') == 1
ns = {'__file__': str(old_script)}
exec(compile(source.split('results=[];packets={}')[0], str(old_script), 'exec'), ns)
export, export_pin = read(B / 'triage-export-index.json')
v4, v4_pin = read(E / 'full-pass/reconciliation-v1/authored-scope-registry-v4-20261117T131639Z.json')
assert v4_pin['sha256'] == '8fec0de5da3901625e4fea16240d4a487878b7b6c803c29a3e3893dc89c1fe7e'
finished = set()
finished_nomination_ids = set()
pilot_receipts = []
pilot_scopes = set()
for family in export['families']:
    folder = E / 'full-pass/native-local/canonical-triage-v1/jobs' / (family['familyId'] + '-screen')
    if not (folder / 'receipt.json').exists():
        continue
    receipt, receipt_pin = read(folder / 'receipt.json')
    if receipt['status'] != 'complete':
        continue
    reply, reply_pin = read(folder / 'reply.json')
    assert receipt['normalizedReplySha256'] == reply_pin['sha256']
    side, side_pin = read(ROOT / family['sidecar']['path'])
    assert side_pin['sha256'] == family['sidecar']['sha256']
    assert {r['ref'] for r in reply['comparisonReviews']} == set(side['comparisonBindings'])
    for row in side['comparisonBindings'].values():
        finished.add(tuple(sorted(row['recordIds'])))
        finished_nomination_ids.update(row['nominationIds'])
    pilot_scopes.update(s['recordId'] for s in side['scopeBindings'].values())
    pilot_receipts.append({'familyId': family['familyId'], 'receipt': receipt_pin, 'reply': reply_pin,
                           'comparisons': len(reply['comparisonReviews']),
                           'scopeReviews': len(reply['scopeReviews'])})

all_edges = ns['edges']
remaining = {key: row for key, row in all_edges.items() if key not in finished}
remaining_scope_ids = {rid for key in remaining for rid in key}
assert pilot_scopes | remaining_scope_ids == set(ns['records'])
ns['edges'] = remaining
ns['edge_keys'] = list(remaining)
ns['records'] = {rid: row for rid, row in ns['records'].items() if rid in remaining_scope_ids}
ns['nomination_to_edge'] = {nid: edge for nid, edge in ns['nomination_to_edge'].items() if edge in remaining}
ns['incident'] = collections.defaultdict(set)
for key in remaining:
    for rid in key:
        ns['incident'][rid].add(key)

notes_by_scope = collections.defaultdict(list)
assessments = {(a['reviewId'], a['unitId']): a for a in v4['unitAssessments']}
v4_records = {r['recordId']: r for r in v4['records']}
missing_notes = []
for rid, record in ns['records'].items():
    assert v4_records[rid]['definition'] == record['definition']
    for uid in sorted(ns['scope_units'][rid]):
        a = assessments.get((record['reviewId'], uid))
        if not a:
            missing_notes.append({'recordId': rid, 'unitId': uid,
                                  'reason': 'No same-review paired unit assessment in registry v4; do not invent notes.'})
            continue
        p, c = a['proposalAttribution'], a['challengeAttribution']
        notes_by_scope[rid].append({
            'unitRef': ns['unit_refs'][uid],
            'proposal': {k: p[k] for k in ('note', 'reason', 'd', 'home')},
            'challenge': {k: c[k] for k in ('note', 'reason', 'd', 'home')},
            'sameExplicitScientificHome': a['homeAgreement']['sameExplicitScientificCard'],
            'contextMeaning': 'Original reviewer notes and local home refs in this scope review; not new placement admission.'})

base_scopes = copy.deepcopy(ns['compact_scopes'])
results, packs = [], {}
for notes, max_pairs in [(False, 120), (True, 120), (True, 100), (True, 80)]:
    ns['compact_scopes'] = copy.deepcopy(base_scopes)
    if notes:
        for rid in remaining_scope_ids:
            ns['compact_scopes'][rid]['pairedSourceAttributions'] = notes_by_scope[rid]
    ns['compact_scope_cost'] = {rid: len(ns['compact'](row)) + 1 for rid, row in ns['compact_scopes'].items()}
    name = 'continuation_40_' + str(max_pairs) + ('_paired_notes' if notes else '_scope_notes_only')
    summary, batches = ns['packing'](name, 'triage_refs', 40, max_pairs, 280000, 'star')
    summary['fullPairedUnitNotesIncluded'] = notes
    summary['completedPilotComparisonsExcluded'] = len(finished)
    summary['scopeAccountingIncludingCompletedPilot'] = len(pilot_scopes | remaining_scope_ids)
    results.append(summary)
    packs[name] = batches

# Lossless deduplication: a unit's paired attribution in one review is shared by
# every scope contributed to in that review. Do not pay its full note cost once
# per scope. The packing algorithm treats these as additional immutable atoms.
original_scope_units = {rid: set(ids) for rid, ids in ns['scope_units'].items()}
source_ids = set(ns['units'])
review_refs = {rid: 'v' + str(i) for i, rid in enumerate(sorted({r['reviewId'] for r in ns['records'].values()}))}
context_keys = sorted({(record['reviewId'], uid) for rid, record in ns['records'].items()
                       for uid in original_scope_units[rid] if (record['reviewId'], uid) in assessments})
context_refs = {key: 'a' + str(i) for i, key in enumerate(context_keys)}
context_atoms = {}
scope_context_atoms = collections.defaultdict(set)
for key in context_keys:
    a = assessments[key]
    atom = 'paired-context:' + key[0] + ':' + key[1]
    context_atoms[atom] = {'ref': context_refs[key], 'reviewRef': review_refs[key[0]],
                           'unitRef': ns['unit_refs'][key[1]],
                           'proposal': {k: a['proposalAttribution'][k] for k in ('note', 'reason', 'd', 'home')},
                           'challenge': {k: a['challengeAttribution'][k] for k in ('note', 'reason', 'd', 'home')},
                           'sameExplicitScientificHome': a['homeAgreement']['sameExplicitScientificCard']}
for rid, record in ns['records'].items():
    scope_context_atoms[rid] = {'paired-context:' + record['reviewId'] + ':' + uid
                                for uid in original_scope_units[rid] if (record['reviewId'], uid) in context_refs}
ns['scope_units'] = {rid: ids | scope_context_atoms[rid] for rid, ids in original_scope_units.items()}
for atom, row in context_atoms.items():
    ns['compact_units'][atom] = row
    ns['compact_unit_cost'][atom] = len(ns['compact'](row)) + 1
    ns['units'][atom] = {'description': ''}  # Never counted as a source description.


def deduplicated_payload(ids, pairs, mode):
    assert mode == 'triage_refs'
    real_units = set().union(*(original_scope_units[rid] for rid in ids))
    atoms = set().union(*(scope_context_atoms[rid] for rid in ids))
    return {
        'kind': 'canonical-triage-with-paired-context-not-dispatch',
        'registrySha256': ns['rpin']['sha256'], 'pairedContextRegistrySha256': v4_pin['sha256'],
        'scopes': [ns['compact_scopes'][rid] for rid in sorted(ids)],
        'units': [ns['compact_units'][uid] for uid in sorted(real_units)],
        'pairedUnitContext': [context_atoms[atom] for atom in sorted(atoms)],
        'nominations': [ns['compact_edges'][key] for key in sorted(pairs)],
        'readingMeaning': 'Exact full definitions, source descriptions and both original unit-attribution notes. Paired context is deduplicated by exact review and unit, never merged across reviews. No new primary reading, placement or scientific admission.'}


ns['payload'] = deduplicated_payload
ns['compact_scopes'] = copy.deepcopy(base_scopes)
for rid in remaining_scope_ids:
    ns['compact_scopes'][rid]['pairedSourceContextRefs'] = [context_atoms[a]['ref'] for a in sorted(scope_context_atoms[rid])]
ns['compact_scope_cost'] = {rid: len(ns['compact'](row)) + 1 for rid, row in ns['compact_scopes'].items()}
for max_pairs in (100, 80):
    name = 'continuation_40_' + str(max_pairs) + '_deduplicated_paired_notes'
    summary, batches = ns['packing'](name, 'triage_refs', 40, max_pairs, 280000, 'star')
    for batch in batches:
        batch['sourceDescriptions'] = len(set().union(*(original_scope_units[rid] for rid in batch['recordIds'])))
        batch['pairedUnitContexts'] = len(set().union(*(scope_context_atoms[rid] for rid in batch['recordIds'])))
    summary['sourceDescriptionExposures'] = sum(b['sourceDescriptions'] for b in batches)
    summary['pairedUnitContextExposures'] = sum(b['pairedUnitContexts'] for b in batches)
    summary['fullPairedUnitNotesIncluded'] = True
    summary['losslessWithinReviewUnitDeduplication'] = True
    summary['completedPilotComparisonsExcluded'] = len(finished)
    summary['scopeAccountingIncludingCompletedPilot'] = len(pilot_scopes | remaining_scope_ids)
    results.append(summary)
    packs[name] = batches

payload_path = B / 'continuation-packings.local.json'
payload_path.write_text(json.dumps({'registrySha256': ns['rpin']['sha256'],
                                    'pairedNoteRegistrySha256': v4_pin['sha256'],
                                    'packs': packs}, separators=(',', ':')) + '\n')
report = {
    'schemaVersion': 'q025-canonical-continuation-packing/1',
    'status': 'measurement_only_unlaunched_no_scientific_admission',
    'inputs': {'frozenExport': export_pin, 'pairedNoteRegistry': v4_pin,
               'frozenPackingScript': {'path': str(old_script.relative_to(ROOT)),
                                       'sha256': hashlib.sha256(old_script.read_bytes()).hexdigest()},
               'completedPilotReceipts': pilot_receipts, 'packings': read(payload_path)[1]},
    'counts': {'originalScopeUniverse': len(pilot_scopes | remaining_scope_ids),
               'completedPilotFamilies': len(pilot_receipts),
               'completedPilotComparisonsExcluded': len(finished),
               'completedOriginalWorkloadIdsExcluded': len(finished_nomination_ids),
               'remainingUniqueComparisons': len(remaining),
               'remainingOriginalWorkloadIds': len(ns['nomination_to_edge']),
               'remainingScopeExposureUniverse': len(remaining_scope_ids),
               'pairedAssessmentRowsAttachedToScopes': sum(map(len, notes_by_scope.values())),
               'missingPairedAssessmentRows': len(missing_notes)},
    'alternatives': results, 'missingPairedAssessments': missing_notes,
    'limitations': [
        'The completed 375 comparison screens are accounted for once and excluded, not converted into accepted negative or positive scientific decisions.',
        'This measures continuation of the frozen 1,112-scope universe; new registry-v4 scopes require separately accounted delta nominations.',
        'Complete definitions and source descriptions remain exact. Paired-note variants add full original per-unit notes, dispositions, reasons and home refs; no primary text or fresh primary-reading claim is added.',
        'A screen escalation is a nomination, not a mandate for another primary-rich call. Existing paired evidence can support explicit coordinator organization decisions; only material ambiguity or new physical meaning needs targeted additional reading.',
        'No active inputs, frozen exports, source campaigns or sealed holdout files were modified.'
    ],
    'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
out = B / 'continuation-measurements.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'report': read(out)[1], 'counts': report['counts']}, indent=2))
