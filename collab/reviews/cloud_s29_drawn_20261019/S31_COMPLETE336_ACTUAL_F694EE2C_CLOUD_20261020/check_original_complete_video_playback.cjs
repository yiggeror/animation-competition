// Playback-only verification of the copied original MP4. Zero scene renders.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{chromium}=require('playwright');
const video=path.join(__dirname,'S31_COMPLETE_336_VIDEO_ONLY.mp4'),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const bytes=fs.readFileSync(video),report={newSceneRenders:0,newGenerationCalls:0,videoSHA256:sha(bytes),pageErrors:[],requestFailures:[]};
 const server=http.createServer((req,res)=>{
  if(req.url==='/actual.mp4'){res.writeHead(200,{'Content-Type':'video/mp4','Content-Length':bytes.length});res.end(bytes);}
  else if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html'});res.end('<!doctype html><link rel="icon" href="data:,"><video controls preload="auto" src="/actual.mp4"></video>');}
  else{res.writeHead(404);res.end();}
 });let browser;
 try{
  await new Promise((ok,bad)=>{server.once('error',bad);server.listen(0,'127.0.0.1',ok);});
  browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();page.on('pageerror',e=>report.pageErrors.push(e.message));page.on('requestfailed',r=>report.requestFailures.push(r.url()));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  report.playback=await page.evaluate(async()=>{
   const v=document.querySelector('video');v.muted=true;
   await new Promise((ok,bad)=>{if(v.readyState>=3)return ok();v.addEventListener('canplay',ok,{once:true});v.addEventListener('error',()=>bad(Error('Media load error')),{once:true});});
   const ended=new Promise((ok,bad)=>{const timer=setTimeout(()=>bad(Error('Playback did not finish in45s')),45000);v.addEventListener('ended',()=>{clearTimeout(timer);ok();},{once:true});v.addEventListener('error',()=>{clearTimeout(timer);bad(Error('Media playback error'));},{once:true});});
   await v.play();await ended;const q=v.getVideoPlaybackQuality();
   return{width:v.videoWidth,height:v.videoHeight,duration:v.duration,currentTime:v.currentTime,ended:v.ended,readyState:v.readyState,mediaError:v.error?.message??null,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames??null};
  });
  const p=report.playback;report.videoBytesUnchanged=sha(fs.readFileSync(video))===report.videoSHA256;
  report.pass=p.width===1920&&p.height===1080&&p.duration===14&&p.ended&&!p.mediaError&&!report.pageErrors.length&&!report.requestFailures.length&&report.videoBytesUnchanged;
  fs.writeFileSync(path.join(__dirname,'ACTUAL_COMPLETE_MP4_BROWSER_PLAYBACK.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(!report.pass)process.exitCode=1;
 }finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));}
})().catch(e=>{console.error(e);process.exitCode=1});
