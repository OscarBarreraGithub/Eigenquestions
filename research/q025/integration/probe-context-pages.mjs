/** Real source records verify paging losslessness; scientific claims are unchanged. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createAtlasContextReader} from '../../../lib/geometry/prepared-atlas.mjs';
import {pageSourceContext} from '../../../lib/protocol/context-page.mjs';
const base='research/q025/geometry/compact-source-context-pack',bytes=await readFile(`${base}/source-context-index.json`),index=JSON.parse(bytes),summary=JSON.parse(await readFile(`${base}/source-context-summary.json`));
const atlas={manifest:{files:{sourceContextIndex:{path:'source-context-index.json',sha256:createHash('sha256').update(bytes).digest('hex')}}},catalog:{}};
const reader=createAtlasContextReader(atlas,{base,readText:path=>readFile(path,'utf8'),readBinary:path=>readFile(path)});
const largest=Object.keys(summary.papers).sort((a,b)=>summary.papers[b].fullContext.uncompressedBytes-summary.papers[a].fullContext.uncompressedBytes)[0];
const selected=[...new Set(['0704.1256',largest,...Object.keys(summary.papers).filter(id=>summary.papers[id].nonpositiveAssessmentCount>0)])];
const results=[],withheldIds=new Set(),assessmentIds=new Set();
for(const paperId of selected){const descriptor=summary.papers[paperId].fullContext,unitId=Object.entries(index.units).find(([id,d])=>d.path===descriptor.path)?.[0];if(!unitId)continue;
  const context=await reader(unitId),first=pageSourceContext(context),assessmentPages=[];let offset=0;
  do{const page=pageSourceContext(context,{section:'assessments',offset});assessmentPages.push(...page.sourceAssessments);offset=page.page.nextOffset;}while(offset!==null);
  if(JSON.stringify(assessmentPages)!==JSON.stringify(context.sourceAssessments))throw new Error('Assessment paging lost a record');
  for(const item of assessmentPages){assessmentIds.add(item.id);if(item.promotionWithheld&&item.readerNote)withheldIds.add(item.id);}
  const objects=[];offset=0;do{const page=pageSourceContext(context,{offset});objects.push(...page.sourceObjects);offset=page.page.nextOffset;}while(offset!==null);
  const ordered=rows=>[...rows].sort((a,b)=>a.id.localeCompare(b.id));
  if(JSON.stringify(ordered(objects))!==JSON.stringify(ordered(context.sourceObjects)))throw new Error('Object pages lost scientific data');
  results.push({paperId,unitId,completeContextBytes:Buffer.byteLength(JSON.stringify(context)),defaultPageBytes:Buffer.byteLength(JSON.stringify(first)),objects:context.sourceObjects.length,defaultObjects:first.sourceObjects.length,assessments:assessmentPages.length,withheldNotes:assessmentPages.filter(a=>a.promotionWithheld&&a.readerNote).length,allObjectBytesPreserved:true,allAssessmentBytesPreserved:true});
}
const receipt={kind:'q025-real-source-context-paging',indexSha256:createHash('sha256').update(bytes).digest('hex'),pagingModuleSha256:createHash('sha256').update(await readFile('lib/protocol/context-page.mjs')).digest('hex'),uniqueAssessmentIds:[...assessmentIds],uniqueWithheldIds:[...withheldIds],results};
await writeFile('research/q025/integration/context-paging-real-receipt.json',JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({cases:results.length,largest:results.reduce((a,b)=>a.completeContextBytes>b.completeContextBytes?a:b),uniqueAssessments:assessmentIds.size,uniqueWithheld:withheldIds.size},null,2));
