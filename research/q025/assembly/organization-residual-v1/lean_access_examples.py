"""Amend the mistaken first-witness example selection without changing certificates."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
old,op=read(B/'access-examples.json'); proposal,pp=read(B/'access-proposal.json'); certificates,cp=read(B/'access-certificates.local.json');p,ap=read(B.parent/'organization-v4/candidate-v1/aggregate.local.json')
ds={d['id']:d for d in p['destinations']}
def definition(d):return {k:d[k] for k in ('id','kind','title','question','summary','scope','readingCoverage','scopeContentSha256') if k in d}
def support(s):
    h,c=s['placement'],s['contribution'];hd,cd=s['placementDecision'],s['contributionDecision']
    agreement=cd.get('readingAgreement',{})
    return {'unitId':s['unitId'],'homeDecisionId':h['decisionId'],'homeWeight':h['allocationWeight'],'homeQualification':h.get('qualification'),
            'contributionDecisionId':c['decisionId'],'role':c['role'],'basis':c['basis'],'contributionQualification':c.get('qualification'),
            'proposalNote':agreement.get('proposalNote'),'challengeNote':agreement.get('challengeNote'),
            'sourceEvidenceAgreement':cd.get('challengerAgreement'),'exactEvidenceCount':len(c['evidenceRefs'])}
def lean(x):return {'routeId':x['routeId'],'certificateSha256':x['certificateSha256'],'sourceScope':x['sourceScope'],'targetScope':x['targetScope'],'sourceQuestion':x['sourceQuestion'],'support':support(x['exactSupport']),'routeWitnessCount':x['routeWitnessCount']}
result=[]
for x in old['examples']:
    if x['case']=='region_target_exception':
        r=next(r for r in certificates['routes'] if r['source']=='q025-candidate-region:88fa8687d2ded4f0a4462ab0' and r['target']=='q025-candidate-region:953776ce2227c9ba181efcad')
        assert r['targetKind']=='region' and len(r['supports'])==1
        y={'case':x['case'],'interpretation':x['interpretation'],'routeId':r['id'],'certificateSha256':r['certificateSha256'],'sourceScope':definition(ds[r['source']]),'targetScope':definition(ds[r['target']]),'sourceQuestion':x['sourceQuestion'],'support':support(r['supports'][0]),'routeWitnessCount':1}
        assert y['sourceQuestion']['unitId']==y['support']['unitId'];result.append(y)
    elif 'routes' in x:result.append({'case':x['case'],'interpretation':x['interpretation'],'routes':[lean(r) for r in x['routes']]})
    elif 'exactSupport' in x:result.append({'case':x['case'],'interpretation':x['interpretation'],**lean(x)})
    else:
        r=x['excludedContribution'];cd=x['contributionDecision'];a=cd.get('readingAgreement',{})
        result.append({k:x[k] for k in ('case','sourceScope','targetScope','sourceQuestion','interpretation','thisUnitExcludedFromTargetRoute')}|{'excludedSupport':{'role':r['role'],'decisionId':r['decisionId'],'basis':r['basis'],'qualification':r.get('qualification'),'proposalNote':a.get('proposalNote'),'challengeNote':a.get('challengeNote')}})
payload={'schemaVersion':'q025-access-examples/2','status':'example_selection_amendment_no_certificate_or_policy_change','supersedesExampleFile':op,'originalProposal':pp,'unchangedCertificates':cp,'aggregate':ap,
         'correction':'The v1 region-target example selected the first target for a multiply-contributing source and displayed question55f48142. This version selects the exact region88fa8687→region953776ce certificate. The1,042 certificates and1,041question/1region target census are unchanged.','examples':result}
out=B/'access-examples-v2.json';out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
pin=read(out)[1]
lines=['# Six exact organizational-access contrasts','',payload['correction'],'']
def show(x):
    lines.extend([f"Source ({x['sourceQuestion']['paperId']}): {x['sourceQuestion']['description']}",''])
    for key in ('sourceScope','targetScope'):
        d=x[key];lines.extend([f"{key}: **{d['title']}** ({d['kind']}; `{d['id']}`).",d['question'],d['summary'],''])
        for field,values in d['scope'].items():
            if values:lines.append(f"{field}: "+'; '.join(values))
        lines.extend(['','Reading limits: '+d.get('readingCoverage',{}).get('readingLimit',''),''])
    a=x['support'];lines.extend([f"Exact role **{a['role']}**; allocation `{a['homeDecisionId']}`; contribution `{a['contributionDecisionId']}`.",'Home qualification: '+str(a['homeQualification']),'Contribution qualification: '+str(a['contributionQualification'])])
    for key in ('proposalNote','challengeNote'):
        if a[key]:lines.append(key+': '+a[key])
    lines.append('')
for i,x in enumerate(result):
    lines += [f"## {i+1}. {x['case']}",'',x['interpretation'],'']
    if 'routes' in x:
        for r in x['routes']:show(r)
    elif 'support' in x:show(x)
    else:
        lines += [f"Source ({x['sourceQuestion']['paperId']}): {x['sourceQuestion']['description']}",f"Home: {x['sourceScope']['title']}. Excluded target: {x['targetScope']['title']}.",json.dumps(x['excludedSupport'],ensure_ascii=False),'']
lines += ['Full exact definitions for every case, including the negative method target, remain in the lean JSON. All source locators and native receipt metadata remain in the unchanged certificate payload.',f"Lean example SHA-256: `{pin['sha256']}`."]
(B/'ACCESS-EXAMPLES-v2.md').write_text('\n'.join(lines)+'\n');print(json.dumps(pin));print(out.stat().st_size)
