import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {sha256} from './corpus.mjs';
import {fixtureInput} from './fixture.mjs';
import {assembleAccepted,scopeContentHash,sourceContributionContentHash} from './accepted.mjs';
import {verifyPrimaryEvidence} from './primary-evidence.mjs';

async function primaryFixture(t){
  const directory=await mkdtemp(join(tmpdir(),'q025-primary-'));t.after(()=>rm(directory,{recursive:true,force:true}));
  const archiveRoot=join(directory,'archive'),contextRoot=join(directory,'context');await mkdir(archiveRoot);await mkdir(contextRoot);
  async function json(root,path,value){const text=JSON.stringify(value);await writeFile(join(root,path),text);return {path,sha256:sha256(text),bytes:Buffer.byteLength(text)};}
  const x=fixtureInput(),sourceSha256='a'.repeat(64),page='A🧪Bounded primary source text';x.corpus.papers.get('p2').sourceSha256=sourceSha256;
  const reading=await json(archiveRoot,'reading-order.json',{source_sha256:sourceSha256,pages:[page]});
  const ref={kind:'primary',paperId:'p2',sourceId:'ev:abcdef',sourceSha256,sourceContext:{path:reading.path,fileSha256:reading.sha256,pdfPage:1,start:2,end:9,textSha256:sha256(Array.from(page).slice(2,9).join(''))}};
  const shard=await json(contextRoot,'context.json',{sourceEvidence:[{id:'source-graph:ev:abcdef',paperId:'p2',sourceSha256,page:1}]});
  const summary=await json(contextRoot,'summary.json',{papers:{p2:{fullContext:shard}}});
  const verification={references:[ref],corpus:x.corpus,archiveRoot,contextRoot,contextManifest:{sourceContextSummary:summary}};
  x.packet.reviewRegistry.push({id:'review:challenge',sha256:'b'.repeat(64)});
  const d=x.packet.destinations.find(d=>d.id==='destination:fine'),row={unitId:'unit:q3',destinationId:d.id,role:'comparison',basis:'source_excerpt_checked',evidenceRefs:[ref],decisionId:'decision:primary'};
  x.packet.sourceContributions=[row];x.packet.decisions.push({id:row.decisionId,type:'source_contribution',status:'accepted',subjectIds:[row.unitId,row.destinationId],sourceReviewIds:['review:fixture','review:challenge'],evidenceRefs:row.evidenceRefs,scopeContentSha256:scopeContentHash(d),contributionContentSha256:sourceContributionContentHash(row,scopeContentHash(d)),challengerAgreement:'independently_agreed',reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:challenge'}});
  return {x,ref,row,verification};
}
test('exact source ID, archived file, page and Unicode-codepoint span resolve before excerpt admission',async t=>{
  const {x,verification}=await primaryFixture(t),verified=await verifyPrimaryEvidence(verification);x.verifiedPrimaryLocators=verified.verifiedLocators;assert.equal(verified.report.distinctLocators,1);assert.equal(verified.report.rawPrimaryTextExported,false);assert.equal(assembleAccepted(x).catalog.sourceContributions[0].basis,'source_excerpt_checked');
});
test('independent audit: arbitrary primary ID is not a source locator even with bound review hashes',async t=>{
  const {x,row}=await primaryFixture(t);row.evidenceRefs=[{kind:'primary',paperId:'p2',id:'not-a-locator'}];x.packet.decisions.at(-1).contributionContentSha256=sourceContributionContentHash(row,x.packet.decisions.at(-1).scopeContentSha256);assert.throws(()=>assembleAccepted(x),/exact resolved primary locator/);
});
test('complete-looking but unresolved primary metadata cannot pass fixture or production component gate',async t=>{
  const {x}=await primaryFixture(t);assert.throws(()=>assembleAccepted(x),/exact resolved primary locator/);
});
test('a valid archive page cannot validate an invented source evidence ID',async t=>{
  const {ref,verification}=await primaryFixture(t);ref.sourceId='ev:ffffff';await assert.rejects(verifyPrimaryEvidence(verification),/source ID\/paper\/page/);
});
test('wrong character offsets cannot borrow a valid span hash',async t=>{
  const {ref,verification}=await primaryFixture(t);ref.sourceContext.start=3;await assert.rejects(verifyPrimaryEvidence(verification),/span\/hash mismatch/);
});
test('modified archived bytes fail the pinned file check',async t=>{
  const {ref,verification}=await primaryFixture(t);await writeFile(join(verification.archiveRoot,ref.sourceContext.path),'{"pages":["changed"]}');await assert.rejects(verifyPrimaryEvidence(verification),/checksum mismatch/);
});
