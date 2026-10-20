// Play the complete delivered8s at1x and retain actual video-frame snapshots.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../../../..');
const {chromium}=require('playwright'),{start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[];
  page.on('pageerror',e=>errors.push(String(e)));await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html`);
  const src='/'+path.relative(root,path.join(__dirname,'S12_natural_fixed_8s_original_audio.mp4'));
  await page.evaluate(url=>{document.body.innerHTML='';document.body.style.margin='0';const v=document.createElement('video');v.src=url;v.muted=true;v.style.width='1920px';v.preload='auto';document.body.append(v)},src);
  await page.waitForFunction(()=>document.querySelector('video').readyState>=4);
  const result=await page.evaluate(async()=>{
   const v=document.querySelector('video'),events=[],captures=[],marks=new Set([0,24,48,74,89,90,95,100,105,110,120,126,132,144,168,191]),c=document.createElement('canvas');c.width=960;c.height=540;const x=c.getContext('2d');v.playbackRate=1;
   const snap=f=>{x.drawImage(v,0,0,960,540);captures.push({frame:f,jpeg:c.toDataURL('image/jpeg',.92)});marks.delete(f)};
   snap(0);
   const track=(now,m)=>{const f=Math.round(m.mediaTime*24);events.push({t:m.mediaTime,frame:f,wall:now});if(marks.has(f))snap(f);if(!v.ended)v.requestVideoFrameCallback(track)};
   v.requestVideoFrameCallback(track);const start=performance.now();await v.play();await new Promise(r=>v.onended=r);
   const q=v.getVideoPlaybackQuality();return{playbackRate:v.playbackRate,mediaDuration:v.duration,wallMs:performance.now()-start,decodedAudioBytes:v.webkitAudioDecodedByteCount,quality:{totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames},events,captures,missedSnapshotMarks:[...marks]};
  });
  const snapshotDir='/tmp/s12_full8s_played';fs.mkdirSync(snapshotDir,{recursive:true});
  for(const s of result.captures)fs.writeFileSync(path.join(snapshotDir,`F${String(s.frame).padStart(3,'0')}.jpg`),Buffer.from(s.jpeg.split(',')[1],'base64'));
  result.actualSnapshots=result.captures.map(s=>({frame:s.frame,path:path.join(snapshotDir,`F${String(s.frame).padStart(3,'0')}.jpg`)}));delete result.captures;result.errors=errors;result.scope='Full original-speed video playback. Anatomy/action review separately recorded; numerical playback success alone is not visual acceptance.';
  fs.writeFileSync(path.join(__dirname,'actual_full_playback_1x.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({duration:result.mediaDuration,wallMs:result.wallMs,quality:result.quality,actualSnapshots:result.actualSnapshots.length,missed:result.missedSnapshotMarks,errors}));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
