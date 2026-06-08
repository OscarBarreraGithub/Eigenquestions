'use strict';

const State = {
  meta: null,
  byId: new Map(),      // node_id -> tree node {node_id,label,parent,children,size,depth_tree}
  details: null,        // node_id -> detail record (lazy)
  detailsPromise: null,
  detailsError: null,   // truthy if details fetch/parse failed
  selected: null,
  search: { timer: null },
};

const TYPE_LABEL = {
  semantic: 'semantic',
  coupling: 'coupling',
  cocitation: 'co-citation',
  technique: 'technique bridge',
};

// ---------------- boot ----------------
async function boot() {
  const [meta, tree] = await Promise.all([
    fetch('data/meta.json').then(r => r.json()),
    fetch('data/tree.json').then(r => r.json()),
  ]);
  State.meta = meta;
  for (const n of tree) State.byId.set(n.node_id, n);

  wireSearch();
  window.addEventListener('hashchange', onHash);

  // Defer the heavy details.json fetch until idle; landing view needs only tree.json.
  const idle = window.requestIdleCallback || (cb => setTimeout(cb, 300));
  idle(() => loadDetails().catch(() => {}));

  // Empty/invalid hashes fall back to root; replaceState avoids a stale entry.
  const root = meta.root || 'node_root';
  const initial = location.hash.slice(1);
  if (!State.byId.has(initial)) {
    history.replaceState(null, '', location.pathname + location.search + '#' + root);
    selectNode(root, { fromHash: true });
  } else {
    selectNode(initial, { fromHash: true });
  }
}

function loadDetails() {
  if (!State.detailsPromise) {
    State.detailsError = null;
    State.detailsPromise = fetch('data/details.json')
      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(d => { State.details = d; return d; })
      .catch(err => {
        State.detailsError = err;
        State.detailsPromise = null; // allow a later retry
        throw err;
      });
  }
  return State.detailsPromise;
}

const ROOT = () => State.meta.root || 'node_root';
const labelOf = id => (State.byId.get(id)?.label) || id;
const childrenOf = id => (State.byId.get(id)?.children || []);
const hasKids = id => childrenOf(id).length > 0;

function ancestorsOf(id) {
  const chain = [];
  const seen = new Set(); // guard against a malformed parent cycle
  let cur = id;
  while (cur != null && State.byId.has(cur) && !seen.has(cur)) {
    seen.add(cur);
    chain.push(cur);
    cur = State.byId.get(cur).parent;
  }
  return chain.reverse(); // root..node
}

function sortedKids(id) {
  return childrenOf(id).slice().sort((a, b) => labelOf(a).localeCompare(labelOf(b)));
}

// ---------------- miller columns ----------------
// Build the full chain of columns from root to the selected node, then a final
// column for the selected node's own children (so you can keep drilling).
function renderColumns(id) {
  const colsEl = document.getElementById('columns');
  colsEl.innerHTML = '';
  // At the root landing keep the tall strip (all fields visible); collapse to
  // the compact strip once the user has drilled into a deeper node.
  colsEl.classList.toggle('deep', id !== ROOT());

  const chain = ancestorsOf(id);          // root..node
  // For each node in the chain, render a column listing its children; the next
  // chain element is the "active" item in that column.
  for (let i = 0; i < chain.length; i++) {
    const parent = chain[i];
    const activeChild = chain[i + 1] || null; // the deeper node, if any
    if (!hasKids(parent)) continue;           // leaf: no column of children
    colsEl.appendChild(buildColumn(parent, activeChild));
  }
  // Note: the loop's last iteration (parent = id, no active child) already
  // renders the selected node's own children column, so there is no separate
  // "final" column to append.

  // Auto-scroll so the rightmost (active) column is visible.
  requestAnimationFrame(() => { colsEl.scrollLeft = colsEl.scrollWidth; });
}

function buildColumn(parentId, activeChildId) {
  const col = document.createElement('div');
  col.className = 'column';
  col.dataset.parent = parentId;
  for (const cid of sortedKids(parentId)) {
    col.appendChild(buildColRow(cid, cid === activeChildId));
  }
  return col;
}

function buildColRow(id, isActive) {
  const node = State.byId.get(id);
  const row = document.createElement('div');
  row.className = 'col-row' + (isActive ? ' active' : '');
  row.dataset.id = id;

  const label = document.createElement('span');
  label.className = 'col-label';
  label.textContent = node.label;
  const nk = childrenOf(id).length;
  label.title = node.label + (nk ? '  ·  ' + nk + ' subtopic' + (nk === 1 ? '' : 's') : '');

  const size = document.createElement('span');
  size.className = 'col-size';
  if (node.size != null) { size.textContent = fmtNum(node.size); size.title = fmtNum(node.size) + ' papers'; }

  const arrow = document.createElement('span');
  arrow.className = 'col-arrow';
  arrow.textContent = nk ? '›' : '';

  row.append(label, size, arrow);
  row.addEventListener('click', () => selectNode(id));
  return row;
}

// Reset the search UI to its idle state.
function clearSearch() {
  if (State.search.timer) { clearTimeout(State.search.timer); State.search.timer = null; }
  const input = document.getElementById('search');
  if (input) input.value = '';
  const results = document.getElementById('search-results');
  if (results) { results.hidden = true; results.innerHTML = ''; }
}

// ---------------- selectNode (single source of truth) ----------------
function selectNode(id, { fromHash = false } = {}) {
  if (!State.byId.has(id)) return;
  State.selected = id;

  clearSearch();
  renderColumns(id);     // rebuild full column chain to this node
  renderBreadcrumb(id);
  renderDetail(id);

  if (!fromHash) {
    if (location.hash.slice(1) !== id) location.hash = id;
  }
}

function onHash() {
  const root = ROOT();
  const id = location.hash.slice(1);
  if (!State.byId.has(id)) {
    history.replaceState(null, '', '#' + root);
    if (State.selected !== root) selectNode(root, { fromHash: true });
    return;
  }
  if (id !== State.selected) selectNode(id, { fromHash: true });
}

// ---------------- breadcrumb ----------------
function renderBreadcrumb(id) {
  const el = document.getElementById('breadcrumb');
  el.innerHTML = '';
  const chain = ancestorsOf(id);
  chain.forEach((cid, i) => {
    if (i > 0) {
      const sep = document.createElement('span');
      sep.className = 'crumb-sep'; sep.textContent = '›';
      el.appendChild(sep);
    }
    const c = document.createElement('span');
    const isCurrent = (i === chain.length - 1);
    c.className = 'crumb' + (isCurrent ? ' current' : '');
    c.textContent = (cid === ROOT()) ? 'All fields' : labelOf(cid);
    c.title = c.textContent;
    if (!isCurrent) c.addEventListener('click', () => selectNode(cid));
    el.appendChild(c);
  });
}

// ---------------- detail region ----------------
async function renderDetail(id) {
  const inner = document.getElementById('detail-inner');
  const node = State.byId.get(id);
  const isRoot = (id === ROOT());

  inner.innerHTML = '';

  const title = document.createElement('h1');
  title.className = 'node-title';
  title.textContent = isRoot ? 'All fields' : node.label;
  inner.appendChild(title);

  const det = State.details ? State.details[id] : null;
  const metaRow = document.createElement('div');
  metaRow.className = 'detail-meta';
  inner.appendChild(metaRow);
  fillMeta(metaRow, node, det, isRoot);

  const idEl = document.createElement('div');
  idEl.className = 'detail-id';
  idEl.textContent = node.node_id;
  inner.appendChild(idEl);

  const body = document.createElement('div');
  inner.appendChild(body);

  if (isRoot) {
    const paras = [
      'We started with about 200,000 high-energy physics papers from arXiv. An embedding model (Qwen3-Embedding) turns each title and abstract into a list of 1024 numbers, a vector, and papers about similar physics get similar vectors. We grouped those vectors into clusters, then split each cluster again, and kept going. That is the tree you are navigating: broad fields at the top, narrow subtopics at the bottom.',
      'To make the questions, we took each topic in the tree and pulled its most representative papers, plus the matching Snowmass community reports where we had them. We gave those to a language model along with how deep and specialized the topic is, and asked it to write open research questions that fit that exact spot. We then embedded each question the same way as the papers and checked that it lands back near its own topic. Each one is a direction the model proposed from that recent work, not a confirmed account of what the field is currently pursuing, so treat them as starting points rather than a settled agenda.',
      'Cosine similarity is how we measure closeness between two vectors. It is the cosine of the angle between them: close to 1 when they point the same way (very similar physics) and close to 0 when they have nothing in common.'
    ];
    for (const t of paras) {
      const d = document.createElement('div');
      d.className = 'note';
      d.textContent = t;
      body.appendChild(d);
    }
    const conn = document.createElement('div');
    conn.className = 'note';
    conn.innerHTML =
      'The links under "Related elsewhere" come from four different signals:' +
      '<dl class="conn-defs">' +
      '<dt>Semantic</dt><dd>topics whose vectors are close, so the writing is about similar physics.</dd>' +
      '<dt>Coupling</dt><dd>topics that cite many of the same earlier papers, so they build on the same foundations.</dd>' +
      '<dt>Co-citation</dt><dd>topics that later papers tend to cite together in the same breath.</dd>' +
      '<dt>Technique bridge</dt><dd>topics that sit far apart in the tree but share methods or references, where a tool from one area carries over to another.</dd>' +
      '</dl>';
    body.appendChild(conn);
    return;
  }

  if (!State.details) {
    const l = document.createElement('div');
    l.className = 'loading'; l.textContent = 'Loading question details…';
    body.appendChild(l);
    try {
      await loadDetails();
    } catch (err) {
      if (State.selected !== id) return;
      body.innerHTML = '';
      const e = document.createElement('div'); e.className = 'note err-note';
      e.textContent = 'Could not load question details (' + (err && err.message || 'fetch error') + ').';
      const retry = document.createElement('span'); retry.className = 'retry-link';
      retry.textContent = 'Retry';
      retry.addEventListener('click', () => renderDetail(id));
      e.appendChild(retry);
      body.appendChild(e);
      return;
    }
    if (State.selected !== id) return;
    fillMeta(metaRow, node, State.details[id], isRoot);
    body.innerHTML = '';
  }
  renderDetailBody(body, id, State.details[id]);
}

function fillMeta(metaRow, node, det, isRoot) {
  const bits = [];
  if (node.size != null) bits.push(fmtNum(node.size) + ' papers');
  if (node.depth_tree != null) bits.push('depth ' + node.depth_tree);
  if (det && det.generality != null) bits.push('generality ' + Number(det.generality).toFixed(3));
  if (det && det.tier) bits.push(det.tier);
  if (det && det.disagreement) bits.push('disagreement');
  if (det && det.year_span && det.year_span[1] != null) {
    const lo = det.year_span[0], hi = det.year_span[1];
    bits.push((lo != null ? lo + '–' : '–') + hi);
  }
  if (isRoot) bits.unshift('top-level grouping');
  metaRow.textContent = bits.join('  ·  ');
}

function renderDetailBody(body, id, det) {
  body.innerHTML = '';
  if (!det) {
    const n = document.createElement('div'); n.className = 'note';
    n.textContent = 'No detail record for this node.'; body.appendChild(n); return;
  }

  if (det.summary) {
    const p = document.createElement('p');
    p.className = 'summary'; p.textContent = det.summary;
    body.appendChild(p);
  }

  // reference papers
  const refs = (det.sources && (det.sources.representative_arxiv_ids || [])) || [];
  if (refs.length) {
    body.appendChild(secHead('Reference papers'));
    const box = document.createElement('div'); box.className = 'refs';
    refs.slice(0, 8).forEach(aid => {
      const a = document.createElement('a');
      a.className = 'ref'; a.textContent = aid;
      a.href = 'https://arxiv.org/abs/' + aid;
      a.target = '_blank'; a.rel = 'noopener';
      a.title = 'arXiv:' + aid + ' (opens in new tab)';
      box.appendChild(a);
    });
    body.appendChild(box);
  }

  // questions
  body.appendChild(secHead('Eigenquestions'));
  if (!det.questions || !det.questions.length) {
    const n = document.createElement('div'); n.className = 'note';
    n.textContent = 'No generated questions for this node — drill down to a more specific subtopic.';
    body.appendChild(n);
  } else {
    const ol = document.createElement('ol'); ol.className = 'qlist';
    for (const q of det.questions) ol.appendChild(questionItem(q));
    body.appendChild(ol);
  }

  // related elsewhere
  renderRelated(body, det.related || []);
}

function secHead(txt) {
  const h = document.createElement('div');
  h.className = 'sec-head'; h.textContent = txt; return h;
}

function questionItem(q) {
  const li = document.createElement('li'); li.className = 'qitem';
  const txt = document.createElement('div');
  txt.className = 'qtext'; txt.textContent = q.question;
  li.appendChild(txt);

  const prereqs = (q.kg_prereqs || []).slice(0, 6);
  if (prereqs.length || q.placement) {
    const meta = document.createElement('div'); meta.className = 'qmeta';
    const parts = [];
    if (prereqs.length) {
      meta.appendChild(Object.assign(document.createElement('span'),
        { className: 'prereq-label', textContent: 'prerequisites: ' }));
      meta.appendChild(document.createTextNode(prereqs.join(', ')));
    }
    if (q.placement) {
      const tail = (prereqs.length ? '  ·  ' : '') + 'embeds back: ' + q.placement
        + (q.cos_to_target != null ? ' (cos ' + Number(q.cos_to_target).toFixed(2) + ')' : '');
      meta.appendChild(document.createTextNode(tail));
    }
    li.appendChild(meta);
  }

  if (q.rationale) {
    const toggle = document.createElement('span');
    toggle.className = 'why-toggle';
    toggle.textContent = '› why this question';
    const bodyEl = document.createElement('div');
    bodyEl.className = 'why-body'; bodyEl.textContent = q.rationale; bodyEl.hidden = true;
    toggle.addEventListener('click', () => {
      bodyEl.hidden = !bodyEl.hidden;
      toggle.textContent = (bodyEl.hidden ? '›' : '▾') + ' why this question';
    });
    li.append(toggle, bodyEl);
  }
  return li;
}

function renderRelated(body, related) {
  const off = related.filter(r => r.rel === 'off_path');
  body.appendChild(secHead('Related elsewhere'));
  const sub = document.createElement('div');
  sub.className = 'rel-sub';
  sub.textContent = 'High-signal connections in distant branches of the tree — the cross-field bridges.';
  body.appendChild(sub);

  if (!off.length) {
    if (State.meta.technique_transfer !== 'present') {
      const p = document.createElement('div'); p.className = 'empty-rel';
      p.textContent = 'technique bridges: computing…'; body.appendChild(p);
    } else {
      const e = document.createElement('div'); e.className = 'empty-rel';
      e.textContent = 'No off-path connections recorded for this node.';
      body.appendChild(e);
    }
    return;
  }

  // order: technique bridges first, then semantic/coupling/cocitation; dedup by id.
  const order = { technique: 0, semantic: 1, coupling: 2, cocitation: 3 };
  const seen = new Set();
  const items = off.slice()
    .sort((a, b) => (order[a.t] ?? 9) - (order[b.t] ?? 9) || (b.w || 0) - (a.w || 0))
    .filter(r => { if (seen.has(r.id)) return false; seen.add(r.id); return true; })
    .slice(0, 20);

  const list = document.createElement('div'); list.className = 'rel-list';
  for (const r of items) {
    const item = document.createElement('div'); item.className = 'rel-item';
    const link = document.createElement('span');
    link.className = 'rel-link'; link.textContent = labelOf(r.id);
    link.title = labelOf(r.id) + '  ·  click to navigate';
    link.addEventListener('click', () => selectNode(r.id)); // rebuilds columns to path
    item.appendChild(link);

    const type = document.createElement('span');
    type.className = 'rel-type'; type.textContent = TYPE_LABEL[r.t] || r.t;
    item.appendChild(type);

    if (r.hf && r.hf !== r.id) {
      const fld = document.createElement('span');
      fld.className = 'rel-field'; fld.textContent = '· in ' + labelOf(r.hf);
      item.appendChild(fld);
    }
    list.appendChild(item);
  }
  body.appendChild(list);
}

// ---------------- search ----------------
function wireSearch() {
  const input = document.getElementById('search');
  const results = document.getElementById('search-results');

  input.addEventListener('input', () => {
    if (State.search.timer) clearTimeout(State.search.timer);
    State.search.timer = setTimeout(() => runSearch(input.value.trim()), 160);
  });

  function runSearch(q) {
    if (!q) { results.hidden = true; results.innerHTML = ''; return; }
    const ql = q.toLowerCase();
    const hits = [];
    for (const [id, n] of State.byId) {
      if (id === ROOT()) continue;
      if (n.label.toLowerCase().includes(ql)) hits.push({ id, where: 'topic' });
      if (hits.length >= 60) break;
    }
    if (State.details && hits.length < 60) {
      const have = new Set(hits.map(h => h.id));
      for (const id in State.details) {
        if (have.has(id)) continue;
        const qs = State.details[id].questions || [];
        if (qs.some(x => x.question.toLowerCase().includes(ql))) {
          hits.push({ id, where: 'question' });
          if (hits.length >= 60) break;
        }
      }
    }
    renderResults(hits, q);
  }

  function renderResults(hits, q) {
    results.hidden = false;
    results.innerHTML = '';
    const head = document.createElement('div'); head.className = 'sr-head';
    if (!hits.length) {
      head.textContent = 'No matches for “' + q + '”';
      results.appendChild(head);
      return;
    }
    const n = Math.min(hits.length, 50);
    head.textContent = n + ' result' + (n === 1 ? '' : 's') + ' for “' + q + '”'
      + (hits.length > 50 ? ' (showing first 50)' : '');
    results.appendChild(head);
    for (const h of hits.slice(0, 50)) {
      const n = State.byId.get(h.id);
      const item = document.createElement('div'); item.className = 'sr-item';
      const lab = document.createElement('span'); lab.className = 'sr-label';
      lab.textContent = n.label; lab.title = n.label;
      if (h.where === 'question') {
        const tag = document.createElement('span'); tag.className = 'sr-tag';
        tag.textContent = 'matches a question'; item.appendChild(tag);
      }
      item.appendChild(lab);
      const crumb = document.createElement('div'); crumb.className = 'sr-crumb';
      const chain = ancestorsOf(h.id).slice(1, -1).map(labelOf);
      crumb.textContent = chain.join(' › ') || 'top level';
      crumb.title = crumb.textContent;
      item.appendChild(crumb);
      // selectNode() calls clearSearch(), which hides results, and rebuilds columns.
      item.addEventListener('click', () => selectNode(h.id));
      results.appendChild(item);
    }
  }
}

// ---------------- utils ----------------
function fmtNum(n) {
  if (n >= 1000) return (n / 1000).toFixed(n >= 10000 ? 0 : 1) + 'k';
  return String(n);
}

boot();
