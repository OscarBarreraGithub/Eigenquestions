import { readFile, readdir, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export async function checkSite(directory = path.join(root, 'dist')) {
  const entries = [];
  async function visit(dir) {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) await visit(file);
      else { const { size } = await stat(file); assert.ok(size <= 25 * 1024 * 1024, `${file} exceeds 25 MiB`); entries.push(path.relative(directory, file)); }
    }
  }
  await visit(directory);
  assert.ok(entries.length <= 20000, 'Too many static assets for a free-plan deployment');
  for (const required of ['index.html', '404.html', 'app.js', 'compute-worker.js', 'styles.css', 'lib/protocol/session.mjs', 'lib/protocol/capsule.mjs', 'lib/geometry/index.mjs', 'data/manifest.json', 'docs/site.md', 'docs/agent-interface.md', 'docs/navigation-contract.md', 'docs/geometry.md', 'docs/geometry-experiments.md', 'docs/stored-views-operations.md']) assert.ok(entries.includes(required), `Missing product asset ${required}`);
  for (const file of entries) assert.ok(!/^(api|quiz|taste|submit|review|leaderboard|explore|_next|\.git)\//.test(file), `Retired route in static output: ${file}`);
  assert.ok(!entries.some(file => file.includes('Q-001-original') || file.includes('Lab Notebook') || file.includes('.env')), 'Private planning/runtime material must not enter the public build');
  const html = await readFile(path.join(directory, 'index.html'), 'utf8');
  for (const match of html.matchAll(/(?:href|src)="(\/(?!\/)[^"#?]+)"/g)) {
    const target = match[1].slice(1);
    if (target) assert.ok(entries.includes(target), `Broken HTML asset link: ${match[1]}`);
  }
  for (const file of entries.filter(name => /\.(mjs|js)$/.test(name))) {
    const source = await readFile(path.join(directory, file), 'utf8');
    for (const match of source.matchAll(/(?:from\s*|import\s*)['"]([^'"]+)['"]/g)) {
      if (!match[1].startsWith('.') && !match[1].startsWith('/')) continue;
      const imported = match[1].startsWith('/') ? match[1].slice(1) : path.posix.normalize(path.posix.join(path.posix.dirname(file), match[1]));
      assert.ok(entries.includes(imported), `Missing browser module ${imported} imported by ${file}`);
    }
  }
  for (const file of entries.filter(name => name.endsWith('.md'))) {
    const source = await readFile(path.join(directory, file), 'utf8');
    for (const match of source.matchAll(/\[[^\]]+\]\(([^\s)]+)\)/g)) {
      const href = match[1];
      const repository = href.match(/^https:\/\/github\.com\/OscarBarreraGithub\/Eigenquestions\/(?:blob|tree)\/main\/(.+?)(?:#.*)?$/);
      if (repository) { assert.ok(await stat(path.join(root, decodeURI(repository[1]))).catch(() => null), `Missing repository documentation target in ${file}: ${href}`); continue; }
      if (/^[a-z][a-z0-9+.-]*:|^#|^\/\//i.test(href)) continue;
      const target = decodeURI(href.split('#')[0]);
      const resolved = target.startsWith('/') ? target.slice(1) : path.posix.normalize(path.posix.join(path.posix.dirname(file), target));
      assert.ok(entries.includes(resolved), `Broken published Markdown link in ${file}: ${href}`);
    }
  }
  const engineSource = await readFile(path.join(directory, 'lib/geometry/index.mjs'));
  const identitySource = await readFile(path.join(directory, 'lib/geometry/identity.mjs'), 'utf8');
  const pinnedHash = identitySource.match(/ENGINE_SOURCE_SHA256\s*=\s*'([a-f0-9]{64})'/)?.[1];
  assert.equal(createHash('sha256').update(engineSource).digest('hex'), pinnedHash, 'Engine identity is stale; geometry owner must repin before release');
  const config = await readFile(path.join(root, 'wrangler.toml'), 'utf8');
  assert.ok(/^main\s*=\s*"backend\/views\.mjs"/m.test(config), 'Only the bounded stored-view handler may run on the default deployment');
  assert.ok(!/d1_databases|nodejs_compat|\.open-next/.test(config), 'Retired backend configuration remains');
  assert.ok(/run_worker_first\s*=\s*\["\/api\/views", "\/api\/views\/\*"\]/.test(config), 'Only stored-view paths may require Worker execution');
  assert.ok(!/\[\[r2_buckets\]\]|\[\[durable_objects/.test(config), 'Storage activation must remain explicit');
  assert.ok(/not_found_handling\s*=\s*"404-page"/.test(config), 'Unknown paths must return 404');
  assert.ok(/eigenquestions\.com\/\*/.test(config), 'Existing domain route must be retained');
  const manifest = JSON.parse(await readFile(path.join(directory, 'data/manifest.json'), 'utf8'));
  const shards = Object.values(manifest.files).flat().filter(file => file?.path && file?.sha256);
  for (const shard of shards) {
    assert.ok(entries.includes(`data/${shard.path}`), `Missing shard ${shard.path}`);
    const buffer = await readFile(path.join(directory, 'data', shard.path));
    assert.equal(buffer.byteLength, shard.bytes, `Size mismatch: ${shard.path}`);
    assert.equal(createHash('sha256').update(buffer).digest('hex'), shard.sha256, `Hash mismatch: ${shard.path}`);
  }
  return { assets: entries.length, corpusId: manifest.corpusId, verifiedShards: shards.length, staticAssets: true, assetsOnly: false, apiRoutes: ['/api/views'], oldRoutesAbsent: true };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) console.log(JSON.stringify(await checkSite(), null, 2));
