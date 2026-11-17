import test from 'node:test';import assert from 'node:assert/strict';import {verifyPrepared,childReadiness} from './runner.mjs';
test('four exact canonical pilot requests retain source-only restrictions',()=>{const p=verifyPrepared();assert.equal(p.jobs.length,4);assert.equal(p.maxAuthorizedConcurrency,8);assert.equal(p.jobs.filter(x=>x.dependsOn).length,2);});
test('fixed source neighborhoods require no fabricated child units',()=>{assert.equal(childReadiness({childDependencies:[]}).status,'ready');});
