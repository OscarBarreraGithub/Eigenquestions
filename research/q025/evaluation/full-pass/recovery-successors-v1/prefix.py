"""Exact complete values from interrupted JSON; no completion or source inference."""
import hashlib,json,re
DEC=json.JSONDecoder()
def value_hash(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def extract(text):
 starts=[m.start() for m in re.finditer(r'\{\s*"version"\s*:\s*"q025-compact-review/1"',text)];assert starts,'No compact review attempt'
 def node(i,path):
  while i<len(text) and text[i].isspace():i+=1
  begin=i
  try:
   value,end=DEC.raw_decode(text,i)
   return {'value':value,'complete':True,'end':end,'locks':[{'path':path,'value':value,'start':len(text[:begin].encode()),'end':len(text[:end].encode()),'sha256':hashlib.sha256(text[begin:end].encode()).hexdigest()}]}
  except json.JSONDecodeError:pass
  if i>=len(text) or text[i] not in '[{':return {'complete':False,'end':i,'locks':[]}
  kind=text[i];i+=1;out={} if kind=='{' else [];locks=[];children={}
  while i<len(text):
   while i<len(text) and (text[i].isspace() or text[i]==','):i+=1
   if i>=len(text):break
   try:
    if kind=='{':
     key,end=DEC.raw_decode(text,i);assert isinstance(key,str);i=end
     while text[i].isspace():i+=1
     assert text[i]==':';i+=1
    else:key=len(out)
   except (json.JSONDecodeError,IndexError,AssertionError):break
   child=node(i,path+[key]);children[str(key)]=child;locks+=child['locks']
   if 'value' in child:
    if kind=='{':out[key]=child['value']
    else:out.append(child['value'])
   i=child['end']
   if not child['complete']:break
  return {'value':out,'complete':False,'end':i,'locks':locks,'children':children}
 attempts=[]
 for start in starts:
  parsed=node(start,[]);children=parsed.get('children',{})
  if parsed['complete']:complete=parsed['value'];partial={};arrays={}
  else:
   complete={k:v['value'] for k,v in children.items() if v['complete']};partial={k:v for k,v in children.items() if not v['complete']};arrays={k:[v2['value'] for v2 in v.get('children',{}).values() if v2['complete']] for k,v in partial.items() if isinstance(v.get('value'),list)}
  attempts.append({'jsonStartByte':len(text[:start].encode()),'completeFields':complete,'completeArrayPrefixes':arrays,'lockedValues':parsed['locks'],'partialTopFields':list(partial),'attemptComplete':parsed['complete']})
 selected=attempts[-1];variants=[]
 # Earlier complete scientific components remain explicit candidates; the new
 # reviewer must compare them even where the latest attempt has not reached them.
 for ai,a in enumerate(attempts[:-1]):
  for lock in a['lockedValues']:
   if not lock['path'] or lock['path'][0] in ['version','familyId','stage']:continue
   path=lock['path'];same=next((x for x in selected['lockedValues'] if x['path']==path and value_hash(x['value'])==value_hash(lock['value'])),None)
   if not same:variants.append({'variantRef':f'attempt{ai}:'+json.dumps(path,separators=(',',':')),'path':path,'value':lock['value'],'valueSha256':value_hash(lock['value']),'sourceRange':{k:lock[k] for k in ['start','end','sha256']},'status':'earlier_complete_component_requires_conflict_review'})
 return {'schemaVersion':'q025-successor-complete-components/1','offsetUnit':'utf8_bytes','selectedAttempt':len(attempts)-1,**selected,'earlierAttempts':attempts[:-1],'streamVariants':variants,'selectionBasis':'Latest coherent top-level attempt; complete earlier differences remain explicit review obligations. No missing scientific values have been generated.'}

def at(value,path):
 for key in path:value=value[key]
 return value

def assemble(prefix,remaining):
 out=json.loads(json.dumps(prefix['completeFields']))
 for field,value in remaining.items():
  assert field not in out,'Completion overwrites a complete field'
  out[field]=json.loads(json.dumps(prefix['completeArrayPrefixes'].get(field,[])))+value if field in prefix['completeArrayPrefixes'] else value
 for lock in prefix['lockedValues']:assert at(out,lock['path'])==lock['value'],'Completion changed preserved component '+str(lock['path'])
 return out
