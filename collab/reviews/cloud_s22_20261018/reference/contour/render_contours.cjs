const fs=require('fs');const path=require('path');const {chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium'});const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const folder=__dirname;
 for(const f of ['000','024']){
  for(const kind of ['source','G','C']){
   const src=kind==='source'?path.join(folder,`F${f}_volume_source.svg`):`/tmp/s22_${kind}${f}.svg`;
   const out=kind==='source'?`/tmp/S22_F${f}_contour_base.png`:`/tmp/s22_${kind}${f}.png`;
   await page.setContent('<html><body style="margin:0;background:transparent">'+fs.readFileSync(src,'utf8')+'</body></html>');
   await page.screenshot({path:out,omitBackground:true});
  }
 }
 await browser.close();console.log('Two manual SVGs and temporary contact masks rasterized with installed Chromium.');})();
