// Decode/play the fixed actual MP4. Does not call scene renderer or alter video.
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'../../../..'),{start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const server=await start(0);let browser;
 const report={newSceneRenders:0,generationCalls:0,pageErrors:[],requestFailures:[],priorInfrastructureAttempt:{error:'page.goto: Download is starting',cause:'Repository static server sends mp4 as download. No scene renderer was called.',fix:'Read exact MP4 bytes through Playwright route with video/mp4 MIME and an HTML video element.'}};
 try {
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();page.on('pageerror',e=>report.pageErrors.push(e.message));page.on('requestfailed',r=>report.requestFailures.push(r.url()));
  const rel=path.relative(root,__dirname).split(path.sep).join('/');
  await page.route('**/review-video.mp4',r=>r.fulfill({status:200,contentType:'video/mp4',body:fs.readFileSync(path.join(__dirname,'S29_F066_F089_REUSED6_NEW18_ACTUAL_1080p24_SILENT.mp4'))}));
  await page.route('**/video-review.html',r=>r.fulfill({status:200,contentType:'text/html',body:'<!doctype html><link rel="icon" href="data:,"><video controls preload="auto" src="./review-video.mp4"></video>'}));
  await page.goto(`http://127.0.0.1:${server.address().port}/${rel}/video-review.html`);
  report.playback=await page.evaluate(async()=>{
   const v=document.querySelector('video');if(!v)throw Error('No actualvideo element');
   v.muted=true;v.pause();v.currentTime=0;
   await new Promise((resolve,reject)=>{if(v.readyState>=3)return resolve();v.addEventListener('canplay',resolve,{once:true});v.addEventListener('error',()=>reject(Error('Media error')),{once:true});});
   const ended=new Promise((resolve,reject)=>{v.addEventListener('ended',resolve,{once:true});v.addEventListener('error',()=>reject(Error('Media error')),{once:true});});
   await v.play();await ended;
   const q=v.getVideoPlaybackQuality();
   return {width:v.videoWidth,height:v.videoHeight,duration:v.duration,readyState:v.readyState,ended:v.ended,mediaError:v.error?.message??null,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames??null,currentTime:v.currentTime};
  });
  const p=report.playback;report.pass=p.width===1920&&p.height===1080&&p.duration===1&&p.ended&&!p.mediaError&&!report.pageErrors.length&&!report.requestFailures.length;
  fs.writeFileSync(path.join(__dirname,'FINAL24_ACTUAL_BROWSER_PLAYBACK_CHECK.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));if(!report.pass)process.exitCode=1;
 } finally {if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
