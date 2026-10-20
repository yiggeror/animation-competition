// Play all16 true110–125 frames at the delivered original speed, with source AAC selected.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../../../..');
const {chromium}=require('playwright'),{start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html`);
  const src='/'+path.relative(root,path.join(__dirname,'S12_110_125_actual_original_audio.mp4'));
  await page.evaluate(url=>{document.body.innerHTML='';document.body.style.margin='0';const v=document.createElement('video');v.src=url;v.muted=true;v.style.width='1920px';document.body.append(v)},src);
  await page.waitForFunction(()=>document.querySelector('video').readyState>=4);
  const result=await page.evaluate(async()=>{
   const v=document.querySelector('video'),events=[];v.playbackRate=1;
   const track=(now,m)=>{events.push({t:m.mediaTime,frame:110+Math.round(m.mediaTime*24),wall:now});if(!v.ended)v.requestVideoFrameCallback(track)};
   v.requestVideoFrameCallback(track);const start=performance.now();await v.play();await new Promise(r=>v.onended=r);
   const q=v.getVideoPlaybackQuality();return{playbackRate:v.playbackRate,mediaDuration:v.duration,wallMs:performance.now()-start,decodedAudioBytes:v.webkitAudioDecodedByteCount,quality:{totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames},events};
  });result.errors=errors;result.scope='Playback technical evidence only; Natural120 peak, body and hand/rod continuity reviewed separately inREADME; playback metrics are not motion acceptance.';
  fs.writeFileSync(path.join(__dirname,'actual_playback_1x.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
