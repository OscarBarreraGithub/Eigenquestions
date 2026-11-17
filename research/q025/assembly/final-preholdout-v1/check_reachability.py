import json,hashlib
from pathlib import Path
from collections import defaultdict,deque
R=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;p=HERE/'packet/aggregate.local.json';data=json.loads(p.read_text());ds={d['id']:d for d in data['destinations']};alias={id:g['destinationId'] for g in data['identityResolution']['canonicalGroups'] for id in g['memberIds']};canon=lambda id:alias.get(id,id)
adj=defaultdict(set)
for r in data['relations']:
 s,t=canon(r['source']),canon(r['target']);adj[s].add(t);adj[t].add(s)
roots=[canon(e['destinationId']) for e in data['publicEntryFrontier']['entries']+data['publicEntryFrontier']['metadataEntries']];reached=set(roots);todo=list(roots)
for d in todo:
 for n in adj[d]:
  if n not in reached:reached.add(n);todo.append(n)
homes=defaultdict(set)
for placement in data['placements']:homes[canon(placement['destinationId'])].add(placement['unitId'])
missing=set(homes)-reached;comps=[]
while missing:
 start=min(missing);cs={start};q=[start]
 for d in q:
  for n in adj[d]:
   if n not in cs:cs.add(n);q.append(n)
 missing-=cs;uids=set().union(*(homes[x] for x in cs));comps.append({'scopes':[{'id':d,**{k:ds[d].get(k) for k in ['kind','title','question','summary','scope','readingCoverage','evidenceIds']},'directUnits':sorted(homes[d])} for d in sorted(cs)],'unitIds':sorted(uids),'scopeCount':len(cs),'allocatedCount':len(uids)})
comps.sort(key=lambda c:(-c['allocatedCount'],c['scopes'][0]['id']))
report={'inputSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rootCount':len(roots),'allocatedTotal':len(set().union(*homes.values())),'reachedAllocated':len(set().union(*(homes[x] for x in reached))),'missingComponents':comps,'scientificOrOrganizationalRoutesOnly':True,'numericalSimilarityRoutesCurrentlyInstalled':False}
(HERE/'remaining-access.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='missingComponents'}));print([(c['allocatedCount'],c['scopeCount'],[d['title'] for d in c['scopes']]) for c in comps])
