/** Portable, deterministic session transitions shared by browser, CLI and MCP. */
export const SCHEMA_VERSION = '1.0.0';
const INTENTS = new Set(['explore', 'derive', 'phenomenology', 'recent', 'using']);
const RELATIONS = new Set(['on', 'using', 'either']);
const LENSES = new Set(['physical_question', 'method', 'combined']);
const STATE_KEYS = new Set(['schemaVersion', 'id', 'corpusId', 'computationId', 'query', 'focusIds', 'intent', 'workRelation', 'lens', 'constraints']);
const ACTION_KEYS = new Set(['type', 'query', 'focusIds', 'intent', 'workRelation', 'lens', 'constraints', 'directionId', 'index']);

function fail(message) { throw new Error(message); }
function plain(value, name) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || ![Object.prototype, null].includes(Object.getPrototypeOf(value))) fail(`${name} must be a plain JSON object`);
  return value;
}
function keys(value, allowed, name) {
  for (const key of Object.keys(value)) if (!allowed.has(key)) fail(`Unknown ${name} field: ${key}`);
}
function string(value, name, max = 4000) {
  if (typeof value !== 'string' || value.length > max) fail(`${name} must be a string of at most ${max} characters`);
  return value.trim().replace(/\s+/g, ' ');
}
function ids(value, name, max = 100) {
  if (!Array.isArray(value) || value.length > max) fail(`${name} must be an array of at most ${max} IDs`);
  return [...new Set(value.map(item => { const id = string(item, name, 300); if (!id) fail(`${name} contains an empty ID`); return id; }))].sort();
}
function choice(value, choices, name) { if (!choices.has(value)) fail(`Unsupported ${name}: ${value}`); return value; }
function constraints(value = {}) {
  plain(value, 'constraints'); keys(value, new Set(['excludeIds', 'yearMin', 'yearMax']), 'constraint');
  const out = {excludeIds: ids(value.excludeIds ?? [], 'excludeIds', 1000)};
  for (const key of ['yearMin', 'yearMax']) if (value[key] !== undefined) {
    if (!Number.isInteger(value[key]) || value[key] < 1000 || value[key] > 3000) fail(`${key} must be an integer between 1000 and 3000`);
    out[key] = value[key];
  }
  if (out.yearMin !== undefined && out.yearMax !== undefined && out.yearMin > out.yearMax) fail('yearMin exceeds yearMax');
  return out;
}
function digest(text) {
  let a = 0x811c9dc5, b = 0x9e3779b9;
  for (let i = 0; i < text.length; i++) { a = Math.imul(a ^ text.charCodeAt(i), 16777619); b = Math.imul(b ^ text.charCodeAt(i), 2246822519); }
  return `state-${(a >>> 0).toString(16).padStart(8, '0')}${(b >>> 0).toString(16).padStart(8, '0')}`;
}
export function normalizeState(input) {
  plain(input, 'state'); keys(input, STATE_KEYS, 'state');
  if (input.schemaVersion !== undefined && input.schemaVersion !== SCHEMA_VERSION) fail(`Unsupported schemaVersion: ${input.schemaVersion}`);
  const corpusId = string(input.corpusId, 'corpusId', 200); if (!corpusId) fail('corpusId is required');
  const computationId = string(input.computationId, 'computationId', 1000); if (!computationId) fail('computationId is required');
  const result = {
    schemaVersion: SCHEMA_VERSION, corpusId, computationId,
    query: string(input.query ?? '', 'query'),
    focusIds: ids(input.focusIds ?? [], 'focusIds'),
    intent: choice(input.intent ?? 'explore', INTENTS, 'intent'),
    workRelation: choice(input.workRelation ?? (input.intent === 'using' ? 'using' : 'either'), RELATIONS, 'workRelation'),
    lens: choice(input.lens ?? 'combined', LENSES, 'lens'),
    constraints: constraints(input.constraints),
  };
  return {schemaVersion: SCHEMA_VERSION, id: digest(JSON.stringify(result)), ...result};
}
export function createSession(initial) {
  const state = normalizeState(initial);
  return {schemaVersion: SCHEMA_VERSION, corpusId: state.corpusId, computationId: state.computationId, states: [state], cursor: 0};
}
export function validateSession(session, {corpusId, computationId} = {}) {
  plain(session, 'session'); keys(session, new Set(['schemaVersion', 'corpusId', 'computationId', 'states', 'cursor']), 'session');
  if (session.schemaVersion !== SCHEMA_VERSION) fail(`Unsupported schemaVersion: ${session.schemaVersion}`);
  if (corpusId && session.corpusId !== corpusId) fail(`Corpus mismatch: expected ${corpusId}, received ${session.corpusId}`);
  if (computationId && session.computationId !== computationId) fail('Computation mismatch: load the matching engine/data version or explicitly start a new session');
  if (!Array.isArray(session.states) || !session.states.length || session.states.length > 500) fail('Session needs between 1 and 500 states');
  if (!Number.isInteger(session.cursor) || session.cursor < 0 || session.cursor >= session.states.length) fail('Invalid history cursor');
  const states = session.states.map(state => {
    if (state.corpusId !== session.corpusId) fail('Mixed corpus IDs in session');
    if (state.computationId !== session.computationId) fail('Mixed computation IDs in session');
    const normalized = normalizeState(state);
    if (normalized.id !== state.id) fail('State ID does not match normalized state; regenerate using navigation commands');
    return normalized;
  });
  return {schemaVersion: SCHEMA_VERSION, corpusId: session.corpusId, computationId: session.computationId, states, cursor: session.cursor};
}
export function currentState(session) { return session.states[session.cursor]; }
export function exportSession(session) {
  const validated = validateSession(session);
  return {schemaVersion: SCHEMA_VERSION, kind: 'eigenquestions-session', corpusId: validated.corpusId, computationId: validated.computationId, session: validated};
}
export function importSession(payload, options = {}) {
  plain(payload, 'export'); keys(payload, new Set(['schemaVersion', 'kind', 'corpusId', 'computationId', 'session']), 'export');
  if (payload.schemaVersion !== SCHEMA_VERSION || payload.kind !== 'eigenquestions-session') fail('Unsupported export format or version');
  if (payload.corpusId !== payload.session?.corpusId) fail('Export corpus ID disagrees with session');
  if (payload.computationId !== payload.session?.computationId) fail('Export computation ID disagrees with session');
  return validateSession(payload.session, options);
}
export function applyAction(inputSession, action, navigator) {
  const session = validateSession(inputSession, {computationId:navigator?.computationId});
  plain(action, 'action'); keys(action, ACTION_KEYS, 'action');
  if (typeof navigator?.computeView !== 'function') fail('A numerical navigator is required');
  const before = currentState(session);
  let next = session;
  if (['back', 'forward', 'replay'].includes(action.type)) {
    const cursor = action.type === 'back' ? Math.max(0, session.cursor - 1)
      : action.type === 'forward' ? Math.min(session.states.length - 1, session.cursor + 1) : action.index;
    if (!Number.isInteger(cursor) || cursor < 0 || cursor >= session.states.length) fail('Replay index is outside history');
    next = {...session, cursor};
  } else if (action.type === 'reset') {
    next = createSession({corpusId: session.corpusId, computationId: session.computationId, ...stateFields(action)});
  } else if (['navigate', 'refine', 'pivot', 'broaden', 'select'].includes(action.type)) {
    let patch = stateFields(action);
    if (action.type === 'select') {
      const direction = navigator.computeView(before).directions.find(item => item.id === action.directionId);
      if (!direction) fail('Direction is absent from the current view; inspect current state before selecting');
      patch = {
        query: direction.query, focusIds: direction.seedIds,
        intent: direction.intent ?? before.intent, lens: direction.lens ?? before.lens,
        workRelation: direction.workRelation ?? before.workRelation,
      };
    }
    const base = {...before};
    if (action.type === 'refine' && !Object.hasOwn(patch, 'focusIds')) {
      base.focusIds = navigator.computeView(before).nodes.slice(0, 5).map(node => node.id);
    }
    if (action.type === 'pivot' || action.type === 'broaden') base.focusIds = [];
    if (action.type === 'broaden') base.constraints = {excludeIds: []};
    const state = normalizeState({...base, ...patch, constraints: patch.constraints ? {...base.constraints, ...patch.constraints} : base.constraints});
    if (session.cursor >= 499) fail('History limit reached; export this session and start a fresh session');
    next = {...session, states: [...session.states.slice(0, session.cursor + 1), state], cursor: session.cursor + 1};
  } else fail(`Unsupported action type: ${action.type}`);
  const view = navigator.computeView(currentState(next));
  if (view.corpusId !== next.corpusId || view.stateId !== currentState(next).id) fail('Engine returned a view for a different state or corpus');
  if (view.computationId !== next.computationId) fail('Engine returned a different computation identity');
  return {session: next, view};
}
function stateFields(action) {
  const fields = Object.fromEntries(['query', 'focusIds', 'intent', 'workRelation', 'lens', 'constraints'].filter(key => Object.hasOwn(action, key)).map(key => [key, action[key]]));
  if (fields.intent === 'using' && !Object.hasOwn(fields, 'workRelation')) fields.workRelation = 'using';
  return fields;
}
