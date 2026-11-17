"""Bounded family-grouped placement inputs for the existing native runner."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];F=ROOT/'research/q025/evaluation/full-pass';OUT=B/'pilot-inputs'
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
registry,rpin=read(F/'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json');lanes,lpin=read(B/'refreshed-lanes.local.json');component,cpin=read(F/'admissions-v4/supported-scope-role-component-v4.json');eligible,epin=read(F/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json')
scopes={d['id']:d for d in component['destinations']};records={r['recordId']:r for r in registry['records']};reviews={r['reviewId']:r for r in registry['reviews']};contexts=collections.defaultdict(list)
for a in registry['unitAssessments']:contexts[a['unitId']].append(a)
units={};manifest=json.loads((ROOT/'data/navigation/manifest.json').read_text())
needed=set(lanes['remainingRows'])
for d in manifest['files']['units']:
    raw=(ROOT/'data/navigation'/d['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==d['sha256']
    for u in json.loads(raw):
        if u['id'] in needed:units[u['id']]=u
assert needed<=set(eligible['unitIds']) and len(needed)==2400
groups=collections.defaultdict(lambda:collections.defaultdict(set));buckets={}
for uid,rs in lanes['remainingRows'].items():
    clean=[x for x in rs if not x['exclusionReasons']];h={x['destinationId'] for x in clean};pa=[x for x in rs if x['homeAgreement']['sameExplicitScientificCard'] and x['homeAgreement']['proposalDefinitionMatchesPinnedOriginal'] and x['chosenHomeAgreedRoles'] and x['destinationId']]
    kind='coverage' if len(h)==1 else 'competing' if len(h)>1 else 'annotation' if pa and all(set(x['exclusionReasons'])<={'unresolved_unit_annotation_screen'} for x in pa) else 'other' if pa else 'absent';buckets[uid]=kind
    for rid in {x['reviewId'] for x in rs}:
        rec=records.get(rid+':r')
        if rec:groups[kind][rec['definition']['title']].add(uid)
selection={
 'annotation':['Flux compactifications, orientifolds and quantum flux consistency','String cosmological dynamics and their limits','Kähler stabilization, inflation and related cosmological constraints','AdS compactifications: scale hierarchies, control and holographic tests','String limits, light spectra and control of gravitational effective theories','Compactification geometry, gauge sectors and consistency'],
 'coverage':['Axion scales, inflation and neighboring cosmology'],
 'competing':['Inflationary models, gravitational structure and consistency tests','String cosmology: dynamics, effective descriptions and empirical access','String-inspired cosmology: running vacuum and neighboring mechanisms','Inflationary dynamics, cosmic relics and gravitational-wave signatures','De Sitter entropy, quantum descriptions and observer access'],
 'absent':['Charged black holes: retention, discharge and extremality'],
}
OUT.mkdir(exist_ok=True);index=[]
for kind,families in selection.items():
    chosen=[]
    for family in families:
        for uid in sorted(groups[kind].get(family,())):
            if uid not in chosen:chosen.append(uid)
            if len(chosen)>=24:break
        if len(chosen)>=24:break
    assert chosen
    # Every proposed home/contribution target from every old assessment remains
    # available, including competing targets outside the packet's main family.
    target_ids=set();mapping={}
    for uid in chosen:
        options=set()
        for x in lanes['remainingRows'][uid]:
            if x['destinationId'] in scopes:options.add(x['destinationId'])
            broad=records.get(x['reviewId']+':r')
            if broad and broad['candidateId'] in scopes:options.add(broad['candidateId'])
        for a in contexts[uid]:
            for q in a['questionContributions']:
                r=records.get(q['recordId'])
                if r and r['candidateId'] in scopes:options.add(r['candidateId'])
        mapping[uid]=options;target_ids|=options
    qrefs={id:'q'+str(i) for i,id in enumerate(sorted(target_ids))};refs={q:{'kind':'admitted_scope','destinationId':id,'scopeContentSha256':scopes[id]['scopeContentSha256']} for id,q in qrefs.items()};rows=[];bindings=[]
    for i,uid in enumerate(chosen):
        u=units[uid];assert hashlib.sha256(u['text'].encode()).hexdigest()==u['evidence']['textSha256'];ref='u'+str(i);refs[ref]={'kind':'source_question','unitId':uid,'paperId':u['paperId'],'descriptionSha256':u['evidence']['textSha256']}
        old=[];now=[];source_pins=[]
        for a in contexts[uid]:
            rv=reviews[a['reviewId']];resolved=[]
            for q in a['questionContributions']:
                r=records.get(q['recordId'])
                if r and r['candidateId'] in qrefs:resolved.append({'scopeRef':qrefs[r['candidateId']],'role':q['role'],'independentRoleAgreement':q['independentRoleAgreement']})
            common={'reviewId':a['reviewId'],'sourceOrigin':a['sourceOrigin'],'resolvedTypedContributions':resolved,'homeAgreement':a['homeAgreement']};old.append({**common,'original':a['proposalAttribution']});now.append({**common,'original':a['challengeAttribution']});source_pins.append({'reviewId':rv['reviewId'],'pins':rv['pins'],'proposalDependency':rv['proposalDependency'],'challengeArtifact':rv['challengeArtifact']})
        rows.append({'ref':ref,'unitId':uid,'paperId':u['paperId'],'description':u['text'],'descriptionSha256':u['evidence']['textSha256'],'proposalAttributions':old,'challengeAttributions':now,'candidateHomeRefs':[qrefs[id] for id in sorted(mapping[uid])],'existingHomeRefs':[],'coverageIssue':{'bucket':kind,'priorCensus':lanes['remainingRows'][uid]},'originalSourceQuestionMustRemainWhole':True})
        bindings.append({'unitRef':ref,'unitId':uid,'browserVectorRow':u['vectorRow'],'textSha256':u['evidence']['textSha256'],'reviewContexts':source_pins})
    family_id='placement-pilot-'+kind
    payload={'schemaVersion':'q025-placement-decision-input/1','familyId':family_id,'units':rows,'scopes':[{'ref':qrefs[id],'id':id,'scopeContentSha256':scopes[id]['scopeContentSha256'],'destination':scopes[id]} for id in sorted(target_ids)],'refRegistry':refs,'machineBindings':{'registry':rpin,'scopeComponent':cpin,'residualInventory':lpin,'eligibleInventory':epin,'units':bindings},'readingLimits':['Complete source descriptions, both exact prior per-unit annotations and all already-admitted candidate target definitions are supplied.','Old primary-reading references are inherited evidence only; primary page text is not supplied in this decision pass. Do not claim to reread it. Identify any consequential missing premise explicitly before requesting bounded primary context.','Choose the most specific existing scope covering the WHOLE original question. A compound source remains whole; normalized multiple homes require explicit complete target coverage. No atomic source split, default numerical bin, alias, new role or scientific route is admitted by this output.','Existing reviewed scope definitions must not be silently rewritten. A truly missing scope is a separate proposal, with unresolved source coverage retained.','Historical/truncated annotations remain exact. Do not guess missing words; distinguish whether the missing wording materially affects placement.'],'selection':{'bucket':kind,'scientificFamilies':families,'unitCount':len(rows),'allOtherResidualUnitsRemainPending':2400-len(rows),'noSealedSourceText':True}}
    p=OUT/(family_id+'.json');p.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');index.append({**read(p)[1],'familyId':family_id,'units':len(rows),'scopes':len(target_ids),'scientificFamilies':families})
report={'schemaVersion':'q025-placement-pilot-source-index/1','status':'prepared_sources_only_no_native_requests_launched','packets':index,'distinctSources':len({u for kind,fs in selection.items() for u in []}),'readingPolicy':'No fresh primary reread; exact descriptions, both old notes and full admitted scopes. Existing native runner/contract owned by evaluation.','scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};report['distinctSources']=sum(p['units'] for p in index);(B/'placement-pilot-index.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
