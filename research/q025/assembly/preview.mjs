/** Provisional chart/portal QA package. Never an accepted science assembly. */
import {mkdir,copyFile,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readPinnedJson,loadFrozenCorpus,sha256} from './corpus.mjs';
import {attachClassification} from './classification.mjs';
import {writePackage} from './package.mjs';

export async function buildPreview({root,out,methodContext=false}) {
  const draftRoot=join(root,'research/q025/integration/draft-atlas'),geometry=join(root,'research/q025/geometry/physics-entrance');
  const draftManifest=await readPinnedJson(join(draftRoot,'manifest.json'));
  const draftCatalog=await readPinnedJson(join(draftRoot,draftManifest.value.files.catalog.path),draftManifest.value.files.catalog.sha256);
  const orientation=await readPinnedJson(join(geometry,'layout-v2/orientation.json')),destinations=await readPinnedJson(join(geometry,'results/destinations.json'));
  const corpus=await loadFrozenCorpus(join(root,'data/navigation'));
  for(const source of draftCatalog.value.sources){const frozen=corpus.unitMap.get(source.id);if(!frozen||frozen.paperId!==source.paperId||frozen.text!==source.evidence.text)throw new Error('Research draft source differs from frozen corpus');}
  const {catalog,entryDestinationId}=attachClassification(draftCatalog.value,{orientation:orientation.value,destinations:destinations.value,detailEntryDestinationId:draftManifest.value.entryDestinationId,reviewOnly:true});
  if(methodContext)for(const d of catalog.destinations.filter(d=>!d.metadataOnly))for(const id of d.contextSourceIds||[]){
    const u=corpus.unitMap.get(id);if(u?.lens!=='method')continue;
    if(catalog.memberships.some(m=>m.destinationId===d.id&&m.unitId===id))continue;
    const qids=catalog.memberships.filter(m=>m.destinationId===d.id&&corpus.unitMap.get(m.unitId)?.lens==='physical_question'&&corpus.unitMap.get(m.unitId).paperId===u.paperId).map(m=>m.unitId);
    if(!qids.length)throw new Error('Context method lacks an exact same-paper primary question');
    catalog.memberships.push({destinationId:d.id,unitId:id,paperId:u.paperId,browserVectorRow:u.browserVectorRow,sourceRow:u.sourceRow,year:corpus.papers.get(u.paperId).year,lens:'method',weight:1,role:'evidence',associationScope:'same_paper_context',placementStatus:'context_only',associationProvenance:{join:'exact frozen paperId',paperId:u.paperId,sourceQuestionIds:qids,noMethodApplicabilityInferred:true}});
  }
  if(catalog.overview)throw new Error('Research preview must not invent a detailed overview');
  await mkdir(out,{recursive:true});
  const indexDescriptor=draftManifest.value.files.sourceContextIndex;
  const context=await readPinnedJson(join(draftRoot,indexDescriptor.path),indexDescriptor.sha256);
  for(const descriptor of new Map(Object.values(context.value.units).map(d=>[d.path,d])).values()){
    await readPinnedJson(join(draftRoot,descriptor.path),descriptor.sha256);
    await copyFile(join(draftRoot,descriptor.path),join(out,descriptor.path));
  }
  await copyFile(join(draftRoot,indexDescriptor.path),join(out,indexDescriptor.path));
  const manifest={...draftManifest.value,atlasId:'physics-classification-research-preview',atlasVersion:methodContext?'2026-11-17-provisional-v2':'2026-11-17-provisional-v1',entryDestinationId,scope:{...draftManifest.value.scope,description:'Research preview: a pinned physics classification chart, an explicit hep-th landmark, and four provisional KK source-reading cards. No detailed atlas geometry is included.',deliveryState:'research_candidate',limitations:['The four scientific cards remain proposals, not accepted full-atlas organization.','The broad chart is a vocabulary classification map, not empirical all-physics paper geometry.','Portal links are curator navigation, not classification equivalence or scientific implication.']},files:{sourceContextIndex:indexDescriptor}};
  const provenance=[draftManifest,draftCatalog,orientation,destinations,context].map(({value,...d})=>d);
  const handoff=await writePackage({directory:out,manifest,catalog,provenance,publicationStatus:'research_candidate_not_accepted'});
  handoff.entryDestinationId=entryDestinationId;handoff.detailEntryDestinationId=draftManifest.value.entryDestinationId;handoff.existingDraftStatusesPreserved=true;handoff.detailGeometryInvented=false;handoff.primaryMembershipCount=catalog.memberships.filter(m=>m.placementStatus!=='context_only').length;handoff.contextAssociationCount=catalog.memberships.filter(m=>m.placementStatus==='context_only').length;
  await writeFile(join(out,'handoff.json'),JSON.stringify(handoff,null,2)+'\n');return handoff;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const root=resolve(fileURLToPath(new URL('../../../',import.meta.url))),out=resolve(process.argv[2]||join(root,'research/q025/assembly/preview-package'));
  console.log(JSON.stringify(await buildPreview({root,out,methodContext:process.argv.includes('--method-context')}),null,2));
}
