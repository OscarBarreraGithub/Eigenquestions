import { cp, mkdir, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'dist');
await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
await cp(path.join(root, 'web'), out, { recursive: true });
for (const [from, to] of [['lib/geometry', 'lib/geometry'], ['lib/protocol/session.mjs', 'lib/protocol/session.mjs'], ['lib/protocol/capsule.mjs', 'lib/protocol/capsule.mjs'], ['data/navigation', 'data'], ['schemas', 'schemas'], ['skills', 'skills']]) {
  await mkdir(path.dirname(path.join(out, to)), { recursive: true });
  try { await cp(path.join(root, from), path.join(out, to), { recursive: true }); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
}
await mkdir(path.join(out, 'docs'), { recursive: true });
for (const name of ['site.md', 'agent-interface.md', 'navigation-contract.md', 'geometry.md', 'geometry-experiments.md', 'stored-views-operations.md']) {
  try { await cp(path.join(root, 'docs', name), path.join(out, 'docs', name)); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
}
// Repository and public data layouts differ. Rewrite only the published copies;
// evidence that is not a product asset remains linked to the source repository.
async function rewriteDocumentation(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) { await rewriteDocumentation(file); continue; }
    if (!entry.name.endsWith('.md')) continue;
    const relativeFile = path.relative(out, file).split(path.sep).join('/');
    const content = await readFile(file, 'utf8');
    let rewritten = '', cursor = 0;
    for (const match of content.matchAll(/(\[[^\]]+\]\()([^\s)]+)(\))/g)) {
      const href = match[2];
      if (/^[a-z][a-z0-9+.-]*:|^#|^\/\//i.test(href)) continue;
      const [pathname, fragment] = href.split('#', 2);
      const repositoryPath = path.posix.normalize(pathname.startsWith('/') ? pathname.slice(1) : path.posix.join(path.posix.dirname(relativeFile), decodeURI(pathname)));
      const publicPath = repositoryPath.replace(/^data\/navigation\//, 'data/');
      let target;
      try {
        if ((await stat(path.join(out, publicPath))).isFile()) target = path.posix.relative(path.posix.dirname(relativeFile), publicPath);
      } catch { /* Repository-only evidence is linked below. */ }
      if (!target) {
        let kind = 'blob';
        try { if ((await stat(path.join(root, repositoryPath))).isDirectory()) kind = 'tree'; } catch { /* The checker reports missing repository targets. */ }
        target = `https://github.com/OscarBarreraGithub/Eigenquestions/${kind}/main/${repositoryPath}`;
      }
      if (fragment) target += `#${fragment}`;
      rewritten += content.slice(cursor, match.index) + match[1] + target + match[3];
      cursor = match.index + match[0].length;
    }
    if (cursor) await writeFile(file, rewritten + content.slice(cursor));
  }
}
await rewriteDocumentation(out);
// Only these explicit product sources reach dist; old public/ and src/ never do.
let count = 0, totalBytes = 0, largest = { path: '', bytes: 0 };
async function audit(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) await audit(full);
    else {
      const { size } = await stat(full);
      if (size > 25 * 1024 * 1024) throw new Error(`Cloudflare's 25 MiB asset limit exceeded: ${path.relative(out, full)}`);
      count++; totalBytes += size;
      if (size > largest.bytes) largest = { path: path.relative(out, full), bytes: size };
    }
  }
}
await audit(out);
if (count > 19999) throw new Error(`Static asset count ${count} exceeds the conservative 20,000-file hosting limit.`);
const report = { format: 'eigenquestions-static-build-v1', files: count + 1, bytes: totalBytes, largestAsset: largest, staticAssets: true, serverIncludedInAssets: false, apiRoutes: ['/api/views'] };
await writeFile(path.join(out, 'build-info.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(`Static site: ${report.files} files, ${(totalBytes / 1024 / 1024).toFixed(1)} MiB → dist/`);
