/** Review-only adapter for evaluation card drafts; never writes product data. */
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateAtlas,createAtlasNavigator} from '../../../lib/geometry/prepared-atlas.mjs';
const root=new URL('../../../',import.meta.url),out=new URL('./draft-atlas/',import.meta.url);
const draft=JSON.parse(await readFile(new URL('research/q025/evaluation/kk-question-card-drafts.json',root),'utf8'));
const corpus=JSON.parse(await readFile(new URL('data/navigation/manifest.json',root),'utf8'));
const papers=new Map(JSON.parse(await readFile(new URL('data/navigation/papers.json',root),'utf8')).map(p=>[p.id,p]));
const shardCache=new Map(),sources=[],sourceRows=new Map();
for(const reference of draft.sources){
  const descriptor=corpus.files.units.find(s=>reference.browserVectorRow>=s.start&&reference.browserVectorRow<s.start+s.count);
  if(!descriptor)throw new Error('Draft source lacks an exact frozen row');
  if(!shardCache.has(descriptor.path)){const bytes=await readFile(new URL(`data/navigation/${descriptor.path}`,root));if(createHash('sha256').update(bytes).digest('hex')!==descriptor.sha256)throw new Error('Frozen source shard mismatch');shardCache.set(descriptor.path,JSON.parse(bytes));}
  const unit=shardCache.get(descriptor.path)[reference.browserVectorRow-descriptor.start],paper=papers.get(unit.paperId);
  if(unit.id!==reference.id||unit.paperId!==reference.paperId)throw new Error('Draft source row mismatch');
  sources.push({id:unit.id,paperId:unit.paperId,title:paper.title,sourceUrl:paper.url,year:paper.year,evidence:{...unit.evidence,id:unit.id,text:unit.text,lens:unit.lens,date:paper.date},editorialReadingSummary:{text:reference.text,status:'draft source-reading summary; frozen source text retained separately'}});
  sourceRows.set(unit.id,{unitId:unit.id,browserVectorRow:reference.browserVectorRow,year:paper.year,lens:unit.lens,weight:1,role:'evidence'});
}
const destinations=structuredClone(draft.destinations).map(d=>{const paperIds=new Set(d.evidenceIds.map(id=>sources.find(s=>s.id===id)?.paperId));return {...d,membershipStatus:'representative',contextSourceIds:sources.filter(s=>paperIds.has(s.paperId)&&s.evidence.lens==='method').map(s=>s.id),scope:{...d.scope},provenance:{...d.provenance,localReviewOnly:true,methodContext:'Same-paper method facets are contextual reading, not an assertion that every method applies to this specific question.'}};});
const memberships=destinations.flatMap(d=>[...new Set((d.contributions||[]).map(c=>c.unitId).concat(d.evidenceIds))].map(id=>({destinationId:d.id,...sourceRows.get(id)})));
const relations=[],pairs=new Set();
for(const d of destinations)for(const targetId of d.proposedDirections||[]){const target=destinations.find(t=>t.id===targetId);if(!target)throw new Error('Draft proposed direction absent');const pair=[d.id,targetId].sort().join('|');if(pairs.has(pair))continue;pairs.add(pair);relations.push({id:`draft-connection-${relations.length+1}`,source:d.id,target:targetId,type:'related_question',evidenceIds:[...new Set([...d.evidenceIds,...target.evidenceIds])],rationale:'Proposed comparison between distinct scoped questions in the source-reading draft. This navigation proposal is not a physical implication or an accepted equivalence.',status:'draft_navigation_proposal_pending_challenge',provenance:{request:'Q-025',source:'evaluation/kk-question-card-drafts.json',field:'proposedDirections'}});}
const catalog={destinations,sources,memberships,relations};
const catalogText=JSON.stringify(catalog);
const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'kk-source-reading-draft',atlasVersion:'2026-11-17-local-review',corpusId:corpus.corpusId,corpusContentHash:corpus.contentHash,entryDestinationId:'q-kk-graviton-thermal-production',snapshotDate:corpus.snapshotDate,scope:{description:'Local source-reading draft for scientific and interface review.',limitations:['Canonical identities and connections are draft proposals awaiting independent challenge. This is not the accepted atlas release.','Representative source membership; not exhaustive literature coverage.'],paperCount:new Set(sources.map(s=>s.paperId)).size,earliestYear:Math.min(...sources.map(s=>s.year)),latestYear:Math.max(...sources.map(s=>s.year))},files:{catalog:{path:'catalog.json',sha256:createHash('sha256').update(catalogText).digest('hex')}}},manifestText=JSON.stringify(manifest);
await mkdir(out,{recursive:true});
const contextRoot=new URL('research/q025/geometry/compact-source-context-pack/',root),contextInput=await readFile(new URL('source-context-index.json',contextRoot),'utf8'),contextIndex=JSON.parse(contextInput);
const units=Object.fromEntries(sources.filter(s=>contextIndex.units[s.id]).map(s=>[s.id,contextIndex.units[s.id]]));
const localContext={...contextIndex,coverage:{...contextIndex.coverage,localReviewSubset:true,description:'Exact source context for the listed local draft sources only; direct relations and contextual co-occurrence remain distinct.'},units};
for(const file of new Set(Object.values(units).map(d=>d.path)))await copyFile(new URL(file,contextRoot),new URL(file,out));
const contextText=JSON.stringify(localContext);await writeFile(new URL('source-context-index.json',out),contextText);
manifest.files.sourceContextIndex={path:'source-context-index.json',sha256:createHash('sha256').update(contextText).digest('hex')};
const finalManifestText=JSON.stringify(manifest),atlas={manifest,catalog,manifestSha256:createHash('sha256').update(finalManifestText).digest('hex')};
validateAtlas(manifest,catalog);const navigator=createAtlasNavigator(atlas);navigator.computeView(navigator.createSession().states[0]);
await writeFile(new URL('manifest.json',out),finalManifestText);await writeFile(new URL('catalog.json',out),catalogText);
await writeFile(new URL('receipt.json',out),JSON.stringify({kind:'local-review-draft',notApprovedForSiteRelease:true,inputSha256:createHash('sha256').update(await readFile(new URL('research/q025/evaluation/kk-question-card-drafts.json',root))).digest('hex'),manifestSha256:atlas.manifestSha256,catalogSha256:manifest.files.catalog.sha256,destinations:destinations.length,sources:sources.length,relations:relations.length},null,2)+'\n');
console.log(JSON.stringify({out:out.pathname,destinations:destinations.length,sources:sources.length,relations:relations.length,status:'local review draft only'}));
