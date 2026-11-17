"""Full-cut organization census using existing paired evidence, not admission."""
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
F = ROOT / 'research/q025/evaluation/full-pass'
sys.path.insert(0, str(F / 'findings-v1'))
from audit_field_completeness import screen
from reconcile_fine_home_audit import reconcile


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


registry, rpin = read(F / 'reconciliation-v1/authored-scope-registry-v4-20261117T131639Z.json')
assert rpin['sha256'] == '8fec0de5da3901625e4fea16240d4a487878b7b6c803c29a3e3893dc89c1fe7e'
component, cpin = read(F / 'admissions-v2/supported-scope-role-component-v2.json')
homes, hpin = read(F / 'home-admissions-v1/home-admission-delta.json')
overlay, opin = read(F / 'annotation-admissions-v3/intake-overlay-v2.json')
assert opin['sha256'] == 'bdea68416a4fcdb751796264a5945e9a93f1780ee26a6cf53cdafc4f0243ae3e'
records = {r['recordId']: r for r in registry['records']}
resolved_scope_flags = {}
for resolution in overlay['scopeAssessmentResolutions']:
    r = records[resolution['recordId']]
    assert resolution['scopeDefinitionUnchanged'] and resolution['doesNotAlterScopeAgreement']
    assert hashlib.sha256(r['assessment']['note'].encode()).hexdigest() == resolution['originalTextSha256']
    assert hashlib.sha256(resolution['replacementText'].encode()).hexdigest() == resolution['replacementTextSha256']
    resolved_scope_flags[r['recordId']] = resolution['resolvedFlags']


def unresolved_scope_flags(r):
    return bool(r.get('scopeDefinitionFlags')) or any(
        flag not in resolved_scope_flags.get(r['recordId'], [])
        for flag in r.get('admissionJustificationFlags', []))

by_candidate = collections.defaultdict(list)
for r in registry['records']:
    by_candidate[r['candidateId']].append(r)
admitted_scopes = {d['id'] for d in component['destinations']}
approved = {r['unitId'] for r in homes['placements']}
positive = {'addresses', 'instantiates', 'specializes'}
compound = re.compile(r'compound|multi[- ]target|(?:distinct|separate).{0,40}targets|linked.{0,20}target', re.I)
context = re.compile(r'\b(?:inherit\w*|context\w*|not (?:a |the )?direct|unclear|ambiguous)\b', re.I)
fine_rows, broad_rows = [], []
seen = set()
for assessment_index, a in enumerate(registry['unitAssessments']):
    key = (a['reviewId'], a['unitId'])
    assert key not in seen
    seen.add(key)
    p, c, h = a['proposalAttribution'], a['challengeAttribution'], a['homeAgreement']
    candidate = h['challenge'].get('candidateId')
    targets = by_candidate.get(candidate, [])
    target = next((r for r in targets if r['reviewId'] == a['reviewId']), targets[0] if targets else None)
    flags = screen({'units': [p, c]})[0]
    changed = any(r['reason'] in ('changed_regime', 'scope_mismatch') for r in (p, c))
    reasons = []
    if not h['sameExplicitScientificCard'] or not h['proposalDefinitionMatchesPinnedOriginal']:
        reasons.append('no_exact_same_explicit_home')
    if not target or target['kind'] != 'question' or not h['unchangedSupportedScope']:
        reasons.append('chosen_home_not_an_unchanged_supported_question_scope')
    agreed_roles = sorted({r['role'] for r in a['questionContributions'] if r['independentRoleAgreement'] and
                           r['recordId'] in records and records[r['recordId']]['candidateId'] == candidate})
    if not set(agreed_roles) & positive:
        reasons.append('no_agreed_direct_target_role_at_chosen_home')
    if flags:
        reasons.append('unresolved_unit_annotation_screen')
    if changed:
        reasons.append('explicit_changed_regime_or_scope_mismatch')
    if target and unresolved_scope_flags(target):
        reasons.append('unresolved_scope_annotation_or_definition_flag')
    other_positive = {q['id'] for row in (p, c) for q in row['q'] if q['role'] in positive and q['id'] != h['challenge'].get('normalizedRef')}
    note_text = p['note'] + ' ' + c['note']
    coverage = []
    if other_positive:
        coverage.append('additional_positive_target_requires_coverage_decision')
    if compound.search(note_text):
        coverage.append('explicit_compound_target_language')
    if context.search(note_text):
        coverage.append('inherited_context_or_ambiguity_language_requires_target_check')
    row = {'unitId': a['unitId'], 'paperId': a['paperId'], 'reviewId': a['reviewId'],
           'destinationId': candidate, 'title': target['definition']['title'] if target else None,
           'scopeStatus': target['scopeStatus'] if target else None,
           'scopeAlreadyAdmitted': candidate in admitted_scopes,
           'homeAgreement': h, 'chosenHomeAgreedRoles': agreed_roles,
           'proposalNote': p['note'], 'challengeNote': c['note'],
           'proposalReason': p['reason'], 'challengeReason': c['reason'],
           'broadDispositions': [p['d'], c['d']], 'exclusionReasons': reasons,
           'coverageReviewReasons': coverage, 'unitAnnotationFlags': flags,
           'sourceAssessmentIndex': assessment_index}
    fine_rows.append(row)
    broad = records.get(a['reviewId'] + ':r')
    if broad and broad['scopeStatus'] == 'independently_supported' and p['d'] == c['d'] and p['d'] in ('member', 'overlap'):
        broad_flags = unresolved_scope_flags(broad)
        broad_rows.append({'unitId': a['unitId'], 'paperId': a['paperId'], 'reviewId': a['reviewId'],
                           'destinationId': broad['candidateId'], 'title': broad['definition']['title'],
                           'scopeAlreadyAdmitted': broad['candidateId'] in admitted_scopes,
                           'jointDisposition': p['d'], 'compoundLanguage': bool(compound.search(note_text)),
                           'contextLanguage': bool(context.search(note_text)),
                           'unresolvedFlags': bool(flags) or changed or broad_flags,
                           'flagReasons': (["unit_annotation"] if flags else []) + (["changed_regime_or_scope_mismatch"] if changed else []) + (["scope_annotation_or_definition"] if broad_flags else []),
                           'proposalNote': p['note'], 'challengeNote': c['note']})

reconciled = reconcile(fine_rows, approved)
fine_ids = {r['unitId'] for r in reconciled if not r['reviewReasons']}
broad_ok = [r for r in broad_rows if not r['unresolvedFlags']]
member = {r['unitId'] for r in broad_ok if r['jointDisposition'] == 'member'}
overlap = {r['unitId'] for r in broad_ok if r['jointDisposition'] == 'overlap'}
compound_ids = {r['unitId'] for r in fine_rows if compound.search(r['proposalNote'] + ' ' + r['challengeNote'])}
assessed = {a['unitId'] for a in registry['unitAssessments']}
unplaced = assessed - approved
lanes = {}
for name, ids in [
    ('additional_global_explicit_fine_home_policy_candidates', fine_ids),
    ('joint_broader_member_without_compound_language', member - compound_ids),
    ('joint_broader_member_needs_whole_compound_scope_coverage_check', member & compound_ids),
    ('joint_broader_overlap_needs_complete_target_allocation', overlap),
]:
    lanes[name] = sorted(unplaced & ids)
    unplaced -= ids
lanes['remaining_assessed_requires_targeted_organization_decision'] = sorted(unplaced)
assert len(approved & assessed) + sum(map(len, lanes.values())) == len(assessed)
residual_roles = collections.defaultdict(set)
for r in registry['records']:
    for c in r['contributions']:
        if c['independentRoleAgreement']:
            residual_roles[c['unitId']].add(c['role'])
residual_types = collections.Counter()
for uid in unplaced:
    roles = residual_roles[uid]
    label = 'agreed_addresses' if 'addresses' in roles else 'agreed_instantiates_or_specializes' if roles & positive else 'method_comparison_boundary_only' if roles else 'no_agreed_question_role'
    residual_types[label] += 1
residual_diagnostics = {
    'hasBroadPairedAttributionBlockedByAnnotationOrPremise': len({r['unitId'] for r in broad_rows if r['unitId'] in unplaced and r['unresolvedFlags']}),
    'broadAttributionBlockedOnlyByUnitAnnotationScreen': len({r['unitId'] for r in broad_rows if r['unitId'] in unplaced and r['flagReasons'] == ['unit_annotation']}),
    'hasExactFineHomeButCoverageDecisionPending': len({r['unitId'] for r in fine_rows if r['unitId'] in unplaced and not r['exclusionReasons'] and r['coverageReviewReasons']}),
    'hasFineHomeBlockedOnlyByAnnotationScreens': len({r['unitId'] for r in fine_rows if r['unitId'] in unplaced and r['exclusionReasons'] and set(r['exclusionReasons']) <= {'unresolved_unit_annotation_screen', 'unresolved_scope_annotation_or_definition_flag'}}),
    'meaning': 'These counts overlap. They identify reusable existing evidence and annotation inspection, not a requirement to reread every source.'}
payload_path = B / 'home-lanes-v4.local.json'
payload_path.write_text(json.dumps({'fineContextRows': fine_rows, 'reconciledFineUnits': reconciled,
                                   'broadContextRows': broad_rows, 'disjointCandidateLanes': lanes},
                                  ensure_ascii=False, separators=(',', ':')) + '\n')
counts = {'eligiblePreHoldoutQuestions': 8430, 'uniqueAssessedUnits': len(assessed),
          'notYetAssessedInThisCut': 8430 - len(assessed), 'alreadyApprovedHomes': len(approved),
          'globalFineHomePolicyCandidateUnits': len(fine_ids),
          'fineCandidateUnitsWhoseScopeAlreadyAdmitted': len({r['unitId'] for r in fine_rows if r['unitId'] in fine_ids and r['scopeAlreadyAdmitted'] and not r['exclusionReasons']}),
          'unflaggedBroaderMemberUnits': len(member), 'unflaggedBroaderOverlapUnits': len(overlap),
          'disjointLanesBeyondApproved': {k: len(v) for k, v in lanes.items()},
          'residualAgreedRoleInventory': dict(residual_types),
          'residualExistingEvidenceDiagnostics': residual_diagnostics,
          'resolvedScopeAnnotationsAppliedWithoutMutatingRegistry': len(resolved_scope_flags),
          'leafLineages': sum(r['kind'] == 'leaf' for r in registry['selectedReviewLineages']),
          'parentLineages': sum(r['kind'] == 'parent' for r in registry['selectedReviewLineages'])}
report = {'schemaVersion': 'q025-full-cut-home-lane-audit/1', 'status': 'candidate_organization_census_no_new_admission',
          'inputs': {'registry': rpin, 'admittedScopeComponent': cpin, 'approvedHomes': hpin,
                     'annotationOverlay': opin,
                     'candidateRows': read(payload_path)[1]}, 'counts': counts,
          'meaning': [
              'A candidate class is not admitted allocation. Exact paired home references and source-target roles are evidence for an explicit coordinator policy; neither contribution nor lexical context becomes H automatically.',
              'New v4 scopes can be independently supported without being in the current mechanical admission component. Those scope admissions are a prerequisite, not a demand to reread the same unchanged scientific definition.',
              'Broad member is a scientific whole-question home only after explicit scope compatibility. A compound question may fit one sufficiently broad admitted scope; weights are split only when allocation actually uses multiple homes.',
              'Overlap alone cannot receive weight1 if part of the source target is excluded. Retain the original question and require complete target coverage or a reviewed broader home.',
              'Annotation/language screens are conservative review queues, not automatically scientific contradictions. Existing approvals are not revoked by a diagnostic.',
              'Candidate IDs are reconciled before final H. No simultaneous ancestor/descendant direct mass, no source disappearance and no old numerical-bin fallback.',
          ], 'newHomesAdmitted': 0, 'noSealedHoldoutOpened': True,
          'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
out = B / 'home-lanes-v4-report.json'
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'report': read(out)[1], 'counts': counts}, indent=2))
