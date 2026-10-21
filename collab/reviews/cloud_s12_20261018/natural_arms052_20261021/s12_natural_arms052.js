import {receiverProjectionBackground} from '/task/s12_receiver_geometry.js';
// Natural full-shoulder-chain source52. No later closed-grip/raising hold.
import {renderPaint,loadImg} from '../../../../js/paint/paintshot.js';
import {shot as originalShot} from '../../../../js/anim/s12_early_retained_current140.js';
import {makeCrane} from '../../../../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../../../../js/puppet.js';
export const DURATION=8,FPS=24;
const BASE='/assets/chars/g12/',PATCH='/collab/reviews/cloud_s12_20261018/natural_arms052_20261021/';let init,layers,background,activeRow,receiverProps;
export async function getSequenceInfo(){await(init||=(async()=>{
 const q=await fetch(BASE+'sequence.json').then(r=>r.json()),row=q.states.find(r=>r.key===52),p=row.prop,b=row.registration||q.registration;
 const [shadow,bg,fg,front,stage]=await Promise.all([loadImg(BASE+q.contactShadow),loadImg(PATCH+'F052_NATURAL_COMPLETE.png'),Promise.resolve(null),loadImg(BASE+q.boxFront),loadImg(BASE+row.background)]);if([shadow,bg,front,stage].some(x=>!x))throw Error('Missing key52 source');
 if((row.transmission||0)!==0||b.x!==275||b.y!==112||b.scale!==.7)throw Error('Unexpected source registration or transmission');
 const crane=makeCrane(1.35,'plain'),sol=solve(crane,p.pose),r=new OffscreenCanvas(1920,1080),x=r.getContext('2d');
 x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,crane,p.pose,'r');x.resetTransform();
 const trans=new OffscreenCanvas(1920,1080),tx=trans.getContext('2d');tx.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(tx,crane,p.pose,'t');tx.resetTransform();const hinges={};
 const local={R:pointOn(crane,sol,'body',[-75,6]),L:pointOn(crane,sol,'neck3',[10,0])};
 for(const role of ['R','L']){const a=p.free[role],q=local[role],b=[p.root[0]+p.matrix[0][0]*q[0]+p.matrix[0][1]*q[1],p.root[1]+p.matrix[1][0]*q[0]+p.matrix[1][1]*q[1]];hinges[role]=b;x.lineCap='round';for(const[color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(...a);x.lineTo(...b);x.stroke()}}
 layers=[{img:shadow,x:0,y:0,sc:1},{img:r,x:0,y:0,sc:1},{img:bg,x:0,y:0,sc:1},{img:front,x:0,y:0,sc:1}];background=stage;activeRow=row;receiverProps={r,trans,hinges,free:p.free};
})());return{fps:24,totalFrames:192,scope:'key52 only source frames52-55, complete natural shoulder-arm chain repair; ownership/camera/light/apparatus unchanged'};}
const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,layers:async()=>layers};
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<52||f>=56)throw RangeError('Only key52 exposures52-55');await getSequenceInfo();shot.bg=receiverProjectionBackground(background,activeRow,receiverProps,originalShot.light(t));return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||52/24,w,h);}

// External exposure selection only; same original person/prop/light path.
export async function renderPhase(ctx,t,w,h){await getSequenceInfo();shot.bg=receiverProjectionBackground(background,activeRow,receiverProps,originalShot.light(t));return renderPaint(ctx,t,w,h,shot);}
