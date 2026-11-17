#!/usr/bin/env python3
"""Reserve unused navigation papers without revealing them to construction workers."""
import json,re,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
UP=Path('/Users/emmy/Developer/physics-atlas-swampland')
WORK=HERE.parents[2]
def papers(x):
 out=set()
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['paper_id','paperId'] and isinstance(v,str):out.add(v)
   else:out.update(papers(v))
 elif isinstance(x,list):
  for y in x:out.update(papers(y))
 return out
excluded=set()
for d in ['reviews','evaluations']:
 for f in (UP/'graph-design/20261105-v1/publication-v1/coarse'/d).rglob('*.json'):excluded|=papers(json.loads(f.read_text()))
for fn in ['journeys.json','ordinary-exploration.json','current-relation-ledger.json']:excluded|=papers(json.loads((HERE/fn).read_text()))
rows=[json.loads(l) for l in (WORK/'research/q025/geometry/round1/source-rows.jsonl').open()]
strata=[('effective_actions',r'compactif.*(effective action|effective theor)|effective.*compactif'),('vacua_stabilization',r'(stabili[sz]|metastab|vacuum|vacua).*(modul|flux)|modul.*stabili'),('distance_emergence',r'(infinite.distance|emergen.*string|distance conjecture|decompactif)'),('symmetry_anomalies',r'(generalized symmetr|higher.form|non.invertible|global anomal|discrete.*gauge.*anomal)'),('inflation_reheating',r'(inflation|reheating)'),('axion_dynamics',r'axion.*(mass|kinetic|mixing|potential|align)'),('scattering_constraints',r'(positivity|dispersion relation|scattering.*amplitude)'),('neutrino_dark_sector',r'(neutrino|dark.matter)')]
chosen=[];used=set(excluded)
for name,pattern in strata:
 candidates=[r for r in rows if r['view']=='physical_question' and r['paper_id'] not in used and re.search(pattern,r['text'],re.I)]
 candidates.sort(key=lambda r:hashlib.sha256(('q025-final-navigation-reservation-v1:'+r['unit_id']).encode()).hexdigest())
 n=0
 for r in candidates:
  if r['paper_id'] in used:continue
  chosen.append(dict(stratum=name,unitId=r['unit_id'],paperId=r['paper_id'],sourceRow=r['sourceRow'],question=r['text'],nodeIds=r['node_ids'],sourceRecordIds=r['source_record_ids'],selectionStatus='reserved_unread_for_post_selection_source_reading; no scientific gold label'))
  used.add(r['paper_id']);n+=1
  if n==3:break
 assert n==3,name
out=dict(schemaVersion='q025-holdout-reservation/1',exclusionPolicy='Exclude all papers appearing in published 45-topic review/fresh-check JSON, visible development probes, and current 128 scientific relation/dossier receipts. This is navigation-use separation, not absence of prior corpus extraction.',excludedPapers=len(excluded),selection='Three distinct paper witnesses per declared stratum by SHA256 ordering of q025-final-navigation-reservation-v1 plus unit ID. Prior assignments are not labels. Read after candidate freeze; retain unsuitable/ambiguous cases explicitly.',records=chosen)
p=HERE/'final-holdout-reservation.local.json';p.write_text(json.dumps(out,indent=2)+'\n')
(HERE/'holdout-commitment.json').write_text(json.dumps(dict(schemaVersion='q025-holdout-commitment/1',reservationSha256=hashlib.sha256(p.read_bytes()).hexdigest(),paperCount=len(chosen),strata=[n for n,_ in strata],excludedPapers=len(excluded),status='reserved; no final prompts or results yet; do not inspect reservation until candidate selection frozen'),indent=2)+'\n')
print('reserved',len(chosen),'papers across',len(strata),'strata; excluded',len(excluded),'previously exposed papers')
