// Diagnose the render log's anonymous 404 without changing any source or clip.
const fs = require('fs');
const path = require('path');
require('../use_system_chromium.cjs');
const { chromium } = require('playwright');
const { start } = require('/workspace/s03a-color-render-f17651aa/tools/js/serve.cjs');
(async () => {
  const server = await start(0), requests = [], errors = [];
  server.on('request', (req, res) => res.on('finish', () => requests.push({path:req.url, status:res.statusCode})));
  const browser = await chromium.launch();
  const page = await browser.newPage({viewport:{width:400,height:300}});
  page.on('console', m => { if (m.type()==='error') errors.push(m.text()); });
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js%2Fanim%2Fs03a_drawn.js&w=1280&h=720`);
  await page.waitForFunction(() => window.__ready || window.__error);
  const error = await page.evaluate(() => window.__error);
  if (error) throw Error(error);
  for (const frame of [0,14,17,25]) await page.evaluate(f => window.renderFrame(f/24), frame);
  await browser.close();
  await new Promise(resolve => server.close(resolve));
  const report = {fixed_commit:'f17651aaee6f03cf0e48bd2939c4c6c1fb86cffb', frames_exercised:[0,14,17,25], requests, console_errors:errors, HTTP_errors:requests.filter(r=>r.status>=400), source_edits:false};
  fs.writeFileSync(path.join(__dirname,'resource_probe.json'), JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report.HTTP_errors));
})();
