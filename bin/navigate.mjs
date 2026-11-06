#!/usr/bin/env node
import {readFile, writeFile, unlink} from 'node:fs/promises';
import path from 'node:path';
import {PROJECT_ROOT, DEFAULT_CONNECTION, loadLocalNavigator, createRuntime, readConnection, bridgeCall, agentSnapshot} from '../lib/protocol/runtime.mjs';
import {startBridge} from '../lib/protocol/bridge.mjs';

const argv = process.argv.slice(2), command = argv.shift() ?? 'help', options = {};
for (let i=0;i<argv.length;i++) {
  if (!argv[i].startsWith('--')) throw new Error(`Unexpected argument ${argv[i]}`);
  const key=argv[i].slice(2); options[key] = ['full'].includes(key) ? true : argv[++i];
  if (options[key] === undefined) throw new Error(`Missing value for --${key}`);
}
const print = value => process.stdout.write(JSON.stringify(value,null,2)+'\n');
try {
  if (command === 'help') {
    process.stdout.write(`Eigenquestions local agent interface (Node 22+)\n\nnode bin/navigate.mjs serve [--port 4317] [--connection FILE]\nnode bin/navigate.mjs state [--full]\nnode bin/navigate.mjs navigate --query "KK towers" [--intent derive] [--relation on]\nnode bin/navigate.mjs refine --query "KK towers as dark matter"\nnode bin/navigate.mjs pivot --query "black hole information"\nnode bin/navigate.mjs select --direction ID\nnode bin/navigate.mjs back | forward | broaden | reset\nnode bin/navigate.mjs replay --index 1\nnode bin/navigate.mjs search --query "dark dimension"\nnode bin/navigate.mjs evidence --ids ID,ID\nnode bin/navigate.mjs export --out session.json\nnode bin/navigate.mjs import --file session.json\nnode bin/navigate.mjs action --json '{"type":"refine","query":"..."}'\nnode bin/navigate.mjs compute --query "KK towers" [--session FILE] [--out snapshot.json]\n\nAll connected commands accept --connection FILE (default ${DEFAULT_CONNECTION}).\nserve prints local/public browser attachment URLs; keep this process running.\ncompute is an offline deterministic JSON artifact; serve gives the same-origin live HTML renderer.\n`);
  } else if (command === 'serve') {
    const {corpus,navigator} = await loadLocalNavigator(options.corpus);
    const runtime = createRuntime(navigator,corpus.manifest.corpusId,{query:options.query??''});
    if (options.session) runtime.import(JSON.parse(await readFile(options.session,'utf8')));
    const bridge = await startBridge({runtime,staticDir:options.static??path.join(PROJECT_ROOT,'dist'),port:Number(options.port??4317),allowedOrigins:(options.origins??'https://eigenquestions.com').split(',')});
    const filename = options.connection??DEFAULT_CONNECTION;
    const connection = {schemaVersion:'1.0.0',url:bridge.url,token:bridge.token,pid:process.pid};
    await writeFile(filename,JSON.stringify(connection,null,2)+'\n',{mode:0o600});
    print({connectionFile:filename,localUrl:`${bridge.url}#token=${bridge.token}`,publicUrl:`https://eigenquestions.com/#bridge=${encodeURIComponent(bridge.url)}&token=${bridge.token}`,note:'Public browser loopback access depends on browser permissions. The local URL uses the same renderer without cross-origin access.'});
    let closing=false;
    const close=async()=>{if(closing)return;closing=true;await bridge.close();try { const saved=JSON.parse(await readFile(filename,'utf8'));if(saved.token===bridge.token)await unlink(filename); }catch{};process.exit(0);};
    process.once('SIGINT',close);process.once('SIGTERM',close);
  } else if (command === 'compute') {
    const {corpus,navigator}=await loadLocalNavigator(options.corpus),runtime=createRuntime(navigator,corpus.manifest.corpusId);
    if(options.session)runtime.import(JSON.parse(await readFile(options.session,'utf8')));
    const snapshot=options.query!==undefined?runtime.action(actionFromOptions('navigate',options)):runtime.snapshot();
    if(options.out)await writeFile(options.out,JSON.stringify(snapshot,null,2)+'\n');else print(snapshot);
  } else {
    const connection=await readConnection(options.connection);
    let result;
    if(command==='state')result=agentSnapshot(await bridgeCall(connection,'/api/session'),{full:options.full});
    else if(command==='search')result=await bridgeCall(connection,'/api/search',{query:options.query??'',options:{intent:options.intent??'explore',workRelation:options.relation??(options.intent==='using'?'using':'either'),limit:Number(options.limit??10)}});
    else if(command==='evidence')result=await bridgeCall(connection,'/api/evidence',{ids:(options.ids??'').split(',').filter(Boolean)});
    else if(command==='export'){result=await bridgeCall(connection,'/api/export');if(options.out){await writeFile(options.out,JSON.stringify(result,null,2)+'\n');result={saved:options.out,corpusId:result.corpusId};}}
    else if(command==='import'){if(!options.file)throw new Error('--file is required');result=agentSnapshot(await bridgeCall(connection,'/api/import',JSON.parse(await readFile(options.file,'utf8'))),{full:options.full});}
    else result=agentSnapshot(await bridgeCall(connection,'/api/action',command==='action'?JSON.parse(options.json):actionFromOptions(command,options)),{full:options.full});
    print(result);
  }
} catch(error) {process.stderr.write(`Eigenquestions: ${error.message}\n`);process.exitCode=1;}
function actionFromOptions(type,opts){
  const action={type};
  for(const [flag,key]of [['query','query'],['intent','intent'],['relation','workRelation'],['lens','lens'],['direction','directionId']])if(opts[flag]!==undefined)action[key]=opts[flag];
  if(opts.ids!==undefined)action.focusIds=opts.ids.split(',').filter(Boolean);
  if(opts.index!==undefined)action.index=Number(opts.index);
  if(opts['year-min']||opts['year-max'])action.constraints={...(opts['year-min']?{yearMin:Number(opts['year-min'])}:{}),...(opts['year-max']?{yearMax:Number(opts['year-max'])}:{})};
  return action;
}
