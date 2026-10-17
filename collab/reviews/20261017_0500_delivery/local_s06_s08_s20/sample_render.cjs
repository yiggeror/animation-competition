const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('playwright');
const {start}=require('/workspace/animation-competition/tools/js/serve.cjs');
const [mod,dir,ts]=process.argv.slice(2);const times=JSON.parse(ts);
(async()=>{fs.mkdirSync(dir,{recursive:true});const server=await start(0);let browser;
try {browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();
page.on('pageerror',e=>console.error(e.message));
const url=`http://127.0.0.1:${server.address().port}/dev/view.html?mod=${encodeURIComponent(mod)}&w=960&h=540&debug=${encodeURIComponent(JSON.stringify({sheetRes:450}))}`;
await page.goto(url);await page.waitForFunction(()=>window.__ready||window.__error,null,{timeout:45000});const err=await page.evaluate(()=>window.__error);if(err)throw Error(err);
const entries=[];for(const t of times){const data=await page.evaluate(async t=>{await window.renderFrame(t);return document.getElementById('c').toDataURL('image/png')},t);const bytes=Buffer.from(data.split(',')[1],'base64');const file=`f${String(Math.round(t*24)).padStart(4,'0')}.png`;fs.writeFileSync(path.join(dir,file),bytes);entries.push({file,t,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});console.log(JSON.stringify({file,t}));}
fs.writeFileSync(path.join(dir,'manifest.json'),JSON.stringify({method:'Original renderer, local diagnostic frames only',commit:'c044ecc8186cfd91e774ea2f41d0c28b5e3e09fa',module:mod,width:960,height:540,browser:browser.version(),debug:{sheetRes:450},entries},null,2)+'\n');
}finally{if(browser)await browser.close();server.close();}})().catch(e=>{console.error(e);process.exitCode=1});
