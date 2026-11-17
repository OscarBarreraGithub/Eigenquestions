"""Exact explicitly supported v2 neighborhood deltas; no implicit group union."""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sys.path.insert(0,str(F/'reconciliation-v1'));from build_authored_registry import fingerprint
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
vh=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
FAMILIES=['axion-vector-production','calabi-yau-periods-and-bps','ads-kk-scale-control','dark-energy-histories','consistent-reductions-and-actions','entropy-and-extremality','de-sitter-organization','distance-and-emergence']
def locations(f):
 p=F/'native-local/navigation-wave-v2/jobs'/f'{f}-proposal';d=F/'native-local/navigation-wave-v2/jobs'/f'{f}-challenge'
 if f=='de-sitter-organization':d=F/'native-local/navigation-recovery-v4/adopted/de-sitter-authored-disposition-challenge'
 if f=='distance-and-emergence':
  p=F/'native-local/navigation-successors-v1/adopted/distance-proposal-authored-context';d=F/'native-local/navigation-successors-v1/jobs/distance-and-emergence-independent-challenge'
 return p,d
def unique_reviews(rows,key):
 out={r[key]:r for r in rows};assert len(out)==len(rows),'Duplicate independent assessment';return out
def assert_exact_coverage(prior,r):
 assert not any(r[k]for k in ['newQuestions','decisions','navigation','sourceContributions']), 'New or changed challenge objects require separate admission'
 assert not r.get('supersededPriorDecisionIds'),'Superseded decisions require separate admission'
 a=unique_reviews(r['priorReviews'],'ref');n=unique_reviews(r['navigationReviews'],'ref');s=unique_reviews(r['sourceContributionReviews'],'index')
 assert set(a)=={q['id']for q in prior['newQuestions']+prior['decisions']}
 assert set(n)=={q['id']for q in prior['navigation']}
 assert set(s)==set(range(len(prior['sourceContributions'])))
 assert all(x['verdict']=='supported_as_written'for coll in [a,n,s]for x in coll.values()),'Exception cannot use exact agreement policy'
 return a,n,s

def main():
 basepath=F/'admissions-v5/supported-scope-role-component-v5.json';base=read(basepath);initial={d['id']:d for d in base['destinations']};policy=F/'navigation-admissions-v1/agreement-policy-authorization.json';reports=[]
 for family in FAMILIES:
  pd,D=locations(family);p=read(D/'packet.actual.json');r=read(D/'reply.json');prior=p['priorReview'];proposalfile=pd/'reply.json';assert read(proposalfile)==prior,'Dependent prior changed'
  assess,navassess,roleassess=assert_exact_coverage(prior,r);targets=copy.deepcopy(initial);mapping={k:v.get('admittedDestinationId')or v['candidateId']for k,v in p['machineBindings']['scopeBindings'].items()};assert set(mapping.values())<=set(targets)
  refs=copy.deepcopy(p['refRegistry']);units={u['ref']:u for u in p['units']};reviewids=[family+'-navigation-proposal',family+'-navigation-independent-challenge']
  for q in prior['newQuestions']:
   if q['id']not in refs:refs[q['id']]={'kind':'current_authored_scope_context','objectId':q['id'],'objectValueSha256':vh(q),'notPrimary':True,'notIndependentSourceEvidence':True}
  def ev(xs):
   assert set(xs)<=set(refs),'Unknown evidence/context reference'
   return [{'localRef':x,**refs[x]}for x in xs]
  reviews=[]
  for ident,jd in zip(reviewids,[pd,D]):
   rec={'id':ident,**pin(jd/'reply.json'),'receiptPath':str((jd/'receipt.json').relative_to(W)),'receiptSha256':sha(jd/'receipt.json'),'kind':'pinned_complete_scientific_review','nativeOrDerivedStatus':read(jd/'receipt.json')['status']}
   if(jd/'normalization.json').exists():rec['normalization']=pin(jd/'normalization.json')
   reviews.append(rec)
  destinations=[];proofs=[]
  for q in prior['newQuestions']:
   a=assess[q['id']];cid='q025-candidate-'+q['kind']+':'+fingerprint(q['kind'],q)[:24];mapping[q['id']]=cid
   us={ref for ref in q['refs']if ref in units};common=[ref for ref in q['refs']if ref in a['refs']and refs[ref].get('kind')=='primary'];papers={refs[ref]['paperId']for ref in common}
   assert us,'New definition lacks whole-description support'
   coverage={'descriptionCheckedCount':len(us),'excerptCheckedCount':sum(units[u]['paperId']in papers for u in us),'readingLimit':q['readingLimit'],'readingBasis':'Supplied complete descriptions and inherited paired scope/attribution notes; only exact own-paper primary windows cited by both native reviewers count as excerpt reading.','scopeSupportNotPhysicalResultVerification':True,'globalCanonicalUniquenessEstablished':False}
   d={'id':cid,'kind':q['kind'],'title':q['title'],'question':q['question'],'summary':q['summary'],'scope':q['scope'],'scientificStatus':'source_reviewed_scope_with_explicit_limits','readingCoverage':coverage,'evidenceIds':sorted(units[u]['unitId']for u in us),'methods':q['methods'],'aliases':[],'scopeDecisionId':f'decision:navigation-v2:{family}:scope:{q["id"]}','provenance':{'localRef':q['id'],'reviewIds':reviewids,'admissionBasis':'exact_explicit_independent_agreement_under_root_authorized_policy','newScientificDefinition':True}}
   assert cid not in targets;destinations.append(d);targets[cid]=d;proofs.append({'id':d['scopeDecisionId'],'type':'scope_acceptance','status':'accepted','subjectIds':[cid],'challengerAgreement':'supported_as_written','scopeAgreement':'unchanged','sourceReviewIds':reviewids,'evidenceRefs':ev(q['refs']),'independentAssessment':a})
  roles=[]
  for i,row in enumerate(prior['sourceContributions']):
   a=roleassess[i];u=units[row['unitRef']];assert row['unitRef']in row['refs']and row['unitRef']in a['refs'],'Role has no shared own-description reference'
   common=[ref for ref in row['refs']if ref in a['refs']and refs[ref].get('kind')=='primary'and refs[ref].get('paperId')==u['paperId']];basis='source_excerpt_checked'if common else'description_checked';evidence=[{'localRef':row['unitRef'],**refs[row['unitRef']],'paperId':u['paperId']}]+ev(common);rid=f'decision:navigation-v2:{family}:role:{i}'
   role={'unitId':u['unitId'],'destinationId':mapping[row['questionRef']],'role':row['role'],'basis':basis,'qualification':row['reason']+' Independent confirmation: '+a['reason'],'evidenceRefs':evidence,'decisionId':rid};roles.append(role);proofs.append({'id':rid,'type':'source_contribution','status':'accepted','subjectIds':[u['unitId'],role['destinationId']],'challengerAgreement':'independently_agreed','reviewAgreement':{'proposalReviewId':reviewids[0],'challengeReviewId':reviewids[1]},'sourceReviewIds':reviewids,'evidenceRefs':evidence,'originalRole':row,'independentAssessment':a,'contextRefs':ev([x for x in row['refs']if x!=row['unitRef']and x not in common])})
  hs=json.loads(subprocess.run(['node',str(F/'admissions-v4/lossless-hashes.mjs')],input=json.dumps({'destinations':list(targets.values()),'rows':roles},ensure_ascii=False),text=True,capture_output=True,check=True).stdout);hmap={d['id']:h for d,h in zip(targets.values(),hs['scopes'])};bp={x['id']:x for x in proofs}
  for d in destinations:d['scopeContentSha256']=hmap[d['id']];bp[d['scopeDecisionId']]['scopeContentSha256']=hmap[d['id']]
  for row,h in zip(roles,hs['rows']):bp[row['decisionId']].update(scopeContentSha256=hmap[row['destinationId']],contributionContentSha256=h)
  ops=[];groups=[]
  for op in prior['decisions']:
   x={'id':f'operation:navigation-v2:{family}:'+op['id'],'nativeOperation':op,'nativeOperationValueSha256':vh(op),'members':[mapping[z]for z in op['members']],'target':mapping.get(op['target']),'admissionBasis':'exact_explicit_independent_agreement_under_root_policy','independentAssessment':assess[op['id']],'sourceReviewIds':reviewids,'evidenceRefs':ev(op['refs']),'status':'accepted_typed_operation_subject_to_global_conflict_gate','publicNavigationAutomaticallyCreated':False,'sourceStatementEquivalenceAsserted':False};ops.append(x)
   if op['operation']=='same_scoped_question':
    groups.append({'operationId':x['id'],'memberDestinationIds':x['members'],'canonicalDestinationId':x['target'],'status':'local_group_supported_global_whole_group_gate_pending','retainedReadingLimits':[{'destinationId':mapping[s['ref']],'readingLimit':s['definition']['readingLimit']}for s in p['scopes']if s['ref']in op['members']],'sourceStatementIdentityEstablished':False,'automaticHomeTransfer':False})
  links=[]
  for row in prior['navigation']:
   a=navassess[row['id']];ids=sorted({refs[x]['unitId']for x in row['refs']if refs[x].get('unitId')});support_kind='direct_supplied_description_refs' if ids else 'inherited_admitted_endpoint_scope_support'
   if not ids:ids=sorted(set(targets[mapping[row['source']]]['evidenceIds']+targets[mapping[row['target']]]['evidenceIds']))
   assert ids,'Route lacks any admitted endpoint support'
   link={'id':f'navigation:v2:{family}:'+row['id'],'source':mapping[row['source']],'target':mapping[row['target']],'type':row['type'],'title':row['title'],'qualification':row['qualification'],'rationale':row['reason'],'evidenceIds':ids,'evidenceRefs':ev(row['refs']),'decisionId':f'decision:navigation-v2:{family}:route:'+row['id'],'provenance':{'nativeRouteId':row['id'],'sourceReviewIds':reviewids,'titleReadingDirection':'outgoing_only','independentAssessment':a,'freshPrimaryReading':any(refs[x].get('kind')=='primary'for x in row['refs']),'evidenceIdBasis':support_kind,'inheritedEvidenceIsNotFreshReading':support_kind=='inherited_admitted_endpoint_scope_support'}};links.append(link);proofs.append({'id':link['decisionId'],'type':'navigation','status':'accepted','subjectIds':[link['source'],link['target']],'relationUse':'public_navigation','relationType':link['type'],'navigationContentSha256':vh({k:v for k,v in link.items()if k not in ['decisionId','provenance']}),'sourceScopeContentSha256':hmap[link['source']],'targetScopeContentSha256':hmap[link['target']],'challengerAgreement':'independently_agreed','reviewAgreement':{'proposalReviewId':reviewids[0],'challengeReviewId':reviewids[1]},'sourceReviewIds':reviewids,'evidenceRefs':link['evidenceRefs']})
  constraints=[{'stage':stage,'status':'current'if stage=='challenge'else'historical_retained','left':mapping[x['left']],'right':mapping[x['right']],'relation':x['relation'],'nativeConstraint':x,'sourceReviewIds':reviewids}for stage,rr in [('proposal',prior),('challenge',r)]for x in rr['pairConstraints']]
  receipt={'schemaVersion':'q025-navigation-policy-admission/2','family':family,'status':'exact_paired_agreements_admitted_subject_to_global_identity_and_DAG_gates','policyAuthorization':pin(policy),'inputs':{'packet':pin(D/'packet.actual.json'),'proposal':pin(proposalfile),'challenge':pin(D/'reply.json'),'proposalReceipt':pin(pd/'receipt.json'),'challengeReceipt':pin(D/'receipt.json'),'normalization':pin(D/'normalization.json'),'existingScopes':pin(basepath)},'scopeHashes':{d['id']:d['scopeContentSha256']for d in destinations},'roleHashes':{x['id']:x['contributionContentSha256']for x in proofs if x['type']=='source_contribution'},'operationHashes':{x['id']:x['nativeOperationValueSha256']for x in ops},'navigationHashes':{x['id']:x['navigationContentSha256']for x in proofs if x['type']=='navigation'},'localEqualityGroups':groups,'preservedLimitations':r['limitations'],'unresolved':r['unresolved'],'counts':{'newScopes':len(destinations),'typedOperations':len(ops),'publicRoutes':len(links),'confirmedSourceRoles':len(roles),'homes':0,'installedAliases':0},'noFreshPrimaryReading':len(p.get('evidence',[]))==0,'newModelsRunByCompiler':0,'sourceQuestionIdentityNotInferred':True};rp=B/(family+'-admission.json');dump(rp,receipt)
  for proof in proofs:proof['coordinatorAdmissionReceipt']=pin(rp)
  for op in ops:op['adjudicationReceipt']=pin(rp)
  component={'schemaVersion':'q025-navigation-admitted-delta/2','destinations':destinations,'sourceContributions':roles,'relations':links,'decisions':proofs,'reviewRegistry':reviews,'typedCanonicalOperations':ops,'canonicalGroupCandidates':groups,'completeLocalPairConstraints':constraints,'sourceScopeBindings':mapping,'scopeInputs':[pin(basepath)],'admissionReceipt':pin(rp),'compoundAnnotations':r['compoundSources'],'placements':[],'aliases':[],'fullAtlasAdmission':False};cp=B/(family+'-component.json');dump(cp,component)
  reports.append({'family':family,'component':pin(cp),'receipt':pin(rp),'counts':receipt['counts'],'roleBasis':{basis:sum(x['basis']==basis for x in roles)for basis in ['description_checked','source_excerpt_checked']},'localEqualityGroups':groups,'summary':r['summary'],'unresolved':r['unresolved'],'readingLimits':r['limitations'],'newDefinitions':[{'id':d['id'],'title':d['title']}for d in destinations],'scopeRefs':{ref:{'id':cid,'title':targets[cid]['title']}for ref,cid in mapping.items()},'noFreshPrimaryReading':receipt['noFreshPrimaryReading']})
 report={'schemaVersion':'q025-navigation-wave-agreement-report/2','families':reports,'counts':{k:sum(r['counts'][k]for r in reports)for k in reports[0]['counts']},'globalGroupGatePending':sum(len(r['localEqualityGroups'])for r in reports),'readableJourneyReviewStillRequired':True};dump(B/'report.json',report);print(json.dumps({k:v for k,v in report.items()if k!='families'}))
if __name__=='__main__':main()
