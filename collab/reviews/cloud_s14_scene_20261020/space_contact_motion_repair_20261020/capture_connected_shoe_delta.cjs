const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{execFileSync}=require('child_process'),{chromium}=require('playwright');
const repo=execFileSync('git',['rev-parse','--show-toplevel'],{encoding:'utf8'}).trim();
const out='/tmp/s14_connected_shoe_delta_20261020';const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 if(fs.existsSync(out))throw Error('Preserve existing outputs, no automatic retry');fs.mkdirSync(out,{recursive:true});
 const log={status:'RUNNING',purpose:'Only confirmed detached-shoe-speckle fix: one actual132 key, no repeated12 pair capture or96frame rerender. Full-range geometry is measured without scene rendering.',frames:[],errors:[],requests:[]};
 const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost');if(u.pathname==='/favicon.ico'){res.writeHead(204).end();return;}const f=path.resolve(repo,'.'+decodeURIComponent(u.pathname));if(!f.startsWith(repo+path.sep)){res.writeHead(403).end();return;}fs.readFile(f,(e,b)=>{log.requests.push({path:u.pathname,status:e?404:200});if(e){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.png':'image/png'})[path.extname(f)]||'application/octet-stream');res.end(b);});});let browser;
 try{
  await new Promise(ok=>server.listen(0,'127.0.0.1',ok));browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  for(const ground of [1])for(const [tail,frames] of [[true,[132]]]){
   const page=await browser.newPage({viewport:{width:1920,height:1080}});page.setDefaultTimeout(180000);page.on('pageerror',e=>log.errors.push(e.message));page.on('requestfailed',r=>log.errors.push(r.url()));
   await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s14_scene_20261020/preview.html?ground=${ground}${tail?'&backstage=1&steps=1':''}`);await page.waitForFunction(()=>window.ready===true);
   for(const f of frames){const binding=await page.evaluate(f=>window.drawActualFrame(f),f),png=await page.locator('canvas').screenshot({type:'png'});if(log.errors.length||log.requests.some(r=>r.status>=400))throw Error('Actual scene resource/page failure');const name=`${ground?'PER_FOOT':'OLD_NOMINAL'}_F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,name),png);log.frames.push({frame:f,ground,binding,file:name,sha256:sha(png),grounding:await page.evaluate(()=>window.groundingReport())});console.log(ground?'per foot':'old nominal',f);}
   const gr=JSON.parse(fs.readFileSync(path.join(repo,'collab/reviews/cloud_s14_scene_20261020/published_grandma_exposures.json')));
   const rt=JSON.parse(fs.readFileSync(path.join(repo,'collab/reviews/cloud_s14_scene_20261020/BACKSTAGE_RETURN_132_167_EXPOSURE_PROPOSAL.json'))).trialRows;
   const tailRows=JSON.parse(fs.readFileSync(path.join(repo,'collab/reviews/cloud_s14_scene_20261020/published_child_tail_exposures.json')));
   log.fullRangeContacts=await page.evaluate(async ({gr,childRows})=>{
    const {groundedShadowLayers,currentGroundingReport}=await import('./space_contact_motion_repair_20261020/ground_contact.mjs');
    const {loadImg}=await import('/js/paint/paintshot.js');
    const results=[];
    for(const e of gr){groundedShadowLayers(await loadImg(e.path),{x:355,y:175,sc:.335},{kind:'grandmaWide',id:e.id,light:[540,487-226*.08]});results.push({frames:[e.frame,e.through],...currentGroundingReport().grandmaWide});}
    for(const e of childRows){const s=e.nativeToCommonScale??1,d=e.nativeToCommonTranslation;groundedShadowLayers(await loadImg(e.path),{x:453.6+d[0]*.16,y:458.32+d[1]*.16,sc:.16*s},{kind:'child',id:e.id,light:[600,390],nativeStoolOffset:e.nativeStoolOffset,groundedSoleRegions:e.groundedSoleRegions});results.push({frames:[e.frame,e.through],...currentGroundingReport().child});}
    return results;
   },{gr,childRows:[...rt,...tailRows]});
   await page.close();
  }
  log.status='ONE_ACTUAL_SHOE_DELTA_AND_ALL_EXPOSURE_CONTACT_GEOMETRY_COMPLETE';
 }catch(e){log.status='FAILED_PRESERVED';log.error=String(e.stack||e);process.exitCode=1;}
 finally{if(browser)await browser.close();if(server.listening)await new Promise(ok=>server.close(ok));fs.writeFileSync(path.join(out,'EXECUTION_LOG.json'),JSON.stringify(log,null,2)+'\n');console.log(JSON.stringify({status:log.status,count:log.frames.length,error:log.error,out}));}
})().catch(e=>{console.error(e);process.exitCode=1;});
