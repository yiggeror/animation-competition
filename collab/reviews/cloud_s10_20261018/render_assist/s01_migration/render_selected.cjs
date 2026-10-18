// Read-only selected-frame probe. No source module, renderer or asset edits.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('playwright');
const sourceRoot=process.argv[2],outRoot=__dirname;
const {start}=require(path.join(sourceRoot,'tools/js/serve.cjs'));
const frames=[0,10,12,20,28,29,30,31,32,33,34,35,43,50,62,70,83];
(async()=>{const srv=await start(0);const browser=await chromium.launch({executablePath:'/usr/bin/chromium'});
 const page=await browser.newPage({viewport:{width:400,height:300}}),responses=[],failures=[],consoleErrors=[],pageErrors=[],favicon=[];
 // Browser housekeeping icon is handled locally, without touching any scene resource.
 await page.route('**/favicon.ico',async route=>{favicon.push(route.request().url());await route.fulfill({status:204,body:''});});
 page.on('response',r=>responses.push({url:r.url(),status:r.status(),resourceType:r.request().resourceType()}));
 page.on('requestfailed',r=>failures.push({url:r.url(),failure:r.failure()}));
 page.on('pageerror',e=>pageErrors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
 const url=`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=js%2Fanim%2Fs01_drawn.js&w=1280&h=720`;
 await page.goto(url);await page.waitForFunction(()=>window.__ready===true||window.__error,null,{timeout:60000});
 const error=await page.evaluate(()=>window.__error);if(error)throw new Error(error);
 const dir=path.join(outRoot,'frames');fs.mkdirSync(dir,{recursive:true});const outputs=[];
 for(const f of frames){const png=await page.evaluate(async t=>{await window.renderFrame(t);return document.getElementById('c').toDataURL('image/png');},f/24);const buf=Buffer.from(png.split(',')[1],'base64');const filename=`F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(dir,filename),buf);outputs.push({frame:f,file:'frames/'+filename,bytes:buf.length,sha256:crypto.createHash('sha256').update(buf).digest('hex')});console.log('actual canvas F'+String(f).padStart(3,'0'));}
 await browser.close();srv.close();
 const bad=responses.filter(r=>r.status>=400);const report={sourceRoot,module:'js/anim/s01_drawn.js',frames,outputs,responses,failedRequests:failures,httpErrors:bad,pageErrors,consoleErrors,localFavicon204: favicon,browser:'system /usr/bin/chromium',dimensions:[1280,720],fps:24,fullShotRerendered:false};
 fs.writeFileSync(path.join(outRoot,'browser_resources.json'),JSON.stringify(report,null,2)+'\n');
 if(bad.length||failures.length||pageErrors.length||consoleErrors.length)throw new Error('Resource/console failure recorded; inspect browser_resources.json');
 console.log(`Selected ${frames.length} frames complete; resource HTTP errors0.`);
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
