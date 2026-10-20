// Play only the delivered MP4 at normal speed; never call the scene renderer.
const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('playwright');
const file=path.join(__dirname,'actual/S29_ACTUAL078_131_54F.mp4');
(async()=>{
 const bytes=fs.readFileSync(file),server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'video/mp4','Content-Length':bytes.length});res.end(bytes);});
 let browser;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  await page.setContent(`<video muted playsinline preload="auto" src="http://127.0.0.1:${server.address().port}/actual.mp4"></video>`);
  const result=await page.evaluate(async()=>{
   const video=document.querySelector('video'),presented=[];
   video.playbackRate=1;
   const onFrame=(now,m)=>{presented.push({globalFrame:78+Math.round(m.mediaTime*24),mediaTime:m.mediaTime,presentedFrames:m.presentedFrames});if(!video.ended)video.requestVideoFrameCallback(onFrame);};
   video.requestVideoFrameCallback(onFrame);
   const done=new Promise((ok,bad)=>{const timeout=setTimeout(()=>bad(Error('Playback timeout')),15000);video.addEventListener('ended',()=>{clearTimeout(timeout);ok();},{once:true});video.addEventListener('error',()=>{clearTimeout(timeout);bad(Error('Media error'));},{once:true});});
   const start=performance.now();await video.play();await done;const elapsedMS=performance.now()-start,q=video.getVideoPlaybackQuality();
   return{ended:video.ended,duration:video.duration,playbackRate:video.playbackRate,elapsedMS,width:video.videoWidth,height:video.videoHeight,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames??null,presentedCallbacks:presented,mediaError:video.error?.message??null};
  });
  if(!result.ended||result.duration!==2.25||result.totalVideoFrames!==54||result.droppedVideoFrames!==0||result.mediaError)throw Error('Delivered normal-speed playback failed: '+JSON.stringify(result));
  const record={file:'actual/S29_ACTUAL078_131_54F.mp4',newSceneRenders:0,newImageCalls:0,...result};fs.writeFileSync(path.join(__dirname,'ACTUAL_NORMAL_RATE_MP4_PLAYBACK.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify(record));
 }finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));}
})().catch(e=>{console.error(e);process.exitCode=1;});
