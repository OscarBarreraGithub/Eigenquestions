import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { setTimeout as delay } from 'node:timers/promises';
import { checkSite } from '../../scripts/site-check.mjs';

test('built assets preserve corpus hashes and complete imports alongside the bounded storage API', async () => {
  const result = await checkSite();
  assert.equal(result.staticAssets, true);
  assert.ok(result.verifiedShards > 1);
});

test('static HTTP server serves the new product and retires old pages and APIs', async () => {
  const port = 22000 + Math.floor(Math.random() * 15000);
  const server = spawn(process.execPath, ['scripts/site-serve.mjs', String(port)], { stdio: 'pipe' });
  let error = '';
  server.stderr.on('data', chunk => { error += chunk; });
  try {
    const origin = `http://127.0.0.1:${port}`;
    let ready = false;
    for (let i = 0; i < 40; i++) { try { ready = (await fetch(origin)).ok; if (ready) break; } catch {} await delay(50); }
    assert.ok(ready, error || 'Static preview failed to start');
    const page = await fetch(origin);
    const html = await page.text();
    assert.match(html, /<title>Eigenquestions/);
    assert.match(html, /id="current-question">Loading exploration/);
    assert.doesNotMatch(html, /value="Kaluza-Klein towers"/, 'Static startup must not show an unrelated default before restoring a saved view');
    assert.ok(html.indexOf('id="columns"') < html.indexOf('id="chartpanel"'), 'Text columns must precede optional geometry');
    assert.match(html, /id="chartpanel"[^>]+hidden/);
    assert.match(html, /id="reset"[^>]*>New path/);
    for (const route of ['/api/pair', '/api/vote', '/api/stats', '/api/submit', '/api/leaderboard', '/api/review/approve', '/quiz', '/quiz/index.html', '/taste/index.html', '/explore/tree/index.html', '/leaderboard', '/submit', '/review', '/unknown-page']) {
      const response = await fetch(origin + route);
      assert.equal(response.status, 404, route);
      assert.match(await response.text(), /This page is no longer available/);
    }
    assert.equal((await fetch(origin + '/api/vote', { method: 'POST', body: '{}' })).status, 405);
    assert.match((await fetch(origin + '/lib/geometry/index.mjs')).headers.get('content-type'), /javascript/);
    assert.match((await fetch(origin + '/data/vectors-000.f32', { method: 'HEAD' })).headers.get('content-type'), /octet-stream/);
    assert.equal((await fetch(origin + '/.env')).status, 404);
  } finally { server.kill('SIGTERM'); }
});
