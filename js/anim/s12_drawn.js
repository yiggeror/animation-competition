// S12 adopted drawings. Person/true prop remain fixed together during exposure.
// Assets and pose data live in production paths, with no review-module imports.
import {renderPaint,loadImg} from '../paint/paintshot.js';
import {makeCrane} from '../lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../puppet.js';
export const DURATION=8;
export const FPS=24;
const W=1920,H=1080,BASE='/assets/chars/g12/',LINE='#3e2a1e';
const smooth=(a,b,x)=>{const u=Math.max(0,Math.min(1,(x-a)/(b-a)));return u*u*(3-2*u);};
let sequencePromise,crane,currentProp,currentKey,active,baseBackground;
const images=new Map();
async function image(name){
 if(!name)return null;
 if(!images.has(name))images.set(name,(async()=>{const im=await loadImg(BASE+name);if(!im)throw Error('S12 missing production image: '+name);return im;})());
 return images.get(name);
}
export async function getSequenceInfo(){return sequencePromise ||= fetch(BASE+'sequence.json').then(async r=>{
 if(!r.ok)throw Error('Missing S12 sequence.json');const q=await r.json();
 // Scene-space ownership masks are already registered. Check every adopted tail
 // pair before rendering; missing masks cannot silently remove a gripping hand.
 for(const name of new Set(q.states.filter(s=>s.start>=106).flatMap(s=>[s.bg,s.fg]))){const im=await image(name);if(!im||im.width!==W||im.height!==H)throw Error('S12 invalid scene-space mask: '+name);}
 return q;
});}
export async function stateAtFrame(frame){
 const q=await getSequenceInfo(),row=q.states.find(s=>frame>=s.start&&frame<=s.end);
 if(!row)throw RangeError('S12 frame '+frame+' has no adopted drawing; tail must be supplied, not padded.');
 return row;
}
function propCanvases(row){
 if(currentKey===row.key)return currentProp;
 crane ||= makeCrane(1.35,'plain');
 const p=row.prop,sol=solve(crane,p.pose),local={R:pointOn(crane,sol,'body',[-75,6]),L:pointOn(crane,sol,'neck3',[10,0])};
 const project=q=>[p.root[0]+p.matrix[0][0]*q[0]+p.matrix[0][1]*q[1],p.root[1]+p.matrix[1][0]*q[0]+p.matrix[1][1]*q[1]];
 const hinges={R:project(local.R),L:project(local.L)},r=new OffscreenCanvas(W,H),x=r.getContext('2d');
 x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,crane,p.pose,'r');x.resetTransform();
 for(const role of ['R','L']){const a=p.free[role],b=hinges[role];x.lineCap='round';for(const [color,width]of[[LINE,7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(...a);x.lineTo(...b);x.stroke();}}
 const trans=new OffscreenCanvas(W,H),tx=trans.getContext('2d');
 tx.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(tx,crane,p.pose,'t');tx.resetTransform();
 currentKey=row.key;return currentProp={r,trans,hinges,free:p.free};
}
function transmissionBackground(base,row,props){
 const alpha=row.transmission||0;if(alpha<=0)return base;
 const out=new OffscreenCanvas(W,H),x=out.getContext('2d');x.drawImage(base,0,0);
 const lid=new Path2D();[[1020,760],[1840,760],[1825,450],[1035,450]].forEach((p,i)=>i?lid.lineTo(...p):lid.moveTo(...p));lid.closePath();
 x.save();x.clip(lid);
 const map=new OffscreenCanvas(W,H),mx=map.getContext('2d');mx.fillStyle='#fff';mx.fillRect(0,0,W,H);
 const root=row.prop.root;mx.save();mx.globalAlpha=alpha;mx.globalCompositeOperation='multiply';mx.filter='blur(6px)';
 mx.translate(root[0]+240,root[1]-70);mx.scale(1.4,1.4);mx.translate(-root[0],-root[1]);mx.drawImage(props.trans,0,0);
 mx.strokeStyle='rgba(70,45,30,0.7)';mx.lineWidth=9;for(const role of ['R','L']){mx.beginPath();mx.moveTo(...props.free[role]);mx.lineTo(...props.hinges[role]);mx.stroke();}mx.restore();
 x.globalCompositeOperation='multiply';x.drawImage(map,0,0);x.restore();return out;
}
export const shot={size:[W,H],layers:async()=>{
 const q=await getSequenceInfo(),b=active.registration||q.registration,props=propCanvases(active);
 const [shadow,bg,fg,front]=await Promise.all([image(q.contactShadow),image(active.bg),image(active.fg),image(q.boxFront)]);
 return [{img:shadow,x:0,y:0,sc:1},{img:bg,x:b.x,y:b.y,sc:b.scale},{img:props.r,x:0,y:0,sc:1},...(fg?[{img:fg,x:b.x,y:b.y,sc:b.scale}]:[]),{img:front,x:0,y:0,sc:1}];
},light:t=>{const f=1+.04*Math.sin(t*11)+.03*Math.sin(t*23);return {ambient:[.03,.026,.03],lights:[{x:-350,y:760,r:2700*f,color:[1,.64,.32],i:1.25,falloff:1.5},{x:1350,y:560,r:760,color:[1,.7,.42],i:.35*f,falloff:1.6}],exposure:1,vignette:.5,grain:7};},glow:()=>[],cam:t=>({x:960+20*smooth(2,8,t),y:540-10*smooth(2,8,t),fit:1+.04*smooth(2,8,t)})};
export async function renderFrame(ctx,t,w,h){
 const frame=Math.floor(t*FPS+1e-7);if(frame<0||frame>=192)throw RangeError('S12 is exactly192 exposures at24fps');
 active=await stateAtFrame(frame);baseBackground=await image(active.background);shot.bg=transmissionBackground(baseBackground,active,propCanvases(active));
 return renderPaint(ctx,t,w,h,shot);
}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
