// S01 · 第 1 场：全景，夏夜的堂屋（底图 bg_01_room_wide），日光灯惨白，吊扇转，电视亮着，蚊香的烟往上飘。
// 小满趴在竹席上横握手机打游戏（合作方画的 anim_01_xiaoman_prone_phone，抠图 assets/chars/x01_prone_phone.png），
// 两条小腿翘着一晃一晃；奶奶坐在竹席那头的矮凳上剥毛豆（g01_beans，骨架驱动：js/rig/acts.js 的 grandmaBeans）。镜头慢慢推近。
// 游戏的"跳"声和剥豆声在 audio/build.py。推西瓜那一下放在 S03（奶奶近景）。
import { renderPaint } from '../paintshot.js';
import { loadRig, render as warp } from '../../rig/warp.js';
import { grandmaBeans } from '../../rig/acts.js';
export const DURATION = 12;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const BW = 1672, BH = 941;
export const GM = { x: 905, y: 772, sc: 0.235 };                       // 奶奶（同 S10）
export const XM = { x: 437, y: 509, sc: 0.19 };                        // 小满：图左上角落在底图 (x, y)，头朝右、手肘撑在竹席上
export const COIL = [770, 712];                                        // 蚊香（地上，竹席右头和奶奶之间）
export const FAN = [787, 112];                                         // 吊扇电机（底图）
// 小腿：绕膝盖晃。图像素里的小腿范围（脚和小腿）和膝盖
const LEGS = { poly: [[0, 90], [470, 90], [470, 560], [410, 690], [300, 735], [0, 640]], cut: [[0, 90], [455, 90], [455, 560], [398, 680], [300, 722], [0, 640]], knee: [330, 715] };
let XL = null;
export async function xmLayers() {
  if (XL) return XL;
  const im = await createImageBitmap(await (await fetch('/assets/chars/x01_prone_phone.png')).blob());
  const mk = (keep, cut) => {
    const c = new OffscreenCanvas(im.width, im.height), x = c.getContext('2d');
    if (keep) { x.beginPath(); keep.forEach(([px, py], i) => (i ? x.lineTo(px, py) : x.moveTo(px, py))); x.closePath(); x.clip(); }
    x.drawImage(im, 0, 0);
    if (cut) { x.globalCompositeOperation = 'destination-out'; x.beginPath(); cut.forEach(([px, py], i) => (i ? x.lineTo(px, py) : x.moveTo(px, py))); x.closePath(); x.fill(); }
    return c;
  };
  return (XL = { body: mk(null, LEGS.cut), legs: mk(LEGS.poly, null), w: im.width, h: im.height });
}
export function xiaoman(L, t) {
  const c = new OffscreenCanvas(L.w, L.h), x = c.getContext('2d');
  x.drawImage(L.body, 0, 0);
  const a = 0.07 * Math.sin(t * 2.4) + 0.03 * Math.sin(t * 5.1 + 1);   // 小腿一晃一晃
  x.save(); x.translate(...LEGS.knee); x.rotate(a); x.translate(-LEGS.knee[0], -LEGS.knee[1]); x.drawImage(L.legs, 0, 0); x.restore();
  return c;
}
// 蚊香：绿色的盘香搁在铁架上，头上一点红
function coil() {
  const c = new OffscreenCanvas(120, 60), x = c.getContext('2d');
  x.translate(60, 34); x.scale(1, 0.35);                                      // 直径约 13 厘米 ≈ 底图 40 像素
  x.strokeStyle = '#2f5a35'; x.lineWidth = 3;
  x.beginPath(); for (let a = 0; a < 6 * Math.PI; a += 0.1) { const r = 3 + a * 0.95; x.lineTo(Math.cos(a) * r, Math.sin(a) * r); } x.stroke();
  x.strokeStyle = '#555'; x.lineWidth = 2; x.beginPath(); x.moveTo(-18, 22); x.lineTo(18, 22); x.moveTo(0, 0); x.lineTo(0, 22); x.stroke();
  return c;
}
export const COILC = coil();
// 接触阴影：小满贴在竹席上的身子、手肘，奶奶的鞋和凳子腿（日光灯在头顶，影子软、贴得紧）
export const SHADOWS = (() => {
  const c = new OffscreenCanvas(BW, BH), x = c.getContext('2d');
  x.filter = 'blur(6px)'; x.fillStyle = 'rgba(40,30,20,0.32)';
  for (const [cx, cy, rx, ry] of [[560, 667, 85, 9], [633, 671, 22, 5], [495, 662, 28, 6], [905, 772, 40, 7], [960, 762, 34, 6]]) { x.beginPath(); x.ellipse(cx, cy, rx, ry, 0, 0, 7); x.fill(); }
  return c;
})();
const tv = (t) => 0.3 + 0.12 * Math.sin(t * 3.1) + 0.08 * Math.sin(t * 7.7 + 1) + (Math.sin(t * 1.3) > 0.85 ? 0.15 : 0);
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const L = await xmLayers();
    return [
      { img: SHADOWS, x: 0, y: 0, sc: 1 },
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      { img: xiaoman(L, t), x: XM.x, y: XM.y + 0.6 * Math.sin(t * 1.7), sc: XM.sc },
      { img: warp(await loadRig('g01_beans'), grandmaBeans(t, { looks: [2.6, 8.2] })), x: GM.x, y: GM.y, sc: GM.sc, ox: 304, oy: 1348 },   // 奶奶：骨架驱动剥豆，抬眼看两次小满
    ];
  },
  light: (t) => ({
    ambient: [0.64, 0.67, 0.73],
    lights: [
      { x: 780, y: 60, r: 1500, color: [0.94, 0.97, 1.0], i: 0.32, falloff: 1.4 },                   // 头顶的日光灯
      { x: 300, y: 440, r: 700, color: [0.55, 0.7, 1.0], i: tv(t), falloff: 1.6 },                   // 电视
    ],
    exposure: 1.0, vignette: 0.3, grain: 5,
  }),
  glow: (t) => [{ x: 241, y: 418, r: 70, color: [150, 190, 255], a: 0.25 * tv(t), core: 0.5 }, { x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x, t) => {
    // 电视屏幕的闪光（放着节目）
    x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = `rgba(110,150,210,${0.25 * tv(t)})`; x.beginPath(); x.roundRect(206, 370, 72, 98, 10); x.fill(); x.restore();
    // 吊扇：转得快，只看得见一圈虚影
    x.save(); x.translate(FAN[0], FAN[1] + 12); x.scale(1, 0.14);
    for (let k = 0; k < 3; k++) { x.fillStyle = 'rgba(225,215,190,0.18)'; x.beginPath(); x.ellipse(0, 0, 175 - k * 4, 175 - k * 4, 0, 0, 7); x.fill(); }
    x.restore();
    // 蚊香的烟：一缕往上飘、左右晃、越高越淡
    x.save(); x.lineCap = 'round';
    for (let k = 0; k < 3; k++) {
      x.strokeStyle = `rgba(215,215,220,${0.2 - k * 0.055})`; x.lineWidth = 1 + k * 1.5;
      x.beginPath(); const p0 = [COIL[0] - 20, COIL[1] - 1]; x.moveTo(...p0);
      for (let s = 1; s <= 24; s++) { const u = s / 24; x.lineTo(p0[0] + 10 * Math.sin(u * 7 - t * 1.3 + k) * u + 8 * u, p0[1] - 110 * u); }
      x.stroke();
    }
    x.restore();
  },
  cam: (t) => { const k = sstep(0, 12, t); return { x: BW / 2 - 60 * k, y: BH / 2 + 10 + 25 * k, fit: 1.0 + 0.12 * k }; },
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
