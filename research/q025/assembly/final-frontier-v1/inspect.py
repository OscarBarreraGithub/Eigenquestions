"""Current admitted graph/home diagnostic; no new relations or roots admitted."""
import json,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[4];A=R/'research/q025/assembly';E=R/'research/q025/evaluation/full-pass';O=Path(__file__).resolve().parent
pins=[]
def read(p):
 b=p.read_bytes();pins.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return json.loads(b)
b=read(A/'placement-incremental-v1/cut-01/candidate-6294/aggregate.local.json');aliases={m:g['destinationId']for g in b['identityResolution']['canonicalGroups']for m in g['memberIds']};canon=lambda x:aliases.get(x,x)
ds={canon(d['id']):d for d in b['destinations']if canon(d['id'])==d['id']};rels={r['id']:r for r in b['relations']};ps=list(b['placements'])
paths=[E/'placement-scope-review-v1/scope-component.json',E/'placement-scope-review-v2/n8-scope-component.json',E/'placement-scope-review-v2/entry-route-component.json',E/'orientation-admissions-v1/parent-orientation-05-component.json',E/'orientation-adjudications-v1/final-replacements-component.json',A/'placement-incremental-v1/cut-02/admitted/component.json',A/'placement-incremental-v1/new-scope-cut-01/component.json',A/'placement-incremental-v1/cut-03/admitted/component.json',A/'placement-incremental-v1/explicit-cut-01/component.json',E/'placement-scope-review-v3/scope-component.json',E/'placement-scope-review-v3/entry-route-component.json',A/'placement-incremental-v1/cut-04/admitted/component.json',A/'placement-incremental-v1/new-scope-cut-02/component.json']
for p in paths:
 c=read(p)
 for d in c.get('destinations',[]):ds[d['id']]=d
 for r in c.get('relations',[]):
  if r['id']in rels:assert rels[r['id']]==r
  rels[r['id']]=r
 ps.extend(c.get('placements',[]))
assert len({p['unitId'] for p in ps})==8017
home=collections.defaultdict(set)
for p in ps:home[canon(p['destinationId'])].add(p['unitId'])
adj=collections.defaultdict(set);children=collections.defaultdict(set);parents=collections.defaultdict(set);incident=collections.defaultdict(list)
for r in rels.values():
 s,t=canon(r['source']),canon(r['target'])
 if s==t:continue
 assert s in ds and t in ds
 adj[s].add(t);adj[t].add(s);incident[s].append(r);incident[t].append(r)
 if r['type']=='narrower':children[s].add(t);parents[t].add(s)
def reach(start,graph,limit=None):
 seen={start};front={start};depth=0
 while front and (limit is None or depth<limit):
  nxt={v for u in front for v in graph[u]}-seen;seen.update(nxt);front=nxt;depth+=1
 return seen
def units(ids):return set().union(*(home[i]for i in ids))if ids else set()
seen=set();components=[]
for id in ds:
 if id in seen:continue
 ids=reach(id,adj);seen.update(ids);us=units(ids)
 components.append({'scopeCount':len(ids),'allocatedSourceCount':len(us),'homeDestinationCount':sum(bool(home[x])for x in ids),'ids':sorted(ids)})
components.sort(key=lambda x:(-x['allocatedSourceCount'],-x['scopeCount']))
candidates=[]
for id,d in ds.items():
 if d['kind']!='region' or len(children[id])<2:continue
 ns=reach(id,children);us=units(ns)
 candidates.append({'id':id,'title':d['title'],'question':d['question'],'kind':d['kind'],'scope':d['scope'],'readingCoverage':d['readingCoverage'],'narrowerChoices':len(children[id]),'distinctPublicNeighbors':len(adj[id]),'directHomeSources':len(home[id]),'narrowerClosureScopes':len(ns),'narrowerClosureSources':len(us),'routeSourcesWithin3Steps':len(units(reach(id,adj,3))),'parentIds':sorted(parents[id]),'sourceUnits':sorted(us),'scienceDefinitionHash':d.get('scopeContentSha256'),'proposedEntryMeaning':'Collection-level access to this already admitted scope, not a new physical containment claim.'})
candidates.sort(key=lambda c:(-c['narrowerClosureSources'],-c['narrowerClosureScopes'],c['id']))
selected=[];covered=set()
for _ in range(15):
 choices=[c for c in candidates if c not in selected];best=max(choices,key=lambda c:len(set(c['sourceUnits'])-covered))
 if not(set(best['sourceUnits'])-covered):break
 selected.append(best);covered.update(best['sourceUnits'])
allreach=set().union(*(reach(c['id'],adj)for c in selected))
result={'schemaVersion':'q025-current-public-frontier-diagnostic/1','status':'candidate_entry_selection_not_admitted','inputs':pins,'allocatedSources':8017,'scopeCount':len(ds),'routeObservationRows':len(rels),'existingOrganizationalAccessNotYetRejoinedForNewHomes':True,'components':components,'topBroadCandidates':candidates[:40],'greedyNonredundantNarrowerCoverageCandidate':[c['id']for c in selected],'candidateNarrowerClosureSources':len(covered),'candidatePublicGraphReachSources':len(units(allreach)),'notReachedHomeComponents':[c for c in components if not any(id in allreach for id in c['ids'])and c['allocatedSourceCount']],'meaning':'Connectivity treats incoming links as browsable navigation only, never converse science. Narrower closure is measured separately; new entry edges are not added.'}
(O/'diagnostic.local.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'scopeCount':len(ds),'components':[(c['scopeCount'],c['allocatedSourceCount'])for c in components[:12]],'candidateNarrowerClosureSources':len(covered),'candidatePublicGraphReachSources':len(units(allreach)),'entries':[{k:c[k]for k in ['id','title','narrowerChoices','directHomeSources','narrowerClosureSources','routeSourcesWithin3Steps']}for c in selected]},indent=2))
