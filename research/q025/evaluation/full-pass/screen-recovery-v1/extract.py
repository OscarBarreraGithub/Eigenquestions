"""Preserve complete screen values and every alternate judgment; no side effects."""
import ast,copy,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def parser():
 p=F/'canonical-recovery-v2/extract_prefix.py';fn=next(x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='parse_attempt');env={'json':json,'hashlib':hashlib};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'),env);return env['parse_attempt']
def extract(text,packet,selected_attempt):
 starts=[m.start()for m in re.finditer(r'\{\s*"version"\s*:\s*"q025-canonical-triage/1"',text)];assert len(starts)==2,'Expected two preserved attempts';parse=parser();attempts=[parse(text,s)for s in starts];selected=copy.deepcopy({**attempts[selected_attempt]['completeFields'],**attempts[selected_attempt]['completeArrayPrefixes']});assert selected['familyId']==packet['familyId']and selected['stage']=='triage';variants=[];identical=[]
 for ai,attempt in enumerate(attempts):
  if ai==selected_attempt:continue
  for field,value in {**attempt['completeFields'],**attempt['completeArrayPrefixes']}.items():
   if field in ['version','familyId','stage']:assert value==selected[field];continue
   rows=enumerate(value)if field in ['scopeReviews','comparisonReviews']else [(None,value)]
   for i,row in rows:
    oldindex=next((j for j,x in enumerate(selected[field])if x['ref']==row['ref']),None)if i is not None else None
    path=[field,oldindex]if oldindex is not None else [field]if i is None and field in selected else None
    previous=selected[field][oldindex]if oldindex is not None else selected.get(field)if i is None else None
    ref=f'attempt{ai}:{field}'+(f':{row["ref"]}'if i is not None else '')
    if previous==row:identical.append({'variantRef':ref,'selectedPath':path,'valueSha256':vh(row)});continue
    variants.append({'variantRef':ref,'selectedPath':path,'alternatePath':[field,i]if i is not None else [field],'alternateValue':copy.deepcopy(row),'alternateValueSha256':vh(row)})
 missing={field:[r['ref']for r in packet[source]if r['ref']not in {x['ref']for x in selected.get(field,[])}]for field,source in [('scopeReviews','scopes'),('comparisonReviews','nominations')]}
 raw=text.encode();tails=[]
 for ai,attempt in enumerate(attempts):
  start=max(row['end']for row in attempt['exactValueRanges']);end=attempts[ai+1]['jsonStartByte']if ai+1<len(attempts)else len(raw);fragment=raw[start:end]
  tails.append({'attempt':ai,'start':start,'end':end,'sha256':hashlib.sha256(fragment).hexdigest(),'text':fragment.decode(),'status':'incomplete_tail_not_an_adopted_judgment'})
 return {'schemaVersion':'q025-screen-retained-components/1','familyId':packet['familyId'],'sourceStreamSha256':hashlib.sha256(raw).hexdigest(),'selectedAttempt':selected_attempt,'selectionBasis':'Choose the coherent attempt with the most complete comparison judgments. Every differing complete alternative remains an explicit review obligation; no field is silently spliced.','offsetUnit':'utf8_bytes','attempts':attempts,'incompleteTails':tails,'selectedFields':selected,'missingRefs':missing,'attemptVariants':variants,'identicalAlternateComponents':identical,'scientificAdmission':False}
def model_components(p):
 out={k:copy.deepcopy(p[k])for k in ['schemaVersion','familyId','selectedAttempt','selectionBasis','selectedFields','missingRefs','attemptVariants','identicalAlternateComponents','incompleteTails']}
 for row in out['attemptVariants']:
  if row['selectedPath']and isinstance(row['alternateValue'],dict):
   selected=out['selectedFields']
   for key in row['selectedPath']:selected=selected[key]
   assert set(selected)==set(row['alternateValue']);row['alternateChanges']={k:v for k,v in row.pop('alternateValue').items()if v!=selected[k]}
  row.pop('alternateValueSha256');row.pop('alternatePath')
 out['alternateEncoding']='alternateChanges replaces only named fields at selectedPath; all other fields are exactly identical. Full alternatives and byte ranges remain in the pinned preserved artifact.'
 return out
