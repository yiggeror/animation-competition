// One complete natural body094/098, original articulated crane, finite shafts.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_drawn.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
import {renderFrame as naturalAfter102} from '../natural102_actual_20261020/s12_natural102_candidate.js';
export const DURATION=8,FPS=24;
const BASE='/collab/reviews/cloud_s12_20261018/natural_pre102_actual_20261020/sources/',OLD='/assets/chars/g12/';
let init,mapping,person,shadow,front,active;const states=new Map();
export async function getSequenceInfo(){await(init||=(async()=>{
 const [m,q,native]=await Promise.all([fetch(BASE+'CONSUMER_MAPPING.json').then(r=>r.json()),fetch(OLD+'sequence.json').then(r=>r.json()),loadImg(BASE+'F094_101_COMPLETE_CHARACTER.png')]);mapping=m;
 if(native.width!==1672||native.height!==941||!m.same_character_for_094_and_098)throw Error('Expected one complete native094/098 character');
 person=new OffscreenCanvas(1920,1080);const px=person.getContext('2d');px.imageSmoothingQuality='high';px.setTransform(...m.character_to_scene);px.drawImage(native,0,0);
 [shadow,front]=await Promise.all([loadImg(OLD+q.contactShadow),loadImg(OLD+q.boxFront)]);const crane=makeCrane(1.35,'plain');
 for(const key of [94,98]){
  const row=q.states.find(s=>s.key===key),p=row.prop,source=m.frames[key],props=new OffscreenCanvas(1920,1080),x=props.getContext('2d');
  if(JSON.stringify(p.pose)!==JSON.stringify(source.original_prop_plan.code_pose))throw Error('Original crane pose mismatch '+key);
  if(Math.hypot(...p.root.map((v,i)=>v-source.original_prop_plan.root_scene[i]))>1e-6)throw Error('Original crane root mismatch '+key);
  x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,crane,p.pose,'r');x.resetTransform();
  const sol=solve(crane,p.pose);
  for(const role of ['R','L']){
   const r=source.rods[role],a=r.A,b=r.B,local=pointOn(crane,sol,role==='R'?'body':'neck3',role==='R'?[-75,6]:[10,0]),projected=[p.root[0]+p.matrix[0][0]*local[0]+p.matrix[0][1]*local[1],p.root[1]+p.matrix[1][0]*local[0]+p.matrix[1][1]*local[1]];
   if(Math.hypot(projected[0]-a[0],projected[1]-a[1])>1e-6)throw Error('Original hinge mismatch '+key+role);
   if(Math.abs(Math.hypot(...a.map((v,i)=>v-b[i]))-r.length)>1e-6)throw Error('Finite rod length mismatch '+key+role);
   x.lineCap='round';for(const [color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke()}
  }
  states.set(key,{key,props,background:await loadImg(OLD+row.background)});
 }
})());return{fps:24,totalFrames:192,availableIntervals:[[94,109]],status:'NATURAL_PRE102_TRUE_ADJACENCY_CANDIDATE',sourceCommit:'95ef8644959df81c7852b1ac2427e368ffecc1a9',states:[{key:'natural_pre102',start:94,end:101,oneCompleteBody:true,propStates:[94,98]},{key:'natural102',start:102,end:105},{key:'same_natural106',start:106,end:109}],entry:'090–093 must be reused from final hair/skin video, never omitted in delivered clip.',mapping:'Whole native character_to_scene once, then original whole-scene camera; no old275/112/.7.',colour:'No grading of existing source or scene;090 from exact final colour video,102/106 through previous successful natural adapter.',paper:'Original makeCrane1.35/drawPuppet with matching original pose/root; provided reference PNGs not consumed.'};}
const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,layers:async()=>[{img:shadow,x:0,y:0,sc:1},{img:active.props,x:0,y:0,sc:1},{img:person,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}]};
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<94||f>109)throw RangeError('090–093 comes from actual final film, only094–109 rendered');if(f>=102)return naturalAfter102(ctx,t,w,h);await getSequenceInfo();active=states.get(f<98?94:98);shot.bg=active.background;return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||94/24,w,h);}
