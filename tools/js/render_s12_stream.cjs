// Real Chromium -> PNG image pipe -> H264. Saves only selected contact frames.
// node tools/js/render_s12_stream.cjs outputDir --first 0 --last 105
const fs=require('fs'),path=require('path'),{spawn}=require('child_process'),{once}=require('events');
const {chromium}=require('playwright'),{start}=require('./serve.cjs');
const args=process.argv.slice(2),out=path.resolve(args[0]||'build/s12_actual');let first=0,last=191;
for(let i=1;i<args.length;i+=2){if(args[i]==='--first')first=+args[i+1];if(args[i]==='--last')last=+args[i+1];}
const picks=new Set([0,22,26,40,60,74,90,102,106,110,120,126,144,168,191]);
(async()=>{fs.mkdirSync(out,{recursive:true});const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage']});let ff;
 const record={renderer:'real Chromium Canvas',module:'js/anim/s12_drawn.js',first,last,fps:24,width:1920,height:1080,renderedFrames:0,selectedFrames:[],errors:[],startedUTC:new Date().toISOString()};
 try{const page=await browser.newPage();page.on('pageerror',e=>record.errors.push(String(e)));page.on('requestfailed',r=>record.errors.push(r.url()+': '+JSON.stringify(r.failure())));page.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('/favicon.ico'))record.errors.push(r.status()+' '+r.url());});
 await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js%2Fanim%2Fs12_drawn.js&w=1920&h=1080`);await page.waitForFunction(()=>window.__ready||window.__error);const error=await page.evaluate(()=>window.__error);if(error)throw Error(error);
 record.sequence=await page.evaluate(async()=>{const m=await import('/js/anim/s12_drawn.js');const q=await m.getSequenceInfo();return {totalFrames:q.totalFrames,availableThrough:q.availableThrough,exposureRows:q.states.length,status:q.status};});
 if(last>record.sequence.availableThrough)throw Error(`S12 adopted drawings stop at${record.sequence.availableThrough}; requested${last} needs the tail package.`);
 const video=path.join(out,`S12_${String(first).padStart(3,'0')}_${String(last).padStart(3,'0')}_actual.mp4`);
 ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore','pipe']});let stderr='';ff.stderr.on('data',b=>stderr+=b);const encoded=once(ff,'close');
 for(let f=first;f<=last;f++){
  const data=await page.evaluate(async n=>{await window.renderFrame(n/24);return document.getElementById('c').toDataURL('image/png');},f);
  const bytes=Buffer.from(data.split(',')[1],'base64');if(picks.has(f)){fs.writeFileSync(path.join(out,`F${String(f).padStart(3,'0')}.png`),bytes);record.selectedFrames.push(f);}
  if(!ff.stdin.write(bytes))await once(ff.stdin,'drain');record.renderedFrames++;if(record.renderedFrames%24===0)console.log(`S12 actual ${record.renderedFrames}/${last-first+1}`);
 }
 ff.stdin.end();const[code]=await encoded;if(code!==0)throw Error('ffmpeg failed '+stderr);record.video=video;record.completedUTC=new Date().toISOString();record.status='ACTUAL_RANGE_ENCODED';console.log(JSON.stringify(record));
 }catch(e){record.status='FAILED_INCOMPLETE_RANGE';record.failure=String(e);if(ff)ff.kill('SIGTERM');throw e;
 }finally{fs.writeFileSync(path.join(out,'runtime.json'),JSON.stringify(record,null,2)+'\n');await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
