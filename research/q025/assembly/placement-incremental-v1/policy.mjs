import {scopeContentHash} from '../accepted.mjs';
/** Root's retained, whole-source existing-home class; no scope creation. */
export function assertExistingWholeHome(row,scopes,canonical){
  const a=row.proposalJudgment,b=row.challengeJudgment,review=row.independentPriorPlacementReview;
  if(a.status!=='existing_homes'||b.status!=='existing_homes'||review.verdict!=='retain')throw Error('Not an independently retained existing home');
  for(const r of [a,b])if(r.coverageMode!=='whole_question_per_home'||r.wholeTargetCoverage!=='complete'||r.missingPremises.length)throw Error('Whole-question coverage or premise gap');
  const assignments=r=>r.homes.map(h=>({scopeRef:h.scopeRef,weight:h.weight})).sort((x,y)=>x.scopeRef.localeCompare(y.scopeRef));
  if(JSON.stringify(assignments(a))!==JSON.stringify(assignments(b)))throw Error('Independent home or weight changed');
  if(!b.homes.length||b.homes.some(h=>!(h.weight>0))||Math.abs(b.homes.reduce((n,h)=>n+h.weight,0)-1)>1e-10)throw Error('Allocation is not normalized');
  for(const h of row.homes){const d=scopes.get(h.destinationId);if(!d||scopeContentHash(d)!==h.scopeContentSha256)throw Error('Exact current admitted scope changed');if(canonical(h.destinationId)!==h.destinationId)throw Error('Canonical placement requires separate revalidation');}
  if(row.homes.length!==b.homes.length||row.homes.some(h=>!b.homes.some(x=>x.scopeRef===h.scopeRef&&x.weight===h.weight)))throw Error('Unbound selected home');
  return true;
}
