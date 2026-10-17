const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const {chromium} = require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const input = path.resolve(process.argv[2]);
const out = path.resolve(process.argv[3]);
const bytes = fs.readFileSync(input);
const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
fs.mkdirSync(out, {recursive:true});
const html = '<!doctype html><meta charset="utf-8"><title>S18 playback check</title><body style="margin:0;background:#222"><video id="v" controls preload="auto" src="/clip.mp4" style="max-width:960px;max-height:1280px"></video></body>';
const server = http.createServer((req,res)=>{
  if(req.url === '/clip.mp4'){
    const range = req.headers.range;
    if(range){
      const m = /^bytes=(\d+)-(\d*)$/.exec(range);
      if(!m){res.writeHead(416);return res.end();}
      const start = Number(m[1]), end = Math.min(m[2]?Number(m[2]):bytes.length-1,bytes.length-1);
      res.writeHead(206,{'Content-Type':'video/mp4','Content-Range':`bytes ${start}-${end}/${bytes.length}`,'Accept-Ranges':'bytes','Content-Length':end-start+1});
      return res.end(bytes.subarray(start,end+1));
    }
    res.writeHead(200,{'Content-Type':'video/mp4','Content-Length':bytes.length});return res.end(bytes);
  }
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html);
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--autoplay-policy=no-user-gesture-required']});
 try {
  const page=await browser.newPage({viewport:{width:1000,height:1320}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}`);
  await page.waitForFunction(()=>document.getElementById('v').readyState>=3,null,{timeout:30000});
  const result=await page.evaluate(async()=>{
    const v=document.getElementById('v');v.playbackRate=1;v.loop=false;v.muted=false;
    const callbacks=[],events=[];let active=true;
    for(const name of ['playing','waiting','stalled','ended','error'])v.addEventListener(name,()=>events.push({event:name,mediaTime:v.currentTime,wallMs:performance.now()}));
    const receive=(now,m)=>{callbacks.push({wallMs:now,mediaTime:m.mediaTime,presentedFrames:m.presentedFrames,expectedDisplayTime:m.expectedDisplayTime});if(active)v.requestVideoFrameCallback(receive);};
    v.requestVideoFrameCallback(receive);
    const start=performance.now();
    const ended=new Promise((resolve,reject)=>{v.addEventListener('ended',resolve,{once:true});v.addEventListener('error',()=>reject(Error(v.error?.message||'media error')),{once:true});setTimeout(()=>reject(Error('playback did not end within 20s')),20000);});
    await v.play();await ended;active=false;
    const quality=v.getVideoPlaybackQuality();
    return {duration:v.duration,playbackRate:v.playbackRate,muted:v.muted,currentTime:v.currentTime,ended:v.ended,width:v.videoWidth,height:v.videoHeight,elapsedWallMs:performance.now()-start,quality:{totalVideoFrames:quality.totalVideoFrames,droppedVideoFrames:quality.droppedVideoFrames,corruptedVideoFrames:quality.corruptedVideoFrames},callbacks,events};
  });
  result.source={input,bytes:bytes.length,sha256};result.browser=await browser.version();result.errors=errors;
  result.scope='Technical normal-rate playback only; callback timestamps and decoded presentation do not establish human perceptual continuity or audio listening approval.';
  fs.writeFileSync(path.join(out,'playback.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify({source:result.source,playbackRate:result.playbackRate,ended:result.ended,elapsedWallMs:result.elapsedWallMs,quality:result.quality,callbackCount:result.callbacks.length,errors},null,2));
 } finally {await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
