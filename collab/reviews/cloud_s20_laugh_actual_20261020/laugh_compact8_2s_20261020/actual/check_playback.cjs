// Play the encoded compact8-state48-frame candidate once at1x.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../../../..');
const {chromium}=require('playwright');
const {start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html`);
  const src='/'+path.relative(root,path.join(__dirname,'S20_144_191_actual.mp4'));
  await page.evaluate(url=>{document.body.innerHTML='';document.body.style.margin='0';const v=document.createElement('video');v.id='v';v.src=url;v.muted=true;v.style.width='1920px';document.body.append(v)},src);
  await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
  const result=await page.evaluate(async()=>{
   const v=document.querySelector('video'),events=[],captures=[];v.playbackRate=1;const rows=[{key:176,start:170,end:175},{key:180,start:176,end:181},{key:184,start:182,end:187},{key:208,start:188,end:191}];const seen=new Set();
   const track=(now,m)=>{const frame=144+Math.round(m.mediaTime*24);events.push({t:m.mediaTime,frame,wall:now});const row=rows.find(r=>frame>=r.start&&frame<=r.end);if(row&&!seen.has(row.key)){seen.add(row.key);const c=document.createElement('canvas');c.width=1920;c.height=1080;c.getContext('2d').drawImage(v,0,0);captures.push({key:row.key,frame,time:m.mediaTime,image:c.toDataURL('image/jpeg',.97)});}if(!v.ended)v.requestVideoFrameCallback(track)};
   v.requestVideoFrameCallback(track);const start=performance.now();await v.play();await new Promise(r=>v.onended=r);
   const q=v.getVideoPlaybackQuality();return{playbackRate:v.playbackRate,mediaDuration:v.duration,wallMs:performance.now()-start,quality:{totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames},events,captures};
  });result.errors=errors;const captures=result.captures;delete result.captures;result.capturedStates=captures.map(c=>({key:c.key,frame:c.frame,time:c.time}));for(const c of captures)fs.writeFileSync(path.join(__dirname,`played_drawing${c.key}.jpg`),Buffer.from(c.image.split(',')[1],'base64'));
  fs.writeFileSync(path.join(__dirname,'actual_playback_1x.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({duration:result.mediaDuration,wallMs:result.wallMs,callbacks:result.events.length,quality:result.quality,errors}));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
