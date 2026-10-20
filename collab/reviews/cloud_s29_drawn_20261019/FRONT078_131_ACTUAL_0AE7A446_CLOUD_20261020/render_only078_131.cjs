// Capture only the authorized source tree and global frames 078–131.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {spawn,execFileSync}=require('child_process'),{chromium}=require('playwright');
const root=path.join(__dirname,'source_at_0ae7a446','served_tree');
const out=process.env.S29_ACTUAL_OUT||'/tmp/s29_front078_131_0ae7a446_actual_20261020';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const keys=new Set([78,81,84,89,90,93,96,99,102,108,115,116,119,120,126,131]);
(async()=>{
 if(fs.existsSync(out))throw Error('Existing output preserved; no automatic retry: '+out);
 fs.mkdirSync(out,{recursive:true});
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'MANIFEST.json')));
 const log={status:'RUNNING',startedUTC:new Date().toISOString(),sourceCommit:'0ae7a446d95343b835fb83f77f05eae61dfb6fb6',entry:'/s29-front-078-131-actual.html',globalRange:[78,131],fps:24,width:1920,height:1080,sourceBefore:[],sourceAfter:[],responses:[],requestFailures:[],pageErrors:[],frames:[],keyPNGs:[],newImageCalls:0,patchApplied:false};
 const sourceHashes=()=>manifest.files.map(r=>{const b=fs.readFileSync(path.join(root,r.repo_target)),actualSHA256=sha(b);if(actualSHA256!==r.sha256)throw Error('Frozen dependency changed: '+r.repo_target);return{path:r.repo_target,sha256:actualSHA256,bytes:b.length};});
 log.sourceBefore=sourceHashes();
 const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost'),f=path.resolve(root,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(root+path.sep)){res.writeHead(403).end();return;}fs.readFile(f,(e,b)=>{if(e){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.json':'application/json','.png':'image/png'})[path.extname(f)]||'application/octet-stream');res.end(b);});});
 let browser,ff,ffDone;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
  browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);
  page.on('pageerror',e=>log.pageErrors.push(e.message));page.on('requestfailed',r=>log.requestFailures.push({url:r.url(),failure:r.failure()}));page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));
  await page.goto(`http://127.0.0.1:${server.address().port}${log.entry}`);await page.waitForFunction(()=>window.ready===true);
  ff=spawn('ffmpeg',['-n','-v','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'S29_ACTUAL078_131_54F.partial.mp4')],{stdio:['pipe','ignore','pipe']});
  let ffError='';ff.stderr.on('data',b=>ffError+=b);ffDone=new Promise(ok=>ff.on('close',ok));
  for(let f=78;f<=131;f++){
   const result=await page.evaluate(async f=>{
    const data=await window.captureActualS29(f);
    let exposure;
    if(f<90)exposure=(await import('/js/anim/s29/exposure.js')).resolveFrame(f);
    else if(f<116)exposure=(await import('/js/anim/s29/front_fold_exposure.js')).resolveFrame(f);
    else exposure=(await import('/js/anim/s29/wrap_tail.js')).WRAP_TAIL_EXPOSURE.find(r=>f>=r.first&&f<=r.last);
    return{data,lastActual:window.lastActual,exposure};
   },f);
   if(log.pageErrors.length||log.requestFailures.length||log.responses.some(r=>r.status>=400))throw Error('Actual source browser error');
   const b=Buffer.from(result.data.split(',')[1],'base64');
   if(b.readUInt32BE(16)!==1920||b.readUInt32BE(20)!==1080)throw Error('Captured canvas dimensions wrong');
   const url=result.exposure.url||`/assets/chars/s29_tail/${result.exposure.file}.png`,sourceSHA256=sha(fs.readFileSync(path.join(root,url)));
   log.frames.push({...result.lastActual,exposure:result.exposure,sourceURL:url,sourceSHA256,actualPNG_SHA256:sha(b)});
   if(keys.has(f)){const file=`F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,file),b);log.keyPNGs.push({globalFrame:f,file,sha256:sha(b)});}
   if(!ff.stdin.write(b))await new Promise((ok,bad)=>{const done=()=>{ff.stdin.off('error',fail);ok();},fail=e=>{ff.stdin.off('drain',done);bad(e);};ff.stdin.once('drain',done);ff.stdin.once('error',fail);});
   if(f%6===0)console.log('S29 actual global',f,'/131');
  }
  ff.stdin.end();const code=await ffDone;ff=null;if(code!==0)throw Error('ffmpeg '+code+': '+ffError);
  log.sourceAfter=sourceHashes();
  if(JSON.stringify(log.sourceBefore)!==JSON.stringify(log.sourceAfter))throw Error('Source mutation during capture');
  const partial=path.join(out,'S29_ACTUAL078_131_54F.partial.mp4'),final=path.join(out,'S29_ACTUAL078_131_54F.mp4');
  const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',partial],{encoding:'utf8'}));
  const v=probe.streams[0];if(probe.streams.length!==1||v.codec_type!=='video'||v.r_frame_rate!=='24/1'||+v.nb_read_frames!==54||+probe.format.duration!==2.25)throw Error('Output format/range mismatch');
  fs.renameSync(partial,final);log.video={file:path.basename(final),sha256:sha(fs.readFileSync(final)),bytes:fs.statSync(final).size,probe};
  log.status='TECHNICAL_COMPLETE_PENDING_ACTUAL_CONTINUOUS_ACTION_REVIEW';
 }catch(e){log.status='FAILED_PRESERVED_NO_AUTOMATIC_RETRY';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(ff){ff.stdin.destroy();ff.kill('SIGTERM');await ffDone;}if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));log.finishedUTC=new Date().toISOString();fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');console.log(JSON.stringify({status:log.status,frames:log.frames.length,error:log.error,out}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
