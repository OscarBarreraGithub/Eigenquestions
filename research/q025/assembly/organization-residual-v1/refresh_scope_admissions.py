"""Apply already-admitted scope status to the still-unallocated home census."""
import collections, copy, hashlib, json, sys
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];F=ROOT/'research/q025/evaluation/full-pass';OLD=B.parent/'organization-v4'
sys.path.insert(0,str(ROOT/'research/q025/geometry/canonical-review-design'))
from reconcile_fine_home_audit import reconcile
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def save(name,v):
    p=B/name;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');return read(p)[1]
census,cpin=read(OLD/'home-lanes-v5.local.json');component,spin=read(F/'admissions-v4/supported-scope-role-component-v4.json');packet,apin=read(OLD/'candidate-v1/aggregate.local.json');registry,rpin=read(F/'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json')
assert spin['sha256']=='98821c0544eb16b26584d65d5838a256bda54c2c65aebe377a834426579274cb'
scopes={d['id']:d for d in component['destinations']};records={r['recordId']:r for r in registry['records']};assessments={(a['reviewId'],a['unitId']):a for a in registry['unitAssessments']};reviews={r['reviewId']:r for r in registry['reviews']};allocated={p['unitId'] for p in packet['placements']};assert len(allocated)==5765
fine=copy.deepcopy(census['fineContextRows']);broad=copy.deepcopy(census['broadContextRows']);changes=[]
for x in fine:
    if x['destinationId'] in scopes:
        x['scopeAlreadyAdmitted']=True
        if 'unresolved_scope_annotation_or_definition_flag' in x['exclusionReasons']:
            d=scopes[x['destinationId']];record=records[d['provenance']['recordId']]
            assert not record['scopeDefinitionFlags']
            changes.append({'unitId':x['unitId'],'reviewId':x['reviewId'],'destinationId':x['destinationId'],'removedDiagnostic':'unresolved_scope_annotation_or_definition_flag','scopeDecisionId':d['scopeDecisionId'],'scopeContentSha256':d['scopeContentSha256'],'retainedHistoricalNoteFlags':record['admissionJustificationFlags'],'reason':'Exact unchanged scientific scope is already admitted; separate review-note flags remain historical, not a stale scope-admission blocker.'})
            x['exclusionReasons']=[v for v in x['exclusionReasons'] if v!='unresolved_scope_annotation_or_definition_flag']
for x in broad:
    if x['destinationId'] in scopes:
        x['flagReasons']=[v for v in x['flagReasons'] if v!='scope_annotation_or_definition'];x['unresolvedFlags']=bool(x['flagReasons']);x['scopeAlreadyAdmitted']=True
new_fine={x['unitId']:x for x in reconcile(fine,allocated) if not x['reviewReasons'] and x['unitId'] not in allocated}
by_broad=collections.defaultdict(list)
for x in broad:
    if x['unitId'] not in allocated and x['unitId'] not in new_fine and x['jointDisposition']=='member' and not x['unresolvedFlags']:by_broad[x['unitId']].append(x)
new_broad={uid:rs for uid,rs in by_broad.items() if len({x['destinationId'] for x in rs})==1 and not any(x['contextLanguage'] for x in rs)}
assert len(new_fine)==142 and len(new_broad)==123
rows=[]
for uid in sorted(set(new_fine)|set(new_broad)):
    if uid in new_fine:
        f=new_fine[uid];did=f['selectedDestinationId'];rids=f['cleanContextReviewIds'];lane='A_exact_paired_scientific_question_home'
    else:
        bs=new_broad[uid];did=bs[0]['destinationId'];rids=sorted({x['reviewId'] for x in bs});compound=any(x['compoundLanguage'] for x in bs) or any('explicit_compound_target_language' in x['coverageReviewReasons'] for x in fine if x['unitId']==uid);lane='B_compound_whole_family_home' if compound else 'B_whole_family_home'
    d=scopes[did];contexts=[]
    for rid in rids:
        a=assessments[(rid,uid)];rv=reviews[rid];contexts.append({'reviewId':rid,'proposal':a['proposalAttribution'],'challenge':a['challengeAttribution'],'homeAgreement':a['homeAgreement'],'pins':rv['pins'],'originalProposal':rv['proposalDependency']})
    rows.append({'unitId':uid,'destinationId':did,'policyClass':lane,'proposedRole':'member','proposedWeight':1,'status':'pending_exact_same_policy_extension','scopeContentSha256':d['scopeContentSha256'],'scopeDecisionId':d['scopeDecisionId'],'sourceReviewIds':rids,'contexts':contexts,'scopeDiagnosticRefresh':[x for x in changes if x['unitId']==uid and x['destinationId']==did],'unitAnnotationFlagsWaived':False,'premiseOrScopeConflictWaived':False})
payload=save('same-policy-candidates.local.json',{'rows':rows,'scopeDiagnosticRefresh':changes,'inputs':[cpin,spin,apin,rpin]})
examples=[];selected=[]
for lane in ['A_exact_paired_scientific_question_home','B_whole_family_home','B_compound_whole_family_home']:
    candidates=[x for x in rows if x['policyClass']==lane];selected.extend(candidates[:2])
for row in selected:
    rid=row['sourceReviewIds'][0];rv=reviews[rid];p,pin=read(ROOT/'research/q025/evaluation'/rv['artifactDirectory']/rv['challengeArtifact']['packetFile']);assert pin['sha256']==rv['pins']['challengePacketSha256'];u=next(x for x in p['units'] if p['refRegistry'][x['descriptionRef']]['unitId']==row['unitId']);assert hashlib.sha256(u['description'].encode()).hexdigest()==p['refRegistry'][u['descriptionRef']]['textSha256'];d=scopes[row['destinationId']]
    examples.append({'source':{'unitId':row['unitId'],'paperId':u['paperId'],'description':u['description'],'descriptionSha256':p['refRegistry'][u['descriptionRef']]['textSha256'],'packet':pin},'candidate':row,'admittedScope':d})
epin=save('same-policy-examples.json',{'examples':examples})
remaining={x['unitId'] for x in registry['unitAssessments']}-allocated-{x['unitId'] for x in rows};by_remaining=collections.defaultdict(list)
for x in fine:
    if x['unitId'] in remaining:by_remaining[x['unitId']].append(x)
counts=collections.Counter()
for uid,rs in by_remaining.items():
    clean=[x for x in rs if not x['exclusionReasons']];homes={x['destinationId'] for x in clean};partial=[x for x in rs if x['homeAgreement']['sameExplicitScientificCard'] and x['homeAgreement']['proposalDefinitionMatchesPinnedOriginal'] and x['chosenHomeAgreedRoles'] and x['destinationId']]
    kind='one_clean_paired_fine_home_coverage_only' if len(homes)==1 else 'multiple_clean_paired_fine_homes' if len(homes)>1 else 'explicit_fine_home_unit_annotation_only' if partial and all(set(x['exclusionReasons'])<={'unresolved_unit_annotation_screen'} for x in partial) else 'explicit_fine_home_other_gap' if partial else 'no_supported_exact_fine_home';counts[kind]+=1
save('refreshed-lanes.local.json',{'fineRows':fine,'broadRows':broad,'remainingRows':by_remaining,'samePolicyUnitIds':sorted(set(new_fine)|set(new_broad))})
report={'schemaVersion':'q025-scope-admission-home-refresh/1','status':'pending_root_exact_row_confirmation','inputs':[cpin,spin,apin,rpin],'candidatePayload':payload,'examples':epin,'counts':{'newFine':142,'newBroad':123,'policyClasses':dict(collections.Counter(x['policyClass'] for x in rows)),'newRows':265,'coverageIfApproved':6030,'remainingEligible':2400,'reserved':43,'remainingBuckets':dict(counts)},'meaning':'Same approved A/B scientific rules, refreshed with current admitted scope status. No unit annotation flag or scientific conflict is waived. Existing exact scope definitions, historical flags and original review notes remain unchanged. These265 rows are not admitted until root confirms their pinned list.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};print(json.dumps(save('same-policy-proposal.json',report),indent=2))
