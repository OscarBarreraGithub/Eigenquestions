import test from 'node:test';
import assert from 'node:assert/strict';
import {createAtlasNavigator} from '../../lib/geometry/prepared-atlas.mjs';
test('scientific cross-routes and broader scope stay ahead of a large alphabetically earlier source-facet list',()=>{
 const source={id:'witness',kind:'vocabulary',title:'Test only',evidence:{text:'Synthetic navigation-order test; no scientific admission.'}};
 const destination=(id,title)=>({id,title,question:title,kind:'question',metadataOnly:true,summary:'Test',scope:{},evidenceIds:[source.id],scientificStatus:'test',placementStatus:'test',provenance:{test:true}});
 const destinations=[destination('current','Current'),destination('narrow','Z narrow'),destination('route','Z typed cross-route'),destination('broad','Z broader')];
 const relation=(id,from,to,type)=>({id,source:from,target:to,type,status:'test',rationale:'Synthetic order test',evidenceIds:[source.id]});
 const relations=[relation('n','current','narrow','narrower'),relation('r','current','route','application_of'),relation('b','broad','current','narrower')];
 relations[1].title='Inspect the reviewed conditional application';relations[2].title='Follow the recorded narrower scope';relations[2].incomingTitle='Return to the reviewed broader setting';
 for(let i=0;i<100;i++){destinations.push(destination('facet-'+i,'A source '+i));relations.push(relation('s'+i,'current','facet-'+i,'source_question'));}
 const catalog={destinations,sources:[source],memberships:[],relations};
 const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'priority-fixture',atlasVersion:'v1',corpusId:'test',corpusContentHash:'a'.repeat(64),entryDestinationId:'current',scope:{description:'Synthetic order test'},files:{catalog:{path:'catalog.json',sha256:'b'.repeat(64)}}};
 const nav=createAtlasNavigator({manifest,catalog,manifestSha256:'c'.repeat(64)}),view=nav.computeView(nav.initialState);
 assert.deepEqual(view.directions.slice(0,3).map(d=>d.selector.destinationId),['narrow','route','broad']);assert.equal(nav.connections('current',{limit:100}).total,103);assert.equal(view.atlas.connectionCount,103);const all=[...nav.connections('current',{limit:100}).items,...nav.connections('current',{offset:100,limit:100}).items];assert.equal(all.filter(r=>r.type==='source_question').length,100);
 assert.equal(view.directions[1].label,relations[1].title);assert.equal(view.directions[2].label,relations[2].incomingTitle);
 const next=nav.createSession({selector:{...nav.initialState.selector,destinationId:'route'}}),arrived=nav.computeView(next.states[0]);assert.equal(arrived.atlas.destination.title,'Z typed cross-route');assert.equal(arrived.directions[0].label,'Current');assert.equal(arrived.directions[0].relation.routeTitle,relations[1].title);assert.equal(arrived.directions[0].relation.traversal,'incoming');
});
