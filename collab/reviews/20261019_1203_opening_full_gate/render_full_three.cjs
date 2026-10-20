const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawn}=require('child_process'),{once}=require('events'),{chromium}=require('playwright');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'EXPECTED.json'),'utf8'));
const jobs=[{s:'S01',n:84,k:[0,17,18,42,43,60,61,83]},{s:'S04',n:72,k:[0,7,8,14,15,33,34,53,54,71]},{s:'S07',n:108,k:[0,2,3,5,6,7,8,15,16,38,39,42,43,45,46,48,49,52,53,56,57,99,100,102,103,105,106,107]}];
(async()=>{
 const root=process.cwd(),out=process.env.OPENING_OUTPUT_DIR||'/tmp/opening-continuity-full',origin=process.env.OPENING_BASE_URL||'http://127.0.0.1:8199';fs.mkdirSync(out,{recursive:true});
 const sourceRows=Object.entries(expected.sources).map(([p,sha256])=>({path:p,sha256:hash(fs.readFileSync(path.join(root,p))),expected:sha256}));
 if(sourceRows.some(x=>x.sha256!==x.expected))throw Error('Fixed production source hash mismatch');
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 let activeFf=null;
 const report={width:1920,height:1080,fps:24,audio:false,sources:sourceRows,jobs:[],http:[],errors:[]};
 try{const page=await browser.newPage({viewport:{width:1920,height:1080}});page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+' '+r.failure()?.errorText));page.on('response',r=>report.http.push({url:r.url(),status:r.status()}));
 await page.route('**/__opening_full__.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><link rel="icon" href="data:,"><canvas width="1920" height="1080"></canvas>'}));await page.goto(origin+'/__opening_full__.html');
 await page.evaluate(async()=>{window.mods={};for(const s of ['S01','S04','S07'])window.mods[s]=await import('/js/anim/'+s.toLowerCase()+'_drawn.js');});
 for(const job of jobs){
  const dir=path.join(out,job.s);fs.mkdirSync(dir,{recursive:true});const movie=path.join(dir,job.s+'_opening_corrected_1080p24.mp4');const ff=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',movie],{stdio:['pipe','ignore',fs.openSync(path.join(dir,'ffmpeg.log'),'w')]});activeFf=ff;const ffDone=once(ff,'close');ff.stdin.on('error',()=>{});
  const rows=[],samples=[];
  for(let frame=0;frame<job.n;frame++){
   const url=await page.evaluate(async({s,frame})=>{const c=document.querySelector('canvas');await window.mods[s].renderFrame(c.getContext('2d'),frame/24,1920,1080);return c.toDataURL('image/png');},{s:job.s,frame});const b=Buffer.from(url.split(',')[1],'base64'),name=job.s+'_F'+String(frame).padStart(3,'0')+'.png',sha256=hash(b);rows.push({frame,sha256});
   if(job.k.includes(frame))fs.writeFileSync(path.join(dir,name),b);
   if(expected.samples[name]){const pass=sha256===expected.samples[name];samples.push({name,sha256,expected:expected.samples[name],pass});if(!pass)throw Error('Approved seven-frame migration mismatch '+name);}
   if(!ff.stdin.write(b))await once(ff.stdin,'drain');
   if(frame%12===0||frame===job.n-1){fs.writeFileSync(path.join(dir,'FRAME_LEDGER.json'),JSON.stringify(rows,null,2));console.log(JSON.stringify({shot:job.s,completed:frame+1,total:job.n}));}
  }
  ff.stdin.end();const [code]=await ffDone;activeFf=null;if(code!==0)throw Error('ffmpeg failed '+job.s+' '+code);
  const jr={shot:job.s,frames:job.n,duration:job.n/24,file:path.relative(out,movie),sha256:hash(fs.readFileSync(movie)),approvedSampleChecks:samples,keyframes:job.k};report.jobs.push(jr);fs.writeFileSync(path.join(dir,'CLIP_CHECK.json'),JSON.stringify(jr,null,2));console.log(JSON.stringify(jr));
 }
 }finally{if(activeFf){activeFf.stdin.destroy();activeFf.kill('SIGTERM');}await browser.close();fs.writeFileSync(path.join(out,'FULL_THREE_CHECK.json'),JSON.stringify(report,null,2));}
 if(report.jobs.length!==3||report.errors.length||report.http.some(x=>x.status>=400)||report.http.some(x=>new URL(x.url).pathname.includes('/reviews/')))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
