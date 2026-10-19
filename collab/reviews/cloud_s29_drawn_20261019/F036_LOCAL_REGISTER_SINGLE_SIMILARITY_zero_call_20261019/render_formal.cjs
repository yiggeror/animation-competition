const fs=require('fs'),path=require('path'),crypto=require('crypto'),{chromium}=require('playwright');
const repo=path.resolve(__dirname,'../../../..'),{start}=require(path.join(repo,'tools/js/serve.cjs'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const candidate=process.argv[2];if(!candidate||!fs.existsSync(path.join(repo,candidate)))throw Error('Pass existing candidate PNG relative to repository root');
 const source=path.join(repo,'js/paint/shots/s29.js'),before=sha(source),server=await start(0);
 let browser;const log={frame:36,time:1.5,candidate,candidateSHA256:sha(path.join(repo,candidate)),sourceSHA256Before:before,responses:[],failed:[],pageerrors:[],runtimeExportOnly:true};
 try{
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));page.on('requestfailed',r=>log.failed.push({url:r.url(),failure:r.failure()}));page.on('pageerror',e=>log.pageerrors.push(e.message));
  await page.route('**/js/paint/shots/s29.js?readonlyShotExport=1',async r=>r.fulfill({status:200,contentType:'text/javascript',body:fs.readFileSync(source,'utf8')+'\nexport {shot as sourceShot};\n'}));
  const base='collab/reviews/cloud_s29_drawn_20261019/F036_LOCAL_REGISTER_SINGLE_SIMILARITY_zero_call_20261019/';
  await page.goto(`http://127.0.0.1:${server.address().port}/${base}formal.html?candidate=${encodeURIComponent('/'+candidate)}`);
  await page.waitForFunction(()=>window.ready===true,null,{timeout:120000});
  const outputs=await page.evaluate(()=>window.payload);
  for(const [name,url]of Object.entries(outputs))fs.writeFileSync(path.join(__dirname,name),Buffer.from(url.split(',')[1],'base64'));
  fs.writeFileSync(path.join(__dirname,'qa/formal_actual_geometry.json'),JSON.stringify(await page.evaluate(()=>window.geometry),null,2)+'\n');
  log.outputs=Object.keys(outputs);log.sourceSHA256After=sha(source);log.sourceUnchanged=before===log.sourceSHA256After;
  log.pass=log.sourceUnchanged&&!log.failed.length&&!log.pageerrors.length&&log.responses.every(r=>r.status<400);
  fs.writeFileSync(path.join(__dirname,'qa/formal_browser_source_check.json'),JSON.stringify(log,null,2)+'\n');
  console.log(JSON.stringify({outputs:log.outputs,sourceUnchanged:log.sourceUnchanged,failed:log.failed,pageerrors:log.pageerrors,pass:log.pass}));if(!log.pass)process.exitCode=1;
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
