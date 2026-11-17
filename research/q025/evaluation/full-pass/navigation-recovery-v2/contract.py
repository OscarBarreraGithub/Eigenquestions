"""Exact retained-object classification; no inferred scientific repair."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('navigation_contract',B.parent/'navigation-decisions-v1/contract.py');nav=importlib.util.module_from_spec(spec);spec.loader.exec_module(nav)
from compact_contract import ob,ar,en,S,A,structure
SCHEMA=copy.deepcopy(nav.SCHEMA);SCHEMA['properties']['equivalenceIssueReviews']=ar(ob(priorDecisionRef=S,currentDecisionRef=S,classification=en('same_scope_editorial_clarification','changed_scientific_scope','insufficient_evidence'),reason=S,refs=A));SCHEMA['required'].append('equivalenceIssueReviews')
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def classify_retained(p,r,issue_required=False):
 original=copy.deepcopy(r);view=copy.deepcopy(r);issues=view.pop('equivalenceIssueReviews',[]);prior=p.get('priorReview')or{};priorq={q['id']:q for q in prior.get('newQuestions',[])};priord={d['id']:d for d in prior.get('decisions',[])};assess={a['ref']:a for a in view['priorReviews']};retained=[];aliases={};questions=[]
 for q in view['newQuestions']:
  if q['id']not in priorq:questions.append(q);continue
  assert q==priorq[q['id']],'Changed prior definition cannot be silently retained';assert assess.get(q['id'],{}).get('verdict')=='supported_as_written','Retained definition needs explicit independent support';retained.append({'kind':'new_question','priorRef':q['id'],'exactValueSha256':vh(q),'createsNewLogicalObject':False})
 view['newQuestions']=questions
 for d in view['decisions']:
  if d['id']not in priord:continue
  assert d==priord[d['id']],'Changed prior decision cannot masquerade as an exact retained object';assert assess.get(d['id'],{}).get('verdict')=='supported_as_written','Retained decision needs explicit independent support';old=d['id'];alias='cd_retained_'+old;assert alias not in {x['id']for x in view['decisions']};aliases[old]=alias;retained.append({'kind':'decision','priorRef':old,'serializationValidationAlias':alias,'exactValueSha256':vh(d),'createsNewLogicalObject':False});d['id']=alias
 for row in view['scopeDispositions']:row['decisionIds']=[aliases.get(v,v)for v in row['decisionIds']]
 # Exact repeated navigation has no stage namespace restriction. Its own
 # explicit review is mandatory in the existing whole-output contract.
 priorlinks={x['id']:x for x in prior.get('navigation',[])}
 for row in view['navigation']:
  if row['id']in priorlinks:
   assert row==priorlinks[row['id']],'Changed route needs a new identity';retained.append({'kind':'navigation','priorRef':row['id'],'exactValueSha256':vh(row),'createsNewLogicalObject':False})
 if issue_required:
  assert len(issues)==1 and issues[0]['priorDecisionRef']=='pd0','Explicit c0/c1/pq0 equivalence issue assessment is required';issue=issues[0];assert issue['reason']and issue['refs']and set(issue['refs'])<=set(p['refRegistry']);assert issue['currentDecisionRef']in{x['id']for x in original['decisions']};row=next(x for x in original['decisions']if x['id']==issue['currentDecisionRef'])
  if issue['classification']=='same_scope_editorial_clarification':assert row['operation']=='same_scoped_question'and set(row['members'])=={'c0','c1','pq0'}and row['target']=='pq0'and not row['definingDifferences'],'Editorial equivalence needs an explicit complete three-scope group and no hidden defining change'
  else:assert row['operation']!='same_scoped_question','Unresolved/changed scope cannot be admitted as equivalence'
 derived=nav.evaluate(p,view);derived['normalizedReview']=original;derived['originalReplyValueSha256']=vh(original);derived['normalizedReplyValueSha256']=vh(original);derived['status']='valid_derived_retained_representation'if retained else'valid_original_representation';derived['retainedPriorObjects']=retained;derived['validationOnlyAliases']=aliases;derived['scientificContentChanged']=False;derived['logicalObjectsDuplicated']=0;derived['acceptance']='Retained objects are byte/value-identical to supplied prior objects and explicitly supported. Temporary aliases serve validation only and create no second scientific object. All substantive operation and whole-group admission gates remain separate.';return derived
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:structure(x['reply'],SCHEMA);print(json.dumps(classify_retained(x['packet'],x['reply'],True),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,ValueError,TypeError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
