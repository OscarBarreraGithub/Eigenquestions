/** Extract bounded exact recorded relations for protocol tests; no science admission. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createAtlasContextReader,createAtlasSourceReader} from '../../../../lib/geometry/prepared-atlas.mjs';
const root=new URL('../../../../',import.meta.url),contextBase=new URL('research/q025/geometry/source-context-v3-compact/pack/',root),mappingPath='research/q025/geometry/relation-retrieval-v1/source-method-routes.json';
const mappingBytes=await readFile(new URL(mappingPath,root)),mappingHash=createHash('sha256').update(mappingBytes).digest('hex');if(mappingHash!=='2d3fc77b042d1dd1bfd42addded3edfcba41de625db1f1d5174ab5cce85b1bfc')throw new Error('Route mapping changed');
const mapping=JSON.parse(mappingBytes),pack=JSON.parse(await readFile(new URL('manifest.json',contextBase))),corpus=JSON.parse(await readFile(new URL('data/navigation/manifest.json',root)));
const atlas={catalog:{},manifest:{atlasId:'source-inspection-test',atlasVersion:'v1',corpusId:corpus.corpusId,corpusContentHash:corpus.contentHash,files:{sourceContextIndex:pack.sourceContextIndex}}};
const readContext=createAtlasContextReader(atlas,{base:contextBase.pathname,readText:filename=>readFile(filename,'utf8'),readBinary:filename=>readFile(filename)}),readSources=createAtlasSourceReader(atlas,{base:new URL('data/navigation/',root).pathname,readText:filename=>readFile(filename,'utf8')});
const cases=[],contexts={},sources={},routes={},units={};
for(const id of ['scientific:production-001','scientific:production-026','scientific:production-097']){
 const route=mapping.routes[id];routes[id]=route;const ids=[...route.sourceMethodUnitIds,...route.targetMethodUnitIds];
 for(const unitId of ids){units[unitId]=mapping.units[unitId];const context=await readContext(unitId),relation=context.sourceRelations.find(r=>r.id===id);if(!relation)throw new Error('Exact relation missing');
  contexts[unitId]={unitId,availability:'available',sourceContextFile:context.sourceContextFile,coverage:{description:'Explicit protocol fixture subset of a checksummed source context; not complete paper context.'},sourceObjects:context.sourceObjects.filter(o=>[relation.source,relation.target].includes(o.id)),sourceRelations:[relation],sourceAssessments:[],sourceEvidence:[],sourceAttachments:context.sourceAttachments.map(a=>({...a,objectIds:a.objectIds.filter(x=>[relation.source,relation.target].includes(x)),relationIds:a.relationIds.filter(x=>x===id)})).filter(a=>a.objectIds.length||a.relationIds.length)};
  const [row]=await readSources([mapping.units[unitId]]);sources[unitId]=row.source;
 }
 cases.push({relationId:id,originUnitId:route.sourceMethodUnitIds[0],sourceObjectId:route.sourceObjectId,targetObjectId:route.targetObjectId,sourceUnitId:route.sourceMethodUnitIds[0],targetUnitId:route.targetMethodUnitIds[0]});
}
const unmapped=mapping.routes['scientific:production-020'];routes[unmapped.id]=unmapped;
const originalFixtures=JSON.parse(await readFile(new URL('research/q025/geometry/relation-retrieval-v1/fixtures.json',root))),unmappedFixture=originalFixtures.fixtures.find(f=>f.route.id===unmapped.id);
const contextIndex=JSON.parse(await readFile(new URL(pack.sourceContextIndex.path,contextBase))),unmappedPaper=unmappedFixture.sourceRelation.endpoints.find(e=>e.id===unmapped.sourceObjectId).paper_id;let unmappedUnitId;
for(const descriptor of Object.values(contextIndex.unitIndex.shards)){const bucket=JSON.parse(await readFile(new URL(descriptor.path,contextBase)));unmappedUnitId=Object.keys(bucket.units).find(id=>bucket.units[id].shardId===unmappedPaper);if(unmappedUnitId)break;}
if(!unmappedUnitId)throw new Error('Unmapped endpoint paper has no context unit');
const fullUnmapped=await readContext(unmappedUnitId),unmappedRelation=fullUnmapped.sourceRelations.find(r=>r.id===unmapped.id);if(!unmappedRelation)throw new Error('Unmapped source relation missing');
const unmappedContext={unitId:unmappedUnitId,availability:'available',coverage:{description:'Explicit unmapped-endpoint protocol fixture.'},sourceObjects:fullUnmapped.sourceObjects.filter(o=>[unmapped.sourceObjectId,unmapped.targetObjectId].includes(o.id)),sourceRelations:[unmappedRelation],sourceAttachments:fullUnmapped.sourceAttachments.map(a=>({...a,objectIds:a.objectIds.filter(x=>[unmapped.sourceObjectId,unmapped.targetObjectId].includes(x)),relationIds:a.relationIds.filter(x=>x===unmapped.id)})).filter(a=>a.objectIds.length||a.relationIds.length),sourceAssessments:[],sourceEvidence:[],sourceContextFile:fullUnmapped.sourceContextFile};contexts[unmappedUnitId]=unmappedContext;
const out={schemaVersion:'q025-source-endpoint-protocol-fixtures/1',scope:'Real frozen source objects and reviewed relations in an explicitly incomplete protocol fixture. No new physical destination, membership or scientific admission.',mappingOrigin:{path:mappingPath,sha256:mappingHash},mapping:{schemaVersion:'1.0.0',kind:mapping.kind,routes,units},cases,contexts,sources,unmapped:unmappedFixture,unmappedContext};
await writeFile(new URL('./fixtures.json',import.meta.url),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({cases:cases.length,units:Object.keys(units).length,bytes:Buffer.byteLength(JSON.stringify(out))}));
