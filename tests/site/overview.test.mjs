import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {screenPoint, worldPoint, zoomCamera, fitCamera, boundsOf, makeSpatialIndex, validateOverview, topicClosure} from '../../web/overview.js';

const manifest = JSON.parse(await readFile(new URL('../../data/overview/manifest.json', import.meta.url)));
const map = JSON.parse(await readFile(new URL('../../data/overview/map.json', import.meta.url)));

test('overview camera preserves the pointed world coordinate, bounds zoom, and fits fixed input', () => {
  const bounds = boundsOf(map.points), camera = fitCamera(bounds, 850, 640), pointer = {x: 127, y: 401};
  const before = worldPoint(pointer, camera, 850, 640), zoomed = zoomCamera(camera, pointer, 2.2, 850, 640, 1, 10000);
  const after = worldPoint(pointer, zoomed, 850, 640);
  assert.ok(Math.abs(before.x - after.x) < 1e-12 && Math.abs(before.y - after.y) < 1e-12);
  for (const point of map.points) { const p = screenPoint([point[2], point[3]], camera, 850, 640); assert.ok(p.x >= 34 && p.x <= 816 && p.y >= 34 && p.y <= 606); }
  assert.equal(zoomCamera(camera, pointer, 1e8, 850, 640, 1, 900).k, 900);
  assert.equal(zoomCamera(camera, pointer, 1e-8, 850, 640, 1, 900).k, 1);
});

test('overview spatial picking matches brute force at multiple camera scales and empty locations', () => {
  const grid = makeSpatialIndex(map.points, boundsOf(map.points));
  for (const [x, y, radius] of [[0,0,.03],[-1,-1,.05],[2.1,.2,.1],[50,50,.1],...map.points.filter((_,i)=>i%997===0).map(p=>[p[2]+.002,p[3]-.001,.05])]) {
    let best = -1, distance = radius * radius;
    map.points.forEach((p, i) => { const d = (x-p[2])**2+(y-p[3])**2; if (d < distance) { distance = d; best = i; } });
    assert.equal(grid.nearest(x,y,radius), best);
  }
});

test('overview validates identities, rejects malformed geometry, and preserves overlapping descendant memberships', () => {
  assert.equal(validateOverview(manifest,map),map);
  assert.equal(map.points.length,8473); assert.equal(map.papers.length,6477);
  assert.equal(map.points.filter(p=>p[5].length>1).length,10);
  for (const index of map.topics[manifest.rootTopicIndex].children) {
    const closure = topicClosure(map.topics,index), members = map.points.filter(p=>p[5].some(home=>closure.has(home)));
    assert.equal(members.length,map.topics[index].unitCount);
  }
  const broken = structuredClone(map); broken.points[0][2]='not a coordinate'; assert.throws(()=>validateOverview(manifest,broken),/coordinates/);
  const cycle = structuredClone(map); cycle.topics[1].parent=1; assert.throws(()=>validateOverview(manifest,cycle),/cyclic hierarchy/);
  const wrongDetails = structuredClone(manifest); wrongDetails.files.details[1].start++; assert.throws(()=>validateOverview(wrongDetails,map),/alignment/);
});
