// S20 compact2s candidate, source c1e66b16. Seven existing whole drawings. Original room renderer/CAMG; accepted drawings,
// camera-only reprojection and exact finite rods. No body rig or pose tween.
import {renderShot,billboardM,S,CRANE_ROOT,RODS,camera} from '../lamp/s06_key.js?s20_compact2s';
import {flatMaps,makeLamp,craneCard} from '../lamp/s08_back.js';
import {makeTurtle,turtlePose} from '../lamp/turtle.js';
import {NECK_UP,NECK_LOW,cranePoseOf,mixNeck,sstep} from '../lamp/choreo.js';
import {drawPuppet} from '../puppet.js';
import {loadImg} from '../paint/paintshot.js';
export const DURATION=8,FPS=24;
const BASE='/assets/chars/g20_laugh_drawn/',NW=1920,NH=1080,CROP_Y=350;
const camOptions=t=>{const k=sstep(6,8,t);return {pos:[2.55,1.7,1.2],target:[1.2,1.15,1+.02*k],hfov:42-4*k};};
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
let init,sequence,states,active,lamp,turtle;
function unproject(cam,p){
 const x=(p[0]-NW/2)/cam.focal,y=(NH/2-p[1])/cam.focal;
 // The adopted projection table stores forward depth z, unlike the engine's
 // project()[2] range. Do not normalize this ray: its forward component is1.
 const ray=cam.fwd.map((f,i)=>f+x*cam.right[i]+y*cam.up[i]);
 return cam.C.map((v,i)=>v+ray[i]*p[2]);
}
function pixels(im){const c=new OffscreenCanvas(im.width,im.height),x=c.getContext('2d');x.drawImage(im,0,0);return x.getImageData(0,0,im.width,im.height).data;}
export async function getSequenceInfo(){
 await (init ||= (async()=>{
  const [q,p]=await Promise.all(['compact_sequence.json','camera_and_rods.json'].map(async f=>{const r=await fetch(BASE+f);if(!r.ok)throw Error('Missing S20 '+f);return r.json();}));sequence=q;states=new Map();
  for(const row of q.states){
   const plan=p.states[row.rodSourceIndex??row.cameraStateIndex],rodCam=camera(NW,NH,plan.camera),sourceCam=camera(NW,NH,row.sourceCamera||plan.camera),maps={};
   for(const side of ['alb','nrm','mat']){const im=await loadImg(BASE+row[side]);if(!im||im.width!==1920||im.height!==2510)throw Error('Invalid S20 adopted map '+row[side]);maps[side]=pixels(im);}
   const rods=plan.rods.map(r=>({...r,worldA:unproject(rodCam,r.A),worldEnd:unproject(rodCam,r.physical_end),worldGrip:unproject(rodCam,r.grip)}));
   states.set(row.key,{row,plan,sourceCam,maps,rods});
  }
 })());return sequence;
}
export async function stateAtFrame(frame){await getSequenceInfo();const row=sequence.states.find(s=>frame>=s.start&&frame<=s.end);if(!row)throw RangeError('S20 compact candidate window is144–191');return states.get(row.key);}

// Same camera eye in all CAMG states: rotation/intrinsics mapping is exact
// independent of scene depth. This resamples only the view, never body parts.
function cameraMaps(state,cam,W,H){
 const out={},src=state.maps,sc=state.sourceCam;
 for(const side of ['alb','nrm','mat'])out[side]={cv:new OffscreenCanvas(W,H),id:new ImageData(W,H)};
 const A=out.alb.id.data,N=out.nrm.id.data,M=out.mat.id.data;
 const coeff=[sc.right,sc.up,sc.fwd].map(v=>[dot(cam.right,v),dot(cam.up,v),dot(cam.fwd,v)]);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const u=(x+.5-W/2)/cam.focal,v=(H/2-y-.5)/cam.focal;
  const a=coeff[0][0]*u+coeff[0][1]*v+coeff[0][2],b=coeff[1][0]*u+coeff[1][1]*v+coeff[1][2],c=coeff[2][0]*u+coeff[2][1]*v+coeff[2][2];
  const sx=NW/2+sc.focal*a/c-.5,sy=NH/2-sc.focal*b/c+CROP_Y-.5,ix=Math.floor(sx),iy=Math.floor(sy);
  if(ix<0||ix>=1919||iy<0||iy>=2509)continue;
  const fx=sx-ix,fy=sy-iy,indices=[(iy*1920+ix)*4,(iy*1920+ix+1)*4,((iy+1)*1920+ix)*4,((iy+1)*1920+ix+1)*4],weights=[(1-fx)*(1-fy),fx*(1-fy),(1-fx)*fy,fx*fy];
  let alpha=0;const rgb=[0,0,0],normal=[0,0,0];
  for(let j=0;j<4;j++){const i=indices[j],w=weights[j]*src.alb[i+3];alpha+=w;for(let k=0;k<3;k++){rgb[k]+=w*src.alb[i+k];normal[k]+=w*src.nrm[i+k];}}
  if(alpha<.01)continue;const z=(y*W+x)*4;
  for(let k=0;k<3;k++)A[z+k]=Math.round(rgb[k]/alpha);A[z+3]=N[z+3]=M[z+3]=Math.round(alpha);
  const ns=normal.map(v=>v/alpha/127.5-1),world=sc.right.map((v,i)=>v*ns[0]+sc.up[i]*ns[1]-sc.fwd[i]*ns[2]);
  for(const [k,basis,sign]of[[0,cam.right,1],[1,cam.up,1],[2,cam.fwd,-1]])N[z+k]=Math.round(127.5+127.5*sign*dot(world,basis));
  const near=indices[(fy>=.5?2:0)+(fx>=.5?1:0)];M[z+1]=src.mat[near+1];M[z+2]=src.mat[near+2];
 }
 for(const side of ['alb','nrm','mat'])out[side].cv.getContext('2d').putImageData(out[side].id,0,0);
 return {alb:out.alb.cv,nrm:out.nrm.cv,mat:out.mat.cv};
}
function craneState(t){const laugh=sstep(5.9,6.3,t),bob=laugh*Math.sin((t-6)*9),neck=mixNeck(NECK_UP,NECK_LOW,.25+.5*laugh+.2*bob);return {root:[CRANE_ROOT[0]-.08,CRANE_ROOT[1]+.005*Math.sin(t*1.7)-.03*laugh+.01*bob],pose:cranePoseOf(neck,{mode:'two'},.04+.1*bob,1)};}
function turtleState(t){const flip=sstep(5.2,5.5,t),spin=sstep(2.4,3,t)*(1-sstep(4.4,4.8,t)),x=1.95+.07*Math.sin(t*3.1)+.04*Math.sin(t*7.3)*(1-flip),z=.80+.05*Math.sin(t*4.3)-.04*flip+.02*Math.abs(Math.sin(t*9))*flip,ang=.22*Math.sin(t*2.7)+spin*.7*Math.sin(t*6.2)+Math.PI*flip;return {root:[x,z],pose:turtlePose(t*(1+flip),{facing:-1,walk:1,speed:1.6+1.2*flip,neckOut:.6-.3*spin,rootAngle:ang})};}
function sheetMatrix(cam,root,facing,px,ox,oy){
 const P=q=>cam.project([root[0]+facing*q[0]/1000,.004,root[1]+q[1]/1000]),a=P([0,0]),b=P([100,0]),c=P([0,100]),u=[(b[0]-a[0])/100,(b[1]-a[1])/100],v=[(c[0]-a[0])/100,(c[1]-a[1])/100];
 return {m:[u[0]/px,u[1]/px,-v[0]/px,-v[1]/px,a[0]-u[0]*ox/px+v[0]*oy/px,a[1]-u[1]*ox/px+v[1]*oy/px],depth:a[2]};
}
const toHand=w=>[w[0],w[2],w[1]];
const shot={cam:camOptions,exp:.26,fog:.5,
 sheet(t,env){turtle ||= makeTurtle();const C=craneState(6),T=turtleState(t);return [
  {pup:turtle,pose:T.pose,root:T.root,dist:.004,rods:[]},
  {pup:env.crane,pose:C.pose,root:C.root,dist:.004,rods:RODS.map((r,i)=>({...r,hand:toHand(active.rods[i].worldEnd)}))}
 ];},
 async cards(CARDS,cam,t,ctx){
  const C=craneState(6),cc=craneCard(ctx.crane,C.pose),cm=sheetMatrix(cam,C.root,C.pose.facing??1,2,900,1000);CARDS.addImage([{maps:cc.maps,m:cm.m}],cm.depth);
  const T=turtleState(t),tc=new OffscreenCanvas(1200,1000),tx=tc.getContext('2d');tx.translate(600,500);tx.scale(2,-2);drawPuppet(tx,turtle,T.pose,'r');const tm=sheetMatrix(cam,T.root,1,2,600,500);CARDS.addImage([{maps:flatMaps(tc,0),m:tm.m}],tm.depth);
  lamp ||= makeLamp();const L=S.lamp,base=[L.x,L.y,L.z],m=billboardM(cam,base,lamp.ox,lamp.oy,lamp.K);CARDS.addImage([{maps:lamp.metal,m},{maps:lamp.glass,m},{maps:lamp.flame,m}],cam.project(base)[2]);
  // Finite physical end, not an infinite line or a fresh hand target.
  for(const r of active.rods){const a=cam.project(r.worldA),b=cam.project(r.worldEnd),g=cam.project(r.worldGrip);CARDS.addStroke([a.slice(0,2),b.slice(0,2)],Math.max(1.5,.007*g[3]),'#9a7848',(a[2]+b[2])/2);}
  const maps=cameraMaps(active,cam,CARDS.W,CARDS.H);CARDS.addImage([{maps,m:[1,0,0,1,0,0]}],cam.project([1.13,1.10,0])[2]);
  // The original CAMG cut places Xiaoman outside the frame; no old human rigs.
 }
};
export async function renderFrame(ctx,t,W,H){const frame=Math.floor(t*24+1e-7);active=await stateAtFrame(frame);return renderShot(ctx,t,W,H,shot);}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||6,W,H);}
