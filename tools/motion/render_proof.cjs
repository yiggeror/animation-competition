const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'../..');
const {start}=require(path.join(ROOT,'tools/js/serve.cjs'));
const [outDir,mode='normal',timesArg]=process.argv.slice(2);
const times=timesArg?JSON.parse(timesArg):Array.from({length:72},(_,i)=>i/24);
const deps=['js/motion/pullcord_proof.js','js/motion/xiaoman_proof.js','js/cut/rig.js','js/cut/render.js','js/lib/figure.js','js/lib/draw.js','tools/motion/render_proof.cjs'];
const hashes=()=>Object.fromEntries(deps.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,p))).digest('hex')]));
(async()=>{fs.mkdirSync(outDir,{recursive:true});const before=hashes(),srv=await start(0);let browser;
try{browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();page.on('pageerror',e=>console.error(e.message));
 await page.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=js/motion/pullcord_proof.js&w=960&h=540`);
 await page.waitForFunction(()=>window.__ready||window.__error,null,{timeout:30000});if(await page.evaluate(()=>window.__error))throw Error(await page.evaluate(()=>window.__error));
 const frames=[];for(const t of times){const r=await page.evaluate(async({t,mode})=>{const m=await import('/js/motion/pullcord_proof.js'),c=document.getElementById('c');const metrics=m.renderFrame(c.getContext('2d'),t,960,540,{skeleton:mode==='skeleton'});return {png:c.toDataURL('image/png'),metrics};},{t,mode});
 const file=`f${String(Math.round(t*24)).padStart(4,'0')}.png`,bytes=Buffer.from(r.png.split(',')[1],'base64');fs.writeFileSync(path.join(outDir,file),bytes);frames.push({file,t,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),metrics:r.metrics});if(frames.length%24===0)console.log(JSON.stringify({frames:frames.length,mode}));}
 const after=hashes();fs.writeFileSync(path.join(outDir,'manifest.json'),JSON.stringify({worktree:ROOT,branch:require('child_process').execFileSync('git',['branch','--show-current'],{cwd:ROOT,encoding:'utf8'}).trim(),head:require('child_process').execFileSync('git',['rev-parse','HEAD'],{cwd:ROOT,encoding:'utf8'}).trim(),mode,width:960,height:540,fps:24,no_interpolation:true,source_before:before,source_after:after,source_unchanged:JSON.stringify(before)===JSON.stringify(after),browser:browser.version(),frames},null,2)+'\n');
}finally{if(browser)await browser.close();srv.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
