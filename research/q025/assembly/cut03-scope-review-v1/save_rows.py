import json,sys,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;A=O.parent
j=json.load(open(A/'placement-incremental-v1/cut-03/exception-intake.json'));l=json.load(open(A/'placement-latent-lookup-v1/supplement.json'));lm={(r['familyId'],r['stage'],r['localRef']):r for r in l['rows']}
p=O/'review.json';out=json.load(open(p))if p.exists()else {'schemaVersion':'q025-assigned-scope-review/1','reviewer':'atlas_geometry_experiments','assignedIndices':list(range(49,85))+list(range(86,90)),'sourceIntakeSha256':'e2c8feedca7ab901585b3a3f046fa6900d1fb60eec30b2dd8f668d09a2d15a7b','latentSupplementSha256':'b18b7a078d28a6824440e32ddf8bc7a91d0125eb2b2f260a6c952b66708c94db','readingBasis':'Full unchanged native definitions, complete selected source descriptions, both historical attribution notes and both new placement judgments, plus the exact current/pending contrasts named per row. No fresh primary reading, model call or global uniqueness assertion.','rows':[]}
for a in json.load(sys.stdin):
 n=j['newScopes'][a['index']];pool=n['globalExistingScopeLookup']['candidates']+[{'id':c['destinationId'],'definition':c['definition']}for c in lm[n['familyId'],n['stage'],n['localRef']]['candidates']]
 def resolve(suffix):
  ids={c['id']for c in pool if c['id'].endswith(suffix)}
  if len(ids)!=1:raise ValueError((a['index'],suffix,ids))
  return ids.pop()
 contrasts=[resolve(s)for s in a.pop('contrastSuffixes')];suffix=a.pop('entrySuffix',None);entry=a.pop('entry',None)
 if suffix:entry={'destinationId':resolve(suffix),**entry,'wholeEndpointDefinitionsRead':True}
 row={'index':a.pop('index'),'familyId':n['familyId'],'localRef':n['localRef'],'definitionSha256':n['definitionSha256'],**a,'closestContrastIds':contrasts,'entry':entry}
 assert row['index']in out['assignedIndices'];out['rows']=[r for r in out['rows']if r['index']!=row['index']]+[row]
out['rows'].sort(key=lambda r:r['index']);out['complete']=len(out['rows'])==40;p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(out['rows']),hashlib.sha256(p.read_bytes()).hexdigest())
