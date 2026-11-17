"""Small complete-clause reviews; no silent completion or source-coverage repair."""
import copy,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent.parent/'recovery'));from compact_contract import structure,ob,ar,en,S,A
SCHEMA=ob(version={'type':'string','const':'q025-clause-review/1'},familyId=S,stage=en('proposal','challenge'),summary=S,results=ar(ob(caseId=S,status=en('complete_as_written','replace_proposed','insufficient_evidence'),replacementText=S,meaningChange=en('unchanged','clarification_within_supplied_scope','narrower','different','unclear'),scopeImpact=en('annotation_only','premise_change','scope_change','unresolved'),reason=S,refs=A)),priorAssessments=ar(ob(caseId=S,decision=en('supported_as_written','revise','insufficient_evidence'),reason=S,refs=A)),limitations=A,unresolved=A)
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def evaluate(p,r):
 structure(r,SCHEMA);assert r['familyId']==p['familyId'] and r['stage']==p['stage'];cases={c['caseId']:c for c in p['cases']};rows=r['results'];assert len(rows)==len(cases) and {x['caseId'] for x in rows}==set(cases),'Missing/duplicate clause coverage'
 for x in rows:
  c=cases[x['caseId']];assert len(x['refs'])==len(set(x['refs'])) and set(x['refs'])<=set(c['refs']),'Invented evidence ref';assert x['reason']
  if x['status']=='complete_as_written':assert x['replacementText']==c['originalText'] and x['meaningChange']=='unchanged','Unchanged clause must be byte-identical'
  elif x['status']=='replace_proposed':assert x['replacementText'] and x['replacementText']!=c['originalText'] and x['refs'] and x['meaningChange']!='unchanged','Replacement must be explicit supported proposal, never recovered lost words'
  else:assert x['replacementText']=='','Abstention must not fabricate a completion'
 prior=p.get('priorReview');assert len(r['priorAssessments'])==(len(cases) if prior else 0),'Missing independent clause assessments'
 if prior:
  assert {x['caseId'] for x in r['priorAssessments']}==set(cases)
  for a in r['priorAssessments']:assert set(a['refs'])<=set(cases[a['caseId']]['refs']) and a['reason']
 return {'schemaVersion':'q025-clause-derived-review/1','status':'valid_original_representation','originalReplyValueSha256':vh(r),'normalizedReplyValueSha256':vh(r),'normalizedReview':copy.deepcopy(r),'factorRenameMap':{},'rowAgreementTransforms':[],'crossUnitDescriptionContext':[],'validation':{'valid':True,'clauseCount':len(rows)},'semanticRepairPerformed':False,'acceptance':'Replacement qualifications and justifications remain candidates until independent agreement/adjudication; original raw fields never change.'}
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit(0)
 d=json.load(sys.stdin)
 try:print(json.dumps(evaluate(d['packet'],d['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
