// 2-6（4.5 秒，月光）：全景放手机 → 0.66 奶奶落盆/压膝起身近景
// → 1.62 小满仰躺扇风/瞟奶奶近景 → 2.35 回全景，走向桌边先扣梁再提灯。
// 翻身与奶奶转身在画外发生；镜内切镜避开未通过的换面，不宣称连续转体已修好。
// 同一全局动作时间、同一场景光照；保留压膝、腿与第一步支撑、握梁后提灯。
import { renderPaint } from '../paint/paintshot.js';
import { COIL, COILC } from '../paint/shots/s01.js';
import { key, charLayer, stool, bowl, limbIK, legFK, XM_LEG, EASE, armSide, shoulderSide, ARM } from './kit.js';
import { darkLight, fan } from './s04.js';
import { GM_AT, GM_K, XM_AT, XM_K, xmProne, phoneSide, tableLamp, LAMP_AT, LAMP_S } from './s01.js';
import * as NAINAI from '../chars/nainai.js';
import * as XIAOMAN from '../chars/xiaoman.js';
import { Figure, tube } from '../lib/figure.js';
export const DURATION = 4.5;
const BW = 1672, BH = 941;
const cl = (v) => Math.min(1, Math.max(0, v));
const seg = (t, a, b, e = 'io') => EASE[e](cl((t - a) / (b - a)));

// ---------------------------------------------------------------- 小满
const T_ROLL = .48, T_FLAT = .72, T_BACK = 1.08;
const PHONE0 = xmProne().phoneAt;
export function xmPhone(t) {             // 手机：0.4 松手掉到席子上，之后就留在那儿（地面坐标）
  const d = seg(t, 0.4, 0.5, 'in');
  return [PHONE0[0] + 2 * d, PHONE0[1] + (-0.8 - PHONE0[1]) * d, PHONE0[2] * (1 - d)];
}
export function xiaomanS07(t) {
  if (t < T_ROLL) {                       // 趴着：0.15 头一低（泄气），0.4 松开手机，0.5 胸口一撑准备翻
    const drop = key(t, [[0.12, 0], [0.32, 1, 'out']]), push = key(t, [[0.48, 0], [0.6, 1, 'out']]), open = seg(t, 0.38, 0.46);
    const P = xmProne({ lean: 1.42 - 0.14 * push, fa: -0.6 + 0.3 * open, hp: open > 0.5 ? 'open' : 'grip',
      head: { tilt: -0.85 - 0.3 * drop + 0.25 * push }, face: { look: [0.8, 0.6 + 0.3 * drop], open: 0.85 - 0.3 * drop, worry: 0.5 * drop, smile: -0.2 * drop } });
    return { view: 'side', P, flip: false };
  }
  if (t < T_BACK) return xiaomanRoll(t);
  // 仰面躺着（侧面、镜像、顺时针转 90°：头朝右、脸朝上）。人物坐标还是"站着"的那套：+x = 脸朝的方向（落地后朝上），-x = 背（贴着席子）
  // 1.08 已落稳；沿用同一地面裁剪，不能在滚完一帧后突然露出穿地裙摆。
  const fanUp = key(t, [[1.3, 0], [1.45, 1, 'out'], [2.0, 1], [2.15, 0, 'in']]);                    // 1.3 抬手扇风，2.15 胳膊摊回席子上
  const flap = t > 1.4 && t < 2.0 ? key(t, [[1.4, 0], [1.55, 1, 'out'], [1.7, 0, 'io'], [1.85, 1, 'out'], [2.0, 0, 'io']]) : 0;
  const rest = [-4, -54], fanAt = [15 - 2 * flap, -88 + 4 * flap];
  const hN = [rest[0] + (fanAt[0] - rest[0]) * fanUp, rest[1] + (fanAt[1] - rest[1]) * fanUp];
  const legs = {};
  for (const [sd, hip, a1, a2] of [['N', XM_LEG.hipN, Math.PI / 2 + 0.07, Math.PI / 2 + 0.1], ['F', XM_LEG.hipF, Math.PI / 2 + 0.03, Math.PI / 2 + 0.12]]) {
    const r = legFK(hip, a1, a2, XM_LEG.thigh, XM_LEG.shin); legs['leg' + sd] = { knee: r.knee, foot: r.foot, footRot: -0.25 };
  }
  const glance = key(t, [[1.82, 0], [1.96, 1, 'out'], [2.08, 1], [2.24, 0, 'io']]);
  // eye() offsets are in body coordinates. In this mirrored, 90° supine view
  // (+look.x, -look.y) moves the drawn iris screen-right/up, toward grandma.
  const look = mix([0.3, -0.5], [1, -1], glance); // one glance, then return to rest
  return { view: 'roll', roll: Math.PI, rot: Math.PI / 2, pivot: [-1, -43.5], to: [-1, -6.6],
    support: { floorY: 0, hipX: -1, shoulderX: 33, clip: true },
    P: { head: { tilt: 0.5 }, breath: 0.8 * seg(t, 0.95, 1.25, 'sine') * (1 - seg(t, 1.25, 1.6)),
      ...legs,
      armN: { hand: hN, hp: fanUp > 0.3 ? 'open' : 'relax', rot: fanUp > 0.3 ? -0.6 + 1.0 * flap : 0 }, armF: { hand: [5, -58], hp: 'relax' },
      face: { open: fanUp > 0.3 ? 0.4 : 0.55, look, mouth: t < 1.25 ? 0.35 * seg(t, 0.9, 1.0) : 0.15, smile: -0.25, worry: 0.45 } } };
}

// Lower onto one shoulder/hip before rolling about the head-to-foot axis.
// In-plane flexion is FK; the roll is a transverse cos projection. A narrow
// back surface replaces the occluded side surface at quarter-turn, with a ground clip and
// a fixed hip x support. It is not a rotated, full-width standing back drawing.
const shortest = (a, b, u) => a + Math.atan2(Math.sin(b - a), Math.cos(b - a)) * u;
export function xiaomanRoll(t) {
  const flat = seg(t, T_ROLL, T_FLAT), settle = seg(t, .98, T_BACK), turn = seg(t, .64, T_BACK);
  const start = xmProne({ lean: 1.42, fa: -.3, hp: 'open', head: { tilt: -1.15 } });
  const P = { lean: 1.42 * (1 - flat), head: { tilt: -1.15 + 1.65 * seg(t, .52, T_BACK) },
    breath: .8 * seg(t, .95, 1.25, 'sine') * (1 - seg(t, 1.25, 1.6)),
    face: { open: .55, look: [.3, -.5], mouth: .35 * seg(t, .9, 1), smile: -.25, worry: .45 } };
  for (const [sd, hip, endA, endB, shin] of [['N', XM_LEG.hipN, Math.PI / 2 + .07, Math.PI / 2 + .1, -2.25], ['F', XM_LEG.hipF, Math.PI / 2 + .03, Math.PI / 2 + .12, -2.35]]) {
    const a = shortest(Math.PI - .2, endA, flat), b = shortest(shin, endB, flat);
    const leg = legFK(hip, a, b, XM_LEG.thigh, XM_LEG.shin);
    P['leg' + sd] = { ...leg, footRot: shortest(shin - Math.PI / 2 + .9, -.25, flat) };
    const S0 = shoulderSide('x', start, sd), A0 = start['arm' + sd], S = shoulderSide('x', P, sd);
    const end = armSide('x', {}, sd, sd === 'N' ? [-4, -54] : [5, -58]);
    const ua = shortest(Math.atan2(A0.elbow[1] - S0[1], A0.elbow[0] - S0[0]), Math.atan2(end.E[1] - end.S[1], end.E[0] - end.S[0]), flat);
    const fa = shortest(Math.atan2(A0.hand[1] - A0.elbow[1], A0.hand[0] - A0.elbow[0]), end.dir, flat);
    const E = [S[0] + ARM.x[0] * Math.cos(ua), S[1] + ARM.x[0] * Math.sin(ua)];
    P['arm' + sd] = { elbow: E, hand: [E[0] + ARM.x[1] * Math.cos(fa), E[1] + ARM.x[1] * Math.sin(fa)], hp: t < .58 ? 'open' : 'relax' };
  }
  return { view: 'roll', P, roll: Math.PI * turn, rot: Math.PI / 2 * flat,
    pivot: [-1, -43.5], to: [-1, -7.5 + .9 * settle],
    support: { floorY: 0, hipX: -1, shoulderX: 33, clip: true } };
}
function rollView(X) {
  const cs = Math.cos(X.roll);
  // Switch the visible surface while the back occludes the face. The side
  // surface is never squeezed through zero width and no second face is blended.
  return Math.abs(cs) >= .66 ? { view: 'side', scaleX: cs } : { view: 'back', scaleX: .6 };
}
function xiaomanHeadCenter(P) {
  const lean = P.lean || 0, n = rot([1.6, -39.9], lean), h = rot([-1, -13.6], lean + P.head.tilt + (P.head.nod || 0) * .12);
  return [-1 + n[0] + h[0], -43.5 + n[1] + h[1]];
}
function rollSprite(X) {
  const choice = rollView(X), o = canvasLayer([400, 520, 760, 690], XM_K, XM_AT), c = o.x;
  c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
  c.beginPath(); c.rect(-200, -200, 400, 200); c.clip();
  const P = choice.view === 'side' ? X.P : { head: { tilt: X.P.head.tilt },
    legL: { foot: [-4.9, -3.7] }, legR: { foot: [4.9, -3.7] },
    armL: { hand: [-13, -56], hp: 'relax' }, armR: { hand: [13, -57], hp: 'relax' } };
  const drawing = XIAOMAN.draw(c, choice.view, P), head = drawing.H([0, 0]);
  c.save(); c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, o.c.width, o.c.height); c.restore();
  let shear = 0, sy = 1;
  if (choice.view === 'back') {
    // Align the replacement surface to the same hip/head landmarks. Keep its
    // finite width, rather than flattening the whole body into a paper edge.
    const target = xiaomanHeadCenter(X.P), span = head[1] - X.pivot[1];
    shear = (Math.cos(X.roll) * (target[0] - X.pivot[0]) - choice.scaleX * head[0]) / span;
    sy = (target[1] - X.pivot[1]) / span;
  }
  c.translate(...X.to); c.rotate(X.rot); c.transform(choice.scaleX, 0, shear, sy, 0, 0);
  c.translate(choice.view === 'side' ? -X.pivot[0] : 0, -X.pivot[1]);
  drawing.fig.draw();
  return { canvas: o.c, figure: drawing.fig, head, choice };
}
function rollingLayer(X, ph) {
  const out = canvasLayer([400, 520, 760, 690], XM_K, XM_AT), x = out.x;
  phoneSide(x, ph, 0);
  x.fillStyle = 'rgba(25,20,18,.12)'; x.beginPath(); x.ellipse(16, -.2, 23, 1.2, 0, 0, Math.PI * 2); x.fill();
  const sprite = rollSprite(X);
  x.save(); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.drawImage(sprite.canvas, 0, 0); x.restore();
  return out.layer;
}

// ---------------------------------------------------------------- 奶奶
// 坐姿由 y=37 开始；先各自抬脚收回 9cm，再以 (24,-4.6)/(20,-4.6) 支撑起身。镜像 +x 朝画面左。
const GL = 35.5, HIP = { N: [0, -75], F: [-3, -75] };
const BOWL0 = [24, -47], BOWL1 = [48, -3.3];                       // 盆沿中心：膝上 → 鞋前外侧；落盆后鞋底外沿仍留 1.8cm 轮廓前间隙
const T_TURN0 = 1.62, T_TURN1 = 1.98, WALK0 = 1.98, STEP = 0.45, SL = 25.5;
const HANDLE = [(LAMP_AT[0] - GM_AT[0]) / GM_K, (LAMP_AT[1] - 690 * LAMP_S - GM_AT[1]) / GM_K];   // 桌上马灯提梁顶（奶奶的地面坐标，不镜像）
function legsTo(P, feet) {           // feet：地面坐标 → 人物坐标里的脚，膝盖用 IK（朝前），骨长固定
  const o = {};
  for (const sd of ['N', 'F']) {
    const f = [feet[sd][0] - (P.x || 0), feet[sd][1] - (P.y || 0)], r = limbIK(HIP[sd], f, GL, GL, 1);
    o['leg' + sd] = { knee: r.joint, foot: r.end };
  }
  return o;
}
// The hand API takes a wrist, not a contact point. Keep the actual hand-local
// anchor on its target and solve the wrist first; then compensate the IK forearm
// angle. [0.82, 0.02] is hand.js's closed-hand grip, in palm-length units.
const mix = (a, b, q) => a.map((v, i) => v + (b[i] - v) * q);
const rot = (p, a) => [p[0] * Math.cos(a) - p[1] * Math.sin(a), p[0] * Math.sin(a) + p[1] * Math.cos(a)];
function contactArm(P, sd, target, angle, hp, anchor = [.82 * 5.4, .02 * 5.4]) {
  const off = rot(anchor, angle), wrist = [target[0] - off[0], target[1] - off[1]];
  const a = armSide('n', P, sd, wrist);
  return { hand: wrist, rot: angle - a.dir, hp };
}
function seatedFeet(t) {
  const feet = {};
  for (const [sd, x, a, b] of [['N', 33, .28, .44], ['F', 29, .46, .62]]) {
    const u = cl((t - a) / (b - a));
    feet[sd] = [x - 9 * EASE.io(u), -4.6 - 1.8 * Math.sin(Math.PI * u)];
  }
  return feet;
}
export function grandmaS07(t) {
  // 接触使用手轮廓锚点，结构测试核对实际 IK 端点，不拿请求腕点冒充接触。
  if (t < T_TURN0) {
    // 0.2–0.72 放盆；0.72–0.92 手回膝；0.95 移重，1.05 离凳，1.6 伸直。
    const bend = key(t, [[0.2, 0.3], [0.72, 1.25], [0.95, 0.72], [1.12, 0.78], [1.6, 0.1]]);
    const fwd = key(t, [[0.95, 0], [1.2, 0.45, 'in'], [1.6, 1, 'out']]), upk = key(t, [[1.05, 0], [1.6, 1, 'io']]);
    const P = { x: 22 * fwd, y: 37 * (1 - upk), lean: bend, head: { nod: 0.2 - 0.25 * seg(t, 0.2, 0.7) + 0.2 * seg(t, 1.3, 1.7), tilt: 0 } };
    Object.assign(P, legsTo(P, seatedFeet(t)));
    const carry = seg(t, 0.2, 0.72), B = [BOWL0[0] + (BOWL1[0] - BOWL0[0]) * carry, BOWL0[1] + (BOWL1[1] - BOWL0[1]) * EASE.in(carry)];
    const toKnee = seg(t, 0.72, 0.92);
    // Place the lower palm surface on the knee cap; a wrist at the knee makes
    // the fingers point up toward the chin. Palm orientation stays horizontal.
    const kn = (sd) => [P['leg' + sd].knee[0], P['leg' + sd].knee[1] - 5.2];
    const onBowl = { N: [B[0] - 10 - P.x, B[1] - .7 - P.y], F: [B[0] - 7 - P.x, B[1] - 2 - P.y] };
    const leave = seg(t, 1.28, 1.5);
    for (const sd of ['N', 'F']) {
      const target = mix(onBowl[sd], kn(sd), toKnee);
      const contact = contactArm(P, sd, target, 0, t < .72 ? 'grip' : 'relax', [.6 * 5.4, .33 * 5.4]);
      const hang = sd === 'N' ? [5, -64] : [1, -65];
      const wrist = mix(contact.hand, hang, leave), a = armSide('n', P, sd, wrist);
      P['arm' + sd] = { hand: wrist, rot: -a.dir * (1 - leave), hp: t < .72 ? 'grip' : 'relax' };
    }
    P.face = { look: [0.5, t < 0.9 ? 0.6 : 0.1], open: 0.85, worry: 0.3 * seg(t, 1.0, 1.15) * (1 - seg(t, 1.5, 1.7)), smile: 0.1 };
    return { view: 'side', flip: true, P, bowl: t < 0.72 ? B : BOWL1, bowlFront: t < 0.72 };   // 盆落在鞋前外侧，落地后保持世界坐标
  }
  if (t < T_TURN1) return grandmaTurn(t);
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
  const grasp = contactArm(P, 'N', handle, -.42, grab ? 'grip' : 'open');
  const wrist = mix(hang, grasp.hand, reach), a = armSide('n', P, 'N', wrist);
  P.armN = { hand: wrist, rot: (-.42 - a.dir) * reach, hp: grab ? 'grip' : reach > .5 ? 'open' : 'relax' };
  P.armF = { hand: [3 + 5 * sw, -64], hp: 'relax' };
  return { view: 'side', flip: false, P, bowl: BOWL1, lampLift: up * 1.5 * GM_K };
}

// A local 2.5-D turn: both feet and the pelvis share one world-space rig. The
// original front pants ignore knee inputs, so this shot draws fixed-length legs
// itself and reuses only the existing upper-body art. No shared character edits.
const v3 = {
  add: (a, b) => a.map((v, i) => v + b[i]),
  sub: (a, b) => a.map((v, i) => v - b[i]),
  scale: (a, s) => a.map(v => v * s),
  dot: (a, b) => a.reduce((s, v, i) => s + v * b[i], 0),
};
function knee3(hip, foot, yaw) {
  const d = v3.sub(foot, hip), len = Math.hypot(...d), unit = v3.scale(d, 1 / len);
  const forward = [Math.cos(yaw), 0, Math.sin(yaw)];
  const plane = v3.sub(forward, v3.scale(unit, v3.dot(unit, forward)));
  const bend = v3.scale(plane, Math.sqrt(Math.max(0, GL * GL - len * len / 4)) / Math.hypot(...plane));
  return v3.add(v3.add(hip, v3.scale(d, .5)), bend);
}
export function grandmaTurn(t) {
  const u = seg(t, T_TURN0, T_TURN1), yaw = Math.PI * (1 - u);
  const body = [-22 - 7 * u, 2.4 * u], feet = {}, rigs = {};
  const P = { x: body[0], y: body[1], lean: .1 + .02 * u, head: { nod: .15, turn: 1 - 2 * seg(t, 1.62, 1.84) }, face: { look: [.6, .1], open: .9, smile: .1 } };
  for (const [sd, from, to, a, b] of [['F', -20, -31, 1.62, 1.82], ['N', -24, -27, 1.82, 1.98]]) {
    const q = cl((t - a) / (b - a)), step = EASE.io(q), sign = sd === 'N' ? -1 : 1;
    const foot = [from + (to - from) * step, -4.6 - 2.6 * Math.sin(Math.PI * q), 0];
    const hx = (sd === 'F' ? -3 * Math.cos(yaw) : 0) + sign * 7.2 * Math.sin(yaw);
    const hip = [body[0] + hx, body[1] - 75, sign * 2 * Math.sin(yaw)];
    const knee = knee3(hip, foot, yaw), shoeYaw = Math.PI * (1 - step);
    rigs[sd] = { hip, knee, foot, shoeYaw, planted: q === 0 || q === 1 };
    feet[sd] = foot.slice(0, 2);
    P['leg' + sd] = { knee: [knee[0] - body[0], knee[1] - body[1]], foot: [foot[0] - body[0], foot[1] - body[1]] };
  }
  return { view: 'turn', flip: false, P, bowl: BOWL1, rigs, feet, yaw };
}
function canvasLayer(box, k, at) {
  const [x0, y0, x1, y1] = box, ss = 2, c = new OffscreenCanvas((x1 - x0) * ss, (y1 - y0) * ss), x = c.getContext('2d');
  x.scale(ss, ss); x.translate(at[0] - x0, at[1] - y0); x.scale(k, k);
  return { c, x, layer: { img: c, x: x0, y: y0, sc: 1 / ss } };
}
function drawTurnLegs(x, G) {
  const fig = new Figure(x, { lw: 2.2, seed: 13, ink: NAINAI.NN.ink });
  for (const sd of ['F', 'N']) {
    const r = G.rigs[sd], hip = r.hip.slice(0, 2), knee = r.knee.slice(0, 2), foot = r.foot.slice(0, 2), z = sd === 'N' ? -4 : -6;
    const pts = tube([hip, mix(hip, knee, .5), knee, mix(knee, foot, .5), foot], [[0, 7.2], [.45, 5.6], [.55, 5.2], [1, 4.6]], { capStart: 'round', capStartK: .4, capEnd: 'flat', step: .7 });
    fig.part('leg' + sd, pts.outline, { fill: sd === 'N' ? NAINAI.NN.pants : '#353a48', z, per: 2 });
    const turn = Math.sin(r.shoeYaw), facing = Math.cos(r.shoeYaw);
    const side = [[-4.6, -.6], [2, -.8], [7.6, 1], [8.8, 3], [7.8, 4.2], [-4.8, 4.2], [-5.2, 1.6]];
    const front = [[-4.4, .4], [0, -.4], [4.4, .4], [4.8, 2.8], [3.2, 4.2], [-3.2, 4.2], [-4.8, 2.8]];
    // When facing left reverse front vertex correspondence, keeping a nonzero
    // projected sole width while the shoe rotates toward the camera.
    const coords = side.map((p, i) => [foot[0] + p[0] * facing + front[i][0] * turn * (facing < 0 ? -1 : 1), foot[1] + p[1] * (1 - turn) + front[i][1] * turn]);
    fig.part('shoe' + sd, coords, { fill: NAINAI.NN.shoe, z: z + .1, inner: true });
    const half = 7.3 * Math.abs(facing) + 4.7 * turn, center = 1.9 * facing;
    fig.part('sole' + sd, [[-half, 3.4], [half, 3.4], [half, 4.8], [-half, 4.8]].map(p => [foot[0] + center + p[0], foot[1] + p[1]]), { fill: NAINAI.NN.sole, z: z + .2, smooth: false });
  }
  fig.draw();
}
function turnUpperView(G) {
  const c = Math.cos(G.yaw), front = Math.abs(c) < Math.sqrt(3) / 2;
  return { view: front ? 'front' : 'side', flip: !front && c < 0,
    scaleX: front ? .84 + .16 * Math.sin(G.yaw) : .84 + .16 * Math.abs(c) };
}
function sideHeadCenter(P) {
  // Same neck/head transforms as chars/nainai.js, used only to keep the head
  // landmark continuous while the single visible view changes.
  const lean = P.lean || 0, n = rot([7.4, -32.9], lean), h = rot([-1.5, -13.9], lean + .08 + (P.head.nod || 0) * .14 + (P.head.tilt || 0));
  return [-1 + n[0] + h[0], -75 + n[1] + h[1]];
}
function upperTurnSprite(G) {
  const choice = turnUpperView(G), o = canvasLayer([760, 380, 1300, 790], GM_K, GM_AT), x = o.x;
  x.translate(G.P.x, G.P.y);
  const q = (Math.PI - G.yaw) / Math.PI, sn = Math.sin(G.yaw), cs = Math.cos(G.yaw);
  const P = { ...G.P, x: 0, y: 0, head: { ...G.P.head, turn: cs },
    armN: { hand: mix([5, -64], [6, -63], q), hp: 'relax' }, armF: { hand: mix([1, -65], [3, -64], q), hp: 'relax' },
    armL: { hand: [-16 - 1.5 * sn, -65 + .8 * cs], hp: 'relax' }, armR: { hand: [16 + 1.5 * sn, -65 - .8 * cs], hp: 'relax' } };
  const drawing = NAINAI[choice.view](x, P), { fig } = drawing, lower = /^(leg|pants|shoe|sole)/;
  fig.parts = fig.parts.filter(p => !lower.test(p.name));
  fig.ops = fig.ops.filter(p => p.kind !== 'part' || !lower.test(p.name));
  x.save(); x.setTransform(1, 0, 0, 1, 0, 0); x.clearRect(0, 0, o.c.width, o.c.height); x.restore();
  const head = drawing.H([0, 0]), sx = choice.scaleX * (choice.flip ? -1 : 1);
  const target = sideHeadCenter(P), targetX = cs * target[0];
  const shear = (targetX - sx * head[0]) / (head[1] + 75), sy = (target[1] + 75) / (head[1] + 75);
  // Align both head coordinates about the hip seam: the selected view follows
  // one continuous head arc while remaining attached to the unchanged legs.
  x.translate(0, -75); x.transform(sx, 0, shear, sy, 0, 0); x.translate(0, 75);
  x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; fig.draw();
  return { canvas: o.c, figure: fig, head, choice };
}
function turnLayer(G) {
  const o = canvasLayer([760, 380, 1300, 790], GM_K, GM_AT), x = o.x;
  x.save(); x.scale(-1, 1); stool(x, -2); bowl(x, ...BOWL1, 26); x.restore();
  drawTurnLegs(x, G);
  const sprite = upperTurnSprite(G);
  x.save(); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.drawImage(sprite.canvas, 0, 0); x.restore();
  return o.layer;
}

// Hard editorial cuts, evaluated in seconds: at 24fps the first new frames are
// F16/F39/F57. Do not snap 2.35s backward to F56. No per-insert time restart.
export function s07Camera(t) {
  if (t >= .66 && t < 1.62) {
    // 608×342 scene-pixel window (16:9), following the rise upward. The early
    // window includes the floor/bowl; the late window retains head and knees.
    return { x: 1024, y: 630 - 90 * seg(t, 1.05, 1.6), fit: BW / 608 };
  }
  if (t >= 1.62 && t < 2.35) return { x: 605, y: 637.5, fit: BW / 400 };
  return { x: BW / 2 - 20, y: BH / 2 + 12, fit: 1.04 };
}
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async (t) => {
    const X = xiaomanS07(t), G = grandmaS07(t), ph = xmPhone(t);
    return [
      { img: COILC, x: COIL[0] - 60, y: COIL[1] - 34, sc: 1 },
      tableLamp(G.lampLift || 0),
      // Do not even submit the offscreen actor during either insert: a wider
      // output aspect ratio must not expose the failed side/back/front swaps.
      ...(t >= .66 && t < 1.62 ? [] : [X.view === 'roll' ? rollingLayer(X, ph) : charLayer('x', X.view, X.P, { box: [400, 520, 760, 690], k: XM_K, at: XM_AT, flip: X.flip, rot: X.rot || 0, pivot: X.pivot, to: X.to,
        before: (x) => { if (X.flip) x.scale(-1, 1); phoneSide(x, ph, 0); } })]),
      ...(t >= 1.62 && t < 2.35 ? [] : [G.view === 'turn' ? turnLayer(G) : charLayer('n', G.view, G.P, { box: [760, 380, 1300, 790], k: GM_K, at: GM_AT, flip: G.flip,
        before: (x) => { if (!G.flip) x.scale(-1, 1); stool(x, -2); if (!G.bowlFront) bowl(x, G.bowl[0], G.bowl[1], 26); },
        after: (x) => { if (!G.flip) x.scale(-1, 1); if (G.bowlFront) bowl(x, G.bowl[0], G.bowl[1], 26); } })]),
    ];
  },
  light: (t) => darkLight(t, 0),
  glow: () => [{ x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }],
  emit: (x) => fan(x, 0),
  cam: s07Camera,
};
export async function renderFrame(ctx, t, W, H) { return renderPaint(ctx, t, W, H, shot); }
