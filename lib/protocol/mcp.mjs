import {agentSnapshot,bridgeCall} from './runtime.mjs';

const actionSchema={type:'object',required:['type'],additionalProperties:false,properties:{
  type:{enum:['navigate','refine','pivot','broaden','select','back','forward','replay','reset','inspect-source','close-source']},
  query:{type:'string',maxLength:4000},focusIds:{type:'array',maxItems:100,items:{type:'string'}},
  intent:{enum:['explore','derive','phenomenology','recent','using']},workRelation:{enum:['on','using','either']},
  lens:{enum:['physical_question','method','combined']},constraints:{type:'object',additionalProperties:false,properties:{excludeIds:{type:'array',items:{type:'string'}},yearMin:{type:'integer'},yearMax:{type:'integer'}}},
  directionId:{type:'string'},index:{type:'integer',minimum:0},
  expectedRevision:{type:'integer',minimum:0,description:'Revision captured before interpreting the requested change. Omitted only for legacy unguarded callers.'},
  sourceInspection:{type:'object',required:['originUnitId','relationId','objectId','unitId'],additionalProperties:false,properties:Object.fromEntries(['originUnitId','relationId','objectId','unitId'].map(key=>[key,{type:'string',maxLength:300}]))},
  selector:{type:'object',required:['kind','atlasId','atlasVersion','destinationId'],additionalProperties:false,properties:{kind:{const:'atlas-destination'},atlasId:{type:'string'},atlasVersion:{type:'string'},destinationId:{type:'string'}}},
}};
export const MCP_TOOLS=[
  {name:'navigator_state',description:'Inspect the current scoped atlas selector, sources, history and recorded directions, normally about 1–15; classification entrances may have more. Optional native exploration has five computed directions. Coverage is frozen, not live literature.',inputSchema:{type:'object',additionalProperties:false,properties:{full:{type:'boolean'}}},annotations:{readOnlyHint:true}},
  {name:'navigator_search',description:'Search without changing the browser. Prepared mode loads the versioned fine index and matches titles/aliases; native mode searches source text. This does not interpret paragraphs or replace independent research.',inputSchema:{type:'object',required:['query'],additionalProperties:false,properties:{query:{type:'string',maxLength:4000},intent:{enum:['explore','derive','phenomenology','recent','using']},workRelation:{enum:['on','using','either']},limit:{type:'integer',minimum:1,maximum:30}}},annotations:{readOnlyHint:true}},
  {name:'navigator_evidence',description:'Read source-linked evidence for up to 30 IDs before making physics claims. Extracted descriptions and retrieval affinities are not proofs.',inputSchema:{type:'object',required:['ids'],additionalProperties:false,properties:{ids:{type:'array',maxItems:30,items:{type:'string'}}}},annotations:{readOnlyHint:true}},
  {name:'navigator_sources',description:'Read prepared source membership or select collection:contributions for separately admitted source-role review observations, qualifications and distinct relationship counts, including excerpts. Read-only; contributions never imply membership or method applicability. Membership filters apply only to the default membership collection.',inputSchema:{type:'object',additionalProperties:false,properties:{destinationId:{type:'string'},collection:{enum:['membership','contributions']},includeContext:{type:'boolean'},offset:{type:'integer',minimum:0},limit:{type:'integer',minimum:1,maximum:100},intent:{enum:['explore','derive','phenomenology','recent','using']},lens:{enum:['combined','physical_question','method']},workRelation:{enum:['on','using','either']},constraints:actionSchema.properties.constraints}},annotations:{readOnlyHint:true}},
  {name:'navigator_connections',description:'Read all recorded incident destination connections, including incoming links without reversing scientific direction. Shared-source organizational access is labeled separately with scope-wide witness counts and immutable proof links. Supply relationId and includeProof:true to read one complete checksummed evidence/review record; it implies neither containment nor method applicability. Prepared atlas only.',inputSchema:{type:'object',additionalProperties:false,properties:{destinationId:{type:'string'},relationId:{type:'string',maxLength:200},includeProof:{type:'boolean'},offset:{type:'integer',minimum:0},limit:{type:'integer',minimum:1,maximum:100}}},annotations:{readOnlyHint:true}},
  {name:'navigator_context',description:'Read one bounded page of pinned source context; defaults to 20 objects. Relations pages include exact mapped endpoint inspection actions; unmapped endpoints stay readable without a follow action. Use section objects|relations|evidence|assessments and offset to continue. Totals and coverage are explicit. Read withheld reader notes before interpreting source relations; absent filtered records do not prove scientific absence.',inputSchema:{type:'object',required:['unitId'],additionalProperties:false,properties:{unitId:{type:'string',maxLength:300},section:{enum:['objects','relations','evidence','assessments']},offset:{type:'integer',minimum:0},limit:{type:'integer',minimum:1,maximum:40},scope:{enum:['direct_record_relation','shared_extraction_window_context','same_paper_context']},kinds:{type:'array',maxItems:40,items:{type:'string'}},objectIds:{type:'array',maxItems:40,items:{type:'string'}}}},annotations:{readOnlyHint:true}},
  {name:'navigator_navigate',description:'Update the connected browser through the shared controller. Supply expectedRevision captured before interpreting the request; on conflict retain the proposed action and newer state, never restamp it. Resolve prepared scope first, then navigate with an exact atlas selector or select a current direction ID. inspect-source follows an exact sourceRoutes action while preserving the physical destination; close-source clears that inspection. Back/forward/replay restore states. Native query/refine/pivot is an explicit alternative. Verify navigator_state browser render acknowledgement.',inputSchema:actionSchema,annotations:{readOnlyHint:false,destructiveHint:false,idempotentHint:false}},
  {name:'navigator_export',description:'Export the reproducible session as portable JSON (no token or executable code).',inputSchema:{type:'object',additionalProperties:false,properties:{}},annotations:{readOnlyHint:true}},
  {name:'navigator_import',description:'Restore a same-corpus session and update the browser. Supply expectedRevision captured before deciding to import; retain the original payload and newer state on conflict. Rejects mismatched corpus/version/state IDs.',inputSchema:{type:'object',required:['payload'],additionalProperties:false,properties:{payload:{type:'object'},expectedRevision:actionSchema.properties.expectedRevision}},annotations:{readOnlyHint:false,destructiveHint:false}},
];
export function createToolHandler(connection) {
  return async(name,args={})=>{
    if(name==='navigator_state')return agentSnapshot(await bridgeCall(connection,'/api/session'),{full:args.full});
    if(name==='navigator_search'){const {query,...options}=args;return bridgeCall(connection,'/api/search',{query,options});}
    if(name==='navigator_evidence')return bridgeCall(connection,'/api/evidence',args);
    if(name==='navigator_sources')return bridgeCall(connection,'/api/sources',args);
    if(name==='navigator_connections')return bridgeCall(connection,'/api/connections',args);
    if(name==='navigator_context')return bridgeCall(connection,'/api/context',args);
    if(name==='navigator_navigate'){const {expectedRevision,...action}=args;return agentSnapshot(await bridgeCall(connection,'/api/action',action,{expectedRevision}));}
    if(name==='navigator_export')return bridgeCall(connection,'/api/export');
    if(name==='navigator_import')return agentSnapshot(await bridgeCall(connection,'/api/import',args.payload,{expectedRevision:args.expectedRevision}));
    throw new Error(`Unknown tool: ${name}`);
  };
}
export async function handleMcpMessage(message,callTool) {
  if(!message||message.jsonrpc!=='2.0'||typeof message.method!=='string')return {jsonrpc:'2.0',id:message?.id??null,error:{code:-32600,message:'Invalid JSON-RPC request'}};
  if(message.id===undefined)return null;
  let result;
  if(message.method==='initialize')result={protocolVersion:['2024-11-05','2025-03-26','2025-06-18'].includes(message.params?.protocolVersion)?message.params.protocolVersion:'2025-06-18',capabilities:{tools:{listChanged:false}},serverInfo:{name:'eigenquestions-navigator',version:'1.0.0'},instructions:'Read the physics-navigator skill. Resolve a prepared scoped destination through lookup and recorded connections, inspect source evidence and full relation proof when needed, then update the browser with the revision captured before interpretation. Native query exploration is an explicit alternative. Verify rendered acknowledgement; coordinates are never invented.'};
  else if(message.method==='ping')result={};
  else if(message.method==='tools/list')result={tools:MCP_TOOLS};
  else if(message.method==='tools/call') {
    try {const value=await callTool(message.params?.name,message.params?.arguments??{});result={content:[{type:'text',text:JSON.stringify(value)}],structuredContent:Array.isArray(value)?{items:value}:value,isError:false};}
    catch(error){const details={error:error.message,...(error.code==='revision_conflict'?{code:error.code,current:agentSnapshot(error.current)}:{})};result={content:[{type:'text',text:JSON.stringify(details)}],structuredContent:details,isError:true};}
  } else return {jsonrpc:'2.0',id:message.id,error:{code:-32601,message:`Method not found: ${message.method}`}};
  return {jsonrpc:'2.0',id:message.id,result};
}
