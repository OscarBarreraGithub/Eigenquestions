"""Exact reviewed relation endpoint -> frozen method-unit mapping, no inference."""
import collections
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


ledger, lpin = read(ROOT / 'research/q025/evaluation/current-relation-ledger.json')
pins, upin = read(ROOT / 'research/q025/geometry/source-index-v2/inputs/units-provenance.json')
methods, by_node = {}, collections.defaultdict(list)
for path, expected in pins.items():
    rows, pin = read(ROOT / path)
    assert pin['sha256'] == expected
    for u in rows:
        if u['lens'] != 'method':
            continue
        methods[u['id']] = u
        for node in u['evidence']['sourceNodeIds']:
            by_node[node].append(u['id'])
routes = []
for r in ledger['records']:
    if not r['admittedScientificEdge']:
        continue
    assert r['status'] == 'accepted_relation' and not r['promotionWithheld']
    left, right = r['nodeIds']
    if r['direction'] == 'right_to_left':
        source, target = right, left
    elif r['direction'] == 'left_to_right':
        source, target = left, right
    else:
        # A symmetric/undirected receipt retains its canonical endpoint order;
        # inspecting the other endpoint never rewrites its scientific direction.
        source, target = left, right
    routes.append({'id': 'scientific:' + r['taskId'], 'type': r['relationCategory'],
                   'sourceObjectId': source, 'targetObjectId': target,
                   'sourceMethodUnitIds': sorted(by_node[source]), 'targetMethodUnitIds': sorted(by_node[target]),
                   'originalDirection': r['direction'], 'status': 'accepted_relation',
                   'promotionWithheld': False, 'receiptSha256': r['receiptSha256'],
                   'bothEndpointsRepresented': bool(by_node[source] and by_node[target]),
                   'mappingBasis': 'exact_source_node_id_in_frozen_method_unit_evidence',
                   'questionEquivalenceInferred': False, 'methodApplicabilityExtended': False})
unit_ids = {uid for r in routes for key in ('sourceMethodUnitIds', 'targetMethodUnitIds') for uid in r[key]}
unit_map = {uid: {'unitId': uid, 'paperId': methods[uid]['paperId'], 'browserVectorRow': methods[uid]['vectorRow'],
                  'lens': 'method', 'textSha256': methods[uid]['evidence']['textSha256'],
                  'sourceNodeIds': methods[uid]['evidence']['sourceNodeIds']} for uid in sorted(unit_ids)}
payload = {'schemaVersion': '1.0.0', 'kind': 'eigenquestions-exact-source-method-routes',
           'routes': {r['id']: r for r in routes}, 'units': unit_map,
           'provenance': {'currentRelationLedger': lpin, 'frozenUnitShards': upin},
           'coverage': {'reviewedPositiveRelations': len(routes),
                        'bothMethodEndpoints': sum(r['bothEndpointsRepresented'] for r in routes),
                        'bothMethodEndpointsByType': dict(collections.Counter(r['type'] for r in routes if r['bothEndpointsRepresented'])),
                        'questionEndpointsInferred': 0},
           'meaning': 'Lazy exact source inspection mapping only. Opening either endpoint does not infer a converse, source home, question equivalence, geometric mass or USING applicability.'}
B.mkdir(parents=True, exist_ok=True)
path = B / 'source-method-routes.json'
path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
examples = []
for task in ('production-001', 'production-026', 'production-097', 'production-020'):
    r = next(r for r in ledger['records'] if r['taskId'] == task)
    route = next(x for x in routes if x['id'] == 'scientific:' + task)
    examples.append({'sourceRelation': r, 'route': route,
                     'sourceMethods': [methods[u] for u in route['sourceMethodUnitIds']],
                     'targetMethods': [methods[u] for u in route['targetMethodUnitIds']],
                     'expected': 'exact_follow_available' if route['bothEndpointsRepresented'] else 'unmapped_no_co_paper_fallback'})
fixtures = {'schemaVersion': 'q025-exact-method-route-fixtures/1', 'mapping': read(path)[1],
            'fixtures': examples, 'noNewScientificAdmission': True}
fp = B / 'fixtures.json'
fp.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'mapping': read(path)[1], 'fixtures': read(fp)[1], 'coverage': payload['coverage']}, indent=2))
