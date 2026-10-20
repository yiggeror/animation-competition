// LOCAL COLLAB CANDIDATE. No change to the production S01 implementation or EDL.
// Original scene/props/light/camera, with only characters replaced by approved drawings.
import { openingPowerStripLayer, HELD_PHONE_PORT } from './opening_power_strip.js';
import { renderPaint, loadImg } from '/js/paint/paintshot.js';
import { COIL, COILC, FAN } from '/js/paint/shots/s01.js';
import { lamp as drawLamp, LX, LB } from '/js/code/s08.js';
import { DURATION, FRAME_COUNT, REGISTRATION, ASSET_INFO, frameIndex, frameAssets } from '/js/anim/s01_drawn_timeline.js';
export { DURATION, FRAME_COUNT };
const BW = 1672, BH = 941;
const tv = (t) => 0.3 + 0.12 * Math.sin(t * 3.1) + 0.08 * Math.sin(t * 7.7 + 1) + (Math.sin(t * 1.3) > 0.85 ? 0.15 : 0);
const FRAMES = new URL('/assets/chars/s01/', import.meta.url);
const verifiedImages = new Map();
async function lockedImage(filename) {
  if (!verifiedImages.has(filename)) verifiedImages.set(filename, (async () => {
    const expected = ASSET_INFO[filename];
    if (!expected) throw new Error('Asset is not in locked manifest: ' + filename);
    const img = await loadImg(new URL(filename, FRAMES).href);
    if (!img) throw new Error('Missing locked drawing: ' + filename);
    if (img.width !== expected.width || img.height !== expected.height) throw new Error('Registered canvas dimensions changed: ' + filename);
    return img;
  })());
  return verifiedImages.get(filename);
}
// This is the exact source table lamp and matchbox; it draws no character.
export const LAMP_AT = [1262, 642], LAMP_S = 0.17;
export function tableLamp(lift = 0) {
  const c = new OffscreenCanvas(220, 200), x = c.getContext('2d');
  x.translate(110, 170 - lift); x.scale(-LAMP_S, LAMP_S); x.translate(-LX, -LB); drawLamp(x, 0, false);
  x.setTransform(1, 0, 0, 1, 0, 0); x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 1; x.beginPath(); x.rect(150, 162, 18, 7); x.fill(); x.stroke();   // 火柴盒
  return { img: c, x: LAMP_AT[0] - 110, y: LAMP_AT[1] - 170, sc: 1 };
}

// Exact original stool primitive and charLayer pre-transform, without calling any code character.
function stool(x, cx, top = 30) {
  x.fillStyle = '#8a5b3c'; x.strokeStyle = '#3b2c25'; x.lineWidth = 1.2;
  x.beginPath(); x.rect(cx - 15, -top, 30, 4); x.fill(); x.stroke();
  for (const dx of [-12, 9]) { x.beginPath(); x.rect(cx + dx, -top + 4, 3, top - 4); x.fill(); x.stroke(); }
}
function originalStoolLayer() {
  const c = new OffscreenCanvas(560, 640), x = c.getContext('2d');
  x.scale(2, 2); x.translate(935 - 780, 775 - 470); x.scale(-2.77, 2.77);
  stool(x, -2);
  return { img: c, x: 780, y: 470, sc: 0.5, contact: { a: 0.45, blur: 3, sy: -0.1, skew: 0.5 } };
}
let cachedStool;
let cachedLamp;
export const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const keys = frameAssets(frameIndex(t)); // Throws for every missing key range before image loading.
    const [X, G] = await Promise.all([lockedImage(keys.X), lockedImage(keys.G)]);
    return [
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      cachedLamp ||= tableLamp(),
      openingPowerStripLayer(HELD_PHONE_PORT),
      { img: X, ...REGISTRATION.X, contact: { a: 0.4, blur: 3, sy: 1, dx: -2, dy: 3 } },   // 接地影子（Opus 10-18）：趴着，影子在身子正下方露一圈；奶奶和凳子在灯的右前方，影子往镜头这边、略往右
      cachedStool ||= originalStoolLayer(),
      { img: G, ...REGISTRATION.G, contact: { a: 0.45, blur: 4, sy: -0.07, skew: 0.5 } }, // Basin, beans, hands and phone are already in the drawings.
    ];
  },
  light: (t) => ({
    ambient: [0.64, 0.67, 0.73],
    lights: [
      { x: 780, y: 60, r: 1500, color: [0.94, 0.97, 1.0], i: 0.32, falloff: 1.4 },
      { x: 300, y: 440, r: 700, color: [0.55, 0.7, 1.0], i: tv(t), falloff: 1.6 },
    ],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  glow: (t) => [{ x: 241, y: 418, r: 70, color: [150, 190, 255], a: 0.25 * tv(t), core: 0.5 }, { x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x, t) => {
    x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = `rgba(110,150,210,${0.25 * tv(t)})`; x.beginPath(); x.roundRect(206, 370, 72, 98, 10); x.fill(); x.restore();
    x.save(); x.translate(FAN[0], FAN[1] + 12); x.scale(1, 0.14);
    for (let k = 0; k < 3; k++) { x.fillStyle = 'rgba(225,215,190,0.18)'; x.beginPath(); x.ellipse(0, 0, 175 - k * 4, 175 - k * 4, 0, 0, 7); x.fill(); }
    x.restore();
    // 蚊香的烟：吊扇的风把它吹斜、吹散
    x.save(); x.lineCap = 'round';
    for (let k = 0; k < 3; k++) {
      x.strokeStyle = `rgba(215,215,220,${0.2 - k * 0.055})`; x.lineWidth = 1 + k * 1.5;
      x.beginPath(); const p0 = [COIL[0] - 20, COIL[1] - 1]; x.moveTo(...p0);
      for (let s = 1; s <= 24; s++) { const u = s / 24; x.lineTo(p0[0] + 45 * u * u + 12 * Math.sin(u * 9 - t * 3 + k) * u, p0[1] - 70 * u); }
      x.stroke();
    }
    x.restore();
  },
  cam: (t) => { const k = t / DURATION; return { x: BW / 2 - 20 * k, y: BH / 2 + 12 * k, fit: 1.0 + 0.04 * k }; },
};
export async function renderFrame(ctx, t, W, H) {
  frameAssets(frameIndex(t));
  const bg = await loadImg('bg_01_room_wide');
  if (!bg) throw new Error('Original S01 background is required; placeholder render refused');
  return renderPaint(ctx, t, W, H, shot);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
