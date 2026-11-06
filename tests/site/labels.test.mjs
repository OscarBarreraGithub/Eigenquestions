import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { boxesOverlap, boxTouchesCircle, placeChartLabel } from '../../web/chart-labels.mjs';
import { loadLocalNavigator } from '../../lib/protocol/runtime.mjs';
import { currentState, importSession } from '../../lib/protocol/session.mjs';

test('the actual public recent-USING state keeps all five markers clear of placed labels', async () => {
  const exported = JSON.parse(await readFile(new URL('../../docs/evidence/public-v1/public-browser-session.json', import.meta.url)));
  const { navigator, corpus } = await loadLocalNavigator();
  const session = importSession(exported, { corpusId: corpus.manifest.corpusId, computationId: navigator.computationId });
  const state = currentState(session);
  assert.equal(state.intent, 'recent');
  assert.equal(state.workRelation, 'using');
  const view = navigator.computeView(state), before = view.directions.map(({ x, y }) => [x, y]);
  assert.equal(view.directions.length, 5);
  const xs = before.map(point => point[0]), ys = before.map(point => point[1]);
  const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
  const bounds = { width: 760, height: 420 }, margin = 54;
  const scale = Math.min((bounds.width - 2 * margin) / Math.max(xmax - xmin, .1), (bounds.height - 2 * margin) / Math.max(ymax - ymin, .1));
  const markers = view.directions.map(direction => ({ x: bounds.width / 2 + (direction.x - (xmin + xmax) / 2) * scale, y: bounds.height / 2 - (direction.y - (ymin + ymax) / 2) * scale, radius: 10 + 18 * Math.sqrt(direction.massFraction) }));
  const obstacles = markers.map(marker => ({ ...marker, radius: Math.max(marker.radius, 22) + 4 }));
  for (const width of [160, 210, 280]) {
    const placed = [];
    markers.forEach((marker, index) => {
      const box = placeChartLabel({ anchor: marker, width, height: 48, bounds, circles: obstacles, labels: placed });
      if (index === 0) assert.ok(box, `Previously obscured direction 1 needs a safe ${width}px label position`);
      if (!box) return; // Omitting a crowded label is the documented fallback.
      assert.ok(box.x >= 12 && box.y >= 12 && box.x + box.width <= bounds.width - 12 && box.y + box.height <= bounds.height - 12);
      for (const other of obstacles) {
        assert.equal(boxTouchesCircle(box, other), false);
        assert.equal(boxesOverlap(box, { x: other.x - other.radius, y: other.y - other.radius, width: other.radius * 2, height: other.radius * 2 }), false);
      }
      for (const other of placed) assert.equal(boxesOverlap(box, other), false);
      assert.deepEqual(placeChartLabel({ anchor: marker, width, height: 48, bounds, circles: obstacles, labels: placed }), box);
      placed.push(box);
    });
    // Wider labels may be omitted; retaining all labels must not override safety.
  }
  assert.deepEqual(view.directions.map(({ x, y }) => [x, y]), before, 'Placement must never move projected coordinates');
});

test('an overfilled chart omits labels instead of covering a marker', () => {
  const anchor = { x: 50, y: 50, radius: 25 };
  assert.equal(placeChartLabel({ anchor, width: 80, height: 60, bounds: { width: 100, height: 100 }, circles: [anchor], labels: [] }), null);
});
