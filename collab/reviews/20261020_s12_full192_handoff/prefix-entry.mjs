/** Limited assembly candidate. No default legacy renderer, no guessed exposure or geometry. */
export function createPrefixSelector(manifest) {
 if(manifest.fps!==24 || manifest.frame_count!==192) throw Error('S12 clock mismatch');
 return frame=>{
  if(!Number.isInteger(frame))throw Error('Integer shot-local frame required');
  if(frame<0||frame>105)return null;
  const entry=manifest.frames[frame];
  if(!entry?.state||!entry.sha256||!entry.native_path)throw Error(`Unresolved approved exposure ${frame}`);
  return entry;
 };
}
export function assertCompletePrefix(manifest){const select=createPrefixSelector(manifest);for(let f=0;f<=105;f++)select(f);}
export function createUnifiedEntry({manifest,preparePrefix,tailBridge,renderPaint,styleShot,front,drawTailBackground,tailShadowLayer}){
 // Cannot enable a partly reconciled manifest. All approved states must have real providers.
 assertCompletePrefix(manifest);
 for(const f of [preparePrefix,renderPaint,front,drawTailBackground])if(typeof f!=='function')throw Error('Missing production dependency');
 if(typeof tailBridge?.prepare!=='function')throw Error('Missing physical tail bridge');
 const select=createPrefixSelector(manifest);
 return {async renderFrame(ctx,t,w,h){
  if(!Number.isFinite(t))throw RangeError('Invalid time');
  const frame=Math.floor(t*24+1e-9);if(frame<0||frame>=192)throw RangeError('Outside S12');
  let background,layers;
  if(frame<106){
   const entry=select(frame),p=await preparePrefix(frame,entry);
   if(p?.nativeSHA256!==entry.sha256)throw Error(`Unverified prefix asset ${frame}`);
   if(p.transmitted!==false||!p.background||!p.shadowLayer||!p.BG||!p.FG||typeof p.drawOriginalPhysicalProps!=='function')throw Error(`Missing approved prefix context/physical geometry ${frame}`);
   for(const img of [p.BG,p.FG])if(img.width!==1024||img.height!==1536)throw Error('Prefix native size mismatch');
   const c=new OffscreenCanvas(1920,1080),x=c.getContext('2d');
   const r=p.drawOriginalPhysicalProps(x);if(r?.then)throw Error('Physical props must be synchronous');
   background=p.background;
   layers=[p.shadowLayer,{img:p.BG,x:275,y:112,sc:.7},{img:c,x:0,y:0,sc:1},{img:p.FG,x:275,y:112,sc:.7},{img:front(),x:0,y:0,sc:1}];
  }else{
   const p=await tailBridge.prepare(frame);
   if(!p||p.A?.rise!==(frame<110?0:1))throw Error('Tail optical onset must be110');
   for(const img of [p.BG,p.FG])if(img?.width!==1920||img?.height!==1080)throw Error('Tail scene size mismatch');
   // This callback is the unchanged production optical backend, not a new projection.
   background=await drawTailBackground(t,p);
   const c=new OffscreenCanvas(1920,1080),x=c.getContext('2d');x.drawImage(p.BG,0,0);
   const r=p.drawSurface(x);if(r?.then)throw Error('Tail props must be synchronous');x.drawImage(p.FG,0,0);
   if(!tailShadowLayer)throw Error('Missing inherited approved tail contact shadow');
   layers=[tailShadowLayer,{img:c,x:0,y:0,sc:1},{img:front(),x:0,y:0,sc:1}];
  }
  // Per-render object avoids mutating the shared source shot.
  return renderPaint(ctx,t,w,h,{...styleShot,size:[1920,1080],bg:background,layers:async()=>layers});
 }};
}
