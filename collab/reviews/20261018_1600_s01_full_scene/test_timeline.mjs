import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { FRAME_COUNT, DURATION, ASSET_INFO, REGISTRATION, frameIndex, frameAssets, pickAsset } from './timeline.js';
assert.equal(FRAME_COUNT, 84); assert.equal(DURATION, 3.5);
const counts = { G: {}, X: {} }; const missing = {};
for (let f = 0; f < 84; f++) {
  assert.equal(frameIndex(f / 24), f);
  const x = pickAsset('X', f); counts.X[x] = (counts.X[x] || 0) + 1;
  const gkeys = [0,10,12,28,29,30,31,32,33,34,35,50,62,70];
  const expectedKey = gkeys.filter(k => k <= f).at(-1);
  const expectedName = 'F' + String(expectedKey).padStart(3, '0') + '_grandma_rgba.png';
  if (ASSET_INFO[expectedName]) {
    const g = frameAssets(f).G; assert.equal(g, expectedName);
    counts.G[g] = (counts.G[g] || 0) + 1;
  } else {
    const key = 'F' + String(expectedKey).padStart(3, '0');
    assert.throws(() => frameAssets(f), new RegExp('missing locked G ' + key)); missing[key] = (missing[key] || 0) + 1;
  }
}
assert.deepEqual(Object.values(counts.X), [10, 18, 15, 41]);
assert.equal(Object.values(counts.G).reduce((a,b)=>a+b,0) + Object.values(missing).reduce((a,b)=>a+b,0), 84);
for (const f of [-1, 84, .5, NaN]) assert.throws(() => frameAssets(f));
for (const t of [-1, 3.5, Infinity, NaN]) assert.throws(() => frameIndex(t));
assert.deepEqual(REGISTRATION.G, { x: 730, y: 375, sc: .2734375 });
assert.deepEqual(REGISTRATION.X, { x: 399.28, y: 533, sc: .16 });
for (const [name, info] of Object.entries(ASSET_INFO)) {
  const bytes = await readFile(new URL('./frames/' + name, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), info.sha256, name);
  assert.equal(bytes.readUInt32BE(16), info.width, name);
  assert.equal(bytes.readUInt32BE(20), info.height, name);
}
console.log(JSON.stringify({status:'passed',frame_count:84,available_scene_frame_count:Object.values(counts.G).reduce((a,b)=>a+b,0),counts,missing,asset_count:Object.keys(ASSET_INFO).length},null,2));
