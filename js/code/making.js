// 片尾"制作与资源"：手机屏幕熄灭以后，暗底上一张一张淡入淡出。只写实际用到的技术手段、工具、字体和声音来源（核对见 CREDITS.md）。
export const DURATION = 18;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
// [开始, 结束, 小标题, [[项目, 内容], ...]]
const CARDS = [
  [0.6, 4.4, '画面', [
    ['人物与屋内底图', '生成式图像绘制，抠图分层，逐格修整'],
    ['皮影、手影、光与影', '程序逐帧计算（Canvas 2D · WebGL）'],
    ['渲染', 'Chromium 无头逐帧输出 · FFmpeg 编码'],
  ]],
  [4.4, 8.2, '声音', [
    ['配乐与音效', '程序合成（加法合成 · Karplus-Strong 拨弦 · 模态合成）'],
    ['音色', '板胡 · 笛子 · 扬琴 · 琵琶 · 梆子 · 板鼓 · 锣 · 钹 · 8-bit'],
    ['', '旋律原创，未使用采样与录音'],
  ]],
  [8.2, 11.4, '字体', [
    ['马善政毛笔楷书 Ma Shan Zheng', 'SIL Open Font License 1.1'],
    ['思源黑体 Noto Sans SC', 'SIL Open Font License 1.1'],
  ]],
  [11.4, 14.4, '工具', [
    ['', 'Node.js · Playwright · Chromium'],
    ['', 'Python · NumPy · SciPy · Pillow · FFmpeg'],
  ]],
];

function bg(ctx, W, H, t) {
  // 暗底 + 底下一点像马灯一样轻轻晃的暖光
  const fl = 1 + 0.04 * Math.sin(t * 7.3) + 0.03 * Math.sin(t * 12.1);
  ctx.fillStyle = '#0b0806'; ctx.fillRect(0, 0, W, H);
  const g = ctx.createRadialGradient(W * 0.5, H * 1.15, 40, W * 0.5, H * 0.95, H * 1.1);
  g.addColorStop(0, `rgba(120,72,30,${0.42 * fl})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

export function renderFrame(ctx, t, W, H) {
  const k = H / 1080;
  bg(ctx, W, H, t);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  for (const [a, b, head, items] of CARDS) {
    const al = sstep(a, a + 0.55, t) * (1 - sstep(b - 0.55, b, t));
    if (al <= 0) continue;
    const rows = items.reduce((n, [l]) => n + (l ? 2 : 1), 0);
    let y = H * 0.5 - (rows * 50 + (items.length - 1) * 34 + 90) * k / 2;
    ctx.font = `400 ${Math.round(34 * k)}px "Noto Sans SC"`; ctx.fillStyle = `rgba(214,170,110,${al})`;
    ctx.fillText(head, W / 2, y); y += 90 * k;
    for (const [label, body] of items) {
      if (label) { ctx.font = `300 ${Math.round(27 * k)}px "Noto Sans SC"`; ctx.fillStyle = `rgba(190,160,120,${0.9 * al})`; ctx.fillText(label, W / 2, y); y += 50 * k; }
      ctx.font = `400 ${Math.round(36 * k)}px "Noto Sans SC"`; ctx.fillStyle = `rgba(242,228,200,${al})`; ctx.fillText(body, W / 2, y); y += (50 + 34) * k;
    }
  }
  // 最后一张：片名
  const al = sstep(14.6, 15.4, t) * (1 - sstep(16.9, 17.8, t));
  if (al > 0) {
    ctx.save(); ctx.font = `${Math.round(110 * k)}px "Ma Shan Zheng"`; ctx.fillStyle = `rgba(246,231,200,${al})`;
    ctx.shadowColor = `rgba(255,190,110,${0.45 * al})`; ctx.shadowBlur = 30 * k; ctx.fillText('奶奶的皮影', W / 2, H * 0.47); ctx.restore();
    ctx.font = `300 ${Math.round(26 * k)}px "Noto Sans SC"`; ctx.fillStyle = `rgba(190,160,120,${0.85 * al})`; ctx.fillText('2026', W / 2, H * 0.47 + 110 * k);
  }
}
export async function render(ctx, arg, W, H) { return renderFrame(ctx, +arg || 0, W, H); }
