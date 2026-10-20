const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{execFileSync}=require('child_process'),{chromium}=require('playwright');
const repo=execFileSync('git',['rev-parse','--show-toplevel'],{encoding:'utf8'}).trim();
const out='/tmp/s14_ground_contact_pairs_20261020';const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 if(fs.existsSync(out))throw Error('Preserve existing outputs, no automatic retry');fs.mkdirSync(out,{recursive:true});
 const log={status:'RUNNING',purpose:'Same actual frame/camera/light/source; only ground-contact mode changes. Early grain held stable in both modes to isolate shadow.',frames:[],errors:[],requests:[]};
 const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost');if(u.pathname==='/favicon.ico'){res.writeHead(204).end();return;}const f=path.resolve(repo,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(repo+path.sep)){res.writeHead(403).end();return;}fs.readFile(f,(e,b)=>{log.requests.push({path:u.pathname,status:e?404:200});if(e){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.png':'image/png'})[path.extname(f)]||'application/octet-stream');res.end(b);});});let browser;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for(const ground of [0,1])for(const [tail,frames] of [[false,[0,81]],[true,[132,156,162,239]]]){
   const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);page.on('pageerror',e=>log.errors.push(e.message));page.on('requestfailed',r=>log.errors.push(r.url()));
   await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s14_scene_20261020/preview.html?ground=${ground}${tail?'&backstage=1&steps=1':''}`);await page.waitForFunction(()=>window.ready===true);
   for(const f of frames){const binding=await page.evaluate(f=>window.drawActualFrame(f),f),png=await page.locator('canvas').screenshot({type:'png'});if(log.errors.length||log.requests.some(r=>r.status>=400))throw Error('Actual scene resource/page failure');const name=`${ground?'PER_FOOT':'OLD_NOMINAL'}_F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,name),png);log.frames.push({frame:f,ground,binding,file:name,sha256:sha(png),grounding:await page.evaluate(()=>window.groundingReport())});console.log(ground?'per foot':'old nominal',f);}
   await page.close();
  }
  log.status='ACTUAL_SHADOW_PAIRS_COMPLETE_PENDING_VISUAL_CONTACT_REVIEW';
 }catch(e){log.status='FAILED_PRESERVED';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');console.log(JSON.stringify({status:log.status,count:log.frames.length,error:log.error,out}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
