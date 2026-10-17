// S24 · 第 8 场：后台近景，2.5 秒。乌龟咬住鹤嘴之后，小满回过头，得意地看奶奶（合作方画的 anim_24_xiaoman_smug，半身）。
// 和 S20 同一个后台机位方向（东北角往西南），推近到她；人物朝床单，所以图水平翻转——她回头看的方向正对着身后的奶奶。
// 床单上停在 S23 咬住鹤嘴的那一刻（鹤僵住、乌龟叼着不放）。
import { renderShot, billboardM, DEBUG } from '../s06_key.js';
import { sheet as sheet23 } from './s23.js';
import { loadMaps } from '../s08_back.js';
export const DURATION = 2.5;
const CAM = { pos: [3.15, 1.62, 1.12], target: [1.80, 0.62, 0.98], hfov: 46 };
// 半身图：底边中点在世界里离地 0.47 米（头顶约 1.30 米），每厘米 18.4 像素
const SM = { file: 'x24_smug', pos: [1.98, 0.78], ox: 379, oy: 1513, sc: 18.4, z0: 0.47 };
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const mul = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
let MAP = null;
const shot = {
  cam: CAM,
  exp: 0.22,
  sheet: (t, env) => sheet23(3.4 + 0.1 * t, env),
  cards: async (CARDS, cam, t) => {
    MAP ||= await loadMaps(SM.file);
    const base = [SM.pos[0], SM.pos[1], SM.z0], d = cam.project(base)[2];
    // 回头的一下（0～0.35 秒头肩往后转一点，用整张图轻微旋转 + 平移表示），然后得意地点一下头
    const turn = 1 - sstep(0, 0.35, t), nod = 0.02 * Math.sin(Math.PI * sstep(0.9, 1.4, t));
    const a = 0.05 * turn - nod, c = Math.cos(a), s = Math.sin(a), [px, py] = [SM.ox, SM.oy];
    const rot = [c, s, -s, c, px - c * px + s * py, py - s * px - c * py];
    const flip = [-1, 0, 0, 1, 2 * SM.ox, 0];
    CARDS.addImage([{ maps: MAP, m: mul(mul(billboardM(cam, base, SM.ox, SM.oy, SM.sc), flip), rot) }], d);
  },
};
export async function render(ctx, arg, W, H) {
  let t = +arg || 0;
  if (arg && arg.startsWith('{')) { const o = JSON.parse(arg); Object.assign(DEBUG, o); t = o.t ?? 0; }
  return renderShot(ctx, t, W, H, shot);
}
export async function renderFrame(ctx, t, W, H) { return renderShot(ctx, t, W, H, shot); }
