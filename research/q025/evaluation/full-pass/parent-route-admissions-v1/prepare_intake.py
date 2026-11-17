"""Reviewable old-contract class, without admitting any route."""
import json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
cp=F/'native-local/parent-route-admissions-v1/class-candidates.json';c=json.loads(cp.read_text());rawp=F/'native-local/parent-route-admissions-v1/route-audit.json';raw=json.loads(rawp.read_text());sp=F/'admissions-v5/supported-scope-role-component-v5.json';ds={x['id']:x for x in json.loads(sp.read_text())['destinations']};rs={r['id']:r for r in c['candidateRows']};allrs={r['id']:r for r in raw['rows']}
paths=[['successor2-parent-5eef7911f1a80cb73c18-challenge:link:10','successor2-parent-5eef7911f1a80cb73c18-challenge:link:24','successor-parent-17324a9d1c6d231abdd8-challenge:link:30','parent-ae4cdd4e0e8516e33bac-challenge:link:24'],['parent-ae3ac5701d07a07d14d4-challenge:link:0','successor-parent-b7f81485b7d06aed5b64-challenge:link:15','successor-parent-e216581a59d87c4cff7a-challenge:link:17','successor-parent-73840db6800ed57ab471-challenge:link:19']]
heldids=['parent-00602c541f9d268ad95f-challenge:link:16','parent-00602c541f9d268ad95f-challenge:link:27','parent-00602c541f9d268ad95f-challenge:link:25','parent-032f4f1eb9d78a11728b-challenge:link:21']
held=[allrs[i]for i in heldids if i in allrs]
if len(held)<4:held.extend(r for r in raw['rows']if r['nativeType']=='broadens')
def compact(r):return {k:r[k]for k in ['id','sourceId','targetId','sourceTitle','targetTitle','nativeType','class','currentReason','comparisons']}|{'reviewPins':r['originalCandidate']['reviewPins']}
examples=[rs[i]for i in c['report']['representativeCandidateIds']]
journeys=[]
for pp in paths:
 rows=[rs[i]for i in pp]
 assert all(a['targetId']==b['sourceId']for a,b in zip(rows,rows[1:]))
 journeys.append({'routeIds':pp,'destinationIds':[rows[0]['sourceId']]+[r['targetId']for r in rows],'titles':[rows[0]['sourceTitle']]+[r['targetTitle']for r in rows],'routes':[compact(r)for r in rows],'status':'candidate_not_admitted'})
selected={r[k]for r in examples+held+[rs[i]for pp in paths for i in pp]for k in ['sourceId','targetId']if r[k]in ds}
intake={'schemaVersion':'q025-parent-route-coordinator-intake/1','classProposal':pin(B/'class-proposal.json'),'candidateInventory':pin(cp),'scopeComponent':pin(sp),'fullEndpointDefinitions':[ds[i]for i in sorted(selected)],'representativeRoutes':[compact(r)for r in examples],'directionSensitiveCounterexamples':[compact(r)for r in held],'candidateJourneys':journeys,'authorityRequested':'A coordinator class based on independent final scoped reassertion under the original parent contract, not invented per-link supported_as_written judgments.','readingBasis':'Existing full scope definitions and both independently authored route statements/citations; no new primary reading.','admission':False}
op=F/'native-local/parent-route-admissions-v1/coordinator-intake.json';dump(op,intake);report={'intake':pin(op),'bytes':op.stat().st_size,'counts':{'candidateRows':len(c['candidateRows']),'exactFullExamples':len(examples),'candidateJourneys':len(journeys),'directionCounterexamples':len(held),'endpointDefinitions':len(selected)},'scopeSubsettingExample':'The quintessence/background-inference route was checked against both complete definitions: source includes source-specific canonical/interacting/noncanonical histories; target selects canonical/interacting/scalar-tensor history and inference without microscopic or current-fit promotion.','compilerProposal':{'publicTypes':c['report']['proposedTypeMap'],'status':'awaiting_coordinator_class_authorization','preserve':['both complete rationales and exact citation metadata','both pinned review artifacts','exact admitted endpoint scope hashes','original native type','original batch provenance in separate ledger'],'title':'exact admitted target title; outgoing only','qualification':'source-specific conditions and both endpoint reading limits remain attached; no new result or universal transfer','excluded':c['report']['strictExclusions'],'deduplication':'Repeated identical source/target/type observations remain separate receipt observations; no extra mass or equivalence.','identity':'No aliases or containment from shared-source identity; global canonical remapping requires separate whole-group admission.'}}
dump(B/'coordinator-intake-index.json',report);print(json.dumps(report))
