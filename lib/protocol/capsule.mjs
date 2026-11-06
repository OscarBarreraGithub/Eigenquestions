/** Portable scientific view data. No DOM, Node APIs, executable payloads or model calls. */
import {currentState, validateSession} from './session.mjs';

export const CAPSULE_VERSION = '1.0.0';
export const CAPSULE_KIND = 'eigenquestions-contextual-view';
export const MAX_JSON_BYTES = 2 * 1024 * 1024;
export const MAX_COMPRESSED_BYTES = 512 * 1024;
export const NATIVE_BUILDER = 'eigenquestions-native';
const encoder = new TextEncoder();
const fail = message => { throw new Error(message); };
const object = (value, name) => {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail(`${name} must be a JSON object`);
  return value;
};
const string = (value, name, maximum = 4000) => {
  if (typeof value !== 'string' || value.length > maximum) fail(`${name} must be a string of at most ${maximum} characters`);
  return value;
};
function array(value, name, maximum) { if (!Array.isArray(value) || value.length > maximum) fail(`${name} must be an array of at most ${maximum} items`); return value; }
function json(value, depth = 0, budget = {remaining: 100000}) {
  if (--budget.remaining < 0) fail('View data has too many JSON values');
  if (depth > 32) fail('View data is nested too deeply');
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return;
  if (typeof value === 'number') { if (!Number.isFinite(value)) fail('View numbers must be finite'); return; }
  if (Array.isArray(value)) { for (const item of value) json(item, depth + 1, budget); return; }
  object(value, 'View data');
  for (const [key, item] of Object.entries(value)) { if (['__proto__', 'prototype', 'constructor'].includes(key)) fail('Reserved object key in view data'); json(item, depth + 1, budget); }
}
const id = (value, name) => { string(value, name, 300); if (!value) fail(`${name} is empty`); return value; };
function optionalStrings(object,key,maximum=1000) { if(object[key]!==undefined) array(object[key],key,maximum).forEach(item=>string(item,key,8000)); }
function optionalNumbers(object,keys) { for(const key of keys) if(object[key]!==undefined && (typeof object[key]!=='number'||!Number.isFinite(object[key]))) fail(`${key} must be a finite number`); }
function references(values, name, available) {
  for (const value of array(values, name, 1000)) if (!available.has(id(value, name))) fail(`${name} references an absent source or group: ${value}`);
}
function validateChart(chart, view) {
  if (chart === null || chart === undefined) return;
  object(chart, 'Chart');
  optionalNumbers(chart,['explainedVariance','neighborRecallAt1','neighborRecallAt5','stress']);
  if(chart.sourceDiagnostics!==undefined){object(chart.sourceDiagnostics,'Source diagnostics');optionalNumbers(chart.sourceDiagnostics,['explainedVariance','neighborRecallAt5']);}
  if (!['affine-plane', 'display-layout'].includes(chart.kind)) fail('Chart kind must be affine-plane or display-layout');
  if (chart.kind === 'affine-plane') {
    const d = chart.dimension;
    if (!Number.isInteger(d) || d < 1 || d > 2048) fail('Invalid affine-plane dimension');
    if (array(chart.center, 'Plane center', 2048).length !== d || array(chart.basis, 'Plane basis', 2).length !== 2) fail('Plane dimensions do not match');
    for (const row of chart.basis) if (array(row, 'Basis vector', 2048).length !== d) fail('Basis dimension does not match');
    for (const value of [...chart.center, ...chart.basis.flat()]) if (typeof value !== 'number' || !Number.isFinite(value)) fail('Affine center and basis must contain finite numbers');
    const dot = (a, b) => a.reduce((sum, value, i) => sum + value * b[i], 0);
    const norms = chart.basis.map(row => dot(row, row));
    if (Math.abs(dot(...chart.basis)) > 1e-5 || norms.some(norm => Math.abs(norm - 1) > 1e-5 && !(chart.degenerate && norm < 1e-10))) fail('Affine basis must be orthonormal, or explicitly degenerate');
    if (typeof chart.scale !== 'number' || typeof chart.thickness !== 'number' || !(chart.scale > 0) || !(chart.thickness >= 0)) fail('Plane scale/thickness is invalid');
    string(chart.metric, 'Plane metric', 2000);
  }
  for (const point of [...view.nodes, ...view.directions]) if (!Number.isFinite(point.x) || !Number.isFinite(point.y)) fail('A displayed chart needs finite coordinates for every source and group');
}

/** Validates without changing labels, memberships, context or computed output. */
export function validateCapsule(input) {
  json(input); object(input, 'Capsule');
  if (input.schemaVersion !== CAPSULE_VERSION || input.kind !== CAPSULE_KIND) fail('Unsupported contextual-view format or version');
  object(input.builder, 'Builder'); id(input.builder.id, 'Builder ID'); string(input.builder.version, 'Builder version', 100);
  object(input.context, 'Scientific context'); string(input.context.question, 'Context question');
  const snapshot = object(input.snapshot, 'Snapshot'), view = object(snapshot.view, 'View');
  for (const key of ['stateId', 'corpusId', 'computationId']) id(view[key], `View ${key}`);
  const nodes = array(view.nodes, 'Sources', 500), directions = array(view.directions, 'Groups', 50);
  const sourceIds = new Set(), allIds = new Set();
  for (const node of nodes) {
    object(node, 'Source'); id(node.id, 'Source ID');
    if (allIds.has(node.id)) fail('Duplicate source ID'); sourceIds.add(node.id); allIds.add(node.id);
    string(node.title, 'Source title', 4000); object(node.evidence, 'Source evidence'); string(node.evidence.text, 'Source evidence text', 64000);
    optionalStrings(node.evidence,'sourceRecordIds'); optionalNumbers(node,['x','y','residual','score']);
  }
  for (const direction of directions) {
    object(direction, 'Group'); id(direction.id, 'Group ID');
    if (allIds.has(direction.id)) fail('Duplicate group/source ID'); allIds.add(direction.id);
    string(direction.label, 'Group label', 4000);
    optionalNumbers(direction,['x','y','residual','mass','massFraction','sourceCount','withinGroupRms']);
    references(direction.memberIds ?? direction.evidenceIds, 'Group members', sourceIds);
    references(direction.evidenceIds, 'Group evidence', sourceIds);
    references(direction.seedIds ?? [], 'Group seeds', sourceIds);
    if (direction.query !== undefined) string(direction.query, 'Group query');
  }
  for (const edge of array(view.edges, 'Relations', 5000)) {
    object(edge, 'Relation');
    references([edge.source, edge.target], 'Relation endpoints', allIds);
    string(edge.type, 'Relation type', 200);
  }
  array(view.warnings, 'View warnings', 100).forEach(item => string(item, 'Warning', 8000));
  object(view.diagnostics, 'View diagnostics'); optionalStrings(view.diagnostics,'contextTerms'); optionalNumbers(view.diagnostics,['distinctPapers','globalCandidateCount']);
  if(view.diagnostics.scope!==undefined){object(view.diagnostics.scope,'Corpus scope');optionalNumbers(view.diagnostics.scope,['paperCount','earliestYear','latestYear']);}
  validateChart(view.chart, view);
  if (snapshot.session) {
    const session = validateSession(snapshot.session), state = currentState(session);
    if (state.id !== view.stateId || session.computationId !== view.computationId || session.corpusId !== view.corpusId) fail('Session and displayed view identity disagree');
  }
  const continuation = object(input.continuation, 'Continuation');
  if (!['native-actions', 'snapshot-only'].includes(continuation.mode)) fail('Unsupported continuation mode');
  string(continuation.description, 'Continuation description', 8000);
  if (continuation.originStateId !== view.stateId) fail('Next actions belong to a different source view');
  const actions = array(continuation.actions, 'Next actions', 100), actionIds = new Set();
  for (const next of actions) {
    object(next, 'Next action'); id(next.id, 'Next-action ID');
    if (actionIds.has(next.id)) fail('Duplicate next-action ID'); actionIds.add(next.id);
    string(next.label, 'Next-action label', 4000); object(next.action, 'Navigation action');
    if (!['navigate', 'refine', 'pivot', 'broaden', 'select', 'back', 'forward', 'replay', 'reset'].includes(next.action.type)) fail('Unsupported next action');
  }
  if (continuation.mode === 'native-actions' && !snapshot.session) fail('Native continuation requires a canonical session');
  if (encoder.encode(JSON.stringify(input)).byteLength > MAX_JSON_BYTES) fail('Contextual view exceeds the 2 MiB decoded limit');
  return input;
}

export function createCapsule(snapshot, {context, builder, continuation} = {}) {
  const session = validateSession(snapshot.session), state = currentState(session);
  const view = structuredClone(snapshot.view);
  if (view.chart && !view.chart.kind) view.chart.kind = 'affine-plane';
  return validateCapsule({schemaVersion: CAPSULE_VERSION, kind: CAPSULE_KIND,
    builder: builder ?? {id: NATIVE_BUILDER, version: '1.0.0'},
    context: context ?? {question: state.query, assumptions: [], openQuestions: [], history: session.states.map((s, index) => ({question: s.query, intent: s.intent, focusIds: s.focusIds, active: index === session.cursor}))},
    snapshot: {session: structuredClone(session), view},
    continuation: continuation ?? {mode: 'native-actions', originStateId: view.stateId, description: 'Continue with the pinned native engine. Source similarity proposes reading directions; it does not establish a physical claim.', actions: view.directions.map(d => ({id: d.id, label: d.label, action: {type: 'select', directionId: d.id}}))}});
}

export function capsuleCapabilities(capsule, computationId) {
  const native = capsule.builder.id === NATIVE_BUILDER && capsule.builder.version === '1.0.0';
  const actionsSupported = native || capsule.continuation.actions.every(next => next.action.type !== 'select');
  const compatible = Boolean(capsule.snapshot.session && computationId && capsule.snapshot.view.computationId === computationId);
  return {display: true, recompute: compatible && native,
    continue: compatible && actionsSupported && capsule.continuation.mode === 'native-actions',
    builder: capsule.builder.id, nativeContextOnly: true,
    notice: !compatible ? 'This view is readable exactly as supplied. Continuing requires its matching engine and data; start a new path to use this browser’s collection.'
      : capsule.builder.id !== NATIVE_BUILDER ? 'Authored groups and labels are preserved. Provided next actions use the native engine; they do not reproduce this builder or guarantee preservation of its broader context.' : capsule.continuation.description};
}

async function readBounded(stream, maximum) {
  const reader = stream.getReader(), chunks = []; let size = 0;
  try { while (true) { const {done, value} = await reader.read(); if (done) break; size += value.byteLength; if (size > maximum) { await reader.cancel(); fail('Contextual view exceeds the decoded size limit'); } chunks.push(value); } }
  finally { reader.releaseLock(); }
  const bytes = new Uint8Array(size); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; } return bytes;
}
export async function decodeCapsuleBytes(input, {encoding = 'auto'} = {}) {
  const bytes = input instanceof Uint8Array ? input : new Uint8Array(input);
  const gzip = encoding === 'gzip' || (encoding === 'auto' && bytes[0] === 0x1f && bytes[1] === 0x8b);
  if (bytes.byteLength > (gzip ? MAX_COMPRESSED_BYTES : MAX_JSON_BYTES)) fail('Contextual view exceeds the upload size limit');
  const decoded = gzip ? await readBounded(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip')), MAX_JSON_BYTES) : bytes;
  return validateCapsule(JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(decoded)));
}
export async function encodeCapsuleBytes(capsule, {gzip = true} = {}) {
  const bytes = encoder.encode(JSON.stringify(validateCapsule(capsule)));
  if (!gzip) return bytes;
  return readBounded(new Blob([bytes]).stream().pipeThrough(new CompressionStream('gzip')), MAX_COMPRESSED_BYTES);
}
