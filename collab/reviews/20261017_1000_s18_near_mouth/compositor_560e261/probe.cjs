const fs=require('fs');
const {chromium}=require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir='/tmp/laidian-s18-pilot-audit/compositor_560e261';
const src=fs.readFileSync(dir+'/source/js/rig/flipbook.js','utf8');
const manifest=JSON.parse(fs.readFileSync(dir+'/source_manifest.json'));
const plan=JSON.parse(fs.readFileSync(dir+'/source/docs/keyframes/S18.json'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});const page=await browser.newPage();
 const results=await page.evaluate(async({src,inputs,plan})=>{
  const mod=await import('data:text/javascript;base64,'+btoa(unescape(encodeURIComponent(src))));
  const originalFetch=globalThis.fetch;const blobs={};for(const a of inputs)blobs[a.version]=await(await originalFetch('data:image/png;base64,'+a.b64)).blob();
  let spec,missingManifest=false;globalThis.fetch=async u=>{
   if(u.endsWith('.json'))return missingManifest?new Response('missing',{status:404}):new Response(JSON.stringify(spec));
   const name=u.split('/').pop().replace('.png','');return blobs[name]?new Response(blobs[name]):new Response('missing',{status:404});
  };
  const make=(a,points=a.feet_anchors,target=[[22,1142],[312,1142]])=>({target:{width:635,height:1175,anchors:target},fps:24,frames:[{file:a.version,anchors:points}],timelineFrames:[[0,0]]});
  const actual=[],normalized=[];
  for(const a of inputs){
   const bitmap=await createImageBitmap(blobs[a.version]);const row={version:a.version,decoded:[bitmap.width,bitmap.height]};
   for(const [kind,points,target]of [['feet',a.feet_anchors,[[22,1142],[312,1142]]],['seat_right',a.seat_right_anchors,[[22,899],[312,1142]]]]){
    spec=make(a,points,target);try{await mod.loadFlip(a.version,{maps:false});row[kind]={accepted:true}}catch(e){row[kind]={accepted:false,error:e.message}}}
   actual.push(row);
   // One uniform resolution conversion; no local edits and no diagnostic PNG exported.
   const c=new OffscreenCanvas(635,1175),ctx=c.getContext('2d');const n=1/a.native_scale;ctx.setTransform(n,0,0,n,0,0);ctx.drawImage(bitmap,0,0);blobs[a.version+'_normalized']=await c.convertToBlob();
   spec=make({...a,version:a.version+'_normalized'},a.nominal_feet);const F=await mod.loadFlip('normalized',{maps:false});const maps=mod.flipMaps(F,0);
   normalized.push({version:a.version,uniformScale:n,output:[F.W,F.H],reg:F.frames[0].reg,matrix:F.frames[0].M,actualCanvas:[maps.alb.width,maps.alb.height]});
  }
  const a=inputs[0];const good=()=>make({...a,version:a.version+'_normalized'},a.nominal_feet);
  const malformed={};for(const [name,change]of Object.entries({flatTarget:s=>{s.target.anchors=[0,50]},flatFrame:s=>{s.frames[0].anchors=[0,50]},fractionalIndex:s=>{s.frames.push({...s.frames[0]});s.timelineFrames=[[0,.5]]}})){
   spec=good();change(spec);try{const F=await mod.loadFlip(name,{maps:false});const i=mod.frameAt(F,0);let drawError=null;try{mod.flipMaps(F,i)}catch(e){drawError=e.message}malformed[name]={accepted:true,key:i,matrixFinite:F.frames[0].M.every(Number.isFinite),drawError}}catch(e){malformed[name]={accepted:false,error:e.message}}}
  spec=good();spec.frames=Array.from({length:12},()=>({...spec.frames[0]}));spec.timelineFrames=plan.timelineFrames;const F=await mod.loadFlip('timing',{maps:false});const ids=Array.from({length:72},(_,n)=>mod.frameAt(F,n/24));const runs=[];ids.forEach((key,n)=>{const q=runs.at(-1);if(q&&q.key===key+1)q.end=n;else runs.push({key:key+1,start:n,end:n})});
  missingManifest=true;const optional=await mod.loadFlip('missing',{optional:true});let requiredError=null;try{await mod.loadFlip('missing')}catch(e){requiredError=e.message}
  return {scope:'Actual PNG decode/load; offscreen uniform-resolution diagnostic; no formal character sequence/film',actual,normalized,malformed,timing:{ids,runs,F14:ids[14]+1,F15:ids[15]+1,F16:ids[16]+1},missingManifest:{optional,requiredError}};
 },{src,plan,inputs:manifest.inputs.map(a=>({...a,b64:fs.readFileSync(a.path).toString('base64')}))});
 fs.writeFileSync(dir+'/probe_results.json',JSON.stringify(results,null,2));console.log(JSON.stringify({...results,timing:{...results.timing,ids:undefined}},null,2));await browser.close();
})();
