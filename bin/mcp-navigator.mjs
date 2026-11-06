#!/usr/bin/env node
import {createInterface} from 'node:readline';
import {readConnection} from '../lib/protocol/runtime.mjs';
import {createToolHandler,handleMcpMessage} from '../lib/protocol/mcp.mjs';

const args=process.argv.slice(2),index=args.indexOf('--connection'),filename=index>=0?args[index+1]:undefined;
let connection;
const callTool=async(name,arguments_)=>{connection??=await readConnection(filename);return createToolHandler(connection)(name,arguments_);};
const lines=createInterface({input:process.stdin,crlfDelay:Infinity});
// Sequential dispatch preserves navigation order; stdout is JSON-RPC only.
for await(const line of lines){
  if(!line.trim())continue;
  let response;
  try {if(line.length>2*1024*1024)throw new Error('Message exceeds 2 MiB');response=await handleMcpMessage(JSON.parse(line),callTool);}
  catch(error){response={jsonrpc:'2.0',id:null,error:{code:-32700,message:error.message}};}
  if(response)process.stdout.write(JSON.stringify(response)+'\n');
}
