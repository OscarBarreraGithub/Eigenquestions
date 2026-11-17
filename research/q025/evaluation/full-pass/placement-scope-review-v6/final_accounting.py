"""Pin final unresolved sources and a non-scientific summary-flag correction."""
import hashlib,json,pathlib
W=pathlib.Path(__file__).resolve().parents[5]
B=pathlib.Path(__file__).resolve().parent
F=B.parent
def read(p): return json.loads((W/p).read_text())
def pin(p):
 p=W/p;b=p.read_bytes();return {'path':str(p.relative_to(W)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(p,obj):
 p=W/p;b=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 if p.exists(): assert p.read_bytes()==b, f'Frozen output differs: {p}'
 else:p.write_bytes(b)
 return pin(str(p.relative_to(W)))
def build():
 rows=[];inputs=[]
 for cut in ['02','03','04','05']:
  p=f'research/q025/assembly/placement-incremental-v1/cut-{cut}/exception-intake.json';d=read(p);inputs.append(pin(p))
  for i,r in enumerate(d['rows']):
   c=r['challengeJudgment']
   if c['status']!='unresolved':continue
   assert not c['homes'] and c['coverageMode']=='unresolved' and c['wholeTargetCoverage']=='incomplete'
   assert hashlib.sha256(r['description'].encode()).hexdigest()==r['descriptionSha256']
   rows.append({'unitId':r['unitId'],'paperId':r['paperId'],'descriptionSha256':r['descriptionSha256'],'familyId':r['familyId'],'unitRef':r['unitRef'],'cut':cut,'rowIndex':i,'outcome':'unresolved_scientific_home','identityStatus':'unresolved_source_facet','allocationWeight':0,'reason':c['reason'],'coverageReason':c['coverageReason'],'missingPremises':c['missingPremises'],'proposalStatus':r['proposalJudgment']['status'],'independentPlacementReview':r['independentPriorPlacementReview'],'decisionBasis':'Complete immutable source description and paired attribution/placement judgments; no new primary reading. Missing premises concern the physical target/context, not a demand to solve the question.','exactInput':inputs[-1],'nativeInputs':r['inputs'],'preserveSupportedAccess':True,'inventedQuestionOrHome':False})
 p='research/q025/evaluation/full-pass/placement-scope-review-v4/changed-home-adjudication.json';a=read(p);ap=pin(p);extra=[r for r in a['rows']if r['outcome']=='withheld_existing_home'];assert len(extra)==1
 r=extra[0];d=read('research/q025/assembly/placement-incremental-v1/cut-03/exception-intake.json');s=next(x for x in d['rows']if x['unitId']==r['unitId'])
 rows.append({'unitId':r['unitId'],'paperId':s['paperId'],'descriptionSha256':r['descriptionSha256'],'familyId':r['familyId'],'unitRef':r['unitRef'],'cut':'03','rowIndex':d['rows'].index(s),'outcome':'coordinator_withheld_scientific_home','identityStatus':'unresolved_source_facet','allocationWeight':0,'reason':r['qualification'],'coverageReason':r['originalProposal']['coverageReason'],'missingPremises':r['originalProposal']['missingPremises'],'proposalStatus':s['proposalJudgment']['status'],'independentPlacementReview':s['independentPriorPlacementReview'],'decisionBasis':'Root read the exact source, both judgments and complete proposed target. Qualified access in the dark-sector scope does not establish a whole scientific home. No new primary reading.','exactInput':ap,'nativeInputs':s['inputs'],'preserveSupportedAccess':True,'inventedQuestionOrHome':False})
 rows.sort(key=lambda r:r['unitId']);assert len(rows)==len({r['unitId']for r in rows})==31
 out={'schemaVersion':'q025-final-eligible-unresolved-sources/1','authority':'root_completion_policy_and_explicit_quiver_withholding','counts':{'eligibleSources':8430,'resolvedScientificHomesExpected':8399,'unresolvedEligibleSources':31,'reservedSources':43,'totalSourceQuestions':8473},'countMeaning':'8399 is the consolidated admission expectation, to be checked against the actual assembly. These 31 eligible sources have zero semantic allocation but retain source/facet discovery and independently supported access. The separate 43 reserved sources remain sealed before candidate freeze.','sourceFacetAccessRequired':True,'reservedContentRead':False,'newModelCalls':0,'freshPrimaryReading':False,'inputCuts':inputs,'explicitRootWithholding':ap,'unitIdsSha256':hashlib.sha256('\n'.join(r['unitId']for r in rows).encode()).hexdigest(),'rows':rows}
 account=save(str((B/'unresolved-source-accounting.json').relative_to(W)),out)
 p='research/q025/evaluation/full-pass/placement-scope-review-v5/changed-home-adjudication.json';d=read(p);changes=[]
 for r in d['rows']:
  assert r['coverageModeMustRemain']==r['exactChallenge']['coverageMode']
  expected=r['coverageModeMustRemain']=='explicit_compound_union'
  if r['compoundUnion']!=expected: changes.append({'rowIndex':r['index'],'unitId':r['unitId'],'path':f"/rows/{r['index']}/compoundUnion",'old':r['compoundUnion'],'new':expected,'authoritativeCoverageMode':r['coverageModeMustRemain']})
 assert len(changes)==19
 fix=save(str((F/'placement-scope-review-v5/changed-home-summary-correction.json').relative_to(W)),{'schemaVersion':'q025-derived-summary-flag-correction/1','original':pin(p),'transform':'For each row, set the convenience compoundUnion summary to (coverageModeMustRemain == explicit_compound_union), after verifying that this exact mode equals exactChallenge.coverageMode. Original receipt remains immutable.','changes':changes,'scientificContentChanged':False,'homesScopesMapsWeightsReadingBasisChanged':False,'currentSemantics':'Exact challenge coverageMode, source-span targetCoverage and normalized weights are authoritative. Each union component covers its mapped target only, never the whole source per home.','rootAuthorization':'Root explicitly approved these exact compound target maps and organizational weights; this corrects only the contradictory convenience summary.'})
 print(json.dumps({'unresolved':account,'summaryCorrection':fix},indent=2))
if __name__=='__main__':build()
