const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawn}=require('child_process'),{once}=require('events'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'../../../..'),{start}=require(path.join(root,'tools/js/serve.cjs'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const tracked=['js/paint/shots/s29.js','js/paint/paintshot.js','js/paint/shots/s29_lamp.js','assets/paint/bg_01_room_wide.png'];
const hashes=()=>Object.fromEntries(tracked.map(p=>[p,sha(fs.readFileSync(path.join(root,p)))]));
(async()=>{
 const log={startUTC:new Date().toISOString(),generationCalls:0,sourceBefore:hashes(),responses:[],failed:[],pageerrors:[],consoleErrors:[],frames:[]};
 fs.mkdirSync(path.join(__dirname,'keys'),{recursive:true});
 const server=await start(0);let browser,ff;
 try{
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));page.on('requestfailed',r=>log.failed.push({url:r.url(),failure:r.failure()}));page.on('pageerror',e=>log.pageerrors.push(e.message));page.on('console',m=>{if(m.type()==='error')log.consoleErrors.push(m.text());});
  const source=path.join(root,'js/paint/shots/s29.js');
  await page.route('**/js/paint/shots/s29.js?readonlyShotExport=1',r=>r.fulfill({status:200,contentType:'text/javascript',body:fs.readFileSync(source,'utf8')+'\nexport {shot as sourceShot};\n'}));
  const rel=path.relative(root,__dirname).split(path.sep).join('/');
  await page.goto(`http://127.0.0.1:${server.address().port}/${rel}/scene.html`);await page.waitForFunction(()=>window.ready===true,null,{timeout:120000});
  const mp4=path.join(__dirname,'S29_F036_F048_ACTUAL_SCENE_1080p24.mp4');
  const argv=['-y','-hide_banner','-loglevel','warning','-f','image2pipe','-vcodec','png','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',mp4];
  log.ffmpegCommand=['ffmpeg',...argv];ff=spawn('ffmpeg',argv,{stdio:['pipe','ignore','pipe']});let fferr='';ff.stderr.on('data',b=>fferr+=b);const completion=new Promise((resolve,reject)=>{ff.on('error',reject);ff.on('close',code=>code===0?resolve():reject(Error('ffmpeg '+code+' '+fferr)));});
  for(let f=36;f<=48;f++){
   const v=await page.evaluate(f=>window.renderActual(f),f),png=Buffer.from(v.png.split(',')[1],'base64');
   log.frames.push({...v.geometry,canvasPNG_SHA256:sha(png)});
   if([36,41,42,47,48].includes(f))fs.writeFileSync(path.join(__dirname,'keys',`S29_F${String(f).padStart(3,'0')}_CANVAS.png`),png);
   if(!ff.stdin.write(png))await once(ff.stdin,'drain');
   console.log('actual frame',f,'state',v.geometry.state);
  }
  ff.stdin.end();await completion;log.ffmpegStderr=fferr;log.mp4_SHA256=sha(fs.readFileSync(mp4));log.sourceAfter=hashes();log.sourceUnchanged=JSON.stringify(log.sourceBefore)===JSON.stringify(log.sourceAfter);log.endUTC=new Date().toISOString();
  log.pass=log.sourceUnchanged&&!log.failed.length&&!log.pageerrors.length&&!log.consoleErrors.length&&log.responses.every(v=>v.status<400)&&log.frames.length===13;
  fs.writeFileSync(path.join(__dirname,'ACTUAL_BROWSER_RUN.json'),JSON.stringify(log,null,2)+'\n');
  console.log(JSON.stringify({pass:log.pass,frames:13,mp4SHA256:log.mp4_SHA256,errors:log.pageerrors,sourceUnchanged:log.sourceUnchanged}));if(!log.pass)process.exitCode=1;
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
