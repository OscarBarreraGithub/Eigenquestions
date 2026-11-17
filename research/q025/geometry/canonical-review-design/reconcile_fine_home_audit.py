"""Reconcile row-level home evidence across all assessments of an exact unit.

This is a policy-candidate census, not a placement compiler. It deliberately
preserves the earlier row-level audit and all original review annotations.
"""
import collections
import hashlib
import json
import re
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
F = ROOT / 'research/q025/evaluation/full-pass'


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)),
                            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def reconcile(rows, approved_ids=()):
    """Do not let one clean context erase explicit coverage work in another.

    Different unrelated scopes' exclusions are retained but are not universal
    cannot-link constraints. Additional positive roles are not themselves a
    contradiction to an explicit home; they are a separate review inventory.
    """
    by_unit = collections.defaultdict(list)
    for row in rows:
        by_unit[row['unitId']].append(row)
    compound = re.compile(r'compound|multi[- ]target|(?:distinct|separate).{0,40}targets|linked.{0,20}target', re.I)
    results = []
    for uid, contexts in sorted(by_unit.items()):
        valid = [r for r in contexts if not r['exclusionReasons']]
        clean = [r for r in valid if not r['coverageReviewReasons']]
        if not clean:
            continue
        targets = sorted({r['destinationId'] for r in valid})
        reasons = []
        if len(targets) > 1:
            reasons.append('multiple_explicit_paired_home_destinations_across_contexts')
        compound_contexts = [r for r in contexts if compound.search(r['proposalNote'] + ' ' + r['challengeNote'])]
        if compound_contexts:
            reasons.append('compound_target_coverage_in_a_recorded_context')
        selected = targets[0] if len(targets) == 1 else None
        same_target_conflicts = [r for r in contexts if selected and r['destinationId'] == selected and
                                any(x in r['exclusionReasons'] for x in (
                                    'explicit_changed_regime_or_scope_mismatch',
                                    'unresolved_unit_annotation_screen',
                                    'unresolved_scope_annotation_or_definition_flag'))]
        if same_target_conflicts:
            reasons.append('unresolved_annotation_or_premise_at_the_same_home')
        same_target_coverage = [r for r in valid if selected and r['destinationId'] == selected and r['coverageReviewReasons']]
        if same_target_coverage:
            reasons.append('coverage_qualification_in_another_assessment_of_the_same_home')
        results.append({
            'unitId': uid, 'paperId': contexts[0]['paperId'],
            'selectedDestinationId': selected, 'explicitPairedDestinationIds': targets,
            'status': 'requires_targeted_coverage_or_canonical_decision' if reasons else 'candidate_explicit_home_policy',
            'reviewReasons': reasons, 'alreadyApprovedSimpleHome': uid in approved_ids,
            'cleanContextReviewIds': sorted({r['reviewId'] for r in clean}),
            'allContextReviewIds': sorted({r['reviewId'] for r in contexts}),
            'compoundContextReviewIds': sorted({r['reviewId'] for r in compound_contexts}),
            'sameTargetConflictReviewIds': sorted({r['reviewId'] for r in same_target_conflicts}),
            'chosenHomeRoles': sorted({role for r in clean for role in r['chosenHomeAgreedRoles']}),
        })
    return results


def main():
    stage, stage_pin = read(B / 'explicit-fine-home-audit.json')
    payload, payload_pin = read(B / 'explicit-fine-home-candidates.local.json')
    broad_report, br_pin = read(B / 'broader-home-audit.json')
    broad, broad_pin = read(B / 'broader-home-candidates.local.json')
    simple, simple_pin = read(F / 'native-local/uncomplicated-home-candidates-v1.json')
    component, component_pin = read(F / 'admissions-v1/supported-scope-role-component-v1.json')
    compiler_pin = read_script(F / 'admissions-v1/audit_uncomplicated_homes.py')
    allrows = payload['cleanCandidateRows'] + payload['coverageReviewRows'] + payload['excludedRows']
    approved = {r['unitId'] for r in simple['candidates']}
    reconciled = reconcile(allrows, approved)
    eligible = {r['unitId'] for r in reconciled if not r['reviewReasons']}
    pending = [r for r in reconciled if r['reviewReasons']]
    by_unit = collections.defaultdict(list)
    positive = collections.defaultdict(set)
    for r in allrows:
        by_unit[r['unitId']].append(r)
    for r in component['sourceContributions']:
        if r['role'] in ('addresses', 'instantiates', 'specializes'):
            positive[r['unitId']].add(r['destinationId'])
    for r in reconciled:
        r['admittedPositiveDestinationIds'] = sorted(positive[r['unitId']])
        r['otherPositiveScopesRequireNoSilentEquivalence'] = len(positive[r['unitId']]) > 1
    index = {r['unitId']: r for r in reconciled}
    sample_exclusions = []
    for sample in broad_report['examples']:
        uid = sample['unitId']
        exclusions = [r for r in simple['excluded'] if r['unitId'] == uid]
        admitted_roles = [r for r in component['sourceContributions'] if r['unitId'] == uid]
        reason = exclusions[0]['reason'] if exclusions else (
            'already_in_approved_simple_class' if uid in approved else
            'not_in_addresses_only_intake' if not any(r['role'] == 'addresses' for r in admitted_roles) else
            'requires_compiler_inspection')
        sample_exclusions.append({
            'paperId': sample['paperId'], 'unitId': uid,
            'originalSimplePolicyExclusion': reason,
            'originalSimplePolicyExclusionRecords': exclusions,
            'admittedRoleInventory': [{'destinationId': r['destinationId'], 'role': r['role'],
                                       'decisionId': r['decisionId']} for r in admitted_roles],
            'globalFineHomeCandidate': index.get(uid),
            'exactAssessmentContexts': by_unit[uid],
            'broadExampleReviewPins': sample['reviewPins'],
        })
    out_payload = {'units': reconciled, 'status': 'candidate_policy_audit_no_new_admission'}
    full_path = B / 'explicit-fine-home-reconciled.local.json'
    full_path.write_text(json.dumps(out_payload, ensure_ascii=False, separators=(',', ':')) + '\n')
    broad_ids = {r['unitId'] for r in broad['candidates']}
    assessed = set(by_unit)
    counts = {
        'uniqueAssessedUnits': len(assessed),
        'stage1RowCleanSingleHomeUnits': stage['counts']['cleanFineHomeSingleDestinationUnits'],
        'unitsWithAtLeastOneRowCleanHome': len(reconciled),
        'globalPolicyCandidateUnits': len(eligible),
        'additionalPolicyCandidateUnitsBeyondApproved1055': len(eligible - approved),
        'pendingAcrossContextCoverageOrCanonicalDecision': len(pending),
        'pendingReasons': dict(collections.Counter(x for r in pending for x in r['reviewReasons'])),
        'alreadyApprovedUnitsWithNewCrossContextScreenFlag': sum(r['alreadyApprovedSimpleHome'] for r in pending),
        'policyCandidateUnitsWithOtherAdmittedPositiveScopes': sum(len(positive[u]) > 1 for u in eligible),
        'remainingAssessedAfterApprovedFineAndUnflaggedBroadCandidateUnion': len(assessed - approved - eligible - broad_ids),
        'newPolicyCandidateRoleCounts': dict(collections.Counter(role for r in reconciled if r['unitId'] in eligible - approved for role in r['chosenHomeRoles'])),
    }
    report = {
        'schemaVersion': 'q025-global-paired-home-evidence-audit/1',
        'status': 'candidate_policy_not_placement_or_identity_admission',
        'inputs': {'stage1Audit': stage_pin, 'stage1Rows': payload_pin, 'broaderAudit': br_pin,
                   'broaderRows': broad_pin, 'approvedSimpleCandidates': simple_pin,
                   'scopeRoleComponent': component_pin, 'simplePolicyCompiler': compiler_pin,
                   'reconciledUnits': read(full_path)[1]},
        'counts': counts, 'eightExactExclusionDiagnoses': sample_exclusions,
        'interpretation': [
            'The original 1,055 rule already permits method, comparison and boundary contributions. Its positive-role set is addresses, instantiates and specializes; only the initial intake is addresses-only.',
            'Stage1 counts were row-clean evidence, not global allocation eligibility. A second context can retain a compound target or another explicit home. This audit never erases that evidence.',
            'A unique explicitly chosen home with a compatible agreed direct-target role can be an organizational candidate despite other scoped contributions. This is neither scientific equivalence nor a license to discard a compound target.',
            'A changed-regime or inherited-context annotation about another scope is not a universal exclusion. Same-target conflicts and explicit compound notes remain targeted review work.',
            'Already approved homes are not revoked by this diagnostic. Any new cross-context concern is an explicit coordinator review item.',
            'Canonical reconciliation must precede final H; multiple candidate IDs are not silently unioned and original numerical bins provide no fallback homes.',
        ],
        'homesAdmitted': 0, 'noSealedHoldoutOpened': True,
        'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    out = B / 'explicit-fine-home-global-audit.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'report': read(out)[1], 'counts': counts}, indent=2))


def read_script(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


if __name__ == '__main__':
    main()
