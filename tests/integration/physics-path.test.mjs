import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeState} from '../../lib/protocol/session.mjs';
import {physicsPath,sourceInspectionHistory} from '../../web/physics-path.mjs';
import {paperTitle} from '../../web/paper-title.mjs';
const selector=id=>({kind:'atlas-destination',atlasId:'fixture',atlasVersion:'v1',destinationId:id});
const state=(id,extra={})=>normalizeState({corpusId:'fixture',computationId:'test',query:id,selector:selector(id),...extra});
const focus=id=>({originUnitId:'unit:origin',relationId:'source-relation',objectId:'obj:'+id,unitId:'unit:'+id});
test('source inspection projects to one physics column without removing exact history or future replay',()=>{
 const states=[state('a'),state('a',{sourceInspection:focus('one')}),state('a',{sourceInspection:focus('two')}),state('a'),state('b')],session={states,cursor:2},before=structuredClone(session);
 const shown=physicsPath(session,{activeOnly:true});assert.equal(shown.length,1);assert.deepEqual(shown[0].indices,[0,1,2]);assert.equal(shown[0].index,2);assert.equal(shown[0].current,true);
 const all=physicsPath(session);assert.equal(all.length,2);assert.equal(all[0].index,2);assert.equal(all[0].endIndex,3);assert.equal(all[1].index,4);assert.deepEqual(session,before);
 assert.deepEqual(sourceInspectionHistory(session).map(row=>[row.index,row.active]),[[1,false],[2,true]]);
 for(const cursor of [0,1,2,3])assert.equal(physicsPath({...session,cursor},{activeOnly:true}).length,1);
 assert.equal(physicsPath({...session,cursor:4},{activeOnly:true}).length,2);
});
test('perspective changes and native exploration retain meaningful separate steps',()=>{
 const states=[state('a'),state('a',{lens:'method'}),state('a',{lens:'method',sourceInspection:focus('one')}),state('b'),state('a')];assert.equal(physicsPath({states,cursor:4}).length,4);
 const native=normalizeState({corpusId:'fixture',computationId:'test',query:'A'});assert.equal(physicsPath({states:[native,native],cursor:1}).length,2);
});
test('paper titles support only safe simple numeric math text and retain unfamiliar TeX literally',()=>{
 assert.equal(paperTitle('Vacua in AdS$_{4}$'),'Vacua in AdS₄');assert.equal(paperTitle('$AdS_{4}$ and $M^{2}$'),'AdS₄ and M²');
 for(const original of ['A $\\frac{x}{y}$ title','<img src=x onerror=alert(1)>','$E=mc^2$','A $100 cost'])assert.equal(paperTitle(original),original);
});
