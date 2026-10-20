// S20 original WebGL scene, explicit adopted exposures, PNG pipe to H264.
// Optional reuse decodes accepted clip intervals without browser rerendering.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),{once}=require('events');
const {chromium}=require('playwright'),{start}=require('./serve.cjs');
const out=path.resolve(process.argv[2]||'build/s20_laugh_actual'),preview=process.argv.includes('--preview');
const options={};for(let i=3;i<process.argv.length;i++){if(process.argv[i].startsWith('--')&&process.argv[i]!=='--preview')options[process.argv[i]]=process.argv[++i]}
const first=+(options['--first']??144),last=+(options['--last']??215),mod=options['--module']||'js/anim/s20_laugh_drawn.js';
const reuseSource=options['--reuse-source'],reuseOrigin=+(options['--reuse-origin']??144),reuseRanges=(options['--reuse-ranges']||'').split(',').filter(Boolean).map(x=>x.split(':').map(Number));
(async()=>{
 fs.mkdirSync(out,{recursive:true});const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage','--enable-unsafe-swiftshader']});let encoder;
 const record={renderer:'Real Chromium original WebGL2 renderShot',module:mod,first,last,width:1920,height:1080,fps:24,preview,renderedFrames:0,errors:[],startedUTC:new Date().toISOString()};
 try{
  const page=await browser.newPage();page.on('pageerror',e=>record.errors.push(String(e)));page.on('requestfailed',r=>record.errors.push(r.url()+': '+JSON.stringify(r.failure())));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))record.errors.push(r.status()+' '+r.url())});
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=${encodeURIComponent(mod)}&w=1920&h=1080`);await page.waitForFunction(()=>window.__ready||window.__error);const error=await page.evaluate(()=>window.__error);if(error)throw Error(error);
  record.sequence=await page.evaluate(async p=>{const m=await import('/'+p);return m.getSequenceInfo()},mod);
  const frames=preview?(first===144?[144,156]:[first,last]):Array.from({length:last-first+1},(_,i)=>first+i),picks=new Set(first===0?[0,4,12,24,32,35]:[144,150,155,156,168,180,192,215]);let encoded;
  if(!preview){const name=first===144&&last===215?'S20_laugh_144_215_actual.mp4':`S20_${String(first).padStart(3,'0')}_${String(last).padStart(3,'0')}_actual.mp4`,video=path.join(out,name);encoder=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore','pipe']});let stderr='';encoder.stderr.on('data',b=>stderr+=b);encoded=once(encoder,'close').then(([c])=>{if(c!==0)throw Error('ffmpeg failed '+stderr)});record.video=video;}
  for(let ix=0;ix<frames.length;ix++){const f=frames[ix],reuse=!preview&&reuseRanges.find(r=>r[0]===f);
   if(reuse){
    const count=reuse[1]-reuse[0]+1,decoder=spawn('ffmpeg',['-loglevel','error','-i',path.resolve(reuseSource),'-vf',`trim=start_frame=${reuse[0]-reuseOrigin}:end_frame=${reuse[1]-reuseOrigin+1}`,'-frames:v',String(count),'-fps_mode','passthrough','-f','image2pipe','-vcodec','png','pipe:1'],{stdio:['ignore','pipe','pipe']});
    let err='';decoder.stderr.on('data',b=>err+=b);decoder.stdout.pipe(encoder.stdin,{end:false});const[code]=await once(decoder,'close');if(code!==0)throw Error('Reuse decode failed '+err);
    (record.reusedRanges||=[]).push({first:reuse[0],last:reuse[1],decodedFrames:count,source:reuseSource,browserRerendered:false});ix+=count-1;console.log(`S20 reused ${reuse[0]}–${reuse[1]}`);continue;
   }
   const data=await page.evaluate(async n=>{await window.renderFrame(n/24);return document.getElementById('c').toDataURL('image/png')},f),bytes=Buffer.from(data.split(',')[1],'base64');
   if(preview||picks.has(f))fs.writeFileSync(path.join(out,`F${f}.png`),bytes);
   if(encoder&&!encoder.stdin.write(bytes))await once(encoder.stdin,'drain');record.renderedFrames++;if(preview||record.renderedFrames%6===0)console.log(`S20 actual ${record.renderedFrames}/${frames.length}, frame${f}`);
  }
  if(encoder){encoder.stdin.end();await encoded}record.completedUTC=new Date().toISOString();record.status=preview?'ACTUAL_KEYS_FOR_VISUAL_REVIEW':'ACTUAL_EXPLICIT_ADOPTED_EXPOSURES';console.log(JSON.stringify(record));
 }catch(e){record.status='FAILED_INCOMPLETE';record.failure=String(e);encoder?.kill('SIGTERM');throw e}
 finally{fs.writeFileSync(path.join(out,'runtime.json'),JSON.stringify(record,null,2)+'\n');await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
