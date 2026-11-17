#!/usr/bin/env python3
import json,collections,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;WORK=HERE.parents[2]
def main():
 cases=json.loads((HERE/'ordinary-exploration.json').read_text())['cases'];us=[u for f in (WORK/'data/navigation').glob('units-*.json') for u in json.loads(f.read_text())];q={u['id']:u for u in us if u['lens']=='physical_question'};byp=collections.defaultdict(list)
 for uid,u in q.items():byp[u['paperId']].append(uid)
 names=[('round1','inherited_ncut'),('round1','diffusion_065'),('round1','diffusion_085'),('round1','multiview'),('round2','local_spectral_minilm'),('round2','local_spectral_consensus'),('round2','local_spectral_qwen'),('round3','multiview_preserve_candidates'),('round3','extra_facet_context'),('round3','inherited_global_qwen')];results=[]
 for round_,name in names:
  path=WORK/'research/q025/geometry'/round_/name/'regions.json'
  if not path.exists():continue
  regions=json.loads(path.read_text());leaves=[r for r in regions if not r['childIds']];homes=collections.defaultdict(list)
  for r in leaves:
   for uid in r['memberIds']:homes[uid].append((r['id'],len(r['memberIds'])))
  out=[]
  for c in cases:
   records=[]
   for s in c['samples']:
    exact=s['unitId'] in q;uids=[s['unitId']] if exact else byp.get(s['paperId'],[])
    eligible=[(uid,home,size) for uid in uids for home,size in homes.get(uid,[])]
    records.append(dict(unitId=s['unitId'],paperId=s['paperId'],sampleRole=s['role'],lookup='exact_question_unit' if exact else 'same_paper_question_proxy_only',candidateQuestionIds=uids,tightestHomeSize=min((a[2] for a in eligible),default=None),homes=eligible))
   sizes=[r['tightestHomeSize'] for r in records if r['tightestHomeSize'] is not None]
   out.append(dict(caseId=c['id'],title=c['reviewedTitle'],found=len(sizes),total=len(records),medianTightestHomeSize=statistics.median(sizes) if sizes else None,maxTightestHomeSize=max(sizes) if sizes else None,records=records))
  results.append(dict(candidate=name,round=round_,leafCount=len(leaves),cases=out))
 result=dict(schemaVersion='q025-ordinary-geometry-comparison/1',meaning='Coverage and reading burden only. Smaller homes do not prove semantic coherence; old region membership is not gold. Method samples use explicitly marked same-paper question proxies when exact Q units are absent.',candidates=results)
 (HERE/'ordinary-geometry-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
 for r in results:print(r['candidate'],'leaves',r['leafCount'],'cases',[(c['caseId'],c['found'],c['medianTightestHomeSize'],c['maxTightestHomeSize']) for c in r['cases']])
if __name__=='__main__':main()
