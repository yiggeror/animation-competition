// Render only explicitly requested available S14 frames. Stream one MP4, save few keys.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{spawn,execFileSync}=require('child_process');
const {chromium}=require('playwright'),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const repo=path.resolve(__dirname,'../../..'),out=process.env.S14_OUTPUT_DIR||'/tmp/s14_actual_close_096_131';
const frames=(process.env.S14_FRAMES||'96:131').split(',').flatMap(s=>{const [a,b]=s.split(':').map(Number);return b===undefined?[a]:Array.from({length:b-a+1},(_,i)=>a+i);});
const W=+(process.env.S14_WIDTH||1920),H=W*9/16;
const keys=new Set((process.env.S14_KEYS||'96,101,102,107,108,113,114,119,120,125,126,131').split(',').map(Number));
(async()=>{
 if(fs.existsSync(out))throw Error('Existing output retained; choose a genuinely new authorized segment, never overwrite '+out);
 fs.mkdirSync(out,{recursive:true});
 const log={status:'running',pid:process.pid,startedUTC:new Date().toISOString(),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),width:W,height:H,fps:24,requestedFrames:frames,renderedFrames:[],keyPNGs:[],responses:[],requestFailures:[],pageErrors:[],newGenerationCalls:0};
 const server=http.createServer((req,res)=>{const url=new URL(req.url,'http://localhost');let f=path.resolve(repo,'.'+decodeURIComponent(url.pathname));if(!f.startsWith(repo+path.sep)){res.writeHead(403).end();return;}fs.readFile(f,(err,b)=>{if(err){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg'})[path.extname(f)]||'application/octet-stream');res.end(b);});});
 let browser,ff,ffDone;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
  browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:W,height:H}});page.setDefaultTimeout(180000);
  page.on('pageerror',e=>log.pageErrors.push(e.message));page.on('requestfailed',r=>log.requestFailures.push({url:r.url(),error:r.failure()}));page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));
  await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s14_scene_20261020/preview.html?w=${W}${process.env.S14_ORIGINAL159_TRIAL==='1'?'&trial159=1':''}${process.env.S14_EXISTING_STEP_TRIAL==='1'?'&steps=1':''}${process.env.S14_BACKSTAGE_OCCLUSION==='1'?'&backstage=1':''}${process.env.S14_UNCOVERED_DIAGNOSTIC==='1'?'&uncovered=1':''}`);await page.waitForFunction(()=>window.ready);
  if(process.env.S14_BACKSTAGE_OCCLUSION==='1'){
   log.backstageOcclusion=await page.evaluate(()=>window.measureBackstageOcclusion());
   if(log.backstageOcclusion.visibleHeadAndRaisedArmsPixelsInOriginalRoom!==0)throw Error('Actual original cloth does not fully occlude old upper pose');
  }
  ff=spawn('ffmpeg',['-v','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'S14_ACTUAL_SEGMENT.partial.mp4')],{stdio:['pipe','ignore','pipe']});
  let stderr='';ff.stderr.on('data',b=>stderr+=b);ffDone=new Promise(ok=>ff.on('close',ok));
  for(const f of frames){
   const binding=await page.evaluate(f=>window.drawActualFrame(f),f),b=await page.locator('canvas').screenshot({type:'png'});
   if(log.pageErrors.length||log.requestFailures.length||log.responses.some(r=>r.status>=400))throw Error('Actual browser resource/page failure');
   if(keys.has(f)){const file=`F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,file),b);log.keyPNGs.push({frame:f,file,sha256:sha(b)});}
   if(!ff.stdin.write(b))await new Promise((ok,bad)=>{const drain=()=>{ff.stdin.off('error',fail);ok();},fail=e=>{ff.stdin.off('drain',drain);bad(e);};ff.stdin.once('drain',drain);ff.stdin.once('error',fail);});
   log.renderedFrames.push(binding);if(f%6===0)console.log('S14 actual',f,'/',frames.at(-1));
  }
  ff.stdin.end();const code=await ffDone;ff=null;if(code!==0)throw Error('ffmpeg '+code+': '+stderr);
  const partial=path.join(out,'S14_ACTUAL_SEGMENT.partial.mp4'),video=path.join(out,'S14_ACTUAL_SEGMENT.mp4');
  const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',partial],{encoding:'utf8'}));
  const v=probe.streams.find(s=>s.codec_type==='video');if(+v.nb_read_frames!==frames.length||v.r_frame_rate!=='24/1')throw Error('Actual frame/rate mismatch');
  fs.renameSync(partial,video);log.video={file:path.basename(video),sha256:sha(fs.readFileSync(video)),bytes:fs.statSync(video).size,probe};log.status='TECHNICAL_COMPLETE_PENDING_ACTUAL_VISUAL_REVIEW';
 }catch(e){log.status='FAILED_PRESERVED_NO_AUTOMATIC_RETRY';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(ff){ff.stdin.destroy();ff.kill('SIGTERM');await ffDone;}if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));log.finishedUTC=new Date().toISOString();fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');console.log(JSON.stringify({status:log.status,frames:log.renderedFrames.length,error:log.error,out}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
