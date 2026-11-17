import test from 'node:test';import assert from 'node:assert/strict';import {verifyPrepared,reviewIndependence} from './runner.mjs';
test('four one-pass pilots preserve prior source/index pins and bound concurrency',()=>{const p=verifyPrepared();assert.equal(p.jobs.length,4);assert.equal(p.maxAuthorizedConcurrency,4);assert.equal(p.primaryWindowsSupplied,0);assert.equal(p.scientificAdmission,false);});

test('triage receipt does not claim a previous stage or independent challenge',()=>{assert.equal(reviewIndependence('triage'),'single_source_only_screen; inherited_reviews_visible; no_independent_challenge');});
