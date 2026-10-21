// Local junction candidate: public edd1fc whole-person middle for F76-77.
// Continuous paper path and accepted geometric receiver unchanged; identity actor registration.
import {renderPaint,loadImg} from '../js/paint/paintshot.js';
import {shot as originalShot} from '../js/anim/s12_early_retained_current140.js';
import {makeCrane} from '../js/lamp/crane.js';
import {drawPuppet,solve,pointOn} from '../js/puppet.js';
import {receiverProjectionBackground} from './s12_receiver_geometry.js';
export const DURATION=140/24,FPS=24;
const ROOT='/collab/reviews/cloud_s12_20261018/',BASE='/assets/chars/g12/';
const SOURCES={bridge:{dir:'natural_first_terminal_mid_20261021',png:'FIRST_TERMINAL_MID_COMPLETE_CHARACTER.png'},first:{dir:'natural_first_lift_20261021',png:'FIRST_LIFT_COMPLETE_CHARACTER.png'},terminal:{dir:'natural_terminal_identity_20261021',png:'NATURAL_TERMINAL_COMPLETE_CHARACTER.png'},lift:{dir:'natural_same_identity_lift_20261021',png:'SAME_IDENTITY_LIFT_COMPLETE_CHARACTER.png'}};
const KEYS=[70,74,78,82,86,90,94,98,102],lerp=(a,b,u)=>a+(b-a)*u;
let corePromise,imagesPromise;const rendered=new Map();
async function core(){return corePromise||=(async()=>{
 const q=await fetch(BASE+'sequence.json').then(r=>r.json()),rows=new Map(q.states.map(r=>[r.key,r]));
 for(const [name,source]of Object.entries(SOURCES)){const m=await fetch(ROOT+source.dir+'/CONSUMER_MAPPING.json').then(r=>r.json());source.states=m.states.states||m.states;}
 return {q,rows,crane:makeCrane(1.35,'plain')};
})();}
function originalSelection(f){return f<74?['first',70]:f<76?['first',74]:f<78?['bridge',76]:f<80?['terminal',90]:f<82?['terminal',94]:['lift',102];}
function planeDepth(matrix){const [[a,b],[c,d]]=matrix,g0=a*a+c*c,g1=b*b+d*d,g01=a*b+c*d,s2=(g0+g1+Math.hypot(g0-g1,2*g01))/2,z0=Math.sqrt(Math.max(0,s2-g0)),z1=z0>1e-8?-g01/z0:Math.sqrt(Math.max(0,s2-g1));return[z0,z1];}
function geometry(data,f){
 if(f<70||f>82)throw RangeError('Only70..82 actual diagnostic');
 const u=(f-70)/12,v=u*u*(3-2*u),sourcePosition=70+32*v;let lo=70,hi=74;
 for(let i=0;i<KEYS.length-1;i++)if(sourcePosition>=KEYS[i]){lo=KEYS[i];hi=KEYS[i+1];}
 const a=data.rows.get(lo).prop,b=data.rows.get(hi).prop,t=(sourcePosition-lo)/(hi-lo),start=data.rows.get(70).prop,end=data.rows.get(102).prop;
 const angles=Object.fromEntries(Object.keys(a.pose.angles).map(k=>[k,lerp(a.pose.angles[k],b.pose.angles[k],t)]));
 const p={root:start.root.map((x,i)=>lerp(x,end.root[i],v)),matrix:a.matrix.map((r,i)=>r.map((x,j)=>lerp(x,b.matrix[i][j],t))),pose:{...a.pose,angles,rootAngle:lerp(a.pose.rootAngle||0,b.pose.rootAngle||0,t)},paperDegrees:lerp(a.paperDegrees,b.paperDegrees,t)};
 const [person,key]=originalSelection(f),native=SOURCES[person].states[String(key)].rods,sol=solve(data.crane,p.pose),depth=planeDepth(p.matrix),rods={};
 for(const role of ['R','L']){
  const local=pointOn(data.crane,sol,role==='R'?'body':'neck3',role==='R'?[-75,6]:[10,0]);
  const A=[p.root[0]+p.matrix[0][0]*local[0]+p.matrix[0][1]*local[1],p.root[1]+p.matrix[1][0]*local[0]+p.matrix[1][1]*local[1],depth[0]*local[0]+depth[1]*local[1]],G=[native[role].G[0],native[role].G[1],A[2]],L=native[role].length,d=Math.hypot(G[0]-A[0],G[1]-A[1]);
  if(d>L+1e-7||d<1e-8)throw Error('Native grip unreachable by original finite rod '+f+role+' '+d+'>'+L);
  const B=[A[0]+(G[0]-A[0])*L/d,A[1]+(G[1]-A[1])*L/d,A[2]],lambda=d/L;
  if(Math.abs(Math.hypot(...A.map((x,i)=>x-B[i]))-L)>1e-6||Math.hypot(...G.map((x,i)=>x-(A[i]+(B[i]-A[i])*lambda)))>1e-6)throw Error('Finite length/contact failed');
  rods[role]={A,B,G,length:L,grip_fraction:lambda,tail_length:L-d,depth_note:'Same2.5D construction as authored maps: drawn grip placed at current hinge depth; not measured hand volume'};
 }
 const backgroundSourceKey=person==='bridge'?74:key;
 return {frame:f,person,sourcePersonKey:key,backgroundSourceKey,originalBackground:data.rows.get(backgroundSourceKey).background,sourcePosition,sourceBracket:[lo,hi],prop:p,rods,originalSourceRoot:person==='bridge'?SOURCES.bridge.states['76'].original_prop.root:data.rows.get(key).prop.root,originalSourceRods:native};
}
export async function auditFrame(f){return geometry(await core(),f);}
async function images(data){return imagesPromise||=(async()=>{const out={backgrounds:new Map()};[out.shadow,out.front]=await Promise.all([loadImg(BASE+data.q.contactShadow),loadImg(BASE+data.q.boxFront)]);for(const k of [70,74,90,94,102]){const im=await loadImg(BASE+data.rows.get(k).background);if(!im)throw Error('Missing unchanged phase background '+k);out.backgrounds.set(k,im);}for(const[name,s]of Object.entries(SOURCES))out[name]=await loadImg(ROOT+s.dir+'/'+s.png);for(const k of ['shadow','front','first','terminal','lift','bridge'])if(!out[k])throw Error('Missing unchanged source '+k);return out;})();}
export async function renderFrame(ctx,t,w,h){
 const f=Math.floor(t*24+1e-7),data=await core(),g=geometry(data,f),imgs=await images(data);
 let active=rendered.get(f);if(!active){const p=g.prop,r=new OffscreenCanvas(1920,1080),trans=new OffscreenCanvas(1920,1080),hinges={},free={};
  for(const[canvas,mode]of[[r,'r'],[trans,'t']]){const x=canvas.getContext('2d');x.setTransform(p.matrix[0][0],p.matrix[1][0],p.matrix[0][1],p.matrix[1][1],...p.root);drawPuppet(x,data.crane,p.pose,mode);x.resetTransform();}
  const x=r.getContext('2d');x.lineCap='round';for(const role of ['R','L']){const a=g.rods[role].A,b=g.rods[role].B;hinges[role]=a.slice(0,2);free[role]=b.slice(0,2);for(const[color,width]of[['#3e2a1e',7],['#c99a52',3]]){x.strokeStyle=color;x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke();}}
  active={row:{key:'continuous-paper-'+f,prop:p},props:{r,trans,hinges,free,rods3d:g.rods},person:imgs[g.person]};rendered.set(f,active);
 }
 const shot={size:[1920,1080],light:originalShot.light,glow:originalShot.glow,cam:originalShot.cam,bg:receiverProjectionBackground(imgs.backgrounds.get(g.backgroundSourceKey),active.row,active.props,originalShot.light(t)),layers:async()=>[{img:imgs.shadow,x:0,y:0,sc:1},{img:active.props.r,x:0,y:0,sc:1},{img:active.person,x:0,y:0,sc:1},{img:imgs.front,x:0,y:0,sc:1}]};
 globalThis.__S12_CONTINUOUS_PAPER_AUDIT=g;return renderPaint(ctx,t,w,h,shot);
}
