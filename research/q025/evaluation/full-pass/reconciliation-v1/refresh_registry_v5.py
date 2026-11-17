"""Add completed lineages and admitted canonical scopes without changing older cuts."""
import collections,copy,datetime,hashlib,json
from pathlib import Path
import refresh_registry_v4 as previous
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sha=previous.sha
OLD=B/'authored-scope-registry-v4-20261117T131639Z.json'
COMP=F/'canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json'
RECEIPT=F/'canonical-pilot-admissions-v1/scope-role-operation-admission.json'
CONSTRAINTS=F/'canonical-pilot-admissions-v1/constraint-precedence.json'
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def eligible_inventory():
 # Read only paper IDs from the sealed reservation, never its descriptions.
 reservation=json.loads((E/'final-holdout-reservation.local.json').read_text())
 papers={x['paperId'] for x in reservation['records']}
 rows=json.loads((E.parent/'geometry/identity-neighbors/units.json').read_text())['rows']
 eligible=sorted(x['unitId'] for x in rows if x['paperId'] not in papers)
 excluded=sorted(x['unitId'] for x in rows if x['paperId'] in papers)
 assert len(eligible)==8430 and len(excluded)==43 and not set(eligible)&set(excluded)
 return {'schemaVersion':'q025-preholdout-eligible-unit-inventory/1','unitIds':eligible,'unitIdsSha256':hashlib.sha256('\n'.join(eligible).encode()).hexdigest(),'counts':{'eligible':8430,'reservedUnreviewed':43,'total':8473},'policy':'Complete reviewed pre-holdout coverage excludes every question on the 24 reserved papers. No reserved text is copied or semantically reviewed. Final release requires a dated post-freeze integration of those 43 units.','sourceInventory':pin(E.parent/'geometry/identity-neighbors/units.json')}
def parent_links(out):
 links=[]
 for review in out['reviews']:
  if review.get('kind')!='parent':continue
  d=E/review['artifactDirectory'];p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text())
  cards=p['priorCards']+p.get('existingCards',[])+r['cards']
  def endpoint(ref):
   if p['refRegistry'].get(ref,{}).get('kind')=='attributed_child_review':
    return {'localRef':ref,'kind':'review_batch_provenance','childRegionId':p['refRegistry'][ref].get('childRegionId'),'candidateId':None}
   if p['refRegistry'].get(ref,{}).get('kind') in ['source_object','source_unit','description','primary']:
    return {'localRef':ref,'kind':'source_context_object','sourceBinding':p['refRegistry'][ref],'candidateId':None,'createsDestination':False}
   h=previous.resolve_home(ref,p,cards)
   return {'localRef':ref,'kind':'scientific_scope' if h.get('candidateId') else 'unresolved','candidateId':h.get('candidateId'),'resolution':h}
  prior=p.get('priorParentLinks',[])
  for i,row in enumerate(r['links']):
   left=endpoint(row['source']);right=endpoint(row['target']);matches=[]
   for j,a in enumerate(prior):
    if a['source']==row['source'] and a['target']==row['target'] and a['type']==row['type']:matches.append({'index':j,'link':a})
   use='pending_explicit_scientific_navigation_decision'
   if any(x['kind']=='review_batch_provenance' for x in [left,right]):use='provenance_endpoint_requires_explicit_provenance_only_decision'
   elif any(x['kind']=='source_context_object' for x in [left,right]):use='source_context_endpoint_not_destination_navigation'
   links.append({'id':review['reviewId']+':link:'+str(i),'source':left,'target':right,'challengeLink':row,'sameEndpointTypePriorLinks':matches,'agreement':'paired_endpoint_type' if matches else 'challenger_new_or_changed','interpretationRequired':True,'publicNavigationAdmitted':False,'relationUse':use,'reviewPins':{'proposal':review['proposalDependency'],'challenge':review['challengeArtifact']}})
 return {'schemaVersion':'q025-parent-navigation-candidates/1','links':links,'counts':dict(collections.Counter(x['agreement'] for x in links)),'semantics':'Exact current proposals and independently repeated endpoint/type candidates only. Native narrows/method labels do not authorize public use of numerical child-batch provenance. No regex reinterpretation or automatic containment; all candidate endpoints and original reasons remain visible.'}
def refresh():
 previous.OLD=OLD;out=previous.refresh();out['schemaVersion']='q025-authored-scope-registry/5'
 c=json.loads(COMP.read_text());admission=pin(RECEIPT);component=pin(COMP)
 for d in c['destinations']:
  family=d['provenance']['pilotFamily'];local=d['provenance']['localRef'];review=d['provenance']['reviewIds'][-1]
  contribution=[]
  for row in c['sourceContributions']:
   if row['destinationId']==d['id']:
    contribution.append({**row,'independentRoleAgreement':False,'coordinatorAdjudicated':True,'scopeAdmissionArtifact':admission})
  out['records'].append({'recordId':'canonical-pilot:'+family+':'+local,'candidateId':d['id'],'admittedDestinationId':d['id'],'kind':d['kind'],'reviewId':review,'reviewKey':'canonical-pilot:'+family,'localRef':local,'scopeStatus':'explicitly_admitted_canonical_pilot_scope_global_identity_pending','definition':{**{k:d[k] for k in ['title','question','summary','scope']},'readingLimit':d['readingCoverage']['readingLimit']},'methods':d.get('methods',[]),'assessment':{'admissionBasis':d['provenance']['admissionBasis'],'scopeDecisionId':d['scopeDecisionId']},'scopeDefinitionFlags':[],'admissionJustificationFlags':[],'contributions':contribution,'evidenceRefs':[e for row in contribution for e in row['evidenceRefs']],'pins':{'componentSha256':component['sha256'],'admissionReceiptSha256':admission['sha256']},'admittedScopeArtifact':component,'scopeContentSha256':d['scopeContentSha256'],'scopeAdmissionArtifact':admission,'globalCanonicalUniquenessEstablished':False})
 out['canonicalPilotAdmission']={'component':component,'receipt':admission,'constraintPrecedence':pin(CONSTRAINTS),'operations':'Admitted typed operations remain subject to global complete-group and public-navigation gates. No automatic aliases or home assignments.','carried124Roles':'Pending explicit independent confirmation; not included as admitted contributions.'}
 inventory=eligible_inventory();actual={x['unitId'] for x in out['unitAssessments']};assert actual==set(inventory['unitIds']),(len(actual),len(set(inventory['unitIds'])-actual))
 old=json.loads(OLD.read_text());oldunits={x['unitId'] for x in old['unitAssessments']};oldids={x['recordId'] for x in old['records']};oldc={x['candidateId'] for x in old['records']}
 out['delta'].update({'newRecordIds':sorted({x['recordId'] for x in out['records']}-oldids),'newCandidateIds':sorted({x['candidateId'] for x in out['records']}-oldc),'newlyAssessedUnitIds':sorted(actual-oldunits),'exactlyPreservedPriorInputs':True})
 out['counts'].update({'authoredScopes':len(out['records']),'authoredQuestions':sum(x['kind']=='question' for x in out['records']),'scopeStatuses':dict(collections.Counter(x['scopeStatus'] for x in out['records'])),'newCandidateScopesSincePreviousCut':len(out['delta']['newCandidateIds']),'admittedCanonicalPilotScopes':30,'admittedCanonicalPilotContributions':4,'eligiblePreHoldoutUnits':8430,'uniqueAssessedUnits':len(actual),'unassessedEligibleUnits':0})
 assert out['counts']['completedLeafPairs']==186
 assert len({x['recordId'] for x in out['records']})==len(out['records'])
 return out,inventory,parent_links(out)
if __name__=='__main__':
 out,inventory,links=refresh();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=B/f'authored-scope-registry-v5-{stamp}.json';dump(path,out);ip=B/'eligible-preholdout-unit-ids-v1.json';dump(ip,inventory);lp=B/f'parent-navigation-candidates-v5-{stamp}.json';dump(lp,links)
 report={'schemaVersion':'q025-authored-registry-version/5','path':str(path.relative_to(W)),'sha256':sha(path),'bytes':path.stat().st_size,'counts':out['counts'],'previousRegistry':out['previousRegistry'],'compiler':pin(Path(__file__)),'eligibleInventory':pin(ip),'parentNavigationCandidates':{**pin(lp),'count':len(links['links'])},'newlyAssessedUnitIds':out['delta']['newlyAssessedUnitIds'],'lineageSelection':[{'canonicalReviewKey':x['canonicalReviewKey'],'reviewId':x['reviewId'],'artifactDirectory':x['artifactDirectory'],'receiptSha256':x['receiptSha256']}for x in out['selectedReviewLineages']],'activeInputsChanged':False};rp=B/f'registry-report-v5-{stamp}.json';rp.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['lineageSelection','newlyAssessedUnitIds']}))
