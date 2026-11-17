"""Continue approved mechanical scope/role policies on the final leaf intake."""
import collections,copy,hashlib,json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2]
sys.path.insert(0,str(F/'reconciliation-v1'));from refresh_registry_v4 import proposal_dependency
sys.path.insert(0,str(F/'annotation-admissions-v3'));from build_intake_overlay import apply_scope_resolution
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
REG=F/'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json';BASE=F/'admissions-v2/supported-scope-role-component-v2.json';OVER=F/'annotation-admissions-v3/intake-overlay-v2.json'
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
def key(e):
 c=e.get('sourceContext',{});return (e.get('kind'),e.get('unitId'),e.get('paperId'),c.get('path'),c.get('pdfPage'),c.get('start'),c.get('end'),c.get('textSha256'),e.get('textSha256'))
def compile_current():
 R=json.loads(REG.read_text());base=json.loads(BASE.read_text());overlay=json.loads(OVER.read_text());resolutions={a['recordId']:a for a in overlay['scopeAssessmentResolutions']};reviews={r['reviewId']:r for r in R['reviews']};out=copy.deepcopy(base)
 destinations={d['id']:d for d in out['destinations']};knownrows={(r['unitId'],r['destinationId'],r['role'])for r in out['sourceContributions']};review_registry={r['id']:r for r in out['reviewRegistry']};newscopes=[];newrows=[];scope_decisions=[];rowmeta=[];excluded=[];role_excluded=[];bindings=[];loaded={};resolved_annotations=[]
 def load(record):
  rid=record['reviewId']
  if rid in loaded:return loaded[rid]
  d=E/reviews[rid]['artifactDirectory'];dep=proposal_dependency(d);assert dep==reviews[rid]['proposalDependency'];pd=E/dep['artifactDirectory'];p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text())
  for rd in [pd,d]:
   receipt=json.loads((rd/'receipt.json').read_text());assert receipt['status']=='complete'and sha(rd/'reply.json')==receipt['normalizedReplySha256'];review_registry[rd.name]={'id':rd.name,'path':str((rd/'reply.json').relative_to(W)),'sha256':sha(rd/'reply.json'),'receiptPath':str((rd/'receipt.json').relative_to(W)),'receiptSha256':sha(rd/'receipt.json'),'model':'gpt-6-astra','effort':'xhigh','sourceOnly':True}
  loaded[rid]=(p,r,{u['i']:u for u in p['units']},{a['i']:a for a in p['priorAssignments']},{a['i']:a for a in r['units']},pd.name,d.name);return loaded[rid]
 def common(p,u,old,now):
  own=p['refRegistry'][u['descriptionRef']];oldrefs={key(p['refRegistry'][v])for v in old['refs']};shared=[]
  for ref in now['refs']:
   m=p['refRegistry'][ref]
   if m.get('kind')in ['primary','source_excerpt']and m.get('paperId')==u['paperId']and key(m)in oldrefs:shared.append({'localRef':ref,**m})
  basis='source_excerpt_checked'if old['b']==now['b']=='excerpt'and shared else'description_checked'
  return basis,[{'localRef':u['descriptionRef'],**own}]+(shared if basis=='source_excerpt_checked'else[])
 for original in R['records']:
  record=apply_scope_resolution(original,resolutions[original['recordId']])if original['recordId']in resolutions else original
  if record is not original:resolved_annotations.append(record['recordId'])
  rid=record['recordId'];cid=record['candidateId']
  if record['scopeStatus']!='independently_supported'or record['scopeDefinitionFlags']:
   excluded.append({'recordId':rid,'candidateId':cid,'reason':record['scopeStatus']if not record['scopeDefinitionFlags']else'unresolved_scope_definition_defect','separateExistingAdmission':bool(record.get('admittedScopeArtifact'))});continue
  p,r,units,prior,current,pid,chid=load(record);local=record['localRef'];card=next(a for a in p['priorCards']if a['id']==local);assess=next(a for a in r['cardReviews']if a['id']==local);assert assess['decision']=='supported_as_written'and assess['scopeChange']=='same';assert all(card[k]==record['definition'][k]for k in ['title','question','summary','scope','readingLimit'])
  ev_ids={c['unitId']for c in record['contributions']};scope_refs=copy.deepcopy(record['evidenceRefs']);representatives=[]
  for m in scope_refs:
   if m.get('kind')=='description'and m.get('unitId'):ev_ids.add(m['unitId'])
   elif m.get('kind')in ['primary','source_excerpt']:ev_ids.update(p['refRegistry'][u['descriptionRef']]['unitId']for u in units.values()if u['paperId']==m['paperId'])
  if not ev_ids and local=='r':
   for i,now in current.items():
    old=prior[i]
    if old['d']!=now['d']or now['d']not in ['member','overlap']:continue
    basis,refs=common(p,units[i],old,now);uid=p['refRegistry'][units[i]['descriptionRef']]['unitId'];ev_ids.add(uid);scope_refs+=refs;representatives.append({'unitId':uid,'disposition':now['d'],'basis':basis,'evidenceRefs':refs,'proposalBasis':old['b'],'challengeBasis':now['b'],'sourceContributionOrHomeAdmission':False})
  if not ev_ids:excluded.append({'recordId':rid,'candidateId':cid,'reason':'no_exact_representative_source_unit_for_scope'});continue
  contributions=[];common_excerpt=set()
  for c in record['contributions']:
   i=c['unitIndex'];old=prior.get(i);now=current[i];reason=None
   if not old or not c['independentRoleAgreement']or(local,c['role'])not in{(q['id'],q['role'])for q in old['q']}:reason='no_exact_independent_role_agreement'
   elif c.get('materialScopeFlag')or old['reason']in ['changed_regime','scope_mismatch']or now['reason']in ['changed_regime','scope_mismatch']:reason='explicit_changed_regime_or_scope_mismatch'
   if reason:role_excluded.append({'recordId':rid,'unitId':c['unitId'],'role':c['role'],'reason':reason});continue
   basis,refs=common(p,units[i],old,now)
   if basis=='source_excerpt_checked':common_excerpt.add(c['unitId'])
   rowkey=(c['unitId'],cid,c['role'])
   if rowkey in knownrows:continue
   decision='decision:source-contribution:'+hashlib.sha256(json.dumps([rid,c['unitId'],c['role']]).encode()).hexdigest()[:24]
   row={'unitId':c['unitId'],'destinationId':cid,'role':c['role'],'basis':basis,'evidenceRefs':refs,'decisionId':decision,'qualification':'Original proposal qualification: '+old['note']+' Independent challenge qualification: '+now['note']}
   contributions.append(row);knownrows.add(rowkey);rowmeta.append({'decisionId':decision,'recordId':rid,'proposalReviewId':pid,'challengeReviewId':chid,'proposalBasis':old['b'],'challengeBasis':now['b'],'commonBasis':basis,'proposalNote':old['note'],'challengeNote':now['note'],'dispositionAgreement':old['d']==now['d'],'factorIdentityAndPlacementAgreementNotInferred':True,'unresolvedFactorQualificationsNotPromoted':True})
  if cid not in destinations:
   count_excerpt=len(common_excerpt)if not representatives else sum(a['basis']=='source_excerpt_checked'for a in representatives)
   coverage={'descriptionCheckedCount':len(ev_ids),'excerptCheckedCount':count_excerpt,'readingLimit':card['readingLimit'],'sourceReadingScope':'Exact paired descriptions and same own-paper primary windows. Representative broad membership supports scope only; no source home or proof verification is inferred.','inheritedParentCoverage':copy.deepcopy(p.get('parentCoverage'))if p.get('kind')=='parent'else None}
   if p.get('kind')=='parent':coverage.update({'directContrastDescriptions':len(ev_ids),'allDescendantsFreshlyRead':False})
   dst={'id':cid,'kind':record['kind'],'title':card['title'],'question':card['question'],'summary':card['summary'],'scope':copy.deepcopy(card['scope']),'scientificStatus':'source_reviewed_scope_with_explicit_limits','readingCoverage':coverage,'evidenceIds':sorted(ev_ids),'methods':card.get('methods',[]),'aliases':[],'scopeDecisionId':'decision:scope:'+hashlib.sha256(rid.encode()).hexdigest()[:24],'provenance':{'recordId':rid,'reviewIds':[pid,chid],'sourceProposalDefinitionUnchanged':True,'canonicalIdentityStatus':'unreconciled_authored_scope','publicationStatus':'pending_canonical_organization_and_explicit_stage_status_copyedit','doesNotVerifyPhysicalResults':True,'admissionJustificationFlags':record['admissionJustificationFlags'],'annotationResolution':record.get('annotationResolution'),'annotationFlagsDoNotAlterExactScopeDefinition':True}}
   destinations[cid]=dst;newscopes.append(dst);scope_decisions.append({'id':dst['scopeDecisionId'],'type':'scope_acceptance','status':'accepted','subjectIds':[cid],'challengerAgreement':'supported_as_written','scopeAgreement':'unchanged','sourceReviewIds':[pid,chid],'evidenceRefs':scope_refs or contributions[0]['evidenceRefs'],'policyAdmission':'Root-authorized exact unchanged-scope continuation; coordinator did not personally reread every source. Review-note flags remain separate from intact exact scope support.'})
   if representatives:bindings.append({'destinationId':cid,'recordId':rid,'representatives':representatives,'parentCoverage':p.get('parentCoverage')})
  newrows+=contributions
 helper=E.parent/'assembly/accepted.mjs';js='import {scopeContentHash,sourceContributionContentHash} from '+json.dumps(helper.as_uri())+';let s="";for await(const c of process.stdin)s+=c;const x=JSON.parse(s),d=new Map(x.destinations.map(a=>[a.id,a]));console.log(JSON.stringify({scopes:x.added.map(scopeContentHash),rows:x.rows.map(r=>sourceContributionContentHash(r,scopeContentHash(d.get(r.destinationId))))}));'
 hashes=json.loads(subprocess.run(['node','--input-type=module','-e',js],input=json.dumps({'destinations':list(destinations.values()),'added':newscopes,'rows':newrows},ensure_ascii=False),text=True,capture_output=True,check=True).stdout)
 for d,h,dec in zip(newscopes,hashes['scopes'],scope_decisions):d['scopeContentSha256']=h;dec['scopeContentSha256']=h
 metadata={x['decisionId']:x for x in rowmeta};newdecisions=list(scope_decisions)
 for row,h in zip(newrows,hashes['rows']):
  m=metadata[row['decisionId']];newdecisions.append({'id':row['decisionId'],'type':'source_contribution','status':'accepted','subjectIds':[row['unitId'],row['destinationId']],'scopeContentSha256':destinations[row['destinationId']]['scopeContentSha256'],'contributionContentSha256':h,'challengerAgreement':'independently_agreed','reviewAgreement':{'proposalReviewId':m['proposalReviewId'],'challengeReviewId':m['challengeReviewId']},'sourceReviewIds':[m['proposalReviewId'],m['challengeReviewId']],'evidenceRefs':row['evidenceRefs'],'readingAgreement':m})
 counts={'acceptedScopes':len(destinations),'acceptedQuestionScopes':sum(d['kind']=='question'for d in destinations.values()),'acceptedRegionScopes':sum(d['kind']=='region'for d in destinations.values()),'acceptedTypedContributions':len(base['sourceContributions'])+len(newrows),'addedScopes':len(newscopes),'addedTypedRoles':len(newrows),'addedBroadRepresentativeScopes':len(bindings),'addedRoleBasis':dict(collections.Counter(x['basis']for x in newrows)),'excludedScopeRecords':len(excluded),'excludedRoles':len(role_excluded),'resolvedScopeAssessmentNotesApplied':len(resolved_annotations),'newHomes':0,'newIdentities':0,'newRelations':0,'carried124RolesAdmitted':0}
 receipt={'schemaVersion':'q025-mechanical-scope-role-admission/3','status':'accepted_scope_contribution_only','adjudicator':'root_policy_class_continuation','inputRegistry':pin(REG),'baseComponent':pin(BASE),'annotationOverlay':pin(OVER),'f28NarrowingAndRevalidation':pin(F/'f28-adjudication-v1/admission-and-revalidation.json'),'policies':[pin(F/'admissions-v1/MECHANICAL-ADMISSION-POLICY.md'),pin(F/'admissions-v2/POLICY.md')],'authorization':'Continue exact unchanged supported scopes, exact paired roles with common basis and qualifications, and joint member/overlap broad representatives. No changed scopes, roles, homes, public branches, identities or carried124 roles. Root did not reread every source.','counts':counts,'addedScopeHashes':{d['id']:d['scopeContentSha256']for d in newscopes},'addedContributionHashes':{r['decisionId']:h for r,h in zip(newrows,hashes['rows'])},'broadRepresentativeBindings':bindings,'resolvedScopeAssessmentRecords':resolved_annotations}
 rp=B/'scope-role-admission-v3.json';rp.write_text(json.dumps(receipt,ensure_ascii=False,separators=(',',':'))+'\n');receipt_ref=pin(rp)
 for dec in newdecisions:dec['policyContinuationReceipt']=receipt_ref
 out['destinations']+=newscopes;out['sourceContributions']+=newrows;out['decisions']+=newdecisions;out['reviewRegistry']=list(review_registry.values());out['schemaVersion']='q025-admitted-component-fragment/5';out['currentPolicyContinuationReceipt']=receipt_ref;out['inputRegistry']=pin(REG);out['exclusions']={'scopeRecords':excluded,'roles':role_excluded};out['counts']=counts;out['separateExplicitComponents']=[pin(F/'canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json'),pin(F/'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json')];out['unchangedPriorScopesAndRoles']={'component':pin(BASE),'scopeCount':len(base['destinations']),'roleCount':len(base['sourceContributions'])};out['annotationAndPremiseOverlays']=[pin(OVER),pin(F/'f28-adjudication-v1/admission-and-revalidation.json')]
 assert out['destinations'][:len(base['destinations'])]==base['destinations'];assert out['sourceContributions'][:len(base['sourceContributions'])]==base['sourceContributions'];assert len(destinations)==len(out['destinations']);assert len({r['decisionId']for r in out['sourceContributions']})==len(out['sourceContributions'])
 cp=B/'supported-scope-role-component-v3.json';cp.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');report={'schemaVersion':'q025-admission-continuation-report/3','counts':counts,'component':{**pin(cp),'bytes':cp.stat().st_size},'receipt':{**receipt_ref,'bytes':rp.stat().st_size},'compiler':pin(Path(__file__)),'exclusionReasons':dict(collections.Counter(x['reason']for x in excluded)),'roleExclusionReasons':dict(collections.Counter(x['reason']for x in role_excluded)),'representativeNewScopes':[{'id':d['id'],'kind':d['kind'],'title':d['title'],'question':d['question'],'scopeContentSha256':d['scopeContentSha256'],'recordId':d['provenance']['recordId'],'readingCoverage':d['readingCoverage']}for d in newscopes[::max(1,len(newscopes)//10)][:10]],'separateExplicitComponents':out['separateExplicitComponents'],'allPriorScopesAndRolesByteEquivalent':True};(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(compile_current(),ensure_ascii=False))
