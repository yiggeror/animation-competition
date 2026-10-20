// S20 original WebGL scene, adopted laugh anchors, PNG pipe to one H264 clip.
// --preview saves only144/156; the continuous run is144–215 at24fps.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),{once}=require('events');
const {chromium}=require('playwright'),{start}=require('./serve.cjs');
const out=path.resolve(process.argv[2]||'build/s20_laugh_actual'),preview=process.argv.includes('--preview');
(async()=>{
 fs.mkdirSync(out,{recursive:true});const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader']});let encoder;
 const record={renderer:'Real Chromium original WebGL2 renderShot',module:'js/anim/s20_laugh_drawn.js',first:144,last:215,width:1920,height:1080,fps:24,preview,renderedFrames:0,errors:[],startedUTC:new Date().toISOString()};
 try{
  const page=await browser.newPage();page.on('pageerror',e=>record.errors.push(String(e)));page.on('requestfailed',r=>record.errors.push(r.url()+': '+JSON.stringify(r.failure())));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))record.errors.push(r.status()+' '+r.url())});
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js%2Fanim%2Fs20_laugh_drawn.js&w=1920&h=1080`);await page.waitForFunction(()=>window.__ready||window.__error);const error=await page.evaluate(()=>window.__error);if(error)throw Error(error);
  record.sequence=await page.evaluate(async()=>{const m=await import('/js/anim/s20_laugh_drawn.js');return m.getSequenceInfo()});
  const frames=preview?[144,156]:Array.from({length:72},(_,i)=>144+i),picks=new Set([144,155,156,168,215]);let encoded;
  if(!preview){const video=path.join(out,'S20_laugh_144_215_actual.mp4');encoder=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore','pipe']});let stderr='';encoder.stderr.on('data',b=>stderr+=b);encoded=once(encoder,'close').then(([c])=>{if(c!==0)throw Error('ffmpeg failed '+stderr)});record.video=video;}
  for(const f of frames){
   const data=await page.evaluate(async n=>{await window.renderFrame(n/24);return document.getElementById('c').toDataURL('image/png')},f),bytes=Buffer.from(data.split(',')[1],'base64');
   if(preview||picks.has(f))fs.writeFileSync(path.join(out,`F${f}.png`),bytes);
   if(encoder&&!encoder.stdin.write(bytes))await once(encoder.stdin,'drain');record.renderedFrames++;if(preview||record.renderedFrames%6===0)console.log(`S20 actual ${record.renderedFrames}/${frames.length}, frame${f}`);
  }
  if(encoder){encoder.stdin.end();await encoded}record.completedUTC=new Date().toISOString();record.status=preview?'ACTUAL_KEYS_FOR_VISUAL_REVIEW':'ACTUAL_CONTINUOUS_TWO_ANCHOR_EXPOSURE_PROBE';console.log(JSON.stringify(record));
 }catch(e){record.status='FAILED_INCOMPLETE';record.failure=String(e);encoder?.kill('SIGTERM');throw e}
 finally{fs.writeFileSync(path.join(out,'runtime.json'),JSON.stringify(record,null,2)+'\n');await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
