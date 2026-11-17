"""Verify and pin the dated final package for integration acceptance."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PACKAGE = ROOT / 'research/q025/assembly/outputs/final-release-v1'
PREVIOUS = ROOT / 'research/q025/assembly/outputs/final-preholdout-geometry-v1'
GEOMETRY = ROOT / 'research/q025/geometry/final-release-v1'


def read(p):
    return json.loads(p.read_text())


def pin(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}


def dump(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    manifest = read(PACKAGE / 'manifest.json'); catalog = read(PACKAGE / 'catalog.json')
    handoff = read(PACKAGE / 'handoff.json'); report = read(PACKAGE / 'assembly-report.json')
    previous_catalog = read(PREVIOUS / 'catalog.json')
    authority = read(ROOT / 'research/q025/evaluation/final-holdout/root-43-source-adjudication.json')
    previous_packet = read(ROOT / 'research/q025/assembly/final-preholdout-v1/packet/aggregate.local.json')
    packet = read(HERE / 'packet/aggregate.local.json')
    for key in ['destinations', 'relations', 'sourceContributions', 'aliases', 'identityResolution', 'publicEntryFrontier']:
        assert packet[key] == previous_packet[key], 'Scientific or canonical input changed: ' + key
    assert packet['placements'][:len(previous_packet['placements'])] == previous_packet['placements']
    assert packet['coverage']['unresolved'][:31] == previous_packet['coverage']['unresolved']
    assert len(packet['placements']) == len(previous_packet['placements']) + 37
    assert manifest['scope']['allocatedQuestionCount'] == 8436
    assert manifest['scope']['unresolvedQuestionCount'] == 37 and manifest['scope']['reservedQuestionCount'] == 0
    assert report['sourceAccountingComplete'] and report['publicEntryReachability']['unreachableAllocatedHomes'] == 0
    assert pin(PACKAGE / 'manifest.json')['sha256'] == handoff['manifestSha256']
    assert pin(PACKAGE / 'catalog.json')['sha256'] == handoff['catalogSha256']
    external = {r['path']: r for r in read(PACKAGE / 'asset-plan.json')['assets']}; verified = set()
    for descriptor in read(PACKAGE / 'delivery-assets.json')['files'] + list(manifest['files'].values()):
        p = PACKAGE / descriptor['path']
        if not p.exists():
            p = Path(external[descriptor['path']]['sourcePath'])
        actual = pin(p)
        assert actual['sha256'] == descriptor['sha256'], descriptor['path']
        assert descriptor.get('bytes', actual['bytes']) == actual['bytes'], descriptor['path']
        assert actual['bytes'] < 25 * 1024 * 1024, descriptor['path']
        verified.add(descriptor['path'])
    assert catalog['overview']['edges'] == previous_catalog['overview']['edges']
    assert [(r['destinationId'], r['x'], r['y']) for r in catalog['overview']['nodes']] == [(r['destinationId'], r['x'], r['y']) for r in previous_catalog['overview']['nodes']]
    assert catalog['destinationAliases'] == previous_catalog['destinationAliases']
    old_ids = {r['id']: r for r in previous_catalog['relations']}
    for row in catalog['relations']:
        if row['id'] in old_ids:
            assert row.get('detail', {}).get('recordSha256') == old_ids[row['id']].get('detail', {}).get('recordSha256'), row['id']
    fine = read(PACKAGE / catalog['fineIndex']['path'])
    fine_index = {r['id']: r for r in fine['destinations']}
    lazy_cache = {}
    new_cases = []
    for row in authority['rows']:
        id = row['unitId'].replace('unit:', 'source-question:'); indexed = fine_index[id]
        descriptor = catalog['detailShards'][indexed['detail']['shardId']]
        if descriptor['path'] not in lazy_cache:
            lazy_cache[descriptor['path']] = read(PACKAGE / descriptor['path'])
        destination = lazy_cache[descriptor['path']]['destinations'][id]['destination']
        assert destination['question'] == row['sourceQuestion']
        unresolved = row['disposition'] == 'approved_unresolved_source_facet'
        if unresolved:
            assert destination['sourceHomeNotice'] == authority['newUnresolvedNotice']
            assert destination['sourceHomeReason'] == row['reason']
            assert not any(p['unitId'] == row['unitId'] for p in packet['placements'])
        new_cases.append({'caseId': row['caseId'], 'paperId': row['paperId'], 'unitId': row['unitId'], 'sourceFacetId': id, 'destinationId': row['destinationId'], 'unresolved': unresolved, 'notice': authority['newUnresolvedNotice'] if unresolved else None, 'reason': row['reason']})
    assert len(fine_index) == 8473
    old_cases = read(ROOT / 'research/q025/assembly/final-preholdout-v1/acceptance-cases.json')
    cases = {'schemaVersion': 'q025-final-release-acceptance-cases/1', 'unchangedPreholdoutCases': old_cases, 'dated43Cases': new_cases, 'h17Override': next(r for r in new_cases if r['caseId'] == 'H17'), 'sixExplicitNotices': [r for r in new_cases if r['unresolved']], 'scientificRoutesUnchanged': True, 'sourceFacetCount': 8473, 'sourceAccessAdded': 37}
    dump(HERE / 'acceptance-cases.json', cases)
    files = ['manifest.json', 'catalog.json', 'accepted-geometry-input.json', 'assembly-report.json', 'partition-validation.json', 'handoff.json', 'asset-plan.json', 'delivery-assets.json']
    result = {'schemaVersion': 'q025-dated-final-release-freeze/1', 'status': 'frozen_for_final_integration_acceptance', 'packageDirectory': str(PACKAGE), 'notApprovedForSiteRelease': True, 'files': [pin(PACKAGE / f) for f in files], 'packet': pin(HERE / 'packet/aggregate.local.json'), 'admissionReceipt': pin(HERE / 'packet/aggregate-admission.json'), 'accountingReceipt': pin(HERE / 'packet/source-accounting-admission.json'), 'rootAdjudication': pin(ROOT / 'research/q025/evaluation/final-holdout/root-43-source-adjudication.json'), 'candidateFreeze': pin(ROOT / 'research/q025/evaluation/final-holdout/candidate-freeze.json'), 'scoreFreeze': pin(ROOT / 'research/q025/evaluation/final-holdout/score-freeze.json'), 'acceptanceCases': pin(HERE / 'acceptance-cases.json'), 'scope': manifest['scope'], 'counts': handoff['counts'], 'publicEntryReachability': report['publicEntryReachability'], 'identity': report['canonicalProjection'], 'sourceMass': report['sourceMass'], 'scientificInputsUnchanged': ['scopes', 'routes', 'source-role observations', 'aliases', 'complete identity inventory', 'public entry frontier', 'old source allocations', 'old unresolved source reasons'], 'newSourceFacetCount': 43, 'newSourceAccessLinks': 37, 'geometry': {'manifest': pin(GEOMETRY / 'results/manifest.json'), 'schematic': pin(GEOMETRY / 'schematic-overview.json'), 'diagnostics': pin(GEOMETRY / 'results/diagnostics.json'), 'unchangedF': read(GEOMETRY / 'results/manifest.json')['unchangedF'], 'membershipSha256': handoff['provenance']['geometryInputSha256'], 'historicalFailedProjectionMembershipSha256': '738f78084a1908a8c7e3057021d400319ef1044344ecbaeaccf71f4d999f3bff', 'newFits': 0}, 'transport': {'verifiedAssetPaths': len(verified), 'externalAssets': len(external), **handoff['partition']['fileCountGate'], 'remoteSourcePack': '/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/pack'}, 'interfacePins': [pin(ROOT / p) for p in ['lib/geometry/prepared-atlas.mjs', 'lib/geometry/prepared-identity.mjs', 'lib/protocol/display-editorial.mjs']], 'tests': pin(HERE / 'tests.log'), 'releaseLimit': 'Scientific accounting is complete, including honest zero-H unresolved facets. Root still owns final browser/agent acceptance, installation and deployment. This dated amendment is not independent retest evidence.'}
    dump(HERE / 'freeze-handoff.json', result)
    print(json.dumps({'freeze': pin(HERE / 'freeze-handoff.json'), 'cases': pin(HERE / 'acceptance-cases.json'), 'verifiedAssets': len(verified)}, indent=2))


if __name__ == '__main__':
    main()
