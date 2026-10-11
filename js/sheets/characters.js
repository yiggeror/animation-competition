// 人物设计稿（2D）：arg = 'turnaround' 三视图与身高 | 'expr' 表情表 | 'hands' 手型
import * as X from '../chars/xiaoman.js';
import * as N from '../chars/nainai.js';
import { Figure, M } from '../lib/figure.js';
import { hand, HAND_POSES } from '../chars/hand.js';
import { setBoil, rrectPts, shape } from '../lib/draw.js';

const PAPER = '#f5eee2', INK = '#3b2c25', SUB = '#7a6a5c';
function title(ctx, t, sub) {
  ctx.fillStyle = INK; ctx.font = '64px "Ma Shan Zheng"'; ctx.textBaseline = 'alphabetic';
  ctx.fillText(t, 60, 100);
  if (sub) { ctx.fillStyle = SUB; ctx.font = '26px "Noto Sans SC"'; ctx.fillText(sub, 60, 146); }
}
function label(ctx, t, x, y, size = 28, color = INK, align = 'center') {
  ctx.fillStyle = color; ctx.font = `${size}px "Noto Sans SC"`; ctx.textAlign = align; ctx.fillText(t, x, y); ctx.textAlign = 'left';
}
function card(ctx, x, y, w, h) {
  ctx.fillStyle = '#fbf7ef'; ctx.beginPath(); ctx.roundRect(x, y, w, h, 18); ctx.fill();
  ctx.strokeStyle = 'rgba(59,44,37,0.12)'; ctx.lineWidth = 2; ctx.stroke();
}

export function render(ctx, arg = 'turnaround', W, H) {
  setBoil(0);
  ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
  if (arg === 'expr') return expr(ctx, W, H);
  if (arg === 'hands') return hands(ctx, W, H);
  return turnaround(ctx, W, H);
}

function turnaround(ctx, W, H) {
  title(ctx, '人物设计 · 三视图', '小满（9 岁，约 1.3 米）和奶奶（七十来岁，约 1.5 米），同一比例。双马尾、红绒球和白圆领让小满从背影、剪影里也一眼认得出。');
  const base = H - 90, s = 5.6;
  // 身高刻度
  ctx.strokeStyle = 'rgba(59,44,37,0.18)'; ctx.lineWidth = 1.5;
  for (let cm = 0; cm <= 125; cm += 25) {
    const y = base - cm * s;
    ctx.beginPath(); ctx.moveTo(60, y); ctx.lineTo(W - 60, y); ctx.stroke();
    label(ctx, cm + ' 厘米', 70, y - 6, 18, SUB, 'left');
  }
  const xs = [270, 560, 850], ns = [1200, 1470, 1720];
  ['front', 'side', 'back'].forEach((v, i) => {
    X.draw(ctx, v, { x: xs[i], y: base, s });
    N.draw(ctx, v, { x: ns[i], y: base, s });
  });
  label(ctx, '小满 · 正面', xs[0], base + 50); label(ctx, '侧面', xs[1], base + 50); label(ctx, '背面', xs[2], base + 50);
  label(ctx, '奶奶 · 正面', ns[0], base + 50); label(ctx, '侧面', ns[1], base + 50); label(ctx, '背面', ns[2], base + 50);
}

const XM_EXPR = [
  ['平常', {}], ['无聊（打游戏）', { open: 0.62, smile: -0.15, look: [0.5, 0.6], blush: 0.3 }],
  ['着急（电量 1%）', { open: 1.2, worry: 1, mouth: 0.45, smile: -0.4 }], ['绝望（瘫倒）', { open: 0.55, worry: 0.9, smile: -0.8, mouth: 0.25 }],
  ['嘴硬（装不在乎）', { frown: 1, smile: -0.5, look: [0.8, 0], blush: 0.25 }], ['看呆了（鹤亮相）', { open: 1.25, brow: 1, mouth: 0.65, smile: 0, look: [0, -0.5] }],
  ['扑哧笑', { happyEyes: 1, smile: 1, mouth: 0.75, blush: 0.95 }], ['被晃得眯眼', { squint: 1, open: 0.45, worry: 0.5, smile: -0.25, mouth: 0.2 }],
  ['做鬼脸', { open: 1.1, mouth: 0.9, smile: 0.5, tongue: 1, brow: 0.6 }],
];
const NN_EXPR = [
  ['平常', {}], ['看孙女（剥豆）', { smile: 0.65, happyEyes: 1, blush: 0.4 }], ['狡黠（有主意了）', { smile: 0.55, look: [0.8, 0], squint: 0.45, brow: 0.4 }],
  ['笑弯了腰', { happyEyes: 1, smile: 1, mouth: 0.85, blush: 0.7 }], ['专注（操纵皮影）', { open: 0.95, look: [0.6, 0.3], smile: 0.1, brow: -0.2 }],
  ['被晃得眯眼', { squint: 1, open: 0.4, smile: 0.0, worry: 0.3 }], ['不好意思地笑', { happyEyes: 1, smile: 0.55, blush: 0.9, look: [0.5, 0.4] }],
  ['鼓腮吹灯', { puff: 1, open: 0.9, brow: 0.3 }], ['愣了一下', { open: 1.25, brow: 0.9, mouth: 0.35, smile: 0 }],
];
function expr(ctx, W, H) {
  title(ctx, '人物设计 · 表情', '每个情绪同时落在眼睛、眉毛、嘴上（眉毛画在刘海上面，被头发挡住也看得见）；动起来时再配上姿态和小动作。');
  const cw = 190, ch = 236, gap = 10, x0 = 60;
  const rows = [['小满', XM_EXPR, X, 5.5], ['奶奶', NN_EXPR, N, 5.6]];
  rows.forEach(([who, list, C, s], r) => {
    const y0 = 190 + r * (ch + 120);
    label(ctx, who, x0, y0 - 16, 30, INK, 'left');
    list.forEach(([name, f], i) => {
      const x = x0 + i * (cw + gap);
      card(ctx, x, y0, cw, ch);
      ctx.save();
      ctx.beginPath(); ctx.roundRect(x, y0, cw, ch, 18); ctx.clip();
      const fc = C === X ? X.XM.faceC : N.NN.faceC;
      // 头放在格子中间偏上
      C.draw(ctx, 'front', { x: x + cw / 2, y: y0 + 128 - fc[1] * s, s, face: f, head: { tilt: name.includes('嘴硬') ? -0.08 : name.includes('狡黠') ? 0.07 : 0 } });
      ctx.restore();
      label(ctx, name, x + cw / 2, y0 + ch + 34, 22);
    });
  });
}

function hands(ctx, W, H) {
  title(ctx, '人物设计 · 手', '卡通四指手，每种手型是一条设计好的整体轮廓；握签子时四指包住、拇指压在前面。奶奶的手大一号，左腕戴玉镯。');
  const names = [['relax', '放松'], ['fist', '拳'], ['grip', '握签子'], ['point', '指'], ['pinch', '捏（剥豆、拉灯绳）'], ['open', '张开'], ['wave', '挥手'], ['rest', '微曲']];
  names.forEach(([k, cn], i) => {
    const x = 90 + (i % 4) * 450, y = 230 + Math.floor(i / 4) * 400;
    card(ctx, x, y, 420, 350);
    for (const [who, D, dx, sz] of [['小满', X.XM, 130, 4.4], ['奶奶', N.NN, 285, 5.4]]) {
      ctx.save(); ctx.translate(x + dx, y + 60); ctx.scale(21, 21);   // 两人按真实大小比较
      const fig = new Figure(ctx, { lw: 3.0, ink: INK });
      hand(fig, M.chain(M.t(0, 0), M.r(Math.PI / 2)), k, { size: sz, skin: D.skin, z: 0, name: 'h', lw: 3.0, line: D.skinShade, ink: INK });
      fig.draw();
      ctx.restore();
    }
    label(ctx, cn, x + 210, y + 330, 26);
  });
}
