"""Measured direction-only packets from existing scoped parent reasoning."""
import json,hashlib,collections,functools
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3];OUT=F/'native-local/orientation-design-v1';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
@functools.cache
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def size(x):return len(json.dumps(x,ensure_ascii=False,separators=(',',':')))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
rawp=F/'native-local/parent-route-admissions-v1/route-audit.json';raw={r['id']:r for r in read(rawp)['rows']};heldp=F/'native-local/parent-route-admissions-v1/class-candidates.json';held=read(heldp)['held'];dirp=F/'native-local/parent-route-admissions-v1/direction-intake.json';reserved=set(read(dirp)['proposedPremiseClass']['candidateIds']);scopep=F/'admissions-v5/supported-scope-role-component-v5.json';ds={d['id']:d for d in read(scopep)['destinations']+read(F/'parent-scope-admission-v2/component.json')['destinations']};rows=[raw[x['id']]for x in held if x['id']not in reserved]
rows.extend(r for r in raw.values()if r['class']=='endpoint_scope_not_admitted' and r['sourceId']in ds and r['targetId']in ds and r['nativeType']in ['method','application','premise_check','broadens'])
# Explicit coordinator premise-class candidates remain outside this draft. No
# assumption of their acceptance is used to admit anything in these packets.
def make(group,num):
 scopeids=sorted({r[k]for r in group for k in ['sourceId','targetId']});refs={cid:f's{i}'for i,cid in enumerate(scopeids)}
 scopes=[{'ref':refs[cid],'kind':ds[cid]['kind'],'title':ds[cid]['title'],'question':ds[cid]['question'],'summary':ds[cid]['summary'],'scope':ds[cid]['scope'],'readingCoverage':ds[cid]['readingCoverage']}for cid in scopeids]
 rels=[];bind={}
 for i,r in enumerate(group):
  ref=f'l{i}';rels.append({'ref':ref,'source':refs[r['sourceId']],'target':refs[r['targetId']],'nativeType':r['nativeType'],'proposalStatements':[x['priorReason']for x in r['comparisons']],'challengeStatement':r['currentReason'],'originalEvidenceKinds':sorted({x['kind']for c in r['comparisons']for x in c['priorRefs']+c['challengeRefs']}),'originalEvidenceProvidedAsText':False});bind[ref]=r
 view={'schemaVersion':'q025-direction-only-source-view/1','familyId':f'parent-orientation-{num:02d}','scopes':scopes,'relations':rels,'readingLimits':['All endpoint definitions and both original independent route statements are supplied unchanged.','Primary citation locators and original review files are pinned in a machine sidecar, but their text is not newly supplied/read.','Choose a scientifically accurate navigation direction/type using this existing reasoning. Do not introduce a new physical condition or transfer a method beyond its stated scope.','A missing substantive premise must be withheld for a targeted evidence check, not guessed.','Rows can be disconnected; packing establishes no scientific relationship between them.']}
 side={'schemaVersion':'q025-direction-only-bindings/1','scopeBindings':{refs[cid]:{'id':cid,'scopeContentSha256':ds[cid]['scopeContentSha256']}for cid in scopeids},'relationBindings':bind,'inputs':{'scopeComponent':pin(scopep),'routeAudit':pin(rawp),'heldCandidates':pin(heldp),'reservedPremiseClassIntake':pin(dirp),'previouslyAdjudicatedParent':pin(F/'parent-scope-admission-v2/component.json')}};return view,side
pending=sorted(rows,key=lambda r:r['id']);groups=[]
while pending:
 group=[pending.pop(0)];known={group[0]['sourceId'],group[0]['targetId']}
 while pending and len(group)<40:
  order=sorted(range(len(pending)),key=lambda i:(-len(known&{pending[i]['sourceId'],pending[i]['targetId']}),pending[i]['id']))
  chosen=None
  for i in order:
   candidate=group+[pending[i]];new=known|{pending[i]['sourceId'],pending[i]['targetId']}
   if len(new)>40:continue
   if size(make(candidate,len(groups))[0])>180000:continue
   chosen=i;break
  if chosen is None:break
  row=pending.pop(chosen);group.append(row);known|={row['sourceId'],row['targetId']}
 groups.append(group)
manifest=[]
for i,g in enumerate(groups):
 view,side=make(g,i);vp=OUT/f'{i:02d}.view.json';sp=OUT/f'{i:02d}.bindings.json';dump(vp,view);dump(sp,side);manifest.append({'id':view['familyId'],'view':pin(vp),'bindings':pin(sp),'scopeCount':len(view['scopes']),'relationCount':len(g),'inputCharacters':size(view),'candidateIds':[r['id']for r in g]})
ids=[i for p in manifest for i in p['candidateIds']];assert len(ids)==len(set(ids))==len(rows);report={'schemaVersion':'q025-direction-adjudication-design/1','status':'prepared_measured_draft_not_native_launch_authorization','candidateCount':len(rows),'reservedPremiseCandidates':len(reserved),'packetCount':len(manifest),'pairedCallCount':len(manifest)*2,'maxInputCharacters':max(p['inputCharacters']for p in manifest),'maxScopes':max(p['scopeCount']for p in manifest),'maxRelations':max(p['relationCount']for p in manifest),'nativeTypes':dict(collections.Counter(r['nativeType']for r in rows)),'families':manifest,'sourceReading':'Complete existing scientific scopes and both independent route rationales; no new primary text or full source-unit attribution reading.','outputContractProposal':'One exact-row decision each: same endpoints or explicit reversal, current type, scoped qualification and outgoing title, or withhold with exact missing premise. Independent challenge explicitly judges every proposed row. No new scopes, identities, homes, roles or physical results.','suggestedInitialMaxActive':4,'futureMaximumNeedsRootCoordination':24};(B/'design-index.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='families'}))
