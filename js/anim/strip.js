// 逐帧检查表：把一个镜头某段时间的每一帧（或隔几帧）排成网格，可以只看人物附近的一块，方便查关节朝向、骨长、脚滑没滑。
// 用法：node tools/js/snap.cjs js/anim/strip.js 输出.png 2560 <高> "S07|0.4:1.0:0.0417|x,y,宽"
//   第二段 起:止:步长（秒），第三段（可选）是 1280×720 画面里要放大的一块（左上角 x、y 和宽度，高按 16:9）。
const MOD = { S01: './s01.js', S02a: './s02a.js', S03: './s03.js', S03a: './s03a.js', S03b: './s03b.js', S04: './s04.js', S05a: './s05a.js', S07: './s07.js', S08: './s08.js' };
export async function render(ctx, arg, W, H) {
  const [id, range, crop] = String(arg).split('|');
  const [a, b, d] = range.split(':').map(Number), mod = await import(MOD[id]);
  const ts = []; for (let t = a; t <= b + 1e-6; t += d) ts.push(+t.toFixed(4));
  const cols = Math.min(6, ts.length), tw = W / cols, th = tw * 9 / 16, lh = 30;
  const [cx, cy, cw] = crop ? crop.split(',').map(Number) : [0, 0, 1280];
  ctx.fillStyle = '#f2ece2'; ctx.fillRect(0, 0, W, H);
  const off = new OffscreenCanvas(1280, 720), ox = off.getContext('2d');
  for (let i = 0; i < ts.length; i++) {
    const x = (i % cols) * tw, y = Math.floor(i / cols) * (th + lh);
    ox.setTransform(1, 0, 0, 1, 0, 0); ox.clearRect(0, 0, 1280, 720);
    await mod.renderFrame(ox, ts[i], 1280, 720);
    ctx.drawImage(off, cx, cy, cw, cw * 9 / 16, x + 3, y + 3, tw - 6, th - 6);
    ctx.fillStyle = '#2b211c'; ctx.font = '20px "Noto Sans SC"';
    ctx.fillText(`${id} 第 ${Math.round(ts[i] * 24)} 帧  ${ts[i].toFixed(2)}s`, x + 8, y + th + 22);
  }
}
