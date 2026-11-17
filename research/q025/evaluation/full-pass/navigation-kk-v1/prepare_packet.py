"""Connect the reviewed dark-sector hierarchy to fixed admitted KK destinations."""
import collections,copy,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];L=F/'native-local/navigation-kk-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':str(p.relative_to(W)),'sha256':sha(p)}
nompath=E.parent/'assembly/organization-v4/kk-navigation-nominations.json';nom=json.loads(nompath.read_text());regpath=F/'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json';R=json.loads(regpath.read_text());records={x['recordId']:x for x in R['records']};reviews={x['reviewId']:x for x in R['reviews']};fixedpath=F/'organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json';fixed=json.loads(fixedpath.read_text());current=[records[x['recordId']]for x in nom['scopes']];fixedscopes=[x for x in fixed['destinations']if x['id']in nom['stableControlIds']];assert len(fixedscopes)==4
uidset={c['unitId']for r in current[:5]for c in r['contributions']}
for d in fixedscopes:uidset.update(d['evidenceIds'])
for r in current[5:]:
 if r['contributions']:uidset.add(r['contributions'][0]['unitId'])
units={};originals={};loaded={}
def load(reviewid):
 if reviewid not in loaded:
  d=E/reviews[reviewid]['artifactDirectory'];loaded[reviewid]=json.loads((d/'packet.actual.json').read_text())
 return loaded[reviewid]
for a in R['unitAssessments']:
 if a['unitId']not in uidset or a['unitId']in units:continue
 p=load(a['reviewId']);u=next(u for u in p['units']if p['refRegistry'][u['descriptionRef']]['unitId']==a['unitId']);units[a['unitId']]={'unitId':a['unitId'],'paperId':u['paperId'],'description':u['description']};originals[a['unitId']]=p['refRegistry'][u['descriptionRef']]
assert set(units)==uidset;umap={uid:f'u{i}'for i,uid in enumerate(sorted(units))};refs={};scopes=[];scopebindings={};cidmap={};notes=[]
for i,r in enumerate(current):
 ref=f'c{i}';cidmap[r['candidateId']]=ref;scopes.append({'ref':ref,'kind':r['kind'],'scopeStatus':r['scopeStatus'],'definition':r['definition'],'methods':r['methods'],'priorReadingAssessment':r['assessment'],'sourceContributions':[{'unitRef':umap[c['unitId']],'role':c['role'],'basis':c['basis'],'independentRoleAgreement':c['independentRoleAgreement']}for c in r['contributions']if c['unitId']in umap]});refs[ref]={'kind':'reviewed_scope','recordId':r['recordId'],'candidateId':r['candidateId']};scopebindings[ref]={'recordId':r['recordId'],'candidateId':r['candidateId'],'review':reviews[r['reviewId']]}
for d in fixedscopes:
 ref=f'c{len(scopes)}';cidmap[d['id']]=ref;scopes.append({'ref':ref,'kind':d['kind'],'scopeStatus':'explicitly_admitted_fixed_destination','definition':{**{k:d[k]for k in ['title','question','summary','scope']},'readingLimit':d['readingCoverage']['readingLimit']},'methods':d.get('methods',[]),'fixedAdmittedDestinationId':d['id'],'scopeContentSha256':d['scopeContentSha256']});refs[ref]={'kind':'admitted_scope','candidateId':d['id']};scopebindings[ref]={'admittedDestinationId':d['id'],'scopeContentSha256':d['scopeContentSha256'],'component':pin(fixedpath)}
for uid,u in units.items():u['ref']=umap[uid];refs[u['ref']]=originals[uid]
relevant={r['reviewId']for r in current}
for a in R['unitAssessments']:
 if a['unitId']not in uidset or a['reviewId']not in relevant:continue
 ref='n'+str(len(notes));notes.append({'ref':ref,'unitRef':umap[a['unitId']],'originalReview':a['reviewId'],'proposal':a['proposalAttribution'],'challenge':a['challengeAttribution'],'homeAgreement':a['homeAgreement'],'originalScopeRefs':{r['localRef']:cidmap[r['candidateId']]for r in current if r['reviewId']==a['reviewId']}});refs[ref]={'kind':'paired_attribution_context','unitId':a['unitId'],'reviewId':a['reviewId']}
evidence=[];seen=set()
for r in current[:5]:
 for c in r['contributions']:
  if c['unitId']not in uidset:continue
  for m in c['evidenceRefs']:
   if m.get('kind')!='primary':continue
   loc=m['sourceContext'];key=(loc['path'],loc['pdfPage'],loc['start'],loc['end'],loc['textSha256'])
   if key in seen:continue
   seen.add(key);archive=Path('/Users/emmy/Developer/physics-atlas-swampland')/loc['path'];doc=json.loads(archive.read_text());assert sha(archive)==loc['fileSha256'];text=doc['pages'][loc['pdfPage']-1][loc['start']:loc['end']];assert hashlib.sha256(text.encode()).hexdigest()==loc['textSha256'];ref='e'+str(len(evidence));evidence.append({'ref':ref,'text':text});refs[ref]=m
links=[];pairs=set()
for row in nom['links']:
 left=row['source'].get('candidateId');right=row['target'].get('candidateId')
 if left not in cidmap or right not in cidmap:continue
 links.append({'source':cidmap[left],'target':cidmap[right],'originalNativeLink':row['challengeLink'],'originalPriorAgreements':row['sameEndpointTypePriorLinks'],'candidateLinkId':row['id'],'status':'unadmitted_native_direction_requires_explicit_scientific_interpretation'});pairs.add(tuple(sorted([cidmap[left],cidmap[right]])))
for a in current:
 if a['localRef']in ['p3','p5']and a['reviewId'].startswith('leaf-0403944'):
  for d in fixedscopes:pairs.add(tuple(sorted([cidmap[a['candidateId']],cidmap[d['id']]])))
controls=[{**x,'source':cidmap[x['source']],'target':cidmap[x['target']]}for x in fixed['relations']if x['source']in cidmap and x['target']in cidmap]
assert len(controls)==7
packet={'schemaVersion':'q025-navigation-decision-packet/1','familyId':'kk-cross-field-routes','stage':'proposal','scopes':scopes,'units':list(units.values()),'pairedUnitContext':notes,'evidence':evidence,'objects':[],'relations':[],'refRegistry':refs,'nominations':[{'id':f'pair{i}','left':a,'right':b}for i,(a,b)in enumerate(sorted(pairs))],'nativeNavigationCandidates':links,'fixedAdmittedNavigationControls':controls,'priorReview':None,'nominationBasis':'Make actual two-way routes from dark sectors and extra dimensions to initial production, cascade thresholds and conditional cosmology. Reconcile the compound full-wave threshold/freeze-in scope against BOTH fixed threshold and flat-bounds destinations. Compare the full-wave linear question against its fixed stable-ID counterpart. Preserve initial production versus viability, stellar production, source-local flat/warped premises and contested EFT matching. Fixed seven arcs and four admitted IDs remain controls; any proposed change is a new explicit adjudication, never mechanical type remapping.','coverage':{'scopes':len(scopes),'wholeDescriptions':len(units),'pairedUnitContexts':len(notes),'primaryWindows':len(evidence),'scopeSupportInheritedBeyondSelectedWitnesses':True,'selectedWitnessPolicy':'Every narrow physical KK source contribution plus fixed-destination evidence units and one broad-family witness. Unselected broad members retain their previous review; no fresh complete-member reading claimed.'},'machineBindings':{'registry':pin(regpath),'sourceNomination':pin(nompath),'fixedComponent':pin(fixedpath),'scopeBindings':scopebindings},'navigationRequirements':['Dark sectors → survival/production → threshold or linear cosmology','Extra dimensions → stellar/KK dynamics → conditional cosmology','Return routes must keep one scoped destination per question','premise_check points from the conditional question to the premise being investigated; native rationale is evidence to interpret, not a rule to reverse blindly.']}
L.mkdir(parents=True,exist_ok=True);path=L/'source-packet.json';path.write_text(json.dumps(packet,ensure_ascii=False,separators=(',',':'))+'\n');index={'schemaVersion':'q025-kk-navigation-intake/1','packet':pin(path),'bytes':path.stat().st_size,'coverage':packet['coverage'],'candidateNavigationCount':len(links),'fixedNavigationCount':7,'nominatedPairs':len(pairs),'nativeLaunches':0,'status':'source_packet_prepared_not_launch_ready'};(B/'source-index.json').write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(index))
