import test from 'node:test';
import assert from 'node:assert/strict';
import {classificationChartDisplay} from '../../web/classification-layout.mjs';

const nodes=Array.from({length:211},(_,i)=>({destinationId:`node-${i}`,component:i<197?0:1,depth:i<16||i===197?0:1,x:Math.sin(i*.37)+(i<197?0:3),y:Math.cos(i*.17),title:i%2?'Condensed Matter, Materials & Applied Physics':'Gravitation, Cosmology & Astrophysics'}));
test('classification graph preserves all coordinates up to a uniform transform within each recorded component',()=>{
  const original=structuredClone(nodes);
  for(const width of [358,748,1132,1536]){
    const display=classificationChartDisplay(nodes,{width});assert.equal(display.points.length,211);assert.equal(display.frames.length,1);
    for(const component of [0,1]){
      const source=nodes.filter(n=>n.component===component),points=display.points.filter(n=>n.component===component),a=source[0],b=source[1],p=points[0],q=points[1],scale=(q.x-p.x)/(b.x-a.x);
      assert.ok(scale>0);
      for(let i=0;i<source.length;i++){
        assert.ok(Math.abs(points[i].x-(p.x+(source[i].x-a.x)*scale))<1e-8);
        assert.ok(Math.abs(points[i].y-(p.y+(source[i].y-a.y)*scale))<1e-8);
        assert.ok(points[i].x>=0&&points[i].x<=width&&points[i].y>=0&&points[i].y<=display.height);
      }
    }
    assert.equal(display.callouts.length,width<900?0:17);
  }
  assert.deepEqual(nodes,original);
});
test('desktop field callouts retain full names and separate accessible targets tied to exact graph anchors',()=>{
  for(const width of [900,1132,1536]){
    const display=classificationChartDisplay(nodes,{width});
    for(const box of display.callouts){
      assert.equal(box.lines.join(' '),nodes.find(n=>n.destinationId===box.destinationId).title);
      assert.equal(box.anchor,display.points.find(n=>n.destinationId===box.destinationId));
      assert.ok(box.width>=44&&box.height>=44&&box.x>=0&&box.x+box.width<=width&&box.y>=0&&box.y+box.height<=display.height);
    }
    for(let i=0;i<17;i++)for(let j=i+1;j<17;j++){const a=display.callouts[i],b=display.callouts[j];assert.ok(a.x+a.width<=b.x||b.x+b.width<=a.x||a.y+a.height<=b.y||b.y+b.height<=a.y);}
  }
});
