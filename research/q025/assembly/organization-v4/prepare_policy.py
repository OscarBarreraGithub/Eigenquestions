"""Concrete placement-policy proposal from frozen paired judgments.

Produces no admitted decisions. The complete ID inventory separates existing
homes, pending policy rows and genuinely unresolved organizational choices.
"""
import collections
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
E = ROOT / 'research/q025/evaluation'
F = E / 'full-pass'


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def save(path, value, pretty=False):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2 if pretty else None,
                               separators=None if pretty else (',', ':')) + '\n')
    return read(path)[1]


registry, rpin = read(F / 'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json')
census, cpin = read(B / 'home-lanes-v5.local.json')
eligible, epin = read(F / 'reconciliation-v1/eligible-preholdout-unit-ids-v1.json')
simple, hpin = read(F / 'home-admissions-v1/home-admission-delta.json')
kk, kpin = read(F / 'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json')
support, spin = read(F / 'admissions-v3/supported-scope-role-component-v3.json')
canonical, apin = read(F / 'canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json')
constraints, xpin = read(F / 'canonical-pilot-admissions-v1/constraint-precedence.json')
records = {r['recordId']: r for r in registry['records']}
by_candidate = collections.defaultdict(list)
for r in registry['records']:
    by_candidate[r['candidateId']].append(r)
reviews = {r['reviewId']: r for r in registry['reviews']}
assessments = {(a['reviewId'], a['unitId']): a for a in registry['unitAssessments']}
source_contexts = collections.defaultdict(list)
for a in registry['unitAssessments']:
    source_contexts[a['unitId']].append(a)
assert set(source_contexts) == set(eligible['unitIds']) and len(source_contexts) == 8430
admitted_scopes = {d['id']: d for comp in (support, kk, canonical) for d in comp['destinations']}
admitted_placements = collections.defaultdict(list)
for row in simple['placements'] + kk['placements']:
    if row['role'] != 'context':
        admitted_placements[row['unitId']].append(row)
assert set(admitted_placements) <= set(source_contexts)
assert all(abs(sum(p['allocationWeight'] for p in ps) - 1) < 1e-10 for ps in admitted_placements.values())

fine = {r['unitId']: r for r in census['reconciledFineUnits'] if not r['reviewReasons']}
fine_rows = collections.defaultdict(list)
for r in census['fineContextRows']:
    fine_rows[r['unitId']].append(r)
broad_rows = collections.defaultdict(list)
for r in census['broadContextRows']:
    broad_rows[r['unitId']].append(r)
packet_cache = {}


def exact_source(uid, review_id=None):
    a = next(a for a in source_contexts[uid] if review_id is None or a['reviewId'] == review_id)
    rv = reviews[a['reviewId']]
    if rv['reviewId'] not in packet_cache:
        p, pin = read(E / rv['artifactDirectory'] / rv['challengeArtifact']['packetFile'])
        assert pin['sha256'] == rv['pins']['challengePacketSha256']
        packet_cache[rv['reviewId']] = (p, pin, {p['refRegistry'][u['descriptionRef']]['unitId']: u for u in p['units']})
    p, pin, umap = packet_cache[rv['reviewId']]
    u = umap[uid]
    ref = p['refRegistry'][u['descriptionRef']]
    assert hashlib.sha256(u['description'].encode()).hexdigest() == ref['textSha256']
    return {'unitId': uid, 'paperId': u['paperId'], 'description': u['description'],
            'descriptionSha256': ref['textSha256'], 'sourcePacket': pin,
            'sourceDescriptionRef': u['descriptionRef']}


def proof_context(a):
    rv = reviews[a['reviewId']]
    return {'reviewId': a['reviewId'], 'sourceOrigin': a['sourceOrigin'],
            'proposal': a['proposalAttribution'], 'challenge': a['challengeAttribution'],
            'homeAgreement': a['homeAgreement'], 'typedContributions': a['questionContributions'],
            'pins': rv['pins'], 'originalProposal': rv['proposalDependency']}


def proposal(uid, destination, lane, contexts):
    definitions = by_candidate[destination]
    record = next((r for r in definitions if r['reviewId'] in contexts), definitions[0])
    return {'unitId': uid, 'destinationId': destination, 'proposedRole': 'member',
            'proposedWeight': 1, 'policyClass': lane, 'status': 'pending_coordinator_policy_admission',
            'scopeAdmissionState': 'already_admitted' if destination in admitted_scopes else 'unchanged_supported_pending_component',
            'scopeContentSha256': admitted_scopes.get(destination, {}).get('scopeContentSha256'),
            'scopeRecordId': record['recordId'],
            'definitionSha256': hashlib.sha256(json.dumps(record['definition'], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
            'sourceReviewIds': sorted(contexts), 'basis': 'existing_paired_scientific_attribution_not_paired_placement_admission',
            'qualification': 'Organizational home for the complete original source question. This does not assert fine-question equivalence, method applicability or a new scientific result.'}


pending, queue, inventory = [], [], []
for uid in sorted(source_contexts):
    if uid in admitted_placements:
        inventory.append({'unitId': uid, 'state': 'existing_admitted_home', 'placements': admitted_placements[uid]})
        continue
    if uid in fine:
        f = fine[uid]
        row = proposal(uid, f['selectedDestinationId'], 'A_exact_paired_scientific_question_home', f['cleanContextReviewIds'])
        pending.append(row)
        inventory.append({'unitId': uid, 'state': 'pending_policy_A', 'proposal': row})
        continue
    members = [r for r in broad_rows[uid] if r['jointDisposition'] == 'member' and not r['unresolvedFlags']]
    destinations = {r['destinationId'] for r in members}
    # Unique reviewed whole-family attribution avoids an arbitrary choice among
    # overlapping broad scopes. Compound identity remains independent of home.
    if len(destinations) == 1 and not any(r['contextLanguage'] for r in members):
        destination = next(iter(destinations))
        compound = any(r['compoundLanguage'] for r in members) or any('compound' in r['coverageReviewReasons'] or 'explicit_compound_target_language' in r['coverageReviewReasons'] for r in fine_rows[uid])
        lane = 'B_compound_whole_family_home' if compound else 'B_whole_family_home'
        row = proposal(uid, destination, lane, {r['reviewId'] for r in members})
        row['compoundSourceRetained'] = compound
        pending.append(row)
        inventory.append({'unitId': uid, 'state': 'pending_policy_B', 'proposal': row})
        continue
    frows = fine_rows[uid]
    options = [{'destinationId': r['destinationId'], 'title': r['title'], 'scopeAlreadyAdmitted': r['scopeAlreadyAdmitted'],
                'reviewId': r['reviewId'], 'homeAgreement': r['homeAgreement'],
                'chosenHomeRoles': r['chosenHomeAgreedRoles'], 'exclusionReasons': r['exclusionReasons'],
                'coverageReviewReasons': r['coverageReviewReasons']} for r in frows if r['destinationId']]
    if len(destinations) > 1:
        question = 'Select or reconcile the reviewed broader scientific homes; distinct candidate IDs do not authorize a mass split or an alias union.'
        kind = 'multiple_reviewed_broad_homes'
    elif members:
        question = 'Check whether the contextual qualification excludes part of the source target from this otherwise paired-member family.'
        kind = 'whole_family_qualification'
    elif any(r['jointDisposition'] == 'overlap' and not r['unresolvedFlags'] for r in broad_rows[uid]):
        question = 'Identify all covered source targets and a whole-question home, or explicitly approve a normalized overlap. An overlap-only family cannot silently receive the whole mass.'
        kind = 'overlap_needs_complete_target_coverage'
    elif any(r['unresolvedFlags'] for r in broad_rows[uid]):
        question = 'Resolve the specific note/premise flag on an already paired broader attribution; a format or reading-limit repair need not trigger another full source reading.'
        kind = 'flagged_existing_broad_attribution'
    elif any(not r['exclusionReasons'] for r in frows):
        question = 'Check whole-question coverage of the exact paired fine-home candidates; reuse their definitions and paired notes before requesting new primary text.'
        kind = 'fine_home_coverage_or_cross_context_conflict'
    else:
        question = 'Choose a scientifically meaningful home from the recorded targets and alternate-family judgments, or specify the missing scope. Do not use an unclassified or numerical-bin fallback.'
        kind = 'explicit_home_missing_or_disputed'
    q = {'unitId': uid, 'paperId': source_contexts[uid][0]['paperId'], 'decisionKind': kind, 'decisionNeeded': question,
         'fineOptions': options, 'broadOptions': broad_rows[uid],
         'sourceContextRefs': [{'reviewId': a['reviewId'], 'unitId': uid} for a in source_contexts[uid]]}
    queue.append(q)
    inventory.append({'unitId': uid, 'state': 'explicit_organization_decision_pending', 'decisionKind': kind})
assert len(inventory) == 8430 and len({r['unitId'] for r in inventory}) == 8430
full_pin = save(B / 'placement-policy-candidates.local.json', {'pendingPlacements': pending, 'organizationDecisionQueue': queue, 'completeEligibleInventory': inventory})

selected = [
    ('A_specialization_boundary_symmetries', 'unit:04c13df18a4f760f60de9f358f6862798e5f827c81098c74e430ae013a015b09'),
    ('A_instantiation_global_uplift', 'unit:01f899fb19b6229a2737879c5798aeebdf381e6c68b170bf7a21aaf41b6ce441'),
    ('A_named_home_despite_other_comparison_and_addresses_routes', 'unit:0c0e5bc0d09c001963465763a3e9658f3a596ca8cb8303f361b69b7867258d3a'),
    ('B_axionic_EFT_string_anomalies', 'unit:002c4e5fbdee96b81e899bfae015ede31b5c59dcd22c3310352ade5f8dd25164'),
    ('B_ordinary_methodological_supergravity_question', 'unit:020d1dd32ca6f8925762345c8d87b3d46a91cc4e47f4092de72e7cebeb21c731'),
    ('B_compound_6d_symmetry_and_anomaly_targets', 'unit:02dd298620e4d0edea3b1967b2805c4362f55a80a94cd7e4f6e28d5ad27a8ce2'),
    ('cross_context_do_not_add_duplicate_mass', 'unit:128622e23dbd0a7aabb43506baba17e3b38181fb22558a0db701685bfbda855c'),
    ('overlap_only_stellar_KK_production_and_decay_bounds', 'unit:bd8c5b9a8b57126b3ca4cd9f8f106d4a591051d19ace30fd62d33141efb25f60'),
    ('annotation_only_flag_is_not_a_new_scientific_home', 'unit:0034b70ea953b9879b3d6034ad618cbfcb1be80a68ce1e19fa6ffa94793dec60'),
    ('negative_KK_inherited_production_is_not_a_production_home', 'unit:be7aae21bb2419d0869faff0e2d1c1e653b0e8e75d40ce2e657fb8fb7495284a'),
]
pending_by_unit = {r['unitId']: r for r in pending}
queue_by_unit = {r['unitId']: r for r in queue}
examples = []
for purpose, uid in selected:
    target_ids = {r['destinationId'] for r in fine_rows[uid] if r['destinationId']}
    target_ids.update(r['destinationId'] for r in broad_rows[uid])
    target_ids.update(r['destinationId'] for r in admitted_placements.get(uid, []))
    scopes = []
    for destination in sorted(target_ids):
        rs = by_candidate[destination]
        if rs:
            scopes.append({'destinationId': destination, 'recordId': rs[0]['recordId'],
                           'definition': rs[0]['definition'], 'scopeStatus': rs[0]['scopeStatus'],
                           'alreadyAdmitted': destination in admitted_scopes, 'pins': rs[0]['pins']})
        elif destination in admitted_scopes:
            scopes.append({'destinationId': destination, 'admittedDefinition': admitted_scopes[destination]})
    examples.append({'purpose': purpose, 'source': exact_source(uid),
                     'proposedPlacement': pending_by_unit.get(uid),
                     'existingAdmittedPlacements': admitted_placements.get(uid, []),
                     'remainingDecision': queue_by_unit.get(uid), 'candidateScopes': scopes,
                     'pairedAssessments': [proof_context(a) for a in source_contexts[uid]],
                     'scopeAndSourceIdentityNotMerged': True})
examples_pin = save(B / 'placement-policy-examples.json', {'schemaVersion': 'q025-placement-policy-examples/1', 'registry': rpin, 'examples': examples}, True)
counts = {'eligibleQuestions': 8430, 'existingAdmittedHomeUnits': len(admitted_placements),
          'existingHomeRows': sum(map(len, admitted_placements.values())),
          'pendingPolicyClasses': dict(collections.Counter(r['policyClass'] for r in pending)),
          'pendingClassesWithAlreadyAdmittedScope': sum(r['scopeAdmissionState'] == 'already_admitted' for r in pending),
          'pendingClassesAwaitingUnchangedScopeComponent': sum(r['scopeAdmissionState'] != 'already_admitted' for r in pending),
          'remainingOrganizationalDecisions': len(queue),
          'remainingDecisionKinds': dict(collections.Counter(r['decisionKind'] for r in queue)),
          'coveredIfBothPoliciesApprovedAfterScopeAdmission': len(admitted_placements) + len(pending),
          'unreviewedEligibleUnits': 0, 'reservedHoldoutUnitsNotAllocated': 43}
report = {'schemaVersion': 'q025-placement-policy-proposal/1', 'status': 'awaiting_explicit_coordinator_policy_admission',
          'inputs': {'registry': rpin, 'eligibleInventory': epin, 'census': cpin, 'existingSimpleHomes': hpin,
                     'existingKKHomes': kpin, 'scopeRoleSupport': spin, 'canonicalScopeRoleComponent': apin,
                     'currentHistoricalCanonicalConstraints': xpin, 'exactCandidateRows': full_pin, 'examples': examples_pin},
          'counts': counts,
          'proposedPolicies': [
              {'class': 'A_exact_paired_scientific_question_home', 'weight': 1,
               'rule': 'Both existing reviewers explicitly chose the same exact unchanged scientific question card, verified against the original proposal definition; the chosen target has an agreed addresses/instantiates/specializes role. Global source-context checks find no competing explicit home, compound coverage ambiguity or unresolved same-target premise/annotation conflict. Extra method/comparison roles do not veto the home. The target must have a separate scope admission before compilation.'},
              {'class': 'B_whole_family_home_and_B_compound_whole_family_home', 'weight': 1,
               'rule': 'When A does not settle the home, both existing reviewers place the complete source unit as member in the same unchanged scientific broad scope; the source has one such unflagged broad destination, no unresolved premise/annotation conflict and no inherited/context ambiguity in those member notes. Admit that whole-family organizational home, including compound source questions whose subtargets remain within the reviewed family. Keep all exact source text and typed subtarget contributions. Do not declare a compound source one atomic canonical question or split mass merely because it has several targets.'}
          ],
          'exceptions': [
              'Existing 1,055 home approvals and the five exact KK/UHECR source homes are preserved. Their six KK/UHECR rows include the explicit half/half compound allocation; no competing source mass is added.',
              'Overlap-only rows need whole-question coverage or explicitly approved normalized overlaps; they do not inherit weight 1 by this policy.',
              'Several distinct broad or fine homes require canonical reconciliation or an explicit choice. Common-target grouping is not equivalence, and no ancestor plus descendant receive duplicate direct mass.',
              'Annotation-only flags are not scientific rejection. Exact admitted repairs are already applied; unresolved severed notes or premise-dependent wording stay a concrete bounded decision rather than triggering blanket paper rereading.',
              'A contextual or inherited positive role does not justify a home: the linear KK source keeps its admitted linear-cosmology home and receives no production allocation.',
              'All pending rows remain outside accepted H until explicit coordinator policy and exact scope/row bindings are recorded. The 43 reserved sources remain unallocated until the separate post-test amendment.'
          ],
          'remainingDecisionWorkflow': 'Resolve each listed exact scientific choice using its complete source description, existing paired notes and already reviewed scope definitions. Inspect new primary text only when those records leave a material premise or scope ambiguity. Reuse retained meaningful broader scopes instead of forcing the narrowest home; create no generic fallback.',
          'homesAdmittedByThisProposal': 0, 'newModelCalls': 0, 'runningScreenInputsChanged': False,
          'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
print(json.dumps({'proposal': save(B / 'placement-policy-proposal.json', report, True), 'examples': examples_pin, 'counts': counts}, indent=2))
