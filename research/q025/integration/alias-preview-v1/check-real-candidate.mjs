/** Read-only real partial-candidate checks; no installation or scientific admission. */
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {loadAtlas,createAtlasNavigator,atlasAddress} from '../../../../lib/geometry/prepared-atlas.mjs';
const root=fileURLToPath(new URL('../../../../',import.meta.url)),base=resolve(root,process.argv[2]||'research/q025/assembly/outputs/organization-candidate-6030-connected-v4');
const sha=async path=>createHash('sha256').update(await readFile(path)).digest('hex');
const atlas=await loadAtlas(base,{readText:path=>readFile(path,'utf8')}),nav=createAtlasNavigator(atlas),redirects=[];
for(const [formerId,canonicalId] of Object.entries(atlas.catalog.destinationAliases||{})){
 await nav.prepareDestination(formerId);const former=nav.createSession({selector:{...nav.initialState.selector,destinationId:formerId}}),canonical=nav.createSession({selector:{...nav.initialState.selector,destinationId:canonicalId}});
 assert.deepEqual(former,canonical);assert.equal(atlasAddress(former.states[0]),atlasAddress(canonical.states[0]));
 const record=nav.destination(formerId);assert.equal(record.id,canonicalId);assert.ok(record.scopedIdentity.originalDefinitions.some(d=>d.id===formerId));assert.equal(record.scopedIdentity.sourceStatementEquivalence,false);
 redirects.push({formerId,canonicalId,stateId:former.states[0].id,originalDefinitions:record.scopedIdentity.originalDefinitions.map(d=>d.id),readingLimitsPreserved:true});
}
assert.equal(redirects.length,4);
const indexed=new Map(atlas.catalog.destinations.map(d=>[d.id,d])),reviewHistoryCandidates=atlas.catalog.destinations.filter(d=>d.summary?.startsWith('No original verbal scientific scope'));
const menus=[];
for(const target of reviewHistoryCandidates){
 const edge=atlas.catalog.relations.find(r=>r.target===target.id||r.source===target.id);if(!edge)continue;
 const current=edge.source===target.id?edge.target:edge.source;if(!indexed.has(current))continue;await nav.prepareDestination(current);
 const state=nav.createSession({selector:{...nav.initialState.selector,destinationId:current}}).states[0],view=nav.computeView(state);
 const direction=view.directions.find(d=>d.selector.destinationId===target.id);if(!direction)continue;
 assert.equal(direction.summary,target.question??target.title);assert.notEqual(direction.summary,target.summary);
 menus.push({currentId:current,targetId:target.id,choiceTitle:direction.label,subtitle:direction.summary,rawReviewHistoryRetained:target.summary});if(menus.length===3)break;
}
assert.ok(menus.length,'real broad-parent choice must be exercised');
await nav.prepareSearch();const search=[];
for(const row of menus){const target=indexed.get(row.targetId),results=nav.search(target.title,{limit:30}),result=results.find(d=>d.id===target.id);assert.ok(result);assert.equal(result.summary,target.question??target.title);await nav.prepareDestination(target.id);assert.equal(nav.destination(target.id).summary,target.summary);search.push({destinationId:target.id,title:result.title,subtitle:result.summary,lookupKind:result.matchKind});}
const report={schemaVersion:'q025-real-alias-preview-check/1',passed:true,partialCandidate:true,publicInstall:false,redirects,broadParentChoices:menus,search,inputs:await Promise.all(['manifest.json','catalog.json'].map(async path=>({path:relative(root,resolve(base,path)),sha256:await sha(resolve(base,path))}))),runtime:await Promise.all(['lib/geometry/prepared-atlas.mjs','lib/protocol/display-editorial.mjs'].map(async path=>({path,sha256:await sha(resolve(root,path))}))),limits:['Read-only shared runtime check on the actual partial candidate; no browser or public HTTPS claim.','Compact previews select the exact scientific question. Raw scientific definitions, scope hashes and reading records remain unchanged.','This does not admit identities or broaden the four already admitted redirect entries.']};
await writeFile(new URL('./real-candidate-report.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,redirects:redirects.length,broadParentChoices:menus.length,lexicalResults:search.length}));
