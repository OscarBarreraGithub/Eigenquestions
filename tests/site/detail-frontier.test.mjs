import test from 'node:test';
import assert from 'node:assert/strict';
import {detailOverviewFrontier,validateNavigationSchematic} from '../../web/detail-frontier.mjs';
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

test('a supplied zero-mass schematic collection anchor is shown without becoming a destination choice',()=>{
  const anchor={x:0,y:0,mass:0,coordinateBasis:'schematic_collection_anchor'},points=new Map([['collection',anchor],['a',{x:2,y:0}]]);
  const result=detailOverviewFrontier({selectedId:'collection',metadataOnly:true,points,connections:[{destinationId:'a',navigationKind:'collection_access',traversal:'outgoing'}],childrenOf:()=>[],parents:[],roots:['collection']});
  assert.deepEqual(result,{topics:['a'],plotted:['collection','a'],collection:true});assert.equal(points.get('collection'),anchor);assert.equal(anchor.mass,0);
});

test('schematic routes bind actual recorded endpoints/direction and never acquire collection mass',()=>{
  const records=new Map([['collection',{metadataOnly:true}],['a',{kind:'region'}]]),relation={id:'route-1',source:'collection',target:'a',type:'related_question'},chart={nodes:[{destinationId:'collection',mass:0,coordinateBasis:'schematic_collection_anchor'},{destinationId:'a'}],edges:[{source:'collection',target:'a',type:'related_question',kind:'recorded_navigation',relationId:'route-1'}]};
  validateNavigationSchematic(chart,records,[relation]);
  for(const altered of [{...relation,source:'a',target:'collection'},{...relation,type:'narrower'},{...relation,id:'unbound'}])assert.throws(()=>validateNavigationSchematic(chart,records,[altered]),/exact recorded direction/);
  const wrong=structuredClone(chart);wrong.nodes[0].mass=1;assert.throws(()=>validateNavigationSchematic(wrong,records,[relation]),/zero mass/);
});
