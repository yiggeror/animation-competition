const fs=require('fs'),path=require('path'),crypto=require('crypto'),{chromium}=require('playwright');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const rootPath='collab/reviews/20261019_1140_opening_continuity_candidate';
(async()=>{
 const out=process.env.OPENING_OUTPUT_DIR||'/tmp/opening-continuity-seven',origin=process.env.OPENING_BASE_URL||'http://127.0.0.1:8199';fs.mkdirSync(out,{recursive:true});
 const sources=['s01_drawn.js','s04_drawn.js','s07_drawn.js','opening_power_strip.js'].map(name=>({path:rootPath+'/'+name,sha256:hash(fs.readFileSync(path.join(__dirname,name)))}));
 const cases=[['S01',0],['S04',8],['S07',8],['S07',39],['S07',43],['S07',53],['S07',57]],rows=[],http=[],errors=[];
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 try{const page=await browser.newPage({viewport:{width:1920,height:1080}});page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>errors.push(r.url()+' '+r.failure()?.errorText));page.on('response',r=>http.push({url:r.url(),status:r.status()}));
 await page.route('**/__opening_verify__.html',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><link rel="icon" href="data:,"><canvas width="1920" height="1080"></canvas>'}));await page.goto(origin+'/__opening_verify__.html');
 await page.evaluate(async base=>{window.modules={};for(const s of ['S01','S04','S07'])window.modules[s]=await import('/'+base+'/'+s.toLowerCase()+'_drawn.js');},rootPath);
 for(const [shot,frame] of cases){const raw=await page.evaluate(async({shot,frame})=>{const c=document.querySelector('canvas');await window.modules[shot].renderFrame(c.getContext('2d'),frame/24,1920,1080);return c.toDataURL('image/png');},{shot,frame});const b=Buffer.from(raw.split(',')[1],'base64'),name=shot+'_F'+String(frame).padStart(3,'0')+'.png';fs.writeFileSync(path.join(out,name),b);const row={shot,frame,file:name,sha256:hash(b)};rows.push(row);console.log(JSON.stringify(row));}
 }finally{await browser.close();}
 const report={scope:'Actual seven-frame candidate only; full scene review remains pending',width:1920,height:1080,fps:24,sources,rows,http,errors,allSevenRendered:rows.length===7,allResourcesOk:http.every(r=>r.status<400),zeroErrors:errors.length===0};fs.writeFileSync(path.join(out,'SOURCE_AND_HTTP_CHECK.json'),JSON.stringify(report,null,2));if(rows.length!==7||errors.length||http.some(r=>r.status>=400))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
