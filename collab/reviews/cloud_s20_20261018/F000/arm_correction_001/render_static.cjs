// Render only two locally authored static SVG guides, no animation/scene/model.
const fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
(async()=>{
 const root=__dirname;
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1672,height:941},deviceScaleFactor:1});
 for(const name of ['arm_volume_layers','full_arm_volume_xray']){
  await page.setContent(fs.readFileSync(path.join(root,'svg',name+'.svg'),'utf8'));
  await page.evaluate(async()=>{for(const img of document.querySelectorAll('image')){const href=img.getAttribute('href');if(href){const probe=new Image();probe.src=href;await probe.decode();}}});
  await page.addStyleTag({content:'html,body{margin:0;padding:0;width:1672px;height:941px;background:transparent;overflow:hidden}svg{display:block}'});
  await page.screenshot({path:path.join(root,name+'.png'),omitBackground:true});
  console.log(name+' static reference rasterized');
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
