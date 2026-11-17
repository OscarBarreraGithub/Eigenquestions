"""Pin the completed pre-holdout package without admitting or changing science."""
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PACKAGE = ROOT / 'research/q025/assembly/outputs/final-preholdout-geometry-v1'
GEOMETRY = ROOT / 'research/q025/geometry/final-overview-v1'


def read(p):
    return json.loads(p.read_text())


def pin(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}


def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    manifest = read(PACKAGE / 'manifest.json')
    catalog = read(PACKAGE / 'catalog.json')
    handoff = read(PACKAGE / 'handoff.json')
    report = read(PACKAGE / 'assembly-report.json')
    geometry = read(PACKAGE / 'accepted-geometry-input.json')
    asset_plan = read(PACKAGE / 'asset-plan.json')
    delivery = read(PACKAGE / 'delivery-assets.json')
    external = {r['path']: r for r in asset_plan['assets']}
    verified = set()
    for r in delivery['files'] + list(manifest['files'].values()):
        path = PACKAGE / r['path']
        if not path.exists():
            path = Path(external[r['path']]['sourcePath'])
        actual = pin(path)
        assert actual['sha256'] == r['sha256'], r['path']
        assert 'bytes' not in r or r['bytes'] == actual['bytes'], r['path']
        assert actual['bytes'] < 25 * 1024 * 1024, r['path']
        verified.add(r['path'])
    assert pin(PACKAGE / 'manifest.json')['sha256'] == handoff['manifestSha256']
    assert pin(PACKAGE / 'catalog.json')['sha256'] == handoff['catalogSha256']
    assert pin(PACKAGE / 'accepted-geometry-input.json')['sha256'] == handoff['provenance']['geometryInputSha256']
    assert manifest['scope']['allocatedQuestionCount'] == 8399
    assert manifest['scope']['unresolvedQuestionCount'] == 31
    assert manifest['scope']['reservedQuestionCount'] == 43
    assert report['publicEntryReachability']['unreachableAllocatedHomes'] == 0
    assert catalog['overview']['kind'] == 'navigation_schematic'

    templates = catalog.get('indexTemplates', {})
    def expand(row, kind):
        return {**templates.get(kind, {}).get(row.get('indexTemplate'), {}), **row}
    destinations = {d['id']: expand(d, 'destinations') for d in catalog['destinations']}
    relations = [expand(r, 'relations') for r in catalog['relations']]
    by_relation = {r['id']: r for r in relations}
    for e in catalog['overview']['edges']:
        r = by_relation[e['relationId']]
        assert all(e[k] == r[k] for k in ['source', 'target', 'type'])
    root = catalog['overview']['entryDestinationId']
    assert destinations[root]['metadataOnly']
    assert next(n for n in catalog['overview']['nodes'] if n['destinationId'] == root)['mass'] == 0
    entries = [e['target'] for e in catalog['overview']['edges']]
    assert len(entries) == len(set(entries)) == 15

    # These acceptance paths use only exact delivered navigation records. Incoming
    # traversal is a UI route, never an assertion of the scientific converse.
    adj = defaultdict(list)
    for r in relations:
        if r['type'] == 'source_question' or r['source'] not in destinations or r['target'] not in destinations:
            continue
        adj[r['source']].append((r['target'], r, 'outgoing'))
        adj[r['target']].append((r['source'], r, 'incoming'))
    def path(start, target):
        queue = deque([start]); seen = {start: None}
        while queue and target not in seen:
            u = queue.popleft()
            for v, relation, direction in sorted(adj[u], key=lambda t: (t[1]['type'] == 'related_question', t[0], t[1]['id'])):
                if v not in seen:
                    seen[v] = (u, relation, direction); queue.append(v)
        assert target in seen, target
        result = []
        while target != start:
            previous, relation, direction = seen[target]
            result.append({'from': previous, 'to': target, 'title': destinations[target]['title'], 'relationId': relation['id'], 'type': relation['type'], 'traversal': direction, 'navigationBasis': relation.get('provenance', {}).get('navigationBasis', 'reviewed_scientific_navigation')})
            target = previous
        return result[::-1]

    units = {u['unitId']: u for u in geometry['units']}
    compound = [a for a in geometry['allocations'] if a.get('coverageMode') == 'explicit_compound_union']
    compound_case = [a for a in compound if units[a['unitId']]['paperId'] == '2604.19817']
    assert len(compound_case) == 2 and sum(a['weight'] for a in compound_case) == 1
    assert all(a['wholeQuestionCoveredByEachHome'] is False for a in compound_case)
    unresolved = catalog['sourceAccounting']['unresolved'][0]
    audit = read(HERE / 'method-access-audit.json')
    method_case = next(r for r in audit['actualReaderChecks'] if r['unresolvedSourcePaper'])
    cases = {
        'classification': {'entry': manifest['entryDestinationId'], 'nodes': len(catalog['orientation']['nodes']), 'portals': catalog['orientation']['portals'], 'sharedCoordinateMetric': False},
        'overview': {'entry': root, 'kind': catalog['overview']['kind'], 'nodes': len(catalog['overview']['nodes']), 'recordedEdges': len(catalog['overview']['edges']), 'choices': [{'destinationId': d, 'title': destinations[d]['title']} for d in entries], 'coordinatesAreMetric': False},
        'darkSectorToProduction': path('q025-candidate-region:7961ee3cebdb154299e78b58', 'q-kk-graviton-thermal-production'),
        'kkConditionalRoutes': [by_relation['navigation:kk:' + str(i)] for i in [0, 2, 3, 4]],
        'blackHoleEntry': {'destinationId': 'q025-candidate-region:e52fcb6489b7f044e70ddb7d', 'availableUniqueDestinations': len({v for v, r, direction in adj['q025-candidate-region:e52fcb6489b7f044e70ddb7d']})},
        'unresolved': {'unitId': unresolved['unitId'], 'destinationId': unresolved['unitId'].replace('unit:', 'source-question:'), 'sourceHomeStatus': 'unresolved', 'reason': unresolved['reason'], 'semanticHMass': 0},
        'compound': {'paperId': '2604.19817', 'rows': compound_case, 'meaning': 'Each destination covers one stated part; the complete map and normalized organizational weights remain visible.'},
        'aliases': catalog['destinationAliases'],
        'methodOnUnresolvedPaper': method_case,
        'sourceMethodRoutes': manifest['files']['sourceMethodRoutes'],
    }
    dump(HERE / 'acceptance-cases.json', cases)
    pins = ['manifest.json', 'catalog.json', 'accepted-geometry-input.json', 'assembly-report.json', 'partition-validation.json', 'handoff.json', 'asset-plan.json', 'delivery-assets.json']
    result = {
        'schemaVersion': 'q025-preholdout-freeze/1',
        'status': 'frozen_for_isolated_acceptance_and_blind_evaluation',
        'packageDirectory': str(PACKAGE),
        'publicationStatus': handoff['publicationStatus'],
        'notApprovedForSiteRelease': True,
        'files': [pin(PACKAGE / p) for p in pins],
        'packet': pin(HERE / 'packet/aggregate.local.json'),
        'accountingReceipt': pin(HERE / 'packet/source-accounting-admission.json'),
        'admissionReceipt': pin(HERE / 'packet/aggregate-admission.json'),
        'acceptanceCases': pin(HERE / 'acceptance-cases.json'),
        'scope': manifest['scope'],
        'counts': handoff['counts'],
        'compoundSourceCount': len({a['unitId'] for a in compound}),
        'publicEntryReachability': report['publicEntryReachability'],
        'identity': report['canonicalProjection'],
        'sourceMass': report['sourceMass'],
        'methodAccess': {k: v for k, v in audit.items() if k not in ['bucketPins', 'actualReaderChecks']},
        'methodActualReaderChecks': len(audit['actualReaderChecks']),
        'methodAudit': pin(HERE / 'method-access-audit.json'),
        'interfacePins': [pin(ROOT / p) for p in ['lib/geometry/prepared-atlas.mjs', 'lib/geometry/prepared-identity.mjs', 'lib/protocol/display-editorial.mjs']],
        'transport': {'verifiedAssetPaths': len(verified), 'externalAssets': len(external), **handoff['partition']['fileCountGate'], 'postTest43FacetUpperBound': handoff['partition']['fileCountGate']['projectedFileCount'] + 43, 'remoteSourcePack': '/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/pack'},
        'geometry': {'membershipSha256': handoff['provenance']['geometryInputSha256'], 'delivered': pin(GEOMETRY / 'schematic-overview.json'), 'numericResults': pin(GEOMETRY / 'results/manifest.json'), 'failedDisplayCorrection': pin(GEOMETRY / 'corrected-display/manifest.json'), 'fullHFCRetained': True, 'noFurtherFits': True},
        'postTestAmendment': 'After blind routing is frozen and root adjudicates the 43 held-out sources, add dated explicit home decisions or unresolved source accounting, include their exact source facets, and regenerate the same assembler/package with a new version. Preserve this manifest and blind evidence. Any changed scope/route is a separately recorded failed-test amendment, not independent success. No new model campaign is implied.',
    }
    dump(HERE / 'freeze-handoff.json', result)
    print(json.dumps({'freeze': pin(HERE / 'freeze-handoff.json'), 'cases': pin(HERE / 'acceptance-cases.json'), 'verifiedAssets': len(verified), 'projectedFiles': result['transport']['projectedFileCount']}, indent=2))


if __name__ == '__main__':
    main()
