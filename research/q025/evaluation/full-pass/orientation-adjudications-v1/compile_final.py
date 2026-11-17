"""The two exact final orientation replacements approved by the coordinator."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;W=F.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
vh=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def save(p,x):
 raw=json.dumps(x,ensure_ascii=False,indent=2)+'\n'
 if p.exists():assert p.read_text()==raw
 else:p.write_text(raw)
ip=F/'native-local/orientation-admissions-v1/final-three-exceptions.json';assert sha(ip)=='9a984019527d9d1f2d0dfb19367503eea7611ced93006d18f3d0868198e72645'
cases=read(ip)['items'];todo=[c for c in cases if c['status']=='replacement_needs_coordinator'];assert len(todo)==2
basep=F/'admissions-v5/supported-scope-role-component-v5.json';ds={d['id']:d for d in read(basep)['destinations']};relations=[];proofs=[]
native=read(F/'orientation-admissions-v1/parent-orientation-05-component.json');reviews=native['reviewRegistry']
for case in todo:
 e=case['effective'];assert e['id']in ['d40','d41'] and e['status']=='route'
 refsmap=case['scopeBindings'];source=refsmap[e['source']]['id'];target=refsmap[e['target']]['id']
 for s in case['completeScopes']:
  d=ds[refsmap[s['ref']]['id']];assert d['scopeContentSha256']==refsmap[s['ref']]['scopeContentSha256']
  for k in ['kind','title','question','summary','scope','readingCoverage']:assert d[k]==s[k]
 short='parent-orientation-05:'+e['originalRef'];refs=[{'kind':'admitted_scope_definition','candidateId':x,'scopeContentSha256':ds[x]['scopeContentSha256']}for x in [source,target]]
 row={'id':'navigation:orientation-adjudicated:'+short,'source':source,'target':target,**{k:e[k]for k in ['type','title','rationale','qualification']},'evidenceIds':sorted(set(ds[source]['evidenceIds']+ds[target]['evidenceIds'])),'evidenceRefs':refs,'decisionId':'decision:orientation-adjudicated:'+short,'provenance':{'coordinatorBasis':'root_read_complete_two_replacements_four_endpoint_definitions_both_judgments_original_statements','originalCandidateId':case['originalCandidateId'],'originalProposal':case['proposal'],'challengeAssessment':case['challengeAssessment'],'exactChallengerReplacement':e,'originalStatements':case['originalRoute'],'freshPrimaryReading':False,'pairedFinalRowAgreement':False,'titleReadingDirection':'outgoing_only','inheritedEndpointReadingCoverage':{i:ds[i]['readingCoverage']for i in [source,target]}}};relations.append(row)
 proofs.append({'id':row['decisionId'],'type':'navigation','status':'accepted','subjectIds':[source,target],'relationUse':'public_navigation','relationType':row['type'],'navigationContentSha256':vh({k:v for k,v in row.items()if k not in ['decisionId','provenance']}),'sourceScopeContentSha256':ds[source]['scopeContentSha256'],'targetScopeContentSha256':ds[target]['scopeContentSha256'],'challengerAgreement':'coordinator_adjudicated_navigation','sourceReviewIds':[r['id']for r in reviews],'evidenceRefs':refs})
rp=B/'final-replacements-receipt.json';save(rp,{'schemaVersion':'q025-orientation-final-replacement-adjudication/1','authority':'root','input':pin(ip),'decision':'Approve exact d40 stabilization-dependent application_of s7 to s15 and d41 limited categorical/geometric method_for s21 to s3. Preserve all qualifications and inherited reading limits. Neither requires applicability across the entire recipient scope. No universal stabilization, soft-spectrum, RG or equivalence result. Keep axion/fixed-tadpole joint withholding pending without a forced route.','approvedCases':todo,'navigationHashes':{p['id']:p['navigationContentSha256']for p in proofs},'sourceScopeHashes':{i:ds[i]['scopeContentSha256']for r in relations for i in [r['source'],r['target']]},'newPrimaryReading':False,'newScopesHomesRolesIdentities':False})
for p in proofs:p['adjudication']={'status':'accepted_explicit_navigation','receipt':pin(rp)}
cp=B/'final-replacements-component.json';save(cp,{'schemaVersion':'q025-orientation-coordinator-delta/1','destinations':[],'relations':relations,'decisions':proofs,'reviewRegistry':reviews,'scopeInputs':[pin(basep)],'admissionReceipt':pin(rp),'sourceContributions':[],'placements':[],'aliases':[],'typedCanonicalOperations':[],'canonicalGroupCandidates':[],'completeLocalPairConstraints':[],'withheldClaimsRetained':[c for c in cases if c['effective']['status']=='withheld'],'fullAtlasAdmission':False})
save(B/'final-replacements-report.json',{'component':pin(cp),'receipt':pin(rp),'exactChallengerReplacementsAdjudicated':2,'newPublicRelations':2,'allFiveOrientationReplacementsClosed':True,'newScopesHomesRolesIdentities':False});print(json.dumps(read(B/'final-replacements-report.json')))
