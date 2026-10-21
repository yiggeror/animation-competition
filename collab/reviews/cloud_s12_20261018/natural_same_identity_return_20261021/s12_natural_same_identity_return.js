import {receiverProjectionBackground} from '/task/s12_receiver_geometry.js';
// Phase-selection same identity lifted-hands candidate. Keep exposure selection external.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_early_retained_current140.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
export const DURATION=8,FPS=24;
const BASE='/assets/chars/g12/',PATCH='/collab/reviews/cloud_s12_20261018/natural_same_identity_return_20261021/';const cache=new Map();
async function prepare(key){if(!cache.has(key))cache.set(key,(async()=>{
 const m=await fetch(PATCH+'CONSUMER_MAPPING.json').then(r=>r.json());const q=await fetch(BASE+'sequence.json').then(r=>r.json()),row=q.states.find(r=>r.key===key),p=row.prop,b=row.registration||q.registration;
 const [shadow,bg,fg,front,stage]=await Promise.all([loadImg(BASE+q.contactShadow),loadImg(m.asset_reference),Promise.resolve(null),loadImg(BASE+q.boxFront),loadImg(BASE+row.background)]);if([shadow,bg,front,stage].some(x=>!x))throw Error('Missing first-lift source');
 // Original character registration is irrelevant: complete replacement RGBA is already scene-registered.
 if(!m.states[String(key)]?.rods)throw Error('Missing explicit finite apparatus mapping');
 const crane=makeCrane(1.35,'plain'),sol=solve(crane,p.pose),r=new OffscreenCanvas(1920,1080),x=r.getContext('2d');
 x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,crane,p.pose,'r');x.resetTransform();
 const trans=new OffscreenCanvas(1920,1080),tx=trans.getContext('2d');tx.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(tx,crane,p.pose,'t');tx.resetTransform();const hinges={},free={};
 const local={R:pointOn(crane,sol,'body',[-75,6]),L:pointOn(crane,sol,'neck3',[10,0])};
 for(const role of ['R','L']){const spec=m.states[String(key)].rods[role],a=spec.B.slice(0,2),q=local[role],b=[p.root[0]+p.matrix[0][0]*q[0]+p.matrix[0][1]*q[1],p.root[1]+p.matrix[1][0]*q[0]+p.matrix[1][1]*q[1]];if(Math.hypot(b[0]-spec.A[0],b[1]-spec.A[1])>1e-6||Math.abs(Math.hypot(...spec.A.map((v,i)=>v-spec.B[i]))-spec.length)>1e-6)throw Error('Finite original hinge/length mismatch');hinges[role]=b;free[role]=a;x.lineCap='round';for(const[color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(...a);x.lineTo(...b);x.stroke()}}
 const layers=[{img:shadow,x:0,y:0,sc:1},{img:r,x:0,y:0,sc:1},{img:bg,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}];return {layers,background:stage,row,props:{r,trans,hinges,free,rods3d:m.states[String(key)].rods}};
})());return cache.get(key);}
export async function getSequenceInfo(){for(const k of [126])await prepare(k);return {fps:24,totalFrames:192,scope:'phase selection only; selector126 are apparatus states, not exposure commitment',selectors:[126]};}
export async function renderPhase(ctx,t,w,h,sourceKey){if(![126].includes(sourceKey))throw RangeError('Choose original apparatus126');const active=await prepare(sourceKey);const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,bg:receiverProjectionBackground(active.background,active.row,active.props,originalShot.light(t)),layers:async()=>active.layers};return renderPaint(ctx,t,w,h,shot);}
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<126||f>=132)throw RangeError('Return diagnostic126-131 only; edit exposure through renderPhase');return renderPhase(ctx,t,w,h,126);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||126/24,w,h);}
