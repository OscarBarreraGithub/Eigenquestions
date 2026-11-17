"""Researcher-facing proposed journeys; no candidate link is admitted here."""
import collections, hashlib, json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];F=ROOT/'research/q025/evaluation/full-pass'
packet=json.loads((B.parent/'organization-v4/candidate-v1/aggregate.local.json').read_text());dest={d['id']:d for d in packet['destinations']};titles={d['title']:d['id'] for d in dest.values()}
raw=json.loads((F/'reconciliation-v1/parent-navigation-candidates-v5-20261117T135430Z.json').read_text());links=[l for l in raw['links'] if l['agreement']=='paired_endpoint_type' and l['source']['kind']==l['target']['kind']=='scientific_scope' and l['source']['candidateId'] in dest and l['target']['candidateId'] in dest]
incident=collections.defaultdict(list);children=collections.defaultdict(set);homes=collections.defaultdict(set);supports=collections.defaultdict(set)
for p in packet['placements']:
    if p['role']!='context':homes[p['destinationId']].add(p['unitId'])
for r in packet['sourceContributions']:
    if r['role'] in ['addresses','instantiates','specializes']:supports[r['destinationId']].add(r['unitId'])
for l in links:
    s,t=l['source']['candidateId'],l['target']['candidateId'];typ=l['challengeLink']['type']
    for a,b,direction in [(s,t,'outgoing'),(t,s,'incoming')]:incident[a].append({'targetId':b,'title':dest[b]['title'],'nativeType':typ,'traversal':direction,'kind':'narrower' if typ=='narrows' and direction=='outgoing' else 'broader' if typ=='narrows' else typ,'candidateLinkId':l['id']})
    if typ=='narrows':children[s].add(t)
def subtree(id):
    seen=set();todo=[id];units=set()
    while todo:
        d=todo.pop()
        if d in seen:continue
        seen.add(d);units|=homes[d];todo+=list(children[d])
    return units
def frontier(id):
    rows=incident[id];return {'scientificLinks':len(rows),'distinctDestinations':len({r['targetId'] for r in rows}),'byType':dict(collections.Counter(r['kind'] for r in rows)),'narrowerDirections':len(children[id]),'directlyAllocatedSourceQuestions':len(homes[id]),'admittedPositiveTargetSources':len(supports[id]),'sourceQuestionsUnderProposedNarrowerClosure':len(subtree(id)),'alternatives':sorted(rows,key=lambda r:({'narrower':0,'broader':2}.get(r['kind'],1),r['title']))}
paths=[['Dark sectors: candidates, cosmic histories and tests','Cosmological survival and depletion of dark relics','Threshold KK cascades, dark matter and irreducible freeze-in','Linear cosmology of decay-induced dark-matter kicks'],['Extra dimensions and conditional quantum-gravity tests','Stellar production and cooling bounds on extra dimensions','Threshold KK cascades, dark matter and irreducible freeze-in','Linear cosmology of decay-induced dark-matter kicks'],['Black-hole entropy, horizon structure and gravitational limits','Microscopic and near-horizon entropy accounts','Counting topology-supported BPS configurations'],['Black-hole entropy, horizon structure and gravitational limits','Excitation spectra, relaxation and near-horizon limits','Near-extremal thresholds and AdS2 limits']]
views=[]
for path in paths:
    steps=[]
    for title in path:
        id=titles[title];steps.append({'destinationId':id,'title':title,'question':dest[id]['question'],**frontier(id)})
    views.append({'status':'candidate_routes_pending_explicit_adjudication','steps':steps})
allfront={id:frontier(id) for id in dest if incident[id]};over=[{'destinationId':id,'title':dest[id]['title'],'scientificLinks':x['scientificLinks'],'distinctDestinations':x['distinctDestinations'],'byType':x['byType']} for id,x in allfront.items() if x['distinctDestinations']>15]
result={'schemaVersion':'q025-researcher-navigation-preview/1','coverage':'5,765-source admitted organizational cohort; all displayed route proposals are explicitly pending. Stable seven-arc KK subgraph already exists separately.','paths':views,'frontierCensus':{'scopesWithCandidateConnections':len(allfront),'moreThan15ScientificLinks':sum(x['scientificLinks']>15 for x in allfront.values()),'moreThan15DistinctScientificNeighbors':len(over),'duplicateEndpointLinkExcess':sum(x['scientificLinks']-x['distinctDestinations'] for x in allfront.values()),'maximumDistinctScientificNeighbors':max(x['distinctDestinations'] for x in allfront.values()),'nodesNeedingGrouping':sorted(over,key=lambda x:-x['distinctDestinations'])},'proposal':'Prefer actual narrower scientific directions, then typed cross-routes and broader entrances, before source-question facet access. For the explicitly listed crowded scientific frontiers, preserve all links and provide type/perspective grouping; do not merge distinct target scopes or force five directions.','scientificWarnings':['Native premise/application labels require explicit direction adjudication; incoming access is not converse scientific implication.','Threshold/full-wave linear records need explicit stable-KK reuse/compound reconciliation.','Proposed closure source counts are preview counts, not admitted containment or new H mass.','Source counts are extracted question units, not unique papers.']}
(B/'researcher-preview.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
md=['These are concrete candidate journeys through admitted scientific scopes. The seven earlier KK routes are admitted; the additional routes below are awaiting explicit adjudication. Counts refer to extracted source questions, not papers.','']
for i,v in enumerate(views,1):
    md += [f'**Journey {i}: '+ ' → '.join(s['title'] for s in v['steps'])+'**','']
    md+=['| View | Scientific alternatives | Sources |','| --- | --- | --- |']
    for s in v['steps']:
        types=', '.join(f'{n} {k}' for k,n in sorted(s['byType'].items()))
        md.append(f"| {s['title']} | {s['distinctDestinations']} distinct neighbors ({types}); {s['narrowerDirections']} narrower directions | {s['directlyAllocatedSourceQuestions']} direct; {s['admittedPositiveTargetSources']} positive-target supports; {s['sourceQuestionsUnderProposedNarrowerClosure']} under proposed narrower closure |")
    md+=['',v['steps'][-1]['question'],'']
md+=['The two dark-sector entrances converge on the same scoped linear-cosmology destination. The threshold premise check remains distinct from initial production and observational reanalysis. The full-wave compound threshold card must be reconciled against the existing separate threshold and flat-dimension-bound destinations; shared sources do not silently merge them.','',f"Across {len(allfront)} connected scientific scopes, {len(over)} have more than 15 distinct scientific neighbors. All native narrower frontiers have at most 13 directions. The remaining crowding comes from useful cross-routes, multiple parents and repeated endpoint links; it should be grouped by relation/perspective and paginated, not silently removed.",'','The current alphabetical cap also mixes exact source-facet access with scientific routes. Root approved prioritizing scientific directions first while retaining all source access. The accompanying JSON includes every alternative and the exact candidate link IDs, so this preview can be checked against the underlying decisions.']
(B/'RESEARCHER-PREVIEW.md').write_text('\n'.join(md)+'\n');print(json.dumps({'paths':len(views),'connectedScopes':len(allfront),'over15':len(over),'maxNeighbors':max(x['distinctDestinations'] for x in allfront.values()),'previewSha256':hashlib.sha256((B/'researcher-preview.json').read_bytes()).hexdigest()}))
