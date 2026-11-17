"""Complete missing fields; preserve earlier stream variants for independent review."""
import copy,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('q025_canonical_base',B.parent/'canonical-v1/contract.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from compact_contract import ob,ar,en,S,A,structure
variant=ob(variantRef=S,selectedQuestionRef=S,decision=en('consistent_revision','material_conflict','unresolved'),definitionDifferences=A,reason=S,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-canonical-completion/1'},familyId=S,stage={'type':'string','const':'proposal'},additionalDecisions=base.SCHEMA['properties']['decisions'],additionalPairConstraints=base.SCHEMA['properties']['pairConstraints'],scopeDispositions=base.SCHEMA['properties']['scopeDispositions'],sourceContributions=base.SCHEMA['properties']['sourceContributions'],compoundSources=base.SCHEMA['properties']['compoundSources'],variantAssessments=ar(variant),limitations=A,unresolved=A)
CHALLENGE_SCHEMA=copy.deepcopy(base.SCHEMA);CHALLENGE_SCHEMA['properties']['streamVariantReviews']=ar(variant);CHALLENGE_SCHEMA['required'].append('streamVariantReviews')
def check_variants(packet,rows):
 expected={x['variantRef']:x for x in packet.get('streamVariants',[])};assert len(rows)==len(expected) and {x['variantRef'] for x in rows}==set(expected),'Missing/duplicate stream-variant assessment'
 for x in rows:assert x['selectedQuestionRef']==expected[x['variantRef']]['selectedQuestionRef'] and x['reason'] and x['refs'];assert set(x['refs'])<=set(packet['refRegistry']),'Invented variant evidence'
def assemble(packet,completion):
 structure(completion,SCHEMA);assert completion['familyId']==packet['familyId'];check_variants(packet,completion['variantAssessments']);prefix=packet['preservedComponents'];out=copy.deepcopy(prefix['completeFields']);out['decisions']=copy.deepcopy(out.get('decisions',prefix['completeArrayPrefixes'].get('decisions',[])))+completion['additionalDecisions'];out['pairConstraints']=copy.deepcopy(out.get('pairConstraints',prefix['completeArrayPrefixes'].get('pairConstraints',[])))+completion['additionalPairConstraints'];out.update({k:completion[k] for k in ['scopeDispositions','sourceContributions','compoundSources','limitations','unresolved']});out['priorReviews']=[];base.evaluate(packet,out);return out

def evaluate(packet,reply):
 if packet['stage']=='challenge':
  structure(reply,CHALLENGE_SCHEMA);check_variants(packet,reply['streamVariantReviews']);plain=copy.deepcopy(reply);variants=plain.pop('streamVariantReviews');out=base.evaluate(packet,plain);out.update(status='valid_derived_representation',originalReplyValueSha256=base.vh(reply),streamVariantReviews=variants,variantPolicy='Withhold affected selected scopes/identity if an earlier definition conflict remains unresolved.');return out
 out=assemble(packet,reply);return {'schemaVersion':'q025-canonical-prefix-completion/2','status':'valid_derived_representation','originalReplyValueSha256':base.vh(reply),'normalizedReplyValueSha256':base.vh(out),'normalizedReview':out,'prefixArtifactSha256':packet['prefixArtifactSha256'],'streamVariantAssessments':reply['variantAssessments'],'completedFields':['decisions_tail','pairConstraints_tail','scopeDispositions','sourceContributions','compoundSources','limitations','unresolved'],'originalCompleteFieldsChanged':False,'discardedCompleteScientificComponents':0,'factorRenameMap':{},'rowAgreementTransforms':[],'crossUnitDescriptionContext':[],'validation':{'valid':True,'scopeCount':len(out['scopeDispositions']),'preservedQuestions':len(out['newQuestions'])},'semanticRepairPerformed':False,'acceptance':'Composite proposal only; original failures and earlier variants preserved. Independent full challenge and variant conflict review required.'}
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 if '--challenge-schema' in sys.argv:print(json.dumps(CHALLENGE_SCHEMA,indent=2));sys.exit(0)
 data=json.load(sys.stdin)
 try:print(json.dumps(evaluate(data['packet'],data['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
