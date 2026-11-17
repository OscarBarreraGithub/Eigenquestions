/** Read-only runtime check of the actual two admitted KK contribution components. */
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadAtlas,createAtlasNavigator} from '../../../../lib/geometry/prepared-atlas.mjs';
const root=resolve(fileURLToPath(new URL('../../../../',import.meta.url))),base=resolve(root,'research/q025/assembly/outputs/organization-candidate-6030-navigation-v2');
const read=async path=>JSON.parse(await readFile(path,'utf8')),sha=async path=>createHash('sha256').update(await readFile(path)).digest('hex');
const paths=['research/q025/evaluation/full-pass/organization-placement-v1/kk-uhecr-admitted-rehearsal-component.json','research/q025/evaluation/full-pass/navigation-admissions-v1/kk-component.json'];
const components=await Promise.all(paths.map(path=>read(resolve(root,path)))),rows=components.flatMap(c=>c.sourceContributions),expected=new Map(rows.map(row=>[[row.decisionId,row.unitId,row.destinationId,row.role].join('\n'),row]));assert.equal(rows.length,38);assert.equal(expected.size,38);
const relationKey=row=>[row.unitId,row.destinationId,row.role].join('\n'),relationships=new Map();for(const row of rows){const k=relationKey(row);if(!relationships.has(k))relationships.set(k,[]);relationships.get(k).push(row);}assert.equal(relationships.size,32);assert.equal([...relationships.values()].filter(rows=>rows.length===2).length,6);
const atlas=await loadAtlas(base,{readText:path=>readFile(path,'utf8')}),navigator=createAtlasNavigator(atlas),verified=[],destinations=[];
for(const id of new Set(rows.map(row=>row.destinationId))){
 await navigator.prepareDestination(id);const d=navigator.destination(id),observations=d.sourceContributions||[];const counts={observations:observations.length,relationships:new Set(observations.map(row=>[row.unitId,row.role].join('\n'))).size};
 assert.equal(d.sourceContributionObservationCount,counts.observations);assert.equal(d.sourceContributionRelationshipCount,counts.relationships);
 let offset=0;do{const page=navigator.sources(id,{collection:'contributions',offset,limit:100});assert.equal(page.observationCount,counts.observations);assert.equal(page.relationshipCount,counts.relationships);for(const row of page.items){const key=[row.decisionId,row.unitId,row.destinationId,row.role].join('\n'),original=expected.get(key);if(!original)continue;for(const [k,value]of Object.entries(original))assert.deepEqual(row[k],value);verified.push(key);}offset+=page.items.length;if(!page.items.length)break;}while(offset<counts.observations);
 await navigator.prepareSources(id);const membershipBefore=navigator.sources(id),usingBefore=navigator.sources(id,{workRelation:'using'});navigator.sources(id,{collection:'contributions'});assert.deepEqual(navigator.sources(id),membershipBefore);assert.deepEqual(navigator.sources(id,{workRelation:'using'}),usingBefore);
 destinations.push({destinationId:id,...counts,membershipCount:membershipBefore.total,usingCount:usingBefore.total});
}
assert.equal(new Set(verified).size,38);
const report={schemaVersion:'q025-real-contribution-observation-check/1',passed:true,admittedObservationRows:38,distinctScopedSourceRoleRelationships:32,repeatedRelationships:6,originalQualifiedRowsPreserved:true,contributionReadDoesNotChangeMembershipOrUsing:true,declaredDestinationCountsMatch:true,inputs:await Promise.all(paths.concat(['lib/geometry/prepared-atlas.mjs','research/q025/assembly/outputs/organization-candidate-6030-navigation-v2/manifest.json','research/q025/assembly/outputs/organization-candidate-6030-navigation-v2/catalog.json']).map(async path=>({path,sha256:await sha(resolve(root,path))}))),destinations,limits:['Actual admitted component transport checked through the shared lazy navigator; this partial candidate is not an installable complete atlas.','No new scientific admission, source reading, browser rendering or public HTTPS claim.']};
await writeFile(new URL('./real-observation-report.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,observations:38,relationships:32,repeats:6,destinations:destinations.length}));
