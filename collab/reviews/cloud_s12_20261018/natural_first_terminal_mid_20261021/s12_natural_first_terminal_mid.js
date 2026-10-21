// Phase-selection FIRST-to-terminal intermediate whole pose. Keep exposure selection external.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_drawn.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
export const DURATION=8,FPS=24;
const BASE='/assets/chars/g12/',PATCH='/collab/reviews/cloud_s12_20261018/natural_first_terminal_mid_20261021/';const cache=new Map();
async function prepare(key){if(!cache.has(key))cache.set(key,(async()=>{
 const m=await fetch(PATCH+'CONSUMER_MAPPING.json').then(r=>r.json());const q=await fetch(BASE+'sequence.json').then(r=>r.json()),row=q.states.find(r=>r.key===74),p=m.states[String(key)].original_prop,b=row.registration||q.registration;
 const [shadow,bg,fg,front,stage]=await Promise.all([loadImg(BASE+q.contactShadow),loadImg(PATCH+'FIRST_TERMINAL_MID_COMPLETE_CHARACTER.png'),Promise.resolve(null),loadImg(BASE+q.boxFront),loadImg(BASE+row.background)]);if([shadow,bg,front,stage].some(x=>!x))throw Error('Missing first-lift source');
 // Original character registration is irrelevant: complete replacement RGBA is already scene-registered.
 if(!m.states[String(key)]?.rods)throw Error('Missing explicit finite apparatus mapping');
 const crane=makeCrane(1.35,'plain'),sol=solve(crane,p.pose),r=new OffscreenCanvas(1920,1080),x=r.getContext('2d');
 x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,crane,p.pose,'r');x.resetTransform();
 const local={R:pointOn(crane,sol,'body',[-75,6]),L:pointOn(crane,sol,'neck3',[10,0])};
 for(const role of ['R','L']){const spec=m.states[String(key)].rods[role],a=spec.B.slice(0,2),q=local[role],b=[p.root[0]+p.matrix[0][0]*q[0]+p.matrix[0][1]*q[1],p.root[1]+p.matrix[1][0]*q[0]+p.matrix[1][1]*q[1]];if(Math.hypot(b[0]-spec.A[0],b[1]-spec.A[1])>1e-6||Math.abs(Math.hypot(...spec.A.map((v,i)=>v-spec.B[i]))-spec.length)>1e-6)throw Error('Finite original hinge/length mismatch');x.lineCap='round';for(const[color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(...a);x.lineTo(...b);x.stroke()}}
 const layers=[{img:shadow,x:0,y:0,sc:1},{img:r,x:0,y:0,sc:1},{img:bg,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}];return {layers,background:stage};
})());return cache.get(key);}
export async function getSequenceInfo(){for(const k of [76])await prepare(k);return {fps:24,totalFrames:192,scope:'phase selection only; selector76 are apparatus states, not exposure commitment',selectors:[76]};}
export async function renderPhase(ctx,t,w,h,sourceKey){if(![76].includes(sourceKey))throw RangeError('Choose original apparatus76');const active=await prepare(sourceKey);const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,bg:active.background,layers:async()=>active.layers};return renderPaint(ctx,t,w,h,shot);}
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<74||f>=80)throw RangeError('Diagnostic74-79 only; exposure externally editable');return renderPhase(ctx,t,w,h,76);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||76/24,w,h);}
