// Production entry adapter for the adopted S14 render, source commit 6933ee5f.
// Keep source modules/assets at their published URLs. No drawing/timing changes.
import {renderFrame as renderPrefix} from '/collab/reviews/cloud_s14_scene_20261020/s14_scene.mjs';
import {renderTail} from '/collab/reviews/cloud_s14_scene_20261020/s14_tail.mjs';
export const DURATION = 10;
export const FPS = 24;
const EXPOSURES = '/collab/reviews/cloud_s14_scene_20261020/BACKSTAGE_RETURN_132_167_EXPOSURE_PROPOSAL.json';
let rowsPromise;
async function stepRows() {
  return rowsPromise ??= fetch(EXPOSURES).then(async r => {
    if (!r.ok) throw Error('S14 exposure load failed: '+r.status);
    return (await r.json()).trialRows;
  });
}
export async function renderFrame(ctx, t, W, H) {
  const f = Math.max(0, Math.min(239, Math.floor(t * FPS + 1e-6)));
  const time = f / FPS;
  if (f < 132) return renderPrefix(ctx, time, W, H);
  if (f < 168) {
    const e = (await stepRows()).find(e => f >= e.frame && f <= e.through);
    if (!e) throw Error('S14 approved step exposure absent at '+f);
    return renderTail(ctx, time, W, H, e, {backstage:true, showUncoveredGrandma:false});
  }
  return renderTail(ctx, time, W, H, null, {backstage:true, showUncoveredGrandma:false});
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
