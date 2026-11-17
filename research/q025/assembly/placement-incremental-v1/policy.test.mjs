import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {assertExistingWholeHome} from './policy.mjs';
const b=JSON.parse(readFileSync(new URL('./cut-01/source-bindings.local.json',import.meta.url))),base=JSON.parse(readFileSync(new URL('../organization-residual-v1/candidate-6117-canonical-v6/aggregate.local.json',import.meta.url))),scopes=new Map(base.destinations.map(d=>[d.id,d])),row=b.rows.find(r=>r.policyEligible);
test('actual unchanged complete-source placement meets the approved class',()=>assert.equal(assertExistingWholeHome(row,scopes,x=>x),true));
test('retained wording cannot override changed scope or missing premise',()=>{for(const mutate of [r=>r.homes[0].scopeContentSha256='0'.repeat(64),r=>r.challengeJudgment.missingPremises=['unread decisive premise'],r=>r.challengeJudgment.coverageMode='compound_union']){const r=structuredClone(row);mutate(r);assert.throws(()=>assertExistingWholeHome(r,scopes,x=>x));}});
test('a changed home or canonical transfer remains a separate decision',()=>{const r=structuredClone(row);r.proposalJudgment.homes[0].weight=.5;assert.throws(()=>assertExistingWholeHome(r,scopes,x=>x),/changed/);assert.throws(()=>assertExistingWholeHome(row,scopes,x=>x+'-replacement'),/separate revalidation/);});
