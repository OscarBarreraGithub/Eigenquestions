"""Only missing challenge fields and explicit second-attempt adjudication."""
import copy,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;F=B.parent;sys.path.append(str(F/'canonical-recovery-v3'))
spec=importlib.util.spec_from_file_location('q025_canonical_v3',F/'canonical-recovery-v3/contract.py');v3=importlib.util.module_from_spec(spec);spec.loader.exec_module(v3)
old=v3.old;base=old.base
from compact_contract import ob,ar,en,S,A,structure
variant=ob(variantRef=S,judgment=en('consistent_revision','material_conflict','unresolved'),definingDifferences=A,reason=S,refs=A)
SCHEMA=ob(version={'type':'string','const':'q025-canonical-challenge-completion/1'},familyId=S,stage={'type':'string','const':'challenge'},additionalLimitations=A,unresolved=A,streamVariantReviews=copy.deepcopy(old.CHALLENGE_SCHEMA['properties']['streamVariantReviews']),attemptVariantReviews=ar(variant))
def assemble(packet,reply):
 structure(reply,SCHEMA);assert reply['familyId']==packet['familyId']=='control-statistics';p=packet['preservedChallenge'];out=copy.deepcopy(p['completeFields']);assert out['stage']=='challenge'
 out['limitations']=copy.deepcopy(p['completeArrayPrefixes']['limitations'])+reply['additionalLimitations'];out['unresolved']=copy.deepcopy(reply['unresolved']);out['streamVariantReviews']=copy.deepcopy(reply['streamVariantReviews'])
 expected={x['variantRef']for x in p['attemptVariants']};rows=reply['attemptVariantReviews'];assert len(rows)==len(expected) and {x['variantRef']for x in rows}==expected,'Missing/duplicate second-attempt adjudication'
 for row in rows:
  assert row['reason'] and row['refs'] and len(row['refs'])==len(set(row['refs'])) and set(row['refs'])<=set(packet['refRegistry']),'Missing/invented variant evidence'
  if row['judgment']=='material_conflict':assert row['definingDifferences'],'Material conflict requires explicit differences'
 return out
def evaluate(packet,reply):
 assembled=assemble(packet,reply);out=v3.evaluate(packet,assembled);p=packet['preservedChallenge'];out.update(status='valid_derived_representation',originalCompletionReplyValueSha256=base.vh(reply),preservedChallengeArtifactSha256=packet['preservedChallengeArtifactSha256'],selectedAttempt=0,attemptVariantReviews=copy.deepcopy(reply['attemptVariantReviews']),withheldAttemptVariantRefs=[x['variantRef']for x in reply['attemptVariantReviews']if x['judgment']!='consistent_revision'],originalCompleteFieldsChanged=False,discardedCompleteScientificComponents=0,completionPolicy='Only limitations tail, unresolved items and two explicit sets of variant judgments are new. All complete selected challenge fields remain immutable; every differing complete second-attempt record remains inspectable. No alternate field is silently spliced or admitted.',acceptance='Strict format/coverage validation admits no scientific equivalence or source contribution. Material conflicts and unresolved variants remain withheld for explicit downstream adjudication.')
 assert all(assembled[k]==v for k,v in p['completeFields'].items()),'Selected completed science changed'
 return out
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
