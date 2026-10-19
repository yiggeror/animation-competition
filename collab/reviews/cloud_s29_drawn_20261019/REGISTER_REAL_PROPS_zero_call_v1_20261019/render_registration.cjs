const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const repo=path.resolve(__dirname,'../../../..');
const {start}=require(path.join(repo,'tools/js/serve.cjs'));
(async()=>{
 const mode=process.argv[2]||'scene';const server=await start(0);
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage();const log={mode,requests:[],responses:[],failed:[],pageerrors:[],readonlyRuntimeExport:'s29 source appended export only in intercepted browser response; on-disk source unchanged'};
 page.on('request',r=>log.requests.push(r.url()));page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));
 page.on('requestfailed',r=>log.failed.push({url:r.url(),error:r.failure()}));page.on('pageerror',e=>log.pageerrors.push(e.message));
 await page.route('**/js/paint/shots/s29.js?readonlyShotExport=1',async route=>{
  const src=fs.readFileSync(path.join(repo,'js/paint/shots/s29.js'),'utf8');
  await route.fulfill({status:200,contentType:'text/javascript',body:src+'\nexport {shot as sourceShot};\n'});
 });
 await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s29_drawn_20261019/REGISTER_REAL_PROPS_zero_call_v1_20261019/registration.html?mode=${mode}`);
 await page.waitForFunction(()=>window.ready===true,null,{timeout:60000});
 const payload=await page.evaluate(()=>window.payload);
 for(const [name,data]of Object.entries(payload))fs.writeFileSync(path.join(__dirname,name),Buffer.from(data.split(',')[1],'base64'));
 fs.writeFileSync(path.join(__dirname,`qa/${mode}_actual_geometry.json`),JSON.stringify(await page.evaluate(()=>window.geometry),null,2)+'\n');
 fs.writeFileSync(path.join(__dirname,`qa/${mode}_browser_resource_log.json`),JSON.stringify(log,null,2)+'\n');
 await browser.close();server.close();console.log(JSON.stringify({mode,outputs:Object.keys(payload),failed:log.failed,pageerrors:log.pageerrors}));
})().catch(e=>{console.error(e);process.exit(1);});
