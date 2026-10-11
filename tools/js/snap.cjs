// 渲染一张静帧：node tools/js/snap.cjs <模块> <输出.png> [宽 高] [参数]
// 模块导出 render(ctx, arg, W, H)（可以是 async）。参数原样传给 render。
const { chromium } = require('playwright');
const { start } = require('./serve.cjs');
const fs = require('fs');
(async () => {
  const [mod, out, W = 1920, H = 1080, arg = ''] = process.argv.slice(2);
  const srv = await start(0);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 300 } });
  page.on('console', (m) => console.log('[page]', m.text()));
  page.on('pageerror', (e) => { console.log('[pageerror]', e.message); process.exitCode = 1; });
  const url = `http://127.0.0.1:${srv.address().port}/dev/view.html?mod=${encodeURIComponent(mod)}&w=${W}&h=${H}`;
  await page.goto(url);
  await page.waitForFunction(() => window.__ready === true || window.__error, null, { timeout: 60000 });
  const err = await page.evaluate(() => window.__error);
  if (err) { console.log('[error]', err); process.exit(1); }
  const data = await page.evaluate(async (a) => { await window.render(a); return document.getElementById('c').toDataURL('image/png'); }, arg);
  fs.writeFileSync(out, Buffer.from(data.split(',')[1], 'base64'));
  console.log(out);
  await browser.close(); srv.close();
})();
