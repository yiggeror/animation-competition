// Real S15 renderFrame, frozen shared dependencies. Only representative frames;
// no production mutation, noS14 rerender, no audio action.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {execFileSync}=require('child_process'),{chromium}=require('playwright');
const repo=execFileSync('git',['rev-parse','--show-toplevel'],{encoding:'utf8'}).trim(),own=path.relative(repo,__dirname).split(path.sep).join('/');
const commit='23853d082d3ff59bf7722e9028647c9b80ff45b9';
const out=process.env.S15_GATE_OUTPUT||'/tmp/s15_F000_E_interface_representatives_20261020';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 if(fs.existsSync(out))throw Error('Existing actual representatives preserved; no automatic retry');fs.mkdirSync(out,{recursive:true});
 const log={status:'RUNNING',sourceCommit:commit,width:1920,height:1080,fps:24,actual:[],requests:[],pageErrors:[],requestFailures:[],productionFilesModified:false,newImageCalls:0};
 const cache=new Map();
 const server=http.createServer((req,res)=>{
  const u=new URL(req.url,'http://localhost'),rel=decodeURIComponent(u.pathname).replace(/^\//,'');
  if(rel.includes('..')){res.writeHead(403).end();return;}
  if(rel==='favicon.ico'){res.writeHead(204).end();return;}
  try{
   let b;
   if(rel.startsWith(own+'/'))b=fs.readFileSync(path.join(repo,rel));
   else{if(!cache.has(rel))cache.set(rel,execFileSync('git',['show',commit+':'+rel],{cwd:repo,maxBuffer:64*1024*1024}));b=cache.get(rel);}
   log.requests.push({path:rel,status:200,bytes:b.length,sha256:sha(b),source:rel.startsWith(own+'/')?'isolated candidate':'frozen shared commit'});
   res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg'})[path.extname(rel)]||'application/octet-stream');res.end(b);
  }catch(e){log.requests.push({path:rel,status:404,error:String(e)});res.writeHead(404).end();}
 });
 let browser;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  // Two original real scene references; remaining original states rendered once
  // through the candidate whose ONLY change is the F000 input path.
  for(const [candidate,frames] of [[false,[0,107]],[true,[0,72,107,108,112,116,120,124,132,144,191]]]){
   const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);
   page.on('pageerror',e=>log.pageErrors.push(e.message));page.on('requestfailed',r=>log.requestFailures.push({url:r.url(),failure:r.failure()}));
   await page.goto(`http://127.0.0.1:${server.address().port}/${own}/representative_actual.html?candidate=${candidate?1:0}`);await page.waitForFunction(()=>window.ready===true);
   for(const f of frames){
    const value=await page.evaluate(f=>window.captureActualS15(f),f),b=Buffer.from(value.png.split(',')[1],'base64');delete value.png;
    if(log.pageErrors.length||log.requestFailures.length||log.requests.some(r=>r.status>=400))throw Error('Real scene dependency/page failure');
    const file=`${candidate?'CANDIDATE':'ORIGINAL'}_F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,file),b);log.actual.push({...value,file,sha256:sha(b),bytes:b.length});fs.writeFileSync(path.join(out,'EXECUTION_LOG_RUNNING.json'),JSON.stringify(log,null,2)+'\n');console.log(candidate?'candidate':'original',f);
   }
   await page.close();
  }
  log.status='REPRESENTATIVE_SCENES_COMPLETE_PENDING_VISUAL_F000_TO_F108_BODY_REVIEW';
 }catch(e){log.status='FAILED_PRESERVED_NO_AUTOMATIC_RETRY';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));log.finishedUTC=new Date().toISOString();fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');console.log(JSON.stringify({status:log.status,actualCount:log.actual.length,error:log.error,out}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
