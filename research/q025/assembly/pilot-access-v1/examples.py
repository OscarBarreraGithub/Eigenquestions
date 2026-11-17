"""Five exact witnesses for the proposed fine-home organizational access class."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];A=ROOT/'research/q025/assembly'
def read(p):
 raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
p,pp=read(A/'organization-residual-v1/candidate-6030-connected-v4/aggregate.local.json');pilot,pi=read(A/'placement-pilot-review-v1/admitted-v1/component.local.json');c,cp=read(B/'candidate-certificates.local.json');ds={d['id']:d for d in p['destinations']+pilot['destinations']};decisions={d['id']:d for d in p['decisions']+pilot['decisions']};home={h['decisionId']:h for h in p['placements']+pilot['placements']};contrib={r['decisionId']:r for r in p['sourceContributions']};rs=c['routes'];selected=[(121,'Whole GMGHS composite to an emission component; no identification with classical protection'),(184,'Linear cosmology to inherited production context; access must not become a production home'),(183,'Threshold dynamics to a conditional bound sibling; original compound allocation remains normalized'),(170,'A DS/dS-specific question can return to a broader entropy/matter question without identity or a global bound'),(0,'A compound lecture home exposes a positive component while source-era claims remain dated')];needed={rs[i]['witnesses'][0]['unitId']for i,_ in selected};units={};manifest=json.loads((ROOT/'data/navigation/manifest.json').read_text())
for d in manifest['files']['units']:
 raw=(ROOT/'data/navigation'/d['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==d['sha256']
 for u in json.loads(raw):
  if u['id']in needed:units[u['id']]=u
assert set(units)==needed
science=('id','kind','title','question','summary','scope','readingCoverage','scopeContentSha256');examples=[]
for i,meaning in selected:
 r=rs[i];w=r['witnesses'][0];u=units[w['unitId']];observations=[]
 for x in w['observations']:
  cr=contrib[x['contributionDecisionId']];proof=decisions[cr['decisionId']];hp=home[x['homeDecisionId']];hd=decisions[hp['decisionId']];observations.append({'home':hp,'homeDecisionId':hd['id'],'homeScopeSha256':hd['scopeContentSha256'],'placementHash':hd['placementContentSha256'],'contribution':{k:v for k,v in cr.items()if k!='evidenceRefs'},'contributionDecisionId':proof['id'],'contributionScopeSha256':proof['scopeContentSha256'],'contributionHash':proof['contributionContentSha256'],'pairedSourceReading':proof.get('readingAgreement'),'sourceReviewIds':proof['sourceReviewIds'],'sourceEvidenceRefs':cr['evidenceRefs'],'homeAdmission':hd.get('adjudication'),'contributionAdjudication':proof.get('adjudication')})
 examples.append({'case':meaning,'source':r['source'],'target':r['target'],'sourceScope':{k:ds[r['source']][k]for k in science if k in ds[r['source']]},'targetScope':{k:ds[r['target']][k]for k in science if k in ds[r['target']]},'sourceQuestion':{'unitId':u['id'],'paperId':u['paperId'],'description':u['text'],'textSha256':u['evidence']['textSha256']},'completeRouteWitnessCount':len(r['witnesses']),'selectedWitnessObservations':observations,'noImplicationContainmentMassUsingOrEquivalence':True})
out={'schemaVersion':'q025-fine-home-access-examples/1','status':'pending_class_admission','inputs':[pp,pi,cp],'examples':examples,'scope':'Each witness is an exact accepted direct question home plus accepted positive role by the identical source unit. This extends organizational access only; method/boundary/comparison roles remain excluded. All204 candidate route supports remain in the pinned certificate file.'};path=B/'examples.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(read(path)[1])
