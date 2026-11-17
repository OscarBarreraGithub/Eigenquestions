"""Trace missing routes using exact homes and separately admitted source roles."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];F=ROOT/'research/q025/evaluation/full-pass'
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
p,ppin=read(B.parent/'organization-v4/candidate-v1/aggregate.local.json');registry,rpin=read(F/'reconciliation-v1/authored-scope-registry-v5-20261117T135430Z.json');native,npin=read(F/'reconciliation-v1/parent-navigation-candidates-v5-20261117T135430Z.json');bins,bpin=read(ROOT/'research/q025/geometry/round3/multiview_preserve_candidates/regions.json');eligible,epin=read(F/'reconciliation-v1/eligible-preholdout-unit-ids-v1.json')
dest={d['id']:d for d in p['destinations']};homes=collections.defaultdict(list)
for row in p['placements']:
    if row['role']!='context':homes[row['unitId']].append(row)
links=[x for x in native['links'] if x['agreement']=='paired_endpoint_type' and x['source']['kind']==x['target']['kind']=='scientific_scope' and x['source']['candidateId'] in dest and x['target']['candidateId'] in dest]
typed=collections.defaultdict(set);narrow=collections.defaultdict(set)
for x in links:
    s,t=x['source']['candidateId'],x['target']['candidateId'];typed[s].add(t);typed[t].add(s)
    if x['challengeLink']['type']=='narrows':narrow[s].add(t)
for x in p['relations']:typed[x['source']].add(x['target']);typed[x['target']].add(x['source'])
bridges=collections.defaultdict(list)
for r in p['sourceContributions']:
    if r['role'] not in ('addresses','instantiates','specializes'):continue
    for h in homes.get(r['unitId'],[]):
        if dest[h['destinationId']]['kind']=='region' and h['destinationId']!=r['destinationId']:
            bridges[(h['destinationId'],r['destinationId'])].append({'unitId':r['unitId'],'role':r['role'],'placementDecisionId':h['decisionId'],'contributionDecisionId':r['decisionId'],'qualification':r.get('qualification')})
enriched={k:set(v) for k,v in typed.items()}
for s,t in bridges:enriched.setdefault(s,set()).add(t);enriched.setdefault(t,set()).add(s)
def distance(g,start):
    seen={start:0};q=collections.deque([start])
    while q:
        u=q.popleft()
        for v in g.get(u,()):
            if v not in seen:seen[v]=seen[u]+1;q.append(v)
    return seen
def covered(dist,units,limit=None):return {u for u in units if any(h['destinationId'] in dist and (limit is None or dist[h['destinationId']]<=limit) for h in homes.get(u,[]))}
binmap={b['id']:b for b in bins};reviews={r['reviewId']:r for r in registry['reviews']};wanted=['Dark sectors: candidates, cosmic histories and tests','Black-hole entropy, horizon structure and gravitational limits'];results=[]
for title in wanted:
    rec=next(r for r in registry['records'] if r['definition']['title']==title);rv=reviews[rec['reviewId']];packet,pin=read(ROOT/'research/q025/evaluation'/rv['artifactDirectory']/rv['challengeArtifact']['packetFile']);assert pin['sha256']==rv['pins']['challengePacketSha256']
    expected=set()
    for child in packet['childScopes']:expected.update(binmap[child['candidateRegionId']]['memberIds'])
    expected &= set(eligible['unitIds']);allocated=expected&homes.keys();did=rec['candidateId'];dist=distance(typed,did);ndist=distance(narrow,did);edist=distance(enriched,did)
    missing=allocated-covered(dist,expected);byhome=collections.Counter(h['destinationId'] for u in missing for h in homes[u]);examples=[]
    for home,count in byhome.most_common(6):
        candidates=[(t,rows) for (s,t),rows in bridges.items() if s==home and t in dist];examples.append({'homeDestinationId':home,'homeTitle':dest[home]['title'],'affectedAllocatedSources':count,'candidateSupportRoutes':[{'targetDestinationId':t,'targetTitle':dest[t]['title'],'exactSharedSourceSupport':rows,'sourceCount':len({r['unitId'] for r in rows})} for t,rows in candidates[:4]]})
    results.append({'entryDestinationId':did,'entryTitle':title,'inheritedParentReviewScope':packet['parentCoverage'],'referenceChildInventoryEligible':len(expected),'allocatedInCurrentCohort':len(allocated),'stillUnallocated':len(expected-allocated),'candidateNarrowerReachableAllocatedSources':len(covered(ndist,expected)),'candidateTypedReachableAllocatedSources':len(covered(dist,expected)),'candidateTypedWithin3':len(covered(dist,expected,3)),'candidateTypedWithin5':len(covered(dist,expected,5)),'missingAllocatedByHomeKind':dict(collections.Counter(dest[h['destinationId']]['kind'] for u in missing for h in homes[u])),'missingHomeKindCountsArePlacementsNotUniqueSources':True,'withExplicitlyProposedSupportRoutes':{'reachableAllocatedSources':len(covered(edist,expected)),'within3':len(covered(edist,expected,3)),'within5':len(covered(edist,expected,5))},'unreachableAllocatedSourcesAfterSupportProposal':[{'unitId':u,'homes':[{'destinationId':h['destinationId'],'title':dest[h['destinationId']]['title']} for h in homes[u]]} for u in sorted(allocated-covered(edist,expected))],'missingFamilyExamples':examples,'parentPacket':pin,'scopeWarning':'Original child source inventory is a coverage probe, not a scientific declaration that every source is inside the parent. Boundary/alternate-source judgments remain authoritative.'})
isolated_homes={h['destinationId'] for hs in homes.values() for h in hs if not typed[h['destinationId']]};global_info={'allocatedSources':len(homes),'allocatedHomeDestinations':len({h['destinationId'] for hs in homes.values() for h in hs}),'isolatedAllocatedHomes':len(isolated_homes),'isolatedBroadHomes':sum(dest[d]['kind']=='region' for d in isolated_homes),'sourcesAtIsolatedHomes':len({u for u,hs in homes.items() if any(h['destinationId'] in isolated_homes for h in hs)}),'exactBroadHomePositiveTargetRouteCandidates':len(bridges),'broadHomesWithCandidateSupportRoutes':len({s for s,t in bridges})}
payload={'schemaVersion':'q025-home-to-scope-coverage-diagnostic/1','status':'candidate_routes_only_no_navigation_admitted','inputs':[ppin,rpin,npin,bpin,epin],'global':global_info,'entries':results,'proposedRoutePolicy':'A source explicitly allocated to an admitted broad home also has an independently admitted addresses/instantiates/specializes contribution to another admitted question. This exact joint evidence can nominate a qualified related-question access route. It asserts neither scope containment nor physical implication, equivalence, method applicability or new allocation. Each route remains pending explicit coordinator/navigation admission.','candidateSupportRoutes':[{'source':s,'target':t,'supports':rs} for (s,t),rs in sorted(bridges.items())],'limitations':['Connectivity is not scope membership. A route that reaches another family may be a valid comparison or alternate home.','No original numerical bin becomes a public node; route endpoints are already admitted scientific scopes.','The existing full graph/source access remains available; candidate support routes are an explicit proposed organizational bridge, not automatically promoted scientific edges.']}
(B/'coverage-paths.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'global':global_info,'entries':[{k:v for k,v in r.items() if k not in ['missingFamilyExamples','parentPacket','inheritedParentReviewScope']} for r in results]},indent=2))
