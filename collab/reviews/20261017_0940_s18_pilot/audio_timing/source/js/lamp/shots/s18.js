// S18 · 第 7 场：小满"噗"地笑出声，捂住嘴。镜头推近到她（床单正面这一侧），床单上还是 S17 结尾：鹤晕乎乎地缓过来，乌龟探出头偷笑。
// 前 0.42 秒她还是"看呆了"（松开胳膊、张着嘴，xm_rig 的 B）；"噗"——换成合作方画的捂嘴笑（anim_18，和 B 同一个裁切框、逐像素对齐），
// 肩膀一耸，然后笑得一颤一颤，慢慢收住。
import { makeShot } from './shotkit.js';
import { sheet as sheet17 } from './s17.js';
import { cards06, billboardM, XM } from '../s06_key.js';
import { RIG16, loadRig, layers16, pose16 } from '../xm_rig.js';
import { loadFlip, frameAt, flipMaps } from '../../rig/flipbook.js';
// 逐帧版（合作方按关键帧单出的 x18_f01…f12，assets/flips/x18_laugh.flip.json）到了就用，整段 3 秒都按关键帧换；没到时退回旧的单张图
let FLIP;
async function flip() { if (FLIP === undefined) { try { FLIP = await loadFlip('x18_laugh'); } catch { FLIP = null; } } return FLIP; }
export const DURATION = 3;
const T_PU = 0.42;                                     // "噗"
const CAM = { pos: [1.05, -2.70, 0.55], target: [0.42, -1.2, 0.70], hfov: 40 };
let LAUGH = null;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const sheet = (t, env) => sheet17(13.6 + 0.3 * t, env);
async function cards(CARDS, cam, t) {
  const F = await flip();
  if (F) {   // 逐帧：关键帧和母版同画幅，用同一个摆放矩阵；动作全在画里，不再整张伸缩
    const R = RIG16, c0 = cam.project([XM.p[0], XM.p[1], XM.seat]);
    const base = [XM.p[0], XM.p[1], (R.floorY - R.oy) / R.sc / 100];
    CARDS.addImage([{ maps: flipMaps(F, frameAt(F, t)), m: billboardM(cam, base, R.ox, R.oy, R.sc) }], c0[2]);
    return;
  }
  if (t < T_PU) return cards06(CARDS, cam, 3.0 + t);   // 第 6 场之后的 B 状态
  LAUGH ||= (await loadRig({ files: { L: 'x18_laugh' } })).L;
  const R = RIG16, u = t - T_PU;
  const c0 = cam.project([XM.p[0], XM.p[1], XM.seat]), depth = c0[2];
  const base = [XM.p[0], XM.p[1], (R.floorY - R.oy) / R.sc / 100];
  // 笑：一耸（0.1 秒里往上 1.5%），然后一颤一颤（6.5 次/秒，慢慢变小），身子往前点一点
  const jolt = Math.sin(Math.PI * Math.min(1, u / 0.16)) * (u < 0.16 ? 1 : 0);
  const shake = Math.sin(u * 6.5 * 2 * Math.PI) * Math.exp(-u * 1.1) * sstep(0.1, 0.25, u);
  const sy = 1 + 0.015 * jolt + 0.006 * shake;
  const lean = 0.012 * sstep(0, 0.4, u) * (1 - 0.6 * sstep(1.6, 2.5, u)) + 0.004 * shake;
  const m0 = billboardM(cam, base, R.ox, R.oy, R.sc);
  const mul = (a, b) => [a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1], a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3], a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5]];
  const [px, py] = [R.ox, R.oy], c = Math.cos(lean), s = Math.sin(lean);
  const rot = [c, s, -s, c, px - c * px + s * py, py - s * px - c * py];      // 绕凳面转（往前倾）
  const squash = [1, 0, 0, sy, 0, R.oy * (1 - sy)];
  CARDS.addImage([{ maps: LAUGH, m: mul(m0, mul(rot, squash)) }], depth);
}
export const { render, renderFrame } = makeShot({ sheet, cards, cam: CAM });
