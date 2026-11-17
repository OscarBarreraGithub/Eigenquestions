#!/usr/bin/env python3
"""Registry-wide nomination audit; no learned encoding or identity admission."""
import argparse,collections,hashlib,json,math,re,unicodedata
from pathlib import Path
STOP=set('a an the and or of for to in on at by with without under from through between into across how what which when why can could do does is are be been being have has that this these those their its each any all as than then where whether while within specified source specific stated proposed particular supplied related different distinct conditions question questions framework frameworks analysis including include approach using determine follows establish given'.split())
def sha(b):return hashlib.sha256(b).hexdigest()
def tokens(value):
 s=unicodedata.normalize('NFKC',str(value)).lower().replace('stabilisation','stabilization').replace('stabilised','stabilized').replace('supersymmetry-breaking','supersymmetry breaking').replace('no-scale','noscale')
 out=set()
 for t in re.findall(r'[a-z0-9]+',s):
  for prefix,canonical in [('sequester','sequestering'),('stabiliz','stabilization'),('mediat','mediation'),('compactif','compactification')]:
   if t.startswith(prefix):t=canonical;break
  if len(t)>4 and t.endswith('s') and not t.endswith('ss'):t=t[:-1]
  if len(t)>1 and t not in STOP:out.add(t)
 return out
def text_of(value):return ' '.join(map(str,value)) if isinstance(value,list) else str(value or '')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--registry',required=True,type=Path);ap.add_argument('--expected-sha256',required=True);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();raw=a.registry.read_bytes();assert sha(raw)==a.expected_sha256,'Registry changed; use a newly pinned snapshot';registry=json.loads(raw);assert registry['schemaVersion'] in ['q025-authored-scope-registry/1','q025-authored-scope-registry/3'];records=registry['records'];factors={f['factorRef']:f for f in registry['factors']};assert len({r['recordId'] for r in records})==len(records)
 features=[];frequency=collections.Counter();factor_exclusions=collections.Counter()
 for r in records:
  d=r['definition'];scope=d['scope'];q=tokens(d['question']);title=tokens(d['title']);target=tokens(text_of(scope.get('targets',[])));frequency.update(q|target)
  fs=collections.defaultdict(dict)
  for ref in {f for c in r['contributions'] for f in c.get('factorRefs',[])}:
   f=factors[ref];definition=f['definition']
   if definition.get('status')=='historical_or_rejected' or f.get('flags'):factor_exclusions['historical_or_flagged_refs']+=1;continue
   kind=definition.get('kind');label=' '.join(sorted(tokens(definition.get('label',''))));
   if kind in ['target','system','regime','method'] and label:fs[kind][label]=ref
  primary=set()
  for e in r.get('evidenceRefs',[]):
   if e.get('kind')=='primary':
    ctx=e.get('sourceContext',{})
    if ctx.get('path') and ctx.get('textSha256'):primary.add((e.get('paperId'),ctx.get('path'),ctx.get('pdfPage'),ctx.get('start'),ctx.get('end'),ctx.get('textSha256')))
  features.append({'q':q,'title':title,'target':target,'sourceIds':{c['unitId'] for c in r['contributions']},'primary':primary,'factor':fs})
 weights={t:1+math.log((len(records)+1)/(n+1)) for t,n in frequency.items()}
 def jac(x,y):return sum(weights.get(t,1) for t in x&y)/max(sum(weights.get(t,1) for t in x|y),1e-12)
 pairs=[];coverage=collections.defaultdict(list);nearest=collections.defaultdict(list);eligible_pairs=0
 for i,left in enumerate(records):
  x=features[i]
  for j in range(i+1,len(records)):
   right=records[j]
   if left['reviewKey']==right['reviewKey'] or left['kind']!=right['kind']:continue
   eligible_pairs+=1;y=features[j];shared=sorted(x['sourceIds']&y['sourceIds']);primary=sorted(x['primary']&y['primary'],key=str);qscore=jac(x['q'],y['q']);tscore=jac(x['target'],y['target']);lscore=jac(x['title'],y['title']);sameq=left['definition']['question'].strip().casefold()==right['definition']['question'].strip().casefold();sametitle=left['definition']['title'].strip().casefold()==right['definition']['title'].strip().casefold();factor_shared={k:sorted(set(x['factor'][k])&set(y['factor'][k])) for k in ['target','system','regime','method']};channels=[]
   if shared:channels.append('same_exact_source_unit')
   if primary:channels.append('same_bounded_primary_window')
   if sameq:channels.append('same_authored_question_text')
   if sametitle or lscore>=.65 or len(x['title']&y['title'])>=2 and lscore>=.18:channels.append('repeated_title')
   if factor_shared['target'] and (tscore>=.12 or qscore>=.12):channels.append('screened_target_factor_overlap')
   if tscore>=.22 and len(x['target']&y['target'])>=3:channels.append('authored_target_overlap')
   if qscore>=.28 and len(x['q']&y['q'])>=4:channels.append('authored_question_overlap')
   score=100*sameq+30*bool(shared)+15*bool(primary)+10*lscore+15*tscore+15*qscore+min(len(factor_shared['target']),3)
   nearest[left['recordId']].append((score,right['recordId']));nearest[right['recordId']].append((score,left['recordId']))
   if not channels:continue
   pairid='scope-nomination:'+sha((left['recordId']+'\n'+right['recordId']).encode())[:24]
   pair={'id':pairid,'recordIds':[left['recordId'],right['recordId']],'candidateIds':[left['candidateId'],right['candidateId']],'admittedDestinationIds':[left.get('admittedDestinationId'),right.get('admittedDestinationId')],'kind':left['kind'],'nominationChannels':channels,'rankingScore':round(score,6),'scoreMeaning':'Queue ordering only; not equivalence probability or scientific confidence.','sharedUnitIds':shared,'sharedPrimaryWindows':[dict(zip(['paperId','path','pdfPage','start','end','textSha256'],p)) for p in primary], 'metrics':{'questionWeightedTokenJaccard':qscore,'targetWeightedTokenJaccard':tscore,'titleWeightedTokenJaccard':lscore},'factorOverlap':{k:[{'normalizedLabel':label,'leftRef':x['factor'][k][label],'rightRef':y['factor'][k][label]} for label in labels] for k,labels in factor_shared.items() if labels},'scopeStatuses':[left['scopeStatus'],right['scopeStatus']],'reviewStatus':'unreviewed_nomination','allowedReviewOutcomes':['same_question_as_scoped','specialization','shared_parent_distinct_questions','method_bridge','comparison','different','unresolved'],'premiseComparisonRequired':True}
   pairs.append(pair);coverage[left['recordId']].append(pairid);coverage[right['recordId']].append(pairid)
 pairs.sort(key=lambda p:(-p['rankingScore'],p['id']));known={r['recordId']:r for r in records};unmatched=[{'recordId':r['recordId'],'title':r['definition']['title'],'status':'no_cross_review_candidate_under_current_rules_not_certified_unique','nearestLexicalReviewCandidates':[{'recordId':v,'rankingScore':s} for s,v in sorted(nearest[r['recordId']],reverse=True)[:3]]} for r in records if not coverage[r['recordId']]]
 a.out.mkdir(parents=True,exist_ok=True);full={'schemaVersion':'q025-global-scope-nominations/1','registryPath':str(a.registry),'registrySha256':sha(raw),'acceptedEquivalences':0,'pairs':pairs,'coverage':[{'recordId':r['recordId'],'candidateId':r['candidateId'],'admittedDestinationId':r.get('admittedDestinationId'),'candidatePairIds':coverage[r['recordId']],'status':'candidate_review_pending' if coverage[r['recordId']] else 'unmatched_review_required'} for r in records],'unmatched':unmatched,'reviewQueue':[{'batchId':f'scope-nominations-{k//12:04d}','pairIds':[p['id'] for p in pairs[k:k+12]],'meaning':'Bounded queue grouping only, not a scientific equivalence class.'} for k in range(0,len(pairs),12)]};full['unmatchedReviewQueue']=[{'batchId':f'scope-unmatched-{k//6:04d}','recordIds':[r['recordId'] for r in unmatched[k:k+6]],'meaning':'Review scientific parent/target and three weak nearest candidates; absence of nominations never certifies uniqueness.'} for k in range(0,len(unmatched),6)];text=json.dumps(full,separators=(',',':'));(a.out/'candidates.json').write_text(text)
 compact={'schemaVersion':'q025-global-scope-nomination-report/1','registryPath':str(a.registry),'registrySha256':sha(raw),'registryCreatedAt':registry['createdAt'],'scriptSha256':sha(Path(__file__).read_bytes()),'authoredScopes':len(records),'authoredQuestions':sum(r['kind']=='question' for r in records),'crossReviewSameKindPairsExamined':eligible_pairs,'candidatePairs':len(pairs),'scopesWithCandidates':sum(bool(v) for v in coverage.values()),'unmatchedScopes':len(unmatched),'candidateChannels':dict(collections.Counter(c for p in pairs for c in p['nominationChannels'])),'scopeStatuses':dict(collections.Counter(r['scopeStatus'] for r in records)),'screenedFactorExclusions':dict(factor_exclusions),'candidateFile':{'path':str(a.out/'candidates.json'),'sha256':sha(text.encode()),'bytes':len(text.encode())},'topCandidates':[{'id':p['id'],'records':[{'recordId':r,'title':known[r]['definition']['title'],'question':known[r]['definition']['question']} for r in p['recordIds']],'channels':p['nominationChannels'],'sharedUnitIds':p['sharedUnitIds'],'rankingScore':p['rankingScore']} for p in pairs[:30]],'unmatched':unmatched,'coverageMeaning':'Every current registry record is examined and explicitly accounted for. A nomination or absence of one never resolves identity. Candidate pairs remain queued until reviewed; new campaign records require a new pinned run.','limitations':['No embeddings, model calls, semantic entailment or automatic canonicalization.','Source reuse may be a comparison, compound target or outside probe; it does not establish equivalence or add geometric mass.','Factor label matches nominate comparisons only; even unflagged factor annotations are not independently certified premises.','All systems, regimes, exclusions and qualifications must be compared by review before equivalence or parent decisions.','High-weight broad vocabulary may still generate false positives; weak/unmatched scopes remain explicit review work.'],'sealedHoldout':'Only the evaluator registry was read; it declares exclusion of24reservedpapers. No sealed-source packet was opened.'}
 (a.out/'report.json').write_text(json.dumps(compact,indent=2)+'\n');print(json.dumps({k:v for k,v in compact.items() if k not in ['topCandidates','unmatched']},indent=2))
if __name__=='__main__':main()
