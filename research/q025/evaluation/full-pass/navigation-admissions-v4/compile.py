"""Authoritative V3-wave successor: unchanged agreements plus exact root-adjudicated corrections."""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sys.path.insert(0,str(F/'reconciliation-v1'));from build_authored_registry import fingerprint
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
vh=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
FAMILIES=[f'strong-scope-bundle-{i:02d}' for i in range(12)]
def locations(f):return (F/'native-local/navigation-wave-v3/jobs'/f'{f}-proposal',F/'native-local/navigation-wave-v3/jobs'/f'{f}-challenge')
def unique_reviews(rows,key):
 out={r[key]:r for r in rows};assert len(out)==len(rows),'Duplicate independent assessment';return out
def assert_exact_coverage(prior,r):
 a=unique_reviews(r['priorReviews'],'ref');n=unique_reviews(r['navigationReviews'],'ref');s=unique_reviews(r['sourceContributionReviews'],'index')
 assert set(a)=={q['id']for q in prior['newQuestions']+prior['decisions']}
 assert set(n)=={q['id']for q in prior['navigation']}
 assert set(s)==set(range(len(prior['sourceContributions'])))
 return a,n,s

def apply_root_replacements(family,original,r,assess,navassess,roleassess):
 prior=copy.deepcopy(original);log=[]
 def replace(collection,oldkey,newobj,reviews,oldreviewkey,newreviewkey):
  index=oldkey if isinstance(oldkey,int)else next(i for i,x in enumerate(prior[collection])if x['id']==oldkey)
  old=prior[collection][index];judgment=reviews[oldreviewkey];assert judgment['verdict']=='revise'
  prior[collection][index]=copy.deepcopy(newobj)
  reviews[newreviewkey]={'verdict':'coordinator_approved','reason':'Root explicitly approved this exact challenger replacement after reading the complete implicated scopes, whole descriptions and both attribution notes. '+newobj.get('reason',newobj.get('readingLimit','')),'refs':newobj['refs'],'originalIndependentJudgment':judgment,'replacedOriginal':old,'nativeChallengerObject':newobj}
  log.append({'collection':collection,'oldIdOrIndex':oldkey,'newIdOrIndex':newobj.get('id',index),'oldValue':old,'newValue':newobj,'nativeIndependentJudgment':judgment,'admissionAuthority':'root_exact_replacement_adjudication','newPrimaryReading':False})
 if family.endswith('-04'):replace('navigation','pn2',r['navigation'][0],navassess,'pn2','cn0')
 if family.endswith('-06'):
  replace('newQuestions','pq2',r['newQuestions'][0],assess,'pq2','cq0')
  for old,new in [('pd10','cd0'),('pd11','cd1')]:replace('decisions',old,next(x for x in r['decisions']if x['id']==new),assess,old,new)
  for old,new in [('pn10','cn0'),('pn11','cn1')]:replace('navigation',old,next(x for x in r['navigation']if x['id']==new),navassess,old,new)
  replace('sourceContributions',4,r['sourceContributions'][0],roleassess,4,4);replace('sourceContributions',7,r['sourceContributions'][1],roleassess,7,7)
 if family.endswith('-11'):
  replace('decisions','pd1',r['decisions'][0],assess,'pd1','cd0')
  new=r['navigation'][0];prior['navigation'].append(copy.deepcopy(new));navassess[new['id']]={'verdict':'coordinator_approved','reason':'Root explicitly approved the exact qualified common-target comparison after reading both complete scopes and the independent correction.','refs':new['refs'],'nativeChallengerObject':new};log.append({'collection':'navigation','oldIdOrIndex':None,'newIdOrIndex':new['id'],'newValue':new,'admissionAuthority':'root_exact_new_route_adjudication'})
 assert {k:len(r[k])for k in ['newQuestions','decisions','navigation','sourceContributions']}==({k:0 for k in ['newQuestions','decisions','navigation','sourceContributions']}if not log else {'newQuestions':int(family.endswith('-06')),'decisions':2 if family.endswith('-06')else int(family.endswith('-11')),'navigation':2 if family.endswith('-06')else 1,'sourceContributions':2 if family.endswith('-06')else 0})
 return prior,log

def main():
 basepath=F/'admissions-v5/supported-scope-role-component-v5.json';base=read(basepath);stablepath=F/'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json';initial={d['id']:d for d in base['destinations']+read(stablepath)['destinations']+read(F/'parent-scope-admission-v2/component.json')['destinations']+read(F/'scope-gap-admissions-v1/component.json')['destinations']};policy=F/'navigation-admissions-v1/agreement-policy-authorization.json';reports=[]
 for family in FAMILIES:
  pd,D=locations(family)
  if not(D/'receipt.json').exists() or read(D/'receipt.json')['status']!='complete':continue
  p=read(D/'packet.actual.json');r=read(D/'reply.json');prior=p['priorReview'];proposalfile=pd/'reply.json';assert read(proposalfile)==prior,'Dependent prior changed'
  assess,navassess,roleassess=assert_exact_coverage(prior,r);original_prior=copy.deepcopy(prior);prior,root_log=apply_root_replacements(family,original_prior,r,assess,navassess,roleassess);targets=copy.deepcopy(initial);mapping={k:v.get('admittedDestinationId')or v['candidateId']for k,v in p['machineBindings']['scopeBindings'].items()}
  refs=copy.deepcopy(p['refRegistry']);units={u['ref']:u for u in p['units']};reviewids=[family+'-navigation-proposal',family+'-navigation-independent-challenge']
  for q in original_prior['newQuestions']+prior['newQuestions']+r['newQuestions']:
   mapping[q['id']]='q025-candidate-'+q['kind']+':'+fingerprint(q['kind'],q)[:24]
   if q['id']not in refs:refs[q['id']]={'kind':'current_authored_scope_context','objectId':q['id'],'objectValueSha256':vh(q),'notPrimary':True,'notIndependentSourceEvidence':True}
  def ev(xs):
   assert set(xs)<=set(refs),'Unknown evidence/context reference'
   return [{'localRef':x,**refs[x]}for x in xs]
  reviews=[]
  for ident,jd in zip(reviewids,[pd,D]):
   rec={'id':ident,**pin(jd/'reply.json'),'receiptPath':str((jd/'receipt.json').relative_to(W)),'receiptSha256':sha(jd/'receipt.json'),'kind':'pinned_complete_scientific_review','nativeOrDerivedStatus':read(jd/'receipt.json')['status']}
   if(jd/'normalization.json').exists():rec['normalization']=pin(jd/'normalization.json')
   reviews.append(rec)
  destinations=[];proofs=[];excluded=[]
  for q in prior['newQuestions']:
   if assess[q['id']]['verdict']not in ['supported_as_written','coordinator_approved']:
    excluded.append({'kind':'scope','original':q,'judgment':assess[q['id']]});continue
   a=assess[q['id']];cid='q025-candidate-'+q['kind']+':'+fingerprint(q['kind'],q)[:24];mapping[q['id']]=cid
   us={ref for ref in q['refs']if ref in units};common=[ref for ref in q['refs']if ref in a['refs']and refs[ref].get('kind')=='primary'];papers={refs[ref]['paperId']for ref in common}
   assert us,'New definition lacks whole-description support'
   coverage={'descriptionCheckedCount':len(us),'excerptCheckedCount':sum(units[u]['paperId']in papers for u in us),'readingLimit':q['readingLimit'],'readingBasis':'Supplied complete descriptions and inherited paired scope/attribution notes; only exact own-paper primary windows cited by both native reviewers count as excerpt reading.','scopeSupportNotPhysicalResultVerification':True,'globalCanonicalUniquenessEstablished':False}
   d={'id':cid,'kind':q['kind'],'title':q['title'],'question':q['question'],'summary':q['summary'],'scope':q['scope'],'scientificStatus':'source_reviewed_scope_with_explicit_limits','readingCoverage':coverage,'evidenceIds':sorted(units[u]['unitId']for u in us),'methods':q['methods'],'aliases':[],'scopeDecisionId':f'decision:navigation-v3:{family}:scope:{q["id"]}','provenance':{'localRef':q['id'],'reviewIds':reviewids,'admissionBasis':'exact_explicit_independent_agreement_under_root_authorized_policy','newScientificDefinition':True}}
   if a['verdict']=='coordinator_approved':
    d['readingCoverage']['readingBasis']='Whole source description and exact existing paired attribution, independently proposed correction and explicit coordinator reading; no new primary reading.'
    d['provenance']['admissionBasis']='root_exact_replacement_adjudication'
   assert cid not in targets;destinations.append(d);targets[cid]=d;proofs.append({'id':d['scopeDecisionId'],'type':'scope_acceptance','status':'accepted','subjectIds':[cid],'challengerAgreement':'coordinator_adjudicated_scope'if a['verdict']=='coordinator_approved'else'supported_as_written','scopeAgreement':'root_adjudicated_replacement'if a['verdict']=='coordinator_approved'else'unchanged','sourceReviewIds':reviewids,'evidenceRefs':ev(q['refs']),'independentAssessment':a})
  roles=[]
  for i,row in enumerate(prior['sourceContributions']):
   a=roleassess[i]
   if a['verdict']not in ['supported_as_written','coordinator_approved'] or mapping[row['questionRef']]not in targets:
    excluded.append({'kind':'source_role','index':i,'original':row,'judgment':a,'missingAdmittedTargets':[mapping[z]for z in [row.get('questionRef'),row.get('source'),row.get('target')]if z in mapping and mapping[z]not in targets]});continue
   u=units[row['unitRef']];assert row['unitRef']in row['refs']and row['unitRef']in a['refs'],'Role has no shared own-description reference'
   common=[ref for ref in row['refs']if ref in a['refs']and refs[ref].get('kind')=='primary'and refs[ref].get('paperId')==u['paperId']];basis='source_excerpt_checked'if common else'description_checked';evidence=[{'localRef':row['unitRef'],**refs[row['unitRef']],'paperId':u['paperId']}]+ev(common);rid=f'decision:navigation-v3:{family}:role:{i}'
   role={'unitId':u['unitId'],'destinationId':mapping[row['questionRef']],'role':row['role'],'basis':basis,'qualification':row['reason']+(' Root adjudication: 'if a['verdict']=='coordinator_approved'else' Independent confirmation: ')+a['reason'],'evidenceRefs':evidence,'decisionId':rid};roles.append(role);proofs.append({'id':rid,'type':'source_contribution','status':'accepted','subjectIds':[u['unitId'],role['destinationId']],'challengerAgreement':'coordinator_adjudicated_source_contribution'if a['verdict']=='coordinator_approved'else'independently_agreed',**({}if a['verdict']=='coordinator_approved'else{'reviewAgreement':{'proposalReviewId':reviewids[0],'challengeReviewId':reviewids[1]}}),'sourceReviewIds':reviewids,'evidenceRefs':evidence,'originalRole':row,'independentAssessment':a,'contextRefs':ev([x for x in row['refs']if x!=row['unitRef']and x not in common])})
  hs=json.loads(subprocess.run(['node',str(F/'admissions-v4/lossless-hashes.mjs')],input=json.dumps({'destinations':list(targets.values()),'rows':roles},ensure_ascii=False),text=True,capture_output=True,check=True).stdout);hmap={d['id']:h for d,h in zip(targets.values(),hs['scopes'])};bp={x['id']:x for x in proofs}
  for d in destinations:d['scopeContentSha256']=hmap[d['id']];bp[d['scopeDecisionId']]['scopeContentSha256']=hmap[d['id']]
  for row,h in zip(roles,hs['rows']):bp[row['decisionId']].update(scopeContentSha256=hmap[row['destinationId']],contributionContentSha256=h)
  ops=[];groups=[]
  for op in prior['decisions']:
   if assess[op['id']]['verdict']not in ['supported_as_written','coordinator_approved'] or op['id']in r.get('supersededPriorDecisionIds',[]) or any(mapping[z]not in targets for z in op['members']):
    excluded.append({'kind':'operation','original':op,'judgment':assess[op['id']],'missingAdmittedTargets':[mapping[z]for z in op['members']if mapping[z]not in targets]});continue
   x={'id':f'operation:navigation-v3:{family}:'+op['id'],'nativeOperation':op,'nativeOperationValueSha256':vh(op),'members':[mapping[z]for z in op['members']],'target':mapping.get(op['target']),'admissionBasis':'root_exact_replacement_adjudication'if assess[op['id']]['verdict']=='coordinator_approved'else'exact_explicit_independent_agreement_under_root_policy','independentAssessment':assess[op['id']],'sourceReviewIds':reviewids,'evidenceRefs':ev(op['refs']),'status':'accepted_typed_operation_subject_to_global_conflict_gate','publicNavigationAutomaticallyCreated':False,'sourceStatementEquivalenceAsserted':False};ops.append(x)
   if op['operation']=='same_scoped_question':
    groups.append({'operationId':x['id'],'memberDestinationIds':x['members'],'canonicalDestinationId':x['target'],'status':'local_group_supported_global_whole_group_gate_pending','retainedReadingLimits':[{'destinationId':mapping[s['ref']],'readingLimit':s['definition']['readingLimit']}for s in p['scopes']if s['ref']in op['members']],'sourceStatementIdentityEstablished':False,'automaticHomeTransfer':False})
  links=[]
  for row in prior['navigation']:
   a=navassess[row['id']]
   if a['verdict']not in ['supported_as_written','coordinator_approved'] or any(mapping[row[k]]not in targets for k in ['source','target']):
    excluded.append({'kind':'navigation','original':row,'judgment':a,'missingAdmittedTargets':[mapping[z]for z in [row.get('questionRef'),row.get('source'),row.get('target')]if z in mapping and mapping[z]not in targets]});continue
   ids=sorted({refs[x]['unitId']for x in row['refs']if refs[x].get('unitId')});support_kind='direct_supplied_description_refs' if ids else 'inherited_admitted_endpoint_scope_support'
   if not ids:ids=sorted(set(targets[mapping[row['source']]]['evidenceIds']+targets[mapping[row['target']]]['evidenceIds']))
   assert ids,'Route lacks any admitted endpoint support'
   link={'id':f'navigation:v3:{family}:'+row['id'],'source':mapping[row['source']],'target':mapping[row['target']],'type':row['type'],'title':row['title'],'qualification':row['qualification'],'rationale':row['reason'],'evidenceIds':ids,'evidenceRefs':ev(row['refs']),'decisionId':f'decision:navigation-v3:{family}:route:'+row['id'],'provenance':{'nativeRouteId':row['id'],'sourceReviewIds':reviewids,'titleReadingDirection':'outgoing_only','independentAssessment':a,'freshPrimaryReading':any(refs[x].get('kind')=='primary'for x in row['refs']),'evidenceIdBasis':support_kind,'inheritedEvidenceIsNotFreshReading':support_kind=='inherited_admitted_endpoint_scope_support'}};links.append(link);proofs.append({'id':link['decisionId'],'type':'navigation','status':'accepted','subjectIds':[link['source'],link['target']],'relationUse':'public_navigation','relationType':link['type'],'navigationContentSha256':vh({k:v for k,v in link.items()if k not in ['decisionId','provenance']}),'sourceScopeContentSha256':hmap[link['source']],'targetScopeContentSha256':hmap[link['target']],'challengerAgreement':'coordinator_adjudicated_navigation'if a['verdict']=='coordinator_approved'else'independently_agreed',**({}if a['verdict']=='coordinator_approved'else{'reviewAgreement':{'proposalReviewId':reviewids[0],'challengeReviewId':reviewids[1]}}),'sourceReviewIds':reviewids,'evidenceRefs':link['evidenceRefs']})
  constraints=[{'stage':stage,'status':'current'if stage=='challenge'else'historical_retained','left':mapping[x['left']],'right':mapping[x['right']],'relation':x['relation'],'nativeConstraint':x,'sourceReviewIds':reviewids}for stage,rr in [('proposal',original_prior),('challenge',r)]for x in rr['pairConstraints']]
  receipt={'schemaVersion':'q025-navigation-policy-admission/2','family':family,'status':'exact_paired_agreements_and_explicit_root_corrections_subject_to_global_identity_and_DAG_gates','policyAuthorization':pin(policy),'rootExceptionAuthorization':'Root explicitly approved every exact challenger replacement in scientific-exceptions.json 784b05eb428d9a299b9e4df465cd1278dbf41c21835895bf9ebdb7c8679d989d after reading all changed objects, full implicated scopes, whole descriptions and paired notes; the twelve old endpoint scopes have their separate exact scope-only receipt.','inputs':{'packet':pin(D/'packet.actual.json'),'proposal':pin(proposalfile),'challenge':pin(D/'reply.json'),'proposalReceipt':pin(pd/'receipt.json'),'challengeReceipt':pin(D/'receipt.json'),'normalization':pin(D/'normalization.json'),'existingScopes':pin(basepath),'stableScopes':pin(stablepath),'previouslyAdjudicatedParent':pin(F/'parent-scope-admission-v2/component.json'),'scopeGapAdmission':pin(F/'scope-gap-admissions-v1/component.json'),'priorAdmissionSnapshot':pin(F/'navigation-admissions-v3'/(family+'-component.json')),'rootScientificExceptionIntake':pin(F/'native-local/navigation-admissions-v3/scientific-exceptions.json')},'scopeHashes':{d['id']:d['scopeContentSha256']for d in destinations},'roleHashes':{x['id']:x['contributionContentSha256']for x in proofs if x['type']=='source_contribution'},'operationHashes':{x['id']:x['nativeOperationValueSha256']for x in ops},'navigationHashes':{x['id']:x['navigationContentSha256']for x in proofs if x['type']=='navigation'},'localEqualityGroups':groups,'preservedLimitations':r['limitations'],'unresolved':r['unresolved'],'counts':{'newScopes':len(destinations),'typedOperations':len(ops),'publicRoutes':len(links),'confirmedSourceRoles':len(roles),'homes':0,'installedAliases':0},'noFreshPrimaryReading':len(p.get('evidence',[]))==0,'excludedOriginalRows':excluded,'unadmittedChallengeObjects':{},'rootAdjudicatedReplacements':root_log,'originalRejectedRowsRetained':bool(root_log),'newModelsRunByCompiler':0,'sourceQuestionIdentityNotInferred':True};rp=B/(family+'-admission.json');dump(rp,receipt)
  for proof in proofs:
   proof['coordinatorAdmissionReceipt']=pin(rp)
   if proof['challengerAgreement'].startswith('coordinator_adjudicated'):
    if 'independentAssessment'in proof:proof['coordinatorAssessment']=proof.pop('independentAssessment')
    if 'originalRole'in proof:proof['admittedChallengerRole']=proof.pop('originalRole')
    proof['adjudication']={'status':{'scope_acceptance':'accepted_explicit_scope','source_contribution':'accepted_explicit_source_contribution','navigation':'accepted_explicit_navigation'}[proof['type']],'receipt':pin(rp)}
  for op in ops:
   op['adjudicationReceipt']=pin(rp)
   if op['admissionBasis']=='root_exact_replacement_adjudication':op['coordinatorAssessment']=op.pop('independentAssessment')
  for row in links:
   if row['provenance'].get('independentAssessment',{}).get('verdict')=='coordinator_approved':row['provenance']['coordinatorAssessment']=row['provenance'].pop('independentAssessment')
  component={'schemaVersion':'q025-navigation-admitted-delta/2','destinations':destinations,'sourceContributions':roles,'relations':links,'decisions':proofs,'reviewRegistry':reviews,'typedCanonicalOperations':ops,'canonicalGroupCandidates':groups,'completeLocalPairConstraints':constraints,'sourceScopeBindings':mapping,'scopeInputs':[pin(basepath),pin(stablepath),pin(F/'parent-scope-admission-v2/component.json'),pin(F/'scope-gap-admissions-v1/component.json')],'admissionReceipt':pin(rp),'compoundAnnotations':r['compoundSources'],'placements':[],'aliases':[],'pendingExceptions':excluded,'pendingChallengeObjects':{},'rootAdjudicatedReplacements':root_log,'supersedesAdmissionSnapshot':pin(F/'navigation-admissions-v3'/(family+'-component.json')),'supersessionMeaning':'Earlier admitted public scientific rows remain unchanged; previously held rows are enabled only by separate endpoint-scope admission or exact root adjudication. Historical rejected proposals and the earlier snapshot remain retained.','fullAtlasAdmission':False};cp=B/(family+'-component.json');dump(cp,component)
  reports.append({'family':family,'component':pin(cp),'receipt':pin(rp),'counts':receipt['counts'],'roleBasis':{basis:sum(x['basis']==basis for x in roles)for basis in ['description_checked','source_excerpt_checked']},'localEqualityGroups':groups,'summary':r['summary'],'unresolved':r['unresolved'],'readingLimits':r['limitations'],'newDefinitions':[{'id':d['id'],'title':d['title']}for d in destinations],'scopeRefs':{ref:{'id':cid,'title':targets.get(cid,{'title':next((s['definition']['title']for s in p['scopes']if s['ref']==ref),next((q['title']for q in prior['newQuestions']+r['newQuestions']if q['id']==ref),ref))})['title'],'admitted':cid in targets}for ref,cid in mapping.items()},'noFreshPrimaryReading':receipt['noFreshPrimaryReading'],'excludedOriginalRows':len(excluded),'pendingChallengeObjects':{},'rootAdjudicatedReplacements':len(root_log)})
 report={'schemaVersion':'q025-navigation-wave-agreement-report/4','families':reports,'counts':{k:sum(r['counts'][k]for r in reports)for k in reports[0]['counts']},'globalGroupGatePending':sum(len(r['localEqualityGroups'])for r in reports),'readableJourneyReviewStillRequired':True};dump(B/'report.json',report);print(json.dumps({k:v for k,v in report.items()if k!='families'}))
if __name__=='__main__':main()
