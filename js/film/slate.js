// 占位卡：还没做好的镜头先用一张卡片顶上（镜头号、场次、内容、时长），粗剪里看节奏用
import { SHOTS } from './edl.js';
export async function render(ctx, arg, W, H) {
  const s = SHOTS.find((x) => x.id === arg) || { id: arg, scene: 0, dur: 0, text: '' };
  const col = { paint: '#3b2f25', engine: '#2b2418', code: '#1f2a33' }[s.line] || '#222';
  ctx.fillStyle = col; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = 'rgba(255,240,220,0.08)'; ctx.fillRect(W * 0.06, H * 0.1, W * 0.88, H * 0.8);
  ctx.fillStyle = '#f3e3c8';
  ctx.font = `${Math.round(H * 0.09)}px "Noto Sans SC"`; ctx.fillText(`${s.id}`, W * 0.1, H * 0.28);
  ctx.font = `${Math.round(H * 0.04)}px "Noto Sans SC"`;
  ctx.fillText(`第 ${s.scene} 场 · ${s.dur} 秒 · ${{ paint: '屋内（背景图 + 打光）', engine: '床单戏（光照引擎）', code: '程序画' }[s.line] || ''}`, W * 0.1, H * 0.38);
  ctx.font = `${Math.round(H * 0.045)}px "Noto Sans SC"`;
  // 自动换行
  const words = [...s.text], maxW = W * 0.8; let line = '', y = H * 0.52;
  for (const ch of words) { if (ctx.measureText(line + ch).width > maxW) { ctx.fillText(line, W * 0.1, y); line = ch; y += H * 0.07; } else line += ch; }
  if (line) ctx.fillText(line, W * 0.1, y);
  ctx.fillStyle = 'rgba(243,227,200,0.5)'; ctx.font = `${Math.round(H * 0.03)}px "Noto Sans SC"`; ctx.fillText('（占位：镜头还没做）', W * 0.1, H * 0.85);
}
