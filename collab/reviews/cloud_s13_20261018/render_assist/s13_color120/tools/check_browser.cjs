// Probe the fixed checkout's actual browser resources and all16 exposure selections.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {execFileSync}=require('child_process');
const {chromium}=require('playwright');
const ROOT=process.cwd(),P=path.resolve(__dirname,'..');
const FIXED='06a588dfbcb0124dfeaee563bcde07613f6bf5f6';
const {start}=require(path.join(ROOT,'tools/js/serve.cjs'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const server=await start(0);let browser;
 try {
  browser=await chromium.launch();const page=await browser.newPage();
  const responses=new Map(),errors=[];let generatedResourceResponses=0;
  page.on('response',r=>{const u=new URL(r.url());if(u.protocol==='http:'&&u.hostname==='127.0.0.1')responses.set(u.pathname,r.status());else generatedResourceResponses++;});
  page.on('pageerror',e=>errors.push(e.message));
  const base=`http://127.0.0.1:${server.address().port}`;
  await page.goto(base+'/dev/view.html?mod=%2Fjs%2Fanim%2Fs13_drawn.js&w=1280&h=720');
  await page.waitForFunction(()=>window.__ready===true||window.__error,null,{timeout:60000});
  const error=await page.evaluate(()=>window.__error);if(error)throw Error(error);
  const starts=[0,18,24,30,36,40,44,50,58,68,78,84,87,90,94,100];
  const state=await page.evaluate(async starts=>{
   const mod=await import('/js/anim/s13_drawn.js');
   const result=[];for(const f of starts){await window.renderFrame(f/24);result.push(mod.state(f/24));}
   return {duration:mod.DURATION,placement:mod.PLACEMENT,states:result,all120:Array.from({length:120},(_,f)=>mod.state(f/24))};
  },starts);
  if(state.duration!==5||state.states.length!==16)throw Error('duration/exposure mismatch');
  const urls=[...responses.keys()].filter(p=>p!='/favicon.ico');
  const hashes=await page.evaluate(async urls=>{
   // dev/view.html imports ../ plus an absolute /js path, yielding a valid same-origin //js pathname.
   // Prefix the origin explicitly: fetch('//js/...') alone would incorrectly address host "js".
   const out=[];for(const url of urls){let r;try{r=await fetch(location.origin+url);}catch(e){throw Error('Resource fetch '+url+':'+e.message);}const data=await r.arrayBuffer();
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(x=>x.toString(16).padStart(2,'0')).join('');
    out.push({path:url,status:r.status,bytes:data.byteLength,sha256:hash});}
   return out;
  },urls);
  for(const r of hashes){
   const file=path.join(ROOT,r.path),disk=fs.readFileSync(file);
   const git=execFileSync('git',['show',FIXED+':'+r.path.replace(/^\/+/, '')],{maxBuffer:64*1024*1024});
   if(r.status!==200||r.sha256!==sha(disk)||r.sha256!==sha(git))throw Error('resource mismatch:'+r.path);
   r.exact_fixed_git_and_disk=true;
  }
  for(const f of starts){if(!hashes.some(r=>r.path===`/assets/chars/x13/F${String(f).padStart(3,'0')}.png`))throw Error('missing native image'+f);}
  if(!hashes.some(r=>r.path==='/assets/paint/bg_01_room_wide.png'))throw Error('missing actual room');
  if(errors.length)throw Error(errors.join('\n'));
  for(const [url,status] of responses){if(status!==200&&url!='/favicon.ico')throw Error('required HTTP'+status+':'+url);}
  fs.writeFileSync(path.join(P,'browser_resources.json'),JSON.stringify({fixed_commit:FIXED,status:'PASS_ALL16_BROWSER_RESOURCES_AND_EXPOSURES',page_errors:errors,nonessential_favicon404:responses.get('/favicon.ico')===404,generated_resource_responses_excluded_from_disk_hash_probe:generatedResourceResponses,browser:await browser.version(),...state,resources:hashes},null,2)+'\n');
  console.log('PASS all16 runtime PNG + background/font/JS resource SHA agree with fixed Git;120 exposure selections;page errors0');
 } finally {if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
