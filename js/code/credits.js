// 片尾（15 秒）：前 8.5 秒字幕慢慢往上走（暗处，马灯的暖光轻轻晃）；然后是竹席上小满的手机——锁屏壁纸换成了床单上那只鹤的影子；
// 最后屏幕自己熄掉，全片结束。手机界面是原创的，没有任何真实品牌。
import { mat, lit, RW, RH, sstep } from './phone.js';
import { LINES, TEAM } from '../film/credits_text.js';
export const DURATION = 15;
let WALL = null;
async function wall() {
  if (WALL) return WALL;
  const r = await fetch('/assets/ui/lock_crane.jpg');
  return (WALL = await createImageBitmap(await r.blob()));
}
function grain(ctx, W, H, t, amt = 6) {
  const gi = ctx.getImageData(0, 0, W, H), G = gi.data; let seed = Math.floor(t * 24) * 7919 + 29;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < G.length; i += 4) { const n = (rnd() - 0.5) * amt; G[i] += n; G[i + 1] += n; G[i + 2] += n; }
  ctx.putImageData(gi, 0, 0);
}
function rolls(ctx, t) {
  // 暗底 + 马灯一样晃的暖光
  const fl = 1 + 0.04 * Math.sin(t * 7.3) + 0.03 * Math.sin(t * 12.1);
  ctx.fillStyle = '#0b0806'; ctx.fillRect(0, 0, RW, RH);
  const g = ctx.createRadialGradient(RW * 0.5, RH * 1.1, 50, RW * 0.5, RH * 0.9, RH * 1.1);
  g.addColorStop(0, `rgba(120,72,30,${0.45 * fl})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, RW, RH);
  const items = [...LINES.map(([h, b]) => ({ h, b })), ...(TEAM.length ? [{ h: '', b: '' }, { h: '制作', b: '' }, ...TEAM.map(([h, b]) => ({ h, b }))] : [])];
  // 有小标题的一段前面空得多，同一段里的接续行挨得近
  const ys = []; let acc = 0;
  items.forEach((it, i) => { acc += i === 0 ? 0 : it.h ? 118 : 54; ys.push(acc); });
  const total = acc;
  const y0 = RH * 1.02 - (RH * 1.02 + total - RH * 0.42) * sstep(0.3, 8.6, t);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  items.forEach((it, i) => {
    const y = y0 + ys[i];
    if (y < -60 || y > RH + 60) return;
    const fade = Math.min(1, Math.max(0, (y - RH * 0.12) / (RH * 0.18))) * Math.min(1, Math.max(0, (RH * 0.96 - y) / (RH * 0.12)));
    if (it.h) { ctx.font = '400 28px "Noto Sans SC"'; ctx.fillStyle = `rgba(190,160,120,${0.85 * fade})`; ctx.fillText(it.h, RW / 2, y - 44); }
    ctx.font = '400 40px "Noto Sans SC"'; ctx.fillStyle = `rgba(242,228,200,${fade})`; ctx.fillText(it.b, RW / 2, y);
  });
  ctx.textAlign = 'left';
}
// 竹席上的手机（竖着放），锁屏
function lock(ctx, t, img) {
  const u = t - 8.5;
  const amb = [0.16, 0.12, 0.09];                    // 马灯从远处照过来的一点暖光
  ctx.fillStyle = '#000'; ctx.fillRect(0, 0, RW, RH);
  const zoom = 1.0 + 0.04 * sstep(0, 6.5, u);
  ctx.save(); ctx.translate(RW / 2, RH / 2); ctx.scale(zoom, zoom); ctx.translate(-RW / 2, -RH / 2);
  ctx.save(); ctx.filter = 'blur(3px)'; ctx.drawImage(mat(), -300, -300); ctx.restore();
  ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = `rgb(${amb.map((v) => Math.round(255 * Math.pow(v, 1 / 2.2))).join(',')})`; ctx.fillRect(0, 0, RW, RH); ctx.restore();
  const on = 1 - sstep(5.7, 6.3, u);                 // 屏幕熄灭
  const PW = 470, PH = 960, R = 64, BZ = 16;
  ctx.translate(RW / 2, RH / 2 - 30); ctx.rotate(-0.07); ctx.scale(0.8, 0.8);
  // 屏幕往竹席上溢的光（冷一点）
  if (on > 0) {
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createRadialGradient(0, 0, PH * 0.3, 0, 0, PH * 0.95);
    g.addColorStop(0, `rgba(120,100,70,${0.35 * on})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(-PH, -PH, PH * 2, PH * 2); ctx.restore();
  }
  // 影子、充电线、机身
  ctx.save(); ctx.translate(14, 18); ctx.filter = 'blur(20px)'; ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.beginPath(); ctx.roundRect(-PW / 2, -PH / 2, PW, PH, R); ctx.fill(); ctx.restore();
  ctx.lineCap = 'round'; const cab = new Path2D(); cab.moveTo(0, PH / 2 + 30); cab.bezierCurveTo(10, PH / 2 + 160, -160, PH / 2 + 120, -260, PH / 2 + 380);
  ctx.strokeStyle = '#4a2e1f'; ctx.lineWidth = 22; ctx.stroke(cab); ctx.strokeStyle = lit('#f2f2ee', [0.2, 0.18, 0.16]); ctx.lineWidth = 15; ctx.stroke(cab);
  ctx.fillStyle = lit('#e8e8e4', [0.22, 0.2, 0.18]); ctx.strokeStyle = '#4a2e1f'; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(-22, PH / 2 - 4, 44, 56, 8); ctx.fill(); ctx.stroke();
  ctx.fillStyle = lit('#2b2d33', [0.35 + 0.4 * on, 0.33 + 0.4 * on, 0.32 + 0.4 * on]); ctx.beginPath(); ctx.roundRect(-PW / 2, -PH / 2, PW, PH, R); ctx.fill();
  ctx.strokeStyle = '#4a2e1f'; ctx.lineWidth = 6; ctx.stroke();
  // 屏幕
  ctx.save(); ctx.beginPath(); ctx.roundRect(-PW / 2 + BZ, -PH / 2 + BZ, PW - 2 * BZ, PH - 2 * BZ, R - BZ); ctx.clip();
  const sw = PW - 2 * BZ, sh = PH - 2 * BZ; ctx.translate(-sw / 2, -sh / 2);
  ctx.fillStyle = '#050505'; ctx.fillRect(0, 0, sw, sh);
  if (on > 0) {
    ctx.globalAlpha = on;
    const sc = Math.max(sw / img.width, sh / img.height); ctx.drawImage(img, (sw - img.width * sc) / 2, (sh - img.height * sc) / 2, img.width * sc, img.height * sc);
    ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fillRect(0, 0, sw, sh);
    ctx.textAlign = 'center'; ctx.fillStyle = '#fff'; ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 12;
    ctx.font = '300 128px "Noto Sans SC"'; ctx.fillText('22:41', sw / 2, 190);
    ctx.font = '400 30px "Noto Sans SC"'; ctx.fillText('7月26日 星期六', sw / 2, 240);
    // 充电：闪电 + 百分比
    ctx.font = '500 28px "Noto Sans SC"'; ctx.fillText('充电中 · 38%', sw / 2 + 14, sh - 150);
    ctx.save(); ctx.translate(sw / 2 - 92, sh - 151); ctx.beginPath(); ctx.moveTo(4, -15); ctx.lineTo(-8, 3); ctx.lineTo(0, 3); ctx.lineTo(-4, 15); ctx.lineTo(9, -3); ctx.lineTo(1, -3); ctx.closePath(); ctx.fill(); ctx.restore();
    // 底部两个圆按钮（手电、相机——简单的原创图标）
    ctx.shadowBlur = 0;
    for (const [x, ic] of [[70, 'torch'], [sw - 70, 'cam']]) {
      ctx.fillStyle = 'rgba(30,30,30,0.45)'; ctx.beginPath(); ctx.arc(x, sh - 70, 36, 0, 7); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 3;
      if (ic === 'torch') { ctx.beginPath(); ctx.moveTo(x - 9, sh - 88); ctx.lineTo(x + 9, sh - 88); ctx.lineTo(x + 5, sh - 72); ctx.lineTo(x + 5, sh - 52); ctx.lineTo(x - 5, sh - 52); ctx.lineTo(x - 5, sh - 72); ctx.closePath(); ctx.stroke(); }
      else { ctx.beginPath(); ctx.roundRect(x - 16, sh - 82, 32, 24, 4); ctx.stroke(); ctx.beginPath(); ctx.arc(x, sh - 70, 7, 0, 7); ctx.stroke(); }
    }
    ctx.fillStyle = 'rgba(255,255,255,0.8)'; ctx.fillRect(sw / 2 - 70, sh - 22, 140, 6);
    ctx.globalAlpha = 1; ctx.textAlign = 'left';
  }
  // 玻璃反光
  const gl = ctx.createLinearGradient(0, 0, sw, sh); gl.addColorStop(0.35, 'rgba(255,240,220,0)'); gl.addColorStop(0.5, 'rgba(255,240,220,0.05)'); gl.addColorStop(0.65, 'rgba(255,240,220,0)');
  ctx.fillStyle = gl; ctx.fillRect(0, 0, sw, sh);
  ctx.restore();
  ctx.restore();
  const v = ctx.createRadialGradient(RW / 2, RH / 2, RH * 0.35, RW / 2, RH / 2, RH * 0.9);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.65)'); ctx.fillStyle = v; ctx.fillRect(0, 0, RW, RH);
}
export async function renderFrame(ctx, t, W, H) {
  const img = await wall();
  ctx.save(); ctx.setTransform(W / RW, 0, 0, H / RH, 0, 0);
  if (t < 9.5) rolls(ctx, t);
  if (t > 8.5) { ctx.save(); ctx.globalAlpha = sstep(8.5, 9.5, t); lock(ctx, t, img); ctx.restore(); }
  // 最后一秒黑下去
  ctx.fillStyle = `rgba(0,0,0,${sstep(14.2, 15, t)})`; ctx.fillRect(0, 0, RW, RH);
  ctx.restore();
  grain(ctx, W, H, t);
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
