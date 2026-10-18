// 2-6 全景（3.5 秒，月光）：0.3 小满撑起来又往后一倒，瘫在竹席上，1.5 用手扇风（扇两下）；
// 奶奶 1.0 把盆放到地上、站起来，2.2 朝立柜走过去（往画面右边，出画前切）。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC } from '../paint/shots/s01.js';
import { key, charLayer, stool, bowl } from './kit.js';
import { grandmaStop, darkLight, fan } from './s04.js';
import { GM_AT, GM_K, XM_AT, XM_K } from './s01.js';
export const DURATION = 3.5;
const BW = 1672, BH = 941;
function xiaoman(t) {
  const up = key(t, [[0.25, 0], [0.5, 1, 'out']]), back = key(t, [[0.5, 0], [0.85, 1, 'in']]);
  const lean = 1.2 - 0.8 * up - 1.85 * back;                    // 趴 → 撑起 → 仰面倒下
  const wave = t > 1.5 && t < 2.9 ? Math.sin((t - 1.5) * Math.PI * 2 / 0.7) : 0;
  const legs = back > 0.5 ? { legN: { foot: [20, -37.5], knee: [10, -46] }, legF: { foot: [16, -37.5], knee: [8, -47] } }
    : { legN: { foot: [-36, -64], knee: [-21, -42] }, legF: { foot: [-28, -68], knee: [-21, -43] } };
  return { y: 36, lean, head: { tilt: -0.9 * (1 - back) + 0.3 * back }, ...legs,
    armN: back > 0.5 ? { hand: [6 + 6 * wave, -84 + 4 * Math.abs(wave)], hp: 'open' } : { elbow: [36, -37.5], hand: [49, -50], hp: 'grip' },
    armF: back > 0.5 ? { hand: [-14, -60], hp: 'relax' } : { elbow: [33, -38], hand: [47, -51], hp: 'grip' },
    face: back > 0.5 ? { open: 0.6, look: [0.3, -0.4], mouth: 0.25, smile: -0.2, worry: 0.4 } : { open: 0.85, look: [0.8, 0.6] } };
}
function grandma(t) {
  const P0 = grandmaStop(1.5);
  const stand = key(t, [[1.1, 0], [1.75, 1, 'io']]);
  const walk = Math.max(0, t - 2.2), ph = walk * Math.PI * 2 / 0.9;
  const fN = [8 + 10 * Math.sin(ph), -4.6 - 3 * Math.max(0, Math.cos(ph))], fF = [8 - 10 * Math.sin(ph), -4.6 - 3 * Math.max(0, -Math.cos(ph))];
  if (stand < 1) return { ...P0, y: 37 * (1 - stand), seated: stand < 0.5, lean: 0.3 + 0.2 * Math.sin(Math.PI * stand), head: { nod: -0.2 + 0.5 * stand }, face: { look: [0.6, 0], open: 0.9 },
    armN: { hand: [20, -70 + 10 * stand], hp: 'relax' }, armF: { hand: [16, -70 + 8 * stand], hp: 'relax' } };
  return { y: 0, seated: false, lean: 0.12, head: { nod: 0.1 }, face: { look: [0.6, 0], open: 0.9 }, legN: { foot: fN }, legF: { foot: fF }, armN: { hand: [10 - 6 * Math.sin(ph), -65], hp: 'relax' }, armF: { hand: [6 + 6 * Math.sin(ph), -66], hp: 'relax' } };
}
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const gx = GM_AT[0] + 55 * GM_K * Math.max(0, t - 2.2);
    return [
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      charLayer('x', 'side', xiaoman(t), { box: [400, 520, 760, 690], k: XM_K, at: XM_AT }),
      charLayer('n', 'side', grandma(t), { box: [760, 380, 1300, 790], k: GM_K, at: [gx, GM_AT[1]], flip: t < 1.9,
        before: (x) => stool(x, t < 1.9 ? -2 : (GM_AT[0] - gx) / GM_K - 2), after: (x) => bowl(x, t < 1.0 ? 24 : 30 - (gx - GM_AT[0]) / GM_K * (t < 1.9 ? 1 : -1), t < 1.0 ? -47 : -6, 26) }),
    ];
  },
  light: (t) => darkLight(t, 0),
  glow: () => [{ x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x) => fan(x, 0),
  cam: () => ({ x: BW / 2 - 20, y: BH / 2 + 12, fit: 1.04 }),
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
