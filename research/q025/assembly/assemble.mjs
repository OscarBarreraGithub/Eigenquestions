/** One production-data compiler. It writes research output, not the public site. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join,resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseArgs} from 'node:util';
import {readPinnedJson,loadFrozenCorpus,sha256} from './corpus.mjs';
import {assembleAccepted,acceptedContentHash} from './accepted.mjs';
import {normalizeCompactIdentity,attachFineSourceAccess} from './fine-identities.mjs';
import {attachClassification} from './classification.mjs';
import {writeLazyPackage} from './lazy-package.mjs';
import {validateAtlas} from '../../../lib/geometry/prepared-atlas.mjs';

export async function runAssembly({root,packetPath,out,overviewPath}) {
  const input=await readPinnedJson(packetPath),packet=input.value,base=dirname(packetPath),resolveInput=path=>resolve(base,path);
  const admission=await readPinnedJson(resolveInput(packet.acceptance.receipt.path),packet.acceptance.receipt.sha256);
  if(admission.value.status!=='accepted_for_assembly'||admission.value.acceptedContentSha256!==acceptedContentHash(packet))throw new Error('Admission receipt does not bind this exact organization packet');
  const verifiedReceiptHashes=new Set([admission.sha256]),verifiedReviews=[];
  for(const r of packet.reviewRegistry){if(!r.path||!r.sha256)throw new Error('Review registry needs exact local artifact and hash');const bytes=await readFile(resolveInput(r.path));if(sha256(bytes)!==r.sha256)throw new Error(`Review artifact changed: ${r.id}`);verifiedReceiptHashes.add(r.sha256);verifiedReviews.push({id:r.id,sha256:r.sha256,bytes:bytes.length});}
  for(const d of packet.decisions)if(d.adjudication?.receipt){const r=d.adjudication.receipt;const read=await readPinnedJson(resolveInput(r.path),r.sha256);verifiedReceiptHashes.add(read.sha256);}
  if(packet.identityResolution){
    const resolution=packet.identityResolution,registry=await readPinnedJson(resolveInput(resolution.registry.path),resolution.registry.sha256);
    if(JSON.stringify(registry.value.records)!==JSON.stringify(resolution.records)||JSON.stringify(registry.value.comparisons)!==JSON.stringify(resolution.comparisons))throw new Error('Identity resolution omits or changes its pinned complete comparison inventory');
    verifiedReceiptHashes.add(registry.sha256);
  }
  const corpus=await loadFrozenCorpus(join(root,'data/navigation'));
  const bins=await readPinnedJson(resolveInput(packet.originalCandidate.regionsPath),packet.originalCandidate.regionsSha256);
  const assembled=assembleAccepted({packet,corpus,originalBins:bins.value,originalBinsSha256:bins.sha256,verifiedReceiptHashes});
  const fineBundles=[];
  for(const ref of packet.fineIdentityPackets||[]){
    const p=await readPinnedJson(resolveInput(ref.packet.path),ref.packet.sha256),r=await readPinnedJson(resolveInput(ref.reply.path),ref.reply.sha256);
    if(!verifiedReviews.some(x=>x.id===ref.reviewId&&x.sha256===r.sha256))throw new Error('Fine review artifact is not in verified review registry');
    fineBundles.push(normalizeCompactIdentity({packet:p.value,reply:r.value,corpus,packetSha256:p.sha256,replySha256:r.sha256,reviewId:ref.reviewId}));
  }
  const access=packet.decisions.find(d=>d.id===packet.fineSourceAccessPolicy?.decisionId);
  if(!access||access.status!=='accepted'||access.type!=='source_access_policy'||access.outcome!=='preserve_source_facets_without_identity_promotion')throw new Error('Explicit fine source-access policy is required');
  attachFineSourceAccess(assembled.catalog,{corpus,proposalBundles:fineBundles,policyDecisionId:access.id});
  await mkdir(out,{recursive:true});
  const geometryText=JSON.stringify(assembled.geometryInput),geometryHash=sha256(geometryText);await writeFile(join(out,'accepted-geometry-input.json'),geometryText);
  if(overviewPath){const o=await readPinnedJson(overviewPath);if(o.value.membershipSha256!==geometryHash)throw new Error('Overview belongs to different accepted membership input');const ids=new Set(assembled.catalog.destinations.map(d=>d.id));if(o.value.nodes.some(n=>!ids.has(n.destinationId)))throw new Error('Overview node absent from catalog');assembled.catalog.overview=o.value;}
  const geometry=join(root,'research/q025/geometry/physics-entrance'),orientation=await readPinnedJson(join(geometry,'layout-v2/orientation.json')),classification=await readPinnedJson(join(geometry,'results/destinations.json'));
  const {catalog,entryDestinationId}=attachClassification(assembled.catalog,{orientation:orientation.value,destinations:classification.value,detailEntryDestinationId:packet.atlas.entryDestinationId});
  const contextRoot=resolveInput(packet.assets.sourceContextRoot),context=await readPinnedJson(join(contextRoot,'manifest.json'),packet.assets.sourceContextManifestSha256);
  const contextDescriptors=[context.value.sourceContextIndex,context.value.sourceContextSummary,...Object.values(context.value.files),...Object.values(context.value.unitIndexFiles)];
  const assets=[...new Map(contextDescriptors.map(d=>[d.path,d])).values()].map(d=>({path:d.path,sha256:d.sha256,bytes:d.bytes,sourcePath:join(contextRoot,d.path)}));
  const assetPlan={schemaVersion:'q025-assembly-asset-plan/1',meaning:'Installer copies each immutable asset once into the package root and verifies its hash; research assembly does not duplicate the full context pack.',assets};
  const assetText=JSON.stringify(assetPlan);await writeFile(join(out,'asset-plan.json'),assetText);
  const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:packet.atlas.atlasId,atlasVersion:packet.atlas.atlasVersion,corpusId:corpus.manifest.corpusId,corpusContentHash:corpus.manifest.contentHash,entryDestinationId,snapshotDate:corpus.manifest.snapshotDate,scope:{...corpus.manifest.scope,...packet.atlas.scope,description:packet.atlas.scope?.description||'Reviewed organization of the frozen Swampland-centered question/method corpus, with a separate broad physics classification entrance.',deliveryState:overviewPath?'accepted_organization_for_integration_review':'accepted_organization_geometry_pending'},files:{sourceContextIndex:context.value.sourceContextIndex,sourceContextSummary:context.value.sourceContextSummary}};
  await writeFile(join(out,'assembly-report.json'),JSON.stringify({...assembled.report,acceptedPacketSha256:input.sha256,acceptedContentSha256:acceptedContentHash(packet),verifiedReviews,fineSourceQuestionCount:corpus.manifest.layers.physical_question.count,fineIdentityProposalGroupCount:fineBundles.reduce((n,b)=>n+b.groups.length,0),geometryInputSha256:geometryHash,geometryPresent:Boolean(overviewPath)},null,2)+'\n');
  const {handoff}=await writeLazyPackage({directory:out,manifest,catalog,externalAssets:assets,validateLogical:logical=>{validateAtlas({...manifest,schemaVersion:'1.0.0',files:{...manifest.files,catalog:{path:'logical-catalog.json',sha256:sha256(JSON.stringify(logical))}}},logical);return {...assembled.report,fullSourceIdentityAndContainmentChecked:true,acceptedPacketSha256:input.sha256,admissionReceiptSha256:admission.sha256};},publicationStatus:overviewPath?'accepted_organization_for_integration_review':'accepted_organization_geometry_pending',provenance:{acceptedPacketSha256:input.sha256,admissionReceiptSha256:admission.sha256,originalBinsSha256:bins.sha256,geometryInputSha256:geometryHash,contextManifestSha256:context.sha256,orientationSha256:orientation.sha256,verifiedReviews}});
  handoff.assetPlan={path:'asset-plan.json',sha256:sha256(assetText),assetCount:assets.length};handoff.fullAssetCopyPending=true;handoff.detailEntryDestinationId=packet.atlas.entryDestinationId;
  await writeFile(join(out,'handoff.json'),JSON.stringify(handoff,null,2)+'\n');return handoff;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const {values}=parseArgs({options:{packet:{type:'string'},out:{type:'string'},overview:{type:'string'}}});if(!values.packet)throw new Error('--packet is required; reviewer outputs are not an admission packet');
  const root=resolve(fileURLToPath(new URL('../../../',import.meta.url)));console.log(JSON.stringify(await runAssembly({root,packetPath:resolve(values.packet),out:resolve(values.out||join(root,'research/q025/assembly/outputs/accepted')),overviewPath:values.overview?resolve(values.overview):undefined}),null,2));
}
