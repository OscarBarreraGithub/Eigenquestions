/** Audit all currently admitted comparisons before any global scoped-question reuse. */
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {join,resolve,relative,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256} from '../corpus.mjs';
import {scopeContentHash} from '../accepted.mjs';
import {validateCanonicalIdentity,identityInventoryHash} from '../fine-identities.mjs';
const here=dirname(fileURLToPath(import.meta.url)),root=resolve(here,'../../../..'),F=join(root,'research/q025/evaluation/full-pass'),out=join(here,'identity-current-v2');
async function read(path){const raw=await readFile(path);return {value:JSON.parse(raw),pin:{path:relative(root,path),sha256:sha256(raw)}};}
const registry=await read(join(F,'reconciliation-v1/authored-scope-registry-v6-20261117T144302Z.json'));
const precedence=await read(join(F,'canonical-pilot-admissions-v1/constraint-precedence.json'));
const packet=await read(join(here,'candidate-6030-navigation-v2/aggregate.local.json'));
const components=await Promise.all(['canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json','navigation-admissions-v1/inflation-component.json','navigation-admissions-v1/amplitude-component.json','navigation-admissions-v1/kk-component.json'].map(p=>read(join(F,p))));
const dest=new Map(packet.value.destinations.map(d=>[d.id,d])),reviewRecords=new Map(packet.value.reviewRegistry.map(r=>[r.id,r]));
const records=new Map();for(const r of registry.value.records){if(!records.has(r.candidateId))records.set(r.candidateId,{id:r.candidateId,registryRecordIds:[]});records.get(r.candidateId).registryRecordIds.push(r.recordId);}
for(const d of dest.values())if(!records.has(d.id))records.set(d.id,{id:d.id,registryRecordIds:[]});
for(const r of records.values())r.contentSha256=sha256(JSON.stringify({id:r.id,scopeContentSha256:dest.has(r.id)?scopeContentHash(dest.get(r.id)):null,registryRecordIds:r.registryRecordIds.sort(),registrySha256:registry.pin.sha256}));
const comparisons=[],history=[...precedence.value.historicalConstraints],groups=[];
const mapOperation=r=>r==='same_scoped_question'?r:r.startsWith('specializes')?'specializes':r==='overlap'?'shared_parent_distinct':r==='changed_scope'?'different':r;
function constraint(c,family,index){
  const operation=mapOperation(c.relation),members=[c.left,c.right];
  if(members.some(id=>!records.has(id)))throw Error('Constraint names absent registry ID');
  comparisons.push({id:'comparison:current:'+family+':'+index,operation,members,target:operation==='same_scoped_question'?members[0]:undefined,definingDifferences:operation==='same_scoped_question'?[]:[c.nativeConstraint.reason],sourceReviewIds:c.sourceReviewIds,evidenceRefs:[{kind:'pinned_current_constraint',family,index,nativeRefs:c.nativeConstraint.refs}],nativeConstraint:c,meaning:'Exact latest independently reviewed constraint; historical predecessor remains separately retained.'});
}
precedence.value.currentConstraints.forEach((c,i)=>constraint(c,'canonical-pilot',i));
for(let i=0;i<components.length;i++){
  const c=components[i];
  if(i){c.value.completeLocalPairConstraints.filter(x=>x.stage==='challenge').forEach((x,j)=>constraint(x,['pilot','inflation','amplitude','kk'][i],j));history.push(...c.value.completeLocalPairConstraints.filter(x=>x.stage!=='challenge'));}
  for(const op of c.value.typedCanonicalOperations){
    // The operation's target is its proposed reusable destination, not an
    // additional compared member. Adding it to a comparison would invent a
    // distinction between an old formulation and its explicitly equal reuse.
    const operation=op.nativeOperation.operation,members=[...op.members];
    if(members.some(id=>!records.has(id)))throw Error('Operation names absent registry ID');
    if(members.length<2)continue;
    comparisons.push({id:op.id,operation,members,target:op.target,definingDifferences:op.nativeOperation.definingDifferences,sourceReviewIds:op.sourceReviewIds,evidenceRefs:op.evidenceRefs,sourceComponent:c.pin,acceptedTypedOperationNotAutomaticUnion:true});
    if(operation==='same_scoped_question'){
      if(op.nativeOperation.definingDifferences.length||!dest.has(op.target))throw Error('Unbound equality scope');
      groups.push({operationId:op.id,memberIds:members,canonicalDestinationId:op.target,canonicalScopeContentSha256:scopeContentHash(dest.get(op.target)),sourceReviewIds:op.sourceReviewIds,
                   retainedReadingLimits:members.map(id=>({destinationId:id,readingCoverage:dest.get(id)?.readingCoverage})),
                   currentHomeRows:packet.value.placements.filter(p=>members.includes(p.destinationId)),status:'whole_group_binding_pending_global_inventory_result',sourceStatementEquivalence:false,automaticHomeTransfer:false});
    }
  }
}
await mkdir(out,{recursive:true});
const inventory={schemaVersion:'q025-current-identity-inventory/1',inputs:[registry.pin,precedence.pin,packet.pin,...components.map(c=>c.pin)],records:[...records.values()],comparisons,historicalConstraints:history,
                 currentVersusHistoricalPolicy:'Current challenge constraints plus explicitly admitted final typed operations only. Historical constraints retain provenance without silently overriding approved revisions. Screening nominations are not admitted scientific constraints.'};
const raw=JSON.stringify(inventory,null,2)+'\n',path=join(out,'inventory.json');await writeFile(path,raw);
const resolution={registry:{path:relative(root,path),sha256:sha256(raw)},records:inventory.records,comparisons,canonicalGroups:[]};
const audit=validateCanonicalIdentity({resolution,destinations:packet.value.destinations,scopeHash:scopeContentHash,reviewRecords,decision:()=>{throw Error('Audit must not invent global group admission');}});
for(const g of groups){g.conflicts=audit.unresolvedConflicts.filter(c=>c.memberIds.some(id=>g.memberIds.includes(id)));g.status=g.conflicts.length?'blocked_by_current_global_constraint':'current_inventory_conflict_free_global_group_and_home_rebinding_pending';}
const report={schemaVersion:'q025-current-whole-group-audit/1',status:groups.some(g=>g.conflicts.length)?'conflict_queue_required':'all_three_explicit_groups_conflict_free_in_current_admitted_inventory',inventory:resolution.registry,identityInventorySha256:identityInventoryHash(resolution),records:records.size,currentComparisons:comparisons.length,historicalConstraintsRetained:history.length,groups,unresolvedConflicts:audit.unresolvedConflicts,
              limitations:['The audit does not claim all authored scopes have completed identity reconciliation. Unreviewed screened candidates remain pending.','No connected component is merged. Exactly three existing explicit whole-group operations are tested, including their target equalities.','All original readingCoverage records are retained. Home weights and route endpoints are not changed by this audit; any later canonical remapping must preserve source mass and typed qualifications.'],automaticAliases:0,automaticHomeTransfers:0,scriptSha256:sha256(await readFile(fileURLToPath(import.meta.url)))};
await writeFile(join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:report.status,records:records.size,comparisons:comparisons.length,history:history.length,conflicts:audit.unresolvedConflicts.length,groups:groups.map(g=>({operationId:g.operationId,members:g.memberIds.length,currentHomeRows:g.currentHomeRows.length,conflicts:g.conflicts.length})),inventory:resolution.registry},null,2));
