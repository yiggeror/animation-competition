// Run from the original repository root, after the coordinator installs the candidate and exact raw assets.
// node collab/reviews/20261019_2226_s30_complete_scene_gate/render_repository_keyframes.cjs [--all]
const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const {spawn} = require('child_process'), {once} = require('events'), {chromium} = require('playwright');
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
(async () => {
  const root = process.cwd(), out = path.join(__dirname, 'actual_browser_frames');
  fs.mkdirSync(out, {recursive:true});
  const man = JSON.parse(fs.readFileSync(path.join(__dirname, 'RAW_ASSET_REUSE_SHA.json')));
  const report = {status:'STARTED', frames:0, all288:process.argv.includes('--all'), rawSHAverified:0,
    sharedHelpersModified:false, edlModified:false, errors:[], missing:[], httpFailures:[], requestFailures:[], favicon:[], states:[], isolation:[]};
  let server, browser, ff, ffDone;
  const save = () => fs.writeFileSync(path.join(out, 'ACTUAL_BROWSER_RENDER_REPORT.json'), JSON.stringify(report, null, 2));
  try {
    report.scriptPath=path.relative(root,__filename);report.modulePath=man.module_destination;
    report.moduleSHA=sha(fs.readFileSync(path.join(root,man.module_destination)));
    if(man.candidate_module_sha256&&report.moduleSHA!==man.candidate_module_sha256)throw Error('Candidate module SHA mismatch');
    for (const a of man.assets) {
      if (sha(fs.readFileSync(path.join(root, a.destination_repo_path))) !== a.sha256) throw Error('Original SHA mismatch '+a.pose);
      report.rawSHAverified++;
    }
    for (const [file, hash] of Object.entries(man.expected_unchanged_helpers || {})) {
      if (sha(fs.readFileSync(path.join(root, file))) !== hash) throw Error('Original helper changed: '+file);
    }
    for (const [file, meta] of Object.entries(man.preexisting_assets || {})) {
      if (sha(fs.readFileSync(path.join(root, file))) !== meta.sha256) throw Error('Original background/shadow asset changed: '+file);
    }
    server = http.createServer((req, res) => {
      let u; try {u=decodeURIComponent(new URL(req.url, 'http://localhost').pathname)} catch {res.writeHead(400);res.end();return;}
      if (u === '/favicon.ico') {report.favicon.push({path:u,status:204,excludedFromSceneErrors:true});res.writeHead(204);res.end();return;}
      if (u === '/__s30_preview.html') {
        res.setHeader('Content-Type','text/html');
        res.end('<html><body style="margin:0;background:black"><canvas id="c" width="1920" height="1080"></canvas><script type="module">window.s30=await import("/js/paint/shots/s30_drawn.js");window.ready=true</script></body></html>');return;
      }
      const p=path.resolve(root, '.'+u);
      if (!p.startsWith(root+path.sep)) {res.writeHead(403);res.end();return;}
      fs.readFile(p, (e,b) => {
        if (e) {report.missing.push(u);res.writeHead(404);res.end();return;}
        res.setHeader('Content-Type', ({'.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg','.json':'application/json'})[path.extname(p)] || 'application/octet-stream');res.end(b);
      });
    });
    await new Promise((ok,no) => {server.once('error',no);server.listen(0,'127.0.0.1',ok)});
    report.previewURL=`http://127.0.0.1:${server.address().port}/__s30_preview.html`;
    report.moduleURL=`http://127.0.0.1:${server.address().port}/js/paint/shots/s30_drawn.js`;
    const executablePath=process.env.CHROMIUM_PATH || (fs.existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined);
    browser=await chromium.launch({headless:true,executablePath,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
    const page=await browser.newPage({viewport:{width:1920,height:1080}});
    page.on('pageerror',e=>report.errors.push(String(e)));
    page.on('requestfailed',r=>report.requestFailures.push({url:r.url(),failure:r.failure()}));
    page.on('response',r=>{if(r.status()>=400)report.httpFailures.push({url:r.url(),status:r.status()})});
    await page.goto(report.previewURL);
    await page.waitForFunction(()=>window.ready, {timeout:30000});
    const render=async f=>page.evaluate(async f=>{
      const c=document.getElementById('c');await window.s30.renderFrame(c.getContext('2d'),f/24,c.width,c.height);
      const {source,...state}=window.s30.state(f/24);
      return {state:{...state,raw:source?.url},jpeg:c.toDataURL('image/jpeg',.96).split(',')[1]};
    },f);
    const keys=[0,26,27,39,40,54,96,114,120,132,138,143,144,146,147,162,180,189,190,287];
    const frames=report.all288 ? Array.from({length:288},(_,i)=>i) : keys,hashes={};
    if (report.all288) {
      ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-r','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',path.join(out,'S30_COMPLETE_288f_24fps_NO_AUDIO.mp4')]);
      ff.stderr.on('data',b=>report.errors.push('ffmpeg: '+String(b)));
      ffDone=new Promise((ok,no)=>{ff.once('error',no);ff.once('close',code=>code===0?ok():no(Error('ffmpeg failed '+code)))});
      ffDone.catch(()=>{});
    }
    for (const f of frames) {
      const r=await render(f),b=Buffer.from(r.jpeg,'base64');hashes[f]=sha(b);
      if(keys.includes(f))fs.writeFileSync(path.join(out,`F${String(f).padStart(3,'0')}.jpg`),b);
      if(ff&&!ff.stdin.write(b))await once(ff.stdin,'drain');
      report.states.push(r.state);report.frames++;console.log('S30',f);
    }
    if(ff){ff.stdin.end();await ffDone;ff=null;}
    // Cross-renderer diagnostics only: never append these to the 288-frame stream.
    for(const f of [120,190,0,190,120]) {
      const r=await render(f),actual=sha(Buffer.from(r.jpeg,'base64')),pass=actual===hashes[f];
      report.isolation.push({frame:f,expected:hashes[f],actual,pass});
      if(!pass)throw Error('Cross-renderer repeated-frame mismatch '+f);
    }
    report.status=report.errors.length||report.missing.length||report.httpFailures.length||report.requestFailures.length?'ERROR':'RENDERED_FOR_VISUAL_REVIEW';save();
    if(report.status==='ERROR')throw Error('Browser errors/missing assets; inspect report');
  } catch(e) {
    report.status='ERROR';report.errors.push(String(e.stack||e));save();throw e;
  } finally {
    if(ff&&!ff.killed)ff.kill('SIGTERM');
    if(browser)await browser.close();
    if(server?.listening)await new Promise(ok=>server.close(ok));
  }
})().catch(e=>{console.error(e.message);process.exit(1)});
