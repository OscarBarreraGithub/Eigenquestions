import test from 'node:test';
import assert from 'node:assert/strict';
import {loadLocalNavigator,createRuntime} from '../../lib/protocol/runtime.mjs';
import {createSession,currentState,normalizeState,applyAction,selectionTarget,exportSession,importSession} from '../../lib/protocol/session.mjs';
import {displayExcerpt,representativeInfo,previousVisitIndex} from '../../lib/protocol/presentation.mjs';
const sourceId='unit:0b1a39f68a400ae50d1d97ab6a9bd3e1b087d101231f4ebe49d49088b10b5b81';
let loaded;const data=()=>loaded??=loadLocalNavigator();

test('Q005 quoted method display is shorter while full source query and numerical view stay unchanged',async()=>{
 const {corpus,navigator}=await data(),runtime=createRuntime(navigator,corpus.manifest.corpusId);
 const start=runtime.action({type:'reset',query:'KK towers'}),direction=start.view.directions.find(d=>d.seedIds.includes(sourceId));
 assert.ok(direction);const before=JSON.stringify(start),info=representativeInfo(direction,start.view.nodes);
 assert.equal(info.kind,'Method');assert.equal(direction.lens,'combined');assert.match(info.sourceTitle,/6D origins/);
 const excerpt=displayExcerpt(direction.label,72);assert.ok(excerpt.length<=72);assert.match(excerpt,/one-loop/);
 assert.equal(JSON.stringify(start),before);
 const selected=runtime.action({type:'select',directionId:direction.id});assert.equal(currentState(selected.session).query,navigator.getEvidence([sourceId])[0].text);
 assert.deepEqual(selected.view,navigator.computeView(currentState(selected.session)));
 assert.equal(representativeInfo(direction,[],false).kind,'Source direction');assert.equal(representativeInfo(direction,start.view.nodes,true).kind,'Authored group');
});
test('Q005 six real selections revisit exact active-prefix states instead of appending a false deeper cycle',async()=>{
 const {corpus,navigator}=await data(),runtime=createRuntime(navigator,corpus.manifest.corpusId);
 let snapshot=runtime.action({type:'reset',query:'KK towers'});snapshot=runtime.action({type:'select',directionId:snapshot.view.directions.find(d=>d.seedIds.includes(sourceId)).id});
 const views=new Map([[snapshot.view.stateId,snapshot.view]]);let returns=0,maxLength=0;
 for(let index=0;index<6;index++){
  const target=selectionTarget(snapshot.session,snapshot.view.directions[0]),before=snapshot;
  snapshot=runtime.action({type:'select',directionId:snapshot.view.directions[0].id});
  assert.deepEqual(currentState(snapshot.session),target.state);
  if(target.revisitIndex>=0){returns++;assert.equal(snapshot.session.cursor,target.revisitIndex);assert.equal(snapshot.session.states.length,before.session.states.length);assert.deepEqual(snapshot.view,views.get(snapshot.view.stateId));}
  views.set(snapshot.view.stateId,snapshot.view);maxLength=Math.max(maxLength,snapshot.session.states.length);
  assert.equal(new Set(snapshot.session.states.map(state=>JSON.stringify(state))).size,snapshot.session.states.length);
 }
 assert.ok(returns>=2);assert.equal(maxLength,5);
 const restored=importSession(exportSession(snapshot.session));assert.deepEqual(restored,snapshot.session);
 assert.deepEqual(navigator.computeView(currentState(restored)),snapshot.view);
});
test('Q005 return comparison keeps constraints/focus distinct, ignores forward branch, and does not collapse typed refine',()=>{
 const a=createSession({corpusId:'fixture',computationId:'math',query:'A'}),base=currentState(a);
 const b=normalizeState({...base,query:'B',focusIds:['b']}),c=normalizeState({...base,query:'C',focusIds:['c']});
 const history={...a,states:[base,b,c],cursor:0};
 const direction={id:'to-c',query:'C',seedIds:['c']};
 assert.equal(selectionTarget(history,direction).revisitIndex,-1);
 const engine={computationId:'math',computeView(state){return {computationId:'math',corpusId:'fixture',stateId:state.id,nodes:[],directions:[direction]};}};
 const selected=applyAction(history,{type:'select',directionId:'to-c'},engine);assert.equal(selected.session.states.length,2);assert.deepEqual(currentState(selected.session),c);
 const sameWords={...history,cursor:2};assert.equal(selectionTarget(sameWords,{query:'B',seedIds:['different']}).revisitIndex,-1);
 const typed=applyAction(a,{type:'refine',query:'A',focusIds:[]},engine);assert.equal(typed.session.states.length,2);
 const legacy={...a,states:[base,b,base,b],cursor:3},serialized=JSON.stringify(legacy);
 assert.equal(previousVisitIndex(legacy,3),1);assert.equal(previousVisitIndex(legacy,2),0);assert.equal(JSON.stringify(legacy),serialized);
 assert.deepEqual(importSession(exportSession(legacy)),legacy);
});
