const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{execFileSync}=require('child_process'),{chromium}=require('playwright');
const repo=execFileSync('git',['rev-parse','--show-toplevel'],{encoding:'utf8'}).trim(),out=process.env.S14_T1_OUTPUT_DIR?path.resolve(process.env.S14_T1_OUTPUT_DIR):path.join(__dirname,'actual_raw'),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
let browser,server;const log={status:'RUNNING',frames:[],responses:[],errors:[],newGenerationCalls:0};
const save=()=>fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');
(async()=>{
 if(fs.existsSync(out))throw Error('Existing actual output is preserved; no automatic retry');fs.mkdirSync(out);save();
 try{
  server=http.createServer((req,res)=>{
   const u=new URL(req.url,'http://localhost');if(u.pathname==='/favicon.ico'){res.writeHead(204).end();return;}
   const f=path.resolve(repo,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(repo+path.sep)){res.writeHead(403).end();return;}
   fs.readFile(f,(e,b)=>{if(e){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.png':'image/png'})[path.extname(f)]||'application/octet-stream');res.end(b);});
  });await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);
  page.on('response',r=>log.responses.push({path:new URL(r.url()).pathname,status:r.status()}));page.on('pageerror',e=>log.errors.push(String(e)));page.on('requestfailed',r=>log.errors.push(r.url()));page.on('console',m=>{if(m.type()==='error')log.errors.push(m.text());});
  await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s14_scene_20261020/child_T1_actual_space_20261020/preview.html`);await page.waitForFunction(()=>window.ready,null,{timeout:15000});
  for(const f of [150,151,152,153,154,155]){
   const binding=await page.evaluate(f=>window.drawActual(f),f),b=await page.locator('canvas').screenshot({type:'png'});
   if(log.errors.length||log.responses.some(r=>r.status>=400&&!r.path.endsWith('/favicon.ico')))throw Error('Actual scene resource/browser failure');
   const file=`F${f}.png`;fs.writeFileSync(path.join(out,file),b);log.frames.push({frame:f,file,sha256:sha(b),binding});save();console.log('Actual A/T1',f);
  }
  const video='S14_A_TO_T1_RAW_ACTUAL_150_155_6F.mp4';
  execFileSync('ffmpeg',['-hide_banner','-loglevel','error','-framerate','24','-start_number','150','-i',path.join(out,'F%d.png'),'-frames:v','6','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,video)]);
  log.video={file:video,sha256:sha(fs.readFileSync(path.join(out,video)))};log.status='ACTUAL_RAW_ADJACENCY_COMPLETE_PENDING_SPACE_REVIEW';
 }catch(e){log.status='FAILED_PRESERVED';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(browser)await browser.close();if(server)await new Promise(ok=>server.close(ok));save();console.log(JSON.stringify({status:log.status,count:log.frames.length,error:log.error}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
