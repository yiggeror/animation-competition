// Authorized S07-only continuation. Original source, Chromium flags, Canvas defaults and strict sample gates.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{spawn}=require('child_process'),{once}=require('events'),{chromium}=require('playwright');
const root=process.cwd(),meta=__dirname,out=process.env.OPENING_OUTPUT_DIR||'/tmp/opening-s07-fresh-c5753892-20261019',dir=path.join(out,'S07');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),now=()=>new Date().toISOString();
const expected=JSON.parse(fs.readFileSync(path.join(root,'collab/reviews/20261019_1203_opening_full_gate/EXPECTED.json')));
const keyframes=[0,2,3,5,6,7,8,15,16,38,39,42,43,45,46,48,49,52,53,56,57,99,100,102,103,105,106,107];
const flags=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'];
const report={source_commit:'c57538925035118c0f8901fc2f22f478fbf803b4',started_utc:now(),pid:process.pid,state:'STARTING',width:1920,height:1080,fps:24,audio:false,total_frames:108,completed_frames:0,frames_sent_to_encoder:0,fresh_page:true,new_canvas:true,prior_S01_S04_render_calls:0,canvas_context_creation:'getContext("2d") with no options',chromium_flags:flags,output_dir:out,sourceChecks:[],approvedSampleChecks:[],http:[],errors:[],console:[],new_imagegen_calls:0};
let browser,server,activeFf,ffDone;
const state=()=>fs.writeFileSync(path.join(meta,'RUN_STATE.json'),JSON.stringify(report,null,2)+'\n');
(async()=>{
 if(fs.existsSync(out))throw Error('Output directory exists; refuse duplicate/overwrite continuation');
 fs.mkdirSync(dir,{recursive:true});
 for(const [p,want]of Object.entries(expected.sources)){const actual=hash(fs.readFileSync(path.join(root,p)));report.sourceChecks.push({path:p,sha256:actual,expected:want,pass:actual===want});}
 if(report.sourceChecks.some(x=>!x.pass))throw Error('Frozen production source mismatch');
 state();
 server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost');if(u.pathname==='/__opening_s07_fresh__.html'){res.setHeader('Content-Type','text/html');return res.end('<!doctype html><link rel="icon" href="data:,"><canvas width="1920" height="1080"></canvas>');}const p=path.resolve(root,'.'+decodeURIComponent(u.pathname));if(!p.startsWith(root+path.sep)){res.writeHead(403);return res.end();}try{res.setHeader('Content-Type',p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'application/octet-stream');res.end(fs.readFileSync(p));}catch(e){res.writeHead(404);res.end();}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));report.http_origin='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:flags});
 const page=await browser.newPage({viewport:{width:1920,height:1080}});
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+' '+r.failure()?.errorText));page.on('response',r=>report.http.push({url:r.url(),status:r.status()}));page.on('console',m=>report.console.push({type:m.type(),text:m.text()}));
 await page.goto(report.http_origin+'/__opening_s07_fresh__.html');
 // Same preload as successful finite fresh-sequence diagnostic; only S07 is rendered.
 await page.evaluate(async()=>{window.mods={};for(const s of ['S01','S04','S07'])window.mods[s]=await import('/js/anim/'+s.toLowerCase()+'_drawn.js');});
 const movie=path.join(dir,'S07_opening_corrected_1080p24.mp4');
 activeFf=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',movie],{stdio:['pipe','ignore',fs.openSync(path.join(dir,'ffmpeg.log'),'w')]});
 ffDone=once(activeFf,'close');activeFf.stdin.on('error',()=>{});report.ffmpeg_pid=activeFf.pid;report.state='RENDERING';state();
 const rows=[];
 for(let frame=0;frame<108;frame++){
  const data=await page.evaluate(async frame=>{const c=document.querySelector('canvas'),ctx=c.getContext('2d');await window.mods.S07.renderFrame(ctx,frame/24,1920,1080);return {png:c.toDataURL('image/png'),attributes:ctx.getContextAttributes()};},frame);
  const b=Buffer.from(data.png.split(',')[1],'base64'),name='S07_F'+String(frame).padStart(3,'0')+'.png',sha256=hash(b);
  rows.push({frame,sha256});report.completed_frames=frame+1;report.latest_frame=frame;report.context_attributes=data.attributes;
  if(keyframes.includes(frame))fs.writeFileSync(path.join(dir,name),b);
  fs.writeFileSync(path.join(dir,'FRAME_LEDGER.json'),JSON.stringify(rows,null,2)+'\n');
  if(expected.samples[name]){const pass=sha256===expected.samples[name];report.approvedSampleChecks.push({name,sha256,expected:expected.samples[name],pass});state();console.log(JSON.stringify({gate:name,sha256,pass}));if(!pass){fs.writeFileSync(path.join(dir,'FAILED_SAMPLE_'+name),b);throw Error('Approved five-frame migration mismatch '+name);}}
  if(!activeFf.stdin.write(b))await once(activeFf.stdin,'drain');report.frames_sent_to_encoder=frame+1;state();
  if(frame%12===0||frame===107)console.log(JSON.stringify({shot:'S07',completed:frame+1,total:108,pid:process.pid}));
 }
 report.state='ENCODING_FINALIZATION';state();activeFf.stdin.end();const [code]=await ffDone;activeFf=null;if(code!==0)throw Error('ffmpeg failed '+code);
 const names=report.approvedSampleChecks.map(x=>x.name);if(names.length!==5||report.approvedSampleChecks.some(x=>!x.pass))throw Error('Five strict approved sample checks incomplete');
 if(report.errors.length||report.http.some(x=>x.status>=400)||report.http.some(x=>new URL(x.url).pathname.includes('/reviews/')))throw Error('HTTP/page/source-path check failed');
 const check={shot:'S07',frames:108,duration:4.5,file:'S07/S07_opening_corrected_1080p24.mp4',sha256:hash(fs.readFileSync(movie)),approvedSampleChecks:report.approvedSampleChecks,keyframes};
 fs.writeFileSync(path.join(dir,'CLIP_CHECK.json'),JSON.stringify(check,null,2)+'\n');report.clip=check;report.state='COMPLETED';report.exit_code=0;
})().catch(e=>{report.state='FAILED';report.error=String(e.stack||e);report.exit_code=1;console.error(e);process.exitCode=1;}).finally(async()=>{
 if(activeFf){activeFf.stdin.destroy();activeFf.kill('SIGTERM');await ffDone.catch(()=>{});}
 if(browser)await browser.close();if(server)await new Promise(r=>server.close(r));
 report.finished_utc=now();report.browser_and_http_stopped=true;report.sourceChecksAfter=Object.entries(expected.sources).map(([p,want])=>({path:p,sha256:hash(fs.readFileSync(path.join(root,p))),expected:want,pass:hash(fs.readFileSync(path.join(root,p)))===want}));
 if(report.sourceChecksAfter.some(x=>!x.pass)){report.state='FAILED';report.exit_code=1;report.error='Frozen production source changed during render';process.exitCode=1;}
 state();fs.writeFileSync(path.join(out,'S07_FRESH_CHECK.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,exit_code:report.exit_code,pid:process.pid,completed_frames:report.completed_frames}));
});
