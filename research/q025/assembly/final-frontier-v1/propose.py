"""Curated existing-scope entry proposal; no new physical scope or route admission."""
import runpy,contextlib,io,json,hashlib,collections
from pathlib import Path
O=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):g=runpy.run_path(str(O/'inspect.py'))
ids=['2826f594e622ec820a3a006c','ab32fe5068d3093c0140abe9','8574187d747387068f02fe63','79dd11c4632243fb25aa5bad','62d736e5f22beae93d504a44','525f7ea42c33dd644d118772','e52fcb6489b7f044e70ddb7d','b35c5857878f0111cd402204','e3c867c46139e156f816e00f','7961ee3cebdb154299e78b58','5fb081b9efa119868d87802b','277d9b2e77af3c3b06134952','ec6e08226449cb148b80a2d2','f87c99e7c23e7d82e9d1db78','88aac1f2c237b6c3e063f6e0']
ids=['q025-candidate-region:'+i for i in ids];ds=g['ds'];adj=g['adj'];home=g['home'];reach=g['reach'];units=g['units'];children=g['children']
def stats(entries):
 dist={x:0 for x in entries};q=collections.deque(entries)
 while q:
  x=q.popleft()
  for y in adj[x]:
   if y not in dist:dist[y]=dist[x]+1;q.append(y)
 byunit={}
 for id,us in home.items():
  if id in dist:
   for u in us:byunit[u]=min(byunit.get(u,999),dist[id])
 return {'reachableSourceCount':len(byunit),'sourceHopHistogram':dict(sorted(collections.Counter(byunit.values()).items())),'sourceCountWithin3Hops':sum(d<=3 for d in byunit.values()),'sourceCountWithin5Hops':sum(d<=5 for d in byunit.values()),'maximumSourceHops':max(byunit.values()),'narrowerClosureSourceCount':len(units(set().union(*(reach(x,children)for x in entries))))}
rows=[]
for id in ids:
 d=ds[id];rows.append({'destinationId':id,'title':d['title'],'relationshipType':'related_question','navigationBasis':'curated_collection_entry','meaning':'Open this reviewed scientific scope as an entry into the collection; no collection-wide physical containment, implication or H allocation is asserted.','exactScope':{k:d[k]for k in ['kind','title','question','summary','scope','readingCoverage','scopeContentSha256']if k in d},'narrowerChoices':len(children[id]),'distinctPublicNeighbors':len(adj[id]),'directHomeSourceCount':len(home[id]),'narrowerClosureSourceCount':len(units(reach(id,children))),'sourceCountWithin3Hops':len(units(reach(id,adj,3)))})
greedy=g['result']['greedyNonredundantNarrowerCoverageCandidate'];covered=set().union(*(reach(x,adj)for x in ids));gaps=[]
for c in g['components']:
 if c['allocatedSourceCount'] and not any(x in covered for x in c['ids']):gaps.append({'sourceCount':c['allocatedSourceCount'],'destinations':[{'id':x,'title':ds[x]['title'],'kind':ds[x]['kind'],'sourceUnitIds':sorted(home[x]),'scopeContentSha256':ds[x].get('scopeContentSha256')}for x in c['ids']]})
proposal={'schemaVersion':'q025-public-entry-frontier-proposal/1','status':'requires_coordinator_entry_admission','sourceInventory':'8017 currently admitted semantic homes; remaining source records remain visible separately and are not assigned by this proposal.','entryLandmark':{'id':'collection:q025-quantum-gravity','kind':'landmark','title':'Quantum gravity and connected physics','metadataOnly':True,'meaning':'A collection entrance and chart orientation, not a new scientific question, physical parent or geometric mass atom.'},'entries':rows,'variedFrontierMetrics':stats(ids),'greedyNarrowerCoverageAlternative':{'ids':greedy,'metrics':stats(greedy),'rejectionReason':'Several near-overlapping compactification/dark-energy entries consume the initial frontier; numerical coverage alone is not a readable subject selection.'},'disconnectedHomeComponents':gaps,'limitations':['Counts use current admitted public science plus existing certified organizational access; new homes have not yet undergone the next same-source rejoin.','Incoming links are browsable without asserting a converse physical relation.','These 15 are collection entries, not an exhaustive partition or fixed branch count at later destinations.','No geometry is fitted here. Final chart must describe actual source/home support and distinguish orientation from membership.'],'inputs':g['pins'],'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
p=O/'proposal.json';p.write_text(json.dumps(proposal,indent=2)+'\n');print(json.dumps({'proposalSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'metrics':proposal['variedFrontierMetrics'],'disconnectedSourceCount':sum(c['sourceCount']for c in gaps),'gapComponents':len(gaps)},indent=2))
