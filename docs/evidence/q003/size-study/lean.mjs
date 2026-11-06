import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {deflateRawSync,brotliCompressSync,constants} from 'node:zlib';
import {loadLocalNavigator} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/runtime.mjs';
import {currentState} from '/Users/emmy/Documents/Eigenquestions/lib/protocol/session.mjs';
const directory='/private/tmp/eigenquestions-q003-size-study-20261106';
const report=JSON.parse(await readFile(`${directory}/report.json`,'utf8'));
const original=JSON.parse(await readFile(`${directory}/axion-ede-snapshot.json`,'utf8'));
const {navigator,corpus}=await loadLocalNavigator();
const omittedNodeFields=['paperId','title','label','sourceUrl','year','date','lens','evidence'];
const lean={measurementFormat:'source-referencing-computed-view-experiment',continuationState:currentState(original.session),view:{...original.view,nodes:original.view.nodes.map(node=>Object.fromEntries(Object.entries(node).filter(([key])=>!omittedNodeFields.includes(key)))),chart:{...original.view.chart,groupCentroids:original.view.chart.groupCentroids.map(({centroid,...rest})=>rest)}}};
// Static fields come from the pinned corpus by ID, not regenerated text.
const sourceEvidence=new Map(navigator.getEvidence(lean.view.nodes.map(n=>n.id)).map(e=>[e.id,e]));
const restoredNodes=lean.view.nodes.map(node=>{const e=sourceEvidence.get(node.id);return {id:node.id,paperId:e.paperId,title:e.title,label:e.text,x:node.x,y:node.y,residual:node.residual,inSlab:node.inSlab,score:node.score,sourceUrl:e.url,year:e.year,date:e.date,lens:e.lens,evidence:e,retrieval:node.retrieval,directionId:node.directionId};});
const byId=new Map(restoredNodes.map(node=>[node.id,node]));
const unitsById=new Map(corpus.units.map(unit=>[unit.id,unit]));
// Repeat the engine's existing weighted-mean formula and member order. No new
// grouping, plane fitting, source selection or numerical approximation occurs.
const dimension=corpus.manifest.encoder.dimensions;
const restoredCentroids=lean.view.chart.groupCentroids.map(group=>{
  const ids=lean.view.directions.find(d=>d.id===group.directionId).memberIds;
  const centroid=Array(dimension).fill(0);let mass=0;
  for(const id of ids){const weight=byId.get(id).score,row=unitsById.get(id).vectorRow;mass+=weight;for(let j=0;j<dimension;j++)centroid[j]+=weight*corpus.vectors[row*dimension+j];}
  return {directionId:group.directionId,centroid:centroid.map(x=>x/(mass||1)),mass:group.mass,sourceCount:group.sourceCount,withinGroupVariance:group.withinGroupVariance};
});
const restored={...lean.view,nodes:restoredNodes,chart:{...lean.view.chart,groupCentroids:restoredCentroids}};
const exactlyEqual=JSON.stringify(restored)===JSON.stringify(original.view);
if(!exactlyEqual)throw Error('Lean hydration differs from original computed view');
const raw=Buffer.from(JSON.stringify(lean)),deflate=deflateRawSync(raw,{level:9}),brotli=brotliCompressSync(raw,{params:{[constants.BROTLI_PARAM_QUALITY]:11}});
const prefix='https://eigenquestions.com/#recipe=',b64=value=>value.toString('base64url').length,budget=length=>[4096,8192,16384].find(limit=>length<=limit)??null;
const sizes={jsonBytes:raw.length,rawBase64urlBytes:b64(raw),deflateBytes:deflate.length,deflateBase64urlBytes:b64(deflate),brotliBytes:brotli.length,brotliBase64urlBytes:b64(brotli),rawWholeUrlBytes:prefix.length+b64(raw),deflateWholeUrlBytes:prefix.length+b64(deflate),brotliWholeUrlBytes:prefix.length+b64(brotli),smallestBudgetBytes:{raw:budget(prefix.length+b64(raw)),deflate:budget(prefix.length+b64(deflate)),brotli:budget(prefix.length+b64(brotli))}};
const result={input:'axion-ede-snapshot.json',sizes,counts:{sources:lean.view.nodes.length,groups:lean.view.directions.length,edges:lean.view.edges.length},retained:'All selected IDs/order, all dynamic source fields/scores/work relations, all graph edges/types/weights/evidence links, all directions with exact labels/queries/members/seeds/properties, complete affine plane center+basis and projection diagnostics/warnings, normalized continuation state and computation/corpus identities.',omitted:{nodeFields:omittedNodeFields,chartFields:['groupCentroids[].centroid'],history:'Prior session states/cursor and UI revision omitted; only current canonical continuationState retained.'},hydration:{fullViewJsonExactlyEqual:exactlyEqual,sha256:createHash('sha256').update(JSON.stringify(restored)).digest('hex'),requires:'Matching pinned corpus for node metadata and source vectors; existing weighted-mean formula/member order for centroids. No retrieval or PCA rerun needed for display.',continuation:'Preserves v1 next-action inputs. Does not preserve prior Back/replay history, agent reasoning, custom continuation semantics, or prove sufficient context beyond v1.'},notice:'Measurement-only serialization, not a production schema or implemented URL transport. JSON numbers retained at original precision.'};
report.leanSourceReferencingView=result;
await writeFile(`${directory}/lean-axion-ede.json`,JSON.stringify(lean));
await writeFile(`${directory}/lean-result.json`,JSON.stringify(result,null,2)+'\n');
await writeFile(`${directory}/report.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
