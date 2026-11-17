"""Read complete scientific fields; exact repeated values are printed once."""
import json,sys
from pathlib import Path
P=Path('research/q025/evaluation/full-pass/native-local/placement-cut04-review-v1/product-70-scopes.json')
d=json.loads(P.read_text());rows={r['index']:r for r in d['rows']}
def clean(v):
 if isinstance(v,dict):return {k:clean(x)for k,x in v.items()if k not in ['refs','evidenceIds','scopeContentSha256','scopeDecisionId','aliases']}
 if isinstance(v,list):return [clean(x)for x in v]
 return v
for spec in sys.argv[1:]:
 parts=spec.split(':');r=rows[int(parts[0])];candidates=[]if len(parts)==1 else [int(i)for i in parts[1].split(',')if i]
 print('\nCASE',r['index'],r['familyId'],r['localRef']);print('DEFINITION',json.dumps(clean(r['definition']),ensure_ascii=False));print('ASSESSMENT',json.dumps(clean(r['independentAssessment']),ensure_ascii=False))
 for s in r['sources']:
  print('SOURCE',s['unitRef'],s['paperId'],s['description'])
  p=clean(s['proposalJudgment']);c=clean(s['challengeJudgment']);same={k:v for k,v in p.items()if k in c and c[k]==v}
  print('BOTH',json.dumps(same,ensure_ascii=False));print('PROPOSAL DIFFERENCES',json.dumps({k:v for k,v in p.items()if k not in same},ensure_ascii=False));print('CHALLENGE DIFFERENCES',json.dumps({k:v for k,v in c.items()if k not in same},ensure_ascii=False));print('INDEPENDENT',json.dumps(clean(s['independentPriorPlacementReview']),ensure_ascii=False))
  print('OLD PROPOSAL',json.dumps([a['original']for a in s['proposalAttributions']],ensure_ascii=False));print('OLD CHALLENGE',json.dumps([a['original']for a in s['challengeAttributions']],ensure_ascii=False))
 for i in candidates:
  c=r['globalExistingScopeLookup']['candidates'][i];print('CONTRAST',i,c['id'],json.dumps(clean(c['definition']),ensure_ascii=False))
