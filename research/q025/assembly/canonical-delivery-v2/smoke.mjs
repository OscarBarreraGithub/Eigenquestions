import {readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname,join,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {loadAtlas,createAtlasNavigator} from '../../../../lib/geometry/prepared-atlas.mjs';
import {sha256} from '../corpus.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),base=join(root,'research/q025/assembly/outputs/organization-candidate-6117-canonical-v6');
const loaded=await loadAtlas(base,{readText:p=>readFile(p,'utf8')}),nav=createAtlasNavigator(loaded),aliases=[];
for(const [oldId,canonicalId]of Object.entries(loaded.catalog.destinationAliases)){
  await nav.prepareDestination(oldId);await nav.prepareDestination(canonicalId);
  const oldSession=nav.createSession({selector:{...nav.initialState.selector,destinationId:oldId}}),canonicalSession=nav.createSession({selector:{...nav.initialState.selector,destinationId:canonicalId}});
  assert.deepEqual(oldSession,canonicalSession);assert.deepEqual(nav.destination(oldId),nav.destination(canonicalId));assert.deepEqual(nav.connections(oldId),nav.connections(canonicalId));
  const d=nav.destination(canonicalId);assert.ok(d.scopedIdentity.originalDefinitions.some(x=>x.id===oldId));aliases.push({oldId,canonicalId,retainedDefinitions:d.scopedIdentity.originalDefinitions.length,identicalState:true});
}
assert.equal(aliases.length,7);
const raw=await readFile(join(base,'accepted-geometry-input.json')),geometry=JSON.parse(raw),sums=new Map();for(const a of geometry.allocations)sums.set(a.unitId,(sums.get(a.unitId)||0)+a.weight);assert.equal(sums.size,6117);assert.ok([...sums.values()].every(x=>Math.abs(x-1)<1e-12));
for(const prefix of ['unit:97dbf3eb','unit:e8cc19c9']){const rows=geometry.allocations.filter(r=>r.unitId.startsWith(prefix));assert.equal(rows.length,1);assert.equal(rows[0].destinationId,'q025-candidate-question:b6a72d6d11c8f9c783284067');assert.equal(rows[0].weight,1);}
const report={schemaVersion:'q025-canonical-real-package-smoke/1',packagePath:relative(root,base),manifestSha256:loaded.manifestSha256,geometryInputSha256:sha256(raw),aliases,allocatedSources:sums.size,maximumAllocationError:Math.max(...[...sums.values()].map(x=>Math.abs(x-1))),explicitRevalidatedHomeCount:2,newPrimaryReading:false,browserQA:false,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};await writeFile(join(here,'smoke.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({redirects:aliases.length,allocatedSources:sums.size,maximumAllocationError:report.maximumAllocationError,passed:true}));
