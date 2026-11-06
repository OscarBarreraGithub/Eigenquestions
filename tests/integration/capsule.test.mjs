import test from 'node:test';
import assert from 'node:assert/strict';
import {createSession,currentState} from '../../lib/protocol/session.mjs';
import {validateCapsule,createCapsule,capsuleCapabilities,encodeCapsuleBytes,decodeCapsuleBytes} from '../../lib/protocol/capsule.mjs';

export function authoredFixture(){return {schemaVersion:'1.0.0',kind:'eigenquestions-contextual-view',builder:{id:'independent-author',version:'2026.11'},context:{question:'Could these mechanisms be compared?',assumptions:['Compare mechanisms, not a proof'],openQuestions:['Which approximation fails?'],interpretations:[{claim:'Possible relation',evidenceIds:['source-a']}]},snapshot:{view:{stateId:'authored-state',corpusId:'external-reading-list',computationId:'external-builder-v7',query:'Could these mechanisms be compared?',nodes:[{id:'source-a',title:'Source A',sourceUrl:'https://arxiv.org/abs/2209.09249',evidence:{text:'Supplied source passage',claimStatus:'unverified author extraction'}},{id:'source-b',title:'Source B',sourceUrl:'javascript:alert(1)',evidence:{text:'A second passage'}}],directions:[{id:'group-one',label:'Author’s exact grouping <img src=x onerror=alert(1)>',memberIds:['source-a','source-b'],evidenceIds:['source-a']},{id:'group-two',label:'Overlapping comparison',memberIds:['source-a'],evidenceIds:['source-a']}],edges:[{source:'group-one',target:'group-two',type:'author-hypothesis',evidenceIds:['source-a']}],chart:null,diagnostics:{},warnings:['Author interpretation requires paper checking']}},continuation:{mode:'snapshot-only',originStateId:'authored-state',description:'Read the supplied sources; this builder is unavailable here.',actions:[]}};}

test('authored overlapping groups/context/relations round-trip exactly through JSON and gzip',async()=>{
 const original=authoredFixture(), before=JSON.stringify(original); assert.equal(validateCapsule(original),original);
 for(const gzip of [false,true])assert.deepEqual(await decodeCapsuleBytes(await encodeCapsuleBytes(original,{gzip})),original);
 assert.equal(JSON.stringify(original),before);assert.deepEqual(capsuleCapabilities(original,'native').continue,false);
});
test('malformed references, resource limits and executable values fail before display',()=>{
 for(const mutate of [c=>c.snapshot.view.directions[0].memberIds.push('absent'),c=>c.snapshot.view.edges[0].target='missing',c=>c.context.bad=()=>{},c=>c.snapshot.view.nodes[0].evidence.sourceRecordIds='bad',c=>c.snapshot.view.diagnostics.contextTerms='bad',c=>c.context.many=Array(100001).fill(0),c=>c.snapshot.view.nodes[0].evidence.text='x'.repeat(64001)]){const value=authoredFixture();mutate(value);assert.throws(()=>validateCapsule(value));}
 const deep=authoredFixture();let cursor=deep.context;for(let i=0;i<35;i++)cursor=cursor.next={};assert.throws(()=>validateCapsule(deep),/deeply/);
});
test('typed affine planes reject strings, nonfinite entries and nonorthogonal basis',()=>{
 const value=authoredFixture();for(const point of [...value.snapshot.view.nodes,...value.snapshot.view.directions]){point.x=0;point.y=0;}
 value.snapshot.view.chart={kind:'affine-plane',dimension:2,center:[0,0],basis:[[1,0],[0,1]],scale:1,thickness:1,metric:'fixture'};
 assert.equal(validateCapsule(value),value);
 for(const bad of ['bad',null,Infinity]){const c=structuredClone(value);c.snapshot.view.chart.basis[0][0]=bad;assert.throws(()=>validateCapsule(c));}
 value.snapshot.view.chart.basis=[[1,0],[1,0]];assert.throws(()=>validateCapsule(value),/orthonormal/);
});
test('native identity/version and executable author continuation are separate capabilities',()=>{
 const session=createSession({corpusId:'fixture',computationId:'pinned',query:'comparison'}),state=currentState(session);
 const input=authoredFixture();input.snapshot.session=session;Object.assign(input.snapshot.view,{stateId:state.id,corpusId:'fixture',computationId:'pinned'});input.continuation.originStateId=state.id;
 const native=createCapsule(input.snapshot);assert.equal(capsuleCapabilities(native,'pinned').recompute,true);
 native.builder.version='future';assert.equal(capsuleCapabilities(native,'pinned').recompute,false);
 input.continuation.mode='native-actions';input.continuation.actions=[{id:'group-one',label:'Explicit native query',action:{type:'refine',query:'comparison in a controlled approximation',focusIds:['source-a']}}];
 assert.equal(capsuleCapabilities(validateCapsule(input),'pinned').continue,true);
 input.continuation.actions[0].action={type:'select',directionId:'group-one'};assert.equal(capsuleCapabilities(input,'pinned').continue,false);
});
