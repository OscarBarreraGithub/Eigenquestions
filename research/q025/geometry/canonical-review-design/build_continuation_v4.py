"""One compact pending queue: old work + registry-v4 delta, no pilot reruns.

Definition/description screening only. Full paired unit context remains pinned
for targeted decisions, and selective-context cost is measured separately.
"""
import ast
import collections
import hashlib
import json
import statistics
import time
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
E = ROOT / 'research/q025/evaluation'


def compact(x):
    return json.dumps(x, ensure_ascii=False, separators=(',', ':'))


def digest(x):
    return hashlib.sha256(compact(x).encode()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def save(path, value):
    raw = (compact(value) + '\n').encode()
    path.parent.mkdir(exist_ok=True, parents=True)
    path.write_bytes(raw)
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'characters': len(raw.decode())}


registry, rpin = read(E / 'full-pass/reconciliation-v1/authored-scope-registry-v4-20261117T131639Z.json')
assert rpin['sha256'] == '8fec0de5da3901625e4fea16240d4a487878b7b6c803c29a3e3893dc89c1fe7e'
new_nominations, npin = read(ROOT / 'research/q025/assembly/outputs/scope-candidates-v4/candidates.json')
old_export, oldpin = read(B / 'triage-export-index.json')
index, ipin = read(E / 'full-pass/canonical-wave-v1/final-source-index.json')
all_records = {r['recordId']: r for r in registry['records']}
review_lookup = {r['reviewId']: r for r in registry['reviews']}
lineages = registry['selectedReviewLineages']
assert len({r['canonicalReviewKey'] for r in lineages}) == len(lineages)
assert len({r['reviewId'] for r in lineages}) == len(lineages)
for r in lineages:
    assert review_lookup[r['reviewId']]['canonicalReviewKey'] == r['canonicalReviewKey']

edges = {}
scope_refs, unit_refs, edge_refs = {}, {}, {}
finished, finished_ids, pilot_scopes = set(), set(), set()
pilot_receipts = []


def add_edge(key, workload_ids, channels):
    key = tuple(sorted(key))
    row = edges.setdefault(key, {'recordIds': list(key), 'nominationIds': set(), 'channels': set()})
    row['nominationIds'].update(workload_ids)
    row['channels'].update(channels)


for f in old_export['families']:
    side, pin = read(ROOT / f['sidecar']['path'])
    assert pin['sha256'] == f['sidecar']['sha256']
    for ref, row in side['scopeBindings'].items():
        rid = row['recordId']
        assert rid in all_records
        assert digest(all_records[rid]['definition']) == row['definitionSha256']
        assert scope_refs.setdefault(rid, ref) == ref
    for ref, row in side['unitBindings'].items():
        assert unit_refs.setdefault(row['unitId'], ref) == ref
    for ref, row in side['comparisonBindings'].items():
        key = tuple(sorted(row['recordIds']))
        add_edge(key, row['nominationIds'], row['channels'])
        assert edge_refs.setdefault(key, ref) == ref
    folder = E / 'full-pass/native-local/canonical-triage-v1/jobs' / (f['familyId'] + '-screen')
    if not (folder / 'receipt.json').exists():
        continue
    receipt, receipt_pin = read(folder / 'receipt.json')
    if receipt['status'] != 'complete':
        continue
    reply, reply_pin = read(folder / 'reply.json')
    assert receipt['normalizedReplySha256'] == reply_pin['sha256']
    assert {r['ref'] for r in reply['comparisonReviews']} == set(side['comparisonBindings'])
    for row in side['comparisonBindings'].values():
        finished.add(tuple(sorted(row['recordIds'])))
        finished_ids.update(row['nominationIds'])
    pilot_scopes.update(r['recordId'] for r in side['scopeBindings'].values())
    pilot_receipts.append({'familyId': f['familyId'], 'receipt': receipt_pin, 'reply': reply_pin,
                           'comparisonCount': len(reply['comparisonReviews'])})
assert len(finished) == 375
old_pair_keys = set(edges)
old_workload_ids = {n for row in edges.values() for n in row['nominationIds']}
prior_pilot_ids = set(index['deferredActivePilotPairIds'])
prior_pilot_pairs = set()
for row in new_nominations['pairs']:
    key = tuple(sorted(row['recordIds']))
    if row['id'] in prior_pilot_ids:
        prior_pilot_pairs.add(key)
        continue
    add_edge(key, [row['id']], row['nominationChannels'])
for row in new_nominations['unmatched']:
    for other in row['nearestLexicalReviewCandidates']:
        key = tuple(sorted((row['recordId'], other['recordId'])))
        # Preserve old weak-contrast IDs when the same anchor pair recurs.
        if key in edges and 'weak_nearest_contrast' in edges[key]['channels']:
            continue
        add_edge(key, ['unmatched-v4:' + digest(list(key))[:24]], ['weak_nearest_contrast'])
all_workload_ids = {n for row in edges.values() for n in row['nominationIds']}
finished_all_ids = {n for key in finished if key in edges for n in edges[key]['nominationIds']}
edges = {key: {'recordIds': row['recordIds'], 'nominationIds': sorted(row['nominationIds']),
                'channels': sorted(row['channels'])}
         for key, row in edges.items() if key not in finished and key not in prior_pilot_pairs}
remaining_scope_ids = {rid for key in edges for rid in key}
accounted = remaining_scope_ids | pilot_scopes | {r for key in prior_pilot_pairs for r in key}
assert accounted == set(all_records), set(all_records) - accounted
records = {rid: all_records[rid] for rid in remaining_scope_ids}
for rid in sorted(set(all_records) - set(scope_refs)):
    scope_refs[rid] = 'c' + str(len(scope_refs))

units, source_packet_pins = {}, {}
for review in registry['reviews']:
    folder = E / review['artifactDirectory']
    packet_file = review.get('challengeArtifact', {}).get('packetFile', 'packet.json')
    packet, pin = read(folder / packet_file)
    assert pin['sha256'] == review['pins']['challengePacketSha256']
    source_packet_pins[review['reviewId']] = pin
    for u in packet['units']:
        ref = packet['refRegistry'][u['descriptionRef']]
        uid = ref['unitId']
        assert hashlib.sha256(u['description'].encode()).hexdigest() == ref['textSha256']
        row = {'unitId': uid, 'paperId': u['paperId'], 'description': u['description'], 'textSha256': ref['textSha256']}
        assert uid not in units or units[uid] == row
        units[uid] = row
for uid in sorted(set(units) - set(unit_refs)):
    unit_refs[uid] = 'u' + str(len(unit_refs))
for key in sorted(set(edges) - set(edge_refs)):
    edge_refs[key] = 'n' + str(len(edge_refs))

scope_units, scope_primary, compact_scopes = {}, {}, {}
for rid, r in all_records.items():
    ids = {c['unitId'] for c in r['contributions']}
    ids.update(e['unitId'] for e in r['evidenceRefs'] if e.get('kind') == 'description' and e.get('unitId'))
    assert ids <= set(units), (rid, ids - set(units))
    scope_units[rid] = ids
    scope_primary[rid] = set()
    assessment = r.get('assessment') or {}
    compact_scopes[rid] = {
        'ref': scope_refs[rid], 'kind': r['kind'], 'scopeStatus': r['scopeStatus'],
        'definition': r['definition'], 'methods': r['methods'],
        'sourceContributions': [{**{k: c.get(k) for k in ('role', 'independentRoleAgreement', 'basis', 'sourceOrigin', 'materialScopeFlag')},
                                 'unitRef': unit_refs[c['unitId']]} for c in r['contributions']],
        'sourceRefs': [unit_refs[u] for u in sorted(ids)],
        'priorReadingAssessment': {k: v for k, v in assessment.items() if k not in ('id', 'refs')},
        'scopeDefinitionFlags': r.get('scopeDefinitionFlags', []),
        'admissionJustificationFlags': r.get('admissionJustificationFlags', []),
        'primaryRereadInThisPacket': False,
        'pairedUnitNotesProvided': False,
    }
    if r.get('admittedDestinationId'):
        compact_scopes[rid]['admittedDestinationId'] = r['admittedDestinationId']
compact_units = {uid: {'ref': unit_refs[uid], 'paperId': r['paperId'], 'description': r['description']} for uid, r in units.items()}
compact_edges = {key: {'ref': edge_refs[key], 'left': scope_refs[key[0]], 'right': scope_refs[key[1]], 'channels': row['channels']} for key, row in edges.items()}
compact_scope_cost = {rid: len(compact(r)) + 1 for rid, r in compact_scopes.items()}
compact_unit_cost = {uid: len(compact(r)) + 1 for uid, r in compact_units.items()}
compact_edge_cost = {key: len(compact(r)) + 1 for key, r in compact_edges.items()}
edge_keys = list(edges)
nomination_to_edge = {nid: key for key, row in edges.items() for nid in row['nominationIds']}
incident = collections.defaultdict(set)
for key in edges:
    for rid in key:
        incident[rid].add(key)
primary_cost = {}


def payload(ids, pairs, mode):
    assert mode == 'triage_refs'
    us = set().union(*(scope_units[rid] for rid in ids))
    return {
        'kind': 'canonical-triage-with-pinned-reference-sidecar-not-dispatch',
        'registrySha256': rpin['sha256'],
        'scopes': [compact_scopes[rid] for rid in sorted(ids)],
        'units': [compact_units[uid] for uid in sorted(us)],
        'nominations': [compact_edges[key] for key in sorted(pairs)],
        'readingMeaning': 'Full exact scope definitions and source descriptions, inherited scope-review notes and paired contribution roles. Per-unit proposer/challenger notes and primary excerpts are omitted here and remain pinned for targeted decisions. This screen cannot settle missing premise context, allocate a source, admit a connection or establish uniqueness.'}


# Reuse precisely the previously measured algorithm, without executing any of
# the frozen script's data loading or output mutation.
packing_path = B / 'measure_packings.py'
tree = ast.parse(packing_path.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ('stats', 'packing')]
assert len(functions) == 2
exec(compile(ast.Module(body=functions, type_ignores=[]), str(packing_path), 'exec'), globals())
alternatives, packings = [], {}
for limit in (100, 80):
    name = 'combined_v4_scope_screen_40_' + str(limit)
    summary, groups = packing(name, 'triage_refs', 40, limit, 280000, 'star')
    alternatives.append(summary)
    packings[name] = groups

# Measure selective note enrichment without paying for every unit's notes or
# changing the selected scientific view. Exact shared-source or flagged rows
# are the only nominations for additional context in this diagnostic.
assessments = {(a['reviewId'], a['unitId']): a for a in registry['unitAssessments']}
selected = packings['combined_v4_scope_screen_40_100']
selective_sizes, selective_context_counts = [], []
for group in selected:
    wanted = set()
    for left, right in group['comparisonKeys']:
        shared = {c['unitId'] for c in all_records[left]['contributions']} & {c['unitId'] for c in all_records[right]['contributions']}
        for rid in (left, right):
            wanted.update((all_records[rid]['reviewId'], uid) for uid in shared)
    for rid in group['recordIds']:
        wanted.update((all_records[rid]['reviewId'], c['unitId']) for c in all_records[rid]['contributions'] if c.get('materialScopeFlag'))
    extra = [{'reviewId': rid, 'unitRef': unit_refs[uid],
              'proposal': {k: assessments[(rid, uid)]['proposalAttribution'].get(k) for k in ('note', 'reason', 'd', 'home')},
              'challenge': {k: assessments[(rid, uid)]['challengeAttribution'].get(k) for k in ('note', 'reason', 'd', 'home')}}
             for rid, uid in sorted(wanted) if (rid, uid) in assessments]
    selective_sizes.append(group['characters'] + len(compact(extra)) + 24)
    selective_context_counts.append(len(extra))

owners = {}
for i, group in enumerate(selected):
    degree = collections.Counter(rid for key in group['comparisonKeys'] for rid in key)
    for rid in group['recordIds']:
        if rid not in owners or degree[rid] > owners[rid][0]:
            owners[rid] = (degree[rid], i)
dest = B / 'continuation-v4'
families = []
for i, group in enumerate(selected):
    family_id = 'canonical-continuation-v4-' + str(i + 1).zfill(4)
    ids = group['recordIds']
    pairs = [tuple(key) for key in group['comparisonKeys']]
    us = set().union(*(scope_units[rid] for rid in ids))
    view = payload(ids, pairs, 'triage_refs')
    view['familyId'] = family_id
    view['stage'] = 'nomination_triage_not_scientific_admission'
    assert len(compact(view)) <= 280000
    vp = save(dest / (family_id + '.local.json'), view)
    side = {
        'schemaVersion': 'q025-canonical-triage-reference-sidecar/1', 'familyId': family_id,
        'registry': rpin, 'scientificView': vp,
        'scopeBindings': {scope_refs[rid]: {'recordId': rid, 'candidateId': all_records[rid]['candidateId'],
                          'admittedDestinationId': all_records[rid].get('admittedDestinationId'),
                          'definitionSha256': digest(all_records[rid]['definition']),
                          'fullRegistryRecordSha256': digest(all_records[rid]),
                          'scopeContentSha256': all_records[rid].get('scopeContentSha256'),
                          'reviewId': all_records[rid]['reviewId'], 'pins': all_records[rid]['pins'],
                          'sourcePacket': source_packet_pins[all_records[rid]['reviewId']],
                          'priorAssessmentWithOriginalRefs': all_records[rid].get('assessment'),
                          'originalEvidenceRefs': all_records[rid]['evidenceRefs'],
                          'originalContributionEvidence': [{'unitId': c['unitId'], 'role': c['role'], 'evidenceRefs': c['evidenceRefs']} for c in all_records[rid]['contributions']]}
                          for rid in ids},
        'unitBindings': {unit_refs[uid]: {'unitId': uid, 'paperId': units[uid]['paperId'], 'textSha256': units[uid]['textSha256']} for uid in sorted(us)},
        'comparisonBindings': {edge_refs[key]: edges[key] for key in pairs},
        'primaryScopeAccountingRefs': [scope_refs[rid] for rid in ids if owners[rid][1] == i],
        'pairedUnitContextLocator': {'registry': rpin, 'array': 'unitAssessments', 'match': ['reviewId', 'unitId'],
                                    'meaning': 'Exact paired attributions, notes, homeAgreement and proposal pins are inherited context for decisions; they are not included in this screening view. Calibration legacy context remains in its pinned source packet.'},
        'primaryReadingStatus': 'No primary text supplied. No fresh primary reading claim.',
        'noNewScientificJudgment': True}
    sp = save(dest / (family_id + '-sidecar.local.json'), side)
    # Verify exact science after serialization, not just aggregate sizes.
    reread, _ = read(ROOT / vp['path'])
    for row in reread['scopes']:
        rid = side['scopeBindings'][row['ref']]['recordId']
        assert row['definition'] == all_records[rid]['definition']
        assert row['methods'] == all_records[rid]['methods']
    for row in reread['units']:
        assert hashlib.sha256(row['description'].encode()).hexdigest() == side['unitBindings'][row['ref']]['textSha256']
    families.append({'familyId': family_id, 'view': vp, 'sidecar': sp, 'scopeCount': len(ids),
                     'comparisonCount': len(pairs), 'sourceDescriptions': len(us), 'primaryWindowsProvided': 0,
                     'recordIds': ids, 'nominationIds': group['nominationIds'],
                     'scopeAccountingAnchors': [rid for rid in ids if owners[rid][1] == i]})

coverage = {
    'registryScopes': len(all_records), 'newRegistryCandidateIds': registry['counts']['newCandidateScopesSincePreviousCut'],
    'selectedUniqueReviewLineages': len(lineages), 'duplicateCanonicalReviewKeys': 0,
    'completedScreenFamilies': len(pilot_receipts), 'completedComparisonsExcluded': len(finished),
    'completedOriginalWorkloadIds': len(finished_ids), 'allWorkloadIdsNowCoveredByCompletedPairs': len(finished_all_ids),
    'priorRichPilotPairIdsStillDeferred': sorted(prior_pilot_ids),
    'priorRichPilotPairsPresentInCurrentNominationSet': len(prior_pilot_pairs),
    'pendingUniqueComparisons': len(edges), 'pendingOriginalWorkloadIds': len(nomination_to_edge),
    'oldPendingComparisonsRetained': len((old_pair_keys - finished) & set(edges)),
    'newComparisonKeysBeyondOldQueuedUniverse': len(set(edges) - old_pair_keys),
    'pendingScopeAccountingAnchors': len(owners),
    'scopesAccountedIncludingCompletedOrPriorPilot': len(accounted),
    'currentUnmatchedScopes': len(new_nominations['unmatched']),
    'acceptedScientificDecisions': 0, 'primaryReadingClaims': 0,
    'omittedScopeDefinitions': 0, 'truncatedSourceDescriptions': 0,
    'pairedUnitNotesOmittedFromViews': True,
}
report = {
    'schemaVersion': 'q025-combined-canonical-continuation/1',
    'status': 'prepared_views_not_native_launch_authorization',
    'registry': rpin, 'previousExport': oldpin, 'currentNominations': npin,
    'completedPilotReceipts': pilot_receipts, 'families': families, 'coverage': coverage,
    'limits': {'maxScopes': 40, 'maxComparisons': 100, 'maxInputCharacters': 280000,
               'observedMaxInputCharacters': max(f['view']['characters'] for f in families)},
    'packingAlternatives': alternatives,
    'selectiveSharedSourceOrFlaggedContextMeasurement': {
        'notSelectedForExport': True, 'characters': stats(selective_sizes),
        'pairedUnitContexts': stats(selective_context_counts),
        'packetsExceeding280kAfterNaiveAddition': sum(n > 280000 for n in selective_sizes),
        'meaning': 'Adds exact shared-source or flagged per-unit notes once per review/unit within a packet; cost only, no rerun or source-reading claim.'},
    'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'packingAlgorithmSha256': hashlib.sha256(packing_path.read_bytes()).hexdigest(),
    'noSealedHoldoutOpened': True,
    'limitations': [
        'This screen prioritizes scopes and possible relations, not identity admission, source allocation or physical claims.',
        'Complete source-specific paired notes are deliberately reserved for targeted decision packets. Missing premise context must be named rather than inferred from the supplied role alone.',
        'A distinct question can still have a useful method, comparison, application or broader-target route. No unreviewed negative certifies uniqueness.',
        'New registry records and old pending nominations are combined once; completed pair screens and the prior rich pilot are not silently rerun.',
        'Review lineages and all 8 already admitted calibration IDs are preserved. Numerical review regions are not public branches.'
    ]}
report_pin = save(B / 'continuation-v4-index.json', report)
print(json.dumps({'index': report_pin, 'families': len(families), 'coverage': coverage,
                  'viewBytes': sum(f['view']['bytes'] for f in families),
                  'selective': report['selectiveSharedSourceOrFlaggedContextMeasurement']}, indent=2))
