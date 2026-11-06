import test from 'node:test';
import assert from 'node:assert/strict';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {Miniflare} from 'miniflare'; // Pinned transitively by the exact Wrangler version.
import handler from '../../backend/views.mjs';
import {MAX_JSON_BYTES, MAX_COMPRESSED_BYTES, decodeCapsuleBytes} from '../../lib/protocol/capsule.mjs';
import {authoredCapsule} from './fixtures/capsule.mjs';

const origin = 'https://eigenquestions.example';
const digest = text => createHash('sha256').update(text).digest('hex');
const jsonBytes = value => new TextEncoder().encode(JSON.stringify(value));
const request = (bytes, headers = {}) => new Request(`${origin}/api/views`, {method: 'POST', headers: {'Content-Type': 'application/gzip', ...headers}, body: bytes, duplex: 'half'});
function runtime(options = {}) {
  return new Miniflare({modules: true, scriptPath: 'backend/index.mjs', compatibilityDate: '2026-05-26',
    r2Buckets: ['VIEWS'], durableObjects: {VIEW_BUDGET: {className: 'ViewBudget', useSQLite: true}},
    bindings: {VIEW_UPLOADS_ENABLED: 'true'}, ...options});
}
async function save(mf, bytes, headers = {}) {
  return mf.dispatchFetch(`${origin}/api/views`, {method: 'POST', headers: {'Content-Type': 'application/gzip', ...headers}, body: bytes});
}

test('real Worker/R2/SQLite round trip preserves unknown-builder authored data and concurrent retries', async () => {
  const mf = runtime();
  try {
    const capsule = authoredCapsule(), bytes = gzipSync(jsonBytes(capsule));
    const responses = await Promise.all(Array.from({length: 12}, () => save(mf, bytes)));
    assert.equal(responses.filter(response => response.status === 201).length, 1);
    assert.equal(responses.filter(response => response.status === 200).length, 11);
    const receipts = await Promise.all(responses.map(response => response.json()));
    const receipt = receipts[0];
    assert.ok(receipts.every(value => value.id === receipt.id));
    assert.match(receipt.id, /^[A-Za-z0-9_-]{22}$/);
    assert.equal(receipt.url, `${origin}/#view=${receipt.id}`);
    assert.equal(receipt.sha256, digest(bytes));
    assert.equal(receipt.bytes, bytes.length);
    assert.ok(!('expiresAt' in receipt));
    const bucket = await mf.getR2Bucket('VIEWS');
    assert.equal((await bucket.list({prefix: 'views/'})).objects.length, 1);
    const response = await mf.dispatchFetch(receipt.readUrl);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get('Access-Control-Allow-Origin'), '*');
    assert.equal(response.headers.get('X-Content-SHA256'), digest(bytes));
    assert.equal(response.headers.get('Content-Encoding'), null);
    assert.match(response.headers.get('Cache-Control'), /immutable/);
    const saved = new Uint8Array(await response.arrayBuffer());
    assert.deepEqual(saved, new Uint8Array(bytes));
    assert.deepEqual(await decodeCapsuleBytes(saved), capsule);
    const unchanged = await mf.dispatchFetch(receipt.readUrl, {headers: {'If-None-Match': response.headers.get('ETag')}});
    assert.equal(unchanged.status, 304);
    const head = await mf.dispatchFetch(receipt.readUrl, {method: 'HEAD'});
    assert.equal(head.headers.get('Content-Length'), String(bytes.length));
    assert.equal(await head.text(), '');
    const next = await save(mf, gzipSync(jsonBytes(authoredCapsule('A distinct scientific question'))));
    assert.equal(next.status, 201);
    assert.notEqual((await next.json()).id, receipt.id);
  } finally { await mf.dispose(); }
});

test('malformed, oversized, deeply nested and inconsistent capsules fail before any storage reservation', async () => {
  let calls = 0;
  const env = {VIEW_UPLOADS_ENABLED: 'true', VIEWS: {}, VIEW_BUDGET: {getByName() { calls++; throw new Error('Must not reserve invalid input'); }}};
  const badReference = authoredCapsule(); badReference.snapshot.view.directions[0].memberIds = ['missing'];
  const future = authoredCapsule(); future.schemaVersion = '999';
  const deep = authoredCapsule(); deep.context.deep = JSON.parse('['.repeat(40) + '0' + ']'.repeat(40));
  const dangerous = authoredCapsule(); dangerous.context = JSON.parse('{"question":"x","__proto__":{"polluted":true}}');
  for (const body of [new Uint8Array([0x1f, 0x8b, 0]), gzipSync('not-json'), gzipSync('{}'), ...[badReference, future, deep, dangerous].map(value => gzipSync(jsonBytes(value)))]) {
    const response = await handler.fetch(request(body), env);
    assert.equal(response.status, 400);
    assert.equal((await response.json()).error.code, 'invalid_capsule');
  }
  for (const body of [new Uint8Array(MAX_COMPRESSED_BYTES + 1), gzipSync(' '.repeat(MAX_JSON_BYTES + 1))]) {
    const response = await handler.fetch(request(body), env);
    assert.equal(response.status, 413);
  }
  const declared = await handler.fetch(request(new Uint8Array(), {'Content-Length': String(MAX_COMPRESSED_BYTES + 1)}), env);
  assert.equal(declared.status, 413);
  const encoded = await handler.fetch(request(gzipSync('{}'), {'Content-Encoding': 'gzip'}), env);
  assert.equal(encoded.status, 415);
  assert.equal(calls, 0);
});

test('JSON is accepted, negative reads are not cached, CORS and method/retired-route boundaries stay explicit', async () => {
  const mf = runtime();
  try {
    const response = await save(mf, jsonBytes(authoredCapsule()), {'Content-Type': 'application/json'});
    assert.equal(response.status, 201);
    const receipt = await response.json();
    assert.equal((await mf.dispatchFetch(receipt.readUrl)).headers.get('Content-Type'), 'application/json');
    for (const pathname of ['/api/views/AAAAAAAAAAAAAAAAAAAAAA', '/api/views/bad-id', '/api/vote', '/api/submit']) {
      const missing = await mf.dispatchFetch(origin + pathname);
      assert.equal(missing.status, 404);
      assert.equal(missing.headers.get('Cache-Control'), 'no-store');
    }
    const preflight = await mf.dispatchFetch(`${origin}/api/views`, {method: 'OPTIONS', headers: {Origin: 'https://agent.example'}});
    assert.equal(preflight.status, 204);
    assert.equal(preflight.headers.get('Access-Control-Allow-Origin'), '*');
    assert.equal((await mf.dispatchFetch(receipt.readUrl, {method: 'DELETE'})).status, 405);
    assert.equal((await mf.dispatchFetch(`${origin}/api/views`)).status, 405);
  } finally { await mf.dispose(); }
});

test('no receipt before durable PUT; failed/lost receipt retry keeps the same reserved id', async () => {
  const id = 'AAAAAAAAAAAAAAAAAAAAAA', bytes = gzipSync(jsonBytes(authoredCapsule()));
  for (const storedBeforeFailure of [false, true]) {
    let object = null, attempts = 0;
    const env = {VIEW_UPLOADS_ENABLED: 'true', VIEW_BUDGET: {getByName: () => ({reserve: async () => ({ok: true, id, createdAt: '2026-11-06T00:00:00Z'})})},
      VIEWS: {head: async () => object, put: async (key, payload, options) => {
        attempts++;
        const saved = {size: payload.length, customMetadata: options.customMetadata};
        if (storedBeforeFailure || attempts > 1) object = saved;
        if (attempts === 1) throw new Error('Simulated uncertain R2 write');
        return saved;
      }}};
    const failed = await handler.fetch(request(bytes), env);
    assert.equal(failed.status, 503);
    const error = await failed.json();
    assert.equal(error.error.code, 'storage_unavailable');
    assert.ok(!error.url && !error.id);
    const retried = await handler.fetch(request(bytes), env);
    assert.equal(retried.status, storedBeforeFailure ? 200 : 201);
    assert.equal((await retried.json()).id, id);
  }
  const unavailable = await handler.fetch(request(bytes), {});
  assert.equal(unavailable.status, 503);
});

test('atomic SQLite budget survives restart, bounds concurrent admissions, reuses reservations and advances UTC days', async () => {
  const persist = await mkdtemp(path.join(tmpdir(), 'eigenquestions-budget-test-'));
  const options = {modules: true, scriptPath: 'tests/backend/fixtures/budget-probe.mjs', compatibilityDate: '2026-05-26', durableObjectsPersist: persist,
    durableObjects: {TEST_BUDGET: {className: 'TestBudget', useSQLite: true}},
    bindings: {TEST_LIMITS: JSON.stringify({bytes: 250, objects: 3, newPerDay: 2, attemptsPerDay: 8})}};
  let mf = new Miniflare(options);
  const reserve = async (name, bytes = 100, time) => (await mf.dispatchFetch(origin, {method: 'POST', body: JSON.stringify({digest: digest(name), bytes, time})})).json();
  try {
    const first = await reserve('a');
    const repeated = await Promise.all(Array.from({length: 3}, () => reserve('a')));
    assert.ok(repeated.every(value => value.id === first.id && value.reused));
    const concurrent = await Promise.all(['b', 'c', 'd'].map(name => reserve(name)));
    assert.equal(concurrent.filter(value => value.ok).length, 1);
    assert.ok(concurrent.filter(value => !value.ok).every(value => value.code === 'daily_save_limit'));
    let state = await (await mf.dispatchFetch(origin)).json();
    assert.equal(state.bytes, 200); assert.equal(state.objects, 2); assert.equal(state.new_today, 2);
    await reserve('a');
    assert.equal((await reserve('a')).code, 'daily_attempt_limit');
    await mf.dispose(); mf = new Miniflare(options);
    assert.equal((await reserve('a')).code, 'daily_attempt_limit', 'Restart must not clear today’s limits');
    const tomorrow = '2026-11-07T00:00:00Z';
    const retry = await reserve('a', 100, tomorrow);
    assert.equal(retry.id, first.id);
    assert.equal((await reserve('e', 51)).code, 'storage_capacity');
    assert.equal((await reserve('e', 50)).ok, true);
    assert.equal((await reserve('f', 1)).code, 'storage_capacity');
    state = await (await mf.dispatchFetch(origin)).json();
    assert.equal(state.bytes, 250); assert.equal(state.objects, 3); assert.equal(state.new_today, 1);
    await reserve('a', 100, '2026-11-06T12:00:00Z');
    assert.equal((await (await mf.dispatchFetch(origin)).json()).day, '2026-11-07', 'Quota day never rolls backwards');
  } finally { await mf.dispose(); await rm(persist, {recursive: true, force: true}); }
});
