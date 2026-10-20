// Explicit six-PNG review gate. Run only on the authorized original cloud.
// Importing this file starts neither a browser nor a server. No video/EDL writes.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {start}=require('./host.cjs');
const FRAMES=[0,23,24,29,30,35],sha=b=>crypto.createHash('sha256').update(b).digest('hex');
async function run({playwright,repo,out=path.join(__dirname,'actual_early_six'),executablePath='/usr/bin/chromium'}){
 const repoRoot=path.resolve(repo||process.cwd());
 const indexBytes=fs.readFileSync(path.join(__dirname,'EARLY_RENDER_INDEX.json'));
 const index=JSON.parse(indexBytes);
 const readback=()=>index.files.map(r=>{const b=fs.readFileSync(path.join(repoRoot,r.path));if(sha(b)!==r.sha256)throw Error('Readback mismatch: '+r.path);return {...r,bytes:b.length};});
 const before=readback();fs.mkdirSync(out,{recursive:true});
 const log={status:'PENDING_ACTUAL_VISUAL_REVIEW',scope:'Six new formal PNGs only: 000/023/024/029/030/035',started:new Date().toISOString(),sourceReadbackBefore:before,frames:[],failed:[],pageErrors:[],consoleErrors:[],responses:[]};
 const server=await start(0,repoRoot);let browser;
 try {
  browser=await playwright.chromium.launch({executablePath,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage();page.on('requestfailed',r=>log.failed.push({url:r.url(),failure:r.failure()}));page.on('pageerror',e=>log.pageErrors.push(e.message));page.on('response',r=>log.responses.push({url:r.url(),status:r.status()}));page.on('console',m=>{if(m.type()==='error')log.consoleErrors.push(m.text());});
  await page.goto(`http://127.0.0.1:${server.address().port}/host.html`);await page.waitForFunction(()=>window.ready===true,null,{timeout:120000});
  for(const f of FRAMES){const r=await page.evaluate(f=>window.renderActual(f),f),b=Buffer.from(r.png.split(',')[1],'base64'),file=`S29_F${String(f).padStart(3,'0')}.png`;fs.writeFileSync(path.join(out,file),b);log.frames.push({...r.geometry,file,pngSHA256:sha(b)});console.log('Rendered',file,'state',r.geometry.state);}
  log.sourceReadbackAfter=readback();log.sourceUnchanged=JSON.stringify(before)===JSON.stringify(log.sourceReadbackAfter)&&sha(indexBytes)===sha(fs.readFileSync(path.join(__dirname,'EARLY_RENDER_INDEX.json')));
  log.f000ExpectedExistingSHA256=index.f000ExistingFormalPNG_SHA256;log.f000MatchesExisting=log.frames[0].pngSHA256===index.f000ExistingFormalPNG_SHA256;
  log.technicalGate=log.sourceUnchanged&&log.frames.length===6&&log.f000MatchesExisting&&!log.failed.length&&!log.pageErrors.length&&!log.consoleErrors.length&&log.responses.every(r=>r.status<400);
  log.status=log.technicalGate?'SIX_PNGS_TECHNICALLY_COMPLETE_PENDING_VISUAL_REVIEW':'HOLD_TECHNICAL_MISMATCH';
 } finally {if(browser)await browser.close();server.close();log.finished=new Date().toISOString();fs.writeFileSync(path.join(out,'ACTUAL_EARLY_SIX.json'),JSON.stringify(log,null,2)+'\n');}
 if(!log.technicalGate)throw Error('Six-PNG technical gate HOLD; see ACTUAL_EARLY_SIX.json');return log;
}
module.exports={run,FRAMES};
if(require.main===module){const args=process.argv.slice(2),value=k=>{const i=args.indexOf(k);return i<0?undefined:args[i+1]};let playwright;try{playwright=require(value('--playwright')||'playwright');}catch(e){throw Error('Use existing Playwright path; no package or service installation. '+e.message);}
run({playwright,repo:value('--repo'),out:value('--out'),executablePath:value('--chromium')}).catch(e=>{console.error(e);process.exitCode=1;});}
