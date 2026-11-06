import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

const overviewRoot = new URL('../../data/overview/', import.meta.url);
const corpusRoot = new URL('../../data/navigation/', import.meta.url);
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const jsonHash = value => sha(JSON.stringify(value));
const read = async (root, path) => JSON.parse(await fs.readFile(new URL(path, root), 'utf8'));
const manifestBytes = await fs.readFile(new URL('manifest.json', overviewRoot));
const manifest = JSON.parse(manifestBytes);
const map = await read(overviewRoot, manifest.files.map.path);
const corpusBytes = await fs.readFile(new URL('manifest.json', corpusRoot));
const corpus = JSON.parse(corpusBytes);

// Independently computed from the pinned upstream publication, before compact
// encoding. These retain complete geometry/membership/topic/link identity while
// allowing separate display captions and transport encodings to evolve.
const SOURCE_IDENTITIES = {
  units: 'e69c6ec0f7c8c49ad7e05828b44eba56a441e08b07fe7ad2b33c9d3825435994',
  topics: '54f8d4b2a06d94eb34b8863664beaba3d64a134d05b6d4ff028c345c692a4f34',
  links: 'c37226541d36fc512eaa236582be4296f9032b74419e393aa682fe5dd6c691eb',
};

test('fixed overview pins its original source, complete bounded file inventory and current exporter', async () => {
  assert.equal(manifest.kind, 'eigenquestions-fixed-overview');
  assert.equal(manifest.viewId, 'minilm-leiden:physical_question:reviewed');
  assert.equal(manifest.source.sha256, 'a6cb5cdb6d955d3ca33b9297be0a301ea50c6c8c75ba2294999adac8163d765b');
  assert.equal(manifest.source.releaseManifestSha256, '907ab3ff3ce99744908d97ab185aaee34ab7f6a869a9b854b2cd302b3b3a7414');
  assert.equal(manifest.source.bytes, 144689193);
  assert.ok(corpus.inputs.some(input => input.path === manifest.source.path && input.sha256 === manifest.source.sha256));
  assert.equal(manifest.corpusId, corpus.corpusId);
  assert.equal(manifest.snapshotDate, corpus.snapshotDate);
  assert.equal(manifest.exportAudit.corpusManifestSha256, sha(corpusBytes));
  assert.equal(manifest.exportAudit.builderSha256, sha(await fs.readFile(new URL('../../scripts/data/build-overview.py', import.meta.url))));
  assert.deepEqual(map.pointColumns, ['unitId', 'paperIndex', 'x', 'y', 'mass', 'homes']);
  assert.deepEqual(map.paperColumns, ['paperId', 'title', 'url']);
  const files = [manifest.files.map, ...manifest.files.details];
  assert.deepEqual((await fs.readdir(overviewRoot)).sort(), ['manifest.json', ...files.map(file => file.path)].sort());
  for (const file of files) {
    assert.match(file.path, /^(?:map|details-\d{3})\.json$/);
    const bytes = await fs.readFile(new URL(file.path, overviewRoot));
    assert.equal(bytes.length, file.bytes, file.path);
    assert.equal(sha(bytes), file.sha256, file.path);
  }
  assert.ok(manifestBytes.length + manifest.files.map.bytes < 3_000_000);
  assert.equal(manifest.files.details.length, 17);
  let start = 0;
  for (const file of manifest.files.details) {
    assert.equal(file.start, start);
    assert.ok(file.count > 0 && file.count <= 512);
    assert.ok(file.bytes < 120_000);
    start += file.count;
  }
  assert.equal(start, 8473);
});

test('every question ID, exact lazy-loaded excerpt, paper identity and source URL matches the frozen corpus', async () => {
  const currentUnits = new Map();
  for (const file of corpus.files.units) {
    for (const unit of await read(corpusRoot, file.path)) {
      if (unit.lens === 'physical_question') currentUnits.set(unit.id, unit);
    }
  }
  const currentPapers = new Map((await read(corpusRoot, corpus.files.papers.path)).map(paper => [paper.id, paper]));
  assert.equal(map.points.length, currentUnits.size);
  assert.equal(new Set(map.points.map(point => point[0])).size, currentUnits.size);
  assert.equal(map.papers.length, 6477);
  for (const [id, title, url] of map.papers) {
    assert.equal(title, currentPapers.get(id)?.title, id);
    assert.equal(url, currentPapers.get(id)?.url, id);
    assert.ok(['http:', 'https:'].includes(new URL(url).protocol), id);
  }
  let checked = 0;
  for (const file of manifest.files.details) {
    const details = await read(overviewRoot, file.path);
    assert.equal(details.start, file.start);
    assert.equal(details.texts.length, file.count);
    for (let i = 0; i < details.texts.length; i++) {
      const [id, paperIndex, , , mass] = map.points[file.start + i];
      const current = currentUnits.get(id);
      assert.ok(current, id);
      assert.equal(current.paperId, map.papers[paperIndex][0], id);
      assert.equal(current.mass, mass, id);
      assert.equal(current.text, details.texts[i], id);
      assert.equal(sha(details.texts[i]), current.evidence.textSha256, id);
      checked++;
    }
  }
  assert.equal(checked, 8473);
});

test('compact encoding preserves every supplied coordinate, overlapping weight, topic label and affinity exactly', () => {
  const units = map.points.map(([id, paper, x, y, mass, homes]) =>
    [id, map.papers[paper][0], x, y, mass, homes.map(home => [map.topics[home].id, mass / homes.length])]);
  assert.equal(jsonHash(units), SOURCE_IDENTITIES.units);
  const topics = map.topics.map(topic => [topic.id, topic.label,
    topic.parent === null ? null : map.topics[topic.parent].id,
    topic.children.map(child => map.topics[child].id), topic.depth,
    topic.x, topic.y, topic.mass, topic.unitCount, topic.paperCount,
    topic.status, topic.summary, topic.limitations,
    topic.representatives.map(row => map.points[row][0]), topic.freshConcern]);
  assert.equal(jsonHash(topics), SOURCE_IDENTITIES.topics);
  const links = map.links.map(link => [map.topics[link.source].id, map.topics[link.target].id, link.weight, link.kind]);
  assert.equal(jsonHash(links), SOURCE_IDENTITIES.links);
  assert.equal(manifest.layout.charts.length, 1);
  assert.equal(manifest.layout.charts[0].component, 0);
  assert.equal(manifest.layout.charts[0].units, 8473);
  assert.equal(manifest.layout.charts[0].layout_only_fallback, false);
  assert.equal(manifest.linkRule.formula, 'C = H.T @ W @ H');
  assert.equal(manifest.linkRule.membership_basis, 'current_reviewed_memberships');
  assert.equal(manifest.linkRule.scientific_relations_promoted, false);
});

test('membership closure retains overlapping, internal and unresolved homes and reproduces distinct-source counts', () => {
  assert.deepEqual(manifest.counts, {facets: 8473, papers: 6477, topics: 12, links: 42,
    overlapFacets: 10, internalHomeFacets: 1, unresolvedFacets: 13});
  const members = map.topics.map(() => new Set());
  const papers = map.topics.map(() => new Set());
  const paperMass = new Map();
  let overlaps = 0, internal = 0;
  map.points.forEach(([id, paper, x, y, mass, homes], row) => {
    assert.ok(Number.isFinite(x) && Number.isFinite(y) && mass > 0, id);
    assert.equal(new Set(homes).size, homes.length, id);
    assert.ok(homes.length > 0, id);
    if (homes.length > 1) overlaps++;
    if (homes.some(home => map.topics[home].children.length)) internal++;
    paperMass.set(paper, (paperMass.get(paper) || 0) + mass);
    for (const home of homes) {
      const visited = new Set();
      for (let index = home; index !== null; index = map.topics[index].parent) {
        assert.ok(!visited.has(index), 'Hierarchy cycle');
        visited.add(index);
        members[index].add(row);
        papers[index].add(paper);
      }
      assert.ok(visited.has(manifest.rootTopicIndex), 'Disconnected home');
    }
  });
  assert.equal(overlaps, 10);
  assert.equal(internal, 1);
  assert.ok([...paperMass.values()].every(mass => Math.abs(mass - 1) < 1e-12));
  map.topics.forEach((topic, i) => {
    assert.equal(members[i].size, topic.unitCount, topic.label);
    assert.equal(papers[i].size, topic.paperCount, topic.label);
    assert.ok(topic.depth <= 2);
    topic.children.forEach(child => assert.equal(map.topics[child].parent, i));
  });
  const unresolved = manifest.membershipRule.unresolvedTopicIndex;
  assert.equal(members[unresolved].size, 13);
  assert.equal(papers[unresolved].size, 13);
  assert.equal(map.topics[unresolved].status, 'deferred');
  assert.equal(map.topics.filter(topic => topic.freshConcern).length, 4);
  assert.equal(map.topics[manifest.rootTopicIndex].children.length, 5);
  assert.equal(map.topics.filter(topic => topic.status === 'agent_proposed').length, 10);
});

test('concise captions retain original labels and explain the actual scientific scope', () => {
  assert.ok(map.topics.every(topic => topic.caption && topic.captionRationale));
  const broad = map.topics.find(topic => topic.caption === 'Quantum gravity, horizons & consistency');
  assert.equal(broad.label, 'Black-hole response and entropy: model dependence and quantum-gravity constraints');
  assert.equal(broad.children.length, 6);
  assert.ok(broad.children.some(index => map.topics[index].label.startsWith('De Sitter')));
  assert.ok(broad.children.some(index => map.topics[index].label.includes('effective field theories')));
  assert.match(broad.captionRationale, /without implying all children are black-hole calculations/);
});
