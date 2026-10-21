// Natural102 body retained at true110/132 apparatus, no old narrow-body tail.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_drawn.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
export const DURATION=8,FPS=24;
const BASE='/collab/reviews/cloud_s12_20261018/consistent_early_chain_20261021/',OLD='/assets/chars/g12/';
let init,shadow,front,active;const people={};const states=new Map();
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
 const [m,q]=await Promise.all([fetch(BASE+'CONSUMER_MAPPING.json').then(r=>r.json()),fetch(OLD+'sequence.json').then(r=>r.json())]);
 for(const [k,b] of Object.entries(m.bodies)){people[k]=await loadImg(b.url);if(people[k].width!==1920||people[k].height!==1080)throw Error('Baked scene alpha must be1920x1080');}
 [shadow,front]=await Promise.all([loadImg(OLD+q.contactShadow),loadImg(OLD+q.boxFront)]);const crane=makeCrane(1.35,'plain');
 for(const key of [78,82,86,90]){
  const row=q.states.find(s=>s.key===key),p=row.prop,canvas=new OffscreenCanvas(1920,1080),x=canvas.getContext('2d'),trans=new OffscreenCanvas(1920,1080),tx=trans.getContext('2d'),hinges={},free={};
  const specification=m.states[String(key)].original_prop;
  if(JSON.stringify(p.pose)!==JSON.stringify(specification.pose)||Math.hypot(...p.root.map((v,i)=>v-specification.root[i]))>1e-6)throw Error('Original85degree crane pose mismatch '+key);
  for(const [cx,mode]of[[x,'r'],[tx,'t']]){cx.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(cx,crane,p.pose,mode);cx.resetTransform()}
  const sol=solve(crane,p.pose);
  for(const role of ['R','L']){
   const r=m.states[String(key)].rods[role],a=r.A,b=r.B,local=pointOn(crane,sol,role==='R'?'body':'neck3',role==='R'?[-75,6]:[10,0]),projected=[p.root[0]+p.matrix[0][0]*local[0]+p.matrix[0][1]*local[1],p.root[1]+p.matrix[1][0]*local[0]+p.matrix[1][1]*local[1]];
   if(Math.hypot(projected[0]-a[0],projected[1]-a[1])>1e-6||Math.abs(Math.hypot(...a.map((v,i)=>v-b[i]))-r.length)>1e-6)throw Error('Original hinge / finite length mismatch '+key+role);
   hinges[role]=a.slice(0,2);free[role]=b.slice(0,2);x.lineCap='round';for(const [color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke()}
  }
  const props={r:canvas,trans,hinges,free};states.set(key,{key,props,row,person:people[m.states[String(key)].body],base:await loadImg(OLD+row.background)});
 }
})());return{fps:24,totalFrames:192,status:'TWO_EARLY_BODIES_CANDIDATE_NOT_CHAIN_ADOPTED',availableIntervals:[[78,93]],body:'two whole similarities already baked; runtime identity',scope:'Original apparatus78/82/86/90 selectors; exposure adjustable, two poses do not guarantee continuous rising to095.'};}

const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,layers:async()=>[{img:shadow,x:0,y:0,sc:1},{img:active.props.r,x:0,y:0,sc:1},{img:active.person,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}]};
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<78||f>93)throw RangeError('Only source7893 apparatus selector; not final exposure');await getSequenceInfo();active=states.get(f<82?78:f<86?82:f<90?86:90);shot.bg=active.base;return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||78/24,w,h);}
