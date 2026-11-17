/** Explicit editorial examples from one pinned admitted component; no classifier. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {destinationPresentation} from '../../../../lib/protocol/display-editorial.mjs';
const root=new URL('../../../../',import.meta.url),artifactPath='research/q025/evaluation/full-pass/admissions-v2/supported-scope-role-component-v2.json';
const bytes=await readFile(new URL(artifactPath,root)),artifactSha256=createHash('sha256').update(bytes).digest('hex');
if(artifactSha256!=='3c5daa26911fb883e434a3a808fcaf1835acd825450e994e1875ccf82d9f2864')throw new Error('Pinned admitted component changed');
const input=JSON.parse(bytes),fields=['kind','title','question','summary','scope','scientificStatus','readingCoverage','evidenceIds'];
const hash=d=>createHash('sha256').update(JSON.stringify(Object.fromEntries(fields.map(key=>[key,d[key]])))).digest('hex');
const selections=[
  {index:107,notes:[['conventions',0,'reading']]},
  {index:904,notes:[['assumptions',0,'workflow']],summary:'Geometry, protected amplitudes and brane/CFT data connect several physical targets. Dimensions, regimes and evidential status remain distinct; shared geometry, modularity or partition-function language does not establish question identity.'},
  {index:915,notes:[['conventions',2,'workflow']],summary:'Constructions, obstructions, unstable extrema, statistical metastability and consistency tests span different dimensions and supersymmetries. Shared formal tools can connect sources with different physical targets.'},
  {index:1019,notes:[['assumptions',2,'reading'],['conventions',2,'workflow'],['conventions',3,'workflow']],summary:'A discovery family spanning different systems, dimensions and mechanisms. Construction, formulation, scalar stability, effective-theory control, spectra and cosmological evolution are separate targets.',readingRemove:'This new parent scope is a proposal requiring independent review or explicit coordinator adjudication. '},
  {index:1021,notes:[['assumptions',3,'reading'],['conventions',3,'workflow']],summary:'Geometric construction, mirror and period calculations, degeneration theory, internal metrics and their physical applications form connected targets. Related questions retain their distinct systems, mechanisms and approximations.',readingRemove:' This parent scope is a new proposal.'}
];
const records=selections.map(({index,notes,summary,readingRemove})=>{
 const source=input.destinations[index];if(hash(source)!==source.scopeContentSha256)throw new Error(`Invalid original hash ${source.id}`);
 const record={id:source.id,...Object.fromEntries(fields.map(key=>[key,source[key]])),scopeContentSha256:source.scopeContentSha256};
 const displayEditorial={schemaVersion:'1.0.0',kind:'presentation-only',scopeContentSha256:record.scopeContentSha256,origin:{artifactPath,artifactSha256,recordPointer:`/destinations/${index}`},relocations:notes.map(([field,n,category])=>({path:`/scope/${field}/${n}`,originalText:source.scope[field][n],category,reason:category==='reading'?'Describes the extent or attribution of source reading, not a physical premise.':'Describes organization or review provenance, not a physical premise or convention.'}))};
 if(summary)displayEditorial.summary={text:summary,originalText:source.summary,reason:'Present the physical subject and distinctions without treating historical proposal-stage wording as current status. Original scientific definition remains unchanged.'};
 if(readingRemove){const originalText=source.readingCoverage.readingLimit;if(!originalText.includes(readingRemove))throw new Error('Reading history text changed');displayEditorial.readingLimit={path:'/readingCoverage/readingLimit',text:originalText.replace(readingRemove,''),originalText,reason:'Move the historical proposal-stage sentence into record history; retain every statement of reading coverage and limitation.'};}
 record.displayEditorial=displayEditorial;destinationPresentation(record);if(hash(record)!==hash(source))throw new Error('Scientific definition changed');return record;
});
const control=input.destinations[530];const result={schemaVersion:'q025-display-editorial-examples/1',status:'presentation_proposal_not_installed',source:{artifactPath,artifactSha256},scope:'Five explicit examples only; no automatic matching or global editorial clearance. Final scope hashes must still match before use.',records,unchangedPhysicsControl:{id:control.id,scopeContentSha256:control.scopeContentSha256,path:'/scope/conventions/0',text:control.scope.conventions[0]},noScientificDefinitionChanged:true};
await writeFile(new URL('./examples.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({records:records.length,originSha256:artifactSha256,output:fileURLToPath(new URL('./examples.json',import.meta.url))}));
