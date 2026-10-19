const fs=require('fs'),path=require('path');const {chromium}=require('playwright');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});try{
const page=await browser.newPage({viewport:{width:1672,height:941},deviceScaleFactor:1});
for(const f of process.argv.slice(2)){const file=path.resolve(f);await page.setContent('<!doctype html><body style="margin:0">'+fs.readFileSync(file,'utf8')+'</body>');await page.screenshot({path:file.replace(/\.svg$/,'.png'),omitBackground:true});}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
