/** Resolve bounded primary evidence against pinned source records and archive bytes. */
import {resolve,relative,sep} from 'node:path';
import {readPinnedJson,sha256} from './corpus.mjs';
const hex=/^[a-f0-9]{64}$/;
export const isPrimaryReference=ref=>['primary','source_excerpt'].includes(ref?.kind);
export function primaryLocatorFingerprint(ref){
  const c=ref?.sourceContext;
  const documentAnchor=ref?.anchorKind==='archived_document_page';
  if(documentAnchor?ref.sourceId!==undefined:ref?.anchorKind!==undefined||!/^ev:[a-f0-9]+$/.test(ref?.sourceId||''))return null;
  if(!isPrimaryReference(ref)||!ref.paperId||!hex.test(ref.sourceSha256||'')||!c||typeof c.path!=='string'||!c.path||!hex.test(c.fileSha256||'')||!Number.isSafeInteger(c.pdfPage)||c.pdfPage<1||!Number.isSafeInteger(c.start)||c.start<0||!Number.isSafeInteger(c.end)||c.end<=c.start||!hex.test(c.textSha256||''))return null;
  return sha256(JSON.stringify({paperId:ref.paperId,...(documentAnchor?{anchorKind:ref.anchorKind}:{sourceId:ref.sourceId}),sourceSha256:ref.sourceSha256,path:c.path,fileSha256:c.fileSha256,pdfPage:c.pdfPage,start:c.start,end:c.end,textSha256:c.textSha256}));
}
function within(root,path){const absolute=resolve(root,path),r=relative(resolve(root),absolute);if(!r||r==='..'||r.startsWith('..'+sep))throw new Error('Primary evidence: locator escapes its archive root');return absolute;}
export async function verifyPrimaryEvidence({references,corpus,archiveRoot,contextRoot,contextManifest}){
  const refs=references.filter(isPrimaryReference),verifiedLocators=new Set(),records=[],files=new Map();
  if(!refs.length)return {verifiedLocators,report:{referenceCount:0,distinctLocators:0,records:[],files:[],rawPrimaryTextExported:false}};
  if(!archiveRoot||!contextRoot||!contextManifest?.sourceContextSummary)throw new Error('Primary evidence: exact archive root and pinned source context are required');
  const descriptor=contextManifest.sourceContextSummary,summary=await readPinnedJson(within(contextRoot,descriptor.path),descriptor.sha256),byPaper=new Map();
  for(const ref of refs){const fingerprint=primaryLocatorFingerprint(ref);if(!fingerprint)throw new Error('Primary evidence: malformed exact primary locator');if(!byPaper.has(ref.paperId))byPaper.set(ref.paperId,[]);byPaper.get(ref.paperId).push({ref,fingerprint});}
  for(const [paperId,paperRefs] of byPaper){
    const paper=corpus.papers.get(paperId),d=summary.value.papers?.[paperId]?.fullContext;
    if(!paper?.sourceSha256||!d)throw new Error(`Primary evidence: paper lacks a pinned source/context ${paperId}`);
    const shard=await readPinnedJson(within(contextRoot,d.path),d.sha256),evidence=new Map((shard.value.sourceEvidence||[]).map(e=>[e.id,e])),readings=new Map();
    for(const {ref,fingerprint} of paperRefs){
      if(verifiedLocators.has(fingerprint))continue;
      const c=ref.sourceContext,documentAnchor=ref.anchorKind==='archived_document_page',e=documentAnchor?null:evidence.get('source-graph:'+ref.sourceId);
      if(ref.sourceSha256!==paper.sourceSha256||(!documentAnchor&&(!e||e.paperId!==paperId||e.sourceSha256!==ref.sourceSha256||e.page!==c.pdfPage)))throw new Error(`Primary evidence: source ID/paper/page does not resolve exactly ${ref.sourceId||ref.paperId}`);
      if(!readings.has(c.path))readings.set(c.path,await readPinnedJson(within(archiveRoot,c.path),c.fileSha256));
      const reading=readings.get(c.path);if(reading.sha256!==c.fileSha256||reading.value.source_sha256!==ref.sourceSha256)throw new Error('Primary evidence: archived source identity changed');
      const page=reading.value.pages?.[c.pdfPage-1];if(typeof page!=='string')throw new Error('Primary evidence: missing exact archived page');
      // The evaluation compiler uses Python Unicode-codepoint offsets. JS UTF-16
      // slicing would misbind any span after a supplementary Unicode character.
      const characters=Array.from(page);if(c.end>characters.length||sha256(characters.slice(c.start,c.end).join(''))!==c.textSha256)throw new Error('Primary evidence: exact source span/hash mismatch');
      verifiedLocators.add(fingerprint);records.push({fingerprint,paperId,...(documentAnchor?{anchorKind:ref.anchorKind,extractedEvidenceIdentityAsserted:false}:{sourceId:ref.sourceId}),sourceSha256:ref.sourceSha256,sourceContext:{path:c.path,fileSha256:c.fileSha256,pdfPage:c.pdfPage,start:c.start,end:c.end,textSha256:c.textSha256},contextShardSha256:shard.sha256});files.set(c.path,{path:c.path,sha256:reading.sha256,bytes:reading.bytes});
    }
  }
  return {verifiedLocators,report:{referenceCount:refs.length,distinctLocators:verifiedLocators.size,archiveOnlyAnchorCount:records.filter(r=>r.anchorKind==='archived_document_page').length,sourceSummarySha256:summary.sha256,records,files:[...files.values()],rawPrimaryTextExported:false,meaning:'Exact archived source, paper, page and bounded text identity verified; extraction evidence IDs are asserted only where supplied and independently resolved. Archive-only anchors assert no extracted semantic object. This does not independently prove scientific relevance, calculations or full-paper coverage.'}};
}
