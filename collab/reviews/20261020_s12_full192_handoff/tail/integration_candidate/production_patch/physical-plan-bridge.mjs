import {createTailSelector,loadTailLayers} from '../tail-adapter.mjs';
/** Production dependencies must be the existing js/lamp/crane.js and js/puppet.js exports.
 * No diagnostic raster or alternate Canvas material is imported here. */
export async function createPhysicalPlanBridge({manifest,loadImage,loadJSON,assetBase,makeCrane,solve,pointOn,drawPuppet}) {
 const select=createTailSelector(manifest),assets=await loadTailLayers(manifest,loadImage,assetBase);
 const prepared=new Map();
 for(const folder of new Set(manifest.timeline.map(e=>e.folder))){
  const p=await loadJSON(`${assetBase.replace(/\/$/,'')}/${folder}/prop_plan.json`);
  const pup=makeCrane(p.actual_makeCrane_scale,'plain'),sol=solve(pup,p.code_pose),b=p.paper_3D_camera_basis,k=p.mm_to_scene_scale,root=p.root_scene;
  if(!Number.isFinite(k)||!b?.flat().every(Number.isFinite)||!root?.every(Number.isFinite))throw Error(`Invalid physical plan ${folder}`);
  const matrix=[k*b[0][0],k*b[1][0],k*b[0][1],k*b[1][1],...root];
  const rods=[];
  for(const key of ['R','L']){
   const r=p.rods[key],q=pointOn(pup,sol,key==='R'?'body':'neck3',key==='R'?[-75,6]:[10,0]);
   const hinge=[root[0]+k*(b[0][0]*q[0]+b[0][1]*q[1]),root[1]+k*(b[1][0]*q[0]+b[1][1]*q[1])];
   if(Math.hypot(...hinge.map((v,i)=>v-r.hinge_scene[i]))>1e-6)throw Error(`Production rig hinge mismatch ${folder}/${key}`);
   const length=Math.hypot(...r.hinge_camera3D_scene_units.map((v,i)=>v-r.free_camera3D_scene_units[i]));
   if(Math.abs(length-r.physical_length_scene_units)>1e-6)throw Error(`Physical rod length mismatch ${folder}/${key}`);
   rods.push([r.free_scene.slice(),r.hinge_scene.slice()]);
  }
  const drawCrane=(ctx,mode)=>{ctx.save();try{ctx.transform(...matrix);drawPuppet(ctx,pup,p.code_pose,mode)}finally{ctx.restore()}};
  prepared.set(folder,Object.freeze({...assets.get(folder),A:Object.freeze({rise:folder==='F106'?0:1,sway:0}),R:Object.freeze({root:root.slice(),rods}),matrix,
   drawTransmitted(ctx){drawCrane(ctx,'t')},
   drawSurface(ctx){
    drawCrane(ctx,'r');
    // Existing approved S12 native-geometry scene rod style (F052 drawRig):7/3 scene px.
    ctx.save();try{ctx.lineCap='round';for(const [a,z]of rods){for(const [color,width]of [['#3e2a1e',7],['#c99a52',3]]){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...z);ctx.stroke()}}}finally{ctx.restore()}
   }
  }));
 }
 return Object.freeze({prepare(frame){const s=select('S12',frame);return s?prepared.get(s.folder):null}});
}
