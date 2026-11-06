import { currentState, exportSession, validateSession } from '/lib/protocol/session.mjs';
import {CAPSULE_KIND, NATIVE_BUILDER, MAX_JSON_BYTES, MAX_COMPRESSED_BYTES, createCapsule, validateCapsule, capsuleCapabilities, decodeCapsuleBytes, encodeCapsuleBytes} from '/lib/protocol/capsule.mjs';
import { placeChartLabel } from '/chart-labels.mjs';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const labels = { explore: 'Explore connections', derive: 'How is it derived?', phenomenology: 'Physical implications', recent: 'Recent within this corpus', using: 'Work using this idea', combined: 'Question + method', physical_question: 'Physical question', method: 'Methods', on: 'work on this idea', either: 'work on or using this idea' };
const colors = ['#a82a2a', '#3f6788', '#786854', '#76617c', '#5a796e'];
let session, view, worker, selectedId, selectedDirectionId, bridge, events, revision = -1, busy = false, allEvidence = false;
let activePanel = 'sources', sourceEpoch = 0, userIntent = 0, draftVersion = 0, draftDirty = false;
let actionQueue = Promise.resolve(), loadingTask = Promise.resolve(), queuedBridgeSnapshot = null, bridgeNeedsRebase = false;
let bridgeRebaseRevision = null;
let activeCapsule, uiRevision = 0, nativeComputationId, nativeEmptySnapshot, workerReady, routeGeneration = 0, routeAbort;
let acceptedCount = 0, renderedRevision = -1;
const observers = new Set(), readyWaiters = [];
const capsuleStorageKey = 'eigenquestions:view:v1';
const columnViews = new Map(), acceptedCapsules = new Map();
const columnStorageKey = 'eigenquestions:columns:v2';
try { for (const item of JSON.parse(localStorage.getItem(columnStorageKey) || '[]')) if (item?.stateId && Array.isArray(item.directions)) columnViews.set(item.stateId, item); } catch {}
let requestId = 0;
const pending = new Map();
let fragment = new URLSearchParams(location.hash.slice(1));
const storageKey = 'eigenquestions:session:v1';
const bridgeStorageKey = 'eigenquestions:companion:v1';
let viewerId;
try { viewerId = sessionStorage.getItem('eigenquestions:viewer:v1') || crypto.randomUUID(); sessionStorage.setItem('eigenquestions:viewer:v1', viewerId); }
catch { viewerId = crypto.randomUUID(); }

function el(tag, className, text) { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; }
function svg(tag, attrs = {}, text) { const node = document.createElementNS(svgNS, tag); for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value); if (text !== undefined) node.textContent = text; return node; }
function status(message, error = false) { $('status').textContent = message; $('status').classList.toggle('error', error); }
function safeUrl(value) { try { const u = new URL(value); return ['https:', 'http:'].includes(u.protocol) ? u.href : null; } catch { return null; } }
function short(value, max = 90) { const str = String(value || ''); return str.length > max ? `${str.slice(0, max - 1).replace(/\s+\S*$/, '')}…` : str; }
function readable(value) { return typeof value === 'number' ? Number(value.toPrecision(4)).toString() : typeof value === 'object' ? JSON.stringify(value) : String(value ?? 'not supplied'); }
function setBusy(value, message = 'Updating directions…') {
  busy = value; document.body.classList.toggle('busy', value);
  document.body.dataset.busy = document.documentElement.dataset.busy = String(value);
  $('pending-indicator').hidden = !value; $('pending-label').textContent = message;
  $('explore-button').setAttribute('aria-busy', String(value));
  $('chart').setAttribute('aria-busy', String(value));
}
function callWorker(type, payload) { return new Promise((resolve, reject) => { const id = ++requestId; pending.set(id, { resolve, reject }); worker.postMessage({ id, type, payload }); }); }
function readableSession(capsule) {
  if (capsule.snapshot.session) return capsule.snapshot.session;
  const v = capsule.snapshot.view;
  return {cursor: 0, states: [{id: v.stateId, corpusId: v.corpusId, computationId: v.computationId, query: capsule.context.question, focusIds: [], constraints: {excludeIds: []}, intent: 'explore', lens: 'combined', workRelation: 'either'}]};
}
function canAttemptContinuation() { return activeCapsule?.continuation.mode === 'native-actions' && Boolean(activeCapsule.snapshot.session); }
function historicalAction(stateId, direction) { const capsule = acceptedCapsules.get(stateId); return capsule?.continuation.actions.find(item => item.id === direction.id)?.action || (columnViews.get(stateId)?.authored ? null : {type:'select',directionId:direction.id}); }
function followDirection(direction) {
  const next = activeCapsule.continuation.actions.find(item => item.id === direction.id);
  if (!next || !canAttemptContinuation()) { status('This supplied group has no executable next action. Inspect its sources, or start a new path.', true); return; }
  return action(next.action, { explicitContinuation: true });
}
function capabilities() { return activeCapsule ? capsuleCapabilities(activeCapsule, nativeComputationId) : {display: false, recompute: false, continue: false}; }
function machineRead() {
  return structuredClone({apiVersion: '1.0.0', revision: uiRevision, busy, mode: bridge ? 'local-companion' : 'browser', renderedRevision,
    capabilities: capabilities(), capsule: activeCapsule ?? null});
}
function notifyAccepted() {
  $('stored-view-link').hidden = true; $('stored-view-url').value = ''; $('stored-view-status').textContent = '';
  ++uiRevision; ++acceptedCount;
  document.documentElement.dataset.uiRevision = String(uiRevision);
  document.documentElement.dataset.acceptedCount = String(acceptedCount);
  const accepted = uiRevision;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    if (uiRevision !== accepted) return;
    renderedRevision = accepted; document.documentElement.dataset.renderedRevision = String(accepted);
  }));
  const snapshot = machineRead();
  for (const resolve of readyWaiters.splice(0)) resolve(snapshot);
  for (const callback of observers) { try { callback(structuredClone(snapshot)); } catch { /* Observer errors do not change the scientific state. */ } }
  window.dispatchEvent(new CustomEvent('eigenquestions:state', {detail: snapshot}));
}
function assertRevision(expected) {
  if (!Number.isInteger(expected) || expected !== uiRevision) {
    const error = new Error('The visible view changed. Read the current revision before applying another view.'); error.code = 'revision_conflict'; error.current = machineRead(); throw error;
  }
}
function save() {
  if (!session) return;
  try { if (activeCapsule) localStorage.setItem(capsuleStorageKey, JSON.stringify(activeCapsule)); if (activeCapsule?.snapshot.session) localStorage.setItem(storageKey, JSON.stringify(exportSession(session))); } catch {}
  const cached = [...columnViews.values()].slice(-24);
  setTimeout(() => { try { localStorage.setItem(columnStorageKey, JSON.stringify(cached)); } catch {} }, 0);
}
function rememberView(result) {
  if (activeCapsule) { acceptedCapsules.delete(result.stateId); acceptedCapsules.set(result.stateId, structuredClone(activeCapsule)); while (acceptedCapsules.size > 24) acceptedCapsules.delete(acceptedCapsules.keys().next().value); }
  columnViews.delete(result.stateId);
  columnViews.set(result.stateId, { authored: activeCapsule?.builder.id !== NATIVE_BUILDER, stateId: result.stateId, computationId: result.computationId, directions: result.directions.map(({ id, label, query, seedIds, sourceCount, evidenceIds }) => ({ id, label, query, seedIds, sourceCount, evidenceIds })) });
  while (columnViews.size > 24) columnViews.delete(columnViews.keys().next().value);
}
function clearViewRoute() { const hash = new URLSearchParams(location.hash.slice(1)); if (hash.has('view') || hash.has('focus')) history.replaceState(null, '', location.pathname + location.search); }
function accept(snapshot, { formVersion, keepRoute = false, preserveContext = false, context: suppliedContext } = {}) {
  if (!snapshot?.session || !snapshot?.view) throw new Error('The companion returned an incomplete session.');
  const next = validateSession(snapshot.session);
  if (snapshot.view.corpusId !== next.corpusId || snapshot.view.computationId !== next.computationId || snapshot.view.stateId !== currentState(next).id) throw new Error('The view does not match the current question or computation. Reconnect or import a fresh session.');
  if (!Array.isArray(snapshot.view.nodes) || !Array.isArray(snapshot.view.directions)) throw new Error('The companion returned an invalid view.');
  if (snapshot.revision !== undefined && snapshot.revision <= revision) return false;
  if (snapshot.revision !== undefined) revision = snapshot.revision;
  nativeComputationId = snapshot.view.computationId;
  if (!keepRoute) clearViewRoute();
  const previousContext = suppliedContext || (preserveContext ? activeCapsule?.context : null);
  activeCapsule = createCapsule(snapshot, previousContext ? {context: {...structuredClone(previousContext), question: currentState(next).query, history: next.states.map((s, index) => ({question: s.query, focusIds: s.focusIds, active: index === next.cursor}))}} : {});
  session = next; view = activeCapsule.snapshot.view; selectedId = null; selectedDirectionId = null; allEvidence = false;
  if (formVersion !== undefined && formVersion === draftVersion) draftDirty = false;
  rememberView(view); render(); save(); notifyAccepted();
  if (bridge && Number.isInteger(snapshot.revision)) {
    const renderedState = currentState(next).id, source = sourceEpoch;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (bridge && source === sourceEpoch && document.documentElement.dataset.stateId === renderedState) bridgeFetch('/api/viewer', { method: 'POST', body: JSON.stringify({ viewerId, stateId: renderedState, revision: snapshot.revision }) }).catch(() => {});
    }));
  }
  return true;
}
function acceptCapsule(input, {expectedRevision, clearForm = false, keepRoute = false} = {}) {
  if (expectedRevision !== undefined) assertRevision(expectedRevision);
  const capsule = structuredClone(validateCapsule(input));
  if (!keepRoute) clearViewRoute();
  ++routeGeneration; routeAbort?.abort();
  ++userIntent; ++sourceEpoch; events?.close(); bridge = null; revision = -1;
  try { sessionStorage.removeItem(bridgeStorageKey); } catch {}
  queuedBridgeSnapshot = null; bridgeNeedsRebase = false; actionQueue = Promise.resolve(); loadingTask = Promise.resolve();
  activeCapsule = capsule; session = readableSession(capsule); view = capsule.snapshot.view;
  selectedId = null; selectedDirectionId = null; allEvidence = false;
  if (clearForm) draftDirty = false;
  $('connection-status').textContent = 'Browser session';
  rememberView(view); render(); save(); setBusy(false); notifyAccepted();
  return machineRead();
}
async function verifyAuthoredAnchors(capsule, payload) {
  if (!capsule || (capsule.builder.id === NATIVE_BUILDER && capsule.builder.version === '1.0.0')) return;
  if (!payload.focusIds?.length) return;
  const evidence = await callWorker('evidence', {ids:payload.focusIds});
  const missing = evidence.filter(source => source.error).map(source => source.id);
  if (missing.length) throw new Error(`Cannot continue this authored view: ${missing.slice(0,3).join(', ')} is not a source in the loaded corpus. The supplied view is unchanged; use genuine source anchors.`);
}
function action(payload, { followup, operation = 'action', clearForm = false, explicitContinuation = false } = {}) {
  ++routeGeneration; routeAbort?.abort();
  const ticket = ++userIntent, source = sourceEpoch, formVersion = draftVersion;
  const baseCapsule = activeCapsule;
  const baseSession = activeCapsule?.snapshot.session ? structuredClone(activeCapsule.snapshot.session) : null, baseRevision = revision;
  const transport = bridge;
  setBusy(true, payload.type === 'reset' ? 'Starting a new path…' : 'Updating directions…');
  status('Computing directions from the current sources…');
  const run = async () => {
    try {
      await loadingTask;
      if (ticket !== userIntent || source !== sourceEpoch) return;
      let result, followed = false, branchContext;
      if (!transport && baseSession && ['back','forward','replay'].includes(payload.type)) {
        const index = payload.type === 'back' ? Math.max(0, baseSession.cursor - 1) : payload.type === 'forward' ? Math.min(baseSession.states.length - 1, baseSession.cursor + 1) : payload.index;
        const target = baseSession.states[index], saved = target && acceptedCapsules.get(target.id);
        if (saved && saved.builder.id !== NATIVE_BUILDER) {
          const restored = structuredClone(saved); restored.snapshot.session = {...baseSession,cursor:index};
          if (!followup) return acceptCapsule(restored);
          await ensureWorker();
          if (ticket !== userIntent || source !== sourceEpoch) return {superseded:true};
          if (!capsuleCapabilities(restored,nativeComputationId).continue) throw new Error('This authored historical view has no compatible continuation. Reopen its file to inspect it.');
          await verifyAuthoredAnchors(restored,followup);
          if (ticket !== userIntent || source !== sourceEpoch) return {superseded:true};
          result = await callWorker('action',{action:followup,baseSession:restored.snapshot.session}); followed = true; branchContext = restored.context;
        } else if (target && columnViews.get(target.id)?.authored && !saved) throw new Error('The exact authored historical view is no longer cached. Reopen its full view file; native recomputation would replace its grouping.');
      }
      if (result) { /* Exact authored historical branch was resolved above. */ } else if (transport) {
        let expectedRevision = baseRevision < 0 ? revision : baseRevision;
        if (bridgeNeedsRebase && baseSession && payload.type !== 'reset') {
          const restored = await bridgeFetch('/api/import', { method: 'POST', headers: { 'If-Match': `"${bridgeRebaseRevision}"` }, body: JSON.stringify(exportSession(baseSession)) }, transport);
          expectedRevision = restored.revision;
          if (ticket !== userIntent || source !== sourceEpoch) { bridgeNeedsRebase = true; bridgeRebaseRevision = restored.revision; return; }
        } else if (bridgeNeedsRebase && payload.type === 'reset') {
          expectedRevision = bridgeRebaseRevision;
        }
        bridgeNeedsRebase = false;
        result = await bridgeFetch(operation === 'import' ? '/api/import' : '/api/action', { method: 'POST', headers: { 'If-Match': `"${expectedRevision}"` }, body: JSON.stringify(payload) }, transport);
      } else {
        const initialized = await ensureWorker();
        if (ticket !== userIntent || source !== sourceEpoch) return {superseded: true};
        if (baseSession && payload.type !== 'reset' && !capsuleCapabilities(baseCapsule, nativeComputationId).continue) throw new Error('This snapshot cannot continue with the installed engine. Start a new path; its original view remains exportable.');
        if (explicitContinuation && baseCapsule.builder.id !== NATIVE_BUILDER && payload.type === 'select') throw new Error('Authored groups need an explicit query and source anchors for native continuation; an authored group ID cannot select a newly computed group.');
        if (operation === 'action') await verifyAuthoredAnchors(baseCapsule,payload);
        if (ticket !== userIntent || source !== sourceEpoch) return {superseded:true};
        result = await callWorker(operation, operation === 'action' ? { action: payload, baseSession: baseSession || initialized.session } : payload);
      }
      if (ticket !== userIntent || source !== sourceEpoch) { if (transport && source === sourceEpoch) { bridgeNeedsRebase = true; bridgeRebaseRevision = result.revision; } return; }
      if (followup && !followed) result = transport ? await bridgeFetch('/api/action', { method: 'POST', headers: { 'If-Match': `"${result.revision}"` }, body: JSON.stringify(followup) }, transport) : await callWorker('action', { action: followup, baseSession: result.session });
      if (ticket !== userIntent || source !== sourceEpoch) { if (transport && source === sourceEpoch) { bridgeNeedsRebase = true; bridgeRebaseRevision = result.revision; } return; }
      // Agent changes may have arrived while this request's response was delayed.
      if (queuedBridgeSnapshot && queuedBridgeSnapshot.revision > (result.revision ?? -1)) result = queuedBridgeSnapshot;
      queuedBridgeSnapshot = null;
      if (payload.type === 'reset') activeCapsule = null;
      accept(result, { formVersion: clearForm ? formVersion : undefined, context: branchContext || (['replay','back','forward'].includes(payload.type) && !followup ? acceptedCapsules.get(result.view.stateId)?.context : undefined), preserveContext: operation === 'action' && !['reset','pivot','replay','back','forward'].includes(payload.type) });
      return machineRead();
    } catch (error) {
      if (ticket === userIntent && source === sourceEpoch) {
        if (error.current) { draftDirty = true; bridgeNeedsRebase = false; const latest = queuedBridgeSnapshot?.revision > error.current.revision ? queuedBridgeSnapshot : error.current; queuedBridgeSnapshot = null; accept(latest); }
        status(error.message, true);
      }
      return {error: error.message, code: error.code || 'action_failed'};
    }
    finally {
      if (ticket === userIntent && source === sourceEpoch) {
        setBusy(false);
        if (queuedBridgeSnapshot) { const queued = queuedBridgeSnapshot; queuedBridgeSnapshot = null; accept(queued); }
      }
    }
  };
  actionQueue = actionQueue.catch(() => {}).then(run);
  return actionQueue;
}
function render() {
  const state = currentState(session), scope = view.diagnostics?.scope || {}, displayQuestion = activeCapsule.context.question;
  const empty = !state.query.trim() && !view.nodes.length;
  document.querySelector('.column-navigation').hidden = empty;
  document.querySelector('.reading-pane').hidden = empty;
  document.querySelector('.navigator-note').hidden = empty || !canAttemptContinuation();
  $('current-context').hidden = empty;
  $('current-question').textContent = displayQuestion || 'Start a new path';
  if (!draftDirty) { $('question').value = displayQuestion; $('intent').value = state.intent; $('lens').value = state.lens; $('work-relation').value = state.workRelation; }
  const context = view.diagnostics?.contextTerms || [];
  $('current-context').textContent = state.query ? `${labels[state.intent]} · ${labels[state.lens]}${state.focusIds.length ? ` · Building on ${state.focusIds.length} sources${context.length ? ` about ${context.slice(0, 3).join(', ')}` : ''}` : ' · Across the corpus'}` : 'Enter a concept or question above. This path has no inherited focus.';
  $('back').disabled = session.cursor === 0 || !canAttemptContinuation();
  $('broaden').disabled = !canAttemptContinuation() || (!state.focusIds.length && !state.constraints?.excludeIds?.length);
  $('path').replaceChildren();
  session.states.forEach((item, index) => {
    if (index) $('path').append(el('span', 'path-arrow', '›'));
    const pathQuestion = (!bridge && acceptedCapsules.get(item.id)?.context.question) || item.query;
    const button = el('button', '', pathQuestion || 'New path'); button.type = 'button'; button.title = `${item.query || 'New path'} · ${labels[item.intent]}`;
    button.setAttribute('aria-label', `Step ${index + 1}: ${item.query || 'New path'}`);
    if (index === session.cursor) button.setAttribute('aria-current', 'step');
    button.disabled = !canAttemptContinuation(); button.addEventListener('click', () => action({ type: 'replay', index })); $('path').append(button);
  });
  $('corpus-scope').textContent = `${(scope.paperCount || 0).toLocaleString()} papers · Swampland-centered collection · ${scope.earliestYear || '?'}–${scope.latestYear || '?'} · Snapshot ${view.diagnostics?.snapshotDate || 'dated in manifest'}. Recent means recent within this collection.`;
  const paperCount = view.diagnostics?.distinctPapers ?? new Set(view.nodes.map(n => n.paperId).filter(Boolean)).size;
  $('evidence-count').textContent = String(activeCapsule.builder.id === NATIVE_BUILDER ? paperCount : view.nodes.length);
  const authored = activeCapsule.builder.id !== NATIVE_BUILDER;
  $('snapshot-notice').hidden = !authored || activeCapsule.builder.id === 'browser-empty';
  $('snapshot-notice').textContent = authored ? `Supplied view · ${activeCapsule.builder.id} ${activeCapsule.builder.version}. Labels and relationships are author interpretations, not verified corpus results. ${activeCapsule.continuation.description}` : '';
  if (authored && activeCapsule.builder.id !== 'browser-empty') { $('current-context').textContent = activeCapsule.context.summary || 'The supplied scientific context and source groups are preserved in this view.'; $('corpus-scope').textContent = `Supplied corpus: ${view.corpusId}`; }
  $('view-geometry').disabled = !view.chart;
  $('export').disabled = !activeCapsule.snapshot.session;
  $('share').disabled = authored || !activeCapsule.snapshot.session;
  if (!view.chart && activePanel === 'geometry') switchPanel('sources');
  updateOptionsSummary(); renderColumns(); renderEvidence();
  if (activePanel === 'geometry') { renderChart(); renderDetails(); }
  status(view.nodes.length ? `${view.directions.length} ${canAttemptContinuation() ? 'next directions' : 'supplied groups'} · ${authored ? `${view.nodes.length} source descriptions` : `${paperCount} papers`} in this view` : state.query ? view.warnings?.[0] || 'No supported sources found. Try another focus.' : 'Ready for your first question.');
  document.documentElement.dataset.ready = 'true';
  document.documentElement.dataset.stateId = state.id;
  document.documentElement.dataset.corpusId = state.corpusId;
}
function renderColumns() {
  const host = $('columns'); host.replaceChildren();
  host.classList.toggle('empty-path', !currentState(session).query && !view.directions.length);
  $('directions-count').textContent = '';
  const states = session.states.slice(0, session.cursor + 1);
  for (let index = 0; index < states.length; index++) {
    const state = states[index], current = index === session.cursor, next = states[index + 1];
    if (!current && !state.query.trim()) continue;
    const cached = columnViews.get(state.id);
    const directions = current ? view.directions : cached?.computationId === state.computationId && !(bridge && cached.authored) ? cached.directions : null;
    const column = el('section', 'miller-column'); column.dataset.stateId = state.id; column.dataset.historyIndex = index; column.dataset.current = String(current);
    const heading = el('div', `column-heading${current ? ' current-column-heading' : ''}`); heading.append(el('span', 'column-step', `Step ${index + 1}`));
    if (!current) heading.append(el('h3', '', short(state.query || 'Your first question', 80)));
    heading.title = state.query; column.append(heading);
    const list = el('div', 'directions'); if (current) list.id = 'directions';
    if (directions?.length) {
      let selected = false;
      directions.forEach((direction, directionIndex) => {
        const row = el('div', 'direction-row'), button = el('button', 'direction'); button.type = 'button'; button.dataset.directionId = direction.id;
        button.title = direction.label; button.setAttribute('aria-label', `Direction ${directionIndex + 1}: ${direction.label}`);
        if (next && next.query === direction.query && direction.seedIds?.every(id => next.focusIds.includes(id))) { button.setAttribute('aria-current', 'step'); selected = true; }
        button.append(el('span', 'direction-number', String(directionIndex + 1).padStart(2, '0')));
        const content = el('span', 'direction-content'); content.append(el('h3', '', direction.label), el('span', 'direction-meta', `${direction.sourceCount || direction.memberIds?.length || direction.evidenceIds.length} source descriptions`));
        button.append(content, el('span', 'direction-arrow', '›'));
        button.disabled = !canAttemptContinuation() || (!current && !historicalAction(state.id,direction)) || (current && !activeCapsule.continuation.actions.some(item => item.id === direction.id && (activeCapsule.builder.id === NATIVE_BUILDER || item.action.type !== 'select')));
        button.addEventListener('click', () => current ? followDirection(direction) : action({ type: 'replay', index }, { followup: historicalAction(state.id,direction) }));
        row.append(button);
        if (current) {
          const inspect = el('button', 'direction-evidence', 'Sources'); inspect.type = 'button'; inspect.setAttribute('aria-label', `Inspect sources for direction ${directionIndex + 1}`); inspect.title = 'Inspect sources'; inspect.setAttribute('aria-pressed', String(selectedDirectionId === direction.id));
          inspect.addEventListener('click', () => {
            selectedDirectionId = direction.id; selectedId = null; allEvidence = false; switchPanel('sources'); renderEvidence();
            host.querySelectorAll('.direction-evidence').forEach(item => item.setAttribute('aria-pressed', String(item === inspect)));
            const heading = $('view-sources'); heading.focus({ preventScroll: true });
            heading.closest('.reading-pane').scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
          }); row.append(inspect);
        }
        list.append(row);
      });
      if (next && !selected) { const follow = el('div', 'column-followup'); follow.append(el('strong', '', 'Follow-up question →'), el('span', '', short(next.query, 120))); list.append(follow); }
    } else if (!current && !directions) {
      const restore = el('div', 'column-restore'); restore.append(el('p', '', 'This step is in your path. Restore it to recompute its directions.'));
      const button = el('button', '', 'Restore step →'); button.type = 'button'; button.addEventListener('click', () => action({ type: 'replay', index })); restore.append(button); list.append(restore);
    } else list.append(el('p', 'empty-state', state.query ? 'No supported directions for this question. Try another focus or broaden the context.' : 'Begin with a physics concept. Your first question will open approximately five directions here.'));
    column.append(list); host.append(column);
  }
  requestAnimationFrame(() => { host.scrollLeft = host.scrollWidth; const crumb = $('path').querySelector('[aria-current]'); if (crumb) $('path').scrollLeft = crumb.offsetLeft - $('path').offsetLeft; updateColumnControls(); });
}
function updateColumnControls() { const host = $('columns'); $('browse-prev').disabled = host.scrollLeft < 2; $('browse-next').disabled = host.scrollLeft + host.clientWidth >= host.scrollWidth - 2; }
function switchPanel(panel) {
  activePanel = panel; document.documentElement.dataset.view = panel;
  $('sources-panel').hidden = panel !== 'sources'; $('chartpanel').hidden = panel !== 'geometry';
  $('view-sources').setAttribute('aria-selected', String(panel === 'sources')); $('view-geometry').setAttribute('aria-selected', String(panel === 'geometry'));
  if (view && panel === 'geometry') { renderChart(); renderDetails(); }
}
function renderChart() {
  const host = $('chart'); host.replaceChildren();
  if (!view.chart) { host.append(el('p', 'empty-state', 'This supplied view has no projection.')); return; }
  if (!view.nodes.length) { host.append(el('p', 'empty-state', 'No source-supported view for this question yet. Try a physics term used in the corpus, or ask your agent to identify a relevant source.')); return; }
  const compact = host.clientWidth < 560;
  // Use CSS-pixel dimensions on narrow charts; geometry still gets one common
  // x/y scale, while numbered controls remain legible and large enough to tap.
  const width = compact ? Math.max(host.clientWidth, 240) : 760;
  const height = compact ? 300 : 420, margin = compact ? 36 : 54;
  const layout = view.chart.kind === 'display-layout';
  const aggregate = layout || view.chart.fitScope === 'direction-centroids';
  const showSources = layout || !aggregate || $('show-sources').checked;
  $('chart-controls').hidden = layout || !aggregate;
  $('chart-key').textContent = layout ? 'Authored groups and sources' : aggregate ? `${view.directions.length} computed directions` : 'Source descriptions';
  const plotted = aggregate ? (showSources ? [...view.nodes, ...view.directions] : view.directions) : view.nodes;
  const xs = plotted.map(n => Number(n.x)), ys = plotted.map(n => Number(n.y));
  if (![...xs, ...ys].every(Number.isFinite)) throw new Error('The view contains invalid coordinates.');
  const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
  const scale = Math.min((width - margin * 2) / Math.max(xmax - xmin, .1), (height - margin * 2) / Math.max(ymax - ymin, .1));
  const x = val => width / 2 + (val - (xmin + xmax) / 2) * scale, y = val => height / 2 - (val - (ymin + ymax) / 2) * scale;
  const plot = svg('svg', { viewBox: `0 0 ${width} ${height}`, class: compact ? 'compact-chart' : '', role: 'group', 'aria-label': aggregate ? 'Computed two-dimensional view of five directions. Numbered markers match the full direction cards below. Select a marker to follow its direction.' : 'Computed two-dimensional view. Select a source point to read its evidence. The same sources are listed after the directions.' });
  host.append(plot); // Actual SVG text metrics are available for placement below.
  for (let i = 1; i < 7; i++) plot.append(svg('line', { x1: i * width / 7, y1: 25, x2: i * width / 7, y2: height - 25, stroke: '#edf0e7', 'stroke-width': 1 }));
  for (let i = 1; i < 5; i++) plot.append(svg('line', { x1: 30, y1: i * height / 5, x2: width - 30, y2: i * height / 5, stroke: '#edf0e7', 'stroke-width': 1 }));
  const byId = new Map([...view.nodes, ...view.directions].map(n => [n.id, n]));
  for (const edge of (showSources ? view.edges.slice(0, 180) : [])) {
    const a = byId.get(edge.source), b = byId.get(edge.target); if (!a || !b) continue;
    const edgeLine = svg('line', { x1: x(a.x), y1: y(a.y), x2: x(b.x), y2: y(b.y), stroke: edge.type === 'same_paper' ? '#8da78f' : '#c1cec1', 'stroke-opacity': edge.type === 'same_paper' ? .48 : .28, 'stroke-width': .8, ...(edge.type === 'same_paper' ? {} : { 'stroke-dasharray': '2 4' }) }); edgeLine.append(svg('title', {}, `Supplied relation: ${edge.type}`)); plot.append(edgeLine);
  }
  const seedIds = new Set(view.directions.map(d => d.seedIds?.[0]));
  const labelBoxes = [];
  for (const node of (showSources ? view.nodes : [])) {
    const index = view.directions.findIndex(d => d.id === node.directionId), color = colors[Math.max(index, 0) % colors.length];
    const group = svg('g', { class: `chart-node${node.id === selectedId ? ' selected' : ''}`, tabindex: 0, role: 'button', 'aria-label': `${node.title}. ${node.label}`, 'aria-pressed': String(node.id === selectedId), 'data-source-id': node.id });
    const r = seedIds.has(node.id) ? 6 : 3.7;
    group.append(svg('circle', { cx: x(node.x), cy: y(node.y), r, fill: node.inSlab === false ? '#fffef9' : color, stroke: color, 'stroke-width': 1.3, 'fill-opacity': .86 }));
    group.append(svg('title', {}, `${node.title}\n${node.label}\nResidual from plane: ${readable(node.residual)}`));
    const select = () => { selectedId = node.id; selectedDirectionId = null; switchPanel('sources'); renderEvidence(); };
    group.addEventListener('click', select); group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(); } });
    plot.append(group);
    if (!compact && !aggregate && (seedIds.has(node.id) || node.id === selectedId)) {
      const text = short(node.title, 47), labelWidth = Math.min(text.length * 5.6, 280);
      let lx = Math.min(width - labelWidth - 12, Math.max(12, x(node.x) + 10)), ly = y(node.y) - 11;
      for (let attempt = 0; attempt < 8 && labelBoxes.some(b => lx < b.x + b.w && lx + labelWidth > b.x && Math.abs(ly - b.y) < 16); attempt++) ly += 17;
      ly = Math.min(height - 12, Math.max(15, ly)); labelBoxes.push({ x: lx, y: ly, w: labelWidth });
      group.append(svg('text', { x: lx, y: ly }, text));
    }
  }
  const directionMarkers = view.directions.map(direction => ({ x: x(direction.x), y: y(direction.y), radius: Math.max(compact ? 16 : 0, 10 + 18 * Math.sqrt(direction.massFraction || .2)) }));
  const markerObstacles = directionMarkers.map(marker => ({ ...marker, radius: Math.max(marker.radius, 22) + 4 }));
  if (showSources) markerObstacles.push(...view.nodes.map(node => ({ x: x(node.x), y: y(node.y), radius: 9 })));
  const directionLabelLayer = svg('g', { class: 'direction-label-layer', 'aria-hidden': 'true', 'pointer-events': 'none' });
  const directionMarkerLayer = svg('g', { class: 'direction-marker-layer' });
  plot.append(directionLabelLayer);
  if (aggregate) view.directions.forEach((direction, index) => {
    const color = colors[index % colors.length], cx = x(direction.x), cy = y(direction.y);
    const group = svg('g', { class: 'chart-node chart-direction', tabindex: 0, role: 'button', 'aria-label': `Follow direction ${index + 1}: ${direction.label}`, 'data-direction-id': direction.id });
    const radius = directionMarkers[index].radius;
    group.append(svg('circle', { cx, cy, r: Math.max(radius, 22), fill: 'transparent', stroke: 'none', class: 'direction-hit-target' }));
    group.append(svg('circle', { cx, cy, r: radius, fill: color, stroke: '#fffef9', 'stroke-width': 3, 'fill-opacity': .95, class: 'direction-dot' }));
    group.append(svg('text', { x: cx, y: cy + 4, 'text-anchor': 'middle', class: 'direction-marker' }, String(index + 1)));
    group.append(svg('title', {}, layout ? `${direction.label}\nAuthor-supplied display position; not an embedding-space distance.` : `${direction.label}\n${direction.sourceCount} source descriptions; ${(100 * direction.massFraction).toFixed(1)}% of retrieval weight.\nWithin-group RMS spread in embedding space: ${readable(direction.withinGroupRms)}. Group proximity is not a physical implication.`));
    const words = short(direction.label, 85).split(' '), lines = []; let line = '';
    for (const word of words) { if ((line + ' ' + word).length > 31 && line) { lines.push(line); line = word; } else line += (line ? ' ' : '') + word; }
    if (line) lines.push(line);
    if (!compact) {
      const text = svg('text', { x: 0, y: 0, class: 'direction-label', 'data-direction-id': direction.id });
      lines.forEach((line, i) => text.append(svg('tspan', { x: 0, dy: i ? 15 : 0 }, line)));
      directionLabelLayer.append(text);
      const measured = text.getBBox(), padding = 3;
      const box = placeChartLabel({ anchor: directionMarkers[index], width: measured.width + padding * 2, height: measured.height + padding * 2, bounds: { width, height }, circles: markerObstacles, labels: labelBoxes });
      if (box) { text.setAttribute('transform', `translate(${box.x + padding - measured.x} ${box.y + padding - measured.y})`); labelBoxes.push(box); }
      else text.remove(); // Full label remains in the numbered direction card.
    }
    const follow = () => followDirection(direction); group.addEventListener('click', follow); group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); follow(); } });
    directionMarkerLayer.append(group);
  });
  plot.append(directionMarkerLayer); // Numbers and tap targets always paint last.
  if (view.chart.kind === 'display-layout') { $('chart-caption').textContent = 'Author-supplied display layout. These positions do not claim to be an affine projection or a physical distance.'; return; }
  const explained = Math.round((view.chart.explainedVariance || 0) * 100);
  $('chart-caption').textContent = aggregate
    ? `${compact ? 'Numbers match the full directions below. ' : ''}These ${view.directions.length} points are weighted centers of source groups, sized by retrieval weight. This plane retains ${explained}% of variation between those centers, versus ${Math.round((view.chart.sourceDiagnostics?.explainedVariance || 0) * 100)}% across individual source descriptions. Groups can be broad; proximity is a reading suggestion, not a physical claim.`
    : `This local 2D projection retains ${explained}% of the selected variation. Filled points meet the current residual cutoff; hollow points lie farther from the plane. Lines show retrieval affinity or the same paper, not established physical connections.`;
}
function renderEvidence() {
  $('evidence').replaceChildren();
  let nodes = [...view.nodes];
  const direction = view.directions.find(item => item.id === selectedDirectionId);
  if (direction) { const ids = new Set(direction.memberIds || direction.evidenceIds); nodes = nodes.filter(node => ids.has(node.id)); }
  $('clear-evidence').hidden = !direction;
  $('evidence-description').textContent = direction ? `Sources behind: ${direction.label}` : 'Read the extracted descriptions, then check the original papers.';
  if (selectedId) nodes.sort((a, b) => Number(b.id === selectedId) - Number(a.id === selectedId));
  const shown = allEvidence ? nodes : nodes.slice(0, 7);
  for (const node of shown) {
    const evidence = node.evidence || {}, card = el('article', `evidence-card${node.id === selectedId ? ' selected' : ''}`);
    card.dataset.sourceId = node.id;
    const relation = node.retrieval?.workRelation?.kind;
    card.append(el('p', 'source-meta', `${evidence.date || evidence.year || node.year || 'date unavailable'} · ${labels[evidence.lens || node.lens] || 'Source'}${relation ? ` · ${relation === 'ambiguous' ? 'role uncertain' : relation}` : ''}`));
    const title = el('h3'), paperUrl = safeUrl(node.sourceUrl || evidence.url);
    if (paperUrl) { const link = el('a', '', node.title); link.href = paperUrl; link.target = '_blank'; link.rel = 'noopener noreferrer'; title.append(link); } else title.textContent = node.title; card.append(title);
    card.append(el('p', 'passage', evidence.text || node.label));
    const details = el('details'); details.append(el('summary', '', 'Source scope & provenance'));
    details.append(el('p', '', 'Extracted source description, not a direct quotation or independently verified result.'));
    if (node.retrieval?.workRelation?.basis) details.append(el('p', '', `Role assessment: ${node.retrieval.workRelation.basis}.`));
    if (evidence.sourceNotice) details.append(el('p', '', evidence.sourceNotice));
    details.append(el('p', '', `Source ID: ${node.id}`));
    if (evidence.sourceRecordIds?.length) details.append(el('p', '', `Source records: ${evidence.sourceRecordIds.join(', ')}`));
    if (view.chart?.kind === 'affine-plane') details.append(el('p', '', `Distance from this local plane: ${readable(node.residual)}. ${node.inSlab === false ? 'Outside' : 'Within'} the chosen residual cutoff.`)); card.append(details);
    const actions = el('div', 'source-actions'), url = safeUrl(node.sourceUrl || evidence.url);
    if (url) { const link = el('a', '', 'Read paper ↗'); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; actions.append(link); }
    const focus = el('button', '', 'Explore this source'); focus.type = 'button'; focus.disabled = !canAttemptContinuation() || activeCapsule.builder.id !== NATIVE_BUILDER; focus.addEventListener('click', () => action({ type: 'refine', query: String(evidence.text || node.label).slice(0, 2000), focusIds: [node.id] })); actions.append(focus); card.append(actions); $('evidence').append(card);
  }
  if (!allEvidence && nodes.length > shown.length) { const more = el('button', '', `Show all ${nodes.length} source descriptions`); more.type = 'button'; more.addEventListener('click', () => { allEvidence = true; renderEvidence(); }); $('evidence').append(more); }
}
function renderDetails() {
  const host = $('chart-details'); host.replaceChildren();
  if (!view.chart) return;
  if (view.chart.kind === 'display-layout') { host.append(el('p', '', 'This is a supplied display layout, without a claimed embedding-plane construction.')); return; }
  const dl = el('dl');
  for (const [key, value] of [['Construction', view.chart.method], ['Fitted objects', view.chart.fitScope || 'source descriptions'], ['Vector dimensions', view.chart.dimension], ['Metric', view.chart.metric], ['Variation retained', `${((view.chart.explainedVariance || 0) * 100).toFixed(1)}%`], ['Residual cutoff', view.chart.thickness], ['Nearest-group recall', view.chart.neighborRecallAt1 ?? view.chart.neighborRecallAt5], ['Projection stress', view.chart.stress], ['Source variation retained', view.chart.sourceDiagnostics ? `${(view.chart.sourceDiagnostics.explainedVariance * 100).toFixed(1)}%` : 'same as above'], ['Source neighborhood recall', view.chart.sourceDiagnostics?.neighborRecallAt5], ['Global candidates', view.diagnostics?.globalCandidateCount], ['State', view.stateId], ['Corpus', view.corpusId]]) { dl.append(el('dt', '', key), el('dd', '', readable(value))); }
  host.append(dl);
  if (view.chart.fitScope === 'direction-centroids') {
    const groups = el('ul'); view.directions.forEach((direction, index) => groups.append(el('li', '', `Direction ${index + 1}: ${direction.sourceCount} source descriptions, ${(100 * direction.massFraction).toFixed(1)}% of retrieval weight, within-group RMS spread ${readable(direction.withinGroupRms)}, distance from plane ${readable(direction.residual)}.`))); host.append(groups);
  }
  const list = el('ul'); for (const warning of view.warnings || []) list.append(el('li', '', warning)); host.append(list);
}
function download(name, payload) { const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })); const a = el('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
function encodeFocus(state) { const encoded = btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(state)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); if (encoded.length > 16000) throw new Error('Focus is too large for a link. Save or download the full view instead.'); return encoded; }
function decodeFocus(value) { if (value.length > 16000) throw new Error('Shared focus is too large. Import a session file instead.'); return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(value.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)))); }
async function bridgeFetch(route, options = {}, connection = bridge) {
  const response = await fetch(new URL(route, connection.origin), { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${connection.token}`, ...options.headers }, signal: AbortSignal.timeout(20000) });
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(response.status === 409 ? 'Your agent changed the path while this request was pending. The newer path is shown; your draft is preserved. Review it and search again.' : `Companion returned HTTP ${response.status}. Check the origin and session token.`);
    if (response.status === 409) error.current = result.current;
    throw error;
  }
  return result;
}
async function connect(origin, token) {
  const url = new URL(origin);
  if (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || !['http:', 'https:'].includes(url.protocol)) throw new Error('The companion must use a loopback origin on your computer.');
  if (!token) throw new Error('A session token is required. Use the companion launch link.');
  const source = ++sourceEpoch, connectionIntent = ++userIntent; events?.close(); queuedBridgeSnapshot = null; bridgeNeedsRebase = false;
  actionQueue = Promise.resolve(); loadingTask = Promise.resolve();
  bridge = { origin: url.origin, token }; revision = -1;
  const connection = bridge;
  try {
    loadingTask = bridgeFetch('/api/session', {}, connection);
    const snapshot = await loadingTask;
    if (source !== sourceEpoch) return;
    accept(snapshot); if (connectionIntent === userIntent) setBusy(false);
    const eventUrl = new URL('/api/events', bridge.origin); eventUrl.searchParams.set('token', token);
    events = new EventSource(eventUrl);
    events.onmessage = ({ data }) => {
      if (source !== sourceEpoch) return;
      try { const snapshot = JSON.parse(data); if (busy) { if (!queuedBridgeSnapshot || snapshot.revision > queuedBridgeSnapshot.revision) queuedBridgeSnapshot = snapshot; } else accept(snapshot); $('connection-status').textContent = 'Agent connected · live updates'; } catch (error) { status(error.message, true); }
    };
    events.onopen = () => { if (source === sourceEpoch) $('connection-status').textContent = 'Agent connected · live updates'; };
    events.onerror = () => { if (source === sourceEpoch) { $('connection-status').textContent = 'Companion reconnecting…'; status('The companion connection interrupted. Updates resume when it reconnects.', true); } };
    $('connection-status').textContent = 'Agent connected · live updates'; $('bridge-message').textContent = 'Connected. Agent actions update this view automatically.';
    let savedToken = false;
    try { sessionStorage.setItem(bridgeStorageKey, JSON.stringify(bridge)); savedToken = true; } catch {}
    if (fragment.has('token') && savedToken) history.replaceState(null, '', location.pathname + location.search);
  } catch (error) { if (source === sourceEpoch) { bridge = null; events?.close(); setBusy(false); } throw error; }
}
async function ensureWorker() {
  if (workerReady) return workerReady;
  worker = new Worker('/compute-worker.js', {type: 'module'});
  worker.onmessage = ({data}) => {
    if (data.type === 'progress') { if (busy && !bridge) status(data.stage === 'index' ? 'Preparing the source index on your device…' : `Loading corpus: ${data.completed}/${data.total} files. Questions compute on your device.`); return; }
    const request = pending.get(data.id); if (!request) return; pending.delete(data.id); data.error ? request.reject(new Error(data.error)) : request.resolve(data.result);
  };
  worker.onerror = event => { for (const request of pending.values()) request.reject(new Error(event.message || 'The computation worker failed.')); pending.clear(); workerReady = null; };
  workerReady = callWorker('init', {}).then(result => { nativeComputationId = result.view.computationId; nativeEmptySnapshot = result; return result; }).catch(error => { workerReady = null; worker?.terminate(); throw error; });
  return workerReady;
}
async function startBrowser(initial = {}, {keepRoute = false} = {}) {
  const source = ++sourceEpoch, ticket = userIntent;
  actionQueue = Promise.resolve(); revision = -1; queuedBridgeSnapshot = null; bridgeNeedsRebase = false;
  setBusy(true, 'Preparing the corpus…');
  loadingTask = (async () => { const initialized = await ensureWorker(); return initial.session ? callWorker('import', initial.session) : initial.state ? callWorker('orient', initial.state) : initialized; })();
  try { const result = await loadingTask; if (source === sourceEpoch && ticket === userIntent) accept(result, {keepRoute}); }
  finally { if (source === sourceEpoch && ticket === userIntent) setBusy(false); }
}
function emptyPath() {
  if (nativeEmptySnapshot) return acceptCapsule(createCapsule(nativeEmptySnapshot));
  return acceptCapsule({schemaVersion:'1.0.0',kind:CAPSULE_KIND,builder:{id:'browser-empty',version:'1.0.0'},context:{question:''},snapshot:{view:{stateId:'empty',corpusId:'not-loaded',computationId:'not-loaded',query:'',nodes:[],directions:[],edges:[],warnings:[],diagnostics:{},chart:null}},continuation:{mode:'snapshot-only',originStateId:'empty',description:'Enter a question to load the collection and compute a new path on this device.',actions:[]}});
}
function updateOptionsSummary() {
  const defaults = { intent: 'explore', lens: 'combined', 'work-relation': 'either', transition: 'refine' };
  const changed = Object.entries(defaults).filter(([id, value]) => $(id).value !== value).length;
  const approach = $('intent').selectedOptions[0]?.textContent || 'Explore connections';
  $('options-summary').textContent = changed ? `${approach} · customized` : approach;
}
$('options-toggle').addEventListener('click', () => { const open = $('options-toggle').getAttribute('aria-expanded') !== 'true'; $('options-toggle').setAttribute('aria-expanded', String(open)); $('options-toggle').closest('.search-workbench').classList.toggle('options-open', open); });
const markDraft = () => { draftDirty = true; draftVersion++; updateOptionsSummary(); };
$('question').addEventListener('input', markDraft);
for (const id of ['intent', 'lens', 'work-relation', 'transition']) $(id).addEventListener('change', markDraft);
$('question-form').addEventListener('submit', event => {
  event.preventDefault(); const query = $('question').value.trim();
  if (!query) { status('Enter a physics question or concept.', true); $('question').focus(); return; }
  action({ type: $('transition').value, query, intent: $('intent').value, lens: $('lens').value, workRelation: $('work-relation').value }, { clearForm: true });
});
$('intent').addEventListener('change', () => { if ($('intent').value === 'using') $('work-relation').value = 'using'; updateOptionsSummary(); });
$('show-sources').addEventListener('change', () => { if (view && activePanel === 'geometry') renderChart(); });
$('view-sources').addEventListener('click', () => switchPanel('sources'));
$('view-geometry').addEventListener('click', () => switchPanel('geometry'));
for (const id of ['view-sources', 'view-geometry']) $(id).addEventListener('keydown', event => { if (['ArrowLeft', 'ArrowRight'].includes(event.key)) { event.preventDefault(); const panel = activePanel === 'sources' ? 'geometry' : 'sources'; switchPanel(panel); $(`view-${panel}`).focus(); } });
$('clear-evidence').addEventListener('click', () => { selectedDirectionId = null; selectedId = null; allEvidence = false; renderEvidence(); $('columns').querySelectorAll('.direction-evidence').forEach(button => button.setAttribute('aria-pressed', 'false')); });
$('columns').addEventListener('scroll', updateColumnControls, { passive: true });
for (const [id, sign] of [['browse-prev', -1], ['browse-next', 1]]) $(id).addEventListener('click', () => $('columns').scrollBy({ left: sign * Math.max(300, $('columns').clientWidth * .75), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' }));
let chartResizeFrame;
window.addEventListener('resize', () => { cancelAnimationFrame(chartResizeFrame); chartResizeFrame = requestAnimationFrame(() => { if (view && activePanel === 'geometry') renderChart(); updateColumnControls(); }); });
$('back').addEventListener('click', () => { if (session) action({ type: 'replay', index: Math.max(0, session.cursor - 1) }); });
$('broaden').addEventListener('click', () => action({ type: 'broaden' }));
$('reset').addEventListener('click', () => {
  $('question').value = ''; $('intent').value = 'explore'; $('lens').value = 'combined'; $('work-relation').value = 'either'; $('transition').value = 'refine';
  markDraft(); $('question').focus(); selectedDirectionId = null; switchPanel('sources');
  if (bridge) action({ type: 'reset', query: '' }, { clearForm: true }); else { draftDirty = false; emptyPath(); }
});
$('export').addEventListener('click', () => { if (activeCapsule?.snapshot.session) download('eigenquestions-session.json', exportSession(activeCapsule.snapshot.session)); });
$('export-view').addEventListener('click', () => { if (activeCapsule) download('eigenquestions-view.json', activeCapsule); });
$('share').addEventListener('click', async () => { try { if (!activeCapsule?.snapshot.session) return; const url = new URL(location.href); url.hash = `focus=${encodeFocus(currentState(session))}`; try { await navigator.clipboard.writeText(url.href); status('Focus link copied. Save or download the full view to preserve groups and context.'); } catch { history.replaceState(null, '', url); status('The address bar contains the focus link. Copy it to share.'); } } catch (error) { status(error.message, true); } });
async function importFile(file) {
  if (!file) return;
  const ticket = ++userIntent; ++routeGeneration; routeAbort?.abort();
  setBusy(true, 'Opening view file…');
  try {
    if (file.size > MAX_JSON_BYTES) throw new Error('View file exceeds the 2 MiB decoded limit.');
    const bytes = new Uint8Array(await file.arrayBuffer());
    if (ticket !== userIntent) return {superseded:true};
    if (bytes[0] === 0x1f && bytes[1] === 0x8b) { const capsule = await decodeCapsuleBytes(bytes); if(ticket!==userIntent)return {superseded:true}; return acceptCapsule(capsule); }
    const payload = JSON.parse(new TextDecoder('utf-8', {fatal:true}).decode(bytes));
    if (payload.kind === CAPSULE_KIND) return acceptCapsule(payload);
    if (payload.view && payload.session) return acceptCapsule(createCapsule(payload));
    if (payload.kind === 'eigenquestions-session') { if (bridge) throw new Error('Disconnect before restoring a separate session.'); return action(payload, {operation:'import'}); }
    throw new Error('This file is not a supported contextual view or navigation session.');
  } catch(error) { if(ticket===userIntent)throw error; return {superseded:true}; }
  finally { if(ticket===userIntent){setBusy(false);if(queuedBridgeSnapshot){const latest=queuedBridgeSnapshot;queuedBridgeSnapshot=null;accept(latest);}} }
}
$('import-open').addEventListener('click', () => $('import-file').click());
$('view-drop').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', async event => { try { await importFile(event.target.files[0]); } catch (error) { status(error.message, true); } finally { event.target.value = ''; } });
window.addEventListener('dragover', event => { if (event.dataTransfer.types.includes('Files')) event.preventDefault(); });
window.addEventListener('drop', async event => { if (!event.dataTransfer.files.length) return; event.preventDefault(); try { await importFile(event.dataTransfer.files[0]); } catch (error) { status(error.message, true); } });
async function publish(capsule = activeCapsule) {
  if (!capsule) throw new Error('There is no view to save.');
  const bytes = await encodeCapsuleBytes(capsule);
  const response = await fetch('/api/views', {method:'POST',headers:{'Content-Type':'application/gzip'},body:bytes,signal:AbortSignal.timeout(30000)});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error?.message || `Saving is unavailable (HTTP ${response.status}). Download the view to keep it.`);
  if (!/^[A-Za-z0-9_-]{22}$/.test(result.id) || !safeUrl(result.url)) throw new Error('Storage returned an invalid saved-view receipt.');
  return result;
}
$('publish-view').addEventListener('click', async () => {
  const savingRevision = uiRevision;
  $('stored-view-status').textContent = 'Saving… Anyone with the link can open this view.'; $('publish-view').disabled = true;
  try {
    const receipt = await publish();
    $('stored-view-url').value = receipt.url; $('stored-view-link').hidden = false;
    const previous = savingRevision !== uiRevision;
    $('stored-view-link').querySelector('label').textContent = previous ? 'Earlier view link' : 'Saved link';
    $('stored-view-status').textContent = previous ? 'Your earlier view was saved; this link belongs to that earlier view. The current view has not been saved. Anyone with the link can open it.' : 'Saved. Anyone with the link can open this view.';
  } catch(error) { $('stored-view-status').textContent = `${error.message} Your current view is unchanged; Download view keeps a local copy.`; }
  finally { $('publish-view').disabled = false; }
});
$('copy-view-link').addEventListener('click', async () => { try { await navigator.clipboard.writeText($('stored-view-url').value); $('stored-view-status').textContent = 'Link copied.'; } catch { $('stored-view-url').focus(); $('stored-view-url').select(); $('stored-view-status').textContent = 'Select and copy the saved link.'; } });
$('agent-open').addEventListener('click', () => $('agent-dialog').showModal()); $('agent-close').addEventListener('click', () => $('agent-dialog').close());
$('bridge-form').addEventListener('submit', async event => { event.preventDefault(); try { await connect($('bridge-origin').value, $('bridge-token').value); } catch (error) { $('bridge-message').textContent = `${error.message} If browser network policy blocks attachment, open the companion’s same-origin local link.`; } });
$('bridge-disconnect').addEventListener('click', async () => { ++userIntent; events?.close(); bridge = null; revision = -1; try { sessionStorage.removeItem(bridgeStorageKey); } catch {} history.replaceState(null, '', location.pathname + location.search); $('connection-status').textContent = 'Browser session'; $('bridge-message').textContent = 'Disconnected. Continuing this session in the browser.'; try { await startBrowser(session ? { session: exportSession(session) } : {}); } catch (error) { status(error.message, true); } });

async function loadRoute({initial = false} = {}) {
  const generation = ++routeGeneration; routeAbort?.abort(); routeAbort = new AbortController();
  ++userIntent; ++sourceEpoch; queuedBridgeSnapshot = null;
  fragment = new URLSearchParams(location.hash.slice(1));
  try {
    if (fragment.has('view')) {
      const id = fragment.get('view'); if (!/^[A-Za-z0-9_-]{22}$/.test(id)) throw new Error('Invalid saved-view identifier.');
      setBusy(true, 'Opening saved view…');
      const response = await fetch(`/api/views/${encodeURIComponent(id)}`, {signal:routeAbort.signal});
      if (!response.ok) { const error = await response.json().catch(() => ({})); throw new Error(error.error?.message || `Saved view could not load (HTTP ${response.status}).`); }
      if (Number(response.headers.get('content-length')) > MAX_JSON_BYTES) throw new Error('Saved view is too large.');
      const reader = response.body.getReader(), chunks=[]; let size=0;
      while (true) { const {done,value}=await reader.read(); if (done) break; size+=value.length; if(size>MAX_JSON_BYTES){await reader.cancel();throw new Error('Saved view is too large.');} chunks.push(value); }
      const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.length;}
      const capsule = await decodeCapsuleBytes(bytes);
      if (generation === routeGeneration) acceptCapsule(capsule, {keepRoute:true});
      return;
    }
    if (fragment.has('focus')) { await startBrowser({state:decodeFocus(fragment.get('focus'))}, {keepRoute:true}); return; }
    let savedBridge; try { savedBridge=JSON.parse(sessionStorage.getItem(bridgeStorageKey)||'null'); } catch {}
    if (fragment.has('token') || (initial && savedBridge)) {
      try { await connect(fragment.get('bridge') || (fragment.has('token') ? location.origin : savedBridge.origin), fragment.get('token') || savedBridge.token); return; }
      catch (error) { try {sessionStorage.removeItem(bridgeStorageKey);}catch{} $('bridge-message').textContent=`${error.message} Open the companion’s local URL for same-origin operation.`; }
    }
    if (initial) {
      const stored = localStorage.getItem(capsuleStorageKey);
      if (stored) { acceptCapsule(JSON.parse(stored)); return; }
      const legacy=localStorage.getItem(storageKey);if(legacy){await startBrowser({session:JSON.parse(legacy)});return;}
    }
    emptyPath();
  } catch (error) { if(generation===routeGeneration && error.name!=='AbortError') {status(`Unable to open this view: ${error.message} Start a new path or open a file to continue.`,true);document.documentElement.dataset.ready='true';} }
  finally { if(generation===routeGeneration) setBusy(false); }
}
window.addEventListener('hashchange', () => loadRoute());
window.eigenquestionsNavigator = Object.freeze({
  version:'1.0.0',
  ready:() => activeCapsule ? Promise.resolve(machineRead()) : new Promise(resolve=>readyWaiters.push(resolve)),
  read:machineRead,
  orient:async (query, options={}) => { if(typeof query!=='string')throw new Error('orient needs a question string.');await ensureWorker();return createCapsule(await callWorker('orient',{...options,query})); },
  evidence:async ids => {if(!Array.isArray(ids)||ids.length>100)throw new Error('Supply at most 100 evidence IDs.');const found=ids.map(id=>activeCapsule?.snapshot.view.nodes.find(node=>node.id===id));if(found.every(Boolean))return structuredClone(found);await ensureWorker();return callWorker('evidence',{ids});},
  apply:(capsule,{expectedRevision}={}) => {assertRevision(expectedRevision);return acceptCapsule(capsule,{expectedRevision});},
  navigate:async (payload,{expectedRevision}={}) => {assertRevision(expectedRevision);const result=await action(payload,{explicitContinuation:true});if(result?.error)throw new Error(result.error);if(!result)throw new Error('Navigation was superseded. Read current state.');return result;},
  export:() => activeCapsule ? structuredClone(activeCapsule) : null,
  publish:async capsule => publish(capsule || activeCapsule),
  subscribe:callback => {if(typeof callback!=='function')throw new Error('subscribe needs a callback.');observers.add(callback);return()=>observers.delete(callback);}
});
loadRoute({initial:true});
