import test from'node:test';import assert from'node:assert/strict';import{verifyPrepared,reviewIndependence}from'./runner.mjs';
test('one independent whole challenge is pinned without a proposal rerun',()=>{const x=verifyPrepared();assert.equal(x.jobs.length,1);assert.equal(x.maxAuthorizedConcurrency,1);assert.equal(x.jobs[0].dependsOn,null);});
test('receipt preserves independent challenge role',()=>assert.equal(reviewIndependence('challenge'),'separate_ephemeral_thread; previous_stage_visible'));
