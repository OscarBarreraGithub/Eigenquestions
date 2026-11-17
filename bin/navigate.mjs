#!/usr/bin/env node
import {readFile, writeFile, unlink} from 'node:fs/promises';
import path from 'node:path';
import {PROJECT_ROOT, DEFAULT_CONNECTION, loadLocalNavigator, loadLocalAtlas, createRuntime, readConnection, bridgeCall, agentSnapshot} from '../lib/protocol/runtime.mjs';
import {startBridge} from '../lib/protocol/bridge.mjs';

const argv=process.argv.slice(2),requested=argv.shift()??'help',help=['help','--help','-h'].includes(requested)||argv.includes('--help')||argv.includes('-h'),command=help?'help':requested,options={};
if(help)argv.length=0;
for (let i=0;i<argv.length;i++) {
  if (!argv[i].startsWith('--')) throw new Error(`Unexpected argument ${argv[i]}`);
  const key=argv[i].slice(2); options[key] = ['full'].includes(key) ? true : argv[++i];
  if (options[key] === undefined) throw new Error(`Missing value for --${key}`);
}
const print = value => process.stdout.write(JSON.stringify(value,null,2)+'\n');
try {
  if (command === 'help') {
    process.stdout.write(`Eigenquestions local agent interface (Node 22+)\n\nnode bin/navigate.mjs serve [--port 4317] [--connection FILE]\nnode bin/navigate.mjs serve --atlas data/atlas/ID/VERSION [--destination ID]\nnode bin/navigate.mjs state [--full]\nnode bin/navigate.mjs navigate --query "KK towers" [--intent derive] [--relation on]\nnode bin/navigate.mjs refine --query "KK towers as dark matter"\nnode bin/navigate.mjs pivot --query "black hole information"\nnode bin/navigate.mjs select --direction ID\nnode bin/navigate.mjs back | forward | broaden | reset\nnode bin/navigate.mjs replay --index 1\nnode bin/navigate.mjs search --query "dark dimension"\nnode bin/navigate.mjs evidence --ids ID,ID\nnode bin/navigate.mjs sources [--destination ID] [--collection membership|contributions] [--offset 0] [--limit 20]\nnode bin/navigate.mjs connections [--destination ID]\nnode bin/navigate.mjs context --id UNIT_ID [--section objects] [--offset 0] [--limit 20]\nnode bin/navigate.mjs inspect-source --origin UNIT_ID --source-relation RELATION_ID --object OBJECT_ID --unit METHOD_UNIT_ID --expected-revision N\nnode bin/navigate.mjs close-source --expected-revision N\nnode bin/navigate.mjs export --out session.json\nnode bin/navigate.mjs import --file session.json\nnode bin/navigate.mjs action --json '{"type":"refine","query":"..."}'\nnode bin/navigate.mjs compute --query "KK towers" [--session FILE] [--out snapshot.json]\nnode bin/navigate.mjs compute --atlas data/atlas/ID/VERSION --destination ID\n\nAll connected commands accept --connection FILE (default ${DEFAULT_CONNECTION}).\nFor every visible mutation, pass --expected-revision N captured before interpreting the request.\nOmission retains legacy unguarded behavior; a conflict never retries or restamps your action.\nserve prints local/public browser attachment URLs; keep this process running.\ncompute is an offline deterministic JSON artifact; serve gives the same-origin live HTML renderer.\n`);
  } else if (command === 'serve') {
    const loaded = options.atlas ? await loadLocalAtlas(options.atlas) : await loadLocalNavigator(options.corpus), {navigator}=loaded;
    const corpusId=loaded.atlas?.manifest.corpusId || loaded.corpus.manifest.corpusId;
    const initial=options.atlas ? (options.destination ? {selector:{...navigator.initialState.selector,destinationId:options.destination}} : {}) : {query:options.query??''};
    if(options.atlas&&options.query)throw new Error('Prepared mode uses --destination; use search for title/alias lookup.');
    if(options.atlas)await navigator.prepareState?.({...navigator.initialState,...initial});
    const runtime = createRuntime(navigator,corpusId,initial);
    if (options.session) await runtime.import(JSON.parse(await readFile(options.session,'utf8')));
    const bridge = await startBridge({runtime,staticDir:options.static??path.join(PROJECT_ROOT,'dist'),port:Number(options.port??4317),allowedOrigins:(options.origins??'https://eigenquestions.com').split(',')});
    const filename = options.connection??DEFAULT_CONNECTION;
    const connection = {schemaVersion:'1.0.0',url:bridge.url,token:bridge.token,pid:process.pid};
    await writeFile(filename,JSON.stringify(connection,null,2)+'\n',{mode:0o600});
    print({connectionFile:filename,localUrl:`${bridge.url}#token=${bridge.token}`,publicUrl:`https://eigenquestions.com/#bridge=${encodeURIComponent(bridge.url)}&token=${bridge.token}`,note:'Public browser loopback access depends on browser permissions. The local URL uses the same renderer without cross-origin access.'});
    let closing=false;
    const close=async()=>{if(closing)return;closing=true;await bridge.close();try { const saved=JSON.parse(await readFile(filename,'utf8'));if(saved.token===bridge.token)await unlink(filename); }catch{};process.exit(0);};
    process.once('SIGINT',close);process.once('SIGTERM',close);
  } else if (command === 'compute') {
    const loaded=options.atlas?await loadLocalAtlas(options.atlas):await loadLocalNavigator(options.corpus),{navigator}=loaded;
    if(options.atlas)await navigator.prepareState?.({...navigator.initialState,...(options.destination?{selector:{...navigator.initialState.selector,destinationId:options.destination}}:{})});
    const runtime=createRuntime(navigator,loaded.atlas?.manifest.corpusId||loaded.corpus.manifest.corpusId,options.atlas&&options.destination?{selector:{...navigator.initialState.selector,destinationId:options.destination}}:{});
    if(options.atlas&&options.query)throw new Error('Prepared mode uses --destination; use search for title/alias lookup.');
    if(options.session)await runtime.import(JSON.parse(await readFile(options.session,'utf8')));
    const snapshot=options.query!==undefined?await runtime.action(actionFromOptions('navigate',options)):runtime.snapshot();
    if(options.out)await writeFile(options.out,JSON.stringify(snapshot,null,2)+'\n');else print(snapshot);
  } else {
    const connection=await readConnection(options.connection);
    const revisionFlag=options['expected-revision'];
    if(revisionFlag!==undefined&&(!/^[0-9]+$/.test(revisionFlag)||!Number.isSafeInteger(Number(revisionFlag))))throw new Error('--expected-revision must be a nonnegative safe integer');
    const guard={expectedRevision:revisionFlag===undefined?undefined:Number(revisionFlag)};
    let result;
    if(command==='state')result=agentSnapshot(await bridgeCall(connection,'/api/session'),{full:options.full});
    else if(command==='search')result=await bridgeCall(connection,'/api/search',{query:options.query??'',options:{intent:options.intent??'explore',workRelation:options.relation??(options.intent==='using'?'using':'either'),limit:Number(options.limit??10)}});
    else if(command==='evidence')result=await bridgeCall(connection,'/api/evidence',{ids:(options.ids??'').split(',').filter(Boolean)});
    else if(command==='sources')result=await bridgeCall(connection,'/api/sources',{...(options.collection?{collection:options.collection}:{}),...(options.destination?{destinationId:options.destination}:{}),offset:Number(options.offset||0),limit:Number(options.limit||30),...(options.lens?{lens:options.lens}:{}),...(options['include-context']!==undefined?{includeContext:options['include-context']===true||options['include-context']==='true'}:{})});
    else if(command==='connections')result=await bridgeCall(connection,'/api/connections',{...(options.destination?{destinationId:options.destination}:{}),offset:Number(options.offset||0),limit:Number(options.limit||100)});
    else if(command==='context')result=await bridgeCall(connection,'/api/context',{unitId:options.id,section:options.section,offset:options.offset===undefined?undefined:Number(options.offset),limit:options.limit===undefined?undefined:Number(options.limit),scope:options.scope,kinds:options.kinds?.split(','),objectIds:options['object-ids']?.split(',')});
    else if(command==='export'){result=await bridgeCall(connection,'/api/export');if(options.out){await writeFile(options.out,JSON.stringify(result,null,2)+'\n');result={saved:options.out,corpusId:result.corpusId};}}
    else if(command==='import'){if(!options.file)throw new Error('--file is required');result=agentSnapshot(await bridgeCall(connection,'/api/import',JSON.parse(await readFile(options.file,'utf8')),guard),{full:options.full});}
    else result=agentSnapshot(await bridgeCall(connection,'/api/action',command==='action'?JSON.parse(options.json):actionFromOptions(command,options),guard),{full:options.full});
    print(result);
  }
} catch(error) {process.stderr.write(error.code==='revision_conflict'?JSON.stringify({error:error.message,code:error.code,current:agentSnapshot(error.current)})+'\n':`Eigenquestions: ${error.message}\n`);process.exitCode=1;}
function actionFromOptions(type,opts){
  const action={type};
  if(type==='inspect-source')action.sourceInspection={originUnitId:opts.origin,relationId:opts['source-relation'],objectId:opts.object,unitId:opts.unit};
  for(const [flag,key]of [['query','query'],['intent','intent'],['relation','workRelation'],['lens','lens'],['direction','directionId']])if(opts[flag]!==undefined)action[key]=opts[flag];
  if(opts.ids!==undefined)action.focusIds=opts.ids.split(',').filter(Boolean);
  if(opts.index!==undefined)action.index=Number(opts.index);
  if(opts['year-min']||opts['year-max'])action.constraints={...(opts['year-min']?{yearMin:Number(opts['year-min'])}:{}),...(opts['year-max']?{yearMax:Number(opts['year-max'])}:{})};
  return action;
}
