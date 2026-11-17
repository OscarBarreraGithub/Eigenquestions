"""Measure admitted supports and pending routes without promoting either."""
import collections, hashlib, json
from pathlib import Path
B = Path(__file__).resolve().parent
ROOT = B.parents[3]
F = ROOT / 'research/q025/evaluation/full-pass'
def read(p):
    raw=p.read_bytes()
    return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()}
paths=['admissions-v3/supported-scope-role-component-v3.json','canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json','organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json','canonical-role-admissions-v1/role-component.json']
inputs=[read(F/p) for p in paths]
dest={d['id']:d for c,pin in inputs for d in c.get('destinations',[])}
roles=[r for c,pin in inputs for r in c.get('sourceContributions',[])]
policy,ppin=read(B/'placement-policy-candidates.local.json')
homes=collections.defaultdict(set)
for item in policy['completeEligibleInventory']:
    for p in item.get('placements',[item['proposal']] if 'proposal' in item else []):homes[p['destinationId']].add(item['unitId'])
homes['q025-candidate-question:fc582eff749d1936943465cf'].add('unit:bd8c5b9a8b57126b3ca4cd9f8f106d4a591051d19ace30fd62d33141efb25f60')
homes['q025-candidate-region:839da90831bec9d6ef0a811b'].add('unit:0034b70ea953b9879b3d6034ad618cbfcb1be80a68ce1e19fa6ffa94793dec60')
support=collections.defaultdict(set)
for r in roles:
    if r['role'] in ('addresses','instantiates','specializes'):support[r['destinationId']].add(r['unitId'])
questions={d for d in dest if dest[d]['kind']=='question'}
regions=set(dest)-questions
raw,linkpin=read(F/'reconciliation-v1/parent-navigation-candidates-v5-20261117T135430Z.json')
links=[l for l in raw['links'] if l['source']['kind']==l['target']['kind']=='scientific_scope' and l['source']['candidateId'] in dest and l['target']['candidateId'] in dest and l['agreement']=='paired_endpoint_type']
def graph(mode):
    g=collections.defaultdict(list)
    for l in links:
        s,t=l['source']['candidateId'],l['target']['candidateId']
        if mode=='narrow_only' and l['challengeLink']['type']!='narrows':continue
        g[s].append((t,l,'forward'))
        if mode=='typed_connections':g[t].append((s,l,'incoming'))
    return g
def path(g,s,t):
    todo=collections.deque([s]);previous={s:None}
    while todo:
        u=todo.popleft()
        if u==t:break
        for v,l,direction in g[u]:
            if v not in previous:previous[v]=(u,l,direction);todo.append(v)
    if t not in previous:return None
    rows=[]
    while previous[t]:
        u,l,direction=previous[t]
        rows.append({'from':u,'fromTitle':dest[u]['title'],'to':t,'toTitle':dest[t]['title'],'candidateLinkId':l['id'],'nativeType':l['challengeLink']['type'],'readingDirection':direction,'rationale':l['challengeLink']['reason'],'status':'pending_explicit_navigation_decision'})
        t=u
    return rows[::-1]
titles={d['title']:d['id'] for d in dest.values()}
journeys=[]
for start,end in [('Dark sectors: candidates, cosmic histories and tests','Linear cosmology of decay-induced dark-matter kicks'),('Extra dimensions and conditional quantum-gravity tests','Linear cosmology of decay-induced dark-matter kicks'),('Linear cosmology of decay-induced dark-matter kicks','Stellar production and cooling bounds on extra dimensions'),('Compactification vacua, effective theories and stability','KK spectra, eigenmodes and interactions')]:
    if start in titles and end in titles:journeys.append({'start':start,'end':end,**{mode:path(graph(mode),titles[start],titles[end]) for mode in ['narrow_only','typed_connections']}})
parents=collections.defaultdict(set);outgoing=collections.Counter()
for l in links:
    if l['challengeLink']['type']=='narrows':parents[l['target']['candidateId']].add(l['source']['candidateId']);outgoing[l['source']['candidateId']]+=1
zero=[d for d in questions if not homes[d]]
result={'schemaVersion':'q025-navigation-candidate-diagnostic/1','status':'candidate_route_comparison_not_admission','inputs':[pin for c,pin in inputs]+[ppin,linkpin],
        'allocationCoverage':{'sourceQuestions':len({u for us in homes.values() for u in us}),'directQuestionDestinations':sum(bool(homes[d]) for d in questions),'questionAllocatedSources':len({u for d in questions for u in homes[d]}),'directBroadDestinations':sum(bool(homes[d]) for d in regions),'broadAllocatedSources':len({u for d in regions for u in homes[d]}),'totalAdmittedQuestionScopes':len(questions),'zeroAllocationWithPositiveSupport':sum(bool(support[d]) for d in zero),'zeroAllocationWithoutPositiveSupport':sum(not support[d] for d in zero),'eligibleUnallocated':8430-len({u for us in homes.values() for u in us}),'holdoutUnallocated':43},
        'supportCoordinatePolicyCandidate':{'roles':['addresses','instantiates','specializes'],'deduplicateBy':['destinationId','unitId'],'weight':'Global per-paper question mass, normalized within each support set; excluded from H and C.','basis':'Centroid of exact supported source coordinates, explicitly distinct from allocated membership position.','exclude':['method','comparison','boundary','same-paper context'],'additionalHMass':0,'unallocatedSourceSupport':'Can be positioned only in a common pinned source-coordinate chart; do not substitute an unrelated allocated home or invent coordinates for sources absent from the chart.'},
        'routeInventory':{'allParentRecords':len(raw['links']),'pairedScopeLinksWithAdmittedEndpoints':len(links),'scopeDestinationsWithMultipleNarrowParents':sum(len(x)>1 for x in parents.values()),'narrowFrontierSizeDistribution':dict(sorted(collections.Counter(outgoing.values()).items())),'moreThan15NarrowDirections':sum(n>15 for n in outgoing.values()),'candidateTypes':dict(collections.Counter(l['challengeLink']['type'] for l in links))},
        'journeys':journeys,'limitations':['These are proposed routes, not accepted navigation. Premise/application direction must be explicitly adjudicated; native labels alone do not supply final semantics.','Narrow-only comparison permits only outgoing native narrows proposals; typed_connections also exposes incoming links without asserting a converse physical relation.','Stable KK admission IDs and new full-wave records remain separate pending explicit reuse/compound-scope reconciliation.','The current public global graph is not complete. Original numerical batches are excluded from both comparisons.'],
        'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(B/'navigation-candidate-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'allocationCoverage':result['allocationCoverage'],'routeInventory':result['routeInventory'],'journeys':[{'start':j['start'],'end':j['end'],**{mode:None if j[mode] is None else len(j[mode]) for mode in ['narrow_only','typed_connections']}} for j in journeys]},indent=2))
