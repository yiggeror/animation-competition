// Play delivered files only. No scene module, renderer or image generation.
const fs=require('fs'),path=require('path'),http=require('http'),{chromium}=require('playwright');
const files=['assembled/S14_PREFIX000_131_132F_CUT_GATE_PENDING.mp4','actual_late141_239/S14_ACTUAL_SEGMENT.mp4','actual_original159_trial156_164/S14_ACTUAL_SEGMENT.mp4'];
(async()=>{
 const server=http.createServer((req,res)=>{const k=Number(req.url.slice(1));if(!Number.isInteger(k)||!files[k]){res.writeHead(404).end();return;}const b=fs.readFileSync(path.join(__dirname,files[k]));res.writeHead(200,{'Content-Type':'video/mp4','Content-Length':b.length});res.end(b);});
 let browser;const result={newSceneRenders:0,clips:[]};
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});const page=await browser.newPage();
  for(let i=0;i<files.length;i++){
   await page.setContent(`<video muted src="http://127.0.0.1:${server.address().port}/${i}"></video>`);
   const playback=await page.evaluate(async()=>{const v=document.querySelector('video');v.muted=true;const done=new Promise((ok,bad)=>{const t=setTimeout(()=>bad(Error('Playback timeout')),30000);v.addEventListener('ended',()=>{clearTimeout(t);ok();},{once:true});v.addEventListener('error',()=>{clearTimeout(t);bad(Error('Media error'));},{once:true});});await v.play();await done;const q=v.getVideoPlaybackQuality();return{ended:v.ended,duration:v.duration,width:v.videoWidth,height:v.videoHeight,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames??null,mediaError:v.error?.message??null};});
   result.clips.push({file:files[i],...playback});
  }
  fs.writeFileSync(path.join(__dirname,'ACTUAL_DELIVERED_MP4_PLAYBACK.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));}
})().catch(e=>{console.error(e);process.exitCode=1;});
