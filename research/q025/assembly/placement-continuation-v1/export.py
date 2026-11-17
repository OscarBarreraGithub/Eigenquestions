"""Pack remaining eligible whole questions using exact scientific context and measured pilot costs."""
import collections,hashlib,json,math
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];F=ROOT/'research/q025/evaluation/full-pass';R=ROOT/'research/q025/assembly/organization-residual-v1';OUT=B/'inputs';OUT.mkdir(exist_ok=True)
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def read(p):return json.loads(p.read_text()),pin(p)
def write(p,x,compact=False):p.write_text(json.dumps(x,ensure_ascii=False,**({'separators':(',',':')}if compact else {'indent':2}))+'\n')
def encoded(x):return len(json.dumps(x,ensure_ascii=False,separators=(',',':')))
reg,rpin=read(F/'reconciliation-v1/authored-scope-registry-v6-20261117T144302Z.json');lanes,lpin=read(R/'refreshed-lanes.local.json');agg,apin=read(R/'candidate-6030-canonical-v3/aggregate.local.json');cat,catpin=read(ROOT/'research/q025/assembly/outputs/organization-candidate-6030-canonical-v3/catalog.json');eligible,epin=read(F/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json');pilot,ppin=read(R/'placement-pilot-delivery.json')
alias=cat['destinationAliases'];canon=lambda x:alias.get(x,x);scopes={d['id']:d for d in agg['destinations']if d['id']not in alias};contributions=list(agg['sourceContributions']);additional=[]
for p in sorted((F/'navigation-admissions-v2').glob('*-component.json')):
 c,cp=read(p);additional.append(cp)
 for d in c.get('destinations',[]):
  if d['id']in scopes:assert scopes[d['id']]['scopeContentSha256']==d['scopeContentSha256']
  else:scopes[d['id']]=d
 contributions+=c.get('sourceContributions',[])
pilot_ids=set()
for p in pilot['packets']:
 side,sp=read(ROOT/p['sidecar']['path']);assert sp==p['sidecar'];pilot_ids|={x['unitId']for x in side['units']}
assert len(pilot_ids)==87
needed=set(lanes['remainingRows'])-pilot_ids;assert len(needed)==2313 and needed<=set(eligible['unitIds']);assert not needed&{x['unitId']for x in agg['placements']if x['status']=='accepted'}
records={r['recordId']:r for r in reg['records']};reviews={r['reviewId']:r for r in reg['reviews']};contexts=collections.defaultdict(list)
for x in reg['unitAssessments']:
 if x['unitId']in needed:contexts[x['unitId']].append(x)
by_contribution=collections.defaultdict(list)
for x in contributions:
 if x['unitId']in needed:by_contribution[x['unitId']].append(x)
units={};manifest=json.loads((ROOT/'data/navigation/manifest.json').read_text())
for d in manifest['files']['units']:
 p=ROOT/'data/navigation'/d['path'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==d['sha256']
 for u in json.loads(raw):
  if u['id']in needed:units[u['id']]=u
assert set(units)==needed
scope_fields=('kind','title','question','summary','scope','readingCoverage','methods','aliases','scientificStatus')
scientific={id:{k:d[k]for k in scope_fields if k in d}for id,d in scopes.items()};scope_size={id:encoded(d)+50 for id,d in scientific.items()};options={};families={};row_cost={}
for uid in needed:
 target=set();fs=set()
 for x in lanes['remainingRows'][uid]:
  if canon(x['destinationId'])in scopes:target.add(canon(x['destinationId']))
 for a in contexts[uid]:
  r=records.get(a['reviewId']+':r')
  if r and canon(r['candidateId'])in scopes:target.add(canon(r['candidateId']));fs.add(scopes[canon(r['candidateId'])]['title'])
  for q in a['questionContributions']:
   r=records.get(q['recordId'])
   if r and canon(r['candidateId'])in scopes:target.add(canon(r['candidateId']))
  for stage in ['proposal','challenge']:
   id=canon(a['homeAgreement'][stage].get('candidateId'))
   if id in scopes:target.add(id)
 for q in by_contribution[uid]:
  id=canon(q['destinationId'])
  if id in scopes:target.add(id)
 options[uid]=target;families[uid]=fs;row_cost[uid]=len(units[uid]['text'])+sum(encoded(a['proposalAttribution'])+encoded(a['challengeAttribution'])+700 for a in contexts[uid])+1400
# Conservative envelope dominates all four measured maximum raw reply sizes.
# 10k fixed +2k per source +750 per prior review context; cap100k leaves20k margin.
def output_estimate(ids):return 10000+2000*len(ids)+750*sum(len(contexts[u])for u in ids)
remaining=set(needed);batches=[]
while remaining:
 pop=collections.Counter(f for u in remaining for f in families[u]);anchor=max(pop,key=lambda f:(pop[f],f))if pop else None
 pool=[u for u in remaining if anchor in families[u]]if anchor else list(remaining)
 start=min(pool,key=lambda u:(len(contexts[u]),sum(scope_size[x]for x in options[u]),u));chosen=[];targets=set();total=6000
 while True:
  fits=[]
  for uid in remaining-set(chosen):
   nc=total+row_cost[uid]+sum(scope_size[x]for x in options[uid]-targets)
   if nc>345000 or output_estimate(chosen+[uid])>100000:continue
   related=bool(families[uid]&families[start]);overlap=len(options[uid]&targets)
   fits.append((not related,-overlap/(1+len(options[uid])),nc-total,uid))
  if not fits:break
  uid=start if not chosen else min(fits)[3]
  # Ensure the selected initial unit satisfies both limits.
  if not chosen and uid not in {x[3]for x in fits}:uid=min(fits)[3]
  chosen.append(uid);total+=row_cost[uid]+sum(scope_size[x]for x in options[uid]-targets);targets|=options[uid]
 if not chosen:raise ValueError('One source exceeds measured envelope: '+start)
 batches.append(chosen);remaining-=set(chosen)
limits=['Complete source descriptions and both exact old per-unit annotations are retained; original source questions remain whole.','Existing admitted definitions are supplied without truncation. Their reading limits and source-era qualifiers remain local; no fresh primary-page reading is claimed.','Choose the most specific existing scientific scope covering the whole original question. More than one whole home needs an explicit reason and normalized weights. A compound union requires an exact complete description-span coverage map and separate adjudication; no atomic source units may be invented.','Prior unresolved annotations and inherited premise caveats remain exact. Distinguish missing words that affect allocation from historical annotation damage; never reconstruct missing wording.','New scopes remain proposals. Absence from this packet is NOT absence from the global admitted inventory: every new definition must undergo the pinned global exact-source/target-neighbor lookup before admission. A broader family is not automatically an equivalent fine question.','No new home, scope, role, alias or navigation is admitted by this export. No default numerical-bin home.','Original p*/q*/x*/f*/e* annotations belong to their reviewRef namespace. Use resolved q* IDs for new choices; an unresolved old ref is not a fabricated candidate.']
packets=[];seen=set();all_source_pins={}
for bi,chosen in enumerate(batches):
 fid=f'placement-continuation-{bi:04d}';target_ids=set().union(*(options[u]for u in chosen));qrefs={id:'q'+str(i)for i,id in enumerate(sorted(target_ids))};rids=sorted({a['reviewId']for u in chosen for a in contexts[u]});rrefs={id:'r'+str(i)for i,id in enumerate(rids)};refreg={q:{'kind':'admitted_scope','destinationId':id,'scopeContentSha256':scopes[id]['scopeContentSha256']}for id,q in qrefs.items()};rows=[];vrows=[];bindings=[]
 for i,uid in enumerate(chosen):
  assert uid not in seen;seen.add(uid);u=units[uid];ref='u'+str(i);assert hashlib.sha256(u['text'].encode()).hexdigest()==u['evidence']['textSha256'];old=[];now=[];vcontexts=[];sourcepins=[]
  for a in contexts[uid]:
   rv=reviews[a['reviewId']];resolved=[]
   for q in a['questionContributions']:
    r=records.get(q['recordId']);id=canon(r['candidateId'])if r else None
    if id in qrefs:resolved.append({'scopeRef':qrefs[id],'role':q['role'],'independentRoleAgreement':q['independentRoleAgreement']})
   common={'reviewId':a['reviewId'],'sourceOrigin':a['sourceOrigin'],'resolvedTypedContributions':resolved,'homeAgreement':a['homeAgreement']};old.append({**common,'original':a['proposalAttribution']});now.append({**common,'original':a['challengeAttribution']});sourcepins.append({'reviewId':rv['reviewId'],'pins':rv['pins'],'proposalDependency':rv['proposalDependency'],'challengeArtifact':rv['challengeArtifact']});h=a['homeAgreement'];vcontexts.append({'reviewRef':rrefs[a['reviewId']],'sourceOrigin':a['sourceOrigin'],'proposal':a['proposalAttribution'],'challenge':a['challengeAttribution'],'resolvedContributions':resolved,'resolvedProposalHomeRef':qrefs.get(canon(h['proposal'].get('candidateId'))),'resolvedChallengeHomeRef':qrefs.get(canon(h['challenge'].get('candidateId'))),'sameExplicitScientificCard':h['sameExplicitScientificCard'],'proposalDefinitionMatchesPinnedOriginal':h['proposalDefinitionMatchesPinnedOriginal'],'unchangedSupportedScope':h['unchangedSupportedScope'],'placementAlreadyAdmitted':False})
  row={'ref':ref,'unitId':uid,'paperId':u['paperId'],'description':u['text'],'descriptionSha256':u['evidence']['textSha256'],'proposalAttributions':old,'challengeAttributions':now,'candidateHomeRefs':[qrefs[x]for x in sorted(options[uid])],'existingHomeRefs':[],'coverageIssue':{'bucket':'residual_scientific_placement','priorCensus':lanes['remainingRows'][uid]},'originalSourceQuestionMustRemainWhole':True};rows.append(row)
  vr={'ref':ref,'paperId':u['paperId'],'description':u['text'],'priorContexts':vcontexts,'candidateHomeRefs':row['candidateHomeRefs'],'existingHomeRefs':[],'coverageIssue':{'bucket':row['coverageIssue']['bucket'],'contexts':[{'reviewRef':rrefs[x['reviewId']],'candidateHomeRef':qrefs.get(canon(x['destinationId'])),'exclusionReasons':x['exclusionReasons']}for x in lanes['remainingRows'][uid]]},'originalSourceQuestionMustRemainWhole':True};vrows.append(vr);assert vr['description']==row['description'];assert [x['proposal']for x in vcontexts]==[x['original']for x in old]and[x['challenge']for x in vcontexts]==[x['original']for x in now]
  bindings.append({'unitRef':ref,'unitId':uid,'browserVectorRow':u['vectorRow'],'textSha256':u['evidence']['textSha256'],'reviewContexts':sourcepins});refreg[ref]={'kind':'source_question','unitId':uid,'paperId':u['paperId'],'descriptionSha256':u['evidence']['textSha256']}
 selection={'scientificFamilies':sorted(set().union(*(families[u]for u in chosen))),'unitCount':len(chosen),'noSealedSourceText':True,'packingBasis':'Shared admitted scope definitions and reviewed scientific family labels; not proposed source homes','estimatedReplyCharacters':output_estimate(chosen),'replyEnvelopePolicy':'10,000 +2,000*sourceCount+750*priorContextCount <=100,000; remaining20,000 of120k guard is reserve.'}
 side={'schemaVersion':'q025-placement-decision-input/1','familyId':fid,'units':rows,'scopes':[{'ref':qrefs[id],'id':id,'scopeContentSha256':scopes[id]['scopeContentSha256'],'destination':scopes[id]}for id in sorted(target_ids)],'refRegistry':refreg,'machineBindings':{'registry':rpin,'scopeComponent':apin,'additionalComponents':additional,'canonicalProjection':catpin,'residualInventory':lpin,'eligibleInventory':epin,'units':bindings},'readingLimits':limits,'selection':selection};sp=OUT/(fid+'.json');write(sp,side)
 view={'schemaVersion':'q025-placement-scientific-view/1','familyId':fid,'units':vrows,'scopes':[{'ref':qrefs[id],**scientific[id]}for id in sorted(target_ids)],'readingLimits':limits,'selection':selection,'sidecar':pin(sp),'reviewNamespaces':{ref:id for id,ref in rrefs.items()}};vp=OUT/(fid+'.view.json');write(vp,view,True);assert len(vp.read_text())<=350000,(fid,len(vp.read_text()));packets.append({'familyId':fid,'view':pin(vp),'sidecar':pin(sp),'units':len(rows),'scopes':len(target_ids),'priorContexts':sum(len(contexts[u])for u in chosen),'viewCharacters':len(vp.read_text()),'estimatedReplyCharacters':output_estimate(chosen),'completeDescriptionsAndBothAnnotationsVerified':True})
assert seen==needed
inventory={'unitIds':sorted(needed),'excludedPilotUnitIds':sorted(pilot_ids),'eligibleInventory':epin,'scopeInventory':[{'id':id,'scopeContentSha256':d['scopeContentSha256']}for id,d in sorted(scopes.items())],'scopeComponents':[apin]+additional,'canonicalProjection':catpin,'globalNewScopeGate':'Exact-source overlap and full title/target neighbor review across this inventory before admitting any new definition; no unreviewed absence claim.'};write(B/'inventory.local.json',inventory)
report={'schemaVersion':'q025-placement-pilot-delivery/1','status':'prepared_sources_only_no_native_launch','packets':packets,'distinctSources':len(seen),'excludedPilotCount':len(pilot_ids),'reservedSourceTextsOpened':0,'inputs':{'registry':rpin,'aggregate':apin,'residual':lpin,'pilot':ppin,'eligible':epin,'additionalScopes':additional},'inventory':pin(B/'inventory.local.json'),'script':pin(Path(__file__)),'packing':{'packets':len(packets),'estimatedNativeCalls':2*len(packets),'sourceCounts':{'min':min(x['units']for x in packets),'max':max(x['units']for x in packets)},'maxViewCharacters':max(x['viewCharacters']for x in packets),'maxViewBytes':max(x['view']['bytes']for x in packets),'maxEstimatedReplyCharacters':max(x['estimatedReplyCharacters']for x in packets),'pilotMeasuredReplyCharacters':{'annotation':53898,'coverage':61856,'competing':88398,'absent':62785}},'admissionPolicy':'No scientific admission. Paired whole-home agreements may feed an explicitly coordinator-approved class; new scopes, changed choices, compound unions or material premise uncertainty remain separately adjudicated.'};write(B/'delivery.json',report);print(json.dumps({k:report[k]for k in ['status','distinctSources','packing']},indent=2))
