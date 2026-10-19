// Harmless loopback static server; no network APIs, no image generation.
const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('playwright');
const root=__dirname;
const server=http.createServer((req,res)=>{
 const p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
 if(!p.startsWith(root+path.sep)&&p!==root){res.writeHead(403);res.end();return;}
 const file=p===root||p.endsWith('/')?path.join(p,'index.html'):p;
 fs.readFile(file,(e,b)=>{if(e){res.writeHead(404);res.end('missing');return;}res.setHeader('Content-Type',file.endsWith('.js')||file.endsWith('.mjs')?'application/javascript':file.endsWith('.json')?'application/json':file.endsWith('.png')?'image/png':'text/html');res.end(b);});
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const logs=[];
 try{
  for(const [tag,W,H] of [['CAM20_F000',1920,1080],['CAM20_F000_same_camera_tall_QA',1920,2160]]){
   const page=await browser.newPage({viewport:{width:W,height:H},deviceScaleFactor:1});
   page.on('console',m=>logs.push(m.type()+': '+m.text()));page.on('pageerror',e=>logs.push('ERROR: '+e.stack));
   await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);await page.waitForFunction(()=>window.ready,{timeout:60000});
   if(process.argv.includes('--scan')){const scan=await page.evaluate(()=>window.scanPuppets());fs.writeFileSync(path.join(root,'puppet_registration_options.json'),JSON.stringify(scan,null,2)+'\n');console.log(JSON.stringify(scan,null,2));await page.close();break;}
   const geo=await page.evaluate(()=>window.preflight());
   if(process.argv.includes('--preflight')){fs.writeFileSync(path.join(root,'geometry_preflight.json'),JSON.stringify(geo,null,2)+'\n');console.log(JSON.stringify(geo,null,2));await page.close();break;}
   console.log('Rendering '+tag);
   const report=await page.evaluate(async({W,H})=>window.renderF000(W,H),{W,H});
   const data=await page.evaluate(()=>document.querySelector('canvas').toDataURL('image/png'));
   fs.writeFileSync(path.join(root,tag+'.png'),Buffer.from(data.split(',')[1],'base64'));
   fs.writeFileSync(path.join(root,tag+'_geometry.json'),JSON.stringify(report,null,2)+'\n');
   console.log('Saved '+tag);await page.close();
  }
 }finally{fs.writeFileSync(path.join(root,'render_console.log'),logs.join('\n')+'\n');await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
