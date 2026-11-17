import test from 'node:test';
import assert from 'node:assert/strict';
import {detailOverviewFrontier} from '../../web/detail-frontier.mjs';
test('zero-mass collection entry fits only its exact plotted destinations, with every unplotted entry still listed',()=>{
  const points=new Map([['a',{x:1,y:2}],['unrelated',{x:5,y:6}]]),before=structuredClone(points);
  const connections=[{destinationId:'a',navigationKind:'collection_access',traversal:'outgoing'},{destinationId:'b',navigationKind:'collection_access',traversal:'outgoing'},{destinationId:'a',navigationKind:'collection_access',traversal:'outgoing'},{destinationId:'unrelated',navigationKind:'collection_access',traversal:'incoming'}];
  const result=detailOverviewFrontier({selectedId:'collection',metadataOnly:true,points,connections,childrenOf:()=>[],parents:[],roots:['unrelated']});
  assert.deepEqual(result,{topics:['a','b'],plotted:['a'],collection:true});assert.deepEqual(points,before);assert.ok(!points.has('collection'));
});
test('scientific frontier keeps supplied narrower and cross-route points without treating collections as containment',()=>{
  const points=new Map(['a','b','c'].map(id=>[id,{x:0,y:0}]));
  const result=detailOverviewFrontier({selectedId:'a',metadataOnly:false,points,connections:[{destinationId:'c',navigationKind:'crosslink',traversal:'outgoing'}],childrenOf:id=>id==='a'?['b']:[],parents:[],roots:['a']});
  assert.deepEqual(result,{topics:['a','b','c'],plotted:['a','b','c'],collection:false});
});
