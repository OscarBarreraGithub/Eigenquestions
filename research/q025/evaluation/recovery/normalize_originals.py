#!/usr/bin/env python3
"""Derive typed references from complete failed originals; preserve every original byte/status."""
import copy,hashlib,json,re,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=B.parent;O=E/'next-wave/native-local/jobs';L=B/'native-local/derived'
sys.path.insert(0,str(E/'next-wave'));from validate_contract import structural,SCHEMA,validate
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def normalize(jid):
 d=O/jid;packet=json.loads((d/'packet.json').read_text());raw=json.loads((d/'reply.raw.txt').read_text());reply=copy.deepcopy(raw);receipt=json.loads((d/'receipt.json').read_text());assert sha(d/'reply.raw.txt')==receipt['replySha256'];structural(raw,SCHEMA)
 units={u['unitIndex']:u for u in packet['units']};assert all(packet['units'][i]['unitIndex']==i for i in units);ev={e['id']:e for e in packet['evidence']};edges={e['id']:e for e in packet['sourceRelations']};existing=set(packet['existingQuestionRefs']);changes=[];errors=[];registry={}
 for i,u in units.items():registry[f'd{i}']={'kind':'description','unitIndex':i,'unitId':u['unitId'],'textSha256':hashlib.sha256(u['description'].encode()).hexdigest(),'spanOrigin':'unit.description','length':len(u['description'])}
 for eid,e in ev.items():registry[eid]={'kind':'source_anchor','sourceId':eid,'paperId':e['paper_id'],'sourceSha256':e['source_sha256'],'sourceContext':{k:v for k,v in e['sourceContext'].items() if k!='text'},'spanOrigin':'sourceContext.text','length':len(e['sourceContext']['text'])}
 for eid,e in edges.items():registry[eid]={'kind':'source_relation','sourceId':eid,'source':e['source'],'target':e['target'],'semanticStatus':e['semanticStatus'],'directUnitIndices':e['directUnitIndices'],'spanOrigin':'sourceRelation.statement','length':len(e['statement'])}
 for qid in existing:registry[qid]={'kind':'existing_question','sourceId':qid,'origin':'provided_existing_candidate'}
 def desc(rawid):
  for pattern in [r'/units/(\d+)/description',r'unitIndex:(\d+)',r'^(\d+)$']:
   m=re.fullmatch(pattern,rawid)
   if m:
    i=int(m.group(1))
    if i not in units:raise ValueError('description index outside exact packet')
    return f'd{i}'
  return None
 def canon(s,path):
  did=desc(s)
  if did:
   if s!=did:changes.append({'path':path,'operation':'resolve_description_identifier','from':s,'to':did,'provenance':'Exact packet array index equals immutable unitIndex; description text hash retained.'})
   return did
  if s not in registry:errors.append({'path':path,'problem':'invented_or_unbound_reference','value':s})
  return s
 def walk(x,path='$'):
  if isinstance(x,dict):
   if x.get('kind') in ['description','source_anchor','source_relation','existing_question'] and 'id' in x:
    before=copy.deepcopy(x);x['id']=canon(x['id'],path+'.id');ref=registry.get(x['id'])
    if ref and ref['kind']!=x['kind']:errors.append({'path':path,'problem':'reference_kind_mismatch'})
    a,z=x.get('start'),x.get('end')
    if (a is None)!=(z is None):errors.append({'path':path,'problem':'partial_range'})
    elif a is None and ref and x['kind']=='description':
     x['start']=0;x['end']=ref['length'];changes.append({'path':path,'operation':'whole_description','from':before,'to':copy.deepcopy(x),'provenance':'Whole exact description, not a newly selected literal subspan.'})
    elif a is not None and ref:
     length=ref.get('length',0)
     if x['kind']=='source_anchor':
      context=ev[x['id']]['sourceContext'];local=0<=a<z<=length;page=context['start']<=a<z<=context['end']
      if a==context['start'] and z==context['end']:
       x['start']=0;x['end']=length;changes.append({'path':path,'operation':'page_context_to_local_whole_context','from':before,'to':copy.deepcopy(x),'sourcePage':context['pdfPage'],'provenance':'Exact supplied sourceContext start/end pair; coordinate conversion changes no selected text.'})
      elif local and page and context['start']!=0:errors.append({'path':path,'problem':'ambiguous_coordinate_origin','value':before})
      elif page and not local:
       x['start']=a-context['start'];x['end']=z-context['start'];changes.append({'path':path,'operation':'unambiguous_page_to_context_range','from':before,'to':copy.deepcopy(x)})
      elif not local:errors.append({'path':path,'problem':'invalid_range','value':before})
     elif not(0<=a<z<=length):errors.append({'path':path,'problem':'invalid_range','value':before})
   for k,v in list(x.items()):
    if k=='evidenceIds' and isinstance(v,list):x[k]=[canon(s,path+'.evidenceIds') for s in v]
    else:walk(v,path+'.'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):walk(v,f'{path}[{i}]')
 walk(reply)
 # A diagnostic compatibility projection is only for checking old validator invariants.
 # Normalized scientific artifact retains ALL typed refs; no nonprimary refs are deleted.
 projection=copy.deepcopy(reply);projection_changes=[]
 def project(x,path='$'):
  if isinstance(x,dict):
   if x.get('kind')=='description' and re.fullmatch(r'd\d+',x.get('id','')):x['id']=x['id'][1:]
   for k,v in list(x.items()):
    if k=='evidenceIds':
     secondary=[s for s in v if s not in ev]
     if secondary:projection_changes.append({'path':path+'.evidenceIds','secondaryTypedReferencesRetainedInNormalizedArtifact':secondary})
     x[k]=[s for s in v if s in ev]
    else:project(v,path+'.'+k)
  elif isinstance(x,list):
   for i,v in enumerate(x):project(v,f'{path}[{i}]')
 project(projection);vp=copy.deepcopy(packet);origins=[]
 for a in reply['priorCardAssessments']:
  q=a['priorQuestionRef'];origin='previous_stage' if q in packet.get('priorQuestionRefs',[]) else 'provided_existing_candidate' if q in existing else 'unbound'
  origins.append({'questionRef':q,'origin':origin})
  if origin=='unbound':errors.append({'problem':'unbound_prior_card','questionRef':q})
 if packet['stage']=='proposal':vp['priorQuestionRefs']=[a['priorQuestionRef'] for a in reply['priorCardAssessments'] if a['priorQuestionRef'] in existing]
 validation=None
 try:validation=validate(vp,projection)
 except Exception as e:errors.append({'problem':'remaining_contract_or_substantive_failure','detail':str(e)})
 out={'schemaVersion':'q025-derived-scientific-review/1','status':'normalized_references_other_constraints_pass' if not errors else 'normalized_with_unresolved_failures','jobId':jid,'originalStatus':receipt['status'],'originalError':receipt['error'],'originalRawSha256':sha(d/'reply.raw.txt'),'originalReceiptSha256':sha(d/'receipt.json'),'originalPacketSha256':sha(d/'packet.json'),'frozenOriginalValidatorSha256':sha(E/'next-wave/validate_contract.py'),'normalizerSha256':sha(Path(__file__)),'normalizedReview':reply,'referenceRegistry':registry,'referenceTransforms':changes,'existingVsPreviousCardOrigins':origins,'compatibilityProjectionPurpose':'Check old non-reference invariants only; typed nonprimary references remain in normalizedReview and registry. No old receipt/status changed.','compatibilityProjectionReferenceLog':projection_changes,'compatibilityValidation':validation,'unresolvedFailures':errors,'scientificAdmission':'Not independently accepted. This derivation changes citation representation only; source science and new question scopes still need independent challenge.'}
 target=L/jid
 if (target/'derived.json').exists():assert json.loads((target/'derived.json').read_text())==out,'Refusing divergent overwrite of existing derivation'
 else:write(target/'derived.json',out)
 summary={k:out[k] for k in ['jobId','status','originalStatus','originalError','originalRawSha256','originalReceiptSha256','originalPacketSha256','normalizerSha256','compatibilityValidation','unresolvedFailures','scientificAdmission']};summary.update(derivedSha256=sha(target/'derived.json'),transformationCount=len(changes),referenceKindCounts=dict(__import__('collections').Counter(v['kind'] for v in registry.values())),unitCount=len(reply['unitAssessments']),questionCardCount=len(reply['questionCards']),originalRegionVerdict=reply['verdict'],summary=reply['summary'],existingVsPreviousCardOrigins=origins)
 return summary
if __name__=='__main__':
 results=[normalize(j) for j in ['kk-production-decay-proposal','effective-actions-vacua-proposal','gauge-geometry-anomaly-proposal']];write(B/'normalization-report.json',{'schemaVersion':'q025-normalization-audit/1','records':results});print(json.dumps(results,indent=2,ensure_ascii=False))
