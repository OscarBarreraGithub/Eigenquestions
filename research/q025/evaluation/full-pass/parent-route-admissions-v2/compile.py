"""Root-authorized legacy parent reassertions, explicitly coordinator-admitted."""
import collections,hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
vh=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 cp=F/'native-local/parent-route-admissions-v2/class-candidates.json';c=read(cp);sp=F/'admissions-v5/supported-scope-role-component-v5.json';ds={d['id']:d for d in read(sp)['destinations']+read(F/'parent-scope-admission-v2/component.json')['destinations']};hmap={d['id']:d['scopeContentSha256']for d in ds.values()};type_map={'narrows':'narrower','related':'related_question','comparison':'comparison','premise_check':'premise_check'};groups=collections.defaultdict(list)
 for r in c['candidateRows']:
  assert r['sourceId']in ds and r['targetId']in ds and r['nativeType']in type_map
  groups[(r['sourceId'],r['targetId'],r['nativeType'])].append(r)
 review_registry={};links=[];proofs=[];allobs=[]
 for (source,target,t),observations in sorted(groups.items()):
  observations.sort(key=lambda r:r['id']);r=observations[0];short=vh([source,target,t])[:24];rid='navigation:parent-reasserted:'+short;refs=[];reviewids=[];obs=[]
  for o in observations:
   pins=o['originalCandidate']['reviewPins'];thisids=[]
   for stage in ['proposal','challenge']:
    p=pins[stage];jd=E/p['artifactDirectory'];reply=jd/'reply.json';receipt=jd/'receipt.json';assert sha(reply)==p['reply.jsonSha256'];assert sha(receipt)==p['receipt.jsonSha256'];key='parent-native:'+stage+':'+sha(reply)[:24]
    rec={'id':key,**pin(reply),'receiptPath':str(receipt.relative_to(W)),'receiptSha256':sha(receipt),'kind':'independent_final_parent_'+stage,'originalContract':pin(F/'parents-wave-v1/INSTRUCTIONS.md')};review_registry[key]=rec;thisids.append(key);reviewids.append(key)
   assert len(set(thisids))==2
   meta={'candidateId':o['id'],'sourceReviewIds':thisids,'originalNativeType':t,'challengeReason':o['currentReason'],'priorStatements':[{'reason':x['priorReason'],'evidenceRefs':x['priorRefs']}for x in o['comparisons']],'challengeEvidenceRefs':o['comparisons'][0]['challengeRefs'],'reviewPins':pins,'noExplicitLinkReviewsFieldClaimed':True};obs.append(meta);allobs.append({'candidateId':o['id'],'compiledRelationId':rid,'sourceReviewIds':thisids})
   for comparison in o['comparisons']:
    for ev in comparison['priorRefs']+comparison['challengeRefs']:
     item={'localRef':ev['ref'],**{k:v for k,v in ev.items()if k!='ref'}}
     if item not in refs:refs.append(item)
  reasons=[]
  for o in observations:
   for reason in [x['priorReason']for x in o['comparisons']]+[o['currentReason']]:
    if reason!=r['currentReason']and reason not in reasons:reasons.append(reason)
  # Representative IDs identify existing supporting scope records only. Their
  # source descriptions/pages were not reread by this deterministic compiler.
  evid=sorted(set(ds[source]['evidenceIds']+ds[target]['evidenceIds']));assert evid
  link={'id':rid,'source':source,'target':target,'type':type_map[t],'title':ds[target]['title'],'rationale':r['currentReason'],'qualification':(('\n'.join(reasons)or r['currentReason'])+(' This navigation check applies only to the stated source-specific inference or construction; it is not a premise of every model in the broader source scope.'if t=='premise_check'else'')),'evidenceIds':evid,'evidenceRefs':refs,'decisionId':'decision:parent-reasserted:'+short,'provenance':{'sourceEvidenceAgreement':'independently_reauthored_under_original_parent_contract','observations':obs,'evidenceIdBasis':'inherited_admitted_endpoint_scope_support','inheritedEvidenceIsNotFreshReading':True,'titleReadingDirection':'outgoing_only','nativeType':t,'noNewerLinkReviewsClaim':True,'coordinatorTypeMap':type_map[t]}}
  reviewids=sorted(set(reviewids));links.append(link);proofs.append({'id':link['decisionId'],'type':'navigation','status':'accepted','subjectIds':[source,target],'relationUse':'public_navigation','relationType':link['type'],'navigationContentSha256':vh({k:v for k,v in link.items()if k not in ['decisionId','provenance']}),'sourceScopeContentSha256':hmap[source],'targetScopeContentSha256':hmap[target],'challengerAgreement':'coordinator_adjudicated_navigation','sourceEvidenceAgreement':'independently_reauthored_under_original_parent_contract','sourceReviewIds':reviewids,'evidenceRefs':refs,'observationIds':[o['id']for o in observations]})
 assert len(allobs)==49 and len(links)==48
 authorization={'schemaVersion':'q025-parent-reassertion-class-authorization/1','authority':'root','decision':'Approve exactly 43 source-local premise checks after reading all paired rationales and seven endpoint examples/counterexamples; add six previously excluded conservative parent arcs whose62 endpoint now has its prior explicit scope admission. Both are separate root-authorized coordinator class decisions, not invented per-link verdicts or universal premises.','inputs':{'classProposal':pin(F/'parent-route-admissions-v1/class-proposal.json'),'coordinatorIntake':pin(F/'native-local/parent-route-admissions-v1/direction-intake.json'),'candidateInventory':pin(cp),'admittedScopes':pin(sp),'previouslyAdjudicatedParent':pin(F/'parent-scope-admission-v2/component.json')},'typeMap':type_map,'counts':{'independentObservations':len(allobs),'scientificArcs':len(links),'nativeObservationTypes':dict(collections.Counter(o['nativeType']for o in c['candidateRows'])),'scientificArcTypes':dict(collections.Counter(r['type']for r in links))},'requiredLimits':['Both complete scoped rationales, citation metadata and pinned independent artifacts remain attached.','No newer explicit linkReviews field is invented.','Incomplete/provenance-only, unadmitted endpoint, changed endpoint/type and unapproved direction-sensitive types remain held.','Public outgoing title is exact admitted target title; no reverse action title is invented.','Global canonical remapping requires a fresh exact scope/type binding and containment DAG revalidation.','Repeated observations do not duplicate scientific assertions or source mass.'],'navigationHashes':{p['id']:p['navigationContentSha256']for p in proofs},'newPrimaryReading':False,'sourceRolesHomesAliasesAdded':False};rp=B/'class-admission.json';dump(rp,authorization)
 for p in proofs:p['adjudication']={'status':'accepted_explicit_navigation','receipt':pin(rp)};p['coordinatorAdmissionReceipt']=pin(rp)
 component={'schemaVersion':'q025-parent-reasserted-navigation-component/1','destinations':[],'relations':links,'decisions':proofs,'reviewRegistry':list(review_registry.values()),'sourceContributions':[],'placements':[],'aliases':[],'typedCanonicalOperations':[],'canonicalGroupCandidates':[],'completeLocalPairConstraints':[],'scopeInputs':[pin(sp),pin(F/'parent-scope-admission-v2/component.json')],'admissionReceipt':pin(rp),'sourceObservationLedger':allobs,'fullAtlasAdmission':False};out=F/'native-local/parent-route-admissions-v2/admitted-component.json';dump(out,component);report={'component':pin(out),'componentBytes':out.stat().st_size,'receipt':pin(rp),'counts':authorization['counts'],'reviewArtifactCount':len(review_registry),'unadmittedDirectionSensitiveRowsInPreparedOrientationDraft':491,'compiler':pin(Path(__file__)),'noAutomaticAliasesHomesOrMass':True};dump(B/'admission-report.json',report);print(json.dumps(report))
if __name__=='__main__':main()
