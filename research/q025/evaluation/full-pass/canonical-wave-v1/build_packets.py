"""Versioned bounded global scope reconciliation, preserving all nominated coverage."""
import collections,copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;Q=E.parent;W=Q.parent.parent;L=F/'native-local/canonical-wave-v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();REG=F/'reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json';NOM=Q/'assembly/outputs/scope-candidates-v3/candidates.json';SOURCE=Q/'geometry/round1/source-rows.jsonl';ARCHIVE=Path('/Users/emmy/Developer/physics-atlas-swampland');MAX_PACKET_CHARACTERS=280000;MAX_SCOPES=12;MAX_NOMINATIONS=30

def build():
 registry=json.loads(REG.read_text());nominations=json.loads(NOM.read_text());assert nominations['registrySha256']==sha(REG);records={r['recordId']:r for r in registry['records']};sealed={r['paperId'] for r in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']};sources={r['unit_id']:r for r in map(json.loads,SOURCE.read_text().splitlines())};source_files={};packet_cache={};unit_scope_cache={}
 def primary_key(ref):
  c=ref['sourceContext'];return (c['path'],c['pdfPage'],c['start'],c['end'],c['textSha256'])
 def record_sources(rid):
  if rid in unit_scope_cache:return unit_scope_cache[rid]
  r=records[rid];ids=set(c['unitId'] for c in r['contributions']);evidence=list(r['evidenceRefs'])+[e for c in r['contributions'] for e in c['evidenceRefs']];ids.update(e['unitId'] for e in evidence if e.get('kind')=='description' and e.get('unitId'));prim={primary_key(e):e for e in evidence if e.get('kind') in ['primary','source_excerpt'] and e.get('sourceContext')};unit_scope_cache[rid]=(ids,prim);return ids,prim
 def make_packet(record_ids,pairs,key='preflight'):
  ordered=list(dict.fromkeys(record_ids));rmap={rid:f'c{i}' for i,rid in enumerate(ordered)};packet={'schemaVersion':'q025-canonical-source-packet/2','familyId':key,'stage':'proposal','scopes':[],'units':[],'evidence':[],'objects':[],'relations':[],'refRegistry':{},'priorReview':None,'sourceReviews':[],'nominations':[],'priorCanonicalConstraints':[]};allunits=set();allprimary={};scopeprimary={};scopeunits={};mandatory=set()
  for rid in ordered:
   ids,primary=record_sources(rid);allunits|=ids;allprimary.update(primary);scopeprimary[rid]=primary;scopeunits[rid]=ids
  for pair in pairs:
   for win in pair.get('sharedPrimaryWindows',[]):
    keywin=(win['path'],win['pdfPage'],win['start'],win['end'],win['textSha256'])
    if keywin in allprimary:mandatory.add(keywin)
  selected=set(mandatory)
  # Every original scientific description is present. Primary selection is bounded,
  # explicit and source-diverse; omitted windows are counted, never cited as read.
  for rid in ordered:
   primary=scopeprimary[rid];chosen=[k for k in primary if k in selected];papers={primary[k]['paperId'] for k in chosen};orderedkeys=sorted(primary,key=lambda k:(primary[k]['paperId'],k[1],k[2]))
   for k in orderedkeys:
    if len([x for x in selected if x in primary])>=6:break
    if primary[k]['paperId'] not in papers:selected.add(k);papers.add(primary[k]['paperId'])
   for k in orderedkeys:
    if len([x for x in selected if x in primary])>=6:break
    selected.add(k)
  umap={}
  for uid in sorted(allunits):
   source=sources[uid];assert source['paper_id'] not in sealed;assert hashlib.sha256(source['text'].encode()).hexdigest()==source['text_sha256'];ref='u'+str(len(umap));umap[uid]=ref;packet['units'].append({'ref':ref,'unitId':uid,'paperId':source['paper_id'],'description':source['text']});packet['refRegistry'][ref]={'kind':'description','unitId':uid,'paperId':source['paper_id'],'textSha256':source['text_sha256']}
  emap={}
  for k in sorted(selected):
   e=copy.deepcopy(allprimary[k]);assert e['paperId'] not in sealed;c=e['sourceContext'];path=ARCHIVE/c['path']
   if c['path'] not in source_files:source_files[c['path']]=(sha(path),json.loads(path.read_text()))
   digest,archive=source_files[c['path']];assert digest==c['fileSha256'];assert archive['source_sha256']==e['sourceSha256'];text=archive['pages'][c['pdfPage']-1][c['start']:c['end']];assert hashlib.sha256(text.encode()).hexdigest()==c['textSha256'];ref='e'+str(len(emap));emap[k]=ref;e.pop('localRef',None);e.pop('ref',None);packet['evidence'].append({'ref':ref,'text':text});packet['refRegistry'][ref]=e
  for rid in ordered:
   r=records[rid];contributions=[{'unitRef':umap[c['unitId']],'role':c['role'],'priorRoleAgreement':c['independentRoleAgreement'],'basis':c['basis'],'sourceOrigin':c.get('sourceOrigin'),'directOrganizationalHomeNotInferred':True}for c in r['contributions']];primary=scopeprimary[rid];packet['scopes'].append({'ref':rmap[rid],'recordId':rid,'candidateId':r['candidateId'],'admittedDestinationId':r.get('admittedDestinationId'),'kind':r['kind'],'scopeStatus':r['scopeStatus'],'definition':r['definition'],'methods':r['methods'],'sourceContributions':contributions,'evidenceRefs':[umap[u]for u in sorted(scopeunits[rid])]+[emap[k]for k in primary if k in emap],'readingBasis':'Exact source descriptions plus selected whole archived primary windows. Prior scope review is attributed; no claim that omitted windows were reread.','primaryCoverage':{'availableWindows':len(primary),'providedWindows':sum(k in emap for k in primary),'omittedWindows':sum(k not in emap for k in primary),'omittedPaperIds':sorted({primary[k]['paperId'] for k in primary if k not in emap})},'admissionPins':r.get('admittedScopeArtifact'),'scopeContentSha256':r.get('scopeContentSha256')});packet['sourceReviews'].append({'reviewId':r['reviewId'],'pins':r['pins']})
  for pair in pairs:packet['nominations'].append({'id':pair['id'],'left':rmap[pair['recordIds'][0]],'right':rmap[pair['recordIds'][1]],'channels':pair.get('nominationChannels',['weak_unmatched_contrast']),'status':'unreviewed_nomination_not_equivalence'})
  packet['coverage']={'authoredScopes':len(ordered),'sourceDescriptions':len(allunits),'primaryWindows':len(selected),'availablePrimaryWindows':len(allprimary),'omittedPrimaryWindows':len(set(allprimary)-selected),'reservedPapersExcluded':len(sealed),'nominatedPairs':len(pairs),'globalRegistryScopes':len(records),'globalRegistrySha256':sha(REG),'graphContext':'No unrelated paper objects included. Exact source IDs, scope definitions and prior contribution roles retained; no generic paper-premise propagation.'};packet['nominationBasis']='Global deterministic shared-source/target/lexical nominations plus explicit weak unmatched controls. Review every queued pair; absent outside candidates never certify uniqueness.';return packet
 # The2current pilot neighborhoods have real science underway. Their within-packet
 # pairs remain an explicit pending pilot dependency, not new repeated model calls.
 pilot=json.loads((F/'canonical-v1/source-index.json').read_text());pilot_sets=[set(x['recordIds'])for x in pilot['families']];deferred=[p for p in nominations['pairs']if any(set(p['recordIds'])<=s for s in pilot_sets)];pairs=[p for p in nominations['pairs']if p not in deferred];remaining={p['id']:p for p in pairs};batches=[];oversize=[]
 while remaining:
  seed=next(iter(remaining.values()));ids=list(seed['recordIds']);selected=[seed];cache=make_packet(ids,selected);size=len(json.dumps(cache,ensure_ascii=False,separators=(',',':')))
  if size>MAX_PACKET_CHARACTERS:oversize.append({'pairId':seed['id'],'recordIds':ids,'characters':size,'status':'requires_separate_context_split_no_dispatch'});remaining.pop(seed['id']);continue
  while True:
   candidates=[p for p in remaining.values() if p['id']not in {x['id']for x in selected} and set(p['recordIds'])&set(ids) and len(set(ids)|set(p['recordIds']))<=MAX_SCOPES]
   candidates.sort(key=lambda p:(-len(set(p['recordIds'])&set(ids)),-p['rankingScore']))
   added=False
   for p in candidates:
    if len(selected)>=MAX_NOMINATIONS:break
    newids=list(dict.fromkeys(ids+p['recordIds']));newpairs=selected+[p];trial=make_packet(newids,newpairs);size=len(json.dumps(trial,ensure_ascii=False,separators=(',',':')))
    if size<=MAX_PACKET_CHARACTERS:ids,selected,cache=newids,newpairs,trial;added=True;break
   if not added:break
  for p in selected:remaining.pop(p['id'])
  batches.append((ids,selected,cache,'nominated_neighborhood'))
 # Unmatched scopes are inspected against their explicit weak nearest candidates.
 for unmatched in nominations['unmatched']:
  rid=unmatched['recordId'];controls=[x['recordId']for x in unmatched['nearestLexicalReviewCandidates']][:3];ps=[{'id':'unmatched:'+hashlib.sha256((rid+'\n'+c).encode()).hexdigest()[:24],'recordIds':[rid,c],'nominationChannels':['weak_nearest_contrast'],'rankingScore':0}for c in controls];ids=[rid]+controls;packet=make_packet(ids,ps);size=len(json.dumps(packet,ensure_ascii=False,separators=(',',':')))
  if size>MAX_PACKET_CHARACTERS:oversize.append({'unmatchedRecordId':rid,'recordIds':ids,'characters':size,'status':'requires_separate_context_split_no_dispatch'});continue
  batches.append((ids,ps,packet,'unmatched_scope_contrasts'))
 index=[]
 for n,(ids,ps,packet,kind) in enumerate(batches):
  key=f'global-scopes-{n+1:04}';packet['familyId']=key;path=L/'sources'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(packet,ensure_ascii=False,separators=(',',':'))+'\n');index.append({'familyId':key,'kind':kind,'sourcePacketPath':str(path.relative_to(E)),'sourcePacketSha256':sha(path),'characters':len(path.read_text()),'recordIds':ids,'pairIds':[p['id']for p in ps],'counts':packet['coverage']})
 queued={x for f in index for x in f['pairIds']};expected={p['id']for p in pairs};assert expected<=queued|{x.get('pairId')for x in oversize};covered={rid for f in index for rid in f['recordIds']};out={'schemaVersion':'q025-global-canonical-intake/1','registryPath':str(REG.relative_to(E)),'registrySha256':sha(REG),'nominationsPath':str(NOM.relative_to(W)),'nominationsSha256':sha(NOM),'sourceRowsSha256':sha(SOURCE),'families':index,'deferredActivePilotPairIds':[p['id']for p in deferred],'oversizeUndispatched':oversize,'coverage':{'globalScopes':len(records),'queuedScopes':len(covered),'notQueuedRecordIds':sorted(set(records)-covered),'globalNominations':len(nominations['pairs']),'queuedNominations':len(expected)-sum('pairId'in x for x in oversize),'deferredPilotNominations':len(deferred),'unmatchedAnchors':len(nominations['unmatched']),'batches':len(index),'proposedCalls':len(index)*2,'availablePrimaryWindows':sum(x['counts']['availablePrimaryWindows']for x in index),'providedPrimaryWindows':sum(x['counts']['primaryWindows']for x in index)},'limits':{'maxPacketCharacters':MAX_PACKET_CHARACTERS,'maxScopesPerBatch':MAX_SCOPES,'maxNominationsPerBatch':MAX_NOMINATIONS},'nativeLaunches':0,'acceptance':'Queue coverage only; no unique-scope or equivalence certification. All pending/outside nominations remain explicit.'};(B/'source-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['coverage']));print('oversize',len(oversize))
if __name__=='__main__':build()
