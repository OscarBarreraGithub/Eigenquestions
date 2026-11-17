"""One typed structural-context exception; frozen scientific validation unchanged."""
import copy,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;V1=B.parent/'recovery-successors-v1';sys.path.append(str(V1))
spec=importlib.util.spec_from_file_location('q025_successor_v1_contract',V1/'contract.py');v1=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1)
SCHEMA=v1.SCHEMA;structure=v1.structure;completion_schema=v1.completion_schema;regular_schema=v1.regular_schema
from prefix import assemble,value_hash
FIELDS={'identityGroups','cardReviews','groupReviews'}

def structural_context(packet,reply,origin):
 assert packet['familyId']=='ce36cae0274019373c8a' and packet['stage']=='proposal'
 composite=assemble(packet['preservedComponents'],reply['remaining']);contexts=[]
 variants={x['variantRef']:x for x in packet['streamVariants']}
 for row in reply['variantAssessments']:
  if row['refs']:continue
  variant=variants[row['variantRef']];assert len(variant['path'])==1 and variant['path'][0] in FIELDS and variant['value']==[]
  key=variant['path'][0];assert composite[key]==[] and row['decision']=='consistent_revision' and row['reason']
  assert packet.get('priorCards',[])==[] and packet.get('priorGroups',[])==[] and packet.get('existingCards',[])==[]
  contexts.append({'variantRef':row['variantRef'],'kind':'artifact_structure','fieldPath':'$.'+key,'comparedValue':[],'valueSha256':value_hash([]),'inputAbsentPaths':['$.priorCards','$.priorGroups','$.existingCards'],'inputAbsentValues':[[],[],[]],'primaryReadingClaim':False,'scientificReferenceInvented':False,'originalAssessment':copy.deepcopy(row),'origin':copy.deepcopy(origin),'scope':'Inspection of the exact supplied earlier proposal/input arrays only; not a scientific assertion of physical absence.'})
 assert {x['fieldPath'] for x in contexts}=={'$.'+k for k in FIELDS} and len(contexts)==3
 out=copy.deepcopy(packet);out['structuralVariantEvidence']=contexts;return out,contexts

def check_variants(packet,rows):
 expected={v['variantRef'] for v in packet.get('streamVariants',[])}
 assert len(rows)==len(expected) and {r['variantRef'] for r in rows}==expected,'Missing/duplicate earlier-attempt review'
 evidence={x['variantRef']:x for x in packet.get('structuralVariantEvidence',[])}
 for row in rows:
  assert row['reason'] and set(row['refs'])<=set(packet['refRegistry']),'Missing/invented variant evidence'
  if row['refs']:continue
  proof=evidence.get(row['variantRef']);assert packet['familyId']=='ce36cae0274019373c8a' and proof and row['decision']=='consistent_revision','Empty scientific refs require exact structural evidence'
  variant=next(x for x in packet['streamVariants'] if x['variantRef']==row['variantRef']);assert variant['path']==[proof['fieldPath'][2:]] and variant['path'][0] in FIELDS and variant['value']==[]
  assert proof['kind']=='artifact_structure' and proof['comparedValue']==[] and proof['valueSha256']==value_hash([]) and proof['inputAbsentValues']==[[],[],[]] and proof['primaryReadingClaim'] is False
  assert all(proof['origin'].get(k) for k in ['packetPath','packetSha256','prefixPath','prefixSha256','replyPath','replySha256','compositeReviewValueSha256'])

v1.check_variants=check_variants
def evaluate(packet,reply):
 out=v1.evaluate(packet,reply)
 if packet.get('structuralVariantEvidence'):out.update(structuralVariantEvidence=copy.deepcopy(packet['structuralVariantEvidence']),structuralContextPolicy='Exact three empty-array artifact inspections remain typed structural context. Raw reply and scientific validation unchanged; no primary references invented.')
 return out

if __name__=='__main__':
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError,IndexError,StopIteration) as error:print(json.dumps({'valid':False,'error':str(error)}));sys.exit(1)
