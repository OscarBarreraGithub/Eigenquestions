"""Lossless scientific view of selected cut03 exceptions for root's parallel review."""
import json,hashlib,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
p=W/'research/q025/assembly/placement-incremental-v1/cut-03/exception-intake.json';sp=W/'research/q025/assembly/placement-latent-lookup-v1/supplement.json'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=lambda p:{'path':str(p.relative_to(W)),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(p)=='e2c8feedca7ab901585b3a3f046fa6900d1fb60eec30b2dd8f668d09a2d15a7b'
d=read(p);supp=read(sp)
def scope(x):return{k:x[k]for k in ['ref','id','kind','title','question','summary','scope','methods','readingCoverage','readingLimit','scientificStatus','scopeContentSha256']if k in x}
def row(r):
 out={k:r[k]for k in ['familyId','unitRef','unitId','paperId','description','descriptionSha256','proposalJudgment','challengeJudgment','independentPriorPlacementReview','proposalAttributions','challengeAttributions','exceptionReasons','inputs']}
 out['homes']=[{k:v for k,v in h.items()if k!='definition'}|({'definition':scope(h['definition'])}if'definition'in h else{})for h in r['homes']]
 packet=read((W/r['inputs']['challenge']['path']).with_name('packet.actual.json'))
 refs=set(re.findall(r'\bq\d+\b',json.dumps(out,ensure_ascii=False)))
 out['completeReferencedScopes']=[scope(x)for x in packet['scopes']if x['ref']in refs]
 return out
changed=[row(r)for r in d['rows']if r['challengeJudgment']['status']=='existing_homes'];new=[]
for i,n in enumerate(d['newScopes']):
 if n['stage']!='challenge' or not n['currentSelectedSourceCount']:continue
 lat=next(x for x in supp['rows']if x['familyId']==n['familyId']and x['localRef']==n['localRef']and x['stage']==n['stage'])
 sourceRows=[row(r)for r in n['sources']]
 proposal=read(W/n['inputs']['proposal']['path']);prior=[x for x in proposal['newScopes']if x['id']==n['definition'].get('revisesRef')]
 new.append({'index':i,'familyId':n['familyId'],'localRef':n['localRef'],'definition':n['definition'],'definitionSha256':n['definitionSha256'],'revisedOriginalDefinitions':prior,'independentAssessment':n['independentAssessment'],'sources':sourceRows,'inputs':n['inputs'],'globalContrasts':[{'id':c['id'],'definition':scope(c['definition']),'sharedSourceUnitIds':c['sharedSourceUnitIds']}for c in n['globalExistingScopeLookup']['candidates']],'latentContrasts':[{'destinationId':c['destinationId'],'status':c['status'],'definition':scope(c['definition'])}for c in lat['candidates']]})
assert len(changed)==12 and len(new)==4
out=F/'native-local/placement-scope-review-v4/root-exceptions.json';out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'input':pin(p),'latentInput':pin(sp),'changedExistingHomes':changed,'challengerAuthoredScopes':new,'readingBasis':'Complete supplied scientific content and existing paired judgments; no new primary reading. Repeated evidence ID arrays and mechanical provenance are omitted only from this view; exact originals remain pinned.','noAdmission':True},ensure_ascii=False,indent=2)+'\n')
idx={'packet':pin(out),'counts':{'changedExistingHomes':12,'selectedChallengerOnlyScopes':4},'sourceInput':pin(p),'latentInput':pin(sp),'freshPrimaryReading':False};(B/'root-exception-index.json').write_text(json.dumps(idx,indent=2)+'\n');print(json.dumps(idx))
