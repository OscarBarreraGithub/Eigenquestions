"""Single-pass prioritization; identity difference never erases useful connections."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent.parent/'recovery'));from compact_contract import structure,ob,ar,en,S,A
SCHEMA=ob(version={'type':'string','const':'q025-canonical-triage/1'},familyId=S,stage={'type':'string','const':'triage'},summary=S,scopeReviews=ar(ob(ref=S,status=en('retain_as_scoped','needs_reconciliation','needs_narrowing','unclear_scope','outside_packet_search_required'),basis=en('scope_definition','paired_review_context','description_checked'),reason=S,refs=A)),comparisonReviews=ar(ob(ref=S,identityScreen=en('plausible_same_scope','different_scoped_targets','specialization_candidate','common_target_candidate','unresolved'),scientificConnections=ar(en('shared_method','conditional_application','broader_question','comparison','none_identified','unresolved')),basis=en('scope_definition','paired_review_context','description_checked'),priority=en('definition_decision_candidate','rich_scope_review','rich_premise_review','rich_relation_review','unresolved'),definingDifferences=A,reason=S,refs=A)),limitations=A,unresolved=A)
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def evaluate(p,r):
 structure(r,SCHEMA);assert r['familyId']==p['familyId']and r['stage']=='triage';scopes={s['ref']:s for s in p['scopes']};units={u['ref']:u for u in p['units']};known=set(scopes)|set(units);pairs={n['ref']:n for n in p['nominations']};assert len(r['scopeReviews'])==len(scopes)and{x['ref']for x in r['scopeReviews']}==set(scopes),'Missing/duplicate scope triage coverage';assert len(r['comparisonReviews'])==len(pairs)and{x['ref']for x in r['comparisonReviews']}==set(pairs),'Missing/duplicate comparison triage coverage'
 for row in r['scopeReviews']+r['comparisonReviews']:
  assert row['reason']and row['refs']and len(row['refs'])==len(set(row['refs']))and set(row['refs'])<=known,'Invented/duplicate/missing triage evidence';
  if row['basis']=='description_checked':assert any(x in units for x in row['refs']),'Description basis needs an actual supplied description'
  elif row['basis']=='paired_review_context':assert any(x in scopes and(scopes[x].get('priorReadingAssessment')or scopes[x]['scopeStatus'].startswith('explicitly_'))for x in row['refs']),'Inherited basis needs an actual prior assessment/admission'
  else:assert all(x in scopes for x in row['refs']),'Definition-only basis must cite scope definitions'
 for row in r['comparisonReviews']:
  assert row['scientificConnections']and len(row['scientificConnections'])==len(set(row['scientificConnections'])),'Missing/duplicate connection screen';assert 'none_identified'not in row['scientificConnections']or len(row['scientificConnections'])==1,'No connection identified cannot erase separately nominated connections'
  if row['identityScreen']=='different_scoped_targets':assert row['definingDifferences'],'Distinct target screen requires explicit defining contrast'
 return {'schemaVersion':'q025-triage-derived-review/1','status':'valid_original_representation','normalizedReview':copy.deepcopy(r),'originalReplyValueSha256':vh(r),'normalizedReplyValueSha256':vh(r),'factorRenameMap':{},'rowAgreementTransforms':[],'crossUnitDescriptionContext':[],'validation':{'valid':True,'scopeCount':len(scopes),'comparisonCount':len(pairs),'primaryWindowsRead':0},'scientificAdmission':False,'identityAdmission':False,'navigationAdmission':False,'acceptance':'One screening pass prioritizes exact later decisions. Different scoped targets can retain method/application/common-parent possibilities. No primary rereading or uniqueness certification.'}
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,ValueError,TypeError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
