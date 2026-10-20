import {createEarlyPhysicalRenderers} from './early-physical.mjs';
/** Paths are verified local provenance, not deployment URLs. Caller supplies authorized materializers. */
export function createResourceProvider({registry,loadVerifiedImage,loadJSON,makeCrane,solve,pointOn,drawPuppet,contexts}){
 const early=createEarlyPhysicalRenderers({drawPuppet}),cache=new Map();
 return async function preparePrefix(frame,entry){
  const key=entry.state,r=registry.states[key];if(!r||r.files.native.sha256!==entry.sha256)throw Error('State/hash binding mismatch '+key);
  const context=typeof contexts==='function'?await contexts(key):contexts[key];
  if(!context?.background||!context?.shadowLayer)throw Error('Missing approved background/contact shadow '+key);
  const binding=r.physical_provider;if(typeof binding!=='object')throw Error('Missing original physical provider '+key);
  if(!cache.has(key))cache.set(key,(async()=>{
   // Materializer MUST verify SHA before decoding. All records contain exact checked hashes.
   await loadVerifiedImage(r.files.native);
   let BG,FG;
   if(r.files.BG&&r.files.FG){BG=await loadVerifiedImage(r.files.BG);FG=await loadVerifiedImage(r.files.FG);}
   else if([0,12,18,22].includes(Number(key.slice(1)))){BG=await loadVerifiedImage(r.files.native);FG=new OffscreenCanvas(1024,1536);}
   else throw Error('Missing actual ownership layers '+key);
   let draw;
   if(binding.type.startsWith('EXACT_ORIGINAL_FUNCTION')){
    const sourceKey=binding.key??key,desc=registry.states[sourceKey].physical_provider;
    const geometry=await loadJSON(desc.geometry),data={A:geometry.states[desc.state_index],crane:makeCrane(1.35,'plain')};
    if(!early[sourceKey])throw Error('Missing exact original function '+sourceKey);
    draw=ctx=>ctx.drawImage(early[sourceKey](data).img,0,0);
   }else if(binding.type==='ORIGINAL_PHYSICAL_PLAN'){
    const p=await loadJSON(binding.path),pup=makeCrane(p.actual_makeCrane_scale,'plain'),solution=solve(pup,p.code_pose),b=p.paper_3D_camera_basis,k=p.mm_to_scene_scale;
    const m=[k*b[0][0],k*b[1][0],k*b[0][1],k*b[1][1],...p.root_scene];
    for(const hand of ['R','L']){const q=pointOn(pup,solution,hand==='R'?'body':'neck3',hand==='R'?[-75,6]:[10,0]),r=p.rods[hand];const h=[m[0]*q[0]+m[2]*q[1]+m[4],m[1]*q[0]+m[3]*q[1]+m[5]];if(Math.hypot(...h.map((v,i)=>v-r.hinge_scene[i]))>1e-6)throw Error('Physical hinge mismatch '+key);}
    draw=ctx=>{ctx.save();try{ctx.transform(...m);drawPuppet(ctx,pup,p.code_pose,'r')}finally{ctx.restore()}ctx.save();try{ctx.lineCap='round';for(const hand of ['R','L'])for(const [color,width]of [['#3e2a1e',7],['#c99a52',3]]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(...p.rods[hand].free_scene);ctx.lineTo(...p.rods[hand].hinge_scene);ctx.stroke()}}finally{ctx.restore()}};
   }else throw Error('Unsupported physical provider '+key);
   return{nativeSHA256:entry.sha256,transmitted:false,BG,FG,drawOriginalPhysicalProps:draw,...context};
  })());return cache.get(key);
 };
}
