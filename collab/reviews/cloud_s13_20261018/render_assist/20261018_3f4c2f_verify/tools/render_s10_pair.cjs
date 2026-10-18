// Real browser Canvas render of eight migration checkpoints for both fixed modules.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'/tmp/s13_render_assist_3f4c2f');
const out=path.resolve(__dirname,'..');
const commit='3f4c2f187daaeacc6b26e26260e426823f2fa6ad';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
if(git('rev-parse','HEAD')!==commit||git('status','--porcelain','-uno'))throw Error('Fixed checkout is not clean at requested commit');
const {start}=require(path.join(root,'tools/js/serve.cjs'));
const frames=[0,24,27,30,33,45,72,96];
const modules={new:'js/anim/s10_drawn.js',old:'collab/reviews/cloud_s10_20261018/F072_096_full120/S10_drawn_full_candidate.js'};
(async()=>{
 const srv=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium'});
 const result={fixed_commit:commit,width:1920,height:1080,frame_numbers:frames,chromium:browser.version(),playwright:require('playwright/package.json').version,modules:{}};
 for(const [name,mod]of Object.entries(modules)){
  const page=await browser.newPage(),resources=[],pageErrors=[],consoleErrors=[],failed=[];
  page.on('pageerror',e=>pageErrors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
  page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));
  const onResponse=r=>resources.push({path:new URL(r.url()).pathname,status:r.status()});
  page.on('response',onResponse);
  await page.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=${encodeURIComponent(mod)}&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready||window.__error);
  const error=await page.evaluate(()=>window.__error);if(error)throw Error(error);
  const states=[];
  for(const f of frames){
   const rendered=await page.evaluate(async({f,mod})=>{const m=await import('/'+mod);await window.renderFrame(f/24);return{data:document.getElementById('c').toDataURL('image/png'),duration:window.DURATION,exposure:m.EXPOSURES.find(r=>f>=r.start&&f<=r.end)}},{f,mod});
   const bytes=Buffer.from(rendered.data.split(',')[1],'base64'),filename=`S10_${name}/F${String(f).padStart(3,'0')}.png`;
   fs.writeFileSync(path.join(out,filename),bytes);states.push({frame:f,time:f/24,file:filename,sha256:sha(bytes),bytes:bytes.length,duration:rendered.duration,exposure:rendered.exposure});
  }
  page.off('response',onResponse);
  const required=resources.filter(r=>r.path!='/favicon.ico');
  // Browser-native fetch avoids DevTools inspector-body eviction for large fonts/bitmaps.
  const bodyAudit=await page.evaluate(async paths=>Promise.all(paths.map(async p=>{const r=await fetch(p,{cache:'no-store'}),data=await r.arrayBuffer(),digest=await crypto.subtle.digest('SHA-256',data);return{path:p,status:r.status,bytes:data.byteLength,response_sha256:Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('')}})),[...new Set(required.map(r=>r.path))]);
  for(const row of bodyAudit){const disk=path.join(root,decodeURIComponent(row.path)),rel=path.relative(root,disk);row.disk_sha256=sha(fs.readFileSync(disk));row.response_equals_fixed_disk=row.response_sha256===row.disk_sha256;row.git_blob=git('rev-parse',commit+':'+rel);row.disk_git_blob=git('hash-object',disk);}
  if(pageErrors.length||failed.length||required.some(r=>r.status!==200)||bodyAudit.some(r=>r.status!==200||r.git_blob!==r.disk_git_blob||!r.response_equals_fixed_disk))throw Error(JSON.stringify({name,pageErrors,failed,resources,bodyAudit}));
  result.modules[name]={path:mod,module_git_blob:git('rev-parse',commit+':'+mod),renders:states,resources,browser_native_fetch_body_audit:bodyAudit,page_errors:pageErrors,console_errors:consoleErrors,request_failures:failed};
  await page.close();console.log(name+':8 actual Canvas frames; required resources match fixed commit.');
 }
 await browser.close();await new Promise(r=>srv.close(r));
 result.byte_comparisons=frames.map(f=>{const n=`F${String(f).padStart(3,'0')}.png`,a=fs.readFileSync(path.join(out,'S10_new',n)),b=fs.readFileSync(path.join(out,'S10_old',n));return{frame:f,new_sha256:sha(a),old_sha256:sha(b),byte_identical:a.equals(b)}});
 fs.writeFileSync(path.join(out,'S10_render_and_resources.json'),JSON.stringify(result,null,2)+'\n');
 if(result.byte_comparisons.some(r=>!r.byte_identical))throw Error('Migration PNG mismatch; evidence preserved.');
 console.log('PASS:8/8 new-vs-old actual1920×1080 PNGs byte-identical.');
})().catch(e=>{console.error(e);process.exit(1)});
