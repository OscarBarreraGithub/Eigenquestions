import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateNavigationBinding} from './accepted.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const read=p=>JSON.parse(readFileSync(resolve(root,p)));
const base=read('research/q025/evaluation/full-pass/admissions-v5/supported-scope-role-component-v5.json');
const stable=read('research/q025/evaluation/full-pass/organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json');
const components=['inflation','amplitude','kk'].map(name=>read(`research/q025/evaluation/full-pass/navigation-admissions-v1/${name}-component.json`));
const dest=new Map([base,stable,...components].flatMap(c=>c.destinations||[]).map(d=>[d.id,d]));
function input(c,row){const proof=c.decisions.find(d=>d.id===row.decisionId),reviewRecords=new Map(c.reviewRegistry.map(r=>[r.id,r])),verifiedReceiptHashes=new Set(c.reviewRegistry.map(r=>r.sha256));if(proof.adjudication)verifiedReceiptHashes.add(proof.adjudication.receipt.sha256);return {row:structuredClone(row),proof:structuredClone(proof),source:structuredClone(dest.get(row.source)),target:structuredClone(dest.get(row.target)),reviewRecords,verifiedReceiptHashes};}
test('all43 actual admitted navigation records bind exact displayed fields and scopes',()=>{
  let count=0;for(const c of [stable,...components])for(const row of c.relations){validateNavigationBinding(input(c,row));count++;}assert.equal(count,43);
});
for(const [name,mutate,pattern] of [
  ['outgoing label',x=>{x.row.title+=' changed';},/content changed/],
  ['qualification',x=>{x.row.qualification='Universal claim';},/content changed/],
  ['incoming label',x=>{x.row.incomingTitle='Invented reverse assertion';},/content changed/],
  ['direction',x=>{[x.row.source,x.row.target]=[x.row.target,x.row.source];},/content changed/],
  ['scope',x=>{x.target.scope.assumptions.push('Changed premise');},/scope changed/],
  ['receipt',x=>{x.verifiedReceiptHashes.clear();},/not verified/],
])test(`rejects changed actual navigation ${name}`,()=>{const x=input(components[0],components[0].relations[0]);mutate(x);assert.throws(()=>validateNavigationBinding(x),pattern);});
test('legacy KK receipt cannot authorize a new unbound qualification',()=>{const x=input(stable,stable.relations[0]);x.row.qualification='Unreviewed premise transfer';assert.throws(()=>validateNavigationBinding(x),/content changed/);});
test('coordinator title correction requires its exact receipt',()=>{const c=components[2],row=c.relations.find(r=>r.provenance.explicitTitleCopyedit),x=input(c,row);x.verifiedReceiptHashes.delete(x.proof.adjudication.receipt.sha256);assert.throws(()=>validateNavigationBinding(x),/coordinator receipt/);});
test('coordinator adjudication cannot be relabeled as independent paired approval',()=>{const c=components[2],row=c.relations.find(r=>r.provenance.explicitTitleCopyedit),x=input(c,row);x.proof.challengerAgreement='independently_agreed';assert.throws(()=>validateNavigationBinding(x),/coordinator adjudication cannot claim/);});
