"""Exact, non-transitive H_broad^T R_positive access certificates; no admission."""
import collections,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent; ROOT=B.parents[3]
def read(p):
    raw=p.read_bytes();return json.loads(raw),{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def save(name,x):
    p=B/name;p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');return read(p)[1]
p,ppin=read(B.parent/'organization-v4/candidate-v1/aggregate.local.json')
diagnostic,dpin=read(B/'coverage-paths.json'); native,npin=read(ROOT/'research/q025/evaluation/full-pass/reconciliation-v1/parent-navigation-candidates-v5-20261117T135430Z.json')
ds={x['id']:x for x in p['destinations']}; decisions={x['id']:x for x in p['decisions']}
homes=collections.defaultdict(list)
for h in p['placements']:
    if h['status']=='accepted' and h['role'] in ('member','overlap') and h.get('allocationWeight',0)>0:homes[h['unitId']].append(h)
routes=collections.defaultdict(list);excluded_roles=collections.Counter()
for row in p['sourceContributions']:
    proof=decisions[row['decisionId']]; assert proof['status']=='accepted' and proof['type']=='source_contribution'
    for h in homes.get(row['unitId'],[]):
        s,t=h['destinationId'],row['destinationId']
        if ds[s]['kind']!='region' or s==t:continue
        if row['role'] not in ('addresses','instantiates','specializes'):
            excluded_roles[row['role']]+=1;continue
        hp=decisions[h['decisionId']];assert hp['status']=='accepted' and hp['type'] in ('placement','overlap')
        assert proof['scopeContentSha256']==ds[t]['scopeContentSha256']
        assert hp['scopeContentSha256']==ds[s]['scopeContentSha256']
        routes[(s,t)].append({'unitId':row['unitId'],'placement':h,'contribution':row,
                            'placementDecision':hp,'contributionDecision':proof})
certificates=[]
for (s,t),supports in sorted(routes.items()):
    # Multiple separately admitted roles remain separate evidence, not repeated mass.
    units={x['unitId'] for x in supports}
    assert len(units)==len(supports), 'Current cut expected unique unit witnesses per route; review multiplicity before changing policy'
    endpoints={k:{'id':did,'kind':ds[did]['kind'],'scopeContentSha256':ds[did]['scopeContentSha256'],'scopeDecisionId':ds[did]['scopeDecisionId']} for k,did in [('source',s),('target',t)]}
    record={'id':'organizational-access:'+digest([s,t])[:24],'type':'related_question','source':s,'target':t,
            'targetKind':ds[t]['kind'],'status':'pending_coordinator_admission','canonicalIdentityStatus':'unreconciled_endpoints_preserved',
            'title':ds[t]['title'],'incomingTitle':ds[s]['title'],'endpointBindings':endpoints,
            'uniqueWitnessCount':len(units),'supportRoles':dict(collections.Counter(x['contribution']['role'] for x in supports)),
            'supports':supports,'semantics':'Organizational access through the exact same source question; no containment, physical implication, equivalence, premise transfer, method applicability or allocation.',
            'reviewBasis':'deterministic_composition_of_explicit_home_and_admitted_positive_contribution_not_independent_route_review'}
    record['certificateSha256']=digest(record);certificates.append(record)
old={(x['source'],x['target']):{r['unitId'] for r in x['supports']} for x in diagnostic['candidateSupportRoutes']}
assert len(certificates)==1042 and all(old[(r['source'],r['target'])]=={s['unitId'] for s in r['supports']} for r in certificates)
certpin=save('access-certificates.local.json',{'inputs':[ppin,dpin],'routes':certificates})
base=[]
for x in native['links']:
    if x['agreement']=='paired_endpoint_type' and x['source']['kind']==x['target']['kind']=='scientific_scope':
        s,t=x['source']['candidateId'],x['target']['candidateId']
        if s in ds and t in ds:base.append({'source':s,'target':t,'type':x['challengeLink']['type'],'status':'candidate'})
base += [dict(r,status='admitted') for r in p['relations']]
def frontier(edges):
    neighbors=collections.defaultdict(set);kinds=collections.defaultdict(collections.Counter)
    for e in edges:
        s,t=e['source'],e['target'];neighbors[s].add(t);neighbors[t].add(s)
        kinds[s][e['type']+':outgoing']+=1;kinds[t][e['type']+':incoming']+=1
    sizes=[len(neighbors[d]) for d in ds];multi=collections.Counter(r['target'] for r in certificates)
    return {'scientificDestinations':len(ds),'destinationsWithAnyChoice':sum(x>0 for x in sizes),'maxDistinctChoices':max(sizes),'moreThan15':sum(x>15 for x in sizes),
            'distinctChoiceHistogram':dict(sorted(collections.Counter(sizes).items())),
            'crowdedDestinations':[{'id':d,'title':ds[d]['title'],'kind':ds[d]['kind'],'distinctChoices':len(neighbors[d]),'incidentArcsByTypeAndTraversal':dict(kinds[d])} for d in sorted(ds,key=lambda x:-len(neighbors[x])) if len(neighbors[d])>15],
            'countsExcludeSourceFacetsAndClassification':True,'incomingTraversalIsAccessNotConverseScientificAssertion':True}
after=base+[{'source':r['source'],'target':r['target'],'type':'derived_organizational_access'} for r in certificates]
before_pairs={tuple(sorted([r['source'],r['target']])) for r in base}
frontiers={'inputs':[ppin,npin,certpin],'candidateNativePlusAdmittedBefore':frontier(base),'sameCandidateGraphPlusProposedAccess':frontier(after),
           'admittedOnlyBefore':frontier(p['relations']),'admittedPlusProposedAccess':frontier(p['relations']+[{'source':r['source'],'target':r['target'],'type':'derived_organizational_access'} for r in certificates]),
           'newDistinctEndpointPairsRelativeToCandidateNative':sum(tuple(sorted([r['source'],r['target']])) not in before_pairs for r in certificates),
           'limitation':'Candidate native route types/directions remain unadmitted. These are choice-count and accessibility diagnostics, not containment or full-release coverage.'}
fp=save('access-frontiers.json',frontiers)
# Hydrate only the exact selected source descriptions; no sealed/source-page text.
prefixes=['unit:a83c7372','unit:72ea9aab','unit:68b2460d','unit:0034b70e']
selected=[]
def witness_route(prefix,target_suffix=None):
    return next((r,next(s for s in r['supports'] if s['unitId'].startswith(prefix))) for r in certificates if any(s['unitId'].startswith(prefix) for s in r['supports']) and (target_suffix is None or r['target'].endswith(target_suffix)))
selections=[('region_target_exception','unit:a83c7372',None),('compound_target_without_premise_transfer','unit:72ea9aab',None),
            ('setting_support_is_not_proof','unit:68b2460d','bc0e38e8d6299c3104eddde6'),('exact_geometric_source_positive_role','unit:0034b70e',None)]
needed={witness_route(pre,suf)[1]['unitId'] for _,pre,suf in selections}
multi=[r for r in certificates if r['target']=='q025-candidate-question:f19bee7b8e7cec3d7887c150']
assert len(multi)==3
needed.update(r['supports'][0]['unitId'] for r in multi)
units={}; manifest=json.loads((ROOT/'data/navigation/manifest.json').read_text())
for shard in manifest['files']['units']:
    raw=(ROOT/'data/navigation'/shard['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==shard['sha256']
    for u in json.loads(raw):
        if u['id'] in needed:units[u['id']]=u
assert needed==units.keys()
def science(d):return {k:d[k] for k in ('id','kind','title','question','summary','scope','readingCoverage','scopeContentSha256') if k in d}
def example(r,s):
    u=units[s['unitId']]
    return {'routeId':r['id'],'certificateSha256':r['certificateSha256'],'sourceScope':science(ds[r['source']]),'targetScope':science(ds[r['target']]),
            'sourceQuestion':{'unitId':u['id'],'paperId':u['paperId'],'description':u['text'],'textSha256':u['evidence']['textSha256']},'exactSupport':s,'routeWitnessCount':r['uniqueWitnessCount']}
interpretations={
 'region_target_exception':'Explicit extra class: region→region organizational access. Conditional IIA trial-search statistics must not merge into the IIB ensemble or become a universal probability.',
 'compound_target_without_premise_transfer':'The intact source connects cutoff compatibility/universality with a conditional species-scale inference. This route does not say Dark Dimension explains the cutoff. It is distinct from the historical HiRes control, which has no KK science link.',
 'setting_support_is_not_proof':'The source supplies a setting/entropy-test apparatus; the exact qualification excludes an independent proof and retains source-local extraction limits. The truncated challenge ending remains historical, not completed by the exporter.',
 'exact_geometric_source_positive_role':'The exact source has an admitted broad home and a specializes role to genus-one/discrete-gauge scope. Six constructions and the degree-one exclusion remain source-local; the separate method role does not enter this class.'}
for label,pre,suf in selections:
    r,s=witness_route(pre,suf);selected.append({'case':label,'interpretation':interpretations[label],**example(r,s)})
selected.append({'case':'same_question_reachable_from_three_broad_homes','interpretation':'Three distinct exact source witnesses from three admitted broad homes reach the same unchanged relic-production question. No scope alias, narrower relation or duplicate H allocation is inferred.','routes':[example(r,r['supports'][0]) for r in multi]})
uid=next(u for u in needed if u.startswith('unit:0034b70e'));excluded=next(r for r in p['sourceContributions'] if r['unitId']==uid and r['role']=='method');h=homes[uid][0]
selected.append({'case':'same_source_method_role_is_excluded','sourceScope':science(ds[h['destinationId']]),'targetScope':science(ds[excluded['destinationId']]),
                'sourceQuestion':{'unitId':uid,'paperId':units[uid]['paperId'],'description':units[uid]['text']},'excludedContribution':excluded,'contributionDecision':decisions[excluded['decisionId']],
                'interpretation':'Even exact same-source method support is excluded from R_positive. This row neither creates this organizational route nor a USING relationship. Another independently qualifying source could still support the endpoint pair; this witness is not promoted.',
                'thisUnitExcludedFromTargetRoute':not any(r['source']==h['destinationId'] and r['target']==excluded['destinationId'] and any(s['unitId']==uid for s in r['supports']) for r in certificates)})
ep=save('access-examples.json',{'inputs':[ppin,certpin],'examples':selected})
policy={'schemaVersion':'q025-organizational-access-proposal/1','status':'pending_explicit_coordinator_class_admission','inputs':[ppin,dpin,npin],
        'certificateFile':certpin,'examples':ep,'frontiers':fp,'routeCount':len(certificates),'targetKinds':dict(collections.Counter(r['targetKind'] for r in certificates)),
        'supportRows':sum(r['uniqueWitnessCount'] for r in certificates),'uniqueSourceWitnesses':len({s['unitId'] for r in certificates for s in r['supports']}),
        'singletonWitnessRoutes':sum(r['uniqueWitnessCount']==1 for r in certificates),'sourceBroadScopes':len({r['source'] for r in certificates}),
        'targetScopes':len({r['target'] for r in certificates}),'targetsAccessibleFromMultipleBroadHomes':sum(n>1 for n in collections.Counter(r['target'] for r in certificates).values()),
        'excludedRoleWitnesses':dict(excluded_roles),
        'classA':'1,041 direct accepted region-home→admitted question routes via exact same source unit with admitted addresses/instantiates/specializes. Both scope versions and every allocation/contribution evidence/qualification are pinned.',
        'classB':'One separately enumerated region→region route, with exact IIA/IIB ensemble distinction retained; approval of question-only Class A does not implicitly approve this class.',
        'semantics':'Nonzero incidence H_broad^T R_positive supplies organizational access only. Witness counts are inventories, not probabilities, confidence or H mass. No transitive generation.',
        'requiredRevalidation':['Accepted direct positive-weight home; never ancestor union/support centroid or proposed home.','Accepted exact positive source contribution; same unit ID, not same paper or similar wording.','Both endpoint scope hashes and canonical mapping remain current. Any identity or scope amendment invalidates the old certificate until rejoined.','Retain all qualifications, source evidence and original review pins; no truncation repair or transfer of source-local premises.'],
        'presentation':'Keep explicit scientific narrower/premise/application/method/comparison routes ahead of derived organizational access; retain all access links in all-connections. Label these as shared-source organizational access. Incoming traversal is navigation, not a converse claim. Counts stay scope-wide unless a complete witness filter is applied.',
        'notChanged':['source allocation H','containment','canonical identity','scope definitions','source contribution roles','method applicability or USING','physical scientific relations','reviewed edge directions'],
        'readingLimit':'Deterministic admission-composition audit, not new primary-source reading or independent route review. Current cut has5,765 allocated sources; pending2,665 and sealed43 are not silently covered.'}
pin=save('access-proposal.json',policy)
lines=['# Shared-source organizational access proposal','',f"Pending approval: **1,041 region→question routes plus one separately enumerated region→region route**. The exact certificates contain3,774 support rows from2,066 unique source questions. No membership, weight, containment or physical implication changes.",'',
       'The source side is a direct accepted broad home. The target side is an admitted addresses, instantiates or specializes contribution by the identical source unit. This is a non-transitive incidence composition, not a semantic similarity or same-paper join. Full qualifications and both underlying decisions remain inspectable.','',
       '| Graph used for choice counts | Connected scopes | Maximum choices | Scopes above15 |','|---|---:|---:|---:|']
for key in ('candidateNativePlusAdmittedBefore','sameCandidateGraphPlusProposedAccess','admittedOnlyBefore','admittedPlusProposedAccess'):
    f=frontiers[key];lines.append(f"| {key} | {f['destinationsWithAnyChoice']} | {f['maxDistinctChoices']} | {f['moreThan15']} |")
lines += ['', 'These counts exclude exact-source facets and classification. The first two rows include unadmitted native route proposals and incoming traversal; they are a usability probe, not accepted scientific reachability. The other two isolate currently admitted routes. Recompute after actual route admission and residual placements.','',
          'The six complete cases are in access-examples.json: the statistical-region exception; compound UHECR/species-scale inference; black-hole setting support without proof; genus-one geometry; one relic-production question reached from three broad homes; and the exact same-source method role that is excluded.','',
          'Derived access stays below explicit scientific routes in foreground ordering. Large frontiers remain available through all-connections; witness count must not masquerade as relevance or applicability. A method/year lens cannot silently filter representative witnesses and report a complete filtered count.','',
          f"Proposal SHA-256: `{pin['sha256']}`. Certificate payload SHA-256: `{certpin['sha256']}`."]
(B/'ACCESS-PROPOSAL.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'proposal':pin,'counts':{k:policy[k] for k in ('routeCount','targetKinds','supportRows','uniqueSourceWitnesses','targetsAccessibleFromMultipleBroadHomes')},'frontiers':{k:{x:frontiers[k][x] for x in ('destinationsWithAnyChoice','maxDistinctChoices','moreThan15')} for k in ('candidateNativePlusAdmittedBefore','sameCandidateGraphPlusProposedAccess','admittedOnlyBefore','admittedPlusProposedAccess')}},indent=2))
