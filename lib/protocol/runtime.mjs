import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import os from 'node:os';
import {loadCorpus, createNavigator} from '../geometry/index.mjs';
import {createSession, currentState, applyAction, exportSession, importSession} from './session.mjs';

export const PROJECT_ROOT = fileURLToPath(new URL('../../', import.meta.url));
export const DEFAULT_CONNECTION = path.join(os.tmpdir(), `eigenquestions-${process.getuid?.() ?? 'user'}.json`);
export async function loadLocalNavigator(corpusDir = path.join(PROJECT_ROOT, 'data/navigation')) {
  const corpus = await loadCorpus(corpusDir, {
    readJson: async filename => JSON.parse(await readFile(filename, 'utf8')),
    readBinary: async filename => { const data = await readFile(filename); return data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength); },
  });
  return {corpus, navigator: createNavigator(corpus)};
}
export function createRuntime(navigator, corpusId, initial = {}) {
  let session = createSession({corpusId, computationId:navigator.computationId, ...initial});
  let view = navigator.computeView(currentState(session));
  let revision = 0;
  const listeners = new Set();
  const viewers = new Map();
  const browserStatus = () => {
    const acks = [...viewers.values()];
    const current = acks.filter(ack => ack.stateId === view.stateId && ack.revision === revision);
    return {acknowledgedCurrent:current.length>0,acknowledgingViewers:current.length,knownViewers:acks.length,lastRenderedStateId:acks.sort((a,b)=>b.time-a.time)[0]?.stateId??null};
  };
  const snapshot = () => ({session, view, revision, browserStatus:browserStatus()});
  const publish = () => { const value = snapshot(); for (const listener of listeners) listener(value); return value; };
  return {
    snapshot,
    action(action) { ({session, view} = applyAction(session, action, navigator)); revision++; return publish(); },
    import(payload) { const imported = importSession(payload, {corpusId,computationId:navigator.computationId}); const computed = navigator.computeView(currentState(imported)); session = imported; view = computed; revision++; return publish(); },
    export() { return exportSession(session); },
    acknowledge({viewerId,stateId,revision:renderedRevision}) {
      if (typeof viewerId !== 'string' || !/^[a-zA-Z0-9_-]{8,100}$/.test(viewerId)) throw new Error('Invalid viewer ID');
      if (stateId !== view.stateId || renderedRevision !== revision) throw new Error('Viewer acknowledgement is for a stale state');
      if (!viewers.has(viewerId) && viewers.size>=20) viewers.delete(viewers.keys().next().value);
      viewers.set(viewerId,{stateId,revision,time:Date.now()});return browserStatus();
    },
    search(query, options = {}) {
      if (typeof query !== 'string' || query.length > 4000) throw new Error('Search query must be a string of at most 4000 characters');
      const limit = options.limit ?? 10;
      if (!Number.isInteger(limit) || limit < 1 || limit > 30) throw new Error('Search limit must be between 1 and 30');
      const state = createSession({corpusId, computationId:navigator.computationId, query, ...Object.fromEntries(['intent','workRelation','lens','constraints','focusIds'].filter(key => options[key] !== undefined).map(key => [key,options[key]]))});
      return navigator.search(query, {...currentState(state), limit});
    },
    evidence(ids) { if (!Array.isArray(ids) || ids.length > 30 || ids.some(id => typeof id !== 'string')) throw new Error('Supply at most 30 string evidence IDs'); return navigator.getEvidence(ids); },
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
  };
}
export async function readConnection(filename = DEFAULT_CONNECTION) {
  const connection = JSON.parse(await readFile(filename, 'utf8'));
  const url = new URL(connection.url);
  if (url.protocol !== 'http:' || url.hostname !== '127.0.0.1' || url.username || url.password || url.pathname !== '/') throw new Error('Bridge connection must be an http://127.0.0.1:PORT/ URL');
  if (typeof connection.token !== 'string' || connection.token.length < 32) throw new Error('Invalid bridge session token');
  return connection;
}
export async function bridgeCall(connection, endpoint, body) {
  const response = await fetch(new URL(endpoint, connection.url), {
    method: body === undefined ? 'GET' : 'POST',
    headers: {'Authorization': `Bearer ${connection.token}`, ...(body === undefined ? {} : {'Content-Type': 'application/json'})},
    ...(body === undefined ? {} : {body: JSON.stringify(body)}),
    signal: AbortSignal.timeout(120000),
  });
  const value = await response.json();
  if (!response.ok) throw new Error(value.error ?? `Bridge request failed (${response.status})`);
  return value;
}
/** Compact semantic object for agents; full basis/coordinates remain available. */
export function agentSnapshot(snapshot, {full = false} = {}) {
  if (full) return snapshot;
  const {view, session, revision, browserStatus} = snapshot;
  const {basis, center, groupCentroids, ...chart} = view.chart;
  return {
    revision, browserStatus, resultDetail:'agent-summary', state: currentState(session),
    history: session.states.map((state, index) => ({index, id: state.id, query: state.query, intent: state.intent, workRelation: state.workRelation, active: index === session.cursor})),
    view: {
      ...view,
      nodeCount:view.nodes.length,edgeCount:view.edges.length,
      nodes:view.nodes.slice(0,12).map(node=>({
        id:node.id,paperId:node.paperId,title:node.title,label:node.label,
        x:node.x,y:node.y,score:node.score,residual:node.residual,sourceUrl:node.sourceUrl,
        retrieval:node.retrieval,
        evidence:{id:node.evidence.id,text:node.evidence.text,lens:node.evidence.lens,date:node.evidence.date,claimStatus:node.evidence.claimStatus},
      })),
      edges: view.edges.filter(edge => view.nodes.slice(0,12).some(node=>node.id===edge.source)&&view.nodes.slice(0,12).some(node=>node.id===edge.target)).slice(0,20),
      directions:view.directions.map(({memberIds,...direction})=>direction),
      detailNotice:'First 12 ranked sources and up to 20 edges shown. Read evidence by ID; request navigator_state full:true for all points, provenance and basis.',
      chart: {...chart, basisDimensions: basis?.map(row => row.length), centerDimensions: center?.length,groupCentroidCount:groupCentroids?.length},
    },
  };
}
