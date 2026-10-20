const fs=require('fs'),path=require('path'),http=require('http'),{chromium}=require('playwright');
(async()=>{
 const root=path.resolve(process.env.S31_LOAD_ROOT || path.join(__dirname,'load_fixture'));const requests=[];
 const srv=http.createServer((req,res)=>{const p=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]));if(!p.startsWith(root+path.sep)){res.writeHead(403);return res.end()};if(req.url==='/index.html'){res.setHeader('Content-Type','text/html');return res.end('<!doctype html><title>S31 import-only verification</title>')};try{const data=fs.readFileSync(p);res.setHeader('Content-Type',p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'application/octet-stream');requests.push({path:req.url,status:200});res.end(data)}catch(e){requests.push({path:req.url,status:404});res.writeHead(404);res.end('Missing')}});await new Promise(r=>srv.listen(0,'127.0.0.1',r));
 let browser;try{browser=await chromium.launch({...(process.env.S31_BROWSER_EXECUTABLE?{executablePath:process.env.S31_BROWSER_EXECUTABLE}:{}),headless:true,args:['--no-sandbox']});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
 const assetPaths=JSON.parse(fs.readFileSync(path.join(__dirname,'fixture_sha_check.json'))).map(x=>'/'+x.path);
 const result=await page.evaluate(async(paths)=>{
  const m=await import('/js/paint/shots/s31_drawn.js');const frozen=await import('/collab/reviews/20261020_0031_s31_complete336_gate/scene_preview/s31_complete_candidate.js');
  const assets=await Promise.all(paths.map(async p=>{const r=await fetch(p);return {path:p,status:r.status,bytes:(await r.arrayBuffer()).byteLength}}));
  const bindings=Array.from({length:180},(_,f)=>m.frameBinding(f));const rods=Array.from({length:180},(_,f)=>m.turtleBindingAtFrame(f).rodLengths);
  return{duration:m.DURATION,fps:m.FPS,sameRenderFunction:m.render===frozen.render,sameRenderFrameFunction:m.renderFrame===frozen.renderFrame,exposures:m.EXPOSURES.length,drawings:Object.keys(m.STATE_BINDINGS).length,bindingsValid:bindings.every((x,f)=>x.frame===f),BFrameReturnsNull:m.frameBinding(180)===null,finiteRodLengths:rods.flat().every(Number.isFinite),assets,renderFunctionsInvoked:0};
 },assetPaths);
 result.pageErrors=errors;result.requests=requests;result.pass=result.duration===14&&result.fps===24&&result.sameRenderFunction&&result.sameRenderFrameFunction&&result.bindingsValid&&result.BFrameReturnsNull&&result.finiteRodLengths&&result.assets.every(x=>x.status===200)&&!errors.length;
 fs.writeFileSync(path.join(__dirname,'BROWSER_LOAD_ONLY_CHECK.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({pass:result.pass,assets:result.assets.length,pageErrors:errors,sameRenderFunction:result.sameRenderFunction,renderFunctionsInvoked:0}));if(!result.pass)process.exitCode=1;
 }finally{if(browser)await browser.close();srv.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
