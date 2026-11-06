import {agentSnapshot,bridgeCall} from './runtime.mjs';

const actionSchema={type:'object',required:['type'],additionalProperties:false,properties:{
  type:{enum:['navigate','refine','pivot','broaden','select','back','forward','replay','reset']},
  query:{type:'string',maxLength:4000},focusIds:{type:'array',maxItems:100,items:{type:'string'}},
  intent:{enum:['explore','derive','phenomenology','recent','using']},workRelation:{enum:['on','using','either']},
  lens:{enum:['physical_question','method','combined']},constraints:{type:'object',additionalProperties:false,properties:{excludeIds:{type:'array',items:{type:'string'}},yearMin:{type:'integer'},yearMax:{type:'integer'}}},
  directionId:{type:'string'},index:{type:'integer',minimum:0},
}};
export const MCP_TOOLS=[
  {name:'navigator_state',description:'Inspect current resolved question, focus, ranked source candidates, about five directions, chart diagnostics and navigation history. This is a frozen corpus, not live literature.',inputSchema:{type:'object',additionalProperties:false,properties:{full:{type:'boolean'}}},annotations:{readOnlyHint:true}},
  {name:'navigator_search',description:'Search the full source corpus without changing the browser; retrieve stable evidence IDs for a concept or explicit ON/USING relation.',inputSchema:{type:'object',required:['query'],additionalProperties:false,properties:{query:{type:'string',maxLength:4000},intent:{enum:['explore','derive','phenomenology','recent','using']},workRelation:{enum:['on','using','either']},limit:{type:'integer',minimum:1,maximum:30}}},annotations:{readOnlyHint:true}},
  {name:'navigator_evidence',description:'Read source-linked evidence for up to 30 IDs before making physics claims. Extracted descriptions and retrieval affinities are not proofs.',inputSchema:{type:'object',required:['ids'],additionalProperties:false,properties:{ids:{type:'array',maxItems:30,items:{type:'string'}}}},annotations:{readOnlyHint:true}},
  {name:'navigator_navigate',description:'Run deterministic geometry and update connected browser. Resolve dialogue to query/intent/relation. refine refreshes context anchors; pivot clears them. select takes a current direction ID; back/forward/replay restore exact states.',inputSchema:actionSchema,annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
  {name:'navigator_export',description:'Export the reproducible session as portable JSON (no token or executable code).',inputSchema:{type:'object',additionalProperties:false,properties:{}},annotations:{readOnlyHint:true}},
  {name:'navigator_import',description:'Restore a previously exported same-corpus session and update the connected browser. Rejects mismatched corpus/version/state IDs.',inputSchema:{type:'object',required:['payload'],additionalProperties:false,properties:{payload:{type:'object'}}},annotations:{readOnlyHint:false,destructiveHint:false}},
];
export function createToolHandler(connection) {
  return async(name,args={})=>{
    if(name==='navigator_state')return agentSnapshot(await bridgeCall(connection,'/api/session'),{full:args.full});
    if(name==='navigator_search'){const {query,...options}=args;return bridgeCall(connection,'/api/search',{query,options});}
    if(name==='navigator_evidence')return bridgeCall(connection,'/api/evidence',args);
    if(name==='navigator_navigate')return agentSnapshot(await bridgeCall(connection,'/api/action',args));
    if(name==='navigator_export')return bridgeCall(connection,'/api/export');
    if(name==='navigator_import')return agentSnapshot(await bridgeCall(connection,'/api/import',args.payload));
    throw new Error(`Unknown tool: ${name}`);
  };
}
export async function handleMcpMessage(message,callTool) {
  if(!message||message.jsonrpc!=='2.0'||typeof message.method!=='string')return {jsonrpc:'2.0',id:message?.id??null,error:{code:-32600,message:'Invalid JSON-RPC request'}};
  if(message.id===undefined)return null;
  let result;
  if(message.method==='initialize')result={protocolVersion:['2024-11-05','2025-03-26','2025-06-18'].includes(message.params?.protocolVersion)?message.params.protocolVersion:'2025-06-18',capabilities:{tools:{listChanged:false}},serverInfo:{name:'eigenquestions-navigator',version:'1.0.0'},instructions:'Read the physics-navigator skill. Interpret conversation into a self-contained query plus intent and ON/USING relation; inspect source evidence. Coordinates are computed, never invented. Browser updates require the running local bridge.'};
  else if(message.method==='ping')result={};
  else if(message.method==='tools/list')result={tools:MCP_TOOLS};
  else if(message.method==='tools/call') {
    try {const value=await callTool(message.params?.name,message.params?.arguments??{});result={content:[{type:'text',text:JSON.stringify(value)}],structuredContent:Array.isArray(value)?{items:value}:value,isError:false};}
    catch(error){result={content:[{type:'text',text:error.message}],isError:true};}
  } else return {jsonrpc:'2.0',id:message.id,error:{code:-32601,message:`Method not found: ${message.method}`}};
  return {jsonrpc:'2.0',id:message.id,result};
}
