// Read-only native account usage probe; never starts a model thread/turn.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),local=resolve(here,'native-local');mkdirSync(local,{recursive:true});
const configPath=resolve(local,'execution.json');
if(!existsSync(configPath))throw Error('Private execution config required; no account lookup guesses.');
const config=JSON.parse(readFileSync(configPath,'utf8'));const {codexAccountEnvironment}=await import(config.helperPath);
const native=spawn(config.nativeBinary,['--no-daemon','-c','cli_auth_credentials_store="file"','-c','forced_login_method="chatgpt"','-c','model_provider="openai"','app-server','--stdio'],{env:codexAccountEnvironment(config.accountDir),cwd:local,stdio:['pipe','pipe','pipe']});
let id=0;const pending=new Map();let stderr='';native.stderr.on('data',d=>{if(stderr.length<16000)stderr+=d.toString().slice(0,16000-stderr.length);});native.stdin.on('error',()=>{});
const request=(method,params)=>new Promise((res,rej)=>{const n=++id,t=setTimeout(()=>{pending.delete(n);rej(Error('bounded RPC timeout'));},15000);pending.set(n,{res,rej,t});native.stdin.write(JSON.stringify({id:n,method,params})+'\n');});
createInterface({input:native.stdout}).on('line',line=>{let x;try{x=JSON.parse(line);}catch{return;}const p=pending.get(x.id);if(p){pending.delete(x.id);clearTimeout(p.t);x.error?p.rej(Error('native RPC rejected')):p.res(x.result);}});
const deadline=setTimeout(()=>native.kill('SIGTERM'),40000);
try{
 await request('initialize',{clientInfo:{name:'q025_read_only_quota_probe',version:'1.0'},capabilities:{experimentalApi:true}});native.stdin.write(JSON.stringify({method:'initialized',params:{}})+'\n');
 const result=await request('account/rateLimits/read',{excludeResetCreditDetails:true,supportsLunaReserve:false});const timestamp=new Date().toISOString();
 writeFileSync(resolve(local,'quota-probe.raw.json'),JSON.stringify({timestamp,result},null,2)+'\n');
 const candidates=[result.rateLimits,...Object.values(result.rateLimitsByLimitId||{})].filter(Boolean);const seen=new Set(),applicable=[];
 for(const x of candidates){if(x.normalModelSlug&&x.normalModelSlug!=='gpt-6-astra')continue;const y={model:x.normalModelSlug??null,scope:x.normalModelSlug?'model_bucket':'reported_account_bucket',primary:x.primary?{usedPercent:x.primary.usedPercent,windowDurationMins:x.primary.windowDurationMins??null,resetsAt:x.primary.resetsAt??null}:null,secondary:x.secondary?{usedPercent:x.secondary.usedPercent,windowDurationMins:x.secondary.windowDurationMins??null,resetsAt:x.secondary.resetsAt??null}:null};const k=JSON.stringify(y);if(!seen.has(k)){seen.add(k);applicable.push(y);}}
 const report={timestamp,ordinaryUsageAllowed:result.ordinaryUsageAllowed??null,applicableUsage:applicable,modelTurnsStarted:0,interpretation:'Null/missing is unknown. Used percentages are backend-reported, not projected completion capacity or reset recovery.'};writeFileSync(resolve(local,'quota-probe.sanitized.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}catch{writeFileSync(resolve(local,'quota-probe.failure.json'),JSON.stringify({timestamp:new Date().toISOString(),status:'read_failed',stderr},null,2)+'\n');console.log(JSON.stringify({timestamp:new Date().toISOString(),ordinaryUsageAllowed:null,status:'read_failed',modelTurnsStarted:0}));process.exitCode=1;}
finally{clearTimeout(deadline);native.stdin.end();native.kill('SIGTERM');for(const p of pending.values()){clearTimeout(p.t);p.rej(Error('probe closed'));}pending.clear();}
