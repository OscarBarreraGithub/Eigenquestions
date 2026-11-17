#!/usr/bin/env node
/** Thin read-only adapter over the existing CLI/runtime; no independent retrieval. */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const [accessFile,command='info',...args]=process.argv.slice(2),options={};
try{
  if(!accessFile)throw new Error('Usage: node read.mjs ACCESS.json info|describe|compute|search|connections|sources|context|evidence [--arguments]');
  const allowed={info:[],describe:['destination'],compute:['destination'],search:['query','limit'],connections:['destination','offset','limit','relation-id','include-proof'],sources:['destination','collection','offset','limit','lens'],context:['id','section','offset','limit','scope','kinds','object-ids'],evidence:['ids']};
  if(!Object.hasOwn(allowed,command))throw new Error('Only explicit read-only commands are available; no mutations or model calls');
  for(let i=0;i<args.length;i++){const key=args[i].replace(/^--/,'');if(args[i]!==`--${key}`||!allowed[command].includes(key)||Object.hasOwn(options,key))throw new Error('Unsupported argument');options[key]=key==='include-proof'?true:args[++i];if(options[key]===undefined)throw new Error('Missing argument value');}
  const access=JSON.parse(await readFile(accessFile,'utf8'));if(access.kind!=='q025-preholdout-readonly-access')throw new Error('Wrong access phase');
  const manifestBytes=await readFile(path.join(access.atlas,'manifest.json'));if(createHash('sha256').update(manifestBytes).digest('hex')!==access.manifestSha256)throw new Error('Frozen manifest changed');
  const manifest=JSON.parse(manifestBytes);if(manifest.scope.deliveryState!=='partial_pre_holdout_candidate'||manifest.scope.sourceAccountingComplete!==false||manifest.scope.reservedQuestionCount!==43)throw new Error('Wrong frozen pre-holdout scope');
  let result;
  if(command==='info')result={manifestSha256:access.manifestSha256,runtimeCommit:access.runtimeCommit,scope:manifest.scope,staticEntry:access.staticEntry,skill:access.skill,publicationStatus:access.publicationStatus,readOnly:true,liveBrowserMutation:false};
  else if(command==='compute')result=JSON.parse(execFileSync(process.execPath,[path.join(access.application,'bin/navigate.mjs'),'compute','--atlas',access.atlas,...(options.destination?['--destination',options.destination]:[])],{encoding:'utf8',maxBuffer:16*1024*1024}));
  else{
    const {loadLocalAtlas,createRuntime}=await import(pathToFileURL(path.join(access.application,'lib/protocol/runtime.mjs')));
    const {atlas,navigator}=await loadLocalAtlas(access.atlas),runtime=createRuntime(navigator,atlas.manifest.corpusId),destinationId=options.destination||manifest.entryDestinationId;
    const page={...(options.offset?{offset:Number(options.offset)}:{}),...(options.limit?{limit:Number(options.limit)}:{})};
    if(command==='describe'){await navigator.prepareDestination?.(destinationId);const destination=navigator.destination(destinationId);result={destination,selector:{...navigator.initialState.selector,destinationId:destination.id},preparedFragment:'#'+new URLSearchParams({atlas:manifest.atlasId,version:manifest.atlasVersion,destination:destination.id}),publicationStatus:'Not installed on the public site; this selector is bound to the frozen test package.'};}
    if(command==='search')result=await runtime.search(options.query||'',{limit:Number(options.limit||10)});
    if(command==='connections')result=await runtime.connections({destinationId,...page,...(options['relation-id']?{relationId:options['relation-id']}:{}),...(options['include-proof']?{includeProof:true}:{})});
    if(command==='sources')result=await runtime.sources({destinationId,...page,...(options.collection?{collection:options.collection}:{}),...(options.lens?{lens:options.lens}:{})});
    if(command==='context')result=await runtime.context({unitId:options.id,...page,...Object.fromEntries(['section','scope'].filter(k=>options[k]).map(k=>[k,options[k]])),...(options.kinds?{kinds:options.kinds.split(',')}:{}),...(options['object-ids']?{objectIds:options['object-ids'].split(',')}:{})});
    if(command==='evidence')result=runtime.evidence((options.ids||'').split(',').filter(Boolean));
  }
  process.stdout.write(JSON.stringify({manifestSha256:access.manifestSha256,readOnly:true,result},null,2)+'\n');
}catch(error){process.stderr.write(`Pre-holdout read: ${error.message}\n`);process.exitCode=1;}
