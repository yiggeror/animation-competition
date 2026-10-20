// Five real production-entry keys, declarative prefix coverage, and the missing-ending boundary.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{chromium}=require('playwright');
const repo=path.resolve(__dirname,'../../..'),out=process.env.S29_KEY_OUTPUT_DIR?path.resolve(process.env.S29_KEY_OUTPUT_DIR):path.join(__dirname,'actual_keyframes');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const log={status:'RUNNING',newSceneFrames:[],coverage:[],responses:[],pageErrors:[],requestFailures:[],expectedEndingFailure:null};
let browser,server;
const save=()=>fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');
(async()=>{
 if(fs.existsSync(out))throw Error('Keep previous outputs; do not rerender this check automatically.');
 fs.mkdirSync(out);save();
 try{
  server=await require(path.join(repo,'tools/js/serve.cjs')).start(0);
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);
  page.on('response',r=>log.responses.push({path:new URL(r.url()).pathname,status:r.status()}));
  page.on('pageerror',e=>log.pageErrors.push(String(e)));
  page.on('requestfailed',r=>log.requestFailures.push({url:r.url(),error:r.failure()}));
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js/paint/shots/s29.js&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready||window.__error);
  log.loader=await page.evaluate(()=>({ready:window.__ready,error:window.__error,duration:window.DURATION}));
  if(log.loader.error||Math.abs(log.loader.duration-272/24)>1e-9)throw Error('Production entry loader/duration failure');
  log.coverage=await page.evaluate(async()=>{
   const early=await import('/js/anim/s29/exposure.js'),front=await import('/js/anim/s29/front_fold_exposure.js'),tail=await import('/js/anim/s29/wrap_tail.js');
   return Array.from({length:240},(_,frame)=>{
    const row=frame<90?early.resolveFrame(frame):frame<116?front.resolveFrame(frame):tail.WRAP_TAIL_EXPOSURE.find(r=>frame>=r.first&&frame<=r.last);
    if(!row)throw Error('Missing prefix exposure '+frame);
    return{frame,url:row.url||`/assets/chars/s29_tail/${row.file}.png`,sha256:row.sha256??null};
   });
  });
  const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'EXPOSURE.json'))).rows;
  for(const row of log.coverage){
   const want=expected.find(r=>row.frame>=r.first&&row.frame<=r.last);
   if(!want||want.url!==row.url)throw Error('Producer exposure differs at '+row.frame);
   const f=path.join(repo,row.url.slice(1));if(!fs.existsSync(f))throw Error('Missing production cel '+f);
   const hash=sha(fs.readFileSync(f));if(row.sha256&&hash!==row.sha256)throw Error('Production hash mismatch '+f);
   row.actualSHA256=hash;
  }
  for(const frame of [0,102,126,172,239]){
   await page.evaluate(t=>window.renderFrame(t),frame/24);
   if(log.pageErrors.length||log.requestFailures.length||log.responses.some(r=>r.status>=400&&!r.path.endsWith('/favicon.ico')))throw Error('Unexpected prefix browser/resource failure');
   const b=await page.locator('#c').screenshot({type:'png'}),file=`ACTUAL_F${String(frame).padStart(3,'0')}.png`;
   fs.writeFileSync(path.join(out,file),b);log.newSceneFrames.push({frame,file,sha256:sha(b)});save();console.log('Production key',frame);
  }
  log.prefixHadNoEndingRequest=!log.responses.some(r=>r.path.includes('s29_preparation_drawn')||r.path.includes('/s29_prepare/'));
  if(!log.prefixHadNoEndingRequest)throw Error('Prefix unexpectedly requested ending assets');
  log.responsesBeforeEndingCheck=log.responses.length;
  log.expectedEndingFailure=await page.evaluate(async()=>{
   try{await window.renderFrame(10);return{unexpectedSuccess:true};}
   catch(e){return{code:e.code,message:e.message,cause:String(e.cause)};}
  });
  if(log.expectedEndingFailure.code!=='S29_ENDING_PREPARATION_MISSING')throw Error('Missing ending did not fail explicitly');
  log.status='PREFIX_000_239_COVERAGE_AND_FIVE_ACTUAL_KEYS_PASS_ENDING_EXPLICITLY_MISSING';
 }catch(e){log.status='FAILED_PRESERVED';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(browser)await browser.close();if(server)await new Promise(ok=>server.close(ok));save();console.log(JSON.stringify({status:log.status,newSceneFrames:log.newSceneFrames.length,error:log.error}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
