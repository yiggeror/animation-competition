// Run only on the already authorized original cloud executor, by the coordinator.
// Does not launch from importing this file. No generation, edits to production, or EDL writes.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {start}=require('./host.cjs');
async function run({playwright,repo,frames,out=path.join(__dirname,'actual_few'),executablePath='/usr/bin/chromium'}){
  const reference=JSON.parse(fs.readFileSync(path.join(__dirname,'ACTUAL_REFERENCE_INDEX.json')));
  frames ??= reference.frames;
  if(!Array.isArray(frames)||!frames.length||frames.some(f=>!Number.isInteger(f)||!reference.frames.includes(f)))throw Error('Only the explicit approved few-frame comparison index may run');
  const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
  const readback=()=>{const index=JSON.parse(fs.readFileSync(path.join(__dirname,'DELIVERY_INDEX.json'))),rows=[...index.runtime,...index.controlFiles];return rows.map(r=>{const isRuntime=!!r.productionCandidatePath; const resolved=isRuntime?path.join(path.resolve(repo||path.join(__dirname,'../../..')),r.productionCandidatePath):path.join(__dirname,r.packagePath); const b=fs.readFileSync(resolved);if(hash(b)!==r.sha256)throw Error('Source/readback mismatch: '+r.packagePath);return {path:r.packagePath,sha256:hash(b),bytes:b.length};});};
  const before=readback();
  if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('Output directory already contains files; do not duplicate an actual run');fs.mkdirSync(out,{recursive:true});const log={sourceReadbackBefore:before,started:new Date().toISOString(),scope:'partial036–071 only',frames:[],failed:[],pageErrors:[],consoleErrors:[],responses:[]};
  const server=await start(0,repo);let browser;
  try{
    browser=await playwright.chromium.launch({executablePath,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
    const page=await browser.newPage();page.on('requestfailed',r=>log.failed.push({url:r.url(),failure:r.failure()}));page.on('pageerror',e=>log.pageErrors.push(e.message));page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));page.on('console',m=>{if(m.type()==='error')log.consoleErrors.push(m.text());});
    await page.goto(`http://127.0.0.1:${server.address().port}/host.html`);await page.waitForFunction(()=>window.ready===true,null,{timeout:120000});
    for(const f of frames){const result=await page.evaluate(f=>window.renderActual(f),f),b=Buffer.from(result.png.split(',')[1],'base64'),name=`S29_F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,name),b);log.frames.push({...result.geometry,file:name,pngSHA256:crypto.createHash('sha256').update(b).digest('hex')});const checked=log.frames[log.frames.length-1];checked.expectedCanvasPNG_SHA256=reference.references[String(f)].canvasPNG_SHA256;checked.matchesOriginalCanvas=checked.pngSHA256===checked.expectedCanvasPNG_SHA256;console.log('actual S29',f,result.geometry.state,'matches original Canvas',checked.matchesOriginalCanvas);}
    log.sourceReadbackAfter=readback();log.sourceUnchanged=JSON.stringify(before)===JSON.stringify(log.sourceReadbackAfter);log.pass=log.sourceUnchanged&&log.frames.every(f=>f.matchesOriginalCanvas)&&!log.failed.length&&!log.pageErrors.length&&!log.consoleErrors.length&&log.responses.every(x=>x.status<400)&&log.frames.length===frames.length;
  }finally{if(browser)await browser.close();server.close();log.finished=new Date().toISOString();fs.writeFileSync(path.join(out,'ACTUAL_RUN.json'),JSON.stringify(log,null,2)+'\n');}
  if(!log.pass)throw Error('Actual render checks failed; see ACTUAL_RUN.json');return log;
}
module.exports={run};
if(require.main===module){const args=process.argv.slice(2),value=k=>{const i=args.indexOf(k);return i<0?undefined:args[i+1]};let playwright;try{playwright=require(value('--playwright')||'playwright');}catch(e){throw Error('Pass --playwright /existing/node_modules/playwright; do not install a new service: '+e.message);}
run({playwright,repo:value('--repo'),frames:value('--frames')?.split(',').map(Number),out:value('--out'),executablePath:value('--chromium')}).catch(e=>{console.error(e);process.exitCode=1;});}
