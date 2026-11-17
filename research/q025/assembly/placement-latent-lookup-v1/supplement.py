#!/usr/bin/env python3
"""Bounded joins of existing neighbor rows to admitted/pending scoped targets.

No encoding, graph rebuild, source-text extraction, or scientific admission.
Sealed IDs are excluded before neighbor-to-scope joins; no sealed text is read.
"""
import gzip, hashlib, json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
A = ROOT / 'research/q025/assembly'
G = ROOT / 'research/q025/geometry/identity-neighbors'
E = ROOT / 'research/q025/evaluation/full-pass'

def pin(path):
    raw = path.read_bytes()
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(raw).hexdigest(), 'bytes':len(raw)}

def read(path, expected=None):
    p = pin(path)
    if expected and p['sha256'] != expected: raise ValueError(f'Changed pinned input {path}')
    return json.loads(path.read_text()), p

def save(name, value):
    path = HERE / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    return pin(path)

manifest, mp = read(G/'manifest.json')
units, up = read(G/'units.json', manifest['unitTable']['sha256'])
eligible, ep = read(E/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json')
allowed = set(eligible['unitIds'])
row_by_id = {u['unitId']:u for u in units['rows']}
assert len(row_by_id) == 8473 and len(allowed) == 8430
neighbors = {}; neighbor_pins = {}
for name, desc in manifest['exports'].items():
    path = G/desc['path']; p = pin(path)
    assert p['sha256'] == desc['sha256']
    data = json.loads(gzip.decompress(path.read_bytes()))
    assert data['unitIdOrderSha256'] == units['unitIdOrderSha256']
    neighbors[name] = data['rows']; neighbor_pins[name] = p

base, bp = read(A/'placement-incremental-v1/cut-01/candidate-6294/aggregate.local.json',
                'e9bb797bb6595e24e42191e8ea20112bdc619dc326ff62efc61cbcaa9bb54d75')
scope_component, sp = read(E/'placement-scope-review-v1/scope-component.json',
                          '1d297c1ef3eece0e34019672b78c4acfd036ee11e3a0c9891fc257e3651f8a4d')
mapping, map_pin = read(E/'placement-scope-review-v1/scope-mapping.json',
                       'e4315bce0cf151d5e055e30f108b2ad8e2445362baa3c089100eb17a87da0f90')
scopes = {d['id']:d for d in base['destinations'] + scope_component['destinations']}
aliases = {m:g['destinationId'] for g in base['identityResolution']['canonicalGroups'] for m in g['memberIds']}
scope_pins = {d['id']:bp for d in base['destinations']}
scope_pins.update({d['id']:sp for d in scope_component['destinations']})
placement_inputs = []
placements = list(base['placements'])
for name in ['cut-02/admitted/component.json','new-scope-cut-01/component.json','cut-03/admitted/component.json']:
    c,p = read(A/'placement-incremental-v1'/name); placement_inputs.append(p); placements.extend(c['placements'])
supports = defaultdict(lambda:defaultdict(list))
for p in placements:
    if p['unitId'] in allowed:
        supports[p['unitId']][aliases.get(p['destinationId'],p['destinationId'])].append({'basis':'admitted_direct_home','decisionId':p['decisionId']})
for r in base['sourceContributions']:
    if r['unitId'] in allowed and r['role'] in ['addresses','instantiates','specializes']:
        supports[r['unitId']][aliases.get(r['destinationId'],r['destinationId'])].append({'basis':'admitted_positive_target_role','role':r['role'],'decisionId':r['decisionId'],'qualification':r.get('qualification')})

new_scopes=[]; intake_pins=[]
admitted_by_local={(r['familyId'],r['localRef']):r for r in mapping['rows']}
pending_by_id={}
for cut in ['cut-01','cut-02','cut-03']:
    intake,p = read(A/'placement-incremental-v1'/cut/'exception-intake.json'); intake_pins.append(p)
    for n in intake['newScopes']:
        n={**n,'intakePin':p}
        new_scopes.append(n)
        admitted=admitted_by_local.get((n['familyId'],n['localRef']))
        if admitted:
            assert admitted['nativeDefinitionSha256']==n['definitionSha256']
            continue
        id='pending-placement-scope:'+n['familyId']+':'+n['stage']+':'+n['localRef']
        scopes[id]=n['definition'];scope_pins[id]=p;pending_by_id[id]=n
        for u in n['sources']:
            if u['unitId'] in allowed:
                supports[u['unitId']][id].append({'basis':'pending_new_scope_selected_home','admitted':False})

results=[]
for n in new_scopes:
    admitted=admitted_by_local.get((n['familyId'],n['localRef']))
    own=admitted['destinationId'] if admitted else 'pending-placement-scope:'+n['familyId']+':'+n['stage']+':'+n['localRef']
    witnesses=defaultdict(list);excluded=0; neighbor_count=0
    for source in n['sources']:
        uid=source['unitId'];assert uid in allowed
        row=row_by_id[uid]
        for model,table in neighbors.items():
            entry=table[row['sourceRow']];assert entry['sourceRow']==row['sourceRow']
            for rank,(idx,weight) in enumerate(entry['neighbors'],1):
                neighbor=units['rows'][idx]
                if neighbor['unitId'] not in allowed: excluded+=1;continue
                neighbor_count+=1
                for id,provenance in supports.get(neighbor['unitId'],{}).items():
                    if id==own or id not in scopes: continue
                    # Repeated exact native definition is one nomination, not a new contrast.
                    pn=pending_by_id.get(id)
                    if pn and pn['definitionSha256']==n['definitionSha256']: continue
                    witnesses[id].append({'queryUnitId':uid,'neighborUnitId':neighbor['unitId'],'queryPaperId':row['paperId'],'neighborPaperId':neighbor['paperId'],'model':model,'rank':rank,'affinityWeight':weight,'sourceRow':row['sourceRow'],'neighborSourceRow':idx,'scopeSupport':provenance})
    ranked=[]
    for id,ww in witnesses.items():
        models=sorted({w['model'] for w in ww}); cross=any(w['queryPaperId']!=w['neighborPaperId'] for w in ww)
        score=sum(1/min(w['rank'] for w in ww if w['model']==m) for m in models)
        ranked.append((len(models),score,cross,id,ww))
    ranked.sort(key=lambda r:(-r[0],-r[1],-r[2],r[3]))
    candidates=[]
    for _,score,cross,id,ww in ranked[:8]:
        d=scopes[id]
        candidates.append({'destinationId':id,'status':'pending_scope_proposal_not_admitted' if id in pending_by_id else 'admitted_scope','definition':{k:d[k] for k in ['id','kind','title','question','summary','scope','readingCoverage'] if k in d},'definitionArtifact':scope_pins[id],'scopeContentSha256':d.get('scopeContentSha256'),'models':sorted({w['model'] for w in ww}),'rankingScore':score,'crossPaperWitness':cross,'witnesses':ww})
    results.append({'familyId':n['familyId'],'localRef':n['localRef'],'stage':n['stage'],'nativeDefinitionSha256':n['definitionSha256'],'sourceIntake':n['intakePin'],'currentAdmissionStatus':'admitted_scope' if admitted else 'pending_scope','admittedDestinationId':admitted['destinationId'] if admitted else None,'sourceUnitIds':[s['unitId'] for s in n['sources']],'eligibleNeighborRowsConsidered':neighbor_count,'sealedNeighborRowsExcluded':excluded,'allNominatedScopeCount':len(ranked),'candidateLimit':8,'candidates':candidates})
output=save('supplement.json',{'schemaVersion':'q025-existing-latent-scope-contrasts/1','inputs':{'neighborManifest':mp,'unitTable':up,'eligibleIds':ep,'neighbors':neighbor_pins,'currentAssembly':bp,'newScopeComponent':sp,'newScopeMapping':map_pin,'placementComponents':placement_inputs,'sourceIntakes':intake_pins},'meaning':'Existing MiniLM and Qwen source-affinity top20 neighbors nominate current/pending scope contrasts through exact source homes or positive target-role evidence. These are not new scientific edges, equivalence decisions, or a global-absence test. W is unchanged.','ranking':'First number of encoder views, then sum of reciprocal best source-neighbor rank per view; no cross-encoder numeric weight comparability assumed. Top8 scoped contrasts retained.','rows':results})
report=save('report.json',{'schemaVersion':'q025-existing-latent-scope-contrast-report/1','supplement':output,'definitionCount':len(results),'alreadyAdmittedDefinitions':sum(r['currentAdmissionStatus']=='admitted_scope' for r in results),'withCandidates':sum(bool(r['candidates']) for r in results),'withCrossPaperCandidate':sum(any(c['crossPaperWitness'] for c in r['candidates']) for r in results),'candidateRows':sum(len(r['candidates']) for r in results),'sealedNeighborRowsExcluded':sum(r['sealedNeighborRowsExcluded'] for r in results),'freshEncoding':False,'freshGraphComputation':False,'scientificAdmission':False,'script':pin(Path(__file__))})
print(json.dumps(report))
