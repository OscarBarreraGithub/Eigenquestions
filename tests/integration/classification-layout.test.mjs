import test from 'node:test';
import assert from 'node:assert/strict';
import {classificationDisplayLayout} from '../../web/classification-layout.mjs';
test('classification display preserves every full label with separate touch targets at mobile and desktop widths',()=>{
  const nodes=Array.from({length:17},(_,i)=>({destinationId:`field-${i}`,x:i===16?10:i*.01,y:i%3*.01,title:i%2?'Condensed Matter, Materials & Applied Physics':'Gravitation, Cosmology & Astrophysics'}));
  for(const width of [358,748]){
    const display=classificationDisplayLayout(nodes,{width});assert.equal(display.nodes.length,17);
    for(const node of display.nodes){assert.equal(node.lines.join(' '),nodes.find(x=>x.destinationId===node.destinationId).title);assert.ok(node.width>=44&&node.height>=44);assert.ok(node.x-node.width/2>=0&&node.x+node.width/2<=width);assert.ok(node.y-node.height/2>=0&&node.y+node.height/2<=display.height);}
    for(let i=0;i<17;i++)for(let j=i+1;j<17;j++){const a=display.nodes[i],b=display.nodes[j];assert.ok(Math.abs(a.x-b.x)>=(a.width+b.width)/2||Math.abs(a.y-b.y)>=(a.height+b.height)/2);}
  }
  assert.equal(nodes[0].x,0);assert.equal(nodes[16].x,10);
});
