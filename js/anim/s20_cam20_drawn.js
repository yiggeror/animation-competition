// Original CAM20 scene with adopted whole drawings. No old human rig.
// A separate module instance keeps this adapter's card/depth shader context
// from changing the already rendered CAMG laugh window.
import {renderShot,billboardM,S,camera} from '../lamp/s06_key.js?s20_adopted_cam20';
import {flatMaps,makeLamp} from '../lamp/s08_back.js';
import {makeCrane} from '../lamp/crane.js';
import {makeTurtle} from '../lamp/turtle.js';
import {drawPuppet,solve,pointOn} from '../puppet.js';
import {loadImg} from '../paint/paintshot.js';
const BASE='/assets/chars/g20/',dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),affine=(m,p)=>[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]];
let initialization,sequence,frozen,lamp,crane,turtle;const images=new Map();
const json=async n=>{const r=await fetch(BASE+n);if(!r.ok)throw Error('Missing S20 '+n);return r.json()};
async function image(n){if(!n)throw Error('Missing adopted S20 image name');if(!images.has(n))images.set(n,(async()=>{const x=await loadImg(BASE+n);if(!x)throw Error('Missing S20 '+n);return flatMaps(x,0)})());return images.get(n)}
export async function getSequenceInfo(){await(initialization||=(async()=>{[sequence,frozen]=await Promise.all([json('sequence.json'),json('frozen_stage.json')]);lamp=makeLamp();crane=makeCrane(1.35,'plain');turtle=makeTurtle(1.3)})());return sequence;}
function sheetMatrix(cam,root,ox,oy){const P=p=>cam.project([root[0]+p[0]/1000,.004,root[1]+p[1]/1000]),q=P([0,0]),a=P([100,0]),b=P([0,100]),u=[(a[0]-q[0])/100,(a[1]-q[1])/100],v=[(b[0]-q[0])/100,(b[1]-q[1])/100];return {m:[u[0]/2,u[1]/2,-v[0]/2,-v[1]/2,q[0]-u[0]*ox/2+v[0]*oy/2,q[1]-u[1]*ox/2+v[1]*oy/2],depth:q[2]};}
function worldOnPeople(cam,p){const r=frozen.registration.pair_registration,x=(p[0]-r.ox)/r.pixels_per_cm/100,y=(r.oy-p[1])/r.pixels_per_cm/100;return r.base_world_m.map((v,i)=>v+x*cam.right[i]+y*cam.up[i]);}
function onSheet(cam,p){const x=(p[0]-960)/cam.focal,y=(540-p[1])/cam.focal,ray=cam.fwd.map((v,i)=>v+x*cam.right[i]+y*cam.up[i]),k=(.004-cam.C[1])/ray[1];return cam.C.map((v,i)=>v+k*ray[i]);}
function depthMask(cards,cam,mask,rangeAt){const id=cards.m.getImageData(0,0,cards.W,cards.H),D=id.data,A=mask.getContext('2d').getImageData(0,0,cards.W,cards.H).data;for(let y=0;y<cards.H;y++)for(let x=0;x<cards.W;x++){const i=(y*cards.W+x)*4;if(A[i+3]<2)continue;const sx=(x+.5-cards.W/2)/cam.focal,sy=(cards.H/2-y-.5)/cam.focal,ray=cam.fwd.map((v,j)=>v+sx*cam.right[j]+sy*cam.up[j]),l=Math.hypot(...ray),rd=ray.map(v=>v/l);D[i]=Math.max(0,Math.min(255,Math.floor(rangeAt(rd,x+.5,y+.5)/8*255)))}cards.m.putImageData(id,0,0);}
function addPlane(cards,cam,layers,point,normal){cards.addImage(layers,cam.project(point)[2]);const mask=new OffscreenCanvas(cards.W,cards.H),x=mask.getContext('2d');for(const L of layers){x.save();x.setTransform(...L.m);x.drawImage(L.maps.alb,0,0);x.restore()}const n=dot(point.map((v,i)=>v-cam.C[i]),normal);depthMask(cards,cam,mask,rd=>n/dot(rd,normal));}
function addRod(cards,cam,r){const a=cam.project(r.A_world),b=cam.project(r.end_world),width=Math.max(1.5,.007*b[3]);cards.addStroke([a.slice(0,2),b.slice(0,2)],width,'#9a7848',(a[2]+b[2])/2);const mask=new OffscreenCanvas(cards.W,cards.H),x=mask.getContext('2d');x.strokeStyle='#fff';x.lineCap='round';x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke();const d=[b[0]-a[0],b[1]-a[1]],l2=dot(d,d),za=dot(r.A_world.map((v,i)=>v-cam.C[i]),cam.fwd),zb=dot(r.end_world.map((v,i)=>v-cam.C[i]),cam.fwd);depthMask(cards,cam,mask,(rd,px,py)=>{const u=Math.max(0,Math.min(1,((px-a[0])*d[0]+(py-a[1])*d[1])/l2));return 1/((1-u)/za+u/zb)/dot(rd,cam.fwd)});}
function propCard(pup,pose,w,h,ox,oy){const c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.translate(ox,oy);x.scale(2,-2);drawPuppet(x,pup,pose,'r');return flatMaps(c,0)}
function frozenGeometry(){const g=frozen.geometry,cam=camera(1920,1080,g.camera),r=frozen.registration.pair_registration,pm=billboardM(cam,r.base_world_m,r.ox,r.oy,r.pixels_per_cm),C={pup:crane,root:g.crane_root_m,pose:g.puppet_poses.crane,ox:1200,oy:1300},T={pup:turtle,root:g.turtle_root_m,pose:g.puppet_poses.turtle,ox:800,oy:700};const rods=g.rod_endpoints.map(e=>{const p=e.id.startsWith('C')?C:T,sol=solve(p.pup,p.pose),q=pointOn(p.pup,sol,e.part,e.at),m=sheetMatrix(cam,p.root,p.ox,p.oy).m,a=affine(m,[p.ox+(p.pose.facing??1)*q[0]*2,p.oy-q[1]*2]);return {...e,A_world:onSheet(cam,a),end_world:worldOnPeople(cam,e.grip_master_px)}});return {cam,pm,C,T,rods};}
async function renderState(ctx,t,W,H,row,closure){
 await getSequenceInfo();const g=frozenGeometry(),reg=frozen.registration.pair_registration;
 if(W!==1920||H!==1080)throw Error('S20 adopted CAM20 adapter currently requires1920x1080');
 let people,child,turtleRaster,rods=g.rods;
 if(closure){
  if(!sequence.closure.child)throw Error(sequence.closure.childMissingReason);
  if(!sequence.closure.scene)throw Error(sequence.closure.sceneMissingReason);
  const scene=await json(sequence.closure.scene);g.T.root=scene.turtle.root_effective_world_xz;g.T.pose=scene.turtle.pose;
  const role=sequence.closure.roleAssets[closure],Cprops=await json(role.rodMapping);
  people=await image(role.people);child=await image(sequence.closure.child);turtleRaster=await image(sequence.closure.turtleRaster);
  rods=[...scene.finite_T_rods.map(r=>({...r,end_world:r.B_world,part:r.source_original_binding.part,at:r.source_original_binding.at})),...(Cprops.rods||Cprops.finite_C_rods.map(r=>({...r,end_world:r.physical_end_world})))];
 }else{
  people=await image(row.people);
  if(row.geometry){const scene=await json(row.geometry);g.T.root=scene.turtle.root;g.T.pose=scene.turtle.pose;rods=[...rods.filter(r=>r.id.startsWith('C')), ...scene.rods];}
 }
 const C=propCard(crane,g.C.pose,2400,2400,1200,1300),T=turtleRaster||propCard(turtle,g.T.pose,1600,1400,800,700),cm=sheetMatrix(g.cam,g.C.root,1200,1300),tm=turtleRaster?{m:[1,0,0,1,0,0]}:sheetMatrix(g.cam,g.T.root,800,700);
 const previous={occ:S.occ,back:S.occBack};S.occ=[];S.occBack=[];
 const actor=(p,ids)=>({pup:p.pup,pose:p.pose,root:p.root,dist:.004,rods:rods.filter(r=>ids.includes(r.id)).map(r=>({part:r.part|| (r.id==='C_B'?'body':r.id==='C_N'?'neck3':r.id==='T_H'?'head':'shell'),at:r.at||(r.id==='C_B'?[-75,6]:r.id==='C_N'?[10,0]:r.id==='T_H'?[20,0]:[0,40]),hand:[r.end_world[0],r.end_world[2],r.end_world[1]]}))});
 const shot={cam:frozen.geometry.camera,exp:.26,fog:.5,sheet:()=>[actor(g.T,['T_H','T_S']),actor(g.C,['C_B','C_N'])],cards:async cards=>{
  for(const r of rods)addRod(cards,g.cam,r);
  addPlane(cards,g.cam,[{maps:C,m:cm.m}],[0,.004,0],[0,1,0]);addPlane(cards,g.cam,[{maps:T,m:tm.m}],[0,.004,0],[0,1,0]);
  const L=S.lamp,b=[L.x,L.y,L.z],lm=billboardM(g.cam,b,lamp.ox,lamp.oy,lamp.K);addPlane(cards,g.cam,[{maps:lamp.metal,m:lm},{maps:lamp.glass,m:lm},{maps:lamp.flame,m:lm}],b,g.cam.fwd);
  addPlane(cards,g.cam,[{maps:people,m:g.pm}],reg.base_world_m,g.cam.fwd);
  if(child)addPlane(cards,g.cam,[{maps:child,m:g.pm}],reg.base_world_m,g.cam.fwd);
 }};
 try{return await renderShot(ctx,t,W,H,shot)}finally{S.occ=previous.occ;S.occBack=previous.back}
}
export async function renderFrame(ctx,t,W,H){const q=await getSequenceInfo(),f=Math.floor(t*24+1e-7),row=q.states.find(s=>f>=s.start&&f<=s.end);if(!row){if(q.publicExposureIntervalsNotYetIntegrated?.some(r=>f>=r[0]&&f<=r[1]))throw Error('S20 frame'+f+' has adopted drawing/exposure, but per-state turtle/finite-rod registration is not bound');throw Error('S20 frame'+f+' has no complete adopted exposure bound here; pose labels are not hold assignments')}return renderState(ctx,t,W,H,row);}
export async function renderClosure(ctx,t,W,H,role='closed'){return renderState(ctx,t,W,H,null,role);}
