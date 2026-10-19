// Rasterizes one manually authored static SVG target. No scene or character rig.
const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{const p=await browser.newPage({viewport:{width:1672,height:941},deviceScaleFactor:1});
 await p.setContent('<!doctype html><html><body style="margin:0">'+fs.readFileSync(path.join(__dirname,'art/child_complete_new_pose.svg'),'utf8')+'</body></html>');
 await p.evaluate(async()=>{await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});
 await p.screenshot({path:path.join(__dirname,'art/child_complete_new_pose.png'),omitBackground:true});
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
