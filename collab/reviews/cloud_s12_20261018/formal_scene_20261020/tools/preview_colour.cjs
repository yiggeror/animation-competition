// A single new colour candidate preview, without rerendering the approved prefix.
const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const {start}=require(path.join(process.cwd(),'tools/js/serve.cjs'));
(async()=>{
 const out=path.resolve('collab/reviews/cloud_s12_20261018/formal_scene_20261020/colour_candidate');
 const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--disable-dev-shm-usage']});
 try{
  const page=await browser.newPage();
  await page.route('**/assets/chars/g12/F102_BG_fcdf16037858.png',r=>r.fulfill({path:path.join(out,'F102_BG_blue_cloth_candidate.png'),contentType:'image/png'}));
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js%2Fanim%2Fs12_drawn.js&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready||window.__error);
  const data=await page.evaluate(async()=>{if(window.__error)throw Error(window.__error);await window.renderFrame(102/24);return document.getElementById('c').toDataURL('image/png')});
  fs.writeFileSync(path.join(out,'F102_actual_colour_candidate.png'),Buffer.from(data.split(',')[1],'base64'));
  console.log('Single F102 colour candidate rendered with unchanged production optics; approved movie unchanged.');
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
