#!/usr/bin/env node
/** Bounded post-deployment verification. No credentials or publication tools. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const ASSETS=[
  ['/', 'index.html'], ['/build-info.json','build-info.json'],
  ['/data/manifest.json','data/manifest.json'], ['/app.js','app.js'],
  ['/compute-worker.js','compute-worker.js'], ['/styles.css','styles.css'],
  ['/lib/geometry/index.mjs','lib/geometry/index.mjs'],
  ['/lib/geometry/identity.mjs','lib/geometry/identity.mjs'],
  ['/lib/protocol/session.mjs','lib/protocol/session.mjs'],
  ['/lib/protocol/capsule.mjs','lib/protocol/capsule.mjs'],
  ['/lib/protocol/presentation.mjs','lib/protocol/presentation.mjs'],
  ['/schemas/contextual-view.schema.json','schemas/contextual-view.schema.json'],
  ['/llms.txt','llms.txt'], ['/robots.txt','robots.txt'], ['/sitemap.xml','sitemap.xml'],
  ['/docs/agent-interface.md','docs/agent-interface.md'],
  ['/skills/physics-navigator/SKILL.md','skills/physics-navigator/SKILL.md'],
  ['/overview.html','overview.html'], ['/overview.js','overview.js'], ['/overview.css','overview.css'],
  ['/data/overview/manifest.json','data/overview/manifest.json'], ['/data/overview/map.json','data/overview/map.json'],
];
const RETIRED=[
  '/quiz/','/taste/','/explore/','/explore/tree/','/review/','/submit/','/leaderboard/',
  '/api/pair','/api/stats','/api/vote','/api/health','/api/submit','/api/leaderboard',
  '/api/review/submissions','/api/review/approve','/api/review/reject',
];
const sha=buffer=>createHash('sha256').update(buffer).digest('hex');
async function boundedResponse(response,maxBytes=2*1024*1024){
  const reader=response.body?.getReader();if(!reader)return Buffer.alloc(0);
  const chunks=[];let size=0;
  try{while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>maxBytes){await reader.cancel();throw new Error('RESPONSE_TOO_LARGE');}chunks.push(value);}}
  finally{reader.releaseLock();}
  return Buffer.concat(chunks);
}
async function pooled(tasks,limit=4){
  const result=new Array(tasks.length);let cursor=0;
  await Promise.all(Array.from({length:Math.min(limit,tasks.length)},async()=>{while(cursor<tasks.length){const index=cursor++;result[index]=await tasks[index]();}}));
  return result;
}
export async function checkPublication({origin='https://eigenquestions.com',dist,timeoutMs=12000}){
  const base=new URL(origin);
  if(!['http:','https:'].includes(base.protocol)||base.username||base.password||base.search||base.hash||base.pathname!=='/')throw new Error('Origin must be a plain HTTP(S) origin without credentials, query or path');
  if(!Number.isInteger(timeoutMs)||timeoutMs<100||timeoutMs>30000)throw new Error('Timeout must be between 100 and 30000 ms');
  const expected=await Promise.all(ASSETS.map(async([route,file])=>({route,file,sha256:sha(await readFile(path.join(dist,file)))})));
  const manifestBuffer=await readFile(path.join(dist,'data/manifest.json'));
  const manifest=JSON.parse(manifestBuffer);
  const engineText=await readFile(path.join(dist,'lib/geometry/index.mjs'),'utf8');
  const identityText=await readFile(path.join(dist,'lib/geometry/identity.mjs'),'utf8');
  const engineVersion=engineText.match(/ENGINE_VERSION\s*=\s*['"]([^'"]+)/)?.[1];
  const sourcePin=identityText.match(/ENGINE_SOURCE_SHA256\s*=\s*['"]([a-f0-9]{64})/)?.[1];
  const parametersPin=identityText.match(/PARAMETERS_SHA256\s*=\s*['"]([a-f0-9]{64})/)?.[1];
  if(!engineVersion||!sourcePin||!parametersPin||sha(Buffer.from(engineText))!==sourcePin)throw new Error('Local engine identity is absent or stale; rebuild the verified release before checking publication');
  const releaseFingerprint=sha(Buffer.from(JSON.stringify(expected.map(({route,sha256})=>({route,sha256})))));
  const tasks=expected.map(item=>async()=>{
    try{
      const url=new URL(item.route,base);url.searchParams.set('__eq_verify',releaseFingerprint.slice(0,16));
      const response=await fetch(url,{headers:{'Cache-Control':'no-cache'},signal:AbortSignal.timeout(timeoutMs),redirect:'follow'});
      const data=await boundedResponse(response),observedSha256=sha(data);
      return {path:item.route,status:response.status,bytes:data.length,expectedSha256:item.sha256,observedSha256,passed:response.status===200&&observedSha256===item.sha256};
    }catch(error){return {path:item.route,passed:false,error:error.name==='TimeoutError'?'TIMEOUT':error.message==='RESPONSE_TOO_LARGE'?'RESPONSE_TOO_LARGE':'FETCH_FAILED'};}
  });
  const assets=await pooled(tasks);
  const retired=await pooled(RETIRED.flatMap(route=>['GET','POST'].map(method=>async()=>{
    try{
      const url=new URL(route,base);url.searchParams.set('__eq_verify',releaseFingerprint.slice(0,16));
      const response=await fetch(url,{method,headers:{'Cache-Control':'no-cache',...(method==='POST'?{'Content-Type':'application/json'}:{})},...(method==='POST'?{body:'{}'}:{}),signal:AbortSignal.timeout(timeoutMs),redirect:'follow'});
      await boundedResponse(response,256*1024);
      return {path:route,method,status:response.status,redirected:response.redirected,passed:method==='GET'?response.status===404:[404,405].includes(response.status)};
    }catch(error){return {path:route,method,passed:false,error:error.name==='TimeoutError'?'TIMEOUT':error.message==='RESPONSE_TOO_LARGE'?'RESPONSE_TOO_LARGE':'FETCH_FAILED'};}
  })));
  return {
    schemaVersion:'1.0.0',kind:'eigenquestions-publication-check',checkedAt:new Date().toISOString(),origin:base.origin,
    expected:{releaseFingerprint,corpusId:manifest.corpusId,computationId:`${engineVersion}:${sourcePin}:${parametersPin}:${sha(manifestBuffer)}`},
    assets,retiredRoutes:retired,
    summary:{assetChecks:assets.length,matchedAssets:assets.filter(x=>x.passed).length,retiredRouteChecks:retired.length,retiredRoutePasses:retired.filter(x=>x.passed).length},
    passed:assets.every(x=>x.passed)&&retired.every(x=>x.passed),
    scope:'Checks exact deployed entrypoint/module/manifest hashes and retired route status. Full corpus shard hashes are verified by the local build and browser loader; this bounded check does not redownload all shards or prove browser rendering.',
  };
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const args=process.argv.slice(2),options={dist:path.resolve(fileURLToPath(new URL('../../dist/',import.meta.url)))};let out;
  try{
    for(let i=0;i<args.length;i+=2){const name=args[i],value=args[i+1];if(value===undefined)throw new Error(`Missing value for ${name}`);if(name==='--origin')options.origin=value;else if(name==='--dist')options.dist=path.resolve(value);else if(name==='--out')out=value;else if(name==='--timeout-ms')options.timeoutMs=Number(value);else throw new Error(`Unknown option ${name}`);}
    const report=await checkPublication(options);const output=JSON.stringify(report,null,2)+'\n';if(out)await writeFile(out,output);process.stdout.write(output);if(!report.passed)process.exitCode=1;
  }catch(error){const report={schemaVersion:'1.0.0',kind:'eigenquestions-publication-check',passed:false,error:error.code==='ENOENT'?'LOCAL_RELEASE_ASSET_MISSING':error.message};const output=JSON.stringify(report,null,2)+'\n';if(out)await writeFile(out,output);process.stdout.write(output);process.exitCode=1;}
}
