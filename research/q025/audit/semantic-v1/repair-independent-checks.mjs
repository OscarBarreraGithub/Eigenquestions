/** Independent repair verification; does not modify original audit or owner files. */
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {fixtureInput} from '../../assembly/fixture.mjs';
import {sha256,readPinnedJson,loadFrozenCorpus} from '../../assembly/corpus.mjs';
import {assembleAccepted,scopeContentHash} from '../../assembly/accepted.mjs';
import {identityInventoryHash,canonicalIdentityGroupHash} from '../../assembly/fine-identities.mjs';
import {verifyPrimaryEvidence} from '../../assembly/primary-evidence.mjs';

const root=fileURLToPath(new URL('../../../../',import.meta.url));
const manifest=await readPinnedJson(resolve(root,'research/q025/assembly/semantic-repair-v1/manifest.json'),'213a8c01419a0c5aa23d73d07c92c19e8ceea2ebdddbb28d1afdc0d06107053f');
const verified=[],externalPinMismatches=[];
for(const descriptor of [...manifest.value.files,...manifest.value.externalEvidence,manifest.value.runtime]){
  const bytes=await readFile(resolve(root,descriptor.path));
  if((descriptor.path.startsWith('tests/')||descriptor.path===manifest.value.runtime.path)&&(sha256(bytes)!==descriptor.sha256||bytes.length!==descriptor.bytes)){
    externalPinMismatches.push({path:descriptor.path,expectedSha256:descriptor.sha256,actualSha256:sha256(bytes),expectedBytes:descriptor.bytes,actualBytes:bytes.length});continue;
  }
  assert.equal(sha256(bytes),descriptor.sha256,descriptor.path);assert.equal(bytes.length,descriptor.bytes,descriptor.path);
  verified.push(descriptor.path);
}

function fixture(){
  const x=fixtureInput();x.packet.reviewRegistry.push({id:'review:challenge',sha256:'b'.repeat(64)});
  const original=x.packet.destinations.find(d=>d.id==='destination:fine');
  const d={...structuredClone(original),id:'destination:second',title:'Second synthetic question scope',scopeDecisionId:'decision:second-scope'};
  x.packet.destinations.push(d);
  x.packet.decisions.push({...structuredClone(x.packet.decisions.find(p=>p.id===original.scopeDecisionId)),id:d.scopeDecisionId,subjectIds:[d.id],scopeContentSha256:scopeContentHash(d)});
  x.packet.identityResolution={registry:{path:'synthetic-registry.json',sha256:'c'.repeat(64)},records:['A','B','C','D','E','F','G','H'].map(id=>({id,contentSha256:sha256(id)})),comparisons:[],canonicalGroups:[]};
  return x;
}
function compare(x,id,operation,members,definingDifferences=[]){
  x.packet.identityResolution.comparisons.push({id,operation,members,target:members.at(-1),definingDifferences,sourceReviewIds:['review:fixture','review:challenge'],evidenceRefs:[{kind:'description',id:'unit:q1'}]});
}
function group(x,id,memberIds,destinationId){
  const r=x.packet.identityResolution,d=x.packet.destinations.find(d=>d.id===destinationId),scope=scopeContentHash(d),inventory=identityInventoryHash(r),g={id,memberIds,destinationId,decisionId:`decision:${id}`};
  r.canonicalGroups.push(g);
  x.packet.decisions.push({id:g.decisionId,type:'question_equivalence',status:'accepted',outcome:'equivalent_as_scoped',subjectIds:[destinationId,...memberIds],sourceReviewIds:['review:fixture','review:challenge'],evidenceRefs:[{kind:'description',id:'unit:q1'}],challengerAgreement:'independently_agreed',changedPremises:[],canonicalDestinationId:destinationId,scopeContentSha256:scope,identityInventorySha256:inventory,identityGroupContentSha256:canonicalIdentityGroupHash(g,scope,inventory),reviewAgreement:{proposalReviewId:'review:fixture',challengeReviewId:'review:challenge'}});
}
const identityChecks=[];
for(const operation of ['different','specializes','shared_parent_distinct','unresolved','comparison'])for(const reverse of [false,true]){
  const x=fixture();
  compare(x,'ab','same_scoped_question',['A','B']);compare(x,'cd','same_scoped_question',['C','D']);compare(x,'ef','same_scoped_question',['E','F']);
  compare(x,'be',operation,['B','E'],operation==='comparison'?['Changed defining premise']:[]);
  const groups=[['group:AC',['A','C'],'destination:fine'],['group:DF',['D','F'],'destination:second']];
  if(reverse)groups.reverse();for(const args of groups)group(x,...args);
  assert.throws(()=>assembleAccepted(x),error=>error.identityConflictQueue?.transitiveConflicts.some(c=>c.constraintComparisonId==='be'&&c.canonicalGroupIds.length===2));
  identityChecks.push({case:'two-group-positive-path-closure',operation,reverseGroupOrder:reverse,rejected:true});
}
{
  const x=fixture();compare(x,'bc','common_target',['B','C']);compare(x,'ad','different',['A','D']);
  group(x,'group:AB',['A','B'],'destination:fine');group(x,'group:CD',['C','D'],'destination:second');
  const result=assembleAccepted(x).catalog.organizationProvenance.identityResolution;
  assert.equal(result.groups.length,2);assert.equal(result.unresolvedConflicts.length,0);assert.equal(result.automaticUnions,0);
  identityChecks.push({case:'common-target-does-not-join-distinct-canonical-groups',accepted:true,groups:result.groups.map(g=>({memberIds:g.memberIds,destinationId:g.destinationId})),automaticUnions:result.automaticUnions});
}
{
  const x=fixture();compare(x,'gh-positive','same_scoped_question',['G','H']);compare(x,'gh-negative','different',['G','H']);group(x,'group:AB',['A','B'],'destination:fine');
  const result=assembleAccepted(x).catalog.organizationProvenance.identityResolution;
  assert.equal(result.groups.length,1);assert.equal(result.unresolvedConflicts.length,1);assert.deepEqual(result.unresolvedConflicts[0].memberIds,['G','H']);
  identityChecks.push({case:'unrelated-conflict-remains-visible-without-blocking-disjoint-group',accepted:true,unresolvedMemberIds:result.unresolvedConflicts[0].memberIds});
}
{
  const x=fixture();compare(x,'ac','specializes',['A','C'],['Extra controlled limit']);group(x,'group:ABCD',['A','B','C','D'],'destination:fine');
  assert.throws(()=>assembleAccepted(x),/recorded distinction, specialization/);
  identityChecks.push({case:'one-complete-destination-group-still-honors-specialization',rejected:true});
}

// The only real archive reads are the 13 already-inspected, unsealed locators.
const corpus=await loadFrozenCorpus(resolve(root,'data/navigation'));
const audit=await readPinnedJson(resolve(root,'research/q025/assembly/cross-leaf-semantics-audit-v1.json'),'9c5f19dfc2b3fc80a20665a49d28e9850a3534e944dd925a14507ea6969a2489');
const contextRoot=resolve(root,'research/q025/geometry/source-context-v3-compact/pack');
const context=await readPinnedJson(resolve(contextRoot,'manifest.json'),'c86bc90966007c28ce40523348e51e4ace4d20d62354f79928133d371f77c6f5');
const primary=await verifyPrimaryEvidence({references:audit.value.inspectedPrimaryLocators,corpus,archiveRoot:'/Users/emmy/Developer/physics-atlas-swampland',contextRoot,contextManifest:context.value});
assert.equal(primary.report.distinctLocators,13);assert.equal(primary.report.files.length,5);assert.equal(primary.report.rawPrimaryTextExported,false);
console.log(JSON.stringify({repairManifestSha256:manifest.sha256,verifiedPinnedFiles:verified,externalPinMismatches,identityChecks,realPrimaryEvidence:{referenceCount:primary.report.referenceCount,distinctLocators:primary.report.distinctLocators,archiveFileCount:primary.report.files.length,sourceSummarySha256:primary.report.sourceSummarySha256,locatorFingerprints:primary.report.records.map(r=>r.fingerprint),rawPrimaryTextExported:false}},null,2));
