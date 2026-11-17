/** Independent semantic probes. Synthetic only; no scientific admission. */
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fixtureInput } from '../../assembly/fixture.mjs';
import { assembleAccepted, scopeContentHash, sourceContributionContentHash } from '../../assembly/accepted.mjs';
import { identityInventoryHash, canonicalIdentityGroupHash } from '../../assembly/fine-identities.mjs';
import { partitionCatalog, validatePartition } from '../../assembly/lazy-package.mjs';
import { validateAtlas, createAtlasNavigator } from '../../../../lib/geometry/prepared-atlas.mjs';

const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const checkpoint = JSON.parse(await readFile(new URL('../../assembly/semantic-checkpoint-v1.json', import.meta.url)));
const repo = new URL('../../../../', import.meta.url);
const mismatches = [];
for (const file of checkpoint.files) {
  const bytes = await readFile(new URL(file.path, repo));
  if (sha256(bytes) !== file.sha256 || bytes.length !== file.bytes) mismatches.push(file.path);
}

function identityFixture(ids = ['A', 'B', 'C', 'D']) {
  const x = fixtureInput();
  x.packet.reviewRegistry.push({ id: 'review:challenge', sha256: 'b'.repeat(64) });
  x.packet.identityResolution = {
    registry: { path: 'synthetic-registry.json', sha256: 'c'.repeat(64) },
    records: ids.map(id => ({ id, contentSha256: sha256(id) })), comparisons: [], canonicalGroups: [],
  };
  return x;
}
function comparison(x, id, operation, members, definingDifferences = []) {
  x.packet.identityResolution.comparisons.push({
    id, operation, members, target: members.at(-1), definingDifferences,
    sourceReviewIds: ['review:fixture', 'review:challenge'],
    evidenceRefs: [{ kind: 'description', id: 'unit:q1' }],
  });
}
function canonicalGroup(x, id, memberIds, destinationId = 'destination:fine') {
  const r = x.packet.identityResolution, d = x.packet.destinations.find(d => d.id === destinationId);
  const group = { id, destinationId, memberIds, decisionId: `decision:${id}` };
  const scope = scopeContentHash(d), inventory = identityInventoryHash(r);
  r.canonicalGroups.push(group);
  x.packet.decisions.push({
    id: group.decisionId, type: 'question_equivalence', status: 'accepted', outcome: 'equivalent_as_scoped',
    subjectIds: [destinationId, ...memberIds], sourceReviewIds: ['review:fixture', 'review:challenge'],
    evidenceRefs: [{ kind: 'description', id: 'unit:q1' }], challengerAgreement: 'independently_agreed',
    changedPremises: [], canonicalDestinationId: destinationId, scopeContentSha256: scope,
    identityInventorySha256: inventory, identityGroupContentSha256: canonicalIdentityGroupHash(group, scope, inventory),
    reviewAgreement: { proposalReviewId: 'review:fixture', challengeReviewId: 'review:challenge' },
  });
  for (const sourceRecordId of memberIds) x.packet.aliases.push({ alias: `Alias ${sourceRecordId}`, sourceRecordId, destinationId, identityGroupId: id, decisionId: group.decisionId });
}
function outcome(x) {
  try {
    const result = assembleAccepted(x);
    return { accepted: true, identity: result.catalog.organizationProvenance.identityResolution,
      aliases: result.catalog.destinations.find(d => d.id === 'destination:fine').aliases,
      contributions: result.catalog.sourceContributions, questionAllocationMaxError: result.report.questionAllocationMaxError };
  } catch (error) { return { accepted: false, error: error.message }; }
}

const inherited = identityFixture();
comparison(inherited, 'ab', 'same_scoped_question', ['A', 'B']);
comparison(inherited, 'bc', 'different', ['B', 'C'], ['Different physical regime']);
canonicalGroup(inherited, 'group:AC', ['A', 'C']);

const sameDestination = identityFixture();
comparison(sameDestination, 'ac', 'specializes', ['A', 'C'], ['C assumes an extra controlled limit']);
canonicalGroup(sameDestination, 'group:AB', ['A', 'B']);
canonicalGroup(sameDestination, 'group:CD', ['C', 'D']);

const primary = fixtureInput(), destination = primary.packet.destinations.find(d => d.id === 'destination:fine');
primary.packet.reviewRegistry.push({ id: 'review:challenge', sha256: 'b'.repeat(64) });
const row = { unitId: 'unit:q3', destinationId: destination.id, role: 'comparison', basis: 'source_excerpt_checked',
  evidenceRefs: [{ kind: 'primary', paperId: 'p2', id: 'not-a-locator' }], decisionId: 'decision:source-contribution' };
primary.packet.sourceContributions = [row];
primary.packet.decisions.push({ id: row.decisionId, type: 'source_contribution', status: 'accepted',
  subjectIds: [row.unitId, row.destinationId], sourceReviewIds: ['review:fixture', 'review:challenge'],
  evidenceRefs: row.evidenceRefs, challengerAgreement: 'independently_agreed', scopeContentSha256: scopeContentHash(destination),
  contributionContentSha256: sourceContributionContentHash(row, scopeContentHash(destination)),
  reviewAgreement: { proposalReviewId: 'review:fixture', challengeReviewId: 'review:challenge' } });

const contributionOnly = structuredClone(primary);
contributionOnly.corpus.unitMap = new Map(contributionOnly.corpus.units.map(unit => [unit.id, unit]));
const contributionRow = contributionOnly.packet.sourceContributions[0];
contributionRow.basis = 'description_checked';
contributionRow.evidenceRefs = [{ kind: 'description', unitId: 'unit:q3', textSha256: contributionOnly.corpus.unitMap.get('unit:q3').evidence.textSha256 }];
const contributionProof = contributionOnly.packet.decisions.find(d => d.id === contributionRow.decisionId);
contributionProof.evidenceRefs = contributionRow.evidenceRefs;
contributionProof.contributionContentSha256 = sourceContributionContentHash(contributionRow, contributionProof.scopeContentSha256);
const placement = contributionOnly.packet.placements.find(p => p.unitId === 'unit:q1');
placement.destinationId = 'destination:a';
contributionOnly.packet.decisions.find(d => d.id === placement.decisionId).subjectIds = ['unit:q1', 'destination:a'];
const compiled = assembleAccepted(contributionOnly);
const manifest = { schemaVersion: '1.0.0', kind: 'eigenquestions-atlas', atlasId: 'fixture', atlasVersion: '1',
  corpusId: 'fixture-corpus', corpusContentHash: 'a'.repeat(64), entryDestinationId: 'destination:root',
  scope: { description: 'Independent synthetic semantic audit' }, files: { catalog: { path: 'catalog.json', sha256: sha256(JSON.stringify(compiled.catalog)) } } };
validateAtlas(manifest, compiled.catalog);
const partition = partitionCatalog(compiled.catalog, { entryDestinationId: 'destination:root' });
const roundTrip = validatePartition(compiled.catalog, partition);
const lazyManifest = { ...manifest, schemaVersion: '1.1.0', files: { catalog: { path: 'catalog.json', sha256: sha256(JSON.stringify(partition.catalog)) } } };
const navigator = createAtlasNavigator({ manifest: lazyManifest, catalog: partition.catalog, manifestSha256: sha256(JSON.stringify(lazyManifest)),
  readShard: async descriptor => JSON.parse(partition.files.find(file => file.descriptor.path === descriptor.path).text) });
let preparation;
try { await navigator.prepareDestination('destination:fine'); preparation = { prepared: true }; }
catch (error) { preparation = { prepared: false, error: error.message }; }

console.log(JSON.stringify({
  frozenCheckpoint: { files: checkpoint.files.length, mismatches },
  inheritedConstraint: outcome(inherited),
  distinctGroupsSameCanonicalDestination: outcome(sameDestination),
  primaryEvidenceWithoutExactLocator: outcome(primary),
  contributionOnlyQuestion: { assemblyAccepted: true, logicalValidationPassed: true, roundTripPassed: roundTrip.passed,
    questionAllocationMaxError: compiled.report.questionAllocationMaxError,
    sourceContributions: compiled.catalog.destinations.find(d => d.id === 'destination:fine').sourceContributions.length,
    primaryMembers: compiled.catalog.destinations.find(d => d.id === 'destination:fine').memberIds.length, ...preparation },
}, null, 2));
