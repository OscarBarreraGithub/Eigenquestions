"""Merge already pinned bounded neighborhoods; preserve every pair and source."""
import copy,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;L=F/'native-local/canonical-wave-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();index=json.loads((B/'source-index.json').read_text());registry=json.loads((E/index['registryPath']).read_text());records={r['recordId']:r for r in registry['records']};MAX_CHARS=280000;MAX_SCOPES=20;MAX_PAIRS=40

def pkey(meta):
 if meta['kind']=='description':return ('description',meta['unitId'])
 c=meta['sourceContext'];return ('primary',c['path'],c['pdfPage'],c['start'],c['end'],c['textSha256'])
def merge(packets,family='preflight'):
 out={'schemaVersion':'q025-canonical-source-packet/2','familyId':family,'stage':'proposal','scopes':[],'units':[],'evidence':[],'objects':[],'relations':[],'refRegistry':{},'priorReview':None,'sourceReviews':[],'nominations':[],'priorCanonicalConstraints':[],'neighborhoods':[]};smap={};emap={};scopes={};nomseen=set();reviewseen=set();available={};nunit=0;nevidence=0
 for p in packets:
  mapping={}
  for u in p['units']:
   meta=p['refRegistry'][u['ref']];key=pkey(meta)
   if key not in emap:
    ref='u'+str(nunit);nunit+=1;emap[key]=ref;out['units'].append({**u,'ref':ref});out['refRegistry'][ref]=meta
   mapping[u['ref']]=emap[key]
  for e in p['evidence']:
   meta=p['refRegistry'][e['ref']];key=pkey(meta)
   if key not in emap:
    ref='e'+str(nevidence);nevidence+=1;emap[key]=ref;out['evidence'].append({**e,'ref':ref});out['refRegistry'][ref]=meta
   mapping[e['ref']]=emap[key]
  for s in p['scopes']:
   rid=s['recordId']
   if rid not in smap:
    ref='c'+str(len(smap));smap[rid]=ref;row=copy.deepcopy(s);row['ref']=ref;row['evidenceRefs']=[mapping[x]for x in s['evidenceRefs']];row['sourceContributions']=[{**c,'unitRef':mapping[c['unitRef']]}for c in s['sourceContributions']];scopes[rid]=row;out['scopes'].append(row)
   else:
    row=scopes[rid];assert row['definition']==s['definition'];row['evidenceRefs']=list(dict.fromkeys(row['evidenceRefs']+[mapping[x]for x in s['evidenceRefs']]))
   mapping[s['ref']]=smap[rid]
  neighborhood=[]
  for n in p['nominations']:
   neighborhood.append(n['id'])
   if n['id'] not in nomseen:nomseen.add(n['id']);out['nominations'].append({**n,'left':mapping[n['left']],'right':mapping[n['right']]})
  out['neighborhoods'].append({'originalFamilyId':p['familyId'],'scopeRefs':[mapping[s['ref']]for s in p['scopes']],'nominationIds':neighborhood,'scopeMeaning':'A comparison workload, not an instruction to invent one common parent for unrelated targets.'})
  for r in p['sourceReviews']:
   key=json.dumps(r,sort_keys=True)
   if key not in reviewseen:reviewseen.add(key);out['sourceReviews'].append(r)
 for rid,s in scopes.items():
  r=records[rid];refs=r['evidenceRefs']+[e for c in r['contributions']for e in c['evidenceRefs']];primary={pkey(e):e for e in refs if e.get('kind')in['primary','source_excerpt'] and e.get('sourceContext')};available.update(primary);provided={pkey(out['refRegistry'][e])for e in s['evidenceRefs']if out['refRegistry'][e]['kind']in['primary','source_excerpt']};s['primaryCoverage']={'availableWindows':len(primary),'providedWindows':len(provided),'omittedWindows':len(set(primary)-provided),'omittedPaperIds':sorted({primary[k]['paperId']for k in primary if k not in provided})}
 out['coverage']={'authoredScopes':len(out['scopes']),'sourceDescriptions':len(out['units']),'primaryWindows':len(out['evidence']),'availablePrimaryWindows':len(available),'omittedPrimaryWindows':len(set(available)-set(emap)),'reservedPapersExcluded':24,'nominatedPairs':len(out['nominations']),'globalRegistryScopes':len(records),'globalRegistrySha256':index['registrySha256'],'graphContext':'Whole source descriptions and bounded exact primary windows; unrelated paper graph objects omitted. No inherited premise is applied universally.'};out['nominationBasis']='Complete explicit pair workload from global nomination ledger. Distinct neighborhoods may share one bounded call; do not force a common parent across them. Compare every named pair and preserve unresolved/outside comparisons.';return out
packets=[json.loads((E/f['sourcePacketPath']).read_text())for f in index['families']];groups=[]
while packets:
 first=packets.pop(0);current=[first];merged=first
 while True:
  ids={s['recordId']for s in merged['scopes']};candidates=sorted(range(len(packets)),key=lambda i:(-len(ids&{s['recordId']for s in packets[i]['scopes']}),len(json.dumps(packets[i],ensure_ascii=False))))
  found=False
  for i in candidates:
   p=packets[i]
   if len(ids|{s['recordId']for s in p['scopes']})>MAX_SCOPES or len(merged['nominations'])+len(p['nominations'])>MAX_PAIRS:continue
   trial=merge(current+[p]);size=len(json.dumps(trial,ensure_ascii=False,separators=(',',':')))
   if size<=MAX_CHARS:current.append(packets.pop(i));merged=trial;found=True;break
  if not found:break
 groups.append(merge(current))
new=[]
for n,p in enumerate(groups):
 key=f'canonical-neighborhoods-{n+1:04}';p['familyId']=key;path=L/'sources-compacted'/f'{key}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':'))+'\n');new.append({'familyId':key,'sourcePacketPath':str(path.relative_to(E)),'sourcePacketSha256':sha(path),'characters':len(path.read_text()),'recordIds':[s['recordId']for s in p['scopes']],'pairIds':[n['id']for n in p['nominations']],'counts':p['coverage']})
assert {p for f in new for p in f['pairIds']}=={p for f in index['families']for p in f['pairIds']};assert {r for f in new for r in f['recordIds']}==set(records);out={**index,'families':new,'originalUncompactedIndexSha256':sha(B/'source-index.json'),'limits':{'maxPacketCharacters':MAX_CHARS,'maxScopesPerBatch':MAX_SCOPES,'maxNominationsPerBatch':MAX_PAIRS},'coverage':{**index['coverage'],'batches':len(new),'proposedCalls':len(new)*2}};(B/'compacted-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['coverage']))
