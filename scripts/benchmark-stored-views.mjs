// Local evidence only: endpoint wall time is not Cloudflare CPU time.
import {performance} from 'node:perf_hooks';
import {gzipSync} from 'node:zlib';
import {writeFile} from 'node:fs/promises';
import {Miniflare} from 'miniflare';
import {loadLocalNavigator, createRuntime} from '../lib/protocol/runtime.mjs';
import {createCapsule, decodeCapsuleBytes, MAX_JSON_BYTES} from '../lib/protocol/capsule.mjs';

const {corpus, navigator} = await loadLocalNavigator();
const runtime = createRuntime(navigator, corpus.manifest.corpusId);
const native = createCapsule(runtime.action({type: 'navigate', query: 'Kaluza-Klein towers dark matter decays', intent: 'phenomenology'}));
const maximum = structuredClone(native);
maximum.context.padding = '';
maximum.context.padding = 'x'.repeat(MAX_JSON_BYTES - Buffer.byteLength(JSON.stringify(maximum)));
const broad = structuredClone(native);
broad.context.padding = Array(Math.floor((MAX_JSON_BYTES - Buffer.byteLength(JSON.stringify(broad)) - 20) / 2)).fill(0);
const cases = [
  ['representative-native', Buffer.from(JSON.stringify(native))],
  ['maximum-decoded-string', Buffer.from(JSON.stringify(maximum))],
  ['maximum-decoded-many-values', Buffer.from(JSON.stringify(broad))],
  ['oversized-decoded-bomb', Buffer.from('x'.repeat(MAX_JSON_BYTES + 1))],
];
const mf = new Miniflare({modules: true, scriptPath: 'backend/index.mjs', compatibilityDate: '2026-05-26',
  r2Buckets: ['VIEWS'], durableObjects: {VIEW_BUDGET: {className: 'ViewBudget', useSQLite: true}}, bindings: {VIEW_UPLOADS_ENABLED: 'true'}});
const rows = [];
try {
  await mf.ready;
  for (const [name, raw] of cases) {
    const bytes = gzipSync(raw), local = [], endpoint = [], statuses = [];
    for (let i = 0; i < 8; i++) {
      const cpu = process.cpuUsage(), start = performance.now();
      let valid = true;
      try { await decodeCapsuleBytes(bytes); } catch { valid = false; }
      const used = process.cpuUsage(cpu);
      local.push({wallMs: performance.now() - start, nodeProcessCpuMs: (used.user + used.system) / 1000, valid});
      const before = performance.now();
      const response = await mf.dispatchFetch('https://eigenquestions.example/api/views', {method: 'POST', headers: {'Content-Type': 'application/gzip'}, body: bytes});
      await response.arrayBuffer();
      endpoint.push(performance.now() - before); statuses.push(response.status);
    }
    rows.push({name, decodedBytes: raw.length, storedBytes: bytes.length, nodeValidation: local, miniflareEndpointWallMs: endpoint, statuses});
  }
} finally { await mf.dispose(); }
const report = {measuredAt: new Date().toISOString(), node: process.version, platform: process.platform,
  runtime: 'Miniflare pinned by Wrangler 4.95.0; local workerd compatibility 2026-05-26',
  caveat: 'Node process CPU measures only local validation. Miniflare numbers are HTTP wall time including local SQLite/R2, not Worker CPU. These measurements do not establish the production Workers Free 10 ms CPU limit or throughput.', rows};
if (process.argv[2]) await writeFile(process.argv[2], JSON.stringify(report, null, 2) + '\n');
for (const row of rows) console.log(JSON.stringify({name: row.name, decodedBytes: row.decodedBytes, storedBytes: row.storedBytes,
  medianNodeValidationCpuMs: row.nodeValidation.map(value => value.nodeProcessCpuMs).sort((a,b) => a-b)[4],
  medianEndpointWallMs: row.miniflareEndpointWallMs.toSorted((a,b) => a-b)[4], statuses: row.statuses}));
