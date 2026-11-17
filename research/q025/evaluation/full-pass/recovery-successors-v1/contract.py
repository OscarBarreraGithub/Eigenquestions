"""Narrow derived-context and interrupted-prefix recovery; frozen validators unchanged."""
import copy,importlib.util,json,sys
from pathlib import Path
from prefix import assemble,value_hash
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('q025_successor_base',B.parent/'parents-wave-v1/contract.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from compact_contract import SCHEMA,structure,ob,ar,en,S,A
VARIANT=ob(variantRef=S,decision=en('consistent_revision','material_conflict','unresolved'),reason=S,refs=A)

def completion_schema(prefix):
 fields={k:copy.deepcopy(v) for k,v in SCHEMA['properties'].items() if k not in prefix['completeFields']}
 for k,preserved in prefix['completeArrayPrefixes'].items():
  if 'maxItems' in fields[k]:fields[k]['maxItems']-=len(preserved)
 return ob(version={'type':'string','const':'q025-successor-completion/1'},familyId=S,stage={'type':'string','const':'proposal'},remaining=ob(**fields),variantAssessments=ar(VARIANT))

def regular_schema(variants=False):
 schema=copy.deepcopy(SCHEMA)
 if variants:schema['properties']['streamVariantReviews']=ar(VARIANT);schema['required'].append('streamVariantReviews')
 return schema

def check_variants(packet,rows):
 expected={v['variantRef'] for v in packet.get('streamVariants',[])}
 assert len(rows)==len(expected) and {r['variantRef'] for r in rows}==expected,'Missing/duplicate earlier-attempt review'
 for row in rows:assert row['reason'] and row['refs'] and set(row['refs'])<=set(packet['refRegistry']),'Missing/invented variant evidence'

def prior_annotation_context(packet,reply):
 """Register only the exact supplied pf28 cited once by this known failed review."""
 out=copy.deepcopy(packet);assert packet['familyId']=='8d2b5fd7cc13cefc77fe' and packet['stage']=='challenge'
 def loci(value,path='$'):
  found=[]
  if isinstance(value,dict):
   for key,item in value.items():
    if key=='refs' and isinstance(item,list) and 'pf28' in item:found.append(path+'.refs')
    found+=loci(item,path+'.'+key)
  elif isinstance(value,list):
   for i,item in enumerate(value):found+=loci(item,path+f'[{i}]')
  return found
 assert loci(reply)==['$.cardReviews[5].refs'],'Prior annotation registration is limited to the exact failed locus'
 row=reply['cardReviews'][5];assert row['id']=='p0' and row['refs']==['e0','e6','e9','pf28'],'Unexpected failed-review locus'
 assert 'pf28' not in out['refRegistry'];factor=next(f for f in packet['priorFactors'] if f['id']=='pf28');assert factor['status']=='historical_or_rejected' and set(factor['refs'])<=set(packet['refRegistry'])
 reference={'kind':'prior_annotation_context','reference':'pf28','definition':copy.deepcopy(factor),'definitionSha256':value_hash(factor),'sourcePrimaryRefs':list(factor['refs']),'primaryReadingClaim':False,'scientificImplicationInferred':False,'originalReplyLocus':'$.cardReviews[5].refs','originalReferences':list(row['refs']),'interpretation':'Exact supplied prior factor annotation; historical/rejected status retained. This is not a new primary-source reading.'}
 out['refRegistry']['pf28']=reference;out['priorAnnotationContext']=[reference]
 return out,reference

def evaluate(packet,reply):
 original=copy.deepcopy(reply);prefix=packet.get('preservedComponents');reviews=[]
 if prefix:
  structure(reply,completion_schema(prefix));assert reply['familyId']==packet['familyId'];check_variants(packet,reply['variantAssessments']);reviews=reply['variantAssessments'];reply=assemble(prefix,reply['remaining'])
 elif packet.get('streamVariants'):
  structure(reply,regular_schema(True));reviews=reply['streamVariantReviews'];check_variants(packet,reviews);reply=copy.deepcopy(reply);reply.pop('streamVariantReviews')
 out=base.evaluate(packet,reply)
 if prefix or reviews:
  out.update(status='valid_derived_representation',originalReplyValueSha256=value_hash(original),compositeReviewValueSha256=value_hash(reply),originalCompleteFieldsChanged=False,discardedCompleteScientificComponents=0,streamVariantAssessments=reviews,prefixArtifactSha256=packet.get('prefixArtifactSha256'),recoveryPolicy='Complete selected components are immutable; earlier complete alternatives remain reviewed candidates. New substantive completion requires independent challenge, not automatic scientific admission.')
 if packet.get('priorAnnotationContext'):
  out.update(status='valid_derived_representation',priorAnnotationContext=packet['priorAnnotationContext'],semanticRepairPerformed=False,contextRegistrationPolicy='Exact supplied prior annotation registered as context only; original reply references and historical/rejected status remain unchanged.')
 return out

if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError,IndexError,StopIteration) as error:print(json.dumps({'valid':False,'error':str(error)}));sys.exit(1)
