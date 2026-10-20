// One authorized actual CAM20 F128 frame. No loop over shot or future states.
const fs=require('fs'),http=require('http'),path=require('path');
const{chromium}=require('playwright');
const out=__dirname,root=path.resolve(out,'..'),logs=[];
const server=http.createServer((q,r)=>{
  const f=path.resolve(root,'.'+new URL(q.url,'http://localhost').pathname);
  if(!f.startsWith(root+path.sep)){r.writeHead(403);r.end();return;}
  fs.readFile(f,(e,b)=>{if(e){r.writeHead(404);r.end();return;}
    r.setHeader('Content-Type',/\.(mjs|js)$/.test(f)?'application/javascript':
      f.endsWith('.json')?'application/json':f.endsWith('.png')?'image/png':'text/html');r.end(b);});
});
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,
    args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  try{
    const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
    page.on('pageerror',e=>logs.push('ERROR '+String(e)));
    page.on('console',m=>logs.push(m.type()+':'+m.text()));
    await page.goto(`http://127.0.0.1:${server.address().port}/next_F132_belly_up_stop_input_001/index_DIAGNOSTIC.html`);
    await page.waitForFunction(()=>window.ready,{timeout:60000});
    const r=await page.evaluate(()=>window.renderCurrent(132));
    for(const[n,data]of Object.entries(r.images))fs.writeFileSync(path.join(out,n),Buffer.from(data.split(',')[1],'base64'));
    fs.writeFileSync(path.join(out,'actual_CAM20_132_geometry_DIAGNOSTIC.json'),JSON.stringify(r.report,null,2)+'\n');
    console.log('Saved actual CAM20 F132 mechanism preflight with unchanged locked128 person. Not a132 pose or generation input.');
  }finally{
    fs.writeFileSync(path.join(out,'browser_console.log'),logs.join('\n')+'\n');
    await browser.close();server.close();
  }
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
