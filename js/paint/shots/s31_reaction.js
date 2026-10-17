// S31-only continuation of the reviewed S30 frozen head position.
// S29/S30 geometry and behavior remain owned by s29_lamp.js.
import { renderFrozenHead } from './s29_lamp.js';
import { renderShot, billboardM, S } from '../../lamp/s06_key.js';
import { loadMaps, makeLamp, flatMaps } from '../../lamp/s08_back.js';

export const DURATION = 7.5;
const GR = { ox: 250, oy: 770, sc: 24 }, START = [1.43, .44, 1.23];
const smooth = (a, b, t) => { const u = Math.max(0, Math.min(1, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
let A = null, B = null, LM = null, MIX = null;
const load = async path => createImageBitmap(await (await fetch(path)).blob());
async function ready(wantB) {
  if (!A) { A = { maps: await loadMaps('g29_prepare_blow'), mask: await load('/assets/chars/g29_prepare_blow_shadow.png') }; LM = lamp(); }
  if (wantB && !B) B = { maps: await loadMaps('g31_release_smile'), mask: await load('/assets/chars/g31_release_smile_shadow.png') };
}

export function reactionState(t) {
  const exit = smooth(5.4, 7.1, t);
  return { close: t < 5.3, release: smooth(4.125, 4.25, t), base: [START[0] + .82 * exit, START[1], START[2]] };
}

// Only the derived face region differs between A/B; premultiplied canvas
// addition also removes the old cheek alpha during this three-frame change.
function poseImage(p) {
  if (p === 0) return A;
  if (p === 1) return B;
  MIX ||= { maps: {}, mask: new OffscreenCanvas(1024, 1536) };
  for (const ch of ['alb', 'nrm', 'mat', 'mask']) {
    const c = ch === 'mask' ? MIX.mask : (MIX.maps[ch] ||= new OffscreenCanvas(1024, 1536));
    const x = c.getContext('2d'), a = ch === 'mask' ? A.mask : A.maps[ch], b = ch === 'mask' ? B.mask : B.maps[ch];
    x.clearRect(0, 0, c.width, c.height); x.globalCompositeOperation = 'source-over'; x.globalAlpha = 1 - p; x.drawImage(a, 0, 0);
    x.globalCompositeOperation = 'lighter'; x.globalAlpha = p; x.drawImage(b, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over';
  }
  return MIX;
}
function actor(base, image) {
  const bounds = [-GR.ox / GR.sc * 10, (GR.oy - 1536) / GR.sc * 10, (1024 - GR.ox) / GR.sc * 10, GR.oy / GR.sc * 10];
  const part = { part: 'head', parent: null, layer: 0, bounds, t: image.mask, r: image.maps.alb };
  return { pup: { rig: [part], parts: { head: part } }, pose: { angles: {}, rootAngle: 0, facing: -1 }, root: [base[0], base[2]], dist: base[1] };
}
function headM(cam, base) {
  const p = cam.project(base), dx = cam.project([base[0] - 1 / 24, base[1], base[2]]), dy = cam.project([base[0], base[1], base[2] - 1 / 24]);
  const a = (dx[0] - p[0]) / 100, b = (dx[1] - p[1]) / 100, c = (dy[0] - p[0]) / 100, d = (dy[1] - p[1]) / 100;
  return [a, b, c, d, p[0] - a * GR.ox - c * GR.oy, p[1] - b * GR.ox - d * GR.oy];
}
// Same bounded lamp card as the reviewed S29 close-up; this helper does not
// alter s29_lamp.js, its exposure, or either earlier shot.
function lamp() {
  const l = makeLamp(), glass = new OffscreenCanvas(260, 460), x = glass.getContext('2d');
  x.globalAlpha = .08; x.drawImage(l.glass.alb, 0, 0); x.globalAlpha = 1;
  x.strokeStyle = 'rgba(216,224,219,.30)'; x.lineWidth = 1.3; x.beginPath(); x.ellipse(130, 235, 52, 70, 0, 0, Math.PI * 2); x.stroke();
  x.strokeStyle = 'rgba(243,239,218,.42)'; x.lineWidth = 2.5; x.lineCap = 'round'; x.beginPath(); x.moveTo(100, 195); x.quadraticCurveTo(84, 218, 90, 244); x.stroke();
  return { ...l, metal: flatMaps(l.metal.alb, 8, .12), glass: flatMaps(glass, 8, 0) };
}

// S30 lasts 12 seconds. Advance the same light/cloth clock by one frame at
// the cut, while Grandma is still holding her breath before the invitation.
export async function renderHeldBackground(ctx, t, w, h) {
  return renderFrozenHead(ctx, 12 + t, w, h);
}

export async function renderReaction(ctx, t, w, h) {
  const state = reactionState(t); await ready(state.release > 0); const image = poseImage(state.release);
  const shot = {
    cam: state.close ? { pos: [1.15, 1.6, 1.32], target: [1.52, .44, 1.32], hfov: 36 } : { pos: [1, -2.5, 1.45], target: [1, 0, 1.45], hfov: 43 },
    exp: state.close ? .08 : .65, fluor: () => 0, fog: state.close ? .2 : .45,
    sheet: () => [actor(state.base, image)],
    cards: state.close ? async (CARDS, cam) => {
      CARDS.addImage([{ maps: image.maps, m: headM(cam, state.base) }], cam.project(state.base)[2]);
      const L = S.lamp, base = [L.x, L.y, L.z], m = billboardM(cam, base, LM.ox, LM.oy, LM.K);
      CARDS.addImage([{ maps: LM.metal, m }, { maps: LM.glass, m }, { maps: LM.flame, m }], cam.project(base)[2]);
    } : null,
  };
  return renderShot(ctx, 24 + t, w, h, shot);
}

// Helper preview only. The parent shot keeps its own 14-second duration.
export async function renderFrame(ctx, t, w, h) { return t < 4 ? renderHeldBackground(ctx, t, w, h) : renderReaction(ctx, t, w, h); }
