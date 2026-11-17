/** A local transport fixture using exact source records; never an accepted atlas. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {createHash} from 'node:crypto';
const root=new URL('../../../../',import.meta.url),fixture=JSON.parse(await readFile(new URL('./fixtures.json',import.meta.url))),corpus=JSON.parse(await readFile(new URL('data/navigation/manifest.json',root)));
const out=resolve(process.argv[2]);await mkdir(out,{recursive:true});
const json=async(name,value)=>{const text=JSON.stringify(value);await writeFile(join(out,name),text);return {path:name,bytes:Buffer.byteLength(text),sha256:createHash('sha256').update(text).digest('hex')};};
const units={};for(const [id,context]of Object.entries(fixture.contexts))units[id]=await json(`context-${id.slice(5,21)}.json`,context);
const sourceContextIndex=await json('source-context-index.json',{schemaVersion:'1.0.0',kind:'eigenquestions-source-context-index',units}),sourceMethodRoutes=await json('source-method-routes.json',fixture.mapping);
const catalog={destinations:[{id:'physics',kind:'region',metadataOnly:true,title:'Physics · source inspection test',question:'Inspect a recorded source method without changing the physical destination.',summary:'Protocol test with exact reviewed source objects. This is not an accepted scientific atlas or a claim that every inspected method applies to this destination.',scope:{assumptions:[]},evidenceIds:[],scientificStatus:'protocol fixture',placementStatus:'metadata-only',provenance:{fixture:true}}],sources:[],memberships:[],relations:[]};
const catalogFile=await json('catalog.json',catalog),manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'q025-source-endpoint-qa',atlasVersion:'2026-11-17-protocol-v1',corpusId:corpus.corpusId,corpusContentHash:corpus.contentHash,entryDestinationId:'physics',scope:{description:'Local source-endpoint protocol fixture; exact source records, no full scientific admission.',limitations:['Not accepted release data']},files:{catalog:catalogFile,sourceContextIndex,sourceMethodRoutes}};
await json('manifest.json',manifest);await json('fixture-cases.json',fixture.cases);console.log(JSON.stringify({directory:out,manifestSha256:createHash('sha256').update(JSON.stringify(manifest)).digest('hex'),sourceUnitContexts:Object.keys(units).length}));
