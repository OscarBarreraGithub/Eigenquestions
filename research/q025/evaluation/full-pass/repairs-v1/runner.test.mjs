import test from 'node:test';import assert from 'node:assert/strict';import {verifyPrepared,childReadiness} from './runner.mjs';
test('four bounded clause jobs preserve source-only and independent challenge structure',()=>{const p=verifyPrepared();assert.equal(p.jobs.length,4);assert.equal(p.maxAuthorizedConcurrency,5);assert.equal(p.jobs.filter(x=>x.dependsOn).length,2);});
test('repair source packets require no invented child coverage',()=>assert.equal(childReadiness({childDependencies:[]}).status,'ready'));
