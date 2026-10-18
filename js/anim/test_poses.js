// 动态分镜用的代码人物：姿势校准（趴着的小满、坐着剥豆的奶奶）
import * as X from '../chars/xiaoman.js';
import * as N from '../chars/nainai.js';
export const DURATION = 1;
export async function renderFrame(ctx, t, W, H) {
  ctx.fillStyle = '#e9e2d6'; ctx.fillRect(0, 0, W, H);
  ctx.strokeStyle = '#999';
  for (const y of [420, 940]) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  // 小满趴着：几组头角度和手位
  const xleans = [1.2, 1.3, 1.4];
  xleans.forEach((ln, i) => {
    ctx.save(); ctx.translate(250 + i * 560, 420); ctx.scale(3.2, 3.2);
    X.draw(ctx, 'side', X.pose({
      y: 36, lean: ln, head: { tilt: -ln * 0.75 },
      legN: { foot: [-36, -64], knee: [-21, -42] }, legF: { foot: [-28, -68], knee: [-21, -43] },
      armN: { elbow: [36, -37.5], hand: [49, -50], hp: 'grip' }, armF: { elbow: [33, -38], hand: [47, -51], hp: 'grip' },
      face: { look: [0.8, 0.6], smile: 0 },
    }));
    ctx.fillStyle = '#222'; ctx.save(); ctx.translate(50, -51); ctx.rotate(-0.5); ctx.fillRect(-1, -7, 2.4, 14); ctx.restore();   // 手机示意
    ctx.restore();
  });
  // 奶奶坐矮凳（凳高 30 cm）：整个人往下挪 37 cm
  const leans = [0.15, 0.3, 0.45];
  leans.forEach((ln, i) => {
    ctx.save(); ctx.translate(300 + i * 560, 940); ctx.scale(2.4, 2.4);
    ctx.fillStyle = '#8a5a3a'; ctx.fillRect(-14, -30, 26, 30);   // 凳子示意
    N.draw(ctx, 'side', N.pose({ y: 37, seated: true, lean: ln, head: { nod: 0.4, tilt: -ln * 0.6 },
      armN: { hand: [27, -82], hp: 'pinch' }, armF: { hand: [24, -84], hp: 'pinch' },
      legN: { foot: [33, -41.6] }, legF: { foot: [29, -41.6] } }));
    ctx.restore();
  });
}
