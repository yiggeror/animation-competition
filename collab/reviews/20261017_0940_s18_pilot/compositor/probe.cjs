const fs = require('fs');
const crypto = require('crypto');
const { chromium } = require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir = '/tmp/laidian-s18-pilot-audit/compositor';
const flipSource = fs.readFileSync(dir+'/source/js/rig/flipbook.js','utf8');
const shotSource = fs.readFileSync(dir+'/source/js/lamp/shots/s18.js','utf8');
const keys = JSON.parse(fs.readFileSync(dir+'/source/docs/keyframes/S18.json'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage();
 const result=await page.evaluate(async({flipSource,shotSource,keys})=>{
  const mod=await import('data:text/javascript;base64,'+btoa(unescape(encodeURIComponent(flipSource))));
  const cv=(w,h,color,rect=[20,20,30,40])=>{const c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.fillStyle=color;x.fillRect(...rect);return c;};
  let spec,images={};
  globalThis.fetch=async u=>u.endsWith('.json')?{ok:true,json:async()=>spec}:{ok:!!images[u],status:404,blob:async()=>images[u]};
  globalThis.createImageBitmap=async x=>x;
  const install=(frames,timeline)=>{spec={frames,ref:0,timeline};images={};for(let i=0;i<frames.length;i++)images['/assets/chars/'+frames[i].file+'.png']=cv(160,100,`rgb(${20+i*15},90,60)`);};
  const frames=keys.keys.map((k,i)=>({file:'k'+i,anchors:[[20,20],[50,20]]}));
  install(frames,keys.keys.map((k,i)=>[k.t,i]));
  const F=await mod.loadFlip('synthetic');
  const actual72=[];
  for(let n=0;n<72;n++){const key=mod.frameAt(F,n/24),m=mod.flipMaps(F,key),p=Array.from(m.alb.getContext('2d').getImageData(25,25,1,1).data);actual72.push({n,t:n/24,key:key+1,pixel:p});}
  const runs=[];for(const f of actual72){const last=runs.at(-1);if(last&&last.key===f.key)last.end=f.n;else runs.push({key:f.key,start:f.n,end:f.n});}for(const r of runs)r.count=r.end-r.start+1;
  const alpha = {};for(const ch of ['alb','nrm','mat']){const c=mod.flipMaps(F,0)[ch];alpha[ch]={inside:Array.from(c.getContext('2d').getImageData(25,25,1,1).data),outside:Array.from(c.getContext('2d').getImageData(0,0,1,1).data)};}
  install([{file:'ref',anchors:[[20,20],[50,20]]},{file:'shift',anchors:[[70,10],[70,25]]}],[[0,0],[1,1]]);
  const A=await mod.loadFlip('affine');const f=A.frames[1];const apply=([x,y])=>[f.M[0]*x+f.M[2]*y+f.M[4],f.M[1]*x+f.M[3]*y+f.M[5]];
  const affine={matrix:f.M,anchor_targets:f.anchors.map(apply),ref_matrix:A.frames[0].M};
  // A non-flat normal rotated with the image retains its encoded XY components.
  A.frames[1].nrm=cv(160,100,'rgb(218,128,218)',[0,0,160,100]);
  const nr=mod.flipMaps(A,1).nrm.getContext('2d').getImageData(25,25,1,1).data;
  affine.normal_after_minus90deg=Array.from(nr);
  // Missing maps are allowed, but a supplied map of the wrong size is not rejected.
  install([{file:'smallmap',anchors:[[20,20],[50,20]]}],[[0,0]]);
  images['/assets/chars/smallmap_n.png']=cv(8,8,'rgb(128,128,255)',[0,0,8,8]);
  const mismatch=await mod.loadFlip('mismatch');
  const mismap=mod.flipMaps(mismatch,0); const mismatched_maps={alb_at_25:Array.from(mismap.alb.getContext('2d').getImageData(25,25,1,1).data),nrm_at_25:Array.from(mismap.nrm.getContext('2d').getImageData(25,25,1,1).data)};
  install([{file:'zero',anchors:[[20,20],[20,20]]}],[[0,0]]);
  const Z=await mod.loadFlip('zero');let zeroError=null;try{mod.flipMaps(Z,0);}catch(e){zeroError=String(e)}
  const degenerate={matrix_finite:Z.frames[0].M.map(Number.isFinite),draw_error:zeroError};
  // Exercise the exact S18 catch/cache function, with only its imported dependencies stubbed.
  const noImports=shotSource.replace(/^import .*;\n/gm,'').replace(/export /g,'');
  let loadCount=0;const makeShot=()=>({render:()=>{},renderFrame:()=>{}});
  const expose=new Function('loadFlip','makeShot','sheet17','cards06','billboardM','XM','RIG16','loadRig','layers16','pose16','frameAt','flipMaps',noImports+'\nreturn {flip,cards};');
  const shot=expose(async()=>{loadCount++;throw new Error('fixture: corrupt or missing frame')},makeShot,()=>{},()=>{},()=>{}, {}, {},()=>{},()=>{},()=>{},()=>{},()=>{});
  const ret1=await shot.flip(),ret2=await shot.flip();
  return {scope:'Synthetic browser canvas probe of frozen modules; no generated character sequence or lit final film',actual72,runs,alpha,affine,mismatched_maps,degenerate,fallback:{loadCount,ret1,ret2}};
 },{flipSource,shotSource,keys});
 fs.writeFileSync(dir+'/probe_results.json',JSON.stringify(result,null,2));
 console.log(JSON.stringify({runs:result.runs,alpha:result.alpha,affine:result.affine,mismatched_maps:result.mismatched_maps,degenerate:result.degenerate,fallback:result.fallback},null,2));
 await browser.close();
})();
