import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {scopeContentHash,sourceContributionContentHash} from '../../../assembly/accepted.mjs';
const here=path.dirname(fileURLToPath(import.meta.url)),full=path.dirname(here),workspace=path.resolve(full,'../../../../');
const hash=b=>createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const pin=p=>({path:path.relative(workspace,p),sha256:hash(fs.readFileSync(p))});
const source=path.join(full,'admissions-v3/supported-scope-role-component-v3.json');
const original=read(source),out=structuredClone(original),byId=new Map(out.destinations.map(d=>[d.id,d]));
const modifications=[],byteEvidence=[];
for(const d of out.destinations){
 const actual=scopeContentHash(d);
 if(actual===d.scopeContentSha256)continue;
 const serialized=JSON.stringify(Object.fromEntries(['kind','title','question','summary','scope','scientificStatus','readingCoverage','evidenceIds'].map(k=>[k,d[k]])));
 const matches=[];
 for(let i=0;i<serialized.length;i++){
  if(serialized.charCodeAt(i)<128)continue;
  for(let count=2;count<=4;count++){
   const corrupted=serialized.slice(0,i)+'\uFFFD'.repeat(count)+serialized.slice(i+1);
   if(hash(corrupted)===d.scopeContentSha256)matches.push({utf16Offset:i,originalCharacter:serialized[i],replacementCharacterCount:count,context:serialized.slice(Math.max(0,i-25),i+26)});
  }
 }
 byteEvidence.push({destinationId:d.id,oldHash:d.scopeContentSha256,correctHash:actual,exactCorruptionMatches:matches});
 modifications.push({table:'destinations',id:d.id,field:'scopeContentSha256',old:d.scopeContentSha256,new:actual});d.scopeContentSha256=actual;
}
const rows=new Map(out.sourceContributions.map(r=>[r.decisionId,r]));
for(const decision of out.decisions){
 const destination=byId.get(decision.subjectIds?.find(x=>byId.has(x)));
 if(destination&&decision.scopeContentSha256&&decision.scopeContentSha256!==destination.scopeContentSha256){modifications.push({table:'decisions',id:decision.id,field:'scopeContentSha256',old:decision.scopeContentSha256,new:destination.scopeContentSha256});decision.scopeContentSha256=destination.scopeContentSha256;}
 if(decision.type==='source_contribution'){
  const row=rows.get(decision.id);if(!row)throw Error('Missing exact row');
  const actual=sourceContributionContentHash(row,byId.get(row.destinationId).scopeContentSha256);
  if(actual!==decision.contributionContentSha256){modifications.push({table:'decisions',id:decision.id,field:'contributionContentSha256',old:decision.contributionContentSha256,new:actual});decision.contributionContentSha256=actual;}
 }
}
const rolePath=path.join(full,'canonical-role-admissions-v1/role-component.json'),role=read(rolePath),canonical=read(path.join(full,'canonical-pilot-admissions-v1/admitted-scope-role-operation-component.json'));
const allScopes=new Map([...out.destinations,...canonical.destinations].map(d=>[d.id,d]));
const roleDecisions=new Map(role.decisions.map(x=>[x.id,x]));
const roleMismatches=role.sourceContributions.filter(r=>roleDecisions.get(r.decisionId).contributionContentSha256!==sourceContributionContentHash(r,scopeContentHash(allScopes.get(r.destinationId)))).map(r=>r.decisionId);
if(roleMismatches.length)throw Error('Separate canonical role delta requires its own correction: '+JSON.stringify(roleMismatches));
const semanticScope=d=>Object.fromEntries(Object.entries(d).filter(([k])=>k!=='scopeContentSha256'));
if(JSON.stringify(original.destinations.map(semanticScope))!==JSON.stringify(out.destinations.map(semanticScope)))throw Error('Scientific destination content changed');
if(JSON.stringify(original.sourceContributions)!==JSON.stringify(out.sourceContributions))throw Error('Source role content changed');
const receipt={schemaVersion:'q025-lossless-hash-correction/1',status:'deterministic_representation_correction_no_scientific_change',input:pin(source),originalPolicyReceipt:pin(path.join(full,'admissions-v3/scope-role-admission-v3.json')),cause:'The earlier Python-to-Node helper appended raw Buffer chunks to a string. A UTF-8 character split between chunks can become replacement characters before JSON.parse. This file reads complete bytes with UTF-8 decoding once. Exact stored-hash matches to corrupted strings establish the observed three scope errors.',scopeCorruptionEvidence:byteEvidence,modifications,counts:{scopesChecked:out.destinations.length,sourceContributionsChecked:out.sourceContributions.length,scopeHashesCorrected:byteEvidence.length,contributionHashesCorrected:modifications.filter(x=>x.field==='contributionContentSha256').length,decisionScopeBindingsCorrected:modifications.filter(x=>x.table==='decisions'&&x.field==='scopeContentSha256').length,separate108RoleHashesChecked:role.sourceContributions.length,separate108RoleHashMismatches:0},scientificScopeFieldsChanged:0,sourceRoleRowsChanged:0,readingCoverageChanged:0,oldArtifactsUnchanged:true,policyAdmission:'Existing root policy and exact paired reviews remain the scientific authorization. This receipt corrects only deterministic bindings to those already stored exact fields.'};
fs.mkdirSync(here,{recursive:true});const rp=path.join(here,'hash-correction-receipt.json');fs.writeFileSync(rp,JSON.stringify(receipt,null,2)+'\n');
out.losslessHashCorrectionReceipt=pin(rp);out.correctedScopeHashes=Object.fromEntries(out.destinations.map(d=>[d.id,d.scopeContentSha256]));
const cp=path.join(here,'supported-scope-role-component-v4.json');fs.writeFileSync(cp,JSON.stringify(out)+'\n');
const report={schemaVersion:'q025-lossless-hash-report/1',component:{...pin(cp),bytes:fs.statSync(cp).size},receipt:pin(rp),counts:receipt.counts,allThreeScopeHashesExplained:byteEvidence.every(x=>x.exactCorruptionMatches.length===1),scientificContentChanged:false};
fs.writeFileSync(path.join(here,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
