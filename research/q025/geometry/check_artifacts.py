#!/usr/bin/env python3
"""Read-only alignment/invariant and source-witness audit. No scientific gold claims."""
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('round',type=Path);p.add_argument('--navigation',type=Path,required=True);p.add_argument('--journeys',type=Path,required=True);a=p.parse_args()
 units=[json.loads(line) for line in (a.round/'source-rows.jsonl').open()];byid={u['unit_id']:u for u in units}
 nav=[]
 for path in sorted(a.navigation.glob('units-*.json')):nav.extend(json.loads(path.read_text()))
 nav=[u for u in nav if u['lens']=='physical_question']
 assert len(units)==len(nav)
 for i,(u,v) in enumerate(zip(units,nav)):
  assert u['unit_id']==v['id'] and u['paper_id']==v['paperId'] and u['sourceRow']==v['vectorRow']==i
  assert u['text_sha256']==v['evidence']['textSha256']==hashlib.sha256(u['text'].encode()).hexdigest()
 results={'sourceRowAlignment':{'checked':len(units),'allPass':True,'rowOrderSha256':hashlib.sha256('\n'.join(u['unit_id'] for u in units).encode()).hexdigest()},'candidates':{}}
 journeys=json.loads(a.journeys.read_text())['cases']
 for folder in sorted(a.round.iterdir()):
  if not (folder/'regions.json').is_file():continue
  regions=json.loads((folder/'regions.json').read_text());rid={r['id']:r for r in regions};sums=defaultdict(float);homes=defaultdict(list);primary={}
  for line in (folder/'memberships.jsonl').open():
   r=json.loads(line);uid=r['unitId'];assert uid in byid and r['regionId'] in rid
   assert byid[uid]['sourceRow']==r['sourceRow']==r['browserVectorRow'];assert 0<r['weight']<=1
   sums[uid]+=r['weight'];homes[uid].append(r)
   if r['primary']:assert uid not in primary;primary[uid]=r['regionId']
  assert set(sums)==set(byid)==set(primary);assert max(abs(v-1) for v in sums.values())<1e-8
  memberships={r['id']:set(r['memberIds']) for r in regions}
  for r in regions:
   assert set(r['representativeUnitIds'])<=memberships[r['id']]<=set(byid)
   for c in r['childIds']:assert memberships[c]<=memberships[r['id']]
  witness=[]
  for case in journeys:
   relevant=[w for w in case['witnesses'] if w['lens']=='physical_question'];details=[]
   for w in relevant:
    uid=w['unitId'];home=rid[primary[uid]] if uid in primary else None
    details.append({'unitId':uid,'paperId':w['paperId'],'present':uid in homes,'primaryRegionId':home['id'] if home else None,'primaryRegionUnits':home['memberCount'] if home else None,'primaryRegionDepth':home['depth'] if home else None,'directHomeCount':len(homes.get(uid,[])),'inRepresentativeSample':uid in home['representativeUnitIds'] if home else False,'memberships':[{'regionId':h['regionId'],'weight':h['weight']} for h in homes.get(uid,[])]})
   witness.append({'journeyId':case['id'],'title':case['title'],'split':case['split'],'questionWitnesses':details,'questionWitnessRecall':sum(x['present'] for x in details)/len(details) if details else None,'methodWitnessCount':sum(w['lens']=='method' for w in case['witnesses']),'note':'Question organization contains question witnesses only; method projection is a numerical context layer. Presence is not semantic or routing validation.'})
  overlap={u for u,h in homes.items() if len(h)>1}
  results['candidates'][folder.name]={'invariantsPass':True,'regionCount':len(regions),'overlapUniqueUnits':len(overlap),'overlapUniquePapers':len({byid[u]['paper_id'] for u in overlap}),'journeys':witness}
 (a.round/'artifact-audit.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({'sourceRowAlignment':results['sourceRowAlignment'],'candidates':{k:{z:v[z] for z in ['invariantsPass','regionCount','overlapUniqueUnits','overlapUniquePapers']} for k,v in results['candidates'].items()}},indent=2))

if __name__=='__main__':main()
