import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {certificateHash,validateOrganizationalAccess} from './organizational-access.mjs';
import {scopeContentHash} from './accepted.mjs';
const dir=new URL('./organization-residual-v1/candidate-6117-connected-v5/',import.meta.url);
const packet=JSON.parse(readFileSync(new URL('aggregate.local.json',dir)));
const row=packet.relations.find(r=>r.organizationalAccess?.policyClass==='fine_home_to_question');
const record=JSON.parse(readFileSync(new URL(row.organizationalAccess.supportCertificate.path,dir))).records[row.id];
function input(){return {row:structuredClone(row),record:structuredClone(record),destinations:packet.destinations,placements:packet.placements,contributions:packet.sourceContributions,decisions:new Map(packet.decisions.map(d=>[d.id,d])),identityResolution:{groups:packet.identityResolution.canonicalGroups},scopeHash:scopeContentHash};}
function rehash(x){x.record.certificateSha256=certificateHash(x.record);x.row.organizationalAccess.certificateSha256=x.record.certificateSha256;}
test('real fine-home access preserves exact direct allocation and positive observations',()=>{const x=input();assert.ok(validateOrganizationalAccess(x).uniqueWitnessCount>0);assert.equal(x.record.endpointBindings.source.kind,'question');assert.equal(x.record.endpointBindings.target.kind,'question');});
test('fine-home access cannot use the historical broad policy implicitly',()=>{const x=input();delete x.record.policyClass;delete x.row.organizationalAccess.policyClass;rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/explicit approved policy class/);});
test('fine-home class cannot authorize a region target',()=>{const x=input();x.destinations=structuredClone(x.destinations);x.destinations.find(d=>d.id===row.target).kind='region';rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/unapproved nonquestion/);});
test('fine-home access cannot substitute an ancestor or contextual home',()=>{const x=input();x.record.witnesses[0].home.role='context';rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/exact direct accepted home/);});
test('fine-home access cannot promote a boundary observation after rehashing',()=>{const x=input();x.record.witnesses[0].observations[0].contribution.role='boundary';rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/positive contribution/);});
test('fine-home access retains the complete scoped witness inventory',()=>{const x=input();x.row.organizationalAccess.countScope='filtered';assert.throws(()=>validateOrganizationalAccess(x),/semantic discriminator/);});
