"""Effective prior graph: explicit support retains objects without re-emission."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('native_navigation',B.parent/'navigation-decisions-v1/contract.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
from compact_contract import structure,ar,A
SCHEMA=copy.deepcopy(old.SCHEMA);SCHEMA['properties']['supersededPriorDecisionIds']=A;SCHEMA['required'].append('supersededPriorDecisionIds')
def vh(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def evaluate(p,r):
 structure(r,SCHEMA);assert r['familyId']==p['familyId']and r['stage']==p['stage'];original=copy.deepcopy(r);view=copy.deepcopy(r);superseded=view.pop('supersededPriorDecisionIds');prior=p.get('priorReview')or{};refs=p['refRegistry'];scopeids={s['ref']for s in p['scopes']}
 expected={d['id']:'decision'for d in prior.get('decisions',[])};expected.update({q['id']:'new_question'for q in prior.get('newQuestions',[])});assess={a['ref']:a for a in view['priorReviews']};assert len(assess)==len(view['priorReviews'])and set(assess)==set(expected),'Missing/duplicate prior assessment';assert all(assess[k]['kind']==v for k,v in expected.items());pd={d['id']:d for d in prior.get('decisions',[])};pq={q['id']:q for q in prior.get('newQuestions',[])}
 assert len(superseded)==len(set(superseded))and set(superseded)<=set(pd),'Unknown/duplicate superseded prior decision';assert all(assess[x]['verdict']=='revise'for x in superseded),'Superseded prior decision needs an explicit revision assessment'
 newq=[];retained=[]
 for q in view['newQuestions']:
  if q['id']in pq:
   assert q==pq[q['id']]and assess[q['id']]['verdict']=='supported_as_written','Changed prior question needs a new ID';retained.append({'kind':'question','ref':q['id'],'valueSha256':vh(q)})
  else:newq.append(q)
 view['newQuestions']=newq
 current={d['id']:d for d in view['decisions']};assert len(current)==len(view['decisions']),'Duplicate current decision';effective=[];aliases={}
 for d in view['decisions']:
  if d['id']in pd:
   assert d==pd[d['id']]and assess[d['id']]['verdict']=='supported_as_written'and d['id']not in superseded,'Changed prior decision needs a new ID'
  else:effective.append(d)
 for ref,d in pd.items():
  if assess[ref]['verdict']=='supported_as_written'and ref not in superseded:
   alias='cd_retained_'+ref;assert alias not in current;aliases[ref]=alias;row=copy.deepcopy(d);row['id']=alias;effective.append(row);retained.append({'kind':'decision','ref':ref,'valueSha256':vh(d)})
 view['decisions']=effective
 for row in view['scopeDispositions']:row['decisionIds']=[aliases.get(x,x)for x in row['decisionIds']]
 known=scopeids|set(pq)|{q['id']for q in newq};compound=view['compoundSources']
 for row in compound:
  assert row['unitRef']in refs and refs[row['unitRef']]['kind']=='description';assert row['questionRefs']and len(row['questionRefs'])==len(set(row['questionRefs']))and set(row['questionRefs'])<=known,'Compound annotation requires one or more known destinations';assert row['reason']and row['refs']and len(row['refs'])==len(set(row['refs']))and set(row['refs'])<=set(refs)
 view['compoundSources']=[]
 oldnav={x['id']:x for x in prior.get('navigation',[])};navreview={x['ref']:x for x in view['navigationReviews']};assert len(navreview)==len(view['navigationReviews'])and set(navreview)==set(oldnav),'Missing prior navigation judgment';emitted={x['id']:x for x in view['navigation']};assert len(emitted)==len(view['navigation']);effective_nav=[]
 for x in view['navigation']:
  if x['id']in oldnav:assert x==oldnav[x['id']]and navreview[x['id']]['verdict']=='supported_as_written','Changed prior route needs a new ID'
  else:effective_nav.append(x)
 for ref,x in oldnav.items():
  if navreview[ref]['verdict']=='supported_as_written':effective_nav.append(copy.deepcopy(x));retained.append({'kind':'navigation','ref':ref,'valueSha256':vh(x)})
 view['navigation']=effective_nav
 # The prior packet can contain this version's extra field; the legacy core
 # sees an exact schema projection while the full provenance stays in output.
 pv=copy.deepcopy(p)
 if pv.get('priorReview'):pv['priorReview'].pop('supersededPriorDecisionIds',None)
 result=old.evaluate(pv,view)
 # Validate all explicit refs/kinds even for objects only retained in the
 # effective graph. No inherited primary claim is manufactured.
 for q in pq.values():
  assert q['question']and q['scope']['targets']and q['refs']and set(q['refs'])<=set(refs)
 result.update({'schemaVersion':'q025-effective-navigation-review/2','normalizedReview':original,'originalReplyValueSha256':vh(original),'normalizedReplyValueSha256':vh(original),'effectiveDecisions':[copy.deepcopy(d)for ref,d in pd.items()if assess[ref]['verdict']=='supported_as_written'and ref not in superseded]+[copy.deepcopy(d)for d in r['decisions']if d['id']not in pd],'effectiveNavigation':effective_nav,'retainedPriorObjects':retained,'compoundAnnotationsChecked':copy.deepcopy(compound),'validationOnlyAliases':aliases,'scientificContentChanged':False,'logicalObjectsDuplicated':0,'acceptance':'Format and complete reference/assessment coverage only. Scientific policy admission and global conflict gates are separate.'});return result
if __name__=='__main__':
 if '--schema'in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except(AssertionError,KeyError,TypeError,ValueError)as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
