const fs=require('fs');
const {chromium}=require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir='/tmp/laidian-s18-pilot-audit/compositor';
const read=p=>fs.readFileSync(dir+'/'+p,'utf8');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await b.newPage();
 const r=await page.evaluate(async ({oldSrc,newSrc,shotSrc})=>{
  const imp=s=>import('data:text/javascript;base64,'+btoa(unescape(encodeURIComponent(s))));
  const old=await imp(oldSrc), patched=await imp(newSrc);
  const canvas=(w,h,col)=>{const c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.fillStyle=col;x.fillRect(0,0,w,h);return c;};
  const alb=canvas(160,100,'#c78143');let spec,smallMap=false;
  globalThis.createImageBitmap=async im=>im;
  globalThis.fetch=async u=>u.endsWith('.json')?{ok:true,json:async()=>spec}:{ok:u.endsWith('a.png')||(smallMap&&u.endsWith('_n.png')),status:404,blob:async()=>u.endsWith('_n.png')?canvas(8,8,'#8080ff'):alb};
  const valid=()=>({canvas:[100,80],referenceAnchors:[[20,20],[50,20]],frames:[{file:'a',anchors:[[70,10],[70,25]]}],timeline:[[0,0]]});
  const apply=(M,[x,y])=>[M[0]*x+M[2]*y+M[4],M[1]*x+M[3]*y+M[5]];
  spec=valid();const before=await old.loadFlip('x'),after=await patched.loadFlip('x');
  const alignment={before:{canvas:[before.W,before.H],anchors:spec.frames[0].anchors.map(p=>apply(before.frames[0].M,p))},after:{canvas:[after.W,after.H],anchors:spec.frames[0].anchors.map(p=>apply(after.frames[0].M,p))}};
  const drawn=patched.flipMaps(after,0);alignment.after.pixel=Array.from(drawn.alb.getContext('2d').getImageData(25,25,1,1).data);
  const cases={missingTarget:s=>{delete s.referenceAnchors},missingCanvas:s=>{delete s.canvas},degenerate:s=>{s.frames[0].anchors=[[1,1],[1,1]]},badIndex:s=>{s.timeline=[[0,1]]},unsorted:s=>{s.timeline=[[0,0],[1,0],[.5,0]]},nonzeroStart:s=>{s.timeline=[[.1,0]]}};
  const rejected={};for(const [k,mut]of Object.entries(cases)){spec=valid();mut(spec);try{await patched.loadFlip(k);rejected[k]=false}catch(e){rejected[k]=String(e)}}
  spec=valid();smallMap=true;try{await patched.loadFlip('mapSize');rejected.mapSize=false}catch(e){rejected.mapSize=String(e)}smallMap=false;
  spec=valid();const G=await patched.loadFlip('valid');const ids=Array.from({length:72},(_,n)=>patched.frameAt(G,n/24));
  const unwrapped=shotSrc.replace(/^import .*;\n/gm,'').replace(/export /g,'');
  const create=new Function('loadFlip','makeShot',unwrapped+'\nreturn {flip,setFlipReviewRequired};');
  let calls=0;const shot=create(async()=>{calls++;throw new Error('fixture missing keyframe')},()=>({render(){},renderFrame(){}}));
  const legacy=await shot.flip();shot.setFlipReviewRequired();let strict=null;try{await shot.flip()}catch(e){strict={message:e.message,cause:e.cause?.message}};
  return {alignment,rejected,valid72:{count:ids.length,allExpectedKey:ids.every(x=>x===0)},strict:{legacy,calls,error:strict},scope:'Frozen module browser probes with synthetic source; not a final character film'};
 },{oldSrc:read('source/js/rig/flipbook.js'),newSrc:read('patch_candidate/js/rig/flipbook.js'),shotSrc:read('patch_candidate/js/lamp/shots/s18.js')});
 fs.writeFileSync(dir+'/patch_probe_results.json',JSON.stringify(r,null,2));console.log(JSON.stringify(r,null,2));await b.close();
 if(Object.values(r.rejected).some(x=>!x)||!r.strict.error||r.alignment.after.canvas.join()!=[100,80].join())process.exit(1);
})();
