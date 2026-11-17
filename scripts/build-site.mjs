import {createHash} from 'node:crypto';
import {loadAtlas,createAtlasNavigator,createAtlasSourceReader} from '../lib/geometry/prepared-atlas.mjs';
import { cp, mkdir, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'dist');
await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
await cp(path.join(root, 'web'), out, { recursive: true });
for (const [from, to] of [['lib/geometry', 'lib/geometry'], ['lib/protocol/session.mjs', 'lib/protocol/session.mjs'], ['lib/protocol/context-page.mjs','lib/protocol/context-page.mjs'], ['lib/protocol/capsule.mjs', 'lib/protocol/capsule.mjs'], ['lib/protocol/presentation.mjs', 'lib/protocol/presentation.mjs'], ['data/navigation', 'data'], ['data/overview', 'data/overview'], ['data/atlas', 'data/atlas'], ['schemas', 'schemas'], ['skills', 'skills']]) {
  await mkdir(path.dirname(path.join(out, to)), { recursive: true });
  try { await cp(path.join(root, from), path.join(out, to), { recursive: true }); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
}
// Small readable records support ordinary HTTP readers and agents without JS or tools.
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
await mkdir(path.join(out,'atlas'),{recursive:true});
await writeFile(path.join(out,'atlas/index.html'),'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Physics atlas — Eigenquestions</title><h1>Physics atlas</h1><p>No prepared catalog is installed in this retained release.</p><p><a href="/">Open the source explorer</a> · <a href="/docs/agent-interface.md">Agent interface</a></p></html>');
let atlasIndex;
try {atlasIndex=JSON.parse(await readFile(path.join(out,'data/atlas/index.json'),'utf8'));}
catch(error){if(error.code!=='ENOENT')throw error;}
if(atlasIndex){
  const index=atlasIndex;
  const links=[];
  for(const entry of index.atlases || []) {
    if(![entry.atlasId,entry.atlasVersion].every(x=>/^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,199}$/.test(x)))throw new Error('Invalid atlas index path');
    const directory=path.join(out,'data/atlas',entry.atlasId,entry.atlasVersion),manifest=JSON.parse(await readFile(path.join(directory,'manifest.json'),'utf8'));
    if(!/^[a-zA-Z0-9][a-zA-Z0-9._-]*\.json$/.test(manifest.files.catalog.path))throw new Error('Invalid atlas catalog path');
    const atlas=await loadAtlas(directory,{readText:filename=>readFile(filename,'utf8')}),catalog=atlas.catalog,navigator=createAtlasNavigator(atlas),readContributions=createAtlasSourceReader(atlas,{base:path.join(out,'data'),readText:filename=>readFile(filename,'utf8')});
    await navigator.prepareSearch?.();
    const checkedMemberships=await navigator.validateCompleteMemberships?.();if(checkedMemberships)console.log(`Validated lazy atlas membership: ${JSON.stringify(checkedMemberships)}`);
    const destinationIndex=new Map(catalog.destinations.map(d=>[d.id,d])),incident=new Map();for(const relation of catalog.relations)for(const id of [relation.source,relation.target]){if(!incident.has(id))incident.set(id,[]);incident.get(id).push(relation);}
    const checkedFiles=new Set();
    async function checkedFile(descriptor,json=false){
      if(!descriptor||!/^[a-zA-Z0-9][a-zA-Z0-9._/-]*\.json(?:\.gz)?$/.test(descriptor.path||'')||descriptor.path.split('/').includes('..')||!/^[a-f0-9]{64}$/.test(descriptor.sha256||''))throw new Error('Invalid declared atlas file');
      const body=await readFile(path.join(directory,descriptor.path));if(descriptor.bytes!==undefined&&descriptor.bytes!==body.length)throw new Error(`Atlas file size mismatch: ${descriptor.path}`);if(createHash('sha256').update(body).digest('hex')!==descriptor.sha256)throw new Error(`Atlas file checksum mismatch: ${descriptor.path}`);checkedFiles.add(descriptor.path);return json?JSON.parse(body.toString('utf8')):undefined;
    }
    if(manifest.files.logicalValidation)await checkedFile(manifest.files.logicalValidation);
    const unrepresented=manifest.files.unrepresentedPapers?await checkedFile(manifest.files.unrepresentedPapers,true):[];if(!Array.isArray(unrepresented))throw new Error('Unrepresented paper inventory must be an array');
    if(manifest.files.sourceContextSummary)await checkedFile(manifest.files.sourceContextSummary);
    const inventoryPath=descriptor=>`/data/atlas/${encodeURIComponent(entry.atlasId)}/${encodeURIComponent(entry.atlasVersion)}/${escapeHtml(descriptor.path)}`;
    const coverageLinks=[manifest.files.sourceContextSummary?`<a href="${inventoryPath(manifest.files.sourceContextSummary)}">Frozen source inventory and context coverage</a>`:'',manifest.files.unrepresentedPapers?`<a href="${inventoryPath(manifest.files.unrepresentedPapers)}">Bibliographic records without source text (${unrepresented.length})</a>`:''].filter(Boolean).join(' · ');

    const contextIndex=manifest.files.sourceContextIndex?await checkedFile(manifest.files.sourceContextIndex,true):null;
    const contextBuckets=new Map(),sourceContextFiles=new Map();
    async function indexSourceContext(source){
      if(sourceContextFiles.has(source.id))return;
      let dictionary=contextIndex;
      if(contextIndex?.unitIndex){const prefix=/^unit:([a-f0-9]{2})/.exec(source.id)?.[1],bucket=prefix&&contextIndex.unitIndex.shards[prefix];if(!bucket)return;if(!contextBuckets.has(prefix))contextBuckets.set(prefix,await checkedFile(bucket,true));dictionary=contextBuckets.get(prefix);}
      const reference=dictionary?.units?.[source.id],file=reference?.shardId?dictionary.shards[reference.shardId]:reference;if(file){if(!checkedFiles.has(file.path))await checkedFile(file);sourceContextFiles.set(source.id,{file,locator:reference.sourceLocator});}
    }
    const contextLinks=source=>{const context=sourceContextFiles.get(source.id);return `${context?.locator?`<p>Archived source locator: ${escapeHtml(JSON.stringify(context.locator))}</p>`:''}${context?.file?`<p><a href="/data/atlas/${encodeURIComponent(entry.atlasId)}/${encodeURIComponent(entry.atlasVersion)}/${escapeHtml(context.file.path)}">Optional complete source context (${context.file.encoding==='gzip'?'gzip JSON':'JSON'})</a>. Exact source-object relations retain their own scope; they do not imply relations between entire topics.</p>`:''}`;};
    const publicDirectory=path.join(out,'atlas',entry.atlasId,entry.atlasVersion);await mkdir(publicDirectory,{recursive:true});
    for(const indexed of catalog.destinations){
      await navigator.prepareDestination?.(indexed.id);const d=navigator.destination(indexed.id);
      if(!/^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,199}$/.test(d.id))throw new Error('Invalid destination path');
      const hash=new URLSearchParams({atlas:entry.atlasId,version:entry.atlasVersion,destination:d.id}),related=incident.get(d.id)||[];
      const sources=navigator.getEvidence(d.evidenceIds).filter(source=>!source.error);for(const source of sources)await indexSourceContext(source);
      const sourceLinks=sources.map(s=>`<li>${/^https?:\/\//.test(s.sourceUrl||'')?`<a href="${escapeHtml(s.sourceUrl)}">${escapeHtml(s.title)}</a>`:escapeHtml(s.title)}<p>${escapeHtml(s.evidence.text)}</p><p>Source ID: ${escapeHtml(s.id)}</p>${contextLinks(s)}</li>`).join('');
      const contributions=await readContributions((d.sourceContributions||[]).map(row=>{const source=navigator.getEvidence([row.unitId])[0];return source&&!source.error?{...row,source}:row;}));
      for(const row of contributions)await indexSourceContext(row.source);
      const contributionSection=contributions.length?`<h2>Source contributions (${contributions.length})</h2><p>These reviewed roles are separate from source membership. A shared source does not establish question equivalence; a method contribution does not certify applicability.</p><ul>${contributions.map(row=>`<li><strong>${escapeHtml(row.role)}</strong> — ${escapeHtml(row.basis)}<p>${/^https?:\/\//.test(row.source.sourceUrl||'')?`<a href="${escapeHtml(row.source.sourceUrl)}">${escapeHtml(row.source.title)}</a>`:escapeHtml(row.source.title)}</p>${row.qualification?`<p>${escapeHtml(row.qualification)}</p>`:''}<p>${escapeHtml(row.source.evidence.text)}</p><p>Exact source: ${escapeHtml(row.unitId)}. Review decision: ${escapeHtml(row.decisionId)}.</p>${contextLinks(row.source)}<details><summary>Evidence and scope binding</summary><pre>${escapeHtml(JSON.stringify({evidenceRefs:row.evidenceRefs,scopeContentSha256:row.scopeContentSha256,provenance:row.provenance},null,2))}</pre></details></li>`).join('')}</ul>`:'';
      const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(d.title)} — Eigenquestions</title><link rel="stylesheet" href="/styles.css"><main style="max-width:70rem;margin:auto;padding:2rem"><a href="/atlas/index.html">Physics atlas</a><h1>${escapeHtml(d.title)}</h1><p>${escapeHtml(d.question)}</p><p>${escapeHtml(d.summary)}</p><p><a href="/#${hash}">Open this destination in the explorer</a></p><h2>Scope</h2>${Object.entries(d.scope).map(([key,values])=>`<h3>${escapeHtml(key)}</h3><ul>${(Array.isArray(values)?values:[values]).map(value=>`<li>${escapeHtml(value)}</li>`).join('')}</ul>`).join('')}<h2>Methods and reading coverage</h2><p>${escapeHtml((d.methods||[]).map(m=>typeof m==='string'?m:m.description||m.label||JSON.stringify(m)).join('; '))}</p><p>${escapeHtml(typeof d.readingLimit==='string'?d.readingLimit:JSON.stringify(d.readingLimit||d.readingCoverage||'Not separately recorded'))}</p>${contributionSection}<h2>Connections</h2><ul>${related.map(r=>{const target=r.source===d.id?r.target:r.source,record=destinationIndex.get(target);return `<li><a href="${encodeURIComponent(target)}.html">${escapeHtml(record.title)}</a> — ${escapeHtml(r.type)} (${r.source===d.id?'outgoing':'incoming'} recorded relation)<p>${escapeHtml(r.rationale)}</p></li>`;}).join('')}</ul><h2>Listed sources</h2><ul>${sourceLinks}</ul><p>Scientific status: ${escapeHtml(d.scientificStatus)}. Placement: ${escapeHtml(d.placementStatus)}.</p><p>Listed sources support this record; they do not claim exhaustive literature coverage. <a href="/data/atlas/${encodeURIComponent(entry.atlasId)}/${encodeURIComponent(entry.atlasVersion)}/manifest.json">Versioned data manifest</a></p></main></html>`;
      await writeFile(path.join(publicDirectory,`${d.id}.html`),html);
    }
    links.push(`<li id="coverage-${escapeHtml(entry.atlasId)}-${escapeHtml(entry.atlasVersion)}"><a href="${encodeURIComponent(entry.atlasId)}/${encodeURIComponent(entry.atlasVersion)}/${encodeURIComponent(entry.entryDestinationId)}.html">${escapeHtml(entry.title)}</a><p>${escapeHtml(entry.scope)}</p>${coverageLinks?`<p>${coverageLinks}</p>`:''}</li>`);
  }
  await mkdir(path.join(out,'atlas'),{recursive:true});await writeFile(path.join(out,'atlas/index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prepared physics atlas — Eigenquestions</title><link rel="stylesheet" href="/styles.css"><main style="max-width:70rem;margin:auto;padding:2rem"><h1>Prepared physics atlas</h1><p>Source-backed destinations and shared connections. Read scopes and evidence before mapping a question; title matching is not semantic interpretation. Coverage is dated and uneven.</p><ul>${links.join('')}</ul><a href="/">Open the explorer</a></main></html>`);
}
await mkdir(path.join(out, 'docs'), { recursive: true });
for (const name of ['site.md', 'contextual-view-showcase.md', 'agent-interface.md', 'navigation-contract.md', 'geometry.md', 'geometry-experiments.md', 'stored-views-operations.md', 'Q-006-overview-contract.md']) {
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
