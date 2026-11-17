// Deterministic compilation only. This module never connects to a native model.
import {readFileSync,writeFileSync,mkdirSync,copyFileSync,existsSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {verifyPrepared,childReadiness,materializeParent} from './runner.mjs';
const HERE=dirname(fileURLToPath(import.meta.url)),ROOT=resolve(HERE,'../native-local/recovery-successors-v2'),EVALUATION=resolve(HERE,'../..');
const read=p=>JSON.parse(readFileSync(p,'utf8')),hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const campaign=verifyPrepared(ROOT),name=process.argv[2]||'run-001';
if(!/^run-\d{3}$/.test(name))throw Error('Use an explicit run-NNN receipt directory');
const output=resolve(ROOT,'preflight',name);if(existsSync(output))throw Error('Preserve the prior preflight; use a new run number');
mkdirSync(output,{recursive:true});copyFileSync(resolve(ROOT,'execution.json'),resolve(output,'execution.json'));
const results=[];
for(const j of campaign.jobs){
 const source=resolve(ROOT,'jobs',j.jobId,'request.json'),req=read(source),children=childReadiness(req,EVALUATION);
 if(j.dependsOn||children.status!=='ready'){
  results.push({jobId:j.jobId,status:'deferred_until_dependencies_complete',dependsOn:j.dependsOn||null,childReadiness:children});continue;
 }
 const dir=resolve(output,'jobs',j.jobId);mkdirSync(dir,{recursive:true});copyFileSync(source,resolve(dir,'request.json'));
 const built=materializeParent(dir,req,output),packet=read(built.packetPath),prompt=readFileSync(built.promptPath,'utf8'),schema=JSON.stringify(read(resolve(EVALUATION,req.schemaPath)));
 const budget={promptCharacters:prompt.length,schemaCharacters:schema.length,maxResponseCharacters:req.maxOutputCharacters,reasoningAndProtocolHeadroomTokens:16000,dispatchGuardTokens:220000};
 budget.conservativeCombinedTokens=Math.ceil((budget.promptCharacters+budget.schemaCharacters+budget.maxResponseCharacters)/3)+16000;
 results.push({jobId:j.jobId,status:budget.conservativeCombinedTokens<=220000?'ready_materialized_sources_verified':'blocked_context_guard',packetSha256:hash(built.packetPath),promptSha256:hash(built.promptPath),schemaSha256:req.schemaSha256,sourceUnitCount:packet.units.length,primaryExcerptCount:packet.evidence.length,childArtifacts:built.request.childArtifacts?.length||0,budget});
}
verifyPrepared(ROOT);
const receipt={schemaVersion:'q025-successor-preflight/1',campaignSha256:hash(resolve(ROOT,'campaign.json')),runnerSha256:hash(resolve(HERE,'runner.mjs')),nativeLaunches:0,sourceHashVerification:'Every actually materialized excerpt and archived source file verified by the same dispatch function. Future dependency-bearing packets are compiled and checked only after their receipts exist.',actualJobDirectoriesMaterialized:0,results};
writeFileSync(resolve(output,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
writeFileSync(resolve(HERE,`preflight-${name}.json`),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({nativeLaunches:0,materialized:results.filter(x=>x.status==='ready_materialized_sources_verified').length,deferred:results.filter(x=>x.status.startsWith('deferred')).length,blocked:results.filter(x=>x.status.startsWith('blocked')).length,receipt:`preflight-${name}.json`}));
if(results.some(x=>x.status.startsWith('blocked')))process.exitCode=1;
