// 2-6 全景（4.5 秒，月光）：小满放下黑了的手机，往右一翻、仰面躺倒，拿手扇两下风，胳膊往席子上一摊，眼睛跟着奶奶；
// 奶奶把盆放到两脚之间的地上，手撑膝盖站起来，转身走到八仙桌边（画面右边），伸手提起桌上的马灯。
// 动作按人体来：骨头长度固定（腿用 IK 接到钉在地上的脚），翻身有中间一张（侧躺、背对镜头），起身是"前倾—离凳—伸直"，
// 转身有正面一张，走路时着地的脚不动、身体往前移。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC } from '../paint/shots/s01.js';
import { key, charLayer, stool, bowl, limbIK, legFK, XM_LEG, EASE } from './kit.js';
import { darkLight, fan } from './s04.js';
import { GM_AT, GM_K, XM_AT, XM_K, xmProne, phoneSide, tableLamp, LAMP_AT } from './s01.js';
export const DURATION = 4.5;
const BW = 1672, BH = 941;
const cl = (v) => Math.min(1, Math.max(0, v));
const seg = (t, a, b, e = 'io') => EASE[e](cl((t - a) / (b - a)));

// ---------------------------------------------------------------- 小满
const T_ROLL = 0.6, T_SIDE = 0.625, T_BACK = 0.69;   // 0.6 起翻；0.625～0.69 侧躺（背对镜头，两帧）；0.69 仰面落地
const PHONE0 = xmProne().phoneAt;
export function xmPhone(t) {             // 手机：0.4 松手掉到席子上，之后就留在那儿（地面坐标）
  const d = seg(t, 0.4, 0.5, 'in');
  return [PHONE0[0] + 2 * d, PHONE0[1] + (-0.8 - PHONE0[1]) * d, PHONE0[2] * (1 - d)];
}
function xiaoman(t) {
  if (t < T_SIDE) {                       // 趴着：0.15 头一低（泄气），0.4 松开手机，0.5 胸口一撑准备翻
    const drop = key(t, [[0.12, 0], [0.32, 1, 'out']]), push = key(t, [[0.48, 0], [0.6, 1, 'out']]), open = seg(t, 0.38, 0.46);
    const P = xmProne({ lean: 1.42 - 0.14 * push, fa: -0.6 + 0.3 * open, hp: open > 0.5 ? 'open' : 'grip',
      head: { tilt: -0.85 - 0.3 * drop + 0.25 * push }, face: { look: [0.8, 0.6 + 0.3 * drop], open: 0.85 - 0.3 * drop, worry: 0.5 * drop, smile: -0.2 * drop } });
    return { view: 'side', P, flip: false };
  }
  if (t < T_BACK) {                       // 侧躺、背对镜头（往自己右边翻，背朝我们）：整个人顺时针转 90°，头朝右
    return { view: 'back', flip: false, rot: Math.PI / 2, pivot: [0, -43.5], to: [-5, -10.5],
      P: { armL: { hand: [-13, -56], hp: 'relax' }, armR: { hand: [13, -57], hp: 'relax' }, legL: { foot: [-6, -4] }, legR: { foot: [3, -6] } } };   // 胳膊顺着身体
  }
  // 仰面躺着（侧面、镜像、顺时针转 90°：头朝右、脸朝上）。人物坐标还是"站着"的那套：+x = 脸朝的方向（落地后朝上），-x = 背（贴着席子）
  const land = key(t, [[T_BACK, 1], [0.78, -0.35, 'out'], [0.9, 0.1, 'io'], [1.0, 0, 'io']]);     // 落地压一下再回弹
  const fanUp = key(t, [[1.3, 0], [1.45, 1, 'out'], [2.0, 1], [2.15, 0, 'in']]);                    // 1.3 抬手扇风，2.15 胳膊摊回席子上
  const flap = t > 1.4 && t < 2.0 ? key(t, [[1.4, 0], [1.55, 1, 'out'], [1.7, 0, 'io'], [1.85, 1, 'out'], [2.0, 0, 'io']]) : 0;
  const rest = [-4, -54], fanAt = [15 - 2 * flap, -88 + 4 * flap];
  const hN = [rest[0] + (fanAt[0] - rest[0]) * fanUp, rest[1] + (fanAt[1] - rest[1]) * fanUp];
  const legs = {};
  for (const [sd, hip, a1, a2] of [['N', XM_LEG.hipN, Math.PI / 2 + 0.07, Math.PI / 2 + 0.1], ['F', XM_LEG.hipF, Math.PI / 2 + 0.03, Math.PI / 2 + 0.12]]) {
    const r = legFK(hip, a1, a2, XM_LEG.thigh, XM_LEG.shin); legs['leg' + sd] = { knee: r.knee, foot: r.foot, footRot: -0.25 };
  }
  const look = t < 2.6 ? [0.3, -0.5] : key(t, [[2.6, [0.3, -0.5]], [2.85, [-0.7, -0.6], 'out']]);    // 2.6 听见奶奶的脚步，眼睛往头顶那边（奶奶走去的方向）瞟
  return { view: 'side', flip: true, rot: Math.PI / 2, pivot: [-1, -43.5], to: [1, -6.6 + 1.2 * Math.max(0, -land)],
    P: { head: { tilt: 0.5 - 0.15 * Math.max(0, land) }, breath: 0.8 * seg(t, 0.95, 1.25, 'sine') * (1 - seg(t, 1.25, 1.6)),
      ...legs,
      armN: { hand: hN, hp: fanUp > 0.3 ? 'open' : 'relax', rot: fanUp > 0.3 ? -0.6 + 1.0 * flap : 0 }, armF: { hand: [5, -58], hp: 'relax' },
      face: { open: fanUp > 0.3 ? 0.4 : 0.55, look, mouth: t < 1.25 ? 0.35 * seg(t, 0.9, 1.0) : 0.15, smile: -0.25, worry: 0.45 } } };
}

// ---------------------------------------------------------------- 奶奶
// 坐着时 pose.y = 37（髋往下挪 37 厘米坐到凳上）。脚钉在地上：地面坐标 (29, -4.6)（远）和 (33, -4.6)（近）——镜像坐标，+x = 她面朝的画面左边。
const GL = 35.5, FEET0 = { N: [33, -4.6], F: [29, -4.6] }, HIP = { N: [0, -75], F: [-3, -75] };
const BOWL0 = [24, -47], BOWL1 = [36, -3.3];                       // 盆：腿上 → 两脚之间的地上（盆沿中心，地面坐标；坐矮凳的老人放盆就放在脚边）
const T_TURN0 = 1.84, T_TURN1 = 1.96, WALK0 = 1.98, STEP = 0.45, SL = 25.5;
const HANDLE = [(LAMP_AT[0] - GM_AT[0]) / GM_K, (LAMP_AT[1] - 117 - GM_AT[1]) / GM_K];   // 桌上马灯提梁顶（奶奶的地面坐标，不镜像）
function legsTo(P, feet) {           // feet：地面坐标 → 人物坐标里的脚，膝盖用 IK（朝前），骨长固定
  const o = {};
  for (const sd of ['N', 'F']) {
    const f = [feet[sd][0] - (P.x || 0), feet[sd][1] - (P.y || 0)], r = limbIK(HIP[sd], f, GL, GL, 1);
    o['leg' + sd] = { knee: r.joint, foot: r.end };
  }
  return o;
}
export function grandmaS07(t) {
  // 检查：手是不是真碰到盆/膝盖（够不着时 IK 会让手停在半空）——见 checkReach()
  if (t < T_TURN0) {
    // 1) 0.2～0.75 前倾，两手端盆放到脚前的地上；2) 0.75～0.95 手撑到膝盖上；3) 0.95～1.6 起身：先往前移重心、屁股离凳，再往上伸直
    const bend = key(t, [[0.2, 0.3], [0.72, 1.25], [0.95, 0.85], [1.12, 0.9], [1.6, 0.14], [1.8, 0.1]]);
    const fwd = key(t, [[0.95, 0], [1.2, 0.45, 'in'], [1.6, 1, 'out']]), upk = key(t, [[1.05, 0], [1.6, 1, 'io']]);
    const P = { x: 27 * fwd, y: 37 * (1 - upk), lean: bend, head: { nod: 0.2 - 0.25 * seg(t, 0.2, 0.7) + 0.2 * seg(t, 1.3, 1.7), tilt: 0 } };
    Object.assign(P, legsTo(P, FEET0));
    const carry = seg(t, 0.2, 0.72), B = [BOWL0[0] + (BOWL1[0] - BOWL0[0]) * carry, BOWL0[1] + (BOWL1[1] - BOWL0[1]) * EASE.in(carry)];
    const toKnee = seg(t, 0.75, 0.95);
    const kn = (sd) => [P['leg' + sd].knee[0] - 3, P['leg' + sd].knee[1] - 5];   // 手掌按在膝盖上面一点
    const onBowl = { N: [B[0] - 2 - P.x, B[1] - 1.5 - P.y], F: [B[0] + 3 - P.x, B[1] - 2 - P.y] };
    const leave = seg(t, 1.28, 1.5);                                                   // 腿快伸直时手离开膝盖，垂到身边
    const hand = (sd) => {
      const a = t < 0.75 ? onBowl[sd] : [onBowl[sd][0] + (kn(sd)[0] - onBowl[sd][0]) * toKnee, onBowl[sd][1] + (kn(sd)[1] - onBowl[sd][1]) * toKnee];
      const side = sd === 'N' ? [5, -64] : [1, -65];
      return t < 1.28 ? a : [kn(sd)[0] + (side[0] - kn(sd)[0]) * leave, kn(sd)[1] + (side[1] - kn(sd)[1]) * leave];
    };
    P.armN = { hand: hand('N'), hp: t < 0.75 ? 'grip' : 'relax' }; P.armF = { hand: hand('F'), hp: t < 0.75 ? 'grip' : 'relax' };
    P.face = { look: [0.5, t < 0.9 ? 0.6 : 0.1], open: 0.85, worry: 0.3 * seg(t, 1.0, 1.15) * (1 - seg(t, 1.5, 1.7)), smile: 0.1 };
    return { view: 'side', flip: true, P, bowl: t < 0.72 ? B : BOWL1, bowlFront: t < 0.72 };   // 端着时盆在身前，放下后在两脚之间（画在人后面）
  }
  if (t < T_TURN1) {                   // 转身：正面一张（脚尖朝镜头，头已经转向画面右边）
    const P = { x: 29, y: 0, head: { turn: 0.45, nod: 0.15 }, legL: { foot: [-4.4, -4.6] }, legR: { foot: [4.4, -4.6] }, face: { look: [-0.6, 0.1], open: 0.9, smile: 0.1 } };
    return { view: 'front', flip: true, P, bowl: BOWL1 };
  }
  // 走：画面右边 = 不镜像时的 +x。起点两脚在 -29 一带；四步、每步 0.45 秒、步长 25.5 厘米，着地的脚不动；第五步收脚站定在八仙桌左边，
  // 然后探身伸手抓桌上马灯的提梁（4.3 抓住，4.4 提起一点）——下一镜 S08 她已经坐在桌边点灯。
  const w = Math.max(0, t - WALK0), k = w / STEP;
  const land = (i) => -29 + SL * i, KEND = 4.7, XEND = 71.5;                               // 第 i 步落脚点（单数近脚、双数远脚）；第五步收脚，站在桌子左边、不挡到桌子
  const body4 = -29 + SL * (4 + (Math.exp(-8) - 1) / 2);
  let bodyX;
  if (k <= 4) bodyX = -29 + SL * (k + (Math.exp(-2 * k) - 1) / 2);                      // 起步速度为 0，慢慢走起来
  else { const q = cl((k - 4) / (KEND - 4)), d = KEND - 4, v0 = SL * d; bodyX = body4 * (2 * q ** 3 - 3 * q ** 2 + 1) + v0 * (q ** 3 - 2 * q ** 2 + q) + XEND * (-2 * q ** 3 + 3 * q ** 2); }   // 最后一步减速停住
  const feet = {};
  for (const sd of ['N', 'F']) {
    let x = sd === 'N' ? -27 : -31, lift = 0;                                            // 转过身以后两脚的位置（跟正面那张对上）
    const steps = sd === 'N' ? [[1, 0, 1], [3, 2, 3], [5, 4, KEND]] : [[2, 1, 2], [4, 3, 4]];   // [第几步, 起, 止]（以步为单位）
    for (const [i, k0, k1] of steps) {
      const to = i === 5 ? XEND - 1 : land(i);
      if (k >= k1) x = to;
      else if (k > k0) { const u = (k - k0) / (k1 - k0); x = x + (to - x) * EASE.io(u); lift = (i === 5 ? 2.5 : 4) * Math.sin(Math.PI * u); }
    }
    feet[sd] = [x, -4.6 - lift];
  }
  const ph = k < 4 ? k - Math.floor(k) : cl((k - 4) / (KEND - 4));
  const bob = k < KEND ? 1.4 + 1.0 * Math.abs(Math.cos(Math.PI * ph)) : 1.0;              // 两脚都着地时髋最低
  const reach = seg(t, 3.95, 4.3), grab = t >= 4.3, up = seg(t, 4.35, 4.5, 'out');
  const P = { x: bodyX, y: bob, lean: 0.12 + 0.32 * reach, head: { nod: 0.15 + 0.2 * reach }, face: { look: [0.6, 0.1 + 0.4 * reach], open: 0.9, smile: 0.1 } };
  Object.assign(P, legsTo(P, feet));
  const sw = k < KEND ? Math.sin(Math.PI * k) * (1 - seg(k, 4, KEND)) : 0;                 // 胳膊和腿反着摆，幅度小，停步时收住
  const handle = [HANDLE[0] - P.x, HANDLE[1] - up * 1.5 - P.y], hang = [6 - 5 * sw, -63];
  P.armN = { hand: [hang[0] + (handle[0] - hang[0]) * reach, hang[1] + (handle[1] - hang[1]) * reach], hp: grab ? 'grip' : reach > 0.5 ? 'open' : 'relax' };
  P.armF = { hand: [3 + 5 * sw, -64], hp: 'relax' };
  return { view: 'side', flip: false, P, bowl: BOWL1, lampLift: up * 1.5 * GM_K };
}

const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const X = xiaoman(t), G = grandmaS07(t), ph = xmPhone(t);
    return [
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      tableLamp(G.lampLift || 0),
      charLayer('x', X.view, X.P, { box: [400, 520, 760, 690], k: XM_K, at: XM_AT, flip: X.flip, rot: X.rot || 0, pivot: X.pivot, to: X.to,
        before: (x) => { if (X.flip) x.scale(-1, 1); phoneSide(x, ph, 0); } }),
      charLayer('n', G.view, G.P, { box: [760, 380, 1300, 790], k: GM_K, at: GM_AT, flip: G.flip,
        before: (x) => { if (!G.flip) x.scale(-1, 1); stool(x, -2); if (!G.bowlFront) bowl(x, G.bowl[0], G.bowl[1], 26); },
        after: (x) => { if (!G.flip) x.scale(-1, 1); if (G.bowlFront) bowl(x, G.bowl[0], G.bowl[1], 26); } }),
    ];
  },
  light: (t) => darkLight(t, 0),
  glow: () => [{ x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x) => fan(x, 0),
  cam: () => ({ x: BW / 2 - 20, y: BH / 2 + 12, fit: 1.04 }),
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
