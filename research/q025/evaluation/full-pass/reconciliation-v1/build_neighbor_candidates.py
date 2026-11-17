"""Nominate scope comparisons from exact existing affinities; never infer equivalence."""
import gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;E=F.parent;W=E.parents[2];G=W/'research/q025/geometry/identity-neighbors';L=F/'native-local/reconciliation-v1';L.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
m=json.loads((G/'manifest.json').read_text());assert sha(G/'units.json')==m['unitTable']['sha256'];rows=json.loads((G/'units.json').read_text())['rows'];assert len(rows)==8473;sealed={r['paperId'] for r in json.loads((E/'final-holdout-reservation.local.json').read_text())['records']};eligible={r['sourceRow'] for r in rows if r['paperId'] not in sealed};byrow={r['sourceRow']:r for r in rows};members=json.loads((F/'coverage-memberships.local.json').read_text());plan=json.loads((F/'coverage-plan.json').read_text());leafkeys={r['reviewKey'] for r in plan['regions'] if r['kind']=='leaf'};home={uid:key for key,record in members.items() if key in leafkeys for uid in record['candidateMemberIds']};maps={}
for model,meta in m['exports'].items():
 assert sha(G/meta['path'])==meta['sha256'];data=json.loads(gzip.decompress((G/meta['path']).read_bytes()));assert data['unitIdOrderSha256']==m['unitIdOrderSha256'];maps[model]={r['sourceRow']:{n[0]:(rank+1,n[1]) for rank,n in enumerate(r['neighbors']) if n[0] in eligible} for r in data['rows'] if r['sourceRow'] in eligible}
pairs={}
for model,graph in maps.items():
 for i,neighbors in graph.items():
  for j,(rank,weight) in neighbors.items():
   if i==j:continue
   a,b=sorted([i,j]);key=(a,b);entry=pairs.setdefault(key,{'a':a,'b':b,'models':{}});entry['models'][model]={'aRank':graph.get(a,{}).get(b,(None,None))[0],'bRank':graph.get(b,{}).get(a,(None,None))[0],'affinityWeight':weight}
candidates=[]
for (a,b),entry in pairs.items():
 if len(entry['models'])<2:continue
 u,v=byrow[a],byrow[b];score=sum(1/r for x in entry['models'].values() for r in [x['aRank'],x['bRank']] if r);mutual=all(x['aRank'] is not None and x['bRank'] is not None for x in entry['models'].values());candidates.append({'caseId':f'affinity-scope-{a}-{b}','unitIds':[u['unitId'],v['unitId']],'sourceRows':[a,b],'paperIds':[u['paperId'],v['paperId']],'originalRegionKeys':[home[u['unitId']],home[v['unitId']]],'acrossOriginalLeaves':home[u['unitId']]!=home[v['unitId']],'samePaper':u['paperId']==v['paperId'],'bothModelsMutual':mutual,'rankNominationScore':score,'existingAffinity':entry['models'],'status':'unreviewed_nomination_not_equivalence'})
candidates.sort(key=lambda x:(-int(x['bothModelsMutual']),-x['rankNominationScore'],x['sourceRows']));dump(L/'all-neighbor-candidates.json',candidates)
selected=[];paper_counts={};unit_counts={};stratum_counts={'cross_leaf':0,'within_leaf':0}
for c in candidates:
 stratum='cross_leaf' if c['acrossOriginalLeaves'] else 'within_leaf';limit=128 if stratum=='cross_leaf' else 64
 if stratum_counts[stratum]>=limit or any(paper_counts.get(p,0)>=2 for p in set(c['paperIds'])) or any(unit_counts.get(u,0)>=1 for u in c['unitIds']):continue
 selected.append(c);stratum_counts[stratum]+=1
 for p in set(c['paperIds']):paper_counts[p]=paper_counts.get(p,0)+1
 for u in c['unitIds']:unit_counts[u]=unit_counts.get(u,0)+1
 if len(selected)==192:break
dump(B/'neighbor-intake.json',{'schemaVersion':'q025-scope-neighbor-intake/1','status':'candidate_intake_not_review_packet','cases':selected,'selectionMeaning':'Paper-diverse nominations; original leaves are provenance only, not scientific classes. Cases require target/regime/source reading before type or truth labels.','heldoutSourcesExposed':0});report={'schemaVersion':'q025-scope-neighbor-nomination/1','graphExportManifestSha256':sha(G/'manifest.json'),'sourceUnitOrderSha256':m['unitIdOrderSha256'],'heldoutReservationSha256':sha(E/'final-holdout-reservation.local.json'),'eligibleUnits':len(eligible),'withheldUnits':8473-len(eligible),'bothModelCandidatePairs':len(candidates),'mutualBothModelPairs':sum(c['bothModelsMutual'] for c in candidates),'crossOriginalLeafPairs':sum(c['acrossOriginalLeaves'] for c in candidates),'intakeCases':len(selected),'intakeStrata':stratum_counts,'intakeSha256':sha(B/'neighbor-intake.json'),'allCandidatesSha256':sha(L/'all-neighbor-candidates.json'),'newEmbeddingsOrModelCalls':0,'interpretation':'Affinity weights are existing retrieval values, not cosine scores, scientific relations, equivalence judgments or gold labels.'};dump(B/'neighbor-report.json',report);print(json.dumps(report,indent=2))
