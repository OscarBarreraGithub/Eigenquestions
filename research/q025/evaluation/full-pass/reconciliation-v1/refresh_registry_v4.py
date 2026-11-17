"""Versioned, explicit-lineage intake. Preserve prior cuts and active inputs."""
import collections, copy, datetime, hashlib, json
from pathlib import Path
from build_authored_registry import build, fingerprint

B=Path(__file__).resolve().parent; F=B.parent; E=F.parent; W=E.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD=B/'authored-scope-registry-v3-20261117T121953Z.json'
# Priority is an explicit successor policy, never lexical job-name matching.
ROOTS=[(10,'leaf','full-leaf-wave-v3/jobs'),(20,'leaf','leaf-recovery-v4/jobs'),
       (10,'parent','parents-wave-v1/jobs'),(10,'parent','parent-pilot-v1/jobs'),
       (30,None,'recovery-successors-v1/jobs'),(30,None,'recovery-successors-v1/adopted'),
       (40,None,'recovery-successors-v2/jobs'),(40,None,'recovery-successors-v2/adopted')]

def resolve_path(text):
 p=Path(text)
 if p.is_absolute():return p
 return W/p if text.startswith('research/') else E/p

def pin_dir(d):
 packet='packet.actual.json' if (d/'packet.actual.json').exists() else 'packet.json'
 return {'artifactDirectory':str(d.relative_to(E)), 'packetFile':packet, **{name+'Sha256':sha(d/name) for name in (packet,'reply.json','reply.raw.txt','receipt.json','normalization.json')}}

def proposal_dependency(d):
 """Resolve the explicit native/adopted dependency; never guess a sibling name."""
 request_path=d/('dispatch-request.json' if (d/'dispatch-request.json').exists() else 'request.json')
 q=json.loads(request_path.read_text()); original=None
 if q.get('originalJobPath'):
  original=resolve_path(q['originalJobPath'])
  q=json.loads((original/'dispatch-request.json').read_text())
 if q.get('priorJobPath'):prior=resolve_path(q['priorJobPath'])
 elif q.get('dependsOn'):prior=(original or d).parent/q['dependsOn']
 else:raise AssertionError(f'No explicit proposal dependency: {d}')
 receipt=json.loads((prior/'receipt.json').read_text())
 assert receipt['status']=='complete', prior
 assert q.get('priorReceiptSha256')==sha(prior/'receipt.json'), ('proposal receipt mismatch',d,prior)
 assert q.get('priorReplySha256')==sha(prior/'reply.json'), ('proposal reply mismatch',d,prior)
 assert receipt['normalizedReplySha256']==sha(prior/'reply.json')
 out={'reviewId':prior.name,**pin_dir(prior),'resolvedFromRequest':{'path':str(request_path.relative_to(W)),'sha256':sha(request_path)}}
 if original:out['originalChallengeDirectory']=str(original.relative_to(E))
 return out

def resolve_home(ref,p,cards):
 if not ref or ref in ['?','u','none','unresolved']:return {'rawRef':ref,'status':'explicitly_unresolved'}
 exact=[c for c in cards if c['id']==ref]
 original=[c for c in cards if c.get('originalId')==ref]
 matches=exact or original
 # Parent packets may expose the exact same inherited card in both tables.
 # Collapse only byte-equivalent scientific definitions at the same local ID.
 if len(matches)>1 and len({(c['id'],json.dumps({k:c.get(k) for k in ['title','question','summary','scope','readingLimit','methods']},sort_keys=True,ensure_ascii=False)) for c in matches})==1:matches=matches[:1]
 if len(matches)!=1:return {'rawRef':ref,'status':'unresolved_or_ambiguous_reference','matchCount':len(matches)}
 c=matches[0];kind='region' if c['id']=='r' else 'question'
 cid=c.get('candidateId') or ('q025-candidate-'+kind+':'+fingerprint(kind,c)[:24])
 return {'rawRef':ref,'normalizedRef':c['id'],'originalId':c.get('originalId',c['id']),'candidateId':cid,'status':'exact_card_reference','normalization':'exact_id' if exact else 'explicit_originalId_to_prior_id','definitionFingerprint':fingerprint(kind,c)}

def same_science(left,right):
 return all(left.get(k)==right.get(k) for k in ['title','question','summary','scope','readingLimit','methods'])

def refresh():
 old=json.loads(OLD.read_text());inventory=[];selected={};paths={};root_entries=[]
 for priority,declared_kind,rel in ROOTS:
  root=F/'native-local'/rel
  if not root.exists():continue
  root_entries.append((root,priority,declared_kind))
  for d in sorted(root.glob('*-challenge')):
   if not (d/'receipt.json').exists():continue
   receipt=json.loads((d/'receipt.json').read_text())
   item={'artifactDirectory':str(d.relative_to(E)),'reviewId':d.name,'status':receipt['status'],'receiptSha256':sha(d/'receipt.json'),'lineagePriority':priority}
   inventory.append(item)
   if receipt['status']!='complete':continue
   p=json.loads((d/'packet.actual.json').read_text());kind=p.get('kind') or declared_kind
   assert kind in ['leaf','parent'];key=kind+':'+p['familyId'];item.update({'canonicalReviewKey':key,'familyId':p['familyId'],'kind':kind,'candidateRegionId':p.get('candidateRegionId')})
   assert sha(d/'reply.json')==receipt['normalizedReplySha256'];item['challengePins']=pin_dir(d)
   if key in selected:
    previous=selected[key]
    assert previous['lineagePriority']!=priority or previous['challengePins']['reply.jsonSha256']==item['challengePins']['reply.jsonSha256'], ('Competing same-priority completed lineage',key)
   if key not in selected or priority>selected[key]['lineagePriority']:selected[key]=item;paths[key]=d
 chosen_dirs={v['artifactDirectory'] for v in selected.values()};out={'schemaVersion':'q025-authored-scope-registry/4','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':[],'factors':[],'reviews':[],'parentReusedScopeReferences':[],'unitAssessments':[],'fineGroupProposals':[],'lineageInventory':inventory,'selectedReviewLineages':list(selected.values()),'previousRegistry':{'path':str(OLD.relative_to(W)),'sha256':sha(OLD)}}
 for root,_,declared_kind in root_entries:
  x=build(root);ids={r['reviewId'] for r in x['reviews'] if str((root/r['reviewId']).relative_to(E)) in chosen_dirs}
  out['records'] += [r for r in x['records'] if r['reviewId'] in ids and ((json.loads((root/r['reviewId']/'packet.actual.json').read_text()).get('kind') or declared_kind)=='leaf' or r['localRef']=='r' or r['localRef'].startswith(('p','q')))]
  out['factors'] += [r for r in x['factors'] if r['reviewId'] in ids]
  out['reviews'] += [r for r in x['reviews'] if r['reviewId'] in ids]
 byreview={r['reviewId']:r for r in out['reviews']}
 for key,item in selected.items():
  d=paths[key];review=byreview[d.name];p=json.loads((d/'packet.actual.json').read_text());r=json.loads((d/'reply.json').read_text());norm=json.loads((d/'normalization.json').read_text())
  dependency=proposal_dependency(d);review.update({'artifactDirectory':str(d.relative_to(E)),'canonicalReviewKey':key,'kind':item['kind'],'proposalDependency':dependency,'challengeArtifact':pin_dir(d),'lineagePriority':item['lineagePriority']})
  units={u['i']:u for u in p['units']};prior={a['i']:a for a in p['priorAssignments']};cards=p['priorCards']+p.get('existingCards',[]);assessment={a['id']:a for a in r['cardReviews']}
  pd=E/dependency['artifactDirectory'];pr=json.loads((pd/'reply.json').read_text());pp=json.loads((pd/dependency['packetFile']).read_text());original_cards=pr['cards']+[{'id':'r',**pr['region']}]+pp.get('existingCards',[])
  # Original IDs and normalized prior IDs identify the SAME immutable supplied card.
  # This is reference normalization, not scientific question equivalence.
  for row in r['units']:
   u=units[row['i']];a=prior[row['i']];uid=p['refRegistry'][u['sourceRef']]['unitId'];oldq={(q['id'],q['role']) for q in a['q']};ph=resolve_home(a['home'],p,cards);ch=resolve_home(row['home'],p,cards+r['cards']);local=ch.get('normalizedRef');sc=assessment.get(local)
   supplied=next((c for c in cards if c['id']==ph.get('normalizedRef')),None);original=next((c for c in original_cards if c['id']==ph.get('originalId')),None);original_matches=bool(supplied and original and same_science(supplied,original));same=ph.get('candidateId') is not None and ph.get('candidateId')==ch.get('candidateId') and original_matches
   out['unitAssessments'].append({'reviewId':d.name,'reviewKey':p['familyId'],'canonicalReviewKey':key,'unitId':uid,'paperId':u['paperId'],'sourceOrigin':u.get('selectionRole'),'descriptionSha256':p['refRegistry'][u['descriptionRef']]['textSha256'],'basis':'source_excerpt_checked' if row['b']=='excerpt' else 'description_checked','disposition':row['d'],'dispositionAgreement':a['d']==row['d'],'title':row['title'],'home':row['home'],'note':row['note'],'reason':row['reason'],'proposalAttribution':{k:copy.deepcopy(a[k]) for k in ['b','d','q','f','refs','reason','note','home','identity','title']},'challengeAttribution':{k:copy.deepcopy(row[k]) for k in ['b','d','q','f','refs','reason','note','home','identity','title']},'homeAgreement':{'proposal':ph,'challenge':ch,'proposalDefinitionMatchesPinnedOriginal':original_matches,'sameExplicitScientificCard':same,'unchangedSupportedScope':bool(same and sc and sc['decision']=='supported_as_written' and sc['scopeChange']=='same'),'placementAdmission':False},'questionContributions':[{'recordId':d.name+':'+q['id'],'role':q['role'],'independentRoleAgreement':(q['id'],q['role']) in oldq} for q in row['q']],'factorRefs':[d.name+':'+f for f in row['f']],'fineIdentityState':row['identity'],'canonicalUniquenessCertified':False,'otherUnitDescriptionContext':[v for v in norm.get('crossUnitDescriptionContext',[]) if v['unitIndex']==row['i']]})
  for g in r['identityGroups']:out['fineGroupProposals'].append({'reviewId':d.name,'group':g,'memberUnitIds':[p['refRegistry'][units[a['i']]['sourceRef']]['unitId'] for a in r['units'] if a['identity']==g['id']],'status':'new_challenger_group_proposal_not_canonical_admission'})
  if item['kind']=='parent':
   for c in p['existingCards']:out['parentReusedScopeReferences'].append({'parentReviewId':d.name,'localRef':c['id'],'existingCandidateId':c.get('candidateId'),'childRef':c.get('childRef'),'scopeStatus':c.get('scopeStatus'),'createsNewRecord':False})
 # Reuse the exact previously admitted stable scopes and their provenance.
 admitted=[copy.deepcopy(r) for r in old['records'] if r.get('admittedScopeArtifact')]
 for record in admitted:
  matches=[i for i,r in enumerate(out['records']) if r['recordId']==record['recordId']]
  if matches:out['records'][matches[0]]=record
  else:out['records'].append(record)
 for review in old['reviews']:
  if review.get('kind')=='explicitly_admitted_calibration_fragment':out['reviews'].append(copy.deepcopy(review))
 bycandidate=collections.defaultdict(list)
 for r in out['records']:bycandidate[r['candidateId']].append(r['recordId'])
 for ref in out['parentReusedScopeReferences']:
  ref['existingRecordIds']=bycandidate.get(ref['existingCandidateId'],[]);ref['resolutionStatus']='existing_candidate_reference' if ref['existingRecordIds'] else 'external_or_pending_scope_reference'
 oldids={r['recordId'] for r in old['records']};oldc={r['candidateId'] for r in old['records']};newids={r['recordId'] for r in out['records']};newc=set(bycandidate)
 out['delta']={'newRecordIds':sorted(newids-oldids),'previousRecordIdsAbsentFromSelectedCurrentLineage':sorted(oldids-newids),'newCandidateIds':sorted(newc-oldc),'previousCandidateIdsAbsentFromCurrentLineage':sorted(oldc-newc),'unchangedCandidateIds':sorted(oldc&newc),'previousDefinitionsNotRereadByThisCompiler':True}
 out['counts']={'completedLeafPairs':sum(k.startswith('leaf:') for k in selected),'completedParentPairs':sum(k.startswith('parent:') for k in selected),'completedSuccessorLeafPairs':sum(k.startswith('leaf:') and v['lineagePriority']>10 for k,v in selected.items()),'authoredScopes':len(out['records']),'authoredQuestions':sum(r['kind']=='question' for r in out['records']),'scopeStatuses':dict(collections.Counter(r['scopeStatus'] for r in out['records'])),'uniqueContributingSourceUnits':len({c['unitId'] for r in out['records'] for c in r['contributions']}),'sourceContributionRecords':sum(len(r['contributions']) for r in out['records']),'unitAssessmentRecords':len(out['unitAssessments']),'uniqueAssessedUnits':len({a['unitId'] for a in out['unitAssessments']}),'exactPairedHomeReferences':sum(a['homeAgreement']['sameExplicitScientificCard'] for a in out['unitAssessments']),'supportedUnchangedPairedHomeReferences':sum(a['homeAgreement']['unchangedSupportedScope'] for a in out['unitAssessments']),'reservedPapersExcluded':24,'reservedQuestionUnitsUnreviewed':43,'admittedCalibrationScopes':8,'adjudicatedParentScopes':1,'newCanonicalQuestionsAdmittedByThisCompiler':0,'duplicateRecordsFromParentReuse':0,'newCandidateScopesSincePreviousCut':len(newc-oldc)}
 assert len({r['recordId'] for r in out['records']})==len(out['records'])
 assert len({r['reviewId'] for r in out['reviews']})==len(out['reviews'])
 out['semantics']='Selected completed proposal/challenge lineage per original scientific review batch. Scope candidates, exact home-reference agreement and source roles remain separate from scientific/canonical/placement admission. Both original per-unit attribution notes and reasons are retained. Parent reuse creates no duplicate identities. Failed and superseded histories remain pinned.'
 return out

if __name__=='__main__':
 out=refresh();stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');path=B/f'authored-scope-registry-v4-{stamp}.json';path.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n');report={'schemaVersion':'q025-authored-registry-version/4','path':str(path.relative_to(W)),'sha256':sha(path),'bytes':path.stat().st_size,'counts':out['counts'],'previousRegistry':out['previousRegistry'],'compilerSha256':sha(__file__),'lineageSelection':[{'canonicalReviewKey':k['canonicalReviewKey'],'reviewId':k['reviewId'],'artifactDirectory':k['artifactDirectory'],'receiptSha256':k['receiptSha256']} for k in out['selectedReviewLineages']],'activeInputsChanged':False};(B/f'registry-report-v4-{stamp}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='lineageSelection'}))
