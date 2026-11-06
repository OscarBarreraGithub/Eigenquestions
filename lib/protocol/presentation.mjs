import {normalizeState} from './session.mjs';
/** Pure presentation helpers: never rewrite scientific queries or evidence. */
export function displayExcerpt(value, maximum = 72) {
  const text = String(value ?? '').trim().replace(/\s+/g, ' ');
  if (text.length <= maximum) return text;
  const prefix = text.slice(0, maximum - 1);
  const boundary = prefix.search(/[.!?](?:\s|$)/);
  const clause = Math.max(prefix.lastIndexOf(';'), prefix.lastIndexOf(','));
  const end = boundary >= 28 ? boundary + 1 : clause >= Math.min(48, maximum * .65) ? clause : prefix.lastIndexOf(' ');
  return `${prefix.slice(0, end > maximum * .45 ? end : prefix.length).trim()}…`;
}
export function representativeInfo(direction, nodes = [], authored = false) {
  if (authored) return {kind:'Authored group',sourceTitle:'',sourceUrl:''};
  const seed = nodes.find(node => direction.seedIds?.includes(node.id));
  const lens = seed?.evidence?.lens || seed?.lens;
  return {kind: lens === 'method' ? 'Method' : lens === 'physical_question' ? 'Question' : 'Source direction', sourceTitle:seed?.title || '',sourceUrl:seed?.sourceUrl || seed?.evidence?.url || ''};
}

/** Legacy duplicate states remain intact; this only identifies an earlier visit. */
export function previousVisitIndex(session,index) {
  if(!session?.states?.[index])return -1;
  const state=JSON.stringify(normalizeState(session.states[index]));
  return session.states.slice(0,index).findIndex(previous=>JSON.stringify(normalizeState(previous))===state);
}
