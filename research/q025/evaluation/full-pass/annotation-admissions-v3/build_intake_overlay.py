"""Make exact annotation resolutions usable without mutating pinned reviews."""
import collections,hashlib,json,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];sys.path.insert(0,str(F/'findings-v1'));from audit_field_completeness import screen
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();textsha=lambda s:hashlib.sha256(s.encode()).hexdigest()
REG=F/'reconciliation-v1/authored-scope-registry-v4-20261117T131639Z.json'

def apply_scope_resolution(record,resolution):
 assert record['recordId']==resolution['recordId']
 assert textsha(record['assessment']['note'])==resolution['originalTextSha256']
 result=dict(record);result['assessment']={**record['assessment'],'note':resolution['replacementText']}
 result['admissionJustificationFlags']=[]
 result['annotationResolution']={k:v for k,v in resolution.items() if k!='replacementText'}
 result['originalAdmissionAssessment']=record['assessment'];result['originalAdmissionJustificationFlags']=record['admissionJustificationFlags']
 return result

def main():
 registry=json.loads(REG.read_text());paths=[F/'annotation-admissions-v1/pilot-annotation-admissions.json',F/'annotation-admissions-v2/annotation-admissions.json',B/'explicit-adjudications.json'];admitted=[]
 for p in paths:
  for row in json.loads(p.read_text())['rows']:admitted.append((row,{'path':str(p.relative_to(W)),'sha256':sha(p)}))
 annotation=[(r,p) for r,p in admitted if r['scopeImpact']=='annotation_only'];premise=[(r,p) for r,p in admitted if r['scopeImpact']=='premise_change'];assert len(annotation)==56 and len(premise)==1
 scope_resolutions=[];factor_resolutions=[];matched=collections.Counter()
 for record in registry['records']:
  if not record.get('assessment'):continue
  note=record['assessment']['note'];cid=record['recordId']+':note'
  matches=[(a,p) for a,p in annotation if a['caseId']==cid and a['originalTextSha256']==textsha(note)]
  if not matches:continue
  assert len(matches)==1;a,p=matches[0]
  assert not screen({'cardReviews':[{'id':record['localRef'],'note':a['replacementText']}]})[0]
  resolution={'recordId':record['recordId'],'caseId':a['caseId'],'originalTextSha256':a['originalTextSha256'],'replacementText':a['replacementText'],'replacementTextSha256':a['replacementTextSha256'],'annotationAdmission':p,'resolvedFlags':record['admissionJustificationFlags'],'scopeDefinitionUnchanged':True,'doesNotAlterScopeAgreement':True};scope_resolutions.append(resolution);matched[a['caseId']]+=1
 for factor in registry['factors']:
  qualification=factor['definition']['qualification'];families=set(re.findall(r'[0-9a-f]{20}',factor['reviewId']))
  for a,p in admitted:
   if a['originalTextSha256']!=textsha(qualification):continue
   if not families.intersection(re.findall(r'[0-9a-f]{20}',a['caseId'])):continue
   factor_resolutions.append({'factorRef':factor['factorRef'],'caseId':a['caseId'],'originalTextSha256':a['originalTextSha256'],'replacementText':a['replacementText'],'replacementTextSha256':a['replacementTextSha256'],'scopeImpact':a['scopeImpact'],'annotationAdmission':p,'originalDefinitionRetained':True,'effectiveQualificationStatus':'admitted_annotation_only' if a['scopeImpact']=='annotation_only' else 'explicit_premise_amendment_dependent_inferences_pending','dependencyRevalidationRequired':a['scopeImpact']=='premise_change'});matched[a['caseId']]+=1
 amended_refs={x['factorRef'] for x in factor_resolutions if x['scopeImpact']=='premise_change'};dependent_units=[a for a in registry['unitAssessments'] if amended_refs.intersection(a['factorRefs'])];dependent_contributions=[{'recordId':r['recordId'],'candidateId':r['candidateId'],'unitId':c['unitId'],'role':c['role'],'factorRefs':sorted(amended_refs.intersection(c['factorRefs']))} for r in registry['records'] for c in r['contributions'] if amended_refs.intersection(c['factorRefs'])];unitids={a['unitId'] for a in dependent_units};records={x['recordId'] for x in dependent_contributions};homes=json.loads((F/'home-admissions-v1/home-admission-delta.json').read_text());affected_homes=[{'unitId':p['unitId'],'destinationId':p['destinationId'],'decisionId':p['decisionId']} for p in homes['placements'] if p['unitId'] in unitids]
 # The mechanical dependency inventory is a conservative flag, not an assertion
 # that each question or placement actually relies on the withdrawn premise.
 audit={'schemaVersion':'q025-premise-amendment-dependency-audit/1','caseId':premise[0][0]['caseId'],'amendmentAdmission':premise[0][1],'amendedFactorRefs':sorted(amended_refs),'dependentUnitAssessments':[{'reviewId':a['reviewId'],'unitId':a['unitId'],'paperId':a['paperId'],'factorRefs':sorted(amended_refs.intersection(a['factorRefs'])),'homeAgreement':a['homeAgreement'],'proposalNote':a['proposalAttribution']['note'],'challengeNote':a['note']} for a in dependent_units],'dependentScopeContributions':dependent_contributions,'affectedExisting1055Homes':affected_homes,'dependentScopeDefinitions':[{'recordId':r['recordId'],'candidateId':r['candidateId'],'definition':r['definition']} for r in registry['records'] if r['recordId'] in records],'status':'explicit_revalidation_required_if_an_inference_relies_on_withdrawn_premise','qualifications':'This inventory follows exact factor references. It does not assert that every listed scoped question relies on the withdrawn premise; intact source-target agreement may survive a separate substantive inspection. No factor premise is promoted through all same-paper units.'}
 ap=B/'premise-dependency-audit.json';ap.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 out={'schemaVersion':'q025-resolved-annotation-intake-overlay/1','registry':{'path':str(REG.relative_to(W)),'sha256':sha(REG)},'scopeAssessmentResolutions':scope_resolutions,'factorQualificationResolutions':factor_resolutions,'premiseDependencyAudit':{'path':str(ap.relative_to(W)),'sha256':sha(ap)},'unmatchedAdmittedCases':[{'caseId':a['caseId'],'reason':'No exact current selected-lineage field match; retain admission without applying to another field.'} for a,p in admitted if not matched[a['caseId']]],'originalRegistryChanged':False,'publicAdmissionChanges':0,'coverageLimit':'This applies the bounded original58-case repair queue only. Later raw outputs require a fresh field-completeness scan.'}
 op=B/'intake-overlay.json';op.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');report={'scopeAssessmentResolutions':len(scope_resolutions),'factorQualificationResolutions':len(factor_resolutions),'resolvedScopeFlagRecords':sum(bool(x['resolvedFlags']) for x in scope_resolutions),'unmatchedCases':len(out['unmatchedAdmittedCases']),'premiseDependentUnits':len(unitids),'premiseDependentContributions':len(dependent_contributions),'affectedExisting1055Homes':len(affected_homes),'overlay':{'path':str(op.relative_to(W)),'sha256':sha(op)},'premiseAudit':out['premiseDependencyAudit'],'originalRegistryUnchanged':sha(REG)==out['registry']['sha256']};(B/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
