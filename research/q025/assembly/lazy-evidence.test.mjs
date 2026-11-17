import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {partitionCatalog,validatePartition} from './lazy-package.mjs';
import {loadFrozenCorpus,hydrateSources} from './corpus.mjs';
import {scopeContentHash} from './accepted.mjs';

test('real admitted122-evidence scope keeps all pinned evidence in lazy detail',async()=>{
  const root=resolve(fileURLToPath(new URL('../../../',import.meta.url)));
  const packet=JSON.parse(await readFile(resolve(root,'research/q025/evaluation/full-pass/admissions-v4/supported-scope-role-component-v4.json'),'utf8'));
  const d=packet.destinations.find(d=>d.id==='q025-candidate-region:839da90831bec9d6ef0a811b');
  assert.equal(d.evidenceIds.length,122);
  const corpus=await loadFrozenCorpus(resolve(root,'data/navigation'));
  const logical={destinations:[d],sources:hydrateSources(corpus).filter(s=>d.evidenceIds.includes(s.id)),memberships:[],relations:[]};
  const partition=partitionCatalog(logical,{entryDestinationId:d.id});
  assert.equal(validatePartition(logical,partition).exactMembershipRoundTrip,true);
  const index=partition.catalog.destinations[0],descriptor=partition.catalog.detailShards[index.detail.shardId];
  const detail=JSON.parse(partition.files.find(f=>f.descriptor.path===descriptor.path).text).destinations[d.id];
  assert.deepEqual(detail.destination.evidenceIds,d.evidenceIds);
  assert.equal(scopeContentHash(detail.destination),scopeContentHash(d));
  assert.deepEqual(new Set(detail.sources.map(s=>s.id)),new Set(d.evidenceIds));
  assert.equal(detail.membershipSample.length,0);
  assert.equal(detail.memberships,undefined);
});
