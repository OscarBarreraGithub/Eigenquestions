import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {certificateHash,validateOrganizationalAccess} from './organizational-access.mjs';
import {scopeContentHash} from './accepted.mjs';
const dir=new URL('./organization-residual-v1/candidate-6030-connected-v4/',import.meta.url);
const packet=JSON.parse(readFileSync(new URL('aggregate.local.json',dir))),row=packet.relations.find(r=>r.provenance?.navigationBasis==='same_source_organizational_access');
const bucket=JSON.parse(readFileSync(new URL(row.organizationalAccess.supportCertificate.path,dir))),record=bucket.records[row.id];
function input(){return {row:structuredClone(row),record:structuredClone(record),destinations:packet.destinations,placements:packet.placements,contributions:packet.sourceContributions,decisions:new Map(packet.decisions.map(d=>[d.id,d])),identityResolution:{groups:packet.identityResolution.canonicalGroups},scopeHash:scopeContentHash};}
function rehash(x){x.record.certificateSha256=certificateHash(x.record);x.row.organizationalAccess.certificateSha256=x.record.certificateSha256;}
test('real accepted access certificate validates exact same-unit home and all role observations',()=>{assert.equal(validateOrganizationalAccess(input()).uniqueWitnessCount,record.uniqueWitnessCount);});
test('rehashing cannot promote a same-paper different unit',()=>{const x=input();x.record.witnesses[0].unitId='unit:unrelated';rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/exact direct/);});
test('rehashing cannot turn method into positive support',()=>{const x=input();x.record.witnesses[0].observations[0].contribution.role='method';rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/positive contribution/);});
test('historical proof qualifications cannot be silently replaced',()=>{const x=input();x.record.witnesses[0].observations[0].contributionDecision.evidenceRefs=[];rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/proof changed/);});
test('duplicate witnesses cannot inflate counts',()=>{const x=input();x.record.witnesses.push(x.record.witnesses[0]);rehash(x);assert.throws(()=>validateOrganizationalAccess(x),/duplicate source/);});
test('current scope replacement invalidates old certificate',()=>{const x=input();x.destinations=structuredClone(x.destinations);x.destinations.find(d=>d.id===x.row.target).question+=' Changed';assert.throws(()=>validateOrganizationalAccess(x),/scope binding/);});
