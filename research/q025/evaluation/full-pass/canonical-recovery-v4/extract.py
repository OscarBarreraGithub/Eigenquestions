"""Read both canonical attempts; execute only the frozen pure parser function."""
import ast,copy,hashlib,json,re
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def parser():
 p=F/'canonical-recovery-v2/extract_prefix.py';tree=ast.parse(p.read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='parse_attempt');env={'json':json,'hashlib':hashlib};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(p),'exec'),env);return env['parse_attempt']
def key(field,row):
 if field in ['newQuestions','decisions']:return row['id']
 if field=='pairConstraints':return tuple(sorted([row['left'],row['right']]))
 if field in ['scopeDispositions','priorReviews']:return row['ref']
 if field=='sourceContributions':return (row['unitRef'],row['questionRef'],row['role'])
 if field=='compoundSources':return row['unitRef']
 return None
def extract(text):
 starts=[m.start()for m in re.finditer(r'\{\s*"version"\s*:\s*"q025-canonical-review/1"',text)];assert len(starts)==2,'Expected exact two retained attempts';parse=parser();attempts=[parse(text,s)for s in starts];first,second=attempts;variants=[];identical=[]
 selected=first['completeFields'];alternate={**second['completeFields'],**second['completeArrayPrefixes']}
 for field,value in alternate.items():
  if field in ['version','familyId','stage']:assert value==selected[field];continue
  if isinstance(value,list):
   before=selected.get(field,first['completeArrayPrefixes'].get(field,[]));lookup={key(field,row):i for i,row in enumerate(before)}
   for i,row in enumerate(value):
    oldindex=lookup.get(key(field,row));path=[field,oldindex] if oldindex is not None else None
    if path is not None and before[oldindex]==row:identical.append({'alternatePath':[field,i],'selectedPath':path,'valueSha256':vh(row)});continue
    variants.append({'variantRef':f'attempt1:{field}:{i}','selectedPath':path,'alternatePath':[field,i],'alternateValue':copy.deepcopy(row),'alternateValueSha256':vh(row)})
  elif value!=selected.get(field):variants.append({'variantRef':f'attempt1:{field}','selectedPath':[field] if field in selected else None,'alternatePath':[field],'alternateValue':copy.deepcopy(value),'alternateValueSha256':vh(value)})
  else:identical.append({'alternatePath':[field],'selectedPath':[field],'valueSha256':vh(value)})
 assert len(first['completeFields']['priorReviews'])==46 and len(second['completeArrayPrefixes']['priorReviews'])==32
 return {'schemaVersion':'q025-canonical-challenge-components/1','selectedAttempt':0,'selectionBasis':'First coherent attempt has all scientific collections and all 46 prior assessments. Second-attempt complete differences remain explicit adjudication obligations; no occurrence order implies scientific acceptance.','offsetUnit':'utf8_bytes','attempts':attempts,'completeFields':copy.deepcopy(first['completeFields']),'completeArrayPrefixes':copy.deepcopy(first['completeArrayPrefixes']),'attemptVariants':variants,'identicalAlternateComponents':identical,'sourceStreamValueSha256':hashlib.sha256(text.encode()).hexdigest()}
def model_components(p):
 out={k:copy.deepcopy(p[k])for k in ['schemaVersion','selectedAttempt','selectionBasis','completeFields','completeArrayPrefixes','attemptVariants','identicalAlternateComponents']}
 for row in out['attemptVariants']:
  path=row['selectedPath'];alternate=row['alternateValue']
  if path is not None and isinstance(alternate,dict):
   selected=out['completeFields']
   for key in path:selected=selected[key]
   assert set(selected)==set(alternate),'Changed record shape needs a full alternative'
   row['alternateChanges']={k:v for k,v in alternate.items()if v!=selected[k]};row.pop('alternateValue')
 out['alternateEncoding']='For alternateChanges, replace only those named top-level fields of selectedPath; every unlisted field is exactly identical. This reconstructs the full alternative without repetition. Scalar alternatives retain alternateValue. Full original values/ranges remain in the pinned artifact.'
 return out
