"""Read-only workload experiments. Packs are review queues, never science clusters.
No model calls, source archive reads, sealed files, or campaign mutations.
"""
import collections,hashlib,json,math,statistics,time
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[3];E=ROOT/'research/q025/evaluation'
def read(path):
    raw=path.read_bytes();return json.loads(raw),{'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def digest(x):return hashlib.sha256(compact(x).encode()).hexdigest()
def primary_key(m):
    c=m['sourceContext'];return (c['path'],c['pdfPage'],c['start'],c['end'],c['textSha256'])
index,ipin=read(E/'full-pass/canonical-wave-v1/final-source-index.json')
registry,rpin=read(E/'full-pass/reconciliation-v1/authored-scope-registry-v3-20261117T121953Z.json')
assert rpin['sha256']=='c9c419d7ded388f1355e31b1bef413ab09ca12de0e7cd60be996f687655fcf8a'
records={r['recordId']:r for r in registry['records']};scope_ids=sorted(records);scopes={};units={};primary={};scope_units=collections.defaultdict(set);scope_primary=collections.defaultdict(set);edges={};nomination_to_edge={};exposure=collections.Counter();primary_exposure=collections.Counter();unit_exposure=collections.Counter();scope_exposure=collections.Counter();packet_pins=[];baseline_sizes=[];baseline_scope_counts=[];baseline_pair_counts=[]
for family in index['families']:
    p,pin=read(E/family['sourcePacketPath']);assert pin['sha256']==family['sourcePacketSha256'];packet_pins.append(pin);baseline_sizes.append(family['characters']);baseline_scope_counts.append(len(p['scopes']));baseline_pair_counts.append(len(p['nominations']));ref=p['refRegistry'];scope_ref={s['ref']:s['recordId'] for s in p['scopes']}
    for u in p['units']:
        uid=u['unitId'];value={'unitId':uid,'paperId':u['paperId'],'description':u['description'],'textSha256':ref[u['ref']]['textSha256']};assert uid not in units or units[uid]==value;units[uid]=value;unit_exposure[uid]+=1;exposure['descriptionCharacters']+=len(u['description'])
    for e in p['evidence']:
        m=ref[e['ref']];key=digest(primary_key(m));value={'id':key,'locator':m,'text':e['text']};value['locator']={k:v for k,v in m.items() if k not in ['ref','localRef','unitIndex']};assert key not in primary or primary[key]['text']==value['text'];primary[key]=value;primary_exposure[key]+=1;exposure['primaryTextCharacters']+=len(e['text'])
    for s in p['scopes']:
        rid=s['recordId'];scope_units[rid];scope_primary[rid];scope_exposure[rid]+=1;assert s['definition']==records[rid]['definition']
        for name in s['evidenceRefs']:
            m=ref[name]
            if m['kind']=='description':scope_units[rid].add(m['unitId'])
            elif m['kind'] in ['primary','source_excerpt']:scope_primary[rid].add(digest(primary_key(m)))
        for c in s['sourceContributions']:scope_units[rid].add(ref[c['unitRef']]['unitId'])
    for n in p['nominations']:
        key=tuple(sorted([scope_ref[n['left']],scope_ref[n['right']]]));edges.setdefault(key,{'recordIds':list(key),'nominationIds':[],'channels':set()});edges[key]['nominationIds'].append(n['id']);edges[key]['channels'].update(n['channels']);nomination_to_edge[n['id']]=key
for edge in edges.values():edge['nominationIds']=sorted(set(edge['nominationIds']));edge['channels']=sorted(edge['channels'])
assert set(scope_units)==set(records)
for rid,r in records.items():
    scopes[rid]={'recordId':rid,'candidateId':r['candidateId'],'admittedDestinationId':r.get('admittedDestinationId'),'kind':r['kind'],'scopeStatus':r['scopeStatus'],'definition':r['definition'],'methods':r['methods'],'sourceContributions':[{k:c.get(k) for k in ['unitId','paperId','role','independentRoleAgreement','basis','sourceOrigin','materialScopeFlag']} for c in r['contributions']],'sourceUnitIds':sorted(scope_units[rid]),'inheritedPrimaryLocatorIds':sorted(scope_primary[rid]),'scopeDefinitionFlags':r.get('scopeDefinitionFlags',[]),'admissionJustificationFlags':r.get('admissionJustificationFlags',[]),'priorReadingPins':r['pins'],'readingMeaning':'Exact supplied scope and whole source descriptions; inherited paired-reading assessments are attributed. Primary is reread only when its text is included.'}
scope_cost={id:len(compact(row))+1 for id,row in scopes.items()};unit_cost={id:len(compact(row))+1 for id,row in units.items()};primary_cost={id:len(compact(row))+1 for id,row in primary.items()};edge_cost={key:len(compact(row))+1 for key,row in edges.items()}
scope_refs={id:'c'+str(i) for i,id in enumerate(sorted(scopes))};unit_refs={id:'u'+str(i) for i,id in enumerate(sorted(units))};edge_refs={key:'n'+str(i) for i,key in enumerate(sorted(edges))}
compact_scopes={}
for id,row in scopes.items():
    r=records[id];assessment=r.get('assessment') or {}
    compact_scopes[id]={'ref':scope_refs[id],'kind':row['kind'],'scopeStatus':row['scopeStatus'],'definition':row['definition'],'methods':row['methods'],'sourceContributions':[{**{k:v for k,v in c.items() if k not in ['unitId','paperId']},'unitRef':unit_refs[c['unitId']]} for c in row['sourceContributions']],'sourceRefs':[unit_refs[u] for u in row['sourceUnitIds']],'priorReadingAssessment':{k:v for k,v in assessment.items() if k not in ['id','refs']},'scopeDefinitionFlags':row['scopeDefinitionFlags'],'admissionJustificationFlags':row['admissionJustificationFlags'],'inheritedPrimaryWindowCount':len(scope_primary[id]),'primaryRereadInThisPacket':False}
    if row['admittedDestinationId']:compact_scopes[id]['admittedDestinationId']=row['admittedDestinationId']
compact_units={id:{'ref':unit_refs[id],'paperId':row['paperId'],'description':row['description']} for id,row in units.items()}
compact_edges={key:{'ref':edge_refs[key],'left':scope_refs[key[0]],'right':scope_refs[key[1]],'channels':row['channels']} for key,row in edges.items()}
compact_scope_cost={id:len(compact(row))+1 for id,row in compact_scopes.items()};compact_unit_cost={id:len(compact(row))+1 for id,row in compact_units.items()};compact_edge_cost={key:len(compact(row))+1 for key,row in compact_edges.items()}
edge_keys=list(edges);incident=collections.defaultdict(set)
for edge in edge_keys:
    for rid in edge:incident[rid].add(edge)
def stats(values):
    return {'min':min(values),'median':statistics.median(values),'mean':statistics.mean(values),'max':max(values),'sum':sum(values)}
def payload(ids,pairs,mode):
    us=set().union(*(scope_units[id] for id in ids));ps=set().union(*(scope_primary[id] for id in ids))
    if mode=='triage_refs':return {'kind':'canonical-triage-with-pinned-reference-sidecar-not-dispatch','registrySha256':rpin['sha256'],'scopes':[compact_scopes[id] for id in sorted(ids)],'units':[compact_units[id] for id in sorted(us)],'nominations':[compact_edges[key] for key in sorted(pairs)],'readingMeaning':'Exact full scope definitions, source descriptions and inherited paired-reading summaries. No primary excerpts reread. Stable record/source/nomination IDs, hashes and original evidence-reference maps remain in the pinned machine sidecar. Workload neighborhoods do not imply shared scientific scope.'}
    return {'kind':'canonical-review-design-measurement-not-dispatch','registrySha256':rpin['sha256'],'mode':mode,'scopes':[scopes[id] for id in sorted(ids)],'units':[units[id] for id in sorted(us)],'primaryWindows':[primary[id] for id in sorted(ps)] if mode=='rich' else [],'nominations':[edges[key] for key in sorted(pairs)],'scopeMeaning':'A workload packet, not a shared scientific region. No uniqueness or equivalence is implied.','readingMeaning':'No primary source reread in triage mode; exact original primary locators remain inherited references to the pinned registry.'}
def packing(name,mode,max_scopes,max_pairs,max_chars,heuristic):
    started=time.monotonic();remaining=set(edge_keys);batches=[];uncovered=set(records)
    sc=compact_scope_cost if mode=='triage_refs' else scope_cost;uc=compact_unit_cost if mode=='triage_refs' else unit_cost;ec=compact_edge_cost if mode=='triage_refs' else edge_cost
    while remaining:
        degree=collections.Counter(r for e in remaining for r in e)
        seed=min(remaining) if heuristic=='lexical_edge_order' else max(remaining,key=lambda e:(degree[e[0]]+degree[e[1]],e))
        ids=set(seed);pairs={seed};us=set().union(*(scope_units[id] for id in ids));ps=set().union(*(scope_primary[id] for id in ids));cost=1000+sum(sc[id] for id in ids)+sum(uc[id] for id in us)+sum(primary_cost[id] for id in ps)*(mode=='rich')+ec[seed]
        if cost>max_chars:raise ValueError(('single pair oversize',name,seed,cost))
        while len(pairs)<max_pairs:
            internal=sorted({e for rid in ids for e in incident[rid]&remaining if set(e)<=ids}-pairs)
            for edge in internal:
                if len(pairs)>=max_pairs or cost+ec[edge]>max_chars:break
                pairs.add(edge);cost+=ec[edge]
            if len(pairs)>=max_pairs:break
            candidates={r for id in ids for e in incident[id]&remaining for r in e if r not in ids}
            best=None
            if len(ids)<max_scopes:
                for rid in sorted(candidates):
                    gained=[e for e in incident[rid]&remaining if set(e)-{rid}<=ids]
                    new_u=scope_units[rid]-us;new_p=scope_primary[rid]-ps;increment=sc[rid]+sum(uc[u] for u in new_u)+(sum(primary_cost[p] for p in new_p) if mode=='rich' else 0)
                    gained=sorted(gained)[:max_pairs-len(pairs)];inc=increment+sum(ec[e] for e in gained)
                    if cost+inc>max_chars or not gained:continue
                    score=(len(gained),-increment,degree[rid]) if heuristic=='star' else (len(gained)/max(inc,1),len(gained),-increment)
                    if best is None or score>best[0]:best=(score,rid,gained,new_u,new_p,inc)
            if best:
                _,rid,gained,new_u,new_p,inc=best;ids.add(rid);pairs.update(gained);us|=new_u;ps|=new_p;cost+=inc;continue
            # Fit a disjoint edge only as a separate named workload neighborhood.
            options=[]
            for edge in remaining-pairs:
                new=set(edge)-ids
                if len(ids|set(edge))>max_scopes:continue
                new_u=set().union(*(scope_units[id] for id in new))-us;new_p=set().union(*(scope_primary[id] for id in new))-ps
                inc=sum(sc[id] for id in new)+sum(uc[u] for u in new_u)+(sum(primary_cost[p] for p in new_p) if mode=='rich' else 0)+ec[edge]
                if cost+inc<=max_chars:options.append((inc,edge,new,new_u,new_p))
            if not options:break
            inc,edge,new,new_u,new_p=min(options,key=lambda x:(x[0],x[1]));ids|=new;pairs.add(edge);us|=new_u;ps|=new_p;cost+=inc
        actual=payload(ids,pairs,mode);chars=len(compact(actual));assert chars<=max_chars,(name,chars,cost)
        batches.append({'recordIds':sorted(ids),'comparisonKeys':[list(e) for e in sorted(pairs)],'nominationIds':sorted({id for e in pairs for id in edges[e]['nominationIds']}),'characters':chars,'sourceDescriptions':len(us),'primaryWindows':len(ps) if mode=='rich' else 0,'sourceDescriptionCharacters':sum(len(units[u]['description']) for u in us),'primaryTextCharacters':sum(len(primary[p]['text']) for p in ps) if mode=='rich' else 0});remaining-=pairs;uncovered-=ids
    assert not uncovered
    covered={n for p in batches for n in p['nominationIds']};assert covered==set(nomination_to_edge)
    sizes=stats([p['characters'] for p in batches]);scope_ex=collections.Counter(r for p in batches for r in p['recordIds']);pair_counts=stats([len(p['comparisonKeys']) for p in batches]);record_counts=stats([len(p['recordIds']) for p in batches]);elapsed=time.monotonic()-started
    summary={'name':name,'mode':mode,'limits':{'maxScopes':max_scopes,'maxPairs':max_pairs,'maxInputCharacters':max_chars},'heuristic':heuristic,'packets':len(batches),'callsIfEveryPacketProposedAndChallenged':2*len(batches),'callsIfTriageOnlySinglePass':len(batches),'inputCharacters':sizes,'scopesPerPacket':record_counts,'pairsPerPacket':pair_counts,'scopeExposures':sum(scope_ex.values()),'maxRepeatedScopeExposures':max(scope_ex.values()),'sourceDescriptionExposures':sum(p['sourceDescriptions'] for p in batches),'primaryWindowExposures':sum(p['primaryWindows'] for p in batches),'primaryTextCharacters':sum(p['primaryTextCharacters'] for p in batches),'sourceDescriptionCharacters':sum(p['sourceDescriptionCharacters'] for p in batches),'coveredUniqueComparisons':len(edge_keys),'coveredNominationIds':len(covered),'coveredScopes':len(scope_ex),'pendingPilotNominationsExcludedExplicitly':len(index['deferredActivePilotPairIds']),'elapsedSeconds':elapsed,'allScopeAndPairCoverageVerified':True}
    print(compact(summary),flush=True);return summary,batches
baseline={'name':'held_uniform_rich_draft','packets':len(index['families']),'callsIfEveryPacketProposedAndChallenged':2*len(index['families']),'inputCharacters':stats(baseline_sizes),'scopesPerPacket':stats(baseline_scope_counts),'pairsPerPacket':stats(baseline_pair_counts),'scopeExposures':sum(scope_exposure.values()),'maxRepeatedScopeExposures':max(scope_exposure.values()),'sourceDescriptionExposures':sum(unit_exposure.values()),'uniqueSourceDescriptions':len(units),'primaryWindowExposures':sum(primary_exposure.values()),'uniquePrimaryWindows':len(primary),'exposureCharacters':dict(exposure),'overNominal280kCharacterCeiling':sum(n>280000 for n in baseline_sizes)}
results=[];packets={}
for config in [('rich_direct_20_40','rich',20,40,280000,'gain_per_character'),('triage_20_40','triage',20,40,280000,'gain_per_character'),('triage_star_60_200','triage',60,200,280000,'star'),('triage_cost_60_200','triage',60,200,280000,'gain_per_character'),('triage_cost_40_120','triage',40,120,280000,'gain_per_character'),('triage_refs_star_60_200','triage_refs',60,200,280000,'star'),('triage_refs_cost_60_200','triage_refs',60,200,280000,'gain_per_character'),('triage_refs_star_40_120','triage_refs',40,120,280000,'star')]:
    summary,groups=packing(*config);results.append(summary);packets[config[0]]=groups
report={'schemaVersion':'q025-canonical-review-packing-experiment/1','status':'design_measurement_not_launch_or_scientific_admission','inputs':{'heldIndex':ipin,'registry':rpin,'sourcePackets':packet_pins},'baseline':baseline,'alternatives':results,'edgeInventory':{'nominationIds':len(nomination_to_edge),'uniqueUnorderedComparisons':len(edge_keys),'originalCumulativeNominationCount':index['coverage']['cumulativeNominations'],'heldPilotIds':index['deferredActivePilotPairIds'],'unmatchedAnchorCount':index['coverage']['unmatchedAnchors'],'unmatchedContrastIds':sum(n.startswith('unmatched:') for n in nomination_to_edge)},'comparisonLimits':['All records and explicit workload IDs are covered; no negative or unmatched scope is declared unique.','Normalized rich alternatives preserve the union of primary windows attached to each scope across the draft, which can be stricter than an individual original packet. Their schema is a measurement format, not the active model contract.','Triage uses exact full scope definitions, whole source descriptions, inherited role/reading status and pins, with zero primary text. No claim of primary rereading.','Scope/pair limits are hypotheses for a bounded triage pilot, not validated semantic/model capacities.','No source archive or sealed holdout file was read; only the evaluator registry and already prepared held packets were inspected.'],'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(B/'measurements.json').write_text(json.dumps(report,indent=2)+'\n');(B/'packings.json').write_text(json.dumps({'schemaVersion':'q025-workload-packings/1','registrySha256':rpin['sha256'],'scienceClusters':False,'packets':packets},separators=(',',':'))+'\n')
