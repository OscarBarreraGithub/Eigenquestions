// Fixed overview only. No explorer controller, numerical engine, or storage.
export const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
export function screenPoint(point, camera, width, height) {
  return {x: (point[0] - camera.x) * camera.k + width / 2, y: height / 2 - (point[1] - camera.y) * camera.k};
}
export function worldPoint(point, camera, width, height) {
  return {x: (point.x - width / 2) / camera.k + camera.x, y: (height / 2 - point.y) / camera.k + camera.y};
}
export function zoomCamera(camera, pointer, factor, width, height, min, max) {
  const anchor = worldPoint(pointer, camera, width, height), k = clamp(camera.k * factor, min, max);
  return {x: anchor.x - (pointer.x - width / 2) / k, y: anchor.y + (pointer.y - height / 2) / k, k};
}
export function boundsOf(points) {
  const bounds = {minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity};
  for (const point of points) {
    bounds.minX = Math.min(bounds.minX, point[2]); bounds.maxX = Math.max(bounds.maxX, point[2]);
    bounds.minY = Math.min(bounds.minY, point[3]); bounds.maxY = Math.max(bounds.maxY, point[3]);
  }
  return bounds;
}
export function fitCamera(bounds, width, height, padding = 35) {
  return {x: (bounds.minX + bounds.maxX) / 2, y: (bounds.minY + bounds.maxY) / 2,
    k: Math.max(.001, Math.min(Math.max(1, width - padding * 2) / Math.max(.001, bounds.maxX - bounds.minX),
      Math.max(1, height - padding * 2) / Math.max(.001, bounds.maxY - bounds.minY)))};
}
export function makeSpatialIndex(points, bounds, cells = 96) {
  const grid = new Map(), dx = Math.max(.001, bounds.maxX - bounds.minX), dy = Math.max(.001, bounds.maxY - bounds.minY);
  const cell = (x, y) => [clamp(Math.floor((x - bounds.minX) / dx * cells), 0, cells - 1), clamp(Math.floor((y - bounds.minY) / dy * cells), 0, cells - 1)];
  points.forEach((point, index) => { const [x, y] = cell(point[2], point[3]), key = y * cells + x; if (!grid.has(key)) grid.set(key, []); grid.get(key).push(index); });
  return {nearest(x, y, radius) {
    const [x0, y0] = cell(x - radius, y - radius), [x1, y1] = cell(x + radius, y + radius);
    let best = -1, distance = radius * radius;
    for (let cy = y0; cy <= y1; cy++) for (let cx = x0; cx <= x1; cx++) for (const index of grid.get(cy * cells + cx) || []) {
      const p = points[index], d = (p[2] - x) ** 2 + (p[3] - y) ** 2;
      if (d < distance || (d === distance && (best < 0 || index < best))) { best = index; distance = d; }
    }
    return best;
  }};
}
export function topicClosure(topics, index) {
  const result = new Set(), queue = [index];
  while (queue.length) { const next = queue.pop(); if (!result.has(next)) { result.add(next); queue.push(...topics[next].children); } }
  return result;
}
export function validateOverview(manifest, map) {
  const require = (condition, message) => { if (!condition) throw new Error(`Invalid overview: ${message}`); };
  require(manifest.kind === 'eigenquestions-fixed-overview' && manifest.schemaVersion === '1.0.0', 'unsupported manifest');
  require(map.schemaVersion === '1.0.0' && map.viewId === manifest.viewId, 'view identity mismatch');
  require(Array.isArray(map.points) && map.points.length > 0 && map.points.length <= 30000, 'point count');
  require(Array.isArray(map.papers) && map.papers.length <= 30000 && Array.isArray(map.topics) && map.topics.length <= 500, 'catalog bounds');
  const topicIndex = n => Number.isInteger(n) && n >= 0 && n < map.topics.length;
  require(topicIndex(manifest.rootTopicIndex), 'root');
  const ids = new Set();
  for (const p of map.points) {
    require(Array.isArray(p) && p.length === 6 && typeof p[0] === 'string' && !ids.has(p[0]), 'point identity'); ids.add(p[0]);
    require(Number.isInteger(p[1]) && p[1] >= 0 && p[1] < map.papers.length && p.slice(2, 5).every(Number.isFinite) && p[4] > 0, 'point coordinates or paper');
    require(Array.isArray(p[5]) && p[5].length > 0 && p[5].every(topicIndex) && new Set(p[5]).size === p[5].length, 'memberships');
  }
  require(map.papers.every(p => Array.isArray(p) && p.length === 3 && p.every(x => typeof x === 'string')), 'paper metadata');
  map.topics.forEach((topic, index) => {
    require(typeof topic.id === 'string' && typeof topic.label === 'string' && typeof topic.caption === 'string' && Number.isFinite(topic.x) && Number.isFinite(topic.y), 'topic metadata');
    require(topic.parent === null || topicIndex(topic.parent), 'topic parent');
    require(Array.isArray(topic.children) && topic.children.every(topicIndex) && !topic.children.includes(index), 'topic children');
    require(Array.isArray(topic.representatives) && topic.representatives.every(n => Number.isInteger(n) && n >= 0 && n < map.points.length), 'topic representatives');
    const seen = new Set([index]); let parent = topic.parent;
    while (parent !== null) { require(!seen.has(parent), 'cyclic hierarchy'); seen.add(parent); parent = map.topics[parent].parent; }
  });
  require(Array.isArray(map.links) && map.links.length <= 5000 && map.links.every(link => topicIndex(link.source) && topicIndex(link.target) && Number.isFinite(link.weight) && link.weight >= 0 && link.kind === 'text_similarity'), 'topic links');
  let start = 0;
  require(Array.isArray(manifest.files?.details), 'detail manifest');
  for (const shard of manifest.files.details) { require(shard.start === start && Number.isInteger(shard.count) && shard.count > 0 && shard.count <= 512, 'detail alignment'); start += shard.count; }
  require(start === map.points.length, 'detail coverage');
  return map;
}

if (typeof document !== 'undefined') startOverview();

async function startOverview() {
  const $ = id => document.getElementById(id), stage = $('overview-stage'), canvas = $('overview-canvas'), ctx = canvas.getContext('2d');
  const status = $('overview-status'), details = $('overview-details'), tooltip = $('overview-tooltip');
  const colors = ['#72b8fa', '#ce9fec', '#edbc6d', '#7cd6be', '#b0bac9'];
  const state = {ready: false, camera: {x: 0, y: 0, k: 1}, width: 1, height: 1, fitScale: 1, selectedTopic: null, selectedPoint: null, hover: -1,
    labels: [], drawn: 0, frame: 0, selectedMembers: null, detailGeneration: 0,
    browseTopic: null, browseSources: false, sourceFilter: '', sourceLimit: 6};
  let manifest, map, bounds, spatial, broad = [], colorOf = [], paperPoints = [], framePending = false, resizeObserver;
  const shardPromises = new Map(), pointers = new Map(); let moved = false, dragStart, searchTimer;
  const text = (tag, value, className) => { const node = document.createElement(tag); node.textContent = value; if (className) node.className = className; return node; };
  const message = value => { status.textContent = value; };
  const caption = index => index === manifest.membershipRule.unresolvedTopicIndex ? 'Unassigned excerpts' : map.topics[index].caption || map.topics[index].label;
  const excerpt = (value, limit = 64) => value.length > limit ? `${value.slice(0, limit - 1).trimEnd()}…` : value;
  const selectedPoint = () => state.selectedPoint === null ? null : map.points[state.selectedPoint];
  const pointScreen = point => screenPoint([point[2], point[3]], state.camera, state.width, state.height);
  const schedule = () => { if (!framePending) { framePending = true; requestAnimationFrame(draw); } };
  function setCamera(camera) {
    const dx = bounds.maxX - bounds.minX, dy = bounds.maxY - bounds.minY;
    state.camera = {x: clamp(camera.x, bounds.minX - dx, bounds.maxX + dx), y: clamp(camera.y, bounds.minY - dy, bounds.maxY + dy), k: clamp(camera.k, state.fitScale * .75, state.fitScale * 100)};
    schedule();
  }
  function zoom(factor, pointer = {x: state.width / 2, y: state.height / 2}) {
    if (state.ready) setCamera(zoomCamera(state.camera, pointer, factor, state.width, state.height, state.fitScale * .75, state.fitScale * 100));
  }
  function fit() { if (!state.ready) return; clearSelection(); setCamera(fitCamera(bounds, state.width, state.height)); message('Showing the full fixed map.'); }
  function resize() {
    const previousFit = state.fitScale;
    state.width = Math.max(1, stage.clientWidth); state.height = Math.max(1, stage.clientHeight);
    const ratio = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(state.width * ratio); canvas.height = Math.round(state.height * ratio);
    canvas.style.width = `${state.width}px`; canvas.style.height = `${state.height}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    if (bounds) {
      const fitted = fitCamera(bounds, state.width, state.height); state.fitScale = fitted.k;
      state.camera = state.ready ? {...state.camera, k: state.camera.k / previousFit * fitted.k} : fitted;
    }
    schedule();
  }
  async function fetchJson(descriptor, maxBytes) {
    if (!descriptor || !/^[a-z0-9-]+\.json$/.test(descriptor.path) || !/^[a-f0-9]{64}$/.test(descriptor.sha256) || !Number.isInteger(descriptor.bytes) || descriptor.bytes > maxBytes) throw new Error('Invalid overview file descriptor.');
    const response = await fetch(`/data/overview/${descriptor.path}`);
    if (!response.ok) throw new Error(`Overview data could not be loaded (${response.status}).`);
    const bytes = await response.arrayBuffer();
    if (bytes.byteLength !== descriptor.bytes) throw new Error('Overview file size does not match its manifest.');
    const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(x => x.toString(16).padStart(2, '0')).join('');
    if (digest !== descriptor.sha256) throw new Error('Overview file does not match its pinned data. Reload to try again.');
    return JSON.parse(new TextDecoder().decode(bytes));
  }
  async function questionText(index) {
    const descriptor = manifest.files.details.find(shard => index >= shard.start && index < shard.start + shard.count);
    if (!shardPromises.has(descriptor.path)) {
      shardPromises.set(descriptor.path, fetchJson(descriptor, 256 * 1024).then(data => {
        if (data.schemaVersion !== '1.0.0' || data.start !== descriptor.start || !Array.isArray(data.texts) || data.texts.length !== descriptor.count || !data.texts.every(value => typeof value === 'string')) throw new Error('Overview source descriptions are not aligned.');
        return data.texts;
      }).catch(error => { shardPromises.delete(descriptor.path); throw error; }));
    }
    return (await shardPromises.get(descriptor.path))[index - descriptor.start];
  }
  function detailHeading(value) {
    details.replaceChildren(text('h2', value)); details.firstChild.id = 'overview-selected-heading';
    details.dataset.pointId = ''; details.dataset.topicId = ''; delete details.dataset.detailReady;
  }
  function revealSourceDetails(generation) {
    requestAnimationFrame(() => {
      if (generation !== state.detailGeneration) return;
      const sidebar = details.closest('.overview-sidebar');
      if (window.matchMedia('(min-width: 761px)').matches && sidebar) sidebar.scrollTop += details.getBoundingClientRect().top - sidebar.getBoundingClientRect().top - 8;
      else details.scrollIntoView({block: 'start', behavior: 'instant'});
      details.focus({preventScroll: true});
    });
  }
  function topicButton(index, className = 'topic-button') {
    const button = text('button', '', className); button.type = 'button'; button.dataset.topicIndex = index;
    button.append(text('span', caption(index)), text('span', `${map.topics[index].paperCount.toLocaleString()} papers · ${map.topics[index].unitCount.toLocaleString()} excerpts`, 'topic-meta'));
    const color = broad.findIndex(parent => topicClosure(map.topics, parent).has(index)); if (color >= 0) button.style.setProperty('--topic-color', colors[color % colors.length]);
    button.setAttribute('aria-pressed', String(state.selectedTopic === index)); button.addEventListener('click', () => selectTopic(index));
    return button;
  }
  function updateTopicButtons() { for (const button of document.querySelectorAll('button[data-topic-index]')) button.setAttribute('aria-pressed', String(Number(button.dataset.topicIndex) === state.selectedTopic)); }
  function sourceButton(index) {
    const point = map.points[index], paper = map.papers[point[1]], button = text('button', '', 'result-button');
    const count = paperPoints[point[1]].length, ordinal = paperPoints[point[1]].indexOf(index) + 1;
    button.type = 'button'; button.dataset.pointIndex = index; button.append(text('span', paper[1]), text('span', `Question excerpt${count > 1 ? ` ${ordinal} of ${count}` : ''} · ${paper[0]}`, 'detail-meta'));
    button.setAttribute('aria-pressed', String(state.selectedPoint === index));
    button.addEventListener('click', () => selectPoint(index)); return button;
  }
  function membersOf(index) {
    const closure = topicClosure(map.topics, index), members = new Set();
    map.points.forEach((point, pointIndex) => { if (point[5].some(home => closure.has(home))) members.add(pointIndex); });
    return members;
  }
  function browseAncestors(index) {
    const ancestors = [];
    for (let current = index; current !== null && current !== manifest.rootTopicIndex; current = map.topics[current].parent) ancestors.unshift(current);
    return ancestors;
  }
  function revealTopicNavigation() {
    const generation = state.detailGeneration;
    requestAnimationFrame(() => {
      if (generation !== state.detailGeneration) return;
      const section = $('overview-topics').closest('.topic-section'), sidebar = section?.closest('.overview-sidebar');
      if (sidebar) sidebar.scrollTop = 0;
      if (section && window.matchMedia('(max-width: 760px)').matches) section.scrollIntoView({block: 'start', behavior: 'instant'});
      $('overview-topics').focus({preventScroll: true});
    });
  }
  function renderSourceChoices() {
    const host = $('overview-topics'), index = state.browseTopic, topic = map.topics[index], members = membersOf(index);
    const ordered = [...new Set([...topic.representatives.filter(point => members.has(point)), ...members])];
    const filter = state.sourceFilter.trim().toLowerCase();
    const matches = ordered.filter(point => { const paper = map.papers[map.points[point][1]]; return `${paper[0]} ${paper[1]}`.toLowerCase().includes(filter); });
    host.replaceChildren();
    for (const point of matches.slice(0, state.sourceLimit)) { const row = document.createElement('li'); row.append(sourceButton(point)); host.append(row); }
    if (!matches.length) { const row = document.createElement('li'); row.append(text('p', 'No source titles or arXiv IDs match this filter.')); host.append(row); }
    if (matches.length > state.sourceLimit) {
      const row = document.createElement('li'), more = text('button', `Show more sources (${state.sourceLimit} of ${matches.length})`, 'result-button');
      more.type = 'button'; more.dataset.loadMore = 'true'; more.addEventListener('click', () => { state.sourceLimit += 6; renderSourceChoices(); }); row.append(more); host.append(row);
    }
    host.dataset.sourceCount = String(matches.length);
  }
  function renderTopicNavigation() {
    const index = state.browseTopic, topic = index === null ? null : map.topics[index], root = topic === null;
    const showSources = !root && (state.browseSources || !topic.children.length);
    const path = $('overview-topic-path'), back = $('overview-topics-back'), host = $('overview-topics'), context = $('overview-topic-context');
    path.replaceChildren(); path.hidden = root;
    if (!root) {
      const full = text('button', 'Full map'); full.type = 'button'; full.dataset.browseRoot = 'true'; full.addEventListener('click', () => { fit(); revealTopicNavigation(); }); path.append(full);
      for (const ancestor of browseAncestors(index)) {
        path.append(text('span', '›'));
        if (ancestor === index && !state.browseSources) { const current = text('span', caption(ancestor)); current.setAttribute('aria-current', 'page'); path.append(current); }
        else { const button = text('button', caption(ancestor)); button.type = 'button'; button.dataset.browseTopic = ancestor; button.addEventListener('click', () => selectTopic(ancestor)); path.append(button); }
      }
      if (state.browseSources) { path.append(text('span', '›')); const current = text('span', 'Source questions'); current.setAttribute('aria-current', 'page'); path.append(current); }
    }
    back.hidden = root;
    back.textContent = !root && state.browseSources && topic.children.length ? 'Back to groups' : !root && topic.parent !== manifest.rootTopicIndex ? 'Parent group' : 'All groups';
    $('overview-topics-heading').textContent = root ? 'Broad groups' : showSources ? 'Source questions' : 'Finer groups';
    context.textContent = root ? 'Choose a topic to see its next choices.' : showSources
      ? `${index === manifest.membershipRule.unresolvedTopicIndex ? 'These excerpts have no current topic assignment.' : topic.children.length ? 'Source questions from this group and its finer groups.' : 'No finer groups in this map yet.'} Browse ${topic.unitCount.toLocaleString()} source excerpts, or filter their paper titles and IDs.`
      : `Choose one of the ${topic.children.length} finer groups in ${caption(index)}.`;
    $('overview-source-filter-field').hidden = !showSources;
    $('overview-source-filter').value = state.sourceFilter;
    $('overview-browse-sources').hidden = root || showSources;
    if (!root) $('overview-browse-sources').textContent = `Browse all ${topic.unitCount.toLocaleString()} source excerpts`;
    if (showSources) renderSourceChoices();
    else {
      delete host.dataset.sourceCount;
      const topics = (root ? broad : topic.children).filter(child => child !== manifest.membershipRule.unresolvedTopicIndex);
      host.replaceChildren(...topics.map(child => { const li = document.createElement('li'); li.append(topicButton(child)); return li; }));
    }
    const unassigned = $('overview-unassigned'); unassigned.replaceChildren(); unassigned.hidden = !root;
    if (root) {
      const unresolved = manifest.membershipRule.unresolvedTopicIndex, button = text('button', `Unassigned excerpts (${map.topics[unresolved].unitCount})`, 'unassigned-button');
      button.type = 'button'; button.dataset.topicIndex = unresolved; button.addEventListener('click', () => selectTopic(unresolved)); unassigned.append(button);
    }
    host.dataset.browseTopic = index === null ? '' : String(index); host.dataset.browseMode = root ? 'root' : showSources ? 'sources' : 'children';
  }
  function selectTopic(index) {
    if (index === manifest.rootTopicIndex) { fit(); revealTopicNavigation(); return; }
    state.detailGeneration++; state.selectedTopic = index; state.selectedPoint = null; state.selectedMembers = membersOf(index); state.hover = -1;
    state.browseTopic = index; state.browseSources = false; state.sourceFilter = ''; state.sourceLimit = 6;
    const topic = map.topics[index]; detailHeading(caption(index)); details.dataset.topicId = topic.id;
    details.append(text('p', `${topic.paperCount.toLocaleString()} papers · ${topic.unitCount.toLocaleString()} question excerpts`, 'detail-meta'));
    if (topic.summary) details.append(text('p', topic.summary));
    if (topic.label !== caption(index)) { const disclosure = document.createElement('details'); disclosure.append(text('summary', 'Original group label'), text('p', topic.label)); details.append(disclosure); }
    const related = map.links.filter(link => link.source === index || link.target === index).sort((a, b) => b.weight - a.weight).slice(0, 3);
    if (related.length) { const disclosure = document.createElement('details'); disclosure.append(text('summary', 'Nearby groups by text affinity')); const list = text('div', '', 'details-list'); related.forEach(link => list.append(topicButton(link.source === index ? link.target : link.source))); disclosure.append(list); details.append(disclosure); }
    if (topic.freshConcern) details.append(text('p', topic.freshConcern, 'detail-meta'));
    const groupBounds = boundsOf([...state.selectedMembers].map(i => map.points[i]));
    setCamera(fitCamera(groupBounds, state.width, state.height, 35));
    renderTopicNavigation(); updateTopicButtons(); revealTopicNavigation(); message(`${caption(index)} selected. Its ${state.selectedMembers.size.toLocaleString()} source excerpts are highlighted.`);
  }
  async function selectPoint(index) {
    const generation = ++state.detailGeneration, point = map.points[index], paper = map.papers[point[1]];
    if (state.browseTopic !== null && !membersOf(state.browseTopic).has(index)) { state.browseTopic = null; state.browseSources = false; state.sourceFilter = ''; state.sourceLimit = 6; }
    state.selectedPoint = index; state.selectedTopic = null; state.selectedMembers = null; state.hover = -1;
    detailHeading(paper[1]); details.dataset.pointId = point[0]; details.append(text('p', `Question excerpt from ${paper[0]}`, 'detail-meta'));
    const question = text('p', 'Loading the source description…', 'detail-excerpt'); question.id = 'overview-excerpt'; details.append(question);
    try { const url = new URL(paper[2]); if (['http:', 'https:'].includes(url.protocol)) { const link = text('a', 'Read the paper ↗', 'detail-link'); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; details.append(link); } } catch { /* No unsafe source link. */ }
    details.append(text('h3', point[5].length > 1 ? 'Overlapping group memberships' : 'Group membership'));
    const homes = text('div', '', 'details-list'); point[5].forEach(home => homes.append(topicButton(home))); details.append(homes);
    details.append(text('p', 'This is a source-scoped question description, not a quotation or a verified physical result.', 'detail-meta'));
    renderTopicNavigation(); setCamera({x: point[2], y: point[3], k: Math.max(state.camera.k, state.fitScale * 10)}); updateTopicButtons(); message(`Selected a question from ${paper[1]}.`);
    revealSourceDetails(generation);
    try { const value = await questionText(index); if (generation === state.detailGeneration) { question.textContent = value; details.dataset.detailReady = 'true'; } }
    catch (error) { if (generation === state.detailGeneration) { question.textContent = error.message; details.dataset.detailReady = 'error'; } }
  }
  function clearSelection() {
    state.detailGeneration++; state.selectedPoint = null; state.selectedTopic = null; state.selectedMembers = null;
    state.browseTopic = null; state.browseSources = false; state.sourceFilter = ''; state.sourceLimit = 6;
    detailHeading('Question details'); details.append(text('p', 'Select a group or a dot to inspect its source questions.')); renderTopicNavigation(); updateTopicButtons();
    const sidebar = details.closest('.overview-sidebar'); if (sidebar) sidebar.scrollTop = 0; schedule();
  }
  function runSearch() {
    if (!state.ready) return;
    const value = $('overview-find').value.trim().toLowerCase(), host = $('overview-results'); host.replaceChildren(); host.hidden = value.length < 2;
    if (value.length < 2) return;
    const topicHits = map.topics.map((t, i) => ({t, i})).filter(({t, i}) => i !== manifest.rootTopicIndex && `${caption(i)} ${t.caption} ${t.label}`.toLowerCase().includes(value)).slice(0, 5);
    const paperHits = map.papers.map((p, i) => ({p, i})).filter(({p}) => `${p[0]} ${p[1]}`.toLowerCase().includes(value)).slice(0, 10);
    const row = child => { const li = document.createElement('li'); li.append(child); host.append(li); };
    for (const {i} of topicHits) row(topicButton(i, 'result-button'));
    for (const {i} of paperHits) if (paperPoints[i]?.length) row(sourceButton(paperPoints[i][0]));
    if (!host.childElementCount) row(text('p', 'No title or group matches. Try another term.'));
    message(`${host.querySelectorAll('button').length} local matches shown. The map layout is unchanged.`);
  }
  function wrapLabel(value, maxWidth, maxLines = 3) {
    const words = value.split(/\s+/), lines = []; let line = '';
    for (const word of words) {
      const next = line ? `${line} ${word}` : word;
      if (ctx.measureText(next).width > maxWidth && line) { lines.push(line); line = word; if (lines.length === maxLines - 1) break; }
      else line = next;
    }
    if (lines.length === maxLines - 1) {
      const consumed = lines.join(' ').split(/\s+/).length;
      line = words.slice(consumed).join(' ');
      while (ctx.measureText(line).width > maxWidth && line.length) line = line.slice(0, -1);
      if (line !== words.slice(consumed).join(' ')) line = `${line.trimEnd().slice(0, -1)}…`;
    }
    if (line) lines.push(line); return lines;
  }
  function paintLabel(value, anchor, type, index, occupied, selected = false) {
    const fontSize = type === 'point' ? 13 : 14; ctx.font = `${selected ? 600 : 500} ${fontSize}px system-ui, sans-serif`;
    const lines = wrapLabel(value, Math.min(type === 'point' ? 230 : 165, state.width - 36), type === 'point' ? 2 : 3);
    const w = Math.max(...lines.map(line => ctx.measureText(line).width)) + 16, h = lines.length * 18 + 12;
    const offsets = [[0, -20], [0, 28], [36, -30], [-36, -30], [45, 35], [-45, 35], [0, -70], [0, 78], [85, -60], [-85, -60], [90, 70], [-90, 70], [0, -120], [0, 125]];
    for (const [dx, dy] of offsets) {
      const box = {x: anchor.x + dx - w / 2, y: anchor.y + dy - h / 2, width: w, height: h};
      if (box.x < 6 || box.y < 6 || box.x + w > state.width - 6 || box.y + h > state.height - 6) continue;
      if (occupied.some(other => box.x < other.x + other.width + 5 && box.x + w + 5 > other.x && box.y < other.y + other.height + 5 && box.y + h + 5 > other.y)) continue;
      ctx.strokeStyle = '#a8bac477'; ctx.lineWidth = .75; ctx.beginPath(); ctx.moveTo(anchor.x, anchor.y); ctx.lineTo(clamp(anchor.x, box.x, box.x + w), clamp(anchor.y, box.y, box.y + h)); ctx.stroke();
      ctx.fillStyle = selected ? '#243c50f2' : '#101c29eb'; ctx.fillRect(box.x, box.y, w, h);
      ctx.fillStyle = '#f0f5fa'; lines.forEach((line, i) => ctx.fillText(line, box.x + 8, box.y + 20 + i * 18));
      const label = {...box, type, index, text: value, fontSize, selected}; occupied.push(label); state.labels.push(label); return true;
    }
    return false;
  }
  function draw() {
    framePending = false; ctx.clearRect(0, 0, state.width, state.height); ctx.fillStyle = '#0c1421'; ctx.fillRect(0, 0, state.width, state.height);
    if (!map) return;
    const ratio = state.camera.k / state.fitScale, radius = clamp(1.15 + Math.log2(Math.max(1, ratio)) * .37, 1.15, 3);
    state.drawn = 0; state.labels = []; const visible = [];
    if (state.selectedTopic !== null) {
      ctx.strokeStyle = '#869bae35'; ctx.lineWidth = 1;
      for (const edge of map.links.filter(link => link.source === state.selectedTopic || link.target === state.selectedTopic)) {
        const a = map.topics[edge.source], b = map.topics[edge.target], x = screenPoint([a.x, a.y], state.camera, state.width, state.height), y = screenPoint([b.x, b.y], state.camera, state.width, state.height);
        ctx.beginPath(); ctx.moveTo(x.x, x.y); ctx.lineTo(y.x, y.y); ctx.stroke();
      }
    }
    for (let color = 0; color < colors.length; color++) {
      for (const dimmed of [true, false]) {
        ctx.fillStyle = colors[color]; ctx.globalAlpha = dimmed ? .11 : .77; ctx.beginPath();
        map.points.forEach((point, index) => {
          if (colorOf[index] !== color || Boolean(state.selectedMembers && !state.selectedMembers.has(index)) !== dimmed) return;
          const p = pointScreen(point); if (p.x < -4 || p.y < -4 || p.x > state.width + 4 || p.y > state.height + 4) return;
          ctx.moveTo(p.x + radius, p.y); ctx.arc(p.x, p.y, radius, 0, 2 * Math.PI); state.drawn++;
          if (!dimmed) visible.push({index, x: p.x, y: p.y});
        }); ctx.fill();
      }
    }
    ctx.globalAlpha = 1;
    for (const index of [state.hover, state.selectedPoint]) if (index !== null && index >= 0) { const p = pointScreen(map.points[index]); ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p.x, p.y, radius + 5, 0, 2 * Math.PI); ctx.stroke(); }
    const occupied = [];
    if (state.selectedPoint !== null) { const point = selectedPoint(); paintLabel(map.papers[point[1]][1], pointScreen(point), 'point', state.selectedPoint, occupied, true); }
    const topics = [...new Set([...(state.selectedTopic === null ? [] : [state.selectedTopic, ...map.topics[state.selectedTopic].children]), ...(ratio >= 1.8 ? broad.flatMap(index => map.topics[index].children) : []), ...broad])];
    topics.sort((a, b) => (a === state.selectedTopic ? -1 : b === state.selectedTopic ? 1 : map.topics[b].mass - map.topics[a].mass));
    for (const index of topics) {
      if (index === manifest.membershipRule.unresolvedTopicIndex) continue;
      const topic = map.topics[index], p = screenPoint([topic.x, topic.y], state.camera, state.width, state.height);
      if (p.x < -20 || p.y < -20 || p.x > state.width + 20 || p.y > state.height + 20 || state.labels.length >= (ratio < 1.8 && state.selectedTopic === null ? 5 : 11)) continue;
      paintLabel(caption(index), p, 'topic', index, occupied, index === state.selectedTopic);
    }
    const labeledTitles = new Set(state.labels.filter(label => label.type === 'point').map(label => label.text));
    if (ratio >= 6) for (const p of visible.sort((a, b) => Math.hypot(a.x - state.width / 2, a.y - state.height / 2) - Math.hypot(b.x - state.width / 2, b.y - state.height / 2))) {
      if (state.labels.length >= 14) break; if (p.index === state.selectedPoint) continue;
      const title = map.papers[map.points[p.index][1]][1]; if (labeledTitles.has(title)) continue;
      if (paintLabel(title, p, 'point', p.index, occupied)) labeledTitles.add(title);
    }
    state.frame++; stage.dataset.frame = String(state.frame); stage.dataset.zoom = ratio.toFixed(3); stage.dataset.ready = 'true';
  }
  function localPointer(event) { const rect = canvas.getBoundingClientRect(); return {x: event.clientX - rect.left, y: event.clientY - rect.top}; }
  function hit(pointer) {
    const label = [...state.labels].reverse().find(box => pointer.x >= box.x && pointer.x <= box.x + box.width && pointer.y >= box.y && pointer.y <= box.y + box.height);
    if (label) return {type: label.type, index: label.index};
    const world = worldPoint(pointer, state.camera, state.width, state.height), index = spatial.nearest(world.x, world.y, 10 / state.camera.k);
    return index >= 0 ? {type: 'point', index} : null;
  }
  $('overview-zoom-in').addEventListener('click', () => zoom(1.5)); $('overview-zoom-out').addEventListener('click', () => zoom(1 / 1.5)); $('overview-fit').addEventListener('click', fit);
  $('overview-topics-back').addEventListener('click', () => {
    if (state.browseTopic === null) return;
    const topic = map.topics[state.browseTopic];
    if (state.browseSources && topic.children.length) selectTopic(state.browseTopic);
    else if (topic.parent === null || topic.parent === manifest.rootTopicIndex) { fit(); revealTopicNavigation(); }
    else selectTopic(topic.parent);
  });
  $('overview-browse-sources').addEventListener('click', () => { if (state.browseTopic === null) return; state.browseSources = true; state.sourceFilter = ''; state.sourceLimit = 6; renderTopicNavigation(); revealTopicNavigation(); });
  $('overview-source-filter').addEventListener('input', event => { state.sourceFilter = event.target.value; state.sourceLimit = 6; renderSourceChoices(); });
  $('overview-find').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(runSearch, 65); });
  $('overview-search').addEventListener('submit', event => { event.preventDefault(); clearTimeout(searchTimer); runSearch(); $('overview-results').querySelector('button')?.click(); });
  canvas.addEventListener('wheel', event => { if (!state.ready) return; event.preventDefault(); zoom(Math.exp(-clamp(event.deltaY, -160, 160) * .004), localPointer(event)); }, {passive: false});
  canvas.addEventListener('pointerdown', event => { if (!state.ready) return; event.preventDefault(); canvas.focus({preventScroll: true}); canvas.setPointerCapture(event.pointerId); pointers.set(event.pointerId, localPointer(event)); if (pointers.size === 1) { moved = false; dragStart = localPointer(event); } else moved = true; if (tooltip) tooltip.hidden = true; });
  canvas.addEventListener('pointermove', event => {
    if (!state.ready) return;
    const next = localPointer(event);
    if (pointers.has(event.pointerId)) {
      const previous = pointers.get(event.pointerId), before = [...pointers.values()]; pointers.set(event.pointerId, next); const after = [...pointers.values()];
      if (pointers.size === 1) { if (Math.hypot(next.x - dragStart.x, next.y - dragStart.y) > 4) moved = true; if (moved) setCamera({...state.camera, x: state.camera.x - (next.x - previous.x) / state.camera.k, y: state.camera.y + (next.y - previous.y) / state.camera.k}); }
      else if (pointers.size === 2) {
        const center = points => ({x: (points[0].x + points[1].x) / 2, y: (points[0].y + points[1].y) / 2});
        const a = center(before), b = center(after), distance = points => Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y);
        const camera = zoomCamera(state.camera, a, distance(after) / Math.max(1, distance(before)), state.width, state.height, state.fitScale * .75, state.fitScale * 100);
        setCamera({...camera, x: camera.x - (b.x - a.x) / camera.k, y: camera.y + (b.y - a.y) / camera.k});
      }
    } else {
      const target = hit(next); state.hover = target?.type === 'point' ? target.index : -1; canvas.style.cursor = target ? 'pointer' : 'grab';
      if (tooltip) { tooltip.hidden = !target; if (target) { tooltip.textContent = target.type === 'topic' ? caption(target.index) : map.papers[map.points[target.index][1]][1]; tooltip.style.left = `${clamp(next.x + 12, 6, Math.max(6, state.width - 240))}px`; tooltip.style.top = `${clamp(next.y + 12, 6, state.height - 70)}px`; } }
      schedule();
    }
  });
  canvas.addEventListener('pointerup', event => { const pointer = localPointer(event), wasActive = pointers.has(event.pointerId); pointers.delete(event.pointerId); if (wasActive && !moved && pointers.size === 0) { const target = hit(pointer); if (target?.type === 'topic') selectTopic(target.index); else if (target) selectPoint(target.index); } });
  canvas.addEventListener('pointercancel', event => { pointers.delete(event.pointerId); moved = true; });
  canvas.addEventListener('pointerleave', () => { if (!pointers.size) { state.hover = -1; if (tooltip) tooltip.hidden = true; schedule(); } });
  canvas.addEventListener('keydown', event => {
    if (!state.ready) return;
    if (['+', '=', '-', 'Home', 'Escape', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) event.preventDefault();
    if (['+', '='].includes(event.key)) zoom(1.4); else if (event.key === '-') zoom(1 / 1.4); else if (event.key === 'Home') fit(); else if (event.key === 'Escape') clearSelection();
    else if (event.key.startsWith('Arrow')) setCamera({...state.camera, x: state.camera.x + (event.key === 'ArrowRight' ? 45 : event.key === 'ArrowLeft' ? -45 : 0) / state.camera.k,
      y: state.camera.y + (event.key === 'ArrowUp' ? 45 : event.key === 'ArrowDown' ? -45 : 0) / state.camera.k});
  });
  window.eigenquestionsOverview = Object.freeze({read: () => ({ready: state.ready, viewId: manifest?.viewId, datasetSha256: manifest?.files?.map?.sha256,
    pointCount: map?.points.length || 0, paperCount: map?.papers.length || 0, topicCount: map?.topics.length || 0, rootChildren: broad,
    camera: {...state.camera}, width: state.width, height: state.height, fitScale: state.fitScale, frame: state.frame, drawn: state.drawn,
    selectedTopic: state.selectedTopic, selectedPoint: state.selectedPoint, selectedUnitId: selectedPoint()?.[0], selectedHomes: selectedPoint()?.[5] || [],
    selectedWorld: selectedPoint() ? {x: selectedPoint()[2], y: selectedPoint()[3]} : null,
    selectedTopicId: state.selectedTopic === null ? null : map.topics[state.selectedTopic].id, selectedMemberCount: state.selectedMembers?.size || 0,
    browseTopic: state.browseTopic, browseMode: state.browseTopic === null ? 'root' : state.browseSources || !map.topics[state.browseTopic].children.length ? 'sources' : 'children',
    labels: state.labels.map(label => ({...label})), loadedDetailShards: [...shardPromises.keys()]})});
  try {
    message('Opening the fixed overview…');
    const response = await fetch('/data/overview/manifest.json'); if (!response.ok) throw new Error(`Overview manifest could not be loaded (${response.status}).`);
    const body = await response.text(); if (body.length > 128 * 1024) throw new Error('Overview manifest is too large.'); manifest = JSON.parse(body);
    map = validateOverview(manifest, await fetchJson(manifest.files.map, 3 * 1024 * 1024)); bounds = boundsOf(map.points); spatial = makeSpatialIndex(map.points, bounds); broad = map.topics[manifest.rootTopicIndex].children;
    const broadClosures = broad.map(index => topicClosure(map.topics, index));
    colorOf = map.points.map(point => { const index = broadClosures.findIndex(set => point[5].some(home => set.has(home))); return index < 0 ? colors.length - 1 : index % colors.length; });
    paperPoints = map.papers.map(() => []); map.points.forEach((point, index) => paperPoints[point[1]].push(index));
    clearSelection(); resize(); state.ready = true;
    document.documentElement.dataset.overviewReady = 'true'; stage.dataset.viewId = manifest.viewId;
    if ($('overview-summary')) $('overview-summary').textContent = `${map.points.length.toLocaleString()} question excerpts · ${map.papers.length.toLocaleString()} papers · fixed collection`;
    message('Drag to pan; zoom to inspect groups and source questions.'); resizeObserver = new ResizeObserver(resize); resizeObserver.observe(stage); schedule();
  } catch (error) { stage.dataset.error = 'true'; message(error.message); detailHeading('Overview unavailable'); details.append(text('p', 'Reload to try the fixed data again. The text explorer remains available in its own tab.')); }
}
