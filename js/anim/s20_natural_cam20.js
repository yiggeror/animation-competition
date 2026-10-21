// NEW consumer adapter based on 01:00 checkpoint, not recovered final entry.
// Isolated CAM20 recovery: adopted whole drawings and original finite rods.
// Paper is painted before rods so the rear-side rod bindings stay visible.
// A separate module instance keeps this adapter's card/depth shader context
// from changing the already rendered CAMG laugh window.
import {renderShot,billboardM,S,camera} from '../lamp/s06_key.js?s20_natural_20261021';
import {flatMaps,makeLamp} from '../lamp/s08_back.js';
import {makeCrane} from '../lamp/crane.js';
import {makeTurtle} from '../lamp/turtle.js';
import {drawPuppet,solve,pointOn} from '../puppet.js';
import {loadImg} from '../paint/paintshot.js';
import {alignedCardShadow} from './s20_card_shadow.js';
import {projectHeldCard} from './s20_project_held_card.js';
import {heldCardShadow} from './s20_held_card_shadow.js';
const BASE='/assets/chars/s20_natural_20261021/',dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),affine=(m,p)=>[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]];
let initialization,sequence,frozen,lamp,crane,turtle;const images=new Map();
const json=async n=>{const r=await fetch(BASE+n);if(!r.ok)throw Error('Missing S20 '+n);return r.json()};
async function image(n){if(!n)throw Error('Missing adopted S20 image name');if(!images.has(n))images.set(n,(async()=>{const x=await loadImg(n.startsWith('/')?n:BASE+n);if(!x)throw Error('Missing S20 '+n);return flatMaps(x,0)})());return images.get(n)}
export async function getSequenceInfo(){await(initialization||=(async()=>{[sequence,frozen]=await Promise.all([json('sequence.json'),json('frozen_stage.json')]);lamp=makeLamp();crane=makeCrane(1.35,'plain');turtle=makeTurtle(.8)})());return sequence;}
function sheetMatrix(cam,root,ox,oy){const P=p=>cam.project([root[0]+p[0]/1000,.004,root[1]+p[1]/1000]),q=P([0,0]),a=P([100,0]),b=P([0,100]),u=[(a[0]-q[0])/100,(a[1]-q[1])/100],v=[(b[0]-q[0])/100,(b[1]-q[1])/100];return {m:[u[0]/2,u[1]/2,-v[0]/2,-v[1]/2,q[0]-u[0]*ox/2+v[0]*oy/2,q[1]-u[1]*ox/2+v[1]*oy/2],depth:q[2]};}
function worldOnPeople(cam,p){const r=frozen.registration.pair_registration,x=(p[0]-r.ox)/r.pixels_per_cm/100,y=(r.oy-p[1])/r.pixels_per_cm/100;return r.base_world_m.map((v,i)=>v+x*cam.right[i]+y*cam.up[i]);}
function onSheet(cam,p){const x=(p[0]-960)/cam.focal,y=(540-p[1])/cam.focal,ray=cam.fwd.map((v,i)=>v+x*cam.right[i]+y*cam.up[i]),k=(.004-cam.C[1])/ray[1];return cam.C.map((v,i)=>v+k*ray[i]);}
function depthMask(cards,cam,mask,rangeAt){const id=cards.m.getImageData(0,0,cards.W,cards.H),D=id.data,A=mask.getContext('2d').getImageData(0,0,cards.W,cards.H).data;for(let y=0;y<cards.H;y++)for(let x=0;x<cards.W;x++){const i=(y*cards.W+x)*4;if(A[i+3]<2)continue;const sx=(x+.5-cards.W/2)/cam.focal,sy=(cards.H/2-y-.5)/cam.focal,ray=cam.fwd.map((v,j)=>v+sx*cam.right[j]+sy*cam.up[j]),l=Math.hypot(...ray),rd=ray.map(v=>v/l);D[i]=Math.max(0,Math.min(255,Math.floor(rangeAt(rd,x+.5,y+.5)/8*255)))}cards.m.putImageData(id,0,0);}
function addPlane(cards,cam,layers,point,normal,frontOfSheet=false){cards.addImage(layers,cam.project(point)[2]);const mask=new OffscreenCanvas(cards.W,cards.H),x=mask.getContext('2d');for(const L of layers){x.save();x.setTransform(...L.m);x.drawImage(L.maps.alb,0,0);x.restore()}const n=dot(point.map((v,i)=>v-cam.C[i]),normal);depthMask(cards,cam,mask,rd=>{const d=n/dot(rd,normal);return frontOfSheet?Math.min(d,(.004-cam.C[1])/rd[1]-.04):d});}
function addRod(cards,cam,r){const a=cam.project(r.A_world),b=cam.project(r.end_world),width=Math.max(1.5,.007*b[3]);cards.addStroke([a.slice(0,2),b.slice(0,2)],width,'#9a7848',(a[2]+b[2])/2);const mask=new OffscreenCanvas(cards.W,cards.H),x=mask.getContext('2d');x.strokeStyle='#fff';x.lineCap='round';x.lineWidth=width;x.beginPath();x.moveTo(a[0],a[1]);x.lineTo(b[0],b[1]);x.stroke();const d=[b[0]-a[0],b[1]-a[1]],l2=dot(d,d),za=dot(r.A_world.map((v,i)=>v-cam.C[i]),cam.fwd),zb=dot(r.end_world.map((v,i)=>v-cam.C[i]),cam.fwd);depthMask(cards,cam,mask,(rd,px,py)=>{const u=Math.max(0,Math.min(1,((px-a[0])*d[0]+(py-a[1])*d[1])/l2));return 1/((1-u)/za+u/zb)/dot(rd,cam.fwd)});}
// Only explicitly marked chest-crossing turn frames need the held turtle in front
// of the torso. Native fist pixels are restored above it; no body warping.
function palmOcclusionMaps(people,rods){
 const maps={};
 for(const key of ['alb','nrm','mat']){
  const cv=new OffscreenCanvas(1672,941),x=cv.getContext('2d');
  x.beginPath();for(const r of rods.filter(r=>r.held!==false))for(const p of [r.grip_master,r.secondary_grip_master].filter(Boolean))x.ellipse(p[0],p[1],21,24,0,0,Math.PI*2);
  x.clip();x.drawImage(people[key],0,0);maps[key]=cv;
 }
 return maps;
}
function propCard(pup,pose,w,h,ox,oy,transmission=0){const c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.translate(ox,oy);x.scale(2,-2);drawPuppet(x,pup,pose,'r');return flatMaps(c,transmission>0?7:0,transmission)}
function frozenGeometry(){const g=frozen.geometry,cam=camera(1920,1080,g.camera),r=frozen.registration.pair_registration,pm=billboardM(cam,r.base_world_m,r.ox,r.oy,r.pixels_per_cm),C={pup:crane,root:g.crane_root_m,pose:g.puppet_poses.crane,ox:1200,oy:1300},T={pup:turtle,root:g.turtle_root_m,pose:g.puppet_poses.turtle,ox:800,oy:700};const rods=g.rod_endpoints.map(e=>{const p=e.id.startsWith('C')?C:T,sol=solve(p.pup,p.pose),q=pointOn(p.pup,sol,e.part,e.at),m=sheetMatrix(cam,p.root,p.ox,p.oy).m,a=affine(m,[p.ox+(p.pose.facing??1)*q[0]*2,p.oy-q[1]*2]);return {...e,A_world:onSheet(cam,a),end_world:worldOnPeople(cam,e.grip_master_px)}});return {cam,pm,C,T,rods};}
async function renderState(ctx,t,W,H,row,closure,custom){
 await getSequenceInfo();const g=frozenGeometry(),reg=frozen.registration.pair_registration;
 if(W!==1920||H!==1080)throw Error('S20 adopted CAM20 adapter currently requires1920x1080');
 let people,child,turtleRaster,rods=g.rods;
 const scene=custom.geometry,heldPlane=scene.paper_state.turtle.plane;g.T.root=scene.paper_state.turtle.root;g.T.pose=scene.paper_state.turtle.pose;g.C.root=scene.paper_state.crane.root;g.C.pose=scene.paper_state.crane.pose;
 people=await image(custom.people);rods=scene.rods.map(r=>({...r,end_world:r.B_world}));
 for(const r of rods){const a=g.cam.project(r.A_world);if(Math.hypot(a[0]-r.A_CAM20[0],a[1]-r.A_CAM20[1])>1e-5)throw Error('Natural source camera mismatch '+r.id)}
 // Existing material 7 represents lamp transmission through backstage leather.
 // Restore only the dark handoff path; taper out as the turtle enters the accepted lit turn.
 const leatherU=Math.max(0,Math.min(1,(1.1-g.T.root[0])/.9));
 const paperOrigin=heldPlane?.origin||[g.T.root[0],.004,g.T.root[1]];
 const lampDistance=Math.hypot(S.lamp.x-paperOrigin[0],S.lamp.y-paperOrigin[1],S.lamp.z-paperOrigin[2]);
 const incidence=heldPlane?Math.abs(dot([S.lamp.x-paperOrigin[0],S.lamp.y-paperOrigin[1],S.lamp.z-paperOrigin[2]],heldPlane.normal)):Math.max(0,S.lamp.y-.004);
 const leatherIrradiance=incidence/Math.pow(lampDistance,3);
 const leatherTransmission=Math.min(.55,.55*leatherIrradiance)*(heldPlane?1:leatherU*leatherU*(3-2*leatherU));
 const C=propCard(crane,g.C.pose,2400,2400,1200,1300),rawT=turtleRaster||propCard(turtle,g.T.pose,1600,1400,800,700,leatherTransmission),T=heldPlane?flatMaps(projectHeldCard(rawT.alb,g.cam,heldPlane),7,leatherTransmission):rawT,cm=sheetMatrix(g.cam,g.C.root,1200,1300),tm=heldPlane?{m:[1,0,0,1,0,0]}:sheetMatrix(g.cam,g.T.root,800,700),tp=heldPlane?.origin||[0,.004,0],tn=heldPlane?.normal||[0,1,0];
 const previous={occ:S.occ,back:S.occBack};S.occ=[];S.occBack=[];
 const actor=(p,ids)=>({pup:p.pup,pose:p.pose,root:p.root,dist:.004,rods:rods.filter(r=>ids.includes(r.id)).map(r=>({part:r.part|| (r.id==='C_B'?'body':r.id==='C_N'?'neck3':r.id==='T_H'?'head':'shell'),at:r.at||(r.id==='C_B'?[-75,6]:r.id==='C_N'?[10,0]:r.id==='T_H'?[20,0]:[0,40]),hand:[r.end_world[0],r.end_world[2],r.end_world[1]]}))});
 const shadow=p=>p===g.T&&heldPlane?heldCardShadow({pup:turtle,pose:g.T.pose,plane:heldPlane,lamp:S.lamp,rods:scene.rods.filter(r=>r.id.startsWith('T'))}):alignedCardShadow({pup:p.pup,pose:p.pose,root:p.root,ox:p.ox,oy:p.oy,w:p===g.T?1600:2400,h:p===g.T?1400:2400,cam:g.cam,matrix:sheetMatrix(g.cam,p.root,p.ox,p.oy).m,rods:rods.filter(r=>r.id.startsWith(p===g.T?'T':'C'))});
 const shot={cam:frozen.geometry.camera,exp:.26,fog:.5,sheet:()=>custom||closure||row?.alignPaper?[shadow(g.T),shadow(g.C)]:[actor(g.T,['T_H','T_S']),actor(g.C,['C_B','C_N'])],cards:async cards=>{
  // Match the adopted laugh lifecycle fix: reuse these canvases and GL, but
  // discard retained 2D backing pixels before composing the next action frame.
  for(const key of ['alb','nrm','mat']){
   const cv=cards[key];cv.width=cards.W;
   cv.getContext('2d').imageSmoothingQuality='high';
  }
  // Cards are composited in 2D before their per-pixel depth reaches WebGL.
  // Keep each finite A-to-B shaft above the paper and below native hands.
  addPlane(cards,g.cam,[{maps:C,m:cm.m}],[0,.004,0],[0,1,0]);addPlane(cards,g.cam,[{maps:T,m:tm.m}],tp,tn);
  for(const r of rods)addRod(cards,g.cam,r);
  const L=S.lamp,b=[L.x,L.y,L.z],lm=billboardM(g.cam,b,lamp.ox,lamp.oy,lamp.K);addPlane(cards,g.cam,[{maps:lamp.metal,m:lm},{maps:lamp.glass,m:lm},{maps:lamp.flame,m:lm}],b,g.cam.fwd);
  addPlane(cards,g.cam,[{maps:people,m:g.pm}],reg.base_world_m,g.cam.fwd,!!custom||!!closure||!!row?.alignPaper);
  if(child)addPlane(cards,g.cam,[{maps:child,m:g.pm}],reg.base_world_m,g.cam.fwd,true);
  if(scene.front_turtle_card){
   // Torso -> held prop and finite shafts -> real local fist/thumb pixels.
   addPlane(cards,g.cam,[{maps:T,m:tm.m}],tp,tn);
   const held=rods.filter(r=>r.id.startsWith('T'));
   for(const r of held){
    const depth=p=>dot(p.map((v,i)=>v-g.cam.C[i]),g.cam.fwd),pd=depth(reg.base_world_m),ad=depth(r.A_world),bd=depth(r.end_world);
    if(ad<pd){const u=bd>pd?(pd-ad)/(bd-ad):1;addRod(cards,g.cam,{...r,end_world:r.A_world.map((v,i)=>v+u*(r.end_world[i]-v))});}
   }
   addPlane(cards,g.cam,[{maps:palmOcclusionMaps(people,held),m:g.pm}],reg.base_world_m,g.cam.fwd,true);
  }

  if(custom?.captureBuffers)globalThis.__s20NaturalBuffers={albedo:cards.alb,material:cards.mat,turtle:T.alb};
 }};
 try{return await renderShot(ctx,t,W,H,shot)}finally{S.occ=previous.occ;S.occBack=previous.back}
}
export async function renderCustomState(ctx,t,W,H,custom){return renderState(ctx,t,W,H,null,null,custom);}
