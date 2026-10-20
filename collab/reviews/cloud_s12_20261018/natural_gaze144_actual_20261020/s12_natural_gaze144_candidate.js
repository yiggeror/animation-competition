// Natural144 whole head-neck-collar gaze, unchanged complete lower body.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_drawn.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
export const DURATION=8,FPS=24;
const BASE='/collab/reviews/cloud_s12_20261018/natural_gaze144_actual_20261020/sources/',BODY=BASE+'F144_COMPLETE_CHARACTER.png',OLD='/assets/chars/g12/';
let init,person,shadow,front,active;const states=new Map();
// Same adopted original box-lid transmission. Only physical rod tails change
// with this new registered complete body; original optical transform retained.
function transmissionBackground(base,row,props,alpha=row.transmission||0){
 if(alpha<=0)return base;
 const out=new OffscreenCanvas(1920,1080),x=out.getContext('2d');x.drawImage(base,0,0);
 const lid=new Path2D();[[1020,760],[1840,760],[1825,450],[1035,450]].forEach((p,i)=>i?lid.lineTo(...p):lid.moveTo(...p));lid.closePath();x.save();x.clip(lid);
 const map=new OffscreenCanvas(1920,1080),mx=map.getContext('2d');mx.fillStyle='#fff';mx.fillRect(0,0,1920,1080);
 const root=row.prop.root;mx.save();mx.globalAlpha=alpha;mx.globalCompositeOperation='multiply';mx.filter='blur(6px)';mx.translate(root[0]+240,root[1]-70);mx.scale(1.4,1.4);mx.translate(-root[0],-root[1]);mx.drawImage(props.trans,0,0);
 mx.strokeStyle='rgba(70,45,30,0.7)';mx.lineWidth=9;for(const role of ['R','L']){mx.beginPath();mx.moveTo(...props.free[role]);mx.lineTo(...props.hinges[role]);mx.stroke();}mx.restore();x.globalCompositeOperation='multiply';x.drawImage(map,0,0);x.restore();return out;
}
export async function getSequenceInfo(){await(init||=(async()=>{
 const [m,q,native]=await Promise.all([fetch(BASE+'CONSUMER_MAPPING.json').then(r=>r.json()),fetch(OLD+'sequence.json').then(r=>r.json()),loadImg(BODY)]);
 if(native.width!==1672||native.height!==941)throw Error('Natural144 body size mismatch');person=new OffscreenCanvas(1920,1080);const px=person.getContext('2d');px.imageSmoothingQuality='high';px.setTransform(...m.character_to_scene);px.drawImage(native,0,0);
 [shadow,front]=await Promise.all([loadImg(OLD+q.contactShadow),loadImg(OLD+q.boxFront)]);const crane=makeCrane(1.35,'plain');
 for(const key of [144]){
  const row=q.states.find(s=>s.key===key),p=row.prop,canvas=new OffscreenCanvas(1920,1080),x=canvas.getContext('2d'),trans=new OffscreenCanvas(1920,1080),tx=trans.getContext('2d'),hinges={},free={};
  const specification=m.original_crane;
  if(JSON.stringify(p.pose)!==JSON.stringify(specification.code_pose)||Math.hypot(...p.root.map((v,i)=>v-specification.root_scene[i]))>1e-6)throw Error('Original85degree crane pose mismatch '+key);
  for(const [cx,mode]of[[x,'r'],[tx,'t']]){cx.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(cx,crane,p.pose,mode);cx.resetTransform()}
  const sol=solve(crane,p.pose);
  for(const role of ['R','L']){
   const r=m.rods[role],a=r.A,b=r.B,local=pointOn(crane,sol,role==='R'?'body':'neck3',role==='R'?[-75,6]:[10,0]),projected=[p.root[0]+p.matrix[0][0]*local[0]+p.matrix[0][1]*local[1],p.root[1]+p.matrix[1][0]*local[0]+p.matrix[1][1]*local[1]];
   if(Math.hypot(projected[0]-a[0],projected[1]-a[1])>1e-6||Math.abs(Math.hypot(...a.map((v,i)=>v-b[i]))-r.length)>1e-6)throw Error('Original hinge / finite length mismatch '+key+role);
   hinges[role]=a.slice(0,2);free[role]=b.slice(0,2);x.lineCap='round';for(const [color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke()}
  }
  const props={r:canvas,trans,hinges,free};states.set(key,{key,props,row,base:await loadImg(OLD+row.background)});
 }
})());return{fps:24,totalFrames:192,status:'NATURAL144_WHOLE_HEAD_NECK_GAZE_CANDIDATE',sourceCommit:'0cd01c023d91f7af8ffb5b667052196a318c241e',availableIntervals:[[144,191]],body:'Complete natural144 alpha1e4f; whole head-neck-collar gaze, same below332 natural body',paper:'Original144 root1240,550 and85degree crane, same110/132 finite rods and full physical tails',missing:[],review:'Actual full8s decides gaze and final pause; no old144 body loaded'};}
const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,layers:async()=>[{img:shadow,x:0,y:0,sc:1},{img:active.props.r,x:0,y:0,sc:1},{img:person,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}]};
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<144||f>191)throw RangeError('Only natural144 gaze and original144–191 response interval bound');await getSequenceInfo();active=states.get(144);shot.bg=transmissionBackground(active.base,active.row,active.props,1);return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||144/24,w,h);}
