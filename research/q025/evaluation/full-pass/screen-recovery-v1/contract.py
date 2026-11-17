"""Strict missing-only completion. The original scientific screen validator is unchanged."""
import copy,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent
spec=importlib.util.spec_from_file_location('q025_frozen_screen',F/'canonical-triage-wave-v2/contract.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
from compact_contract import ob,ar,en,S,A,structure
SCHEMA=ob(version={'type':'string','const':'q025-screen-completion/1'},familyId=S,stage={'type':'string','const':'triage'},missingScopeReviews=copy.deepcopy(base.SCHEMA['properties']['scopeReviews']),missingComparisonReviews=copy.deepcopy(base.SCHEMA['properties']['comparisonReviews']),additionalLimitations=A,unresolved=A,attemptVariantReviews=ar(ob(variantRef=S,judgment=en('consistent_revision','material_conflict','unresolved'),definingDifferences=A,reason=S,refs=A)))
def assemble(packet,reply):
 structure(reply,SCHEMA);assert reply['familyId']==packet['familyId'];p=packet['preservedScreen'];out=copy.deepcopy(p['selectedFields'])
 for field,added in [('scopeReviews','missingScopeReviews'),('comparisonReviews','missingComparisonReviews')]:
  expected=set(p['missingRefs'][field]);rows=reply[added];assert len(rows)==len(expected)and{x['ref']for x in rows}==expected,'Missing/duplicate/overwritten screen completion';out[field]=out.get(field,[])+copy.deepcopy(rows)
 out['limitations']=out.get('limitations',[])+copy.deepcopy(reply['additionalLimitations']);assert 'unresolved'not in out,'A complete unresolved field must be preserved';out['unresolved']=copy.deepcopy(reply['unresolved'])
 expected={x['variantRef']for x in p['attemptVariants']};rows=reply['attemptVariantReviews'];assert len(rows)==len(expected)and{x['variantRef']for x in rows}==expected,'Missing/duplicate attempt variant review';known={x['ref']for x in packet['scopes']+packet['units']}
 for row in rows:
  assert row['reason']and row['refs']and len(row['refs'])==len(set(row['refs']))and set(row['refs'])<=known,'Missing/invented variant evidence'
  if row['judgment']=='material_conflict':assert row['definingDifferences'],'Material conflict requires explicit differences'
 return out
def evaluate(packet,reply):
 assembled=assemble(packet,reply);out=base.evaluate(packet,assembled);p=packet['preservedScreen'];retained=p['selectedFields']
 for field,value in retained.items():assert assembled[field][:len(value)]==value if isinstance(value,list)else assembled[field]==value,'Retained completed judgment changed'
 withheld=[x['variantRef']for x in reply['attemptVariantReviews']if x['judgment']!='consistent_revision']
 out.update(status='valid_derived_representation',originalCompletionReplyValueSha256=base.vh(reply),preservedScreenArtifactSha256=packet['preservedScreenArtifactSha256'],selectedAttempt=p['selectedAttempt'],attemptVariantReviews=copy.deepcopy(reply['attemptVariantReviews']),withheldAttemptVariantRefs=withheld,withheldComponents=[{'variantRef':x['variantRef'],'selectedPath':x['selectedPath']}for x in p['attemptVariants']if x['variantRef']in withheld],originalCompleteFieldsChanged=False,discardedCompleteScientificComponents=0,completionPolicy='Only missing scope/comparison records, tail limitations/unresolved items and explicit variant assessments are new. Complete selected judgments remain unchanged. Conflicting alternatives are withheld for downstream adjudication; normalized selected fields do not resolve the conflict.',scientificAdmission=False,identityAdmission=False,navigationAdmission=False)
 return out
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,ValueError,TypeError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
