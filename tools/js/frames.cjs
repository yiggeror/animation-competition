// 逐帧渲染一个动画模块：node tools/js/frames.cjs <模块> <输出目录> [--fps 24] [--w 1920 --h 1080] [--from 0 --to 末尾] [--workers 3] [--mp4 输出.mp4 [--clean 1]] [--debug '{"sheetRes":450}']
// 模块导出 DURATION 和 renderFrame(ctx, t, W, H)。每帧是时间的纯函数，所以可以多个浏览器页面并行。
const { chromium } = require('playwright');
const { start } = require('./serve.cjs');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const argv = process.argv.slice(2);
const mod = argv[0], outDir = argv[1];
const opt = {};
for (let i = 2; i < argv.length; i += 2) opt[argv[i].replace(/^--/, '')] = argv[i + 1];
const fps = +(opt.fps || 24), W = +(opt.w || 1920), H = +(opt.h || 1080), workers = +(opt.workers || 3);
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const srv = await start(0);
  const browser = await chromium.launch();
  const url = `http://127.0.0.1:${srv.address().port}/dev/view.html?mod=${encodeURIComponent(mod)}&w=${W}&h=${H}` + (opt.debug ? `&debug=${encodeURIComponent(opt.debug)}` : '');
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 400, height: 300 } });
    page.on('pageerror', (e) => console.log('[pageerror]', e.message));
    page.on('console', (m) => { if (m.type() === 'error') console.log('[page]', m.text()); });
    await page.goto(url);
    await page.waitForFunction(() => window.__ready === true || window.__error, null, { timeout: 60000 });
    const err = await page.evaluate(() => window.__error);
    if (err) { console.log('[error]', err); process.exit(1); }
    return page;
  };
  const probe = await open();
  const dur = await probe.evaluate(() => window.DURATION);
  await probe.close();
  const f0 = Math.round(+(opt.from || 0) * fps), f1 = Math.round(Math.min(+(opt.to || dur), dur) * fps);
  console.log(`${f1 - f0} 帧，${W}×${H}，${fps} 帧/秒，${workers} 个页面`);
  let done = 0; const t0 = Date.now();
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const page = await open();
    for (let f = f0 + w; f < f1; f += workers) {
      const data = await page.evaluate(async (t) => { await window.renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, f / fps);
      fs.writeFileSync(path.join(outDir, `${String(f).padStart(5, '0')}.png`), Buffer.from(data.split(',')[1], 'base64'));
      if (++done % 24 === 0) console.log(`  ${done}/${f1 - f0}  ${(done / ((Date.now() - t0) / 1000)).toFixed(1)} 帧/秒`);
    }
    await page.close();
  }));
  await browser.close(); srv.close();
  if (opt.mp4) {
    const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-start_number', String(f0), '-i', path.join(outDir, '%05d.png'),
      '-frames:v', String(f1 - f0), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', opt.crf || '18', '-tune', 'animation', opt.mp4], { stdio: 'inherit' });
    if (r.status !== 0) process.exit(r.status);
    console.log(opt.mp4);
    if (opt.clean) fs.rmSync(outDir, { recursive: true, force: true });   // 压好视频后删掉逐帧 PNG（1080p 一个镜头上 GB，盘不够）
  }
})();
