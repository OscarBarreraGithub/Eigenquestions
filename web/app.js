import { currentState, exportSession, validateSession } from '/lib/protocol/session.mjs';
import { placeChartLabel } from '/chart-labels.mjs';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const labels = { explore: 'Explore connections', derive: 'How is it derived?', phenomenology: 'Physical implications', recent: 'Recent within this corpus', using: 'Work using this idea', combined: 'Question + method', physical_question: 'Physical question', method: 'Methods', on: 'work on this idea', either: 'work on or using this idea' };
const colors = ['#a82a2a', '#3f6788', '#786854', '#76617c', '#5a796e'];
let session, view, worker, selectedId, selectedDirectionId, bridge, events, revision = -1, busy = false, allEvidence = false;
let activePanel = 'sources', sourceEpoch = 0, userIntent = 0, draftVersion = 0, draftDirty = false;
let actionQueue = Promise.resolve(), loadingTask = Promise.resolve(), queuedBridgeSnapshot = null, bridgeNeedsRebase = false;
let bridgeRebaseRevision = null;
const columnViews = new Map();
const columnStorageKey = 'eigenquestions:columns:v2';
try { for (const item of JSON.parse(localStorage.getItem(columnStorageKey) || '[]')) if (item?.stateId && Array.isArray(item.directions)) columnViews.set(item.stateId, item); } catch {}
let requestId = 0;
const pending = new Map();
const fragment = new URLSearchParams(location.hash.slice(1));
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
function save() {
  if (!session) return;
  try { localStorage.setItem(storageKey, JSON.stringify(exportSession(session))); } catch {}
  const cached = [...columnViews.values()].slice(-24);
  setTimeout(() => { try { localStorage.setItem(columnStorageKey, JSON.stringify(cached)); } catch {} }, 0);
}
function rememberView(result) {
  columnViews.delete(result.stateId);
  columnViews.set(result.stateId, { stateId: result.stateId, computationId: result.computationId, directions: result.directions.map(({ id, label, query, seedIds, sourceCount, evidenceIds }) => ({ id, label, query, seedIds, sourceCount, evidenceIds })) });
  while (columnViews.size > 24) columnViews.delete(columnViews.keys().next().value);
}
function accept(snapshot, { formVersion } = {}) {
  if (!snapshot?.session || !snapshot?.view) throw new Error('The companion returned an incomplete session.');
  const next = validateSession(snapshot.session);
  if (snapshot.view.corpusId !== next.corpusId || snapshot.view.computationId !== next.computationId || snapshot.view.stateId !== currentState(next).id) throw new Error('The view does not match the current question or computation. Reconnect or import a fresh session.');
  if (!Array.isArray(snapshot.view.nodes) || !Array.isArray(snapshot.view.directions)) throw new Error('The companion returned an invalid view.');
  if (snapshot.revision !== undefined && snapshot.revision <= revision) return false;
  if (snapshot.revision !== undefined) revision = snapshot.revision;
  session = next; view = snapshot.view; selectedId = null; selectedDirectionId = null; allEvidence = false;
  if (formVersion !== undefined && formVersion === draftVersion) draftDirty = false;
  rememberView(view); render(); save();
  if (bridge && Number.isInteger(snapshot.revision)) {
    const renderedState = currentState(next).id, source = sourceEpoch;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (bridge && source === sourceEpoch && document.documentElement.dataset.stateId === renderedState) bridgeFetch('/api/viewer', { method: 'POST', body: JSON.stringify({ viewerId, stateId: renderedState, revision: snapshot.revision }) }).catch(() => {});
    }));
  }
  return true;
}
function action(payload, { followup, operation = 'action', clearForm = false } = {}) {
  const ticket = ++userIntent, source = sourceEpoch, formVersion = draftVersion;
  const baseSession = session ? structuredClone(session) : null, baseRevision = revision;
  const transport = bridge;
  setBusy(true, payload.type === 'reset' ? 'Starting a new path…' : 'Updating directions…');
  status('Computing directions from the current sources…');
  const run = async () => {
    try {
      await loadingTask;
      if (ticket !== userIntent || source !== sourceEpoch) return;
      let result;
      if (transport) {
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
      } else result = await callWorker(operation, operation === 'action' ? { action: payload, baseSession } : payload);
      if (ticket !== userIntent || source !== sourceEpoch) { if (transport && source === sourceEpoch) { bridgeNeedsRebase = true; bridgeRebaseRevision = result.revision; } return; }
      if (followup) result = transport ? await bridgeFetch('/api/action', { method: 'POST', headers: { 'If-Match': `"${result.revision}"` }, body: JSON.stringify(followup) }, transport) : await callWorker('action', { action: followup, baseSession: result.session });
      if (ticket !== userIntent || source !== sourceEpoch) { if (transport && source === sourceEpoch) { bridgeNeedsRebase = true; bridgeRebaseRevision = result.revision; } return; }
      // Agent changes may have arrived while this request's response was delayed.
      if (queuedBridgeSnapshot && queuedBridgeSnapshot.revision > (result.revision ?? -1)) result = queuedBridgeSnapshot;
      queuedBridgeSnapshot = null;
      accept(result, { formVersion: clearForm ? formVersion : undefined });
    } catch (error) {
      if (ticket === userIntent && source === sourceEpoch) {
        if (error.current) { draftDirty = true; bridgeNeedsRebase = false; const latest = queuedBridgeSnapshot?.revision > error.current.revision ? queuedBridgeSnapshot : error.current; queuedBridgeSnapshot = null; accept(latest); }
        status(error.message, true);
      }
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
  const state = currentState(session), scope = view.diagnostics?.scope || {};
  $('current-question').textContent = state.query || 'Start a new path';
  if (!draftDirty) { $('question').value = state.query; $('intent').value = state.intent; $('lens').value = state.lens; $('work-relation').value = state.workRelation; }
  const context = view.diagnostics?.contextTerms || [];
  $('current-context').textContent = state.query ? `${labels[state.intent]} · ${labels[state.lens]}${state.focusIds.length ? ` · Building on ${state.focusIds.length} sources${context.length ? ` about ${context.slice(0, 3).join(', ')}` : ''}` : ' · Across the corpus'}` : 'Enter a concept or question above. This path has no inherited focus.';
  $('back').disabled = session.cursor === 0;
  $('broaden').disabled = !state.focusIds.length && !state.constraints?.excludeIds?.length;
  $('path').replaceChildren();
  session.states.forEach((item, index) => {
    if (index) $('path').append(el('span', 'path-arrow', '›'));
    const button = el('button', '', short(item.query || 'New path', 35)); button.type = 'button'; button.title = `${item.query || 'New path'} · ${labels[item.intent]}`;
    button.setAttribute('aria-label', `Step ${index + 1}: ${item.query || 'New path'}`);
    if (index === session.cursor) button.setAttribute('aria-current', 'step');
    button.addEventListener('click', () => action({ type: 'replay', index })); $('path').append(button);
  });
  $('corpus-scope').textContent = `Eigenquestions v2 · ${(scope.paperCount || 0).toLocaleString()} papers · Swampland-centered collection · ${scope.earliestYear || '?'}–${scope.latestYear || '?'} · Snapshot ${view.diagnostics?.snapshotDate || 'dated in manifest'}. Recent means recent within this collection.`;
  $('evidence-count').textContent = `${view.diagnostics?.distinctPapers ?? new Set(view.nodes.map(n => n.paperId)).size}`;
  updateOptionsSummary(); renderColumns(); renderEvidence();
  if (activePanel === 'geometry') { renderChart(); renderDetails(); }
  status(view.nodes.length ? `${view.directions.length} next directions · ${view.diagnostics?.distinctPapers || new Set(view.nodes.map(n => n.paperId)).size} papers in this view` : state.query ? view.warnings?.[0] || 'No supported sources found. Try another focus.' : 'A new path is ready. Enter your first question.');
  document.documentElement.dataset.ready = 'true';
  document.documentElement.dataset.stateId = state.id;
  document.documentElement.dataset.corpusId = state.corpusId;
}
function renderColumns() {
  const host = $('columns'); host.replaceChildren();
  host.classList.toggle('empty-path', !currentState(session).query && !view.directions.length);
  $('directions-count').textContent = `${view.directions.length} directions`;
  const states = session.states.slice(0, session.cursor + 1);
  for (let index = 0; index < states.length; index++) {
    const state = states[index], current = index === session.cursor, next = states[index + 1];
    const cached = columnViews.get(state.id);
    const directions = current ? view.directions : cached?.computationId === state.computationId ? cached.directions : null;
    const column = el('section', 'miller-column'); column.dataset.stateId = state.id; column.dataset.historyIndex = index; column.dataset.current = String(current);
    const heading = el('div', `column-heading${current ? ' current-column-heading' : ''}`); heading.append(el('span', 'column-step', current ? `Step ${index + 1} · Choose a direction` : `Step ${index + 1}`));
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
        button.addEventListener('click', () => current ? action({ type: 'select', directionId: direction.id }) : action({ type: 'replay', index }, { followup: { type: 'select', directionId: direction.id } }));
        row.append(button);
        if (current) {
          const inspect = el('button', 'direction-evidence', 'Sources'); inspect.type = 'button'; inspect.setAttribute('aria-label', `Inspect sources for direction ${directionIndex + 1}`); inspect.title = 'Inspect sources'; inspect.setAttribute('aria-pressed', String(selectedDirectionId === direction.id));
          inspect.addEventListener('click', () => {
            selectedDirectionId = direction.id; selectedId = null; allEvidence = false; switchPanel('sources'); renderEvidence();
            host.querySelectorAll('.direction-evidence').forEach(item => item.setAttribute('aria-pressed', String(item === inspect)));
            const heading = $('reading-heading'); heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true });
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
  if (!view.nodes.length) { host.append(el('p', 'empty-state', 'No source-supported view for this question yet. Try a physics term used in the corpus, or ask your agent to identify a relevant source.')); return; }
  const compact = host.clientWidth < 560;
  // Use CSS-pixel dimensions on narrow charts; geometry still gets one common
  // x/y scale, while numbered controls remain legible and large enough to tap.
  const width = compact ? Math.max(host.clientWidth, 240) : 760;
  const height = compact ? 300 : 420, margin = compact ? 36 : 54;
  const aggregate = view.chart.fitScope === 'direction-centroids';
  const showSources = !aggregate || $('show-sources').checked;
  $('chart-controls').hidden = !aggregate;
  $('chart-key').textContent = aggregate ? `${view.directions.length} computed directions` : 'Source descriptions';
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
  const byId = new Map(view.nodes.map(n => [n.id, n]));
  for (const edge of (showSources ? view.edges.slice(0, 180) : [])) {
    const a = byId.get(edge.source), b = byId.get(edge.target); if (!a || !b) continue;
    plot.append(svg('line', { x1: x(a.x), y1: y(a.y), x2: x(b.x), y2: y(b.y), stroke: edge.type === 'same_paper' ? '#8da78f' : '#c1cec1', 'stroke-opacity': edge.type === 'same_paper' ? .48 : .28, 'stroke-width': .8, ...(edge.type === 'same_paper' ? {} : { 'stroke-dasharray': '2 4' }) }));
  }
  const seedIds = new Set(view.directions.map(d => d.seedIds[0]));
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
    group.append(svg('title', {}, `${direction.label}\n${direction.sourceCount} source descriptions; ${(100 * direction.massFraction).toFixed(1)}% of retrieval weight.\nWithin-group RMS spread in embedding space: ${readable(direction.withinGroupRms)}. Group proximity is not a physical implication.`));
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
    const follow = () => action({ type: 'select', directionId: direction.id }); group.addEventListener('click', follow); group.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); follow(); } });
    directionMarkerLayer.append(group);
  });
  plot.append(directionMarkerLayer); // Numbers and tap targets always paint last.
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
    details.append(el('p', '', `Distance from this local plane: ${readable(node.residual)}. ${node.inSlab === false ? 'Outside' : 'Within'} the chosen residual cutoff.`)); card.append(details);
    const actions = el('div', 'source-actions'), url = safeUrl(node.sourceUrl || evidence.url);
    if (url) { const link = el('a', '', 'Read paper ↗'); link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer'; actions.append(link); }
    const focus = el('button', '', 'Explore this source'); focus.type = 'button'; focus.addEventListener('click', () => action({ type: 'refine', query: String(evidence.text || node.label).slice(0, 2000), focusIds: [node.id] })); actions.append(focus); card.append(actions); $('evidence').append(card);
  }
  if (!allEvidence && nodes.length > shown.length) { const more = el('button', '', `Show all ${nodes.length} source descriptions`); more.type = 'button'; more.addEventListener('click', () => { allEvidence = true; renderEvidence(); }); $('evidence').append(more); }
}
function renderDetails() {
  const host = $('chart-details'); host.replaceChildren();
  const dl = el('dl');
  for (const [key, value] of [['Construction', view.chart.method], ['Fitted objects', view.chart.fitScope || 'source descriptions'], ['Vector dimensions', view.chart.dimension], ['Metric', view.chart.metric], ['Variation retained', `${((view.chart.explainedVariance || 0) * 100).toFixed(1)}%`], ['Residual cutoff', view.chart.thickness], ['Nearest-group recall', view.chart.neighborRecallAt1 ?? view.chart.neighborRecallAt5], ['Projection stress', view.chart.stress], ['Source variation retained', view.chart.sourceDiagnostics ? `${(view.chart.sourceDiagnostics.explainedVariance * 100).toFixed(1)}%` : 'same as above'], ['Source neighborhood recall', view.chart.sourceDiagnostics?.neighborRecallAt5], ['Global candidates', view.diagnostics?.globalCandidateCount], ['State', view.stateId], ['Corpus', view.corpusId]]) { dl.append(el('dt', '', key), el('dd', '', readable(value))); }
  host.append(dl);
  if (view.chart.fitScope === 'direction-centroids') {
    const groups = el('ul'); view.directions.forEach((direction, index) => groups.append(el('li', '', `Direction ${index + 1}: ${direction.sourceCount} source descriptions, ${(100 * direction.massFraction).toFixed(1)}% of retrieval weight, within-group RMS spread ${readable(direction.withinGroupRms)}, distance from plane ${readable(direction.residual)}.`))); host.append(groups);
  }
  const list = el('ul'); for (const warning of view.warnings || []) list.append(el('li', '', warning)); host.append(list);
}
function download(name, payload) { const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })); const a = el('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
function encodeFocus(state) { return btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(state)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
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
async function startBrowser(initial = {}) {
  const source = ++sourceEpoch, ticket = userIntent;
  actionQueue = Promise.resolve();
  revision = -1; queuedBridgeSnapshot = null; bridgeNeedsRebase = false;
  setBusy(true, 'Preparing the corpus…'); worker?.terminate();
  for (const request of pending.values()) request.reject(new Error('Computation source changed.'));
  pending.clear();
  worker = new Worker('/compute-worker.js', { type: 'module' });
  worker.onmessage = ({ data }) => {
    if (data.type === 'progress') { if (source === sourceEpoch) status(data.stage === 'index' ? 'Preparing the source index on your device…' : `Loading corpus: ${data.completed}/${data.total} files. The first visit downloads the collection; later questions use local data.`); return; }
    const request = pending.get(data.id); if (!request) return; pending.delete(data.id); data.error ? request.reject(new Error(data.error)) : request.resolve(data.result);
  };
  worker.onerror = event => { for (const request of pending.values()) request.reject(new Error(event.message || 'The computation worker failed to load. Reload to retry.')); pending.clear(); };
  loadingTask = callWorker('init', initial);
  try { const result = await loadingTask; if (source === sourceEpoch && ticket === userIntent) accept(result); }
  finally { if (source === sourceEpoch && ticket === userIntent) setBusy(false); }
}
function updateOptionsSummary() {
  const defaults = { intent: 'explore', lens: 'combined', 'work-relation': 'either', transition: 'refine' };
  const changed = Object.entries(defaults).filter(([id, value]) => $(id).value !== value).length;
  const approach = $('intent').selectedOptions[0]?.textContent || 'Explore connections';
  $('options-summary').textContent = `${approach} · ${changed ? `${changed} changed` : '4 settings'}`;
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
  action({ type: 'reset', query: '' }, { clearForm: true });
});
$('export').addEventListener('click', () => { if (session) download('eigenquestions-session.json', exportSession(session)); });
$('export-view').addEventListener('click', () => { if (session) download('eigenquestions-view.json', { session, view, revision: Math.max(0, revision) }); });
$('share').addEventListener('click', async () => { if (!session) return; const url = new URL(location.href); url.hash = `focus=${encodeFocus(currentState(session))}`; try { await navigator.clipboard.writeText(url.href); status('Current focus link copied. It preserves this question, source anchors, and approach; export a session for the full path.'); } catch { history.replaceState(null, '', url); status('The address bar now contains your shareable focus link. Copy it to share.'); } });
$('import-open').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 8 * 1024 * 1024) throw new Error('Session file is too large (maximum 8 MiB).');
    if (bridge) throw new Error('Disconnect from the local companion before importing a separate browser session.');
    const payload = JSON.parse(await file.text()); draftDirty = false; await action(payload, { operation: 'import', clearForm: true });
  } catch (error) { status(error.message, true); } finally { event.target.value = ''; }
});
$('agent-open').addEventListener('click', () => $('agent-dialog').showModal()); $('agent-close').addEventListener('click', () => $('agent-dialog').close());
$('bridge-form').addEventListener('submit', async event => { event.preventDefault(); try { await connect($('bridge-origin').value, $('bridge-token').value); } catch (error) { $('bridge-message').textContent = `${error.message} If browser network policy blocks attachment, open the companion’s same-origin local link.`; } });
$('bridge-disconnect').addEventListener('click', async () => { ++userIntent; events?.close(); bridge = null; revision = -1; try { sessionStorage.removeItem(bridgeStorageKey); } catch {} history.replaceState(null, '', location.pathname + location.search); $('connection-status').textContent = 'Browser session'; $('bridge-message').textContent = 'Disconnected. Continuing this session in the browser.'; try { await startBrowser(session ? { session: exportSession(session) } : {}); } catch (error) { status(error.message, true); } });

async function boot() {
  let savedBridge;
  try { savedBridge = JSON.parse(sessionStorage.getItem(bridgeStorageKey) || 'null'); } catch {}
  if (fragment.has('token') || (savedBridge && !fragment.has('focus'))) {
    try { await connect(fragment.get('bridge') || (fragment.has('token') ? location.origin : savedBridge.origin), fragment.get('token') || savedBridge.token); setBusy(false); return; }
    catch (error) { try { sessionStorage.removeItem(bridgeStorageKey); } catch {} $('bridge-message').textContent = `${error.message} Open the companion’s local URL for same-origin operation.`; status('Could not attach to the companion. Loading a browser session instead.', true); }
  }
  let initial = {};
  if (fragment.has('focus')) initial.state = decodeFocus(fragment.get('focus'));
  else { try { const saved = localStorage.getItem(storageKey); if (saved) initial.session = JSON.parse(saved); } catch { /* No usable saved session. */ } }
  try { await startBrowser(initial); }
  catch (error) {
    if (initial.session) { status(`Saved session could not be restored (${error.message}). Starting a fresh session…`); await startBrowser(); }
    else throw error;
  }
}
boot().catch(error => { setBusy(false); status(`Unable to load the explorer: ${error.message} Reload to retry.`, true); $('directions')?.replaceChildren(el('p', 'empty-state', 'The corpus could not load. Check your connection and reload. Your exported sessions remain portable.')); });
