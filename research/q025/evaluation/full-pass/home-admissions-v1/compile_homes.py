"""Bind the exact root-approved 1,055-home cut; do not expand its rule or inputs."""
import collections, hashlib, json, re, subprocess, sys
from pathlib import Path

B = Path(__file__).resolve().parent
F, E = B.parent, B.parent.parent
W = E.parents[2]
sys.path.insert(0, str(F / 'findings-v1'))
from audit_field_completeness import screen as field_screen

PINS = {
 'native-local/uncomplicated-home-candidates-v1.json': '90f8d0b907b219e82af7fcecb3b0745a32cec43857eafdd8248b97fc49a36fe0',
 'admissions-v1/uncomplicated-home-policy-audit-v1.json': '9ac8f84776f393d655bb4128371a04c6c4c85e3ce2a1910356fac14e4689aa44',
 'admissions-v1/supported-scope-role-component-v1.json': '7524a7784f7e4f9103cf4938278df3ebf53ed7af05da0e56688ecfbf80f51a93',
 'reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json': 'c9c419d7ded388f1355e31b1bef413ab09ca12de0e7cd60be996f687655fcf8a',
}
POSITIVE = {'addresses', 'instantiates', 'specializes'}
CONTEXT = re.compile(r'\b(?:inherit\w*|context\w*|compound|multi[- ]target|distinct.{0,40}targets|linked.{0,20}target|unclear|ambiguous|not (?:a |the )?direct|future work|not performed)\b', re.I)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump = lambda p, x: Path(p).write_text(json.dumps(x, ensure_ascii=False, separators=(',', ':')) + '\n')

def exclusion(prior, current, local, global_address_ids, record):
 if global_address_ids != {record['candidateId']}: return 'multiple_addresses_destinations'
 if record['scopeStatus'] != 'independently_supported' or record['scopeDefinitionFlags']: return 'scope_not_unchanged_supported'
 if any((local, 'addresses') not in {(q['id'], q['role']) for q in a['q']} for a in (prior, current)): return 'no_paired_addresses'
 if any(a['d'] != 'member' for a in (prior, current)): return 'not_joint_member'
 if any({q['id'] for q in a['q'] if q['role'] in POSITIVE} != {local} for a in (prior, current)): return 'multiple_or_changed_positive_targets'
 if any(a['identity'] == 'u' for a in (prior, current)): return 'unresolved_identity'
 if any(a['reason'] in ('changed_regime', 'scope_mismatch') for a in (prior, current)): return 'changed_scope_or_regime'
 if record['admissionJustificationFlags']: return 'unresolved_scope_note_flag'
 if field_screen({'units': [prior, current]})[0]: return 'unresolved_unit_annotation_flag'
 if CONTEXT.search(prior['note'] + ' ' + current['note']): return 'context_compound_or_unclear_target'
 return None

def main():
 for path, expected in PINS.items():
  assert sha(F / path) == expected, f'Input cut changed: {path}'
 candidates = json.loads((F / 'native-local/uncomplicated-home-candidates-v1.json').read_text())['candidates']
 component = json.loads((F / 'admissions-v1/supported-scope-role-component-v1.json').read_text())
 registry = json.loads((F / 'reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json').read_text())
 records = {r['candidateId']: r for r in registry['records']}
 reviews = {r['reviewId']: r for r in registry['reviews']}
 scopes = {d['id']: d for d in component['destinations']}
 contributions = {r['decisionId']: r for r in component['sourceContributions']}
 proofs = {r['id']: r for r in component['decisions']}
 addresses = collections.defaultdict(set)
 for r in component['sourceContributions']:
  if r['role'] == 'addresses': addresses[r['unitId']].add(r['destinationId'])
 cache, placements, evidence_bindings = {}, [], []
 assert len(candidates) == 1055 and len({c['unitId'] for c in candidates}) == 1055
 for c in candidates:
  record = records[c['destinationId']]
  rid = record['reviewId']
  if rid not in cache:
   directory = E / reviews[rid]['artifactDirectory']
   p = json.loads((directory / 'packet.actual.json').read_text())
   r = json.loads((directory / 'reply.json').read_text())
   receipt = json.loads((directory / 'receipt.json').read_text())
   assert receipt['status'] == 'complete' and sha(directory / 'reply.json') == receipt['normalizedReplySha256']
   cache[rid] = (p, {p['refRegistry'][u['descriptionRef']]['unitId']: u for u in p['units']}, {u['i']: u for u in p['priorAssignments']}, {u['i']: u for u in r['units']})
  p, units, old, now = cache[rid]
  u = units[c['unitId']]
  a, b = old[u['i']], now[u['i']]
  assert exclusion(a, b, record['localRef'], addresses[c['unitId']], record) is None, c['unitId']
  assert c['description'] == u['description'] and c['paperId'] == u['paperId']
  assert c['proposalNote'] == a['note'] and c['challengeNote'] == b['note']
  source = contributions[c['contributionDecisionId']]
  proof = proofs[source['decisionId']]
  scope = scopes[c['destinationId']]
  assert source['role'] == 'addresses' and source['unitId'] == c['unitId'] and source['destinationId'] == c['destinationId']
  assert c['scopeContentSha256'] == scope['scopeContentSha256'] == proof['scopeContentSha256']
  assert source['basis'] == c['basis'] and source['evidenceRefs'] == c['evidenceRefs']
  assert proof['challengerAgreement'] == 'independently_agreed'
  decision_id = 'decision:organizational-home:' + hashlib.sha256((c['unitId'] + '\n' + c['destinationId']).encode()).hexdigest()[:24]
  placements.append({'unitId': c['unitId'], 'destinationId': c['destinationId'], 'role': 'member', 'status': 'accepted', 'basis': source['basis'], 'allocationWeight': 1, 'workRelation': 'on', 'qualification': 'This source addresses a question within this scoped destination. Its specific system, regime and source-reading limits remain attached; membership does not equate the source statement with the broader question.', 'evidenceRefs': source['evidenceRefs'], 'decisionId': decision_id})
  evidence_bindings.append({'decisionId': decision_id, 'sourceContributionDecisionId': source['decisionId'], 'sourceReviewIds': proof['sourceReviewIds'], 'reviewAgreement': proof['reviewAgreement'], 'sourceDescriptionSha256': p['refRegistry'][u['descriptionRef']]['textSha256'], 'sourceScopeContentSha256': scope['scopeContentSha256'], 'originalNotesSha256': {stage: hashlib.sha256(row['note'].encode()).hexdigest() for stage, row in [('proposal', a), ('challenge', b)]}, 'evidenceAgreementIsNotOriginalPlacementAgreement': True})
 helper = E.parent / 'assembly/accepted.mjs'
 script = 'import {scopeContentHash,placementContentHash} from ' + json.dumps(helper.as_uri()) + ';let s="";for await(const c of process.stdin)s+=c;const x=JSON.parse(s),d=new Map(x.scopes.map(d=>[d.id,d]));console.log(JSON.stringify(x.placements.map(p=>({scope:scopeContentHash(d.get(p.destinationId)),placement:placementContentHash(p,scopeContentHash(d.get(p.destinationId)))}))));'
 hashes = json.loads(subprocess.run(['node', '--input-type=module', '-e', script], input=json.dumps({'scopes': component['destinations'], 'placements': placements}, ensure_ascii=False), text=True, capture_output=True, check=True).stdout)
 for c, h in zip(candidates, hashes): assert c['scopeContentSha256'] == h['scope'], (c['destinationId'], c['scopeContentSha256'], h['scope'])
 receipt = {'schemaVersion': 'q025-uncomplicated-home-policy-admission/1', 'status': 'accepted_explicit_placement', 'adjudicator': 'root_policy_authorization', 'authorization': 'Root read ten full examples and explicit KK counterexamples, then authorized the conservative exact class in POLICY.md. This is organizational membership in unchanged scopes, not original independent placement agreement or canonical question identity.', 'policy': {'path': str((B/'POLICY.md').relative_to(W)), 'sha256': sha(B/'POLICY.md')}, 'inputCut': [{'path': str((F/path).relative_to(W)), 'sha256': value} for path, value in PINS.items()], 'compilerSha256': sha(__file__), 'placements': [{'unitId': p['unitId'], 'destinationId': p['destinationId'], 'scopeContentSha256': h['scope'], 'placementContentSha256': h['placement'], 'allocationWeight': 1} for p,h in zip(placements, hashes)], 'scopeChangePolicy': 'A changed canonical scope requires placement revalidation; no automatic remap is authorized.', 'scientificIdentityAdmission': False, 'fullAtlasAdmission': False}
 receipt_path = B/'home-policy-admission.json'
 dump(receipt_path, receipt)
 ref = {'path': str(receipt_path.relative_to(W)), 'sha256': sha(receipt_path)}
 decisions = [{'id': p['decisionId'], 'type': 'placement', 'status': 'accepted', 'subjectIds': [p['unitId'], p['destinationId']], 'scopeContentSha256': h['scope'], 'placementContentSha256': h['placement'], 'challengerAgreement': 'not_reviewed_as_placement', 'sourceEvidenceAgreement': 'independently_agreed', 'adjudication': {'status': 'accepted_explicit_placement', 'receipt': ref}, 'sourceReviewIds': m['sourceReviewIds'], 'evidenceRefs': p['evidenceRefs'], 'sourceAgreementBinding': m} for p,h,m in zip(placements, hashes, evidence_bindings)]
 fragment = {'schemaVersion': 'q025-organization-admission-delta/1', 'baseComponent': {'path': str((F/'admissions-v1/supported-scope-role-component-v1.json').relative_to(W)), 'sha256': PINS['admissions-v1/supported-scope-role-component-v1.json']}, 'placements': placements, 'decisions': decisions, 'adjudicationReceipt': ref, 'allocationPolicy': 'explicit_normalized_weights', 'scopeChanges': [], 'relations': [], 'aliases': [], 'completeAtlasAdmission': False, 'canonicalRemapping': 'Requires separately admitted mapping and unchanged scope or explicit placement revalidation.'}
 output = B/'home-admission-delta.json'
 dump(output, fragment)
 report = {'schemaVersion': 'q025-home-admission-report/1', 'admittedUnits': len(placements), 'admittedPlacements': len(placements), 'distinctDestinations': len({p['destinationId'] for p in placements}), 'readingBasis': dict(collections.Counter(p['basis'] for p in placements)), 'allWeightsOne': True, 'component': {'path': str(output.relative_to(W)), 'sha256': sha(output)}, 'adjudicationReceipt': ref, 'inputCut': receipt['inputCut'], 'fullAtlasAdmission': False, 'scopeOrIdentityChanges': 0}
 (B/'report.json').write_text(json.dumps(report, indent=2)+'\n')
 print(json.dumps(report))

if __name__ == '__main__': main()
