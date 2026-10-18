// Audit the exact candidate module in the same repository HTTP/Canvas environment.
const { chromium } = require('playwright');
const { start } = require('../../../../../tools/js/serve.cjs');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../../../..');
const OUT = path.resolve(__dirname, '../qa/browser_audit.json');
const mod = 'collab/reviews/cloud_s13_20261018/full_scene/s13_drawn.js';
(async () => {
  const srv = await start(0), b = await chromium.launch({ executablePath: '/usr/bin/chromium' });
  const page = await b.newPage();
  const httpErrors = [], pageErrors = [];
  page.on('response', r => { if(r.status() >= 400) httpErrors.push({url:new URL(r.url()).pathname,status:r.status()}); });
  page.on('pageerror', e => pageErrors.push(String(e)));
  await page.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=${mod}&w=1280&h=720`);
  await page.waitForFunction(() => window.__ready || window.__error);
  const result = await page.evaluate(async mod => {
    if(window.__error) throw Error(window.__error);
    const m = await import('/' + mod), states = [];
    // Render one frame from every state, making every character asset and scene dependency load.
    for(const [,f] of m.SHEET) await window.renderFrame(f/24);
    for(let f=0;f<120;f++) states.push(m.state(f/24));
    return {duration:window.DURATION,sheet:m.SHEET,placement:m.PLACEMENT,states,canvas:[document.getElementById('c').width,document.getElementById('c').height]};
  }, mod);
  await b.close(); await new Promise(r => srv.close(r));
  result.browser = 'system Chromium'; result.chromium_version = b.version();
  result.module = mod; result.http_errors = httpErrors; result.page_errors = pageErrors;
  result.root = ROOT;
  if(pageErrors.length || httpErrors.some(r => r.url !== '/favicon.ico')) throw Error(JSON.stringify({pageErrors,httpErrors}));
  fs.writeFileSync(OUT,JSON.stringify(result,null,2)+'\n');
  console.log('PASS:16 scene states rendered in browser;120 selector states; no required-asset/page errors.');
})().catch(e=>{console.error(e);process.exit(1)});
