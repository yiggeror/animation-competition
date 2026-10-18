// Authorized only after tail_lock.json records the actual Astra-approved tails.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'../../../..'),{start}=require(path.join(ROOT,'tools/js/serve.cjs'));
const rel=path.relative(ROOT,__dirname).split(path.sep).join('/');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const lock=JSON.parse(fs.readFileSync(path.join(__dirname,'tail_lock.json'))),map=JSON.parse(fs.readFileSync(path.join(__dirname,'resource_map.json')));
 if(lock.status!=='approved'||!lock.approved_tail_commit)throw new Error('S22_TAIL_FREEZE_REQUIRED: no actual scene capture before Astra final tail lock.');
 for(const id of ['F108','F114'])if(lock.approved_final_RGBA?.[id]!==map.exposures.find(r=>r.id===id).sha256)throw new Error('S22 tail SHA mismatch: '+id);
 for(const row of map.exposures)if(sha(fs.readFileSync(path.join(ROOT,row.url)))!==row.sha256)throw new Error('S22 actual image SHA mismatch: '+row.id);
 const out=path.join(__dirname,'scene120'),frames=path.join(out,'frames');fs.mkdirSync(frames,{recursive:true});
 const server=await start(0),base=`http://127.0.0.1:${server.address().port}`;
 const executablePath=['/usr/bin/chromium','/usr/bin/chromium-browser'].find(p=>fs.existsSync(p));const browser=await chromium.launch({executablePath,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[],http=[];page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()+':'+r.failure()?.errorText));page.on('response',r=>http.push({url:r.url(),status:r.status()}));
 await page.goto(base+'/dev/view.html?mod='+encodeURIComponent(rel+'/S22_drawn.js')+'&w=1920&h=1080');await page.waitForFunction(()=>window.__ready||window.__error,null,{timeout:60000});const error=await page.evaluate(()=>window.__error);if(error)throw new Error(error);
 const frameSHA=[];
 for(let f=0;f<120;f++){
  const data=await page.evaluate(async t=>{await window.renderFrame(t);return document.querySelector('canvas').toDataURL('image/png');},f/24);const bytes=Buffer.from(data.split(',')[1],'base64');const file=String(f).padStart(5,'0')+'.png';fs.writeFileSync(path.join(frames,file),bytes);frameSHA.push({frame:f,file,sha256:sha(bytes)});if((f+1)%24===0)console.log(`${f+1}/120 actual Canvas frames`);
 }
 await browser.close();server.close();if(errors.length)throw new Error(errors.join('\n'));if(http.some(r=>r.status>=400&&/\.(png|js|json)(\?|$)/.test(r.url)))throw new Error('Scene asset HTTP failure');
 const clip=path.join(out,'S22_actual_scene120.mp4');const command=['-y','-v','error','-framerate','24','-i',path.join(frames,'%05d.png'),'-frames:v','120','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',clip];let result=spawnSync('ffmpeg',command,{stdio:'inherit'});if(result.status!==0)throw new Error('Scene encode failed');
 const probe=JSON.parse(spawnSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',clip],{encoding:'utf8'}).stdout);if(probe.streams.length!==1||+probe.streams[0].nb_read_frames!==120||+probe.format.duration!==5)throw new Error('Actual scene exposure mismatch');
 const selected=Array.from(new Set(map.exposures.flatMap(r=>[r.start,r.end]))).sort((a,b)=>a-b);fs.mkdirSync(path.join(out,'decoded_actual'),{recursive:true});
 for(const f of selected){result=spawnSync('ffmpeg',['-y','-v','error','-i',clip,'-vf',`select=eq(n\\,${f})`,'-frames:v','1',path.join(out,'decoded_actual',`F${String(f).padStart(3,'0')}.png`)]);if(result.status!==0)throw new Error('Actual scene decode failed');}
 const manifest={clip:'scene120/S22_actual_scene120.mp4',sha256:sha(fs.readFileSync(clip)),fps:24,frames:120,size:[1920,1080],duration:5,actual_Canvas_module:rel+'/S22_drawn.js',module_sha256:sha(fs.readFileSync(path.join(__dirname,'S22_drawn.js'))),tail_lock:lock,resource_map:map,frame_sha256:frameSHA,actual_decoded_frames:selected,http,errors,scene_integrated:true,audio_integrated:false,production_ready:false,production_EDL_audio_ready_changed:false,ffprobe:probe,encode_command:['ffmpeg',...command]};
 fs.writeFileSync(path.join(__dirname,'provenance/actual_scene120_manifest.json'),JSON.stringify(manifest,null,2)+'\n');console.log(clip);
})().catch(e=>{console.error(e.message);process.exit(1);});
