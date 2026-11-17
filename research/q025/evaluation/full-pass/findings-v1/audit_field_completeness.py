"""Screen every raw response string; flags are evidence for inspection, not repairs."""
import collections,datetime,hashlib,json,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
sys.path.insert(0,str(F.parent/'recovery'))
from compact_contract import SCHEMA

def strings(value,schema,path='$',owner=None):
 if isinstance(value,dict):
  for k,v in value.items():yield from strings(v,schema.get('properties',{}).get(k,{}),path+'.'+k,value)
 elif isinstance(value,list):
  for i,v in enumerate(value):yield from strings(v,schema.get('items',{}),f'{path}[{i}]',owner)
 elif isinstance(value,str):yield path,value,schema,owner

def screen(reply):
 rows=list(strings(reply,SCHEMA));groups=collections.defaultdict(list)
 for path,value,schema,owner in rows:
  if path.endswith('.note') and len(value)>80:groups[re.sub(r'\[\d+\]','[*]',path)].append((path,value))
 clustered=set()
 for group in groups.values():
  incomplete=[(p,v) for p,v in group if not re.search(r'[.!?\]\)]\s*$',v)]
  if len(incomplete)>=4:
   bins=collections.Counter(len(v)//5 for _,v in incomplete)
   for bucket,count in bins.items():
    if count>=4:clustered.update(p for p,v in incomplete if len(v)//5==bucket)
 flags=[]
 for path,value,schema,owner in rows:
  cap=schema.get('maxLength');reasons=[]
  if cap is not None and len(value)==cap:reasons.append('exact_schema_max_length')
  prose=any(path.endswith('.'+k) for k in ['note','qualification','summary','readingLimit','reason','question'])
  if prose and len(value)>50:
   if re.search(r'\b(?:and|or|but|the|a|an|of|to|with|under|than|that|where|which|from|must|also|as|for|into|by|without)\s*$',value,re.I):reasons.append('terminal_function_word')
   if value.endswith((' ','-','–','—')):reasons.append('trailing_space_or_hyphen')
  if path in clustered:reasons.append('clustered_short_unpunctuated_notes')
  if not reasons:continue
  impact='admission_justification' if '.cardReviews[' in path or '.groupReviews[' in path else ('factor_qualification' if '.factors[' in path else ('scope_definition' if path.startswith(('$.cards[','$.region.')) else 'other_review_annotation'))
  record={'path':path,'length':len(value),'schemaMaxLength':cap,'atSchemaCap':cap is not None and len(value)==cap,'reasons':reasons,'suffix':value[-100:],'impact':impact,'status':'screening_flag_requires_inspection_not_proof_of_truncation'}
  if owner and 'refs' in owner:record['refs']=owner['refs']
  if '.factors[' in path:record.update(factorId=owner['id'],kind=owner['kind'])
  elif owner and 'id' in owner:record['cardId']=owner['id']
  flags.append(record)
 return flags,len(rows)

def audit(root):
 records=[];counts=collections.Counter();files=[]
 for d in sorted(Path(root).iterdir()):
  if not (d/'receipt.json').exists() or not (d/'reply.raw.txt').exists():continue
  raw=(d/'reply.raw.txt').read_bytes()
  try:reply=json.loads(raw)
  except json.JSONDecodeError:continue
  receipt=json.loads((d/'receipt.json').read_text());fields,n=screen(reply);counts['nativeReplies']+=1;counts['allStringFieldsScanned']+=n
  rawhash=hashlib.sha256(raw).hexdigest();receipt_hash=hashlib.sha256((d/'receipt.json').read_bytes()).hexdigest();files.append({'jobId':d.name,'rawSha256':rawhash,'receiptSha256':receipt_hash})
  for flag in fields:
   counts['flaggedFields']+=1;counts['fieldsAtCap']+=flag['atSchemaCap'];counts['factorQualificationsAtCap']+=flag['impact']=='factor_qualification' and flag['atSchemaCap'];counts[flag['impact']+'Flags']+=1
  if fields:records.append({'jobId':d.name,'rawSha256':rawhash,'receiptSha256':receipt_hash,'origin':'imported_native_output' if receipt.get('nativeTurnStartedHere') is False else 'native_output','fields':fields})
 return {'schemaVersion':'q025-native-field-completeness-audit/2','observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':dict(counts),'inspectedInputs':files,'findings':records,'interpretation':'All raw string fields are traversed against the frozen schema. Exact maxLength, syntactically suspicious endings and clusters of short unpunctuated notes are separate screening reasons, not automatic scientific failures. The423440c0413bb3814c19 challenge cardReview notes already end at155–157 characters in native output although their schema permits420; this is distinct from240-character factor qualifications. No compiler repair or clipping is inferred. Exact native emitting cause remains unresolved.','admissionPolicy':'Scope definition, admission justification, factor premise and unit annotation are separate. Do not treat a severed justification as complete or an incomplete factor as an admitted premise. An intact independently supported scope/source contribution is not automatically rejected because a separate annotation is incomplete. Targeted source repair only where the missing clause affects a conclusion; preserve original bytes and never guess missing words.'}

if __name__=='__main__':
 report=audit(F/'native-local/full-leaf-wave-v3/jobs');(B/'field-completeness-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['counts']))
