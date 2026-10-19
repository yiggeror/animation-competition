// Run from the production repository root after importing MANIFEST.json's 8 files.
// node /path/to/render_s06_browser86_stream.cjs /tmp/s06_browser86/S06.mp4
// One independent Chromium page. All 86 frames are painted separately; PNGs stream to ffmpeg.
const fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const root=process.cwd();const{chromium}=require(require.resolve('playwright',{paths:[root]}));const{start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const out=path.resolve(process.argv[2]||'/tmp/s06_browser86/S06.mp4');if(fs.existsSync(out))throw new Error('Output already exists; choose a new explicit output path: '+out);fs.mkdirSync(path.dirname(out),{recursive:true});
 const server=await start(0);let browser,ff;
 try{
  browser=await chromium.launch();const page=await browser.newPage({viewport:{width:400,height:300}});page.on('pageerror',e=>console.error('[pageerror]',e.message));page.on('console',m=>{if(m.type()==='error')console.error('[console]',m.text())});
  await page.goto(`http://127.0.0.1:${server.address().port}/dev/view.html?mod=js%2Fanim%2Fs06_drawn.js&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready===true||window.__error,null,{timeout:120000});
  const state=await page.evaluate(()=>({error:window.__error,duration:window.DURATION}));if(state.error)throw new Error(state.error);if(Math.round(state.duration*24)!==86)throw new Error('S06 duration is not 86 frames');
  ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','24','-vcodec','png','-i','-','-frames:v','86','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-tune','animation','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
  const finished=new Promise((resolve,reject)=>{ff.on('error',reject);ff.on('close',c=>c===0?resolve():reject(new Error('ffmpeg exit '+c)));});
  for(let f=0;f<86;f++){
   const data=await page.evaluate(async t=>{await window.renderFrame(t);return document.getElementById('c').toDataURL('image/png')},f/24);const bytes=Buffer.from(data.split(',')[1],'base64');
   if(f===0||f===85)fs.writeFileSync(path.join(path.dirname(out),`S06_BROWSER_F${String(f).padStart(3,'0')}.png`),bytes);
   if(!ff.stdin.write(bytes))await new Promise((resolve,reject)=>{ff.stdin.once('drain',resolve);ff.stdin.once('error',reject)});
   if((f+1)%24===0||f===85)console.log(`${f+1}/86`);
  }
  ff.stdin.end();await finished;ff=null;console.log(out);
 }finally{if(ff)ff.kill();if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
