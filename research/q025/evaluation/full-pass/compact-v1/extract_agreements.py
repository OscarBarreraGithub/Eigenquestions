"""Inspect compact judgments without promoting reviewer output to accepted science."""
import hashlib,json,sys,subprocess
from pathlib import Path
from compact_pipeline import assignment_comparison
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'recovery'))
from compact_contract import validate

def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def extract(packet,review,review_id,review_sha):
 validation=validate(packet,review);units={u['i']:u for u in packet['units']};registry=packet['refRegistry'];rows={a['i']:a for a in review['units']}
 def uid(i):return registry[f'u{i}']['unitId']
 def exact_refs(refs):return [{'ref':r,**registry[r]} for r in refs]
 def evidence_units(refs):
  out=[]
  for r in refs:
   rr=registry[r]
   if rr.get('unitIndex') in units:out.append(uid(rr['unitIndex']))
   elif rr['kind']=='primary':out.extend(uid(i) for i,u in units.items() if r in u['primaryRefs'])
   elif rr['kind']=='source_object':out.extend(uid(i) for i,u in units.items() if r in u['sourceObjectRefs'])
  return list(dict.fromkeys(out))
 assessments={a['id']:a for a in review['cardReviews']};scope_candidates=[]
 for c in packet.get('priorCards',[]):
  a=assessments[c['id']];kind='region' if c['id']=='r' else 'question'
  indices=[i for i,row in rows.items() if kind=='region' and row['d'] in ['member','overlap'] or any(q['id']==c['id'] for q in row['q'])]
  refs=list(dict.fromkeys(c.get('refs',[])+a['refs']));ev=evidence_units(refs)
  content={'kind':kind,'title':c['title'],'question':c['question'],'summary':c['summary'],'scope':c['scope'],'scientificStatus':'source_reviewed_scope_with_explicit_limits','readingCoverage':{'descriptionCheckedCount':len(indices),'excerptCheckedCount':sum(rows[i]['b']=='excerpt' for i in indices),'readingLimit':c.get('readingLimit',''),'sourceReadingScope':'Supplied descriptions and bounded primary excerpts only; no full-paper or figure verification.'},'evidenceIds':ev}
  candidate_id='q025-scope-candidate:'+digest({k:content[k] for k in ['kind','question','scope']})[:24]
  scope_candidates.append({'id':candidate_id,'localRef':c['id'],'content':content,'agreement':a['decision'],'scopeChange':a['scopeChange'],'unchangedPriorScope':True,'requiresCoordinatorAdmission':True,'eligibleUnchangedScope':a['decision']=='supported_as_written' and a['scopeChange']=='same' and bool(ev),'assessment':a,'sourceReviewIds':[review_id],'sourceReviewSha256':review_sha,'evidenceRefs':exact_refs(refs),'memberIndices':indices})
 # Shared helper owns exact readable-scope hashing, including its insertion order.
 helper=Path(__file__).resolve().parents[3]/'assembly/accepted.mjs'
 js='import {scopeContentHash} from '+json.dumps(helper.as_uri())+';let s="";for await(const c of process.stdin)s+=c;console.log(JSON.stringify(JSON.parse(s).map(scopeContentHash)));'
 hashes=json.loads(subprocess.run(['node','--input-type=module','-e',js],input=json.dumps([x['content'] for x in scope_candidates],ensure_ascii=False),text=True,capture_output=True,check=True).stdout)
 for c,h in zip(scope_candidates,hashes):c['scopeContentSha256']=h
 comparison=assignment_comparison(packet,review);comparison={a['i']:a for a in comparison};assignments=[];groups=[]
 for a in review['units']:
  factors={f['id']:f for f in packet.get('priorFactors',[])+review['factors']}
  assignments.append({'unitId':uid(a['i']),'unitIndex':a['i'],'basis':'source_excerpt_checked' if a['b']=='excerpt' else 'description_checked','disposition':a['d'],'contributions':a['q'],'activeFactorRefs':[f for f in a['f'] if factors[f]['status']!='historical_or_rejected'],'historicalFactorRefs':[f for f in a['f'] if factors[f]['status']=='historical_or_rejected'],'identity':a['identity'],'title':a['title'],'agreement':comparison[a['i']],'reason':a['reason'],'note':a['note'],'alternateHome':a['home'],'evidenceRefs':exact_refs([f'd{a["i"]}']+a['refs'] if f'd{a["i"]}' not in a['refs'] else a['refs'])})
 for g in review['identityGroups']:
  groups.append({**g,'representativeUnitId':uid(g['representative']),'memberIds':[uid(a['i']) for a in review['units'] if a['identity']==g['id']],'identityStatus':'proposed_equivalence_candidate','accepted':False})
 for a in review['units']:
  if a['identity'] in ['s','?']:groups.append({'id':f'source-fine:{uid(a["i"])}','representativeUnitId':uid(a['i']),'memberIds':[uid(a['i'])],'title':a['title'],'identityStatus':'proposed_singleton' if a['identity']=='s' else 'unresolved','accepted':False,'reason':a['note'],'parentCardRefs':[q['id'] for q in a['q']]})
 return {'schemaVersion':'q025-compact-agreement-candidates/1','familyId':packet['familyId'],'status':'requires_coordinator_admission','reviewId':review_id,'reviewSha256':review_sha,'validation':validation,'originalRegionVerdict':review['verdict'],'scopeCandidates':scope_candidates,'newUnchallengedCards':review['cards'],'currentRegionCandidate':review['region'],'assignments':assignments,'fineIdentityGroups':groups,'groupReviews':review['groupReviews'],'links':review['links'],'identityComparisons':review['identityComparisons'],'limitations':review['limitations'],'unresolved':review['unresolved'],'acceptance':'No raw verdict, rewritten scope, singleton or new fine group is automatically admitted.'}
if __name__=='__main__':
 packet=json.loads(Path(sys.argv[1]).read_text());reply_path=Path(sys.argv[2]);review=json.loads(reply_path.read_text());out=extract(packet,review,sys.argv[4] if len(sys.argv)>4 else reply_path.parent.name,hashlib.sha256(reply_path.read_bytes()).hexdigest());Path(sys.argv[3]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'valid':True,'scopes':len(out['scopeCandidates']),'eligibleUnchangedScopes':sum(x['eligibleUnchangedScope'] for x in out['scopeCandidates']),'assignments':len(out['assignments']),'fineGroups':len(out['fineIdentityGroups']),'accepted':False}))
