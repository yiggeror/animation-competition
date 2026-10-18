// Prepared locally, never executed locally. Run inside the authorized cloud repo.
// Verifies full 120-frame Canvas equivalence; does not grant visual approval/ready.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert/strict');
const {createRequire} = require('module');
const {spawnSync} = require('child_process');
const PACK = path.resolve(__dirname, '..');
const ROOT = path.resolve(process.argv[2] || process.cwd());
const REL = path.relative(ROOT, PACK).split(path.sep).join('/');
const OUT = path.resolve(process.argv[3] || path.join(PACK, 'cloud_actual_' + new Date().toISOString().replace(/[-:.]/g, '')));
const SOURCE = 'collab/reviews/cloud_s22_20261018/scene_integration_120';
const COMPARE_MODE = process.env.S22_COMPARE_MODE || 'historical';
const SOURCE_MODULE_SHA = 'a5d4596d86e9e8a485b70ad3f567716ee6878637f96236b4003a59c42d659d1f';
const readJSON = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const run = (cmd, args, options = {}) => {
  const r = spawnSync(cmd, args, {encoding: 'utf8', ...options});
  if (r.error || r.status !== 0) throw new Error(`${cmd} failed: ${r.error || r.stderr || r.status}`);
  return r.stdout;
};
let server, browser;
(async () => {
  assert(['historical', 'paired'].includes(COMPARE_MODE), 'S22_COMPARE_MODE must be historical or paired.');
  assert(REL && !REL.startsWith('../') && !path.isAbsolute(REL), 'Place QA package inside the repository.');
  assert(!fs.existsSync(OUT), 'Choose a new output directory; never overwrite an earlier render.');
  const rows = readJSON(path.join(PACK, 'UPLOAD_ROWS.json'));
  const bindings = readJSON(path.join(PACK, 'SOURCE_ASSET_BINDINGS.json'));
  const depManifest = readJSON(path.join(PACK, 'qa/dependencies.json'));
  const map = readJSON(path.join(ROOT, 'assets/chars/s22/resource_map.json'));
  const lock = readJSON(path.join(ROOT, 'assets/chars/s22/tail_lock.json'));
  const originalManifest = readJSON(path.join(PACK, 'source_snapshot', SOURCE, 'provenance/actual_scene120_manifest.json'));
  for (const row of rows) {
    const b = fs.readFileSync(path.join(ROOT, row.path));
    assert.equal(b.length, row.size, row.path); assert.equal(sha(b), row.sha256, row.path);
  }
  for (const row of depManifest.files) assert.equal(sha(fs.readFileSync(path.join(ROOT, row.path))), row.sha256, 'Shared dependency changed: ' + row.path);
  for (const row of depManifest.files) if (row.path.startsWith('js/')) assert.equal(sha(fs.readFileSync(path.join(PACK, 'source_snapshot', row.path))), row.sha256, 'Snapshot dependency changed: ' + row.path);
  assert.equal(sha(fs.readFileSync(path.join(PACK, 'source_snapshot', SOURCE, 'S22_drawn.js'))), SOURCE_MODULE_SHA);
  assert.equal(lock.status, 'approved');
  for (const id of ['F108', 'F114']) assert.equal(lock.approved_final_RGBA[id], map.exposures.find(r => r.id === id).sha256);
  fs.mkdirSync(path.join(OUT, 'frames'), {recursive: true});
  fs.mkdirSync(path.join(OUT, 'decoded_actual'), {recursive: true});
  const repoRequire = createRequire(path.join(ROOT, 'package.json'));
  const {chromium} = repoRequire('playwright');
  const {start} = require(path.join(ROOT, 'tools/js/serve.cjs'));
  server = await start(0);
  const base = `http://127.0.0.1:${server.address().port}`;
  const executablePath = process.env.CHROMIUM_PATH || ['/usr/bin/chromium', '/usr/bin/chromium-browser'].find(p => fs.existsSync(p));
  browser = await chromium.launch({...(executablePath ? {executablePath} : {}), headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage']});
  const captures = [];
  for (const kind of (COMPARE_MODE === 'paired' ? ['production', 'reference'] : ['production'])) {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
    const errors = [], http = [], interceptedOriginalPNGs = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('requestfailed', r => errors.push(r.url() + ': ' + r.failure()?.errorText));
    page.on('response', r => http.push({url: r.url(), status: r.status()}));
    await page.route('**/*', async route => {
      const u = new URL(route.request().url());
      if (u.origin !== base) { errors.push('Unexpected external request: ' + u.href); return route.abort(); }
      if (kind === 'production' && u.pathname.startsWith('/collab/')) { errors.push('Forbidden production review request: ' + u.href); return route.abort(); }
      // Reference imports the unchanged e2601ed module and unchanged helper bytes.
      // Map its original PNG URL to the SHA-proven identical production bytes.
      const binding = kind === 'reference' && bindings.assets.find(r => '/' + r.source_path === u.pathname);
      if (binding) {
        const data = fs.readFileSync(path.join(ROOT, binding.production_path));
        assert.equal(sha(data), binding.sha256);
        interceptedOriginalPNGs.push({source: binding.source_path, production: binding.production_path, sha256: binding.sha256});
        return route.fulfill({status: 200, contentType: 'image/png', body: data});
      }
      return route.continue();
    });
    const mod = kind === 'production' ? 'js/anim/s22_drawn.js' : `${REL}/source_snapshot/${SOURCE}/S22_drawn.js`;
    await page.goto(base + '/dev/view.html?mod=' + encodeURIComponent(mod) + '&w=1920&h=1080');
    await page.waitForFunction(() => window.__ready || window.__error, null, {timeout: 60000});
    const error = await page.evaluate(() => window.__error); if (error) throw Error(error);
    const preflight = await page.evaluate(async modulePath => (await import('/' + modulePath)).preflight(), mod);
    assert.equal(preflight.drawings, 12);
    const frames = [];
    for (let f = 0; f < 120; f++) {
      const data = await page.evaluate(async t => { await window.renderFrame(t); return document.querySelector('canvas').toDataURL('image/png'); }, f / 24);
      const bytes = Buffer.from(data.split(',')[1], 'base64');
      const filename = String(f).padStart(5, '0') + '.png';
      if (kind === 'production') fs.writeFileSync(path.join(OUT, 'frames', filename), bytes);
      frames.push({frame: f, file: filename, sha256: sha(bytes)});
      if ((f + 1) % 24 === 0) console.log(`${kind}: ${f + 1}/120 actual Canvas frames`);
    }
    await page.close();
    assert.equal(errors.length, 0, errors.join('\n'));
    assert.equal(http.filter(r => r.status >= 400 && /\.(png|js|json|ttf)(\?|$)/.test(r.url)).length, 0, 'Resource HTTP failure');
    if (kind === 'reference') assert.equal(interceptedOriginalPNGs.length, 12);
    captures.push({kind, module: mod, frames, preflight, http, errors, interceptedOriginalPNGs});
  }
  await browser.close(); browser = null; server.close(); server = null;
  const paired = captures[0].frames.map((r, i) => { const ref = COMPARE_MODE === 'paired' ? captures[1].frames[i].sha256 : originalManifest.frame_sha256[i].sha256; return {frame: i, production: r.sha256, reference: ref, same: r.sha256 === ref, same_as_historical_e2601ed: r.sha256 === originalManifest.frame_sha256[i].sha256}; });
  fs.writeFileSync(path.join(OUT, 'canvas_comparison.json'), JSON.stringify({mode: COMPARE_MODE, frames: paired, captures}, null, 2) + '\n');
  assert(paired.every(r => r.same), COMPARE_MODE === 'historical' ? 'Production PNG differs from fixed e2601ed ledger. Preserve this output and check that Chromium/cloud environment matches the source render; no automatic duplicate source render was run. Only if historical environment cannot be matched, use explicitly selected S22_COMPARE_MODE=paired for a same-runtime differential diagnosis.' : 'Actual Canvas PNG bytes differ between migrated and fixed e2601ed modules.');
  const clip = path.join(OUT, 'S22_production_scene120.mp4');
  run('ffmpeg', ['-v', 'error', '-framerate', '24', '-i', path.join(OUT, 'frames/%05d.png'), '-frames:v', '120', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', clip]);
  const probe = JSON.parse(run('ffprobe', ['-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', clip]));
  assert.equal(probe.streams.length, 1); assert.equal(probe.streams[0].codec_type, 'video');
  assert.equal(+probe.streams[0].nb_read_frames, 120); assert.equal(+probe.format.duration, 5);
  assert.equal(probe.streams[0].width, 1920); assert.equal(probe.streams[0].height, 1080); assert.equal(probe.streams[0].r_frame_rate, '24/1');
  const selected = Array.from(new Set(map.exposures.flatMap(r => [r.start, r.end]))).sort((a, b) => a - b);
  for (const f of selected) run('ffmpeg', ['-v', 'error', '-i', clip, '-vf', `select=eq(n\\,${f})`, '-frames:v', '1', path.join(OUT, 'decoded_actual', 'F' + String(f).padStart(3, '0') + '.png')]);
  const result = {status: COMPARE_MODE === 'historical' ? 'PASS_HISTORICAL_CANVAS_EQUIVALENCE_ONLY' : 'PASS_PAIRED_CANVAS_EQUIVALENCE_ONLY', comparison_mode: COMPARE_MODE, source_commit: bindings.source_commit, source_module_sha256: SOURCE_MODULE_SHA, production_module_sha256: bindings.production_module_sha256, canvas_png_matches: paired.filter(r => r.same).length, historical_png_matches: paired.filter(r => r.same_as_historical_e2601ed).length, historical_match_note: 'Default requires 120/120 equality against the e2601ed original Canvas PNG ledger and renders production only. Paired fallback is explicitly selected only when source environment cannot be reproduced.', clip: path.relative(ROOT, clip), clip_sha256: sha(fs.readFileSync(clip)), ffprobe: probe, captures, decoded_boundary_frames: selected, whole_scene_visual_review: 'NOT_PERFORMED_BY_THIS_SCRIPT', audio_integrated: false, production_ready: false};
  fs.writeFileSync(path.join(OUT, 'actual_cloud_checks.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({status: result.status, comparison_mode: result.comparison_mode, canvas_png_matches: result.canvas_png_matches, clip: result.clip, clip_sha256: result.clip_sha256, production_ready: false}, null, 2));
})().catch(e => {console.error(e.stack || e); process.exitCode = 1;}).finally(async () => {if (browser) await browser.close(); if (server) server.close();});
