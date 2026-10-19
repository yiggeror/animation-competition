const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
(async () => {
  const root = path.dirname(__dirname);
  const log = { status: 'running', responses: [], requestFailed: [], pageErrors: [], pngs: [], boundary: null };
  const server = http.createServer((req, res) => {
    const p = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!p.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
    fs.readFile(p, (e, data) => {
      if (e) { res.writeHead(404); res.end(); return; }
      res.setHeader('Content-Type', ({ '.js': 'text/javascript', '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json' })[path.extname(p)] || 'application/octet-stream');
      res.end(data);
    });
  });
  let browser;
  try {
    await new Promise((ok, bad) => { server.once('error', bad); server.listen(0, '127.0.0.1', ok); });
    browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'], executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium' });
    const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
    page.on('response', r => log.responses.push({ url: r.url(), status: r.status(), ok: r.ok() }));
    page.on('requestfailed', r => log.requestFailed.push({ url: r.url(), error: r.failure()?.errorText || 'unknown' }));
    page.on('pageerror', e => { log.pageErrors.push(String(e.stack || e)); console.error('PAGEERROR', e.stack || e); });
    page.on('console', m => console.log('BROWSER', m.type(), m.text()));
    const failIfNeeded = () => {
      if (log.pageErrors.length) throw new Error('Browser pageerror; see RENDER_EXECUTION_LOG.json');
      if (log.requestFailed.length) throw new Error('Network requestfailed; see exact URLs in RENDER_EXECUTION_LOG.json');
      const bad = log.responses.filter(r => r.status >= 400 && !new URL(r.url).pathname.endsWith('/favicon.ico'));
      if (bad.length) throw new Error('Required HTTP response failed; see exact URLs in RENDER_EXECUTION_LOG.json');
    };
    const save = async name => {
      failIfNeeded();
      const p = path.join(__dirname, name);
      await page.locator('canvas').screenshot({ path: p });
      const b = fs.readFileSync(p);
      log.pngs.push({ filename: name, bytes: b.length, sha256: crypto.createHash('sha256').update(b).digest('hex') });
    };
    log.entryUrl = `http://127.0.0.1:${server.address().port}/scene_preview/preview.html`;
    await page.goto(log.entryUrl);
    await page.waitForFunction(() => window.ready, null, { timeout: 30000 });
    failIfNeeded();
    await page.evaluate(() => window.captureBReference());
    await save('S31_B_F180_CLEAN.png');
    const meta = [];
    for (const f of [0, 116]) {
      meta.push(await page.evaluate(f => window.renderFrame(f), f));
      await save(`S31_A_F${String(f).padStart(3, '0')}_ACTUAL_SCENE.png`);
    }
    log.boundary = await page.evaluate(() => window.checkBAfterA());
    fs.writeFileSync(path.join(__dirname, 'A_TO_B_ISOLATION_CHECK.json'), JSON.stringify(log.boundary, null, 2));
    await save('S31_B_F180_AFTER_A.png');
    fs.writeFileSync(path.join(__dirname, 'ACTUAL_SCENE_REGISTRATION.json'), JSON.stringify(meta, null, 2));
    failIfNeeded();
    if (log.boundary.some(r => !r.exactMatch || r.differingChannels !== 0 || r.maxAbsoluteDifference !== 0)) throw new Error('Original B180 changed after A: pixel-isolation test FAILED');
    log.status = 'passed';
  } catch (e) {
    log.status = 'failed'; log.error = String(e.stack || e); throw e;
  } finally {
    if (browser) await browser.close();
    if (server.listening) await new Promise(ok => server.close(ok));
    fs.writeFileSync(path.join(__dirname, 'RENDER_EXECUTION_LOG.json'), JSON.stringify(log, null, 2));
    console.log(JSON.stringify({ status: log.status, pngs: log.pngs, boundary: log.boundary, httpFailures: log.responses.filter(r => !r.ok), requestFailed: log.requestFailed, pageErrors: log.pageErrors }, null, 2));
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
