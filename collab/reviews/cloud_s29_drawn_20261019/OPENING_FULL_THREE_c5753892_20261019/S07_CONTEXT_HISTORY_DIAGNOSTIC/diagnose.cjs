// Finite S07 diagnostic only. Unmodified production modules, no MP4 and no S01/S04 frames.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto'),{chromium}=require('playwright');
const root=process.cwd(),out=__dirname,hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const expected=JSON.parse(fs.readFileSync(path.join(root,'collab/reviews/20261019_1203_opening_full_gate/EXPECTED.json')));
const report={purpose:'Isolate fresh Canvas versus sequential S07 history at F008; strict expected SHA unchanged',sourceChecks:[],cases:[],errors:[],console:[],responses:[]};
for(const [p,want] of Object.entries(expected.sources)){const actual=hash(fs.readFileSync(path.join(root,p)));report.sourceChecks.push({path:p,actual,expected:want,pass:actual===want});}
if(report.sourceChecks.some(x=>!x.pass))throw Error('Frozen production source mismatch');
(async()=>{
 const server=http.createServer((req,res)=>{const url=new URL(req.url,'http://localhost'),p=path.resolve(root,'.'+decodeURIComponent(url.pathname));if(!p.startsWith(root+path.sep)){res.writeHead(403);return res.end();}if(url.pathname==='/__s07_diagnostic__.html'){res.setHeader('Content-Type','text/html');return res.end('<!doctype html><link rel="icon" href="data:,"><canvas width="1920" height="1080"></canvas>');}try{res.setHeader('Content-Type',p.endsWith('.js')?'text/javascript':p.endsWith('.png')?'image/png':'application/octet-stream');res.end(fs.readFileSync(p));}catch(e){res.writeHead(404);res.end();}});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 let browser;
 try{
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const specs=[{name:'FRESH_DIRECT_F008',frames:[8]},{name:'FRESH_S07_SEQUENCE_000_008',frames:[0,1,2,3,4,5,6,7,8]},{name:'FRESH_CPU_CONTEXT_F008',frames:[8],willReadFrequently:true}];
  for(const spec of specs.filter(x=>!process.env.DIAGNOSTIC_CASE||x.name===process.env.DIAGNOSTIC_CASE)){
   const page=await browser.newPage({viewport:{width:1920,height:1080}});
   page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+' '+r.failure()?.errorText));page.on('console',m=>report.console.push({case:spec.name,type:m.type(),text:m.text()}));page.on('response',r=>report.responses.push({case:spec.name,url:r.url(),status:r.status()}));
   await page.goto(`http://127.0.0.1:${server.address().port}/__s07_diagnostic__.html`);
   if(spec.willReadFrequently)await page.evaluate(()=>document.querySelector('canvas').getContext('2d',{willReadFrequently:true}));
   await page.evaluate(async()=>{window.mods={};for(const s of ['S01','S04','S07'])window.mods[s]=await import('/js/anim/'+s.toLowerCase()+'_drawn.js');});
   const result={name:spec.name,frames:[]};
   for(const frame of spec.frames){
    const data=await page.evaluate(async frame=>{const c=document.querySelector('canvas');await window.mods.S07.renderFrame(c.getContext('2d'),frame/24,1920,1080);return {png:c.toDataURL('image/png'),attributes:c.getContext('2d').getContextAttributes()};},frame),b=Buffer.from(data.png.split(',')[1],'base64');
    result.frames.push({frame,sha256:hash(b),contextAttributes:data.attributes});
    if(frame===8){fs.writeFileSync(path.join(out,spec.name+'.png'),b);result.pass=hash(b)===expected.samples['S07_F008.png'];result.expected=expected.samples['S07_F008.png'];}
    console.log(JSON.stringify({case:spec.name,frame,sha256:hash(b),expected:frame===8?expected.samples['S07_F008.png']:null}));
   }
   report.cases.push(result);await page.close();fs.writeFileSync(path.join(out,process.env.DIAGNOSTIC_CASE?'RESULT_'+process.env.DIAGNOSTIC_CASE+'.json':'RESULT.json'),JSON.stringify(report,null,2)+'\n');
  }
 }finally{if(browser)await browser.close();await new Promise(r=>server.close(r));fs.writeFileSync(path.join(out,process.env.DIAGNOSTIC_CASE?'RESULT_'+process.env.DIAGNOSTIC_CASE+'.json':'RESULT.json'),JSON.stringify(report,null,2)+'\n');}
})().catch(e=>{console.error(e);process.exitCode=1});
