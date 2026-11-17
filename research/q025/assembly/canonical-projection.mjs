/** Transport exact admitted scoped-question identity after original proof gates. */
import {sha256} from './corpus.mjs';
const hashIds=ids=>sha256([...new Set(ids)].sort().join('\n'));
const fail=message=>{throw Error('Canonical projection: '+message);};
export function projectCanonicalCatalog({catalog,geometryInput,identityResolution,originalDefinitions,methodContextPolicy}) {
  const rawDest=new Map(catalog.destinations.map(d=>[d.id,d])),allGroups=identityResolution.groups||[];
  // An admitted lexical equivalence among registry-only candidate records does
  // not imply that those record IDs were ever public destination URLs.
  const groups=allGroups.filter(g=>g.memberIds.some(id=>rawDest.has(id)));
  if(!groups.length)return {catalog,geometryInput,report:{groups:0,registryOnlyGroups:allGroups.length,redirects:0,massChanged:false}};
  const aliases={},groupByMember=new Map(),rawDefinitions=new Map(originalDefinitions.map(d=>[d.id,d]));
  for(const g of groups)for(const id of g.memberIds){
    if(!rawDest.has(id)||!rawDest.has(g.destinationId))fail('exact member definition unavailable');
    if(groupByMember.has(id))fail('member appears in more than one whole group');groupByMember.set(id,g);
    if(id!==g.destinationId){if(aliases[id])fail('ambiguous redirect');aliases[id]=g.destinationId;}
  }
  for(const [s,t] of Object.entries(aliases))if(s===t||aliases[t])fail('redirect chains or cycles require one explicit complete group');
  const canonical=id=>aliases[id]||id;
  // The current approval revalidated four homes already at the canonical IDs.
  // A future group involving noncanonical allocated mass needs its own explicit
  // placement revalidation, never an implicit sum/renormalization here.
  if(geometryInput.allocations.some(a=>canonical(a.destinationId)!==a.destinationId))fail('home transfer requires explicit canonical placement revalidation');
  const destinations=catalog.destinations.filter(d=>!aliases[d.id]).map(d=>({...d})),dest=new Map(destinations.map(d=>[d.id,d]));
  for(const g of groups){
    const d=dest.get(g.destinationId);d.scopedIdentity={groupId:g.id,canonicalDestinationId:g.destinationId,identityInventorySha256:g.identityInventorySha256,decisionId:g.decisionId,
      originalDefinitions:g.memberIds.map(id=>structuredClone(rawDefinitions.get(id))),retainedReadingLimits:g.memberIds.map(id=>({destinationId:id,readingCoverage:structuredClone(rawDefinitions.get(id).readingCoverage)})),sourceStatementEquivalence:false};
    d.evidenceIds=[...d.evidenceIds]; // Exact canonical representative evidence is unchanged.
  }
  const observations=[],observationKeys=new Set();
  for(const row of catalog.sourceContributions||[]){
    const id=canonical(row.destinationId),g=groupByMember.get(row.destinationId),key=[row.decisionId,row.unitId,id,row.role].join('\n');
    if(observationKeys.has(key))fail('canonical projection duplicates one admitted observation');observationKeys.add(key);
    observations.push(id===row.destinationId?row:{...row,destinationId:id,scopeContentSha256:dest.get(id).scopeContentSha256,provenance:{...row.provenance,canonicalProjection:{identityGroupId:g.id,identityDecisionId:g.decisionId,originalDestinationId:row.destinationId,originalScopeContentSha256:row.scopeContentSha256,originalDecisionId:row.decisionId,originalObservation:structuredClone(row),meaning:'Same scoped-question identity projection; original qualification, evidence, target version and receipt remain unchanged.'}}});
  }
  for(const d of destinations){d.sourceContributions=observations.filter(r=>r.destinationId===d.id);d.sourceContributionObservationCount=d.sourceContributions.length;d.sourceContributionRelationshipCount=new Set(d.sourceContributions.map(r=>r.unitId+'\n'+r.role)).size;}
  const memberships=[],memberMap=new Map();
  for(const row of catalog.memberships){
    const id=canonical(row.destinationId),key=id+'\n'+row.unitId,old=memberMap.get(key),mapped=id===row.destinationId?row:{...row,destinationId:id,canonicalProjection:{originalDestinationId:row.destinationId,identityDecisionId:groupByMember.get(row.destinationId).decisionId}};
    if(old){if(old.weight!==mapped.weight||old.role!==mapped.role||old.placementStatus!==mapped.placementStatus||old.associationScope!==mapped.associationScope)fail('membership union needs explicit unequal-row adjudication');continue;}
    memberMap.set(key,mapped);memberships.push(mapped);
  }
  for(const d of destinations){
    const rows=memberships.filter(r=>r.destinationId===d.id),primary=rows.filter(r=>r.placementStatus!=='context_only');d.memberIds=primary.map(r=>r.unitId).sort();d.memberIdsSha256=hashIds(d.memberIds);d.contextAssociationCount=rows.length-primary.length;
    d.contextSourceIds=[...new Set((groupByMember.get(d.id)?.memberIds||[d.id]).flatMap(id=>rawDest.get(id).contextSourceIds||[]))];
  }
  const relations=[],suppressedSelfRelations=[];
  for(const row of catalog.relations){
    const source=canonical(row.source),target=canonical(row.target),changed=source!==row.source||target!==row.target;
    const projection=changed?{sourceOriginalId:row.source,targetOriginalId:row.target,originalRelation:structuredClone(row),identityDecisionIds:[...new Set([groupByMember.get(row.source)?.decisionId,groupByMember.get(row.target)?.decisionId].filter(Boolean))],sourceCanonicalScopeContentSha256:dest.get(source).scopeContentSha256,targetCanonicalScopeContentSha256:dest.get(target).scopeContentSha256}:null;
    if(source===target){suppressedSelfRelations.push({relation:row,canonicalDestinationId:source,projection,reason:'Accepted scoped identity makes this an internal/self route; original exact scientific relation is retained as provenance.'});continue;}
    relations.push(changed?{...row,source,target,provenance:{...row.provenance,canonicalEndpointProjection:projection}}:row);
  }
  const parents=new Map(destinations.map(d=>[d.id,[]]));for(const r of relations.filter(r=>r.type==='narrower'))parents.get(r.target).push(r.source);
  const visiting=new Set(),visited=new Set();
  function acyclic(id){if(visiting.has(id))fail('projected containment is cyclic');if(visited.has(id))return;visiting.add(id);for(const p of parents.get(id))acyclic(p);visiting.delete(id);visited.add(id);}
  for(const id of parents.keys())acyclic(id);
  // Equivalent scopes can have different recorded parents. Closing memberships
  // before projection misses those newly shared ancestors. Recompute displayed
  // closure from the admitted direct allocations on the projected narrower DAG;
  // the allocations themselves remain byte-for-byte unchanged.
  const ancestorMemo=new Map();function ancestors(id){if(!ancestorMemo.has(id)){const set=new Set();for(const p of parents.get(id)){set.add(p);for(const a of ancestors(p))set.add(a);}ancestorMemo.set(id,set);}return ancestorMemo.get(id);}
  const allocatedUnits=new Set(geometryInput.allocations.map(a=>a.unitId)),originalPrimaryKeys=new Set(memberships.filter(r=>r.placementStatus!=='context_only').map(r=>r.destinationId+'\n'+r.unitId));
  const rebuilt=new Map(),allocationByUnit=new Map();
  function add(row){const key=row.destinationId+'\n'+row.unitId,old=rebuilt.get(key);if(!old||old.placementStatus==='context_only'&&row.placementStatus!=='context_only')rebuilt.set(key,row);else if(row.placementStatus!=='context_only'){old.weight=Math.min(1,old.weight+row.weight);old.decisionIds=[...new Set([...(old.decisionIds||[]),...(row.decisionIds||[])])];}}
  for(const a of geometryInput.allocations){if(!allocationByUnit.has(a.unitId))allocationByUnit.set(a.unitId,[]);allocationByUnit.get(a.unitId).push(a);const template=memberMap.get(a.destinationId+'\n'+a.unitId);if(!template)fail('direct allocation lacks its exact source membership');for(const id of [a.destinationId,...ancestors(a.destinationId)])add({...template,destinationId:id,weight:a.weight,decisionIds:a.decisionId?[a.decisionId]:template.decisionIds,canonicalContainmentClosure:{directDestinationId:a.destinationId,via:'admitted_narrower_only',identityInventorySha256:identityResolution.inventorySha256}});}
  for(const rows of allocationByUnit.values())for(const a of rows)for(const b of rows)if(a!==b&&(a.destinationId===b.destinationId||ancestors(a.destinationId).has(b.destinationId)))fail('projected direct homes duplicate a canonical destination or its ancestor');
  for(const row of memberships)if(row.placementStatus!=='context_only'&&!allocatedUnits.has(row.unitId))add({...row});
  const methodTemplates=new Map();for(const row of memberships.filter(r=>r.placementStatus==='context_only')){if(row.associationScope==='same_paper_context'&&row.lens==='method')methodTemplates.set(row.unitId,row);else add({...row});}
  if(methodContextPolicy?.kind){
    const methodsByPaper=new Map();for(const row of methodTemplates.values()){if(!methodsByPaper.has(row.paperId))methodsByPaper.set(row.paperId,[]);methodsByPaper.get(row.paperId).push(row);}
    for(const d of destinations.filter(d=>d.kind==='region'||methodContextPolicy.kind==='same_paper_context_at_scientific_destinations'&&d.kind==='question')){
      const byPaper=new Map();for(const row of rebuilt.values())if(row.destinationId===d.id&&allocatedUnits.has(row.unitId)&&row.placementStatus!=='context_only'){if(!byPaper.has(row.paperId))byPaper.set(row.paperId,[]);byPaper.get(row.paperId).push(row.unitId);}
      for(const [paperId,qids]of byPaper)for(const template of methodsByPaper.get(paperId)||[])add({...template,destinationId:d.id,associationProvenance:{...template.associationProvenance,sourceQuestionIds:[...new Set(qids)].sort(),noMethodApplicabilityInferred:true}});
    }
  }else for(const row of memberships.filter(r=>r.placementStatus==='context_only'&&r.associationScope==='same_paper_context'))add({...row});
  memberships.splice(0,memberships.length,...rebuilt.values());
  let addedAncestorRows=0;for(const row of memberships)if(row.placementStatus!=='context_only'&&!originalPrimaryKeys.has(row.destinationId+'\n'+row.unitId))addedAncestorRows++;
  for(const d of destinations){const rows=memberships.filter(r=>r.destinationId===d.id),primary=rows.filter(r=>r.placementStatus!=='context_only');d.memberIds=primary.map(r=>r.unitId).sort();d.memberIdsSha256=hashIds(d.memberIds);d.contextAssociationCount=rows.length-primary.length;}
  for(const r of relations.filter(r=>r.type==='narrower'))for(const uid of dest.get(r.target).memberIds)if(!dest.get(r.source).memberIds.includes(uid))fail('projected containment is not a true source subset');
  const geometryDest=geometryInput.destinations.filter(d=>!aliases[d.id]).map(d=>({...d,memberIds:dest.get(d.id).memberIds,parentIds:[...new Set(parents.get(d.id))]}));
  const report={groups:groups.length,redirects:Object.keys(aliases).length,originalDefinitionsRetained:groups.reduce((s,g)=>s+g.memberIds.length,0),suppressedSelfRelations:suppressedSelfRelations.length,sourceContributionObservations:observations.length,sourceContributionRelationships:new Set(observations.map(r=>[r.unitId,r.destinationId,r.role].join('\n'))).size,ancestorClosureRecomputed:true,addedAncestorRows,massChanged:false,homeRowsRemapped:0,sourceStatementEquivalence:false};
  return {catalog:{...catalog,destinations,memberships,relations,sourceContributions:observations,destinationAliases:aliases,organizationProvenance:{...catalog.organizationProvenance,canonicalProjection:{...report,suppressedSelfRelations}}},geometryInput:{...geometryInput,destinations:geometryDest,baseDestinationIds:[...new Set(geometryInput.baseDestinationIds.map(canonical))],canonicalIdentityProjection:report},report};
}
