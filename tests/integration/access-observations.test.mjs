import test from 'node:test';
import assert from 'node:assert/strict';
import {createAtlasNavigator,validateAtlas} from '../../lib/geometry/prepared-atlas.mjs';
import {createRuntime} from '../../lib/protocol/runtime.mjs';
function fixture(){
 const source={id:'unit:a',paperId:'paper-a',title:'Synthetic source',year:2024,evidence:{text:'Synthetic transport test; no scientific admission.'}};
 const destination=id=>({id,kind:'question',title:id,question:`Question ${id}`,summary:'Test only',scope:{},evidenceIds:[source.id],scientificStatus:'test',placementStatus:'test',provenance:{test:true}});
 const catalog={destinations:['current','narrow','science','broad','access','facet'].map(destination),sources:[source],memberships:[{destinationId:'current',unitId:source.id,weight:1,role:'on',year:2024,lens:'physical_question'}],relations:[]};
 const relation=(id,from,to,type)=>({id,source:from,target:to,type,status:'test',rationale:'Exact source organizational test',evidenceIds:[source.id]});
 catalog.relations=[relation('facet','current','facet','source_question'),relation('access','current','access','related_question'),relation('science','current','science','premise_check'),relation('narrow','current','narrow','narrower'),relation('broad','broad','current','narrower')];
 const access=catalog.relations[1];access.title='Do not reverse or reuse this as a scientific action';access.provenance={navigationBasis:'same_source_organizational_access'};access.organizationalAccess={uniqueWitnessCount:7,countScope:'scope_wide',supportCertificate:{path:'access/bucket.json',sha256:'a'.repeat(64),recordId:'access'},certificateSha256:'b'.repeat(64),policyReceipt:{path:'access/policy.json',sha256:'c'.repeat(64)}};
 const manifest={schemaVersion:'1.0.0',kind:'eigenquestions-atlas',atlasId:'test',atlasVersion:'v1',corpusId:'test',corpusContentHash:'a'.repeat(64),entryDestinationId:'current',scope:{description:'Synthetic test'},files:{catalog:{path:'catalog.json',sha256:'b'.repeat(64)}}};
 return {manifest,catalog,manifestSha256:'c'.repeat(64)};
}
function contribution(decisionId,qualification){return {unitId:'unit:a',paperId:'paper-a',destinationId:'access',role:'addresses',basis:'description_checked',evidenceRefs:[{kind:'description',unitId:'unit:a'}],decisionId,qualification,scopeContentSha256:'a'.repeat(64),browserVectorRow:0,sourceRow:0,lens:'physical_question',contributionStatus:'accepted_typed_contribution',provenance:{doesNotAssertDirectHome:true,doesNotAssertEquivalence:true,doesNotAssertMethodApplicability:true}};}
test('shared-source access stays subordinate, scope-wide, incoming-readable and usable with zero membership',async()=>{
 const x=fixture(),nav=createAtlasNavigator(x),state=nav.initialState,view=nav.computeView(state);
 assert.deepEqual(view.directions.map(d=>d.selector.destinationId),['narrow','science','broad','access','facet']);
 const access=view.directions[3];assert.equal(access.label,'access');assert.equal(access.navigationKind,'shared_source_access');assert.equal(access.relation.type,'related_question');assert.match(access.relation.accessNotice,/not containment/);
 const filtered=nav.createSession({workRelation:'using'}),fv=nav.computeView(filtered.states[0]);assert.equal(fv.atlas.matchingSourceCount,0);assert.equal(fv.directions.find(d=>d.selector.destinationId==='access').relation.organizationalAccess.uniqueWitnessCount,7);
 const next=nav.createSession({selector:{...state.selector,destinationId:'access'}}),arrived=nav.computeView(next.states[0]);assert.equal(arrived.atlas.membershipCount,0);assert.equal(arrived.directions[0].relation.traversal,'incoming');assert.equal(arrived.directions[0].label,'current');assert.equal(arrived.directions[0].relation.source,'current');assert.equal(arrived.directions[0].relation.target,'access');
 const runtime=createRuntime(nav,'test'),before=JSON.stringify(runtime.snapshot()),read=await runtime.connections({destinationId:'access'});assert.deepEqual(read.items[0].organizationalAccess,x.catalog.relations[1].organizationalAccess);assert.equal(JSON.stringify(runtime.snapshot()),before);
});
test('distinct admitted observations preserve qualifications while counting one relationship and zero USING',async()=>{
 const x=fixture(),d=x.catalog.destinations.find(d=>d.id==='access');d.sourceContributions=[contribution('decision:one','First admitted condition.'),contribution('decision:two','Separate admitted review qualification.')];d.sourceContributionObservationCount=2;d.sourceContributionRelationshipCount=1;validateAtlas(x.manifest,x.catalog);
 const nav=createAtlasNavigator(x),runtime=createRuntime(nav,'test'),page=await runtime.sources({destinationId:'access',collection:'contributions',limit:1});assert.equal(page.total,2);assert.equal(page.observationCount,2);assert.equal(page.relationshipCount,1);assert.equal(page.items[0].qualification,d.sourceContributions[0].qualification);assert.equal((await runtime.sources({destinationId:'access',collection:'contributions',offset:1})).items[0].qualification,d.sourceContributions[1].qualification);assert.equal(nav.sources('access',{workRelation:'using'}).total,0);assert.equal(nav.sources('access').total,0);
 d.sourceContributions[1].decisionId='decision:one';assert.throws(()=>validateAtlas(x.manifest,x.catalog),/duplicate typed source contribution observation/);d.sourceContributions[1].decisionId='decision:two';d.sourceContributionRelationshipCount=2;assert.throws(()=>validateAtlas(x.manifest,x.catalog),/incorrect sourceContributionRelationshipCount/);
});
test('access metadata cannot masquerade as containment or filtered witness counts',()=>{
 for(const change of [r=>r.type='narrower',r=>delete r.provenance.navigationBasis,r=>r.organizationalAccess.countScope='filtered',r=>r.organizationalAccess.supportCertificate.path='../outside.json',r=>r.organizationalAccess.uniqueWitnessCount=0]){const x=fixture();change(x.catalog.relations[1]);assert.throws(()=>validateAtlas(x.manifest,x.catalog),/organizational/);}
});

test('one foreground destination preserves multiple directed scientific and organizational reasons',()=>{
 const x=fixture(),science=x.catalog.relations.find(r=>r.id==='science'),access=x.catalog.relations.find(r=>r.id==='access');
 science.title='Inspect the explicitly reviewed premise';science.qualification='Only under the stated model conditions.';
 access.target='science';
 x.catalog.relations.push({...science,id:'reverse-science',source:'science',target:'current',type:'application_of',title:'An outgoing phrase that must never be reused backwards'});
 const nav=createAtlasNavigator(x),view=nav.computeView(nav.initialState),directions=view.directions.filter(d=>d.selector.destinationId==='science');
 assert.equal(directions.length,1);const choice=directions[0];assert.equal(choice.routeCount,3);assert.equal(choice.relations.length,3);assert.equal(choice.relations.find(r=>r.id==='science').qualification,science.qualification);assert.equal(choice.relations.find(r=>r.id==='access').organizationalAccess.uniqueWitnessCount,7);
 const reverse=choice.relations.find(r=>r.id==='reverse-science');assert.equal(reverse.traversal,'incoming');assert.equal(reverse.source,'science');assert.equal(reverse.choiceTitle,'science');
 assert.equal(view.atlas.connectionCount,6);assert.equal(nav.connections('current').total,6);assert.equal(view.directions.length,4);assert.ok(!choice.label.includes('must never'));
 const runtime=createRuntime(nav,'test'),next=runtime.action({type:'select',directionId:choice.id});assert.equal(next.view.atlas.destination.id,'science');assert.equal(next.view.atlas.destination.title,'science');
});
