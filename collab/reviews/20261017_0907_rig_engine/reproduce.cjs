const fs=require('fs'),http=require('http'),path=require('path'),crypto=require('crypto');
const {chromium}=require('playwright');
const root=__dirname;
const server=http.createServer((req,res)=>{
 const p=new URL(req.url,'http://localhost').pathname;
 if(p==='/'){res.setHeader('content-type','text/html');return res.end('<!doctype html><title>warp engine minimal reproduction</title><body>Minimal synthetic canvases only</body>');}
 if(p==='/warp.js'){res.setHeader('content-type','text/javascript');return res.end(fs.readFileSync(path.join(root,'source/warp.js')));}
 res.writeHead(404);res.end();
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 let browser;
 try{
  browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page=await browser.newPage(),consoleLog=[],pageErrors=[];
  page.on('console',m=>consoleLog.push({type:m.type(),text:m.text()}));page.on('pageerror',e=>pageErrors.push(e.message));
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  const result=await page.evaluate(async()=>{
   const contexts=[];const originalGet=OffscreenCanvas.prototype.getContext;
   OffscreenCanvas.prototype.getContext=function(type,...args){const ctx=originalGet.call(this,type,...args);if(type==='webgl2'&&ctx&&!contexts.some(x=>x.gl===ctx))contexts.push({gl:ctx,id:contexts.length+1,w:this.width,h:this.height});return ctx;};
   const {bind,render,boneMatrices}=await import('/warp.js');
   const canvas=(w,h)=>new OffscreenCanvas(w,h);
   function image(w,h){const c=canvas(w,h),x=c.getContext('2d');x.fillStyle='#1475ce';x.fillRect(w*.25,h*.25,w*.5,h*.5);x.fillStyle='#e82124';x.fillRect(w*.5,h*.4,w*.15,h*.2);return c;}
   const rig=(w,h,pins=[])=>({bones:[{name:'root',parent:null,head:[w/2,h/2],tail:[w*.75,h/2]}],layers:[],pins});
   const outputs={};
   async function capture(name,B,pose={}){
    const out=render(B,pose),g=contexts[contexts.length-1],errors=[];for(let k=0;k<8;k++){const e=g.gl.getError();if(!e)break;errors.push({decimal:e,hex:'0x'+e.toString(16)});}
    const pixels=out.getContext('2d').getImageData(0,0,out.width,out.height).data;
    let nontransparent=0,redCount=0,redX=0,redY=0;
    for(let i=0;i<pixels.length;i+=4){if(pixels[i+3])nontransparent++;if(pixels[i]>180&&pixels[i+1]<100&&pixels[i+2]<100&&pixels[i+3]>128){redCount++;redX+=(i/4)%out.width;redY+=Math.floor((i/4)/out.width);}}
    const blob=await out.convertToBlob({type:'image/png'}),buf=new Uint8Array(await blob.arrayBuffer());let s='';for(const v of buf)s+=String.fromCharCode(v);
    const info={name,size:[out.width,out.height],contextId:g.id,errors,nontransparentPixels:nontransparent,redPixels:redCount,redCentroid:redCount?[redX/redCount,redY/redCount]:null,pngBase64:btoa(s),pixelAtPin:Array.from(pixels.slice((64*out.width+96)*4,(64*out.width+96)*4+4))};outputs[name]=info;return info;
   }
   const pinImg=canvas(128,128),px=pinImg.getContext('2d');px.fillStyle='#1475ce';px.fillRect(32,48,80,32);px.fillStyle='#e82124';px.fillRect(92,60,8,8);
   const pinRig=rig(128,128,[[96,64]]),pinBound=bind(pinImg,pinRig,{step:8}),noPinBound=bind(pinImg,rig(128,128),{step:8});
   await capture('pin_rest',pinBound);await capture('pin_rot90',pinBound,{root:{rot:Math.PI/2}});await capture('no_pin_rot90',noPinBound,{root:{rot:Math.PI/2}});
   const L=pinBound.layers[0],v=Array.from(L.rest).findIndex((q,k)=>k%2===0&&q===96&&L.rest[k+1]===64)/2;
   const matrices=boneMatrices(pinBound,{root:{rot:Math.PI/2}}),deformed=[0,0];
   for(let k=0;k<4;k++){const j=v*4+k,m=matrices[L.i[j]],w=L.w[j];deformed[0]+=w*(m[0]*96+m[2]*64+m[4]);deformed[1]+=w*(m[1]*96+m[3]*64+m[5]);}
   const bindArraysEqual=['rest','w','i','tris'].every(k=>JSON.stringify(Array.from(pinBound.layers[0][k]))===JSON.stringify(Array.from(noPinBound.layers[0][k])));
   const Aimage=image(96,64),Bimage=image(64,96),A=bind(Aimage,rig(96,64),{step:8}),B=bind(Bimage,rig(64,96),{step:8});
   await capture('size_A_first',A);await capture('size_B',B);await capture('size_A_again',A);
   const freshA=bind(Aimage,rig(96,64),{step:8});await capture('size_A_fresh_bind_control',freshA);await capture('size_A_repeat_control',freshA);
   const g=contexts[0].gl,ext=g.getExtension('WEBGL_debug_renderer_info');
   return {outputs,pin:{point:[96,64],vertexIndex:v,weights:Array.from(L.w.slice(v*4,v*4+4)),indices:Array.from(L.i.slice(v*4,v*4+4)),deformed,displacement:Math.hypot(deformed[0]-96,deformed[1]-64),bindArraysEqual},contexts:contexts.map(c=>({id:c.id,width:c.w,height:c.h})),gpu:{version:g.getParameter(g.VERSION),renderer:ext?g.getParameter(ext.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER)},userAgent:navigator.userAgent};
  });
  for(const [name,item]of Object.entries(result.outputs)){const png=Buffer.from(item.pngBase64,'base64');delete item.pngBase64;item.pngSHA256=crypto.createHash('sha256').update(png).digest('hex');fs.writeFileSync(path.join(root,'evidence',name+'.png'),png);}
  result.consoleLog=consoleLog;result.pageErrors=pageErrors;result.browserVersion=browser.version();result.sourceSHA256=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'source/warp.js'))).digest('hex');
  result.comparisons={pinVsNoPinPNGIdentical:result.outputs.pin_rot90.pngSHA256===result.outputs.no_pin_rot90.pngSHA256,AFirstVsAAgainPNGIdentical:result.outputs.size_A_first.pngSHA256===result.outputs.size_A_again.pngSHA256,AFirstVsFreshBindPNGIdentical:result.outputs.size_A_first.pngSHA256===result.outputs.size_A_fresh_bind_control.pngSHA256,freshVsRepeatPNGIdentical:result.outputs.size_A_fresh_bind_control.pngSHA256===result.outputs.size_A_repeat_control.pngSHA256};
  fs.writeFileSync(path.join(root,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
