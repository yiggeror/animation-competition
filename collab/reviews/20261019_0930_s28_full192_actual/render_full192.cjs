const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {spawn,execFileSync}=require('child_process'),{once}=require('events');
(async()=>{
  const out=process.env.S28_OUTPUT_DIR||'/tmp/s28-full192',keep=new Set([0,12,42,63,66,84,86,131,132,162,191]);fs.mkdirSync(out,{recursive:true});
  const video=path.join(out,'S28_FULL192_24FPS_8S.mp4'),rows=[],errors=[];fs.writeFileSync(path.join(out,'FRAME_SHA256.jsonl'),'');
  const encoder=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','24','-vcodec','png','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','inherit','inherit']});
  const encoded=new Promise((resolve,reject)=>{encoder.once('error',reject);encoder.once('close',code=>code===0?resolve():reject(new Error('ffmpeg exit '+code)));});encoded.catch(()=>{});
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  try{
    const page=await browser.newPage({viewport:{width:1920,height:1080}});
    page.on('pageerror',e=>{errors.push(String(e));console.error('PAGEERROR',String(e));});
    page.on('requestfailed',r=>console.error('REQUESTFAILED',r.url(),r.failure()?.errorText));
    page.on('response',r=>{if(r.status()>=400)console.error('HTTP',r.status(),r.url());});
    await page.goto(process.env.S28_PREVIEW_URL||'http://127.0.0.1:8197/collab/reviews/20261019_0930_s28_full192_actual/preview.html');
    await page.waitForFunction(()=>window.ready,null,{timeout:90000});
    for(let frame=0;frame<192;frame++){
      const result=await page.evaluate(f=>window.renderFullS28(f),frame),png=Buffer.from(result.png.split(',')[1],'base64');delete result.png;
      result.sha256=crypto.createHash('sha256').update(png).digest('hex');result.bytes=png.length;
      if(keep.has(frame))fs.writeFileSync(path.join(out,`F${String(frame).padStart(3,'0')}.png`),png);
      if(!encoder.stdin.write(png))await once(encoder.stdin,'drain');
      rows.push(result);fs.appendFileSync(path.join(out,'FRAME_SHA256.jsonl'),JSON.stringify(result)+'\n');
      if((frame+1)%24===0)console.log(JSON.stringify({completed:frame+1,total:192,lastFrame:frame,lastSHA256:result.sha256}));
    }
    encoder.stdin.end();await encoded;
    const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_read_frames,duration','-of','json',video],{encoding:'utf8'}));
    const v=probe.streams[0];if(v.nb_read_frames!=='192'||v.r_frame_rate!=='24/1'||Math.abs(Number(v.duration)-8)>1e-6||errors.length)throw new Error('S28 output gate failed '+JSON.stringify({v,errors}));
    fs.writeFileSync(path.join(out,'FULL192_CHECK.json'),JSON.stringify({sourceCommit:'8a86a552fba1a822aae0f27ca53e2b0defb4e392',entry:'collab/reviews/20261019_0901_s28_float_depth/entry_full192.mjs',frames:192,stageFrames:132,phoneFrames:60,cutFrame:132,probe,errors,videoSHA256:crypto.createHash('sha256').update(fs.readFileSync(video)).digest('hex'),visualReview:'PENDING actual whole clip'},null,2));
  }finally{await browser.close();if(!encoder.stdin.writableEnded)encoder.kill();}
})().catch(e=>{console.error(e);process.exit(1)});
