import { currentState, exportSession, validateSession } from '/lib/protocol/session.mjs';
import { placeChartLabel } from '/chart-labels.mjs';

const $ = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const labels = { explore: 'Explore connections', derive: 'How is it derived?', phenomenology: 'Physical implications', recent: 'Recent within this corpus', using: 'Work using this idea', combined: 'Question + method', physical_question: 'Physical question', method: 'Methods', on: 'work on this idea', either: 'work on or using this idea' };
const colors = ['#3f7866', '#5b7d9d', '#a48a50', '#96758c', '#7a8e53'];
let session, view, worker, selectedId, bridge, events, revision = -1, busy = false, allEvidence = false;
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
function setBusy(value) { busy = value; document.body.classList.toggle('busy', value); $('explore-button').disabled = value; $('chart').setAttribute('aria-busy', String(value)); }
function callWorker(type, payload) { return new Promise((resolve, reject) => { const id = ++requestId; pending.set(id, { resolve, reject }); worker.postMessage({ id, type, payload }); }); }
function save() { if (!session) return; try { localStorage.setItem(storageKey, JSON.stringify(exportSession(session))); } catch { /* Storage may be disabled; exports still work. */ } }
function accept(snapshot) {
  if (!snapshot?.session || !snapshot?.view) throw new Error('The companion returned an incomplete session.');
  const next = validateSession(snapshot.session);
  if (snapshot.view.corpusId !== next.corpusId || snapshot.view.computationId !== next.computationId || snapshot.view.stateId !== currentState(next).id) throw new Error('The view does not match the current question or computation. Reconnect or import a fresh session.');
  if (!Array.isArray(snapshot.view.nodes) || !Array.isArray(snapshot.view.directions)) throw new Error('The companion returned an invalid view.');
  if (snapshot.revision !== undefined && snapshot.revision < revision) return;
  if (snapshot.revision !== undefined) revision = snapshot.revision;
  session = next; view = snapshot.view; selectedId = null; allEvidence = false;
  render(); save();
  if (bridge && Number.isInteger(snapshot.revision)) {
    const renderedState = currentState(next).id;
    // Acknowledgement follows a paint opportunity, not merely an open SSE socket.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (bridge && document.documentElement.dataset.stateId === renderedState) bridgeFetch('/api/viewer', { method: 'POST', body: JSON.stringify({ viewerId, stateId: renderedState, revision: snapshot.revision }) }).catch(() => {});
    }));
  }
}
async function action(payload) {
  if (busy || !session) return;
  setBusy(true); status('Drawing a new view around your question…');
  try {
    const result = bridge ? await bridgeFetch('/api/action', { method: 'POST', body: JSON.stringify(payload) }) : await callWorker('action', payload);
    accept(result);
  } catch (error) { status(error.message, true); }
  finally { setBusy(false); }
}
function render() {
  const state = currentState(session), scope = view.diagnostics?.scope || {};
  $('current-question').textContent = state.query || 'Choose a physics question';
  $('question').value = state.query;
  $('intent').value = state.intent; $('lens').value = state.lens; $('work-relation').value = state.workRelation;
  const context = view.diagnostics?.contextTerms || [];
  $('current-context').textContent = `${labels[state.intent]} · ${labels[state.lens]}${state.focusIds.length ? ` · Building on ${state.focusIds.length} source descriptions${context.length ? ` about ${context.slice(0, 4).join(', ')}` : ''}` : ' · Searching across the corpus'}`;
  $('back').disabled = session.cursor === 0; $('broaden').disabled = !state.focusIds.length && !state.constraints?.excludeIds?.length;
  $('path').replaceChildren();
  session.states.forEach((item, index) => {
    if (index) $('path').append(el('span', 'path-arrow', '›'));
    const button = el('button', '', short(item.query || 'Starting point', 44)); button.type = 'button'; button.title = `${item.query} · ${labels[item.intent]}`;
    if (index === session.cursor) button.setAttribute('aria-current', 'step');
    button.addEventListener('click', () => action({ type: 'replay', index })); $('path').append(button);
  });
  $('corpus-scope').textContent = `${(scope.paperCount || 0).toLocaleString()} papers · ${(scope.unitCount || 0).toLocaleString()} source descriptions · ${scope.earliestYear || '?'}–${scope.latestYear || '?'} · Snapshot ${view.diagnostics?.snapshotDate || 'dated in manifest'}. Recent means recent within this frozen Swampland-centered collection.`;
  $('evidence-count').textContent = `${view.diagnostics?.distinctPapers ?? new Set(view.nodes.map(n => n.paperId)).size} papers`;
  renderChart(); renderDirections(); renderEvidence(); renderDetails();
  status(view.nodes.length ? `${view.nodes.length} source descriptions, ${view.directions.length} suggested directions. Your question changes both the selection and the view.` : view.warnings?.[0] || 'No supported sources found. Try a more specific term or pivot to a different focus.');
  document.documentElement.dataset.ready = 'true';
  document.documentElement.dataset.stateId = state.id;
  document.documentElement.dataset.corpusId = state.corpusId;
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
    const select = () => { selectedId = node.id; renderChart(); renderEvidence(); };
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
function renderDirections() {
  $('directions').replaceChildren(); $('directions-count').textContent = `${view.directions.length} directions`;
  view.directions.forEach((direction, index) => {
    const button = el('button', 'direction'); button.type = 'button'; button.dataset.directionId = direction.id;
    button.append(el('span', 'direction-number', String(index + 1).padStart(2, '0')));
    const body = el('span'); body.append(el('h3', '', direction.label), el('p', '', direction.summary));
    body.append(el('span', 'direction-meta', `${direction.evidenceIds.length} supporting source description${direction.evidenceIds.length === 1 ? '' : 's'} · suggested connection`));
    button.append(body, el('span', 'direction-arrow', '↗'));
    button.addEventListener('click', () => action({ type: 'select', directionId: direction.id })); $('directions').append(button);
  });
  if (!view.directions.length) $('directions').append(el('p', 'empty-state', 'No supported directions in this context. Pivot to another question, broaden the current view, or ask your agent to find a source anchor.'));
}
function renderEvidence() {
  $('evidence').replaceChildren();
  let nodes = [...view.nodes];
  if (selectedId) nodes.sort((a, b) => Number(b.id === selectedId) - Number(a.id === selectedId));
  const shown = allEvidence ? nodes : nodes.slice(0, 7);
  for (const node of shown) {
    const evidence = node.evidence || {}, card = el('article', `evidence-card${node.id === selectedId ? ' selected' : ''}`);
    card.dataset.sourceId = node.id;
    const relation = node.retrieval?.workRelation?.kind;
    card.append(el('p', 'source-meta', `${evidence.date || evidence.year || node.year || 'date unavailable'} · ${labels[evidence.lens || node.lens] || 'Source'}${relation ? ` · ${relation === 'ambiguous' ? 'role uncertain' : relation}` : ''}`));
    card.append(el('h3', '', node.title));
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
async function bridgeFetch(route, options = {}) {
  const response = await fetch(new URL(route, bridge.origin), { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${bridge.token}` }, signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`Companion returned HTTP ${response.status}. Check the origin and session token.`);
  return response.json();
}
async function connect(origin, token) {
  const url = new URL(origin);
  if (!['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) || !['http:', 'https:'].includes(url.protocol)) throw new Error('The companion must use a loopback origin on your computer.');
  if (!token) throw new Error('A session token is required. Use the companion launch link.');
  bridge = { origin: url.origin, token }; revision = -1;
  try {
    accept(await bridgeFetch('/api/session'));
    events?.close();
    const eventUrl = new URL('/api/events', bridge.origin); eventUrl.searchParams.set('token', token);
    events = new EventSource(eventUrl);
    events.onmessage = ({ data }) => { try { accept(JSON.parse(data)); $('connection-status').textContent = 'Agent connected · live updates'; } catch (error) { status(error.message, true); } };
    events.onopen = () => { $('connection-status').textContent = 'Agent connected · live updates'; };
    events.onerror = () => { $('connection-status').textContent = 'Companion reconnecting…'; status('The companion connection interrupted. Updates will resume when it reconnects.', true); };
    $('connection-status').textContent = 'Agent connected · live updates'; $('bridge-message').textContent = 'Connected. Agent actions update this view automatically.';
    // Tab-scoped storage preserves attachment across reload; never export this token.
    let savedToken = false;
    try { sessionStorage.setItem(bridgeStorageKey, JSON.stringify(bridge)); savedToken = true; } catch { /* Keep launch fragment if storage is unavailable. */ }
    if (fragment.has('token') && savedToken) history.replaceState(null, '', location.pathname + location.search);
  } catch (error) { bridge = null; events?.close(); throw error; }
}
async function startBrowser(initial = {}) {
  setBusy(true); worker?.terminate(); worker = new Worker('/compute-worker.js', { type: 'module' });
  worker.onmessage = ({ data }) => {
    if (data.type === 'progress') { status(data.stage === 'index' ? 'Preparing the source index on your device…' : `Loading corpus: ${data.completed}/${data.total} files. The first visit downloads the frozen corpus; subsequent views use local data.`); return; }
    const request = pending.get(data.id); if (!request) return; pending.delete(data.id); data.error ? request.reject(new Error(data.error)) : request.resolve(data.result);
  };
  worker.onerror = event => { for (const request of pending.values()) request.reject(new Error(event.message || 'The computation worker failed to load. Reload the page to retry.')); pending.clear(); };
  try { accept(await callWorker('init', initial)); }
  finally { setBusy(false); }
}
$('question-form').addEventListener('submit', event => { event.preventDefault(); const query = $('question').value.trim(); if (!query) { status('Enter a physics question or concept.', true); return; } action({ type: $('transition').value, query, intent: $('intent').value, lens: $('lens').value, workRelation: $('work-relation').value }); });
$('intent').addEventListener('change', () => { if ($('intent').value === 'using') $('work-relation').value = 'using'; });
$('show-sources').addEventListener('change', () => { if (view) renderChart(); });
let chartResizeFrame;
window.addEventListener('resize', () => { cancelAnimationFrame(chartResizeFrame); chartResizeFrame = requestAnimationFrame(() => { if (view) renderChart(); }); });
$('back').addEventListener('click', () => action({ type: 'back' }));
$('broaden').addEventListener('click', () => action({ type: 'broaden' }));
$('reset').addEventListener('click', () => action({ type: 'reset', query: 'Kaluza-Klein towers' }));
$('export').addEventListener('click', () => { if (session) download('eigenquestions-session.json', exportSession(session)); });
$('export-view').addEventListener('click', () => { if (session) download('eigenquestions-view.json', { session, view, revision: Math.max(0, revision) }); });
$('share').addEventListener('click', async () => { if (!session) return; const url = new URL(location.href); url.hash = `focus=${encodeFocus(currentState(session))}`; try { await navigator.clipboard.writeText(url.href); status('Current focus link copied. It preserves this question, source anchors, and approach; export a session for the full path.'); } catch { history.replaceState(null, '', url); status('The address bar now contains your shareable focus link. Copy it to share.'); } });
$('import-open').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 8 * 1024 * 1024) throw new Error('Session file is too large (maximum 8 MiB).');
    if (bridge) throw new Error('Disconnect from the local companion before importing a separate browser session.');
    const payload = JSON.parse(await file.text()); setBusy(true); accept(await callWorker('import', payload)); status('Session imported. This view was recomputed from the frozen corpus.');
  } catch (error) { status(error.message, true); } finally { setBusy(false); event.target.value = ''; }
});
$('agent-open').addEventListener('click', () => $('agent-dialog').showModal()); $('agent-close').addEventListener('click', () => $('agent-dialog').close());
$('bridge-form').addEventListener('submit', async event => { event.preventDefault(); try { await connect($('bridge-origin').value, $('bridge-token').value); } catch (error) { $('bridge-message').textContent = `${error.message} If browser network policy blocks attachment, open the companion’s same-origin local link.`; } });
$('bridge-disconnect').addEventListener('click', async () => { events?.close(); bridge = null; revision = -1; try { sessionStorage.removeItem(bridgeStorageKey); } catch {} history.replaceState(null, '', location.pathname + location.search); $('connection-status').textContent = 'Browser session'; $('bridge-message').textContent = 'Disconnected. Continuing this session in the browser.'; try { await startBrowser(session ? { session: exportSession(session) } : {}); } catch (error) { status(error.message, true); } });

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
boot().catch(error => { setBusy(false); status(`Unable to load the explorer: ${error.message} Reload to retry.`, true); $('chart').replaceChildren(el('p', 'empty-state', 'The corpus or computation could not load. Check your connection and reload the page. Your exported sessions remain portable.')); });
