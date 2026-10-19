// Bounded diagnostic only. Run from the fixed original repository root.
// Two fresh browser contexts, six draws; no source changes or movie re-render.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('playwright');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const root=process.cwd(),out=path.join(__dirname,'finite_ctx_diagnostic_ed1721c1');fs.mkdirSync(out,{recursive:true});
 const man=JSON.parse(fs.readFileSync(path.join(__dirname,'RAW_ASSET_REUSE_SHA.json')));
 const protectedFiles=[{path:path.relative(root,path.join(__dirname,'render_repository_keyframes.cjs')),sha256:'ee1be7b737925a68cbb5b252e9ad9282b681580b9ce6ecc50da97f0cfcc9931f'},{path:man.module_destination,sha256:man.candidate_module_sha256},...man.assets.map(a=>({path:a.destination_repo_path,sha256:a.sha256})),...Object.entries(man.expected_unchanged_helpers||{}).map(([path,sha256])=>({path,sha256})),...Object.entries(man.preexisting_assets||{}).map(([path,m])=>({path,sha256:m.sha256}))];
 const report={status:'STARTED',sourceCommit:'ed1721c17b4e27d1e72a4379cdd67eb3edfeef21',scriptSHA256:sha(fs.readFileSync(__filename)),freshContextSequences:[[0,0],[0,190,0,190]],draws:[],comparisons:[],sourceChecks:[],errors:[],missing:[],httpFailures:[],requestFailures:[],favicon:[],consoleWarnings:[],fullMovieRendered:false,productionSourceModified:false,strictHistoricalRepeat0Resolved:false,notes:['Original failed repeat000 pixels were not retained. This finite diagnostic does not reconstruct that image.','PNG then JPEG capture and explicit RGBA readback after each draw are diagnostic observations; those readbacks may affect browser Canvas backend selection.','A clean six-draw result excludes direct short cross-renderer contamination for this test, not arbitrary long-history non-determinism.']};
 let server,browser;
 const save=()=>fs.writeFileSync(path.join(out,'FINITE_CONTEXT_DIAGNOSTIC.json'),JSON.stringify(report,null,2)+'\n');
 const verify=stage=>{for(const a of protectedFiles){const h=sha(fs.readFileSync(path.join(root,a.path)));report.sourceChecks.push({stage,path:a.path,SHA256:h,pass:h===a.sha256});if(h!==a.sha256)throw Error('Protected source changed: '+a.path);}};
 try{
  verify('before');
  server=http.createServer((req,res)=>{
   let u;try{u=decodeURIComponent(new URL(req.url,'http://localhost').pathname)}catch{res.writeHead(400);res.end();return;}
   if(u==='/favicon.ico'){report.favicon.push({path:u,status:204,excludedFromSceneErrors:true});res.writeHead(204);res.end();return;}
   if(u==='/__s30_finite_diag.html'){res.setHeader('Content-Type','text/html');res.end('<html><body style="margin:0"><canvas id="c" width="1920" height="1080"></canvas><script type="module">window.s30=await import("/js/paint/shots/s30_drawn.js");window.snapshots=[];window.ready=true</script></body></html>');return;}
   const p=path.resolve(root,'.'+u);if(!p.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
   fs.readFile(p,(e,b)=>{if(e){report.missing.push(u);res.writeHead(404);res.end();return;}res.setHeader('Content-Type',({'.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg','.json':'application/json'})[path.extname(p)]||'application/octet-stream');res.end(b);});
  });
  await new Promise((ok,no)=>{server.once('error',no);server.listen(0,'127.0.0.1',ok)});
  report.previewURL=`http://127.0.0.1:${server.address().port}/__s30_finite_diag.html`;report.moduleURL=`http://127.0.0.1:${server.address().port}/js/paint/shots/s30_drawn.js`;
  const executablePath=process.env.CHROMIUM_PATH||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined);
  browser=await chromium.launch({headless:true,executablePath,args:['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  report.browserVersion=browser.version();
  for(const [ci,sequence]of report.freshContextSequences.entries()){
   const context=await browser.newContext({viewport:{width:1920,height:1080}}),page=await context.newPage();
   page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.requestFailures.push({url:r.url(),failure:r.failure()}));page.on('response',r=>{if(r.status()>=400)report.httpFailures.push({url:r.url(),status:r.status()})});page.on('console',m=>{if(['warning','error'].includes(m.type()))report.consoleWarnings.push({context:ci,type:m.type(),text:m.text()});});
   await page.goto(report.previewURL);await page.waitForFunction(()=>window.ready,{timeout:30000});
   for(const [i,f]of sequence.entries()){
    const r=await page.evaluate(async({i,f})=>{
     const c=document.getElementById('c'),x=c.getContext('2d');
     const state=()=>({globalAlpha:x.globalAlpha,globalCompositeOperation:x.globalCompositeOperation,filter:x.filter,imageSmoothingEnabled:x.imageSmoothingEnabled,imageSmoothingQuality:x.imageSmoothingQuality,transform:Array.from(x.getTransform().toFloat64Array()),attributes:x.getContextAttributes?.()||null});
     const before=state();await window.s30.renderFrame(x,f/24,c.width,c.height);const after=state();
     const png=c.toDataURL('image/png').split(',')[1],jpeg=c.toDataURL('image/jpeg',.96).split(',')[1],rgba=x.getImageData(0,0,c.width,c.height).data;
     const digest=await crypto.subtle.digest('SHA-256',rgba);const rgbaSHA=Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');
     window.snapshots.push({frame:f,rgba,rgbaSHA});const {source,...shotState}=window.s30.state(f/24);
     return{png,jpeg,rgbaSHA,before,after,shotState,index:i,frame:f};
    },{i,f});
    const name=`CTX${ci+1}_${i}_F${String(f).padStart(3,'0')}`,png=Buffer.from(r.png,'base64'),jpeg=Buffer.from(r.jpeg,'base64');
    fs.writeFileSync(path.join(out,name+'.png'),png);fs.writeFileSync(path.join(out,name+'.jpg'),jpeg);
    delete r.png;delete r.jpeg;report.draws.push({...r,context:ci+1,png:name+'.png',pngSHA256:sha(png),jpeg:name+'.jpg',jpegSHA256:sha(jpeg)});save();console.log('S30_DIAG',ci+1,i,f,r.rgbaSHA);
   }
   const pairs=ci===0?[[0,1]]:[[0,2],[1,3]];
   for(const [a,b]of pairs){
    const d=await page.evaluate(({a,b})=>{
     const A=window.snapshots[a],B=window.snapshots[b],W=1920,H=1080;
     const make=()=>({pixels:0,changedPixelsRGBA:0,changedPixelsRGB:0,maxAbsRGB:0,maxAbsAlpha:0,sumAbsRGB:0,sumSquaredRGB:0});
     const stats={all:make(),innerCircle470:make(),vignetteOuter486:make(),transitionRing470_486:make(),motherBodyBox:make(),TVContactBox:make(),motherFeetBox:make(),originalTailHeadBox:make()};
     const diff=new Uint8ClampedArray(W*H*4);
     for(let y=0;y<H;y++)for(let x=0;x<W;x++){
      const k=(y*W+x)*4,dr=Math.abs(A.rgba[k]-B.rgba[k]),dg=Math.abs(A.rgba[k+1]-B.rgba[k+1]),db=Math.abs(A.rgba[k+2]-B.rgba[k+2]),da=Math.abs(A.rgba[k+3]-B.rgba[k+3]),max=Math.max(dr,dg,db),sum=dr+dg+db,sq=dr*dr+dg*dg+db*db,r2=(x-960)**2+(y-540)**2;
      diff[k]=Math.min(255,dr*24);diff[k+1]=Math.min(255,dg*24);diff[k+2]=Math.min(255,db*24);diff[k+3]=255;
      const rs=['all'];if(r2<=470**2)rs.push('innerCircle470');if(r2>=486**2)rs.push('vignetteOuter486');if(r2>470**2&&r2<486**2)rs.push('transitionRing470_486');if(x>=270&&x<522&&y>=400&&y<782)rs.push('motherBodyBox');if(x>=270&&x<314&&y>=542&&y<572)rs.push('TVContactBox');if(x>=360&&x<472&&y>=748&&y<784)rs.push('motherFeetBox');if(x>=280&&x<1450&&y>=100&&y<1080)rs.push('originalTailHeadBox');
      for(const name of rs){const s=stats[name];s.pixels++;if(max||da)s.changedPixelsRGBA++;if(max)s.changedPixelsRGB++;s.maxAbsRGB=Math.max(s.maxAbsRGB,max);s.maxAbsAlpha=Math.max(s.maxAbsAlpha,da);s.sumAbsRGB+=sum;s.sumSquaredRGB+=sq;}
     }
     for(const s of Object.values(stats)){s.meanAbsRGB=s.sumAbsRGB/(3*s.pixels);s.RMS_RGB=Math.sqrt(s.sumSquaredRGB/(3*s.pixels));delete s.sumAbsRGB;delete s.sumSquaredRGB;}
     const c=document.createElement('canvas');c.width=W;c.height=H;c.getContext('2d').putImageData(new ImageData(diff,W,H),0,0);
     return{a,b,frame:A.frame,firstRGBA_SHA256:A.rgbaSHA,repeatRGBA_SHA256:B.rgbaSHA,exactRGBA:A.rgbaSHA===B.rgbaSHA,stats,diffPNG:c.toDataURL('image/png').split(',')[1]};
    },{a,b});
    const name=`CTX${ci+1}_${a}_${b}_ABS_RGB_X24.png`;fs.writeFileSync(path.join(out,name),Buffer.from(d.diffPNG,'base64'));delete d.diffPNG;report.comparisons.push({...d,context:ci+1,diffPNG:name});save();
   }
   await context.close();
  }
  verify('after');report.status=report.errors.length||report.missing.length||report.httpFailures.length||report.requestFailures.length?'COMPLETED_WITH_RUNTIME_ERRORS':'COMPLETED_FINITE_DIAGNOSTIC';report.allThreePairsRGBAExact=report.comparisons.length===3&&report.comparisons.every(x=>x.exactRGBA);save();console.log(JSON.stringify({status:report.status,draws:report.draws.length,allThreePairsRGBAExact:report.allThreePairsRGBAExact,report:path.join(out,'FINITE_CONTEXT_DIAGNOSTIC.json')}));
 }catch(e){report.status='ERROR';report.errors.push(String(e.stack||e));save();throw e;}
 finally{if(browser)await browser.close();if(server?.listening)await new Promise(ok=>server.close(ok));}
})().catch(e=>{console.error(e.message);process.exitCode=1});
