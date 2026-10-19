// Isolated integration gate. Source renderer, room, lamp, camera, exposure and fog
// are imported unchanged. No legacy code-person pose or deformation is called.
import {renderShot,billboardM,S,camera} from '../F000/f000_scene_gate_001/source_snapshot/js/lamp/s06_key.js';
import {flatMaps,makeLamp,craneCard} from '../F000/f000_scene_gate_001/source_snapshot/js/lamp/s08_back.js';
import {makeCrane} from '../F000/f000_scene_gate_001/source_snapshot/js/lamp/crane.js';
import {makeTurtle,turtlePose} from '../F000/f000_scene_gate_001/source_snapshot/js/lamp/turtle.js';
import {NECK_UP,NECK_LOW,NECK_DOWN,cranePoseOf,mixNeck} from '../F000/f000_scene_gate_001/source_snapshot/js/lamp/choreo.js';
import {solve,pointOn,drawPuppet} from '../F000/f000_scene_gate_001/source_snapshot/js/puppet.js';

export const CAM20={pos:[3.05,1.5,1.18],target:[1.5,.42,.95],hfov:58};
const input=await (await fetch(new URL('./registration_input.json',import.meta.url))).json();
const alb=await createImageBitmap(await(await fetch(new URL('./people_F000_rods_rotated.png',import.meta.url))).blob());
const people=flatMaps(alb,0),lamp=makeLamp(),crane=makeCrane(1.35,'plain'),turtle=makeTurtle();
// Facing follows the four approved painted axes; it is not copied from the old
// code-person staging. Puppet identities and attachment part coordinates stay fixed.
const cpose=cranePoseOf(mixNeck(NECK_UP,NECK_LOW,.25),{mode:'two'},input.crane_root_angle??-.4,-1);
const tpose=turtlePose(0,{facing:-1,walk:1,speed:1.6,neckOut:.6,rootAngle:.3});
const specs={T_H:{part:'head',at:[20,0]},T_S:{part:'shell',at:[0,40]},C_B:{part:'body',at:[-75,6]},C_N:{part:'neck3',at:[10,0]}};
const reg=input.pair_registration;
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const affine=(m,p)=>[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]];
const inverse=(m,p)=>{const d=m[0]*m[3]-m[1]*m[2],x=p[0]-m[4],y=p[1]-m[5];return[(m[3]*x-m[2]*y)/d,(-m[1]*x+m[0]*y)/d];};
const world=(cam,p)=>{
 const x=(p[0]-reg.ox)/reg.pixels_per_cm/100,y=(reg.oy-p[1])/reg.pixels_per_cm/100;
 return reg.base_world_m.map((v,i)=>v+cam.right[i]*x+cam.up[i]*y);
};
const floor=(cam,p)=>{const q=world(cam,p),u=-cam.C[2]/(q[2]-cam.C[2]);return cam.C.map((v,i)=>v+(q[i]-v)*u);};
function sheetM(cam,root,ox,oy){
 const W=mm=>cam.project([root[0]+mm[0]/1000,.004,root[1]+mm[1]/1000]);
 const q0=W([0,0]),q1=W([100,0]),q2=W([0,100]);
 const a=[(q1[0]-q0[0])/100,(q1[1]-q0[1])/100,(q2[0]-q0[0])/100,(q2[1]-q0[1])/100];
 return {m:[a[0]/2,a[1]/2,-a[2]/2,-a[3]/2,q0[0]-a[0]*ox/2+a[2]*oy/2,q0[1]-a[1]*ox/2+a[3]*oy/2],d:q0[2]};
}
function endpoints(cam,pup,pose,root,names,ox,oy){
 const sol=solve(pup,pose),cf=pose.facing??1,m=sheetM(cam,root,ox,oy);
 return names.map(id=>{const r=specs[id],p=pointOn(pup,sol,r.part,r.at);return {id,local_mm:p,card_px:[ox+cf*p[0]*2,oy-p[1]*2],screen:affine(m.m,[ox+cf*p[0]*2,oy-p[1]*2]),m};});
}
function solveRoot(cam,pm,pup,pose,names,origin,ox,oy){
 const error=root=>endpoints(cam,pup,pose,root,names,ox,oy).map(e=>{
  const p=inverse(pm,e.screen),l=input.rods[e.id];return(p[1]-l.slope*p[0]-l.intercept)/Math.hypot(1,l.slope);
 });
 let root=[...origin];
 for(let n=0;n<20;n++){
  const f=error(root);if(Math.hypot(...f)<1e-6)break;
  const h=1e-5,fx=error([root[0]+h,root[1]]),fz=error([root[0],root[1]+h]);
  const a=(fx[0]-f[0])/h,b=(fz[0]-f[0])/h,c=(fx[1]-f[1])/h,d=(fz[1]-f[1])/h,det=a*d-b*c;
  if(Math.abs(det)<1e-8)throw Error('Degenerate puppet registration');
  root[0]-=(d*f[0]-b*f[1])/det;root[1]-=(-c*f[0]+a*f[1])/det;
 }
 return {root,residual_master_px:error(root),ends:endpoints(cam,pup,pose,root,names,ox,oy)};
}
export function geometry(W=1920,H=1080){
 const cam=camera(W,H,CAM20),pm=billboardM(cam,reg.base_world_m,reg.ox,reg.oy,reg.pixels_per_cm);
 const C={root:input.crane_root_m,residual_master_px:[0,0],ends:endpoints(cam,crane,cpose,input.crane_root_m,['C_B','C_N'],900,1000)};
 const T=solveRoot(cam,pm,turtle,tpose,['T_H','T_S'],[1.95,.8],600,500);
 const ends=[...C.ends,...T.ends].map(e=>({...e,master_px:inverse(pm,e.screen),grip_screen:affine(pm,input.rods[e.id].grip_master_px),grip_world_m:world(cam,input.rods[e.id].grip_master_px)}));
 const feet=Object.fromEntries(Object.entries(input.sole_landmarks_master_px).map(([id,p])=>[id,{master_px:p,screen:affine(pm,p),billboard_world_m:world(cam,p),floor_world_m:floor(cam,p)}]));
 return {cam,pm,C,T,ends,feet};
}
function propBounds(cam,pup,pose,state,ox,oy){
 const sol=solve(pup,pose),m=sheetM(cam,state.root,ox,oy).m,pts=[];
 for(const j of pup.rig){const [x0,y0,x1,y1]=pup.parts[j.part].bounds;for(const p of [[x0,y0],[x1,y0],[x0,y1],[x1,y1]]){const q=pointOn(pup,sol,j.part,p);pts.push(affine(m,[ox+(pose.facing??1)*q[0]*2,oy-q[1]*2]));}}
 return [Math.min(...pts.map(p=>p[0])),Math.min(...pts.map(p=>p[1])),Math.max(...pts.map(p=>p[0])),Math.max(...pts.map(p=>p[1]))];
}
export function scanPuppetRegistration(){
 const cam=camera(1920,1080,CAM20),pm=billboardM(cam,reg.base_world_m,reg.ox,reg.oy,reg.pixels_per_cm);
 const options={C:[],T:[]};
 for(const type of ['C','T'])for(const facing of [-1,1])for(let ai=-24;ai<=24;ai++)for(const blend of (type==='C'?[0,.25,.5,.75,1,1.25,1.5,1.75,2]:[0])){
  const angle=ai*.05;
  const pose=type==='C'?cranePoseOf(blend<=1?mixNeck(NECK_UP,NECK_LOW,blend):mixNeck(NECK_LOW,NECK_DOWN,blend-1),{mode:'two'},angle,facing):turtlePose(0,{facing,walk:1,speed:1.6,neckOut:.6,rootAngle:angle});
  const pup=type==='C'?crane:turtle,names=type==='C'?['C_B','C_N']:['T_H','T_S'],ox=type==='C'?900:600,oy=type==='C'?1000:500;
  let state;try{state=solveRoot(cam,pm,pup,pose,names,[1.4,1.2],ox,oy);}catch{continue;}
  if(!state.root.every(Number.isFinite)||state.root[0]<.25||state.root[0]>2.35||state.root[1]<.15||state.root[1]>1.94||Math.hypot(...state.residual_master_px)>.01)continue;
  const ends=state.ends.map(e=>({...e,p:inverse(pm,e.screen)}));
  if(ends.some(e=>e.p[0]>input.rods[e.id].shaft_tip_master_px[0]-3))continue;
  const bounds=propBounds(cam,pup,pose,state,ox,oy);
  const clip=Math.max(0,-bounds[0])+Math.max(0,-bounds[1])+Math.max(0,bounds[2]-1920)+Math.max(0,bounds[3]-1080);
  const extra=ends.reduce((s,e)=>s+Math.abs(e.p[0]-input.rods[e.id].shaft_tip_master_px[0]),0);
  options[type].push({pose,root:state.root,bounds,score:clip*20+Math.abs(angle)*8+extra*.01+(type==='C'?Math.abs(blend-.25)*3:0),clip,blend,angle,facing});
 }
 for(const type of ['C','T'])options[type].sort((a,b)=>a.score-b.score);
 return {C:options.C.slice(0,6),T:options.T.slice(0,6)};
}
function actorProxy(cam){
 // Actual new art positions supply caster locations; no old-person shadow proxies.
 const out=[];
 for(const points of Object.values(input.sole_outline_points_master_px))for(const p of points){const q=floor(cam,p);out.push([q[0],q[1],.018,.028]);}
 for(const [p,r] of [[[1110,500],.17],[[1110,360],.17],[[1100,140],.14],[[1090,710],.07],[[1173,710],.07],[[588,460],.12],[[582,330],.11],[[577,255],.13],[[560,770],.045],[[613,770],.045]]){
  const q=world(cam,p);out.push([...q,r]);
 }
 return out;
}
function fixCardDepth(cards,cam,mask,depthAt){
 // The shared source encodes a single Euclidean range per card. For a whole
 // two-person card this can put the child BEHIND the sheet. Correct only the
 // isolated adapter's material R channel, using camera-ray/plane intersection.
 const id=cards.m.getImageData(0,0,cards.W,cards.H),D=id.data,M=mask.getContext('2d').getImageData(0,0,cards.W,cards.H).data;
 for(let y=0;y<cards.H;y++)for(let x=0;x<cards.W;x++){
  const i=(y*cards.W+x)*4;if(M[i+3]<2)continue;
  const sx=(x+.5-cards.W/2)/cam.focal,sy=(cards.H/2-y-.5)/cam.focal;
  const ray=cam.fwd.map((v,j)=>v+cam.right[j]*sx+cam.up[j]*sy);
  const len=Math.hypot(...ray),rd=ray.map(v=>v/len),depth=depthAt(rd,x+.5,y+.5);
  // Floor the 8-bit range: 4mm leather/sheet separation is less than one bin.
  D[i]=Math.max(0,Math.min(255,Math.floor(depth/8*255)));
 }
 cards.m.putImageData(id,0,0);
}
function addPlaneCard(cards,cam,layers,depth,point,normal){
 cards.addImage(layers,depth);
 const mask=new OffscreenCanvas(cards.W,cards.H),cx=mask.getContext('2d');
 for(const L of layers){cx.save();cx.setTransform(...L.m);cx.drawImage(L.maps.alb,0,0);cx.restore();}
 const numerator=dot(point.map((v,i)=>v-cam.C[i]),normal);
 fixCardDepth(cards,cam,mask,rd=>numerator/dot(rd,normal));
}
function addRod(cards,cam,e,width,W,H){
 const pts=[e.screen,e.grip_screen],B=cam.project(e.grip_world_m);
 cards.addStroke(pts,width+1,'#57422b',(e.m.d+B[2])/2);
 cards.addStroke(pts,width,'#ae8750',(e.m.d+B[2])/2);
 const mask=new OffscreenCanvas(W,H),x=mask.getContext('2d');x.strokeStyle='#fff';x.lineWidth=width+1;x.lineCap='round';x.beginPath();x.moveTo(...pts[0]);x.lineTo(...pts[1]);x.stroke();
 const a=pts[0],b=pts[1],v=[b[0]-a[0],b[1]-a[1]],len2=dot(v,v);
 const sx=(a[0]-W/2)/cam.focal,sy=(H/2-a[1])/cam.focal,rv=cam.fwd.map((q,i)=>q+cam.right[i]*sx+cam.up[i]*sy);
 const opticalA=(.004-cam.C[1])/rv[1],opticalB=dot(e.grip_world_m.map((q,i)=>q-cam.C[i]),cam.fwd);
 fixCardDepth(cards,cam,mask,(rd,px,py)=>{const u=Math.max(0,Math.min(1,((px-a[0])*v[0]+(py-a[1])*v[1])/len2));return 1/((1-u)/opticalA+u/opticalB)/dot(rd,cam.fwd);});
}
export async function renderF000(canvas,W=1920,H=1080,t=0){
 if(t!==0)throw Error('Only F000 is authorized; later states are not implemented.');
 canvas.width=W;canvas.height=H;
 const g=geometry(W,H);S.occ=[];S.occBack=actorProxy(g.cam);
 const tc=new OffscreenCanvas(1200,1000),tx=tc.getContext('2d');tx.translate(600,500);tx.scale(2,-2);drawPuppet(tx,turtle,tpose,'r');
 const cm=sheetM(g.cam,g.C.root,1200,1300),tm=sheetM(g.cam,g.T.root,600,500);
 const cc=new OffscreenCanvas(2400,2400),cx=cc.getContext('2d');cx.translate(1200,1300);cx.scale(2,-2);drawPuppet(cx,crane,cpose,'r');const propC=flatMaps(cc,0),propT=flatMaps(tc,0);
 const actor=(pup,pose,state,ids)=>({pup,pose,root:state.root,dist:.004,rods:ids.map(id=>{const r=specs[id],w=world(g.cam,input.rods[id].grip_master_px);return {...r,hand:[w[0],w[2],w[1]]};})});
 const shot={cam:CAM20,exp:.26,fog:.5,
  sheet:()=>[actor(turtle,tpose,g.T,['T_H','T_S']),actor(crane,cpose,g.C,['C_B','C_N'])],
  cards:async cards=>{
   // Rods are behind puppet skins and the real painted hands. Every endpoint
   // uses the same affine card map as its skin (not a mismatched perspective).
   for(const e of g.ends){
    const width=Math.max(1.5,2.7*Math.abs(g.pm[0]));
    addRod(cards,g.cam,e,width,W,H);
   }
   addPlaneCard(cards,g.cam,[{maps:propC,m:cm.m}],cm.d,[0,.004,0],[0,1,0]);
   addPlaneCard(cards,g.cam,[{maps:propT,m:tm.m}],tm.d,[0,.004,0],[0,1,0]);
   const L=S.lamp,lb=[L.x,L.y,L.z],lm=billboardM(g.cam,lb,lamp.ox,lamp.oy,lamp.K);
   addPlaneCard(cards,g.cam,[{maps:lamp.metal,m:lm},{maps:lamp.glass,m:lm},{maps:lamp.flame,m:lm}],g.cam.project(lb)[2],lb,g.cam.fwd);
   addPlaneCard(cards,g.cam,[{maps:people,m:g.pm}],g.cam.project(reg.base_world_m)[2],reg.base_world_m,g.cam.fwd);
  }};
 await renderShot(canvas.getContext('2d'),0,W,H,shot);
 return report(g,W,H);
}
export function report(g=geometry(),W=1920,H=1080){
 return {frame:0,time_seconds:0,W,H,camera:CAM20,exp:.26,fog:.5,
  actual_source_renderer:'s06_key.renderShot / unchanged snapshot',new_model_calls:0,later_states_rendered:0,
  pair_registration:reg,art_height_ratio_X_to_G:input.raster_height_ratio_X_to_G,
  crane_root_m:g.C.root,turtle_root_m:g.T.root,puppet_poses:{crane:cpose,turtle:tpose},
  puppet_bounds_conservative_screen:{crane:propBounds(g.cam,crane,cpose,g.C,900,1000),turtle:propBounds(g.cam,turtle,tpose,g.T,600,500)},
  puppet_registration_status:'DIRECTOR_SCOPE_372d96fe / single formal CAM20 candidate; not batch-approved',
  root_solver_residual_master_px:{C:g.C.residual_master_px,T:g.T.residual_master_px},
  rod_endpoints:g.ends.map(e=>({id:e.id,holder:input.rods[e.id].initial_holder,part:specs[e.id].part,at:specs[e.id].at,
   master_px:e.master_px,screen:e.screen,grip_master_px:input.rods[e.id].grip_master_px,grip_screen:e.grip_screen,
   grip_world_m:e.grip_world_m,shaft_tip_master_px:input.rods[e.id].shaft_tip_master_px,
   extends_beyond_painted_tip:e.master_px[0]<input.rods[e.id].shaft_tip_master_px[0],
   skin_endpoint_stroke_endpoint_error_px:0})),
  feet:g.feet,room:S.room,sheet:S.sheet,lamp:S.lamp,moon:S.moon,
  actor_caster_proxy_count:S.occBack.length,material_depth:'isolated adapter per-pixel ray/plane range, floor-quantised to 8-bit / shared renderer unchanged',
  note:'Official camera is a medium shot. Auxiliary taller F000 uses the same camera and focal length to inspect feet. No independent body transform.'};
}

export function scanApprovedRootOnly(){
 const cam=camera(1920,1080,CAM20),out=[];
 for(let xi=60;xi<=230;xi+=2)for(let zi=30;zi<=170;zi+=2){const root=[xi/100,zi/100],state={root},bounds=propBounds(cam,crane,cpose,state,900,1000);const [l,t,r,b]=bounds;
 if(l<10||t<15||r>1110||b>1040)continue;
 const score=Math.abs(r-650)*2+Math.abs(t-90)*.4+Math.abs(b-770)*.1;
 out.push({root,bounds,score,ends:endpoints(cam,crane,cpose,root,['C_B','C_N'],900,1000).map(e=>({id:e.id,screen:e.screen}))});}
 return out.sort((a,b)=>a.score-b.score).slice(0,8);
}

export function preflightMasks(){
 const g=geometry(),W=1920,H=1080,pc=new OffscreenCanvas(W,H),px=pc.getContext('2d'),hc=new OffscreenCanvas(W,H),hx=hc.getContext('2d');
 px.setTransform(...sheetM(g.cam,g.C.root,900,1000).m);px.drawImage(craneCard(crane,cpose).maps.alb,0,0);
 hx.setTransform(...g.pm);hx.beginPath();hx.rect(480,165,195,245);hx.clip();hx.drawImage(alb,0,0);
 const p=px.getImageData(0,0,W,H).data,h=hx.getImageData(0,0,W,H).data;let overlap=0,count=0,l=W,t=H,r=0,b=0;
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){const i=(y*W+x)*4;if(p[i+3]>80){count++;l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);if(h[i+3]>80)overlap++;}}
 return {crane_root_m:g.C.root,actual_crane_bounds:[l,t,r+1,b+1],crane_pixels:count,actual_crane_overlap_child_head_pixels:overlap,conservative_bounds:propBounds(g.cam,crane,cpose,g.C,900,1000),camera:CAM20};
}
export function scanHeadClearRodRoots(){
 const W=1920,H=1080,g=geometry(),hc=new OffscreenCanvas(W,H),hx=hc.getContext('2d');hx.setTransform(...g.pm);hx.beginPath();hx.rect(480,165,195,245);hx.clip();hx.drawImage(alb,0,0);const hd=hx.getImageData(0,0,W,H).data;
 const hit=(x,y)=>{x=Math.round(x);y=Math.round(y);return x>=0&&x<W&&y>=0&&y<H&&hd[(y*W+x)*4+3]>50;};
 const cc=craneCard(crane,cpose).maps.alb,cx=cc.getContext('2d'),cd=cx.getImageData(0,0,cc.width,cc.height).data,pts=[];
 for(let y=0;y<cc.height;y+=6)for(let x=0;x<cc.width;x+=6)if(cd[(y*cc.width+x)*4+3]>80)pts.push([x,y]);
 const out=[];let framed=0,clearRods=0;
 for(let xi=30;xi<=210;xi+=2)for(let zi=50;zi<=154;zi+=2){const root=[xi/100,zi/100],state={root},bounds=propBounds(g.cam,crane,cpose,state,900,1000);const [l,t,r,b]=bounds;if(l<15||t<20||r>1080||b>1020)continue;framed++;
 const es=endpoints(g.cam,crane,cpose,root,['C_B','C_N'],900,1000);let bad=false;
 for(const e of es){const grip=affine(g.pm,input.rods[e.id].grip_master_px),a=e.screen,n=Math.ceil(Math.hypot(grip[0]-a[0],grip[1]-a[1])/2);for(let i=0;i<=n;i++){const t=i/n,x=a[0]*(1-t)+grip[0]*t,y=a[1]*(1-t)+grip[1]*t;if(hit(x,y)||hit(x,y-4)||hit(x,y+4)||hit(x-4,y)||hit(x+4,y)){bad=true;break;}}if(bad)break;}
 if(bad)continue;clearRods++;
 const m=sheetM(g.cam,root,900,1000).m;for(const p of pts){const [x,y]=affine(m,p);if(hit(x,y)||hit(x-3,y)||hit(x+3,y)){bad=true;break;}}
 if(bad)continue;
 out.push({root,bounds,score:Math.abs(r-1050)+Math.abs(t-70)*.3,ends:es.map(e=>({id:e.id,screen:e.screen}))});}
 out.sort((a,b)=>a.score-b.score);return{framed_candidates:framed,head_clear_rod_candidates:clearRods,fully_head_clear_candidates:out.length,best:out.slice(0,6),camera_unchanged:CAM20};
}

// One global rigid crane-assembly rotation/translation, all internal angles fixed.
// Keep the upper neck3 endpoint exactly fixed while registering body to new CB.
export function solveLowerOnlyRigidAssembly(){
 const cam=camera(1920,1080,CAM20),pm=billboardM(cam,reg.base_world_m,reg.ox,reg.oy,reg.pixels_per_cm),target=input.crane_neck3_fixed_master_px;
 const error=v=>{const pose={...cpose,rootAngle:v[2]},ee=endpoints(cam,crane,pose,[v[0],v[1]],['C_B','C_N'],900,1000),b=inverse(pm,ee[0].screen),n=inverse(pm,ee[1].screen),q=input.rods.C_B;return[n[0]-target[0],n[1]-target[1],(b[1]-q.slope*b[0]-q.intercept)/Math.hypot(1,q.slope)];};
 const solve=(a,b)=>{a=a.map((r,i)=>[...r,b[i]]);for(let c=0;c<3;c++){let k=c;for(let j=c+1;j<3;j++)if(Math.abs(a[j][c])>Math.abs(a[k][c]))k=j;[a[c],a[k]]=[a[k],a[c]];const p=a[c][c];if(Math.abs(p)<1e-12)throw Error('rigid assembly singular');for(let j=c;j<4;j++)a[c][j]/=p;for(let i=0;i<3;i++)if(i!==c){const v=a[i][c];for(let j=c;j<4;j++)a[i][j]-=v*a[c][j];}}return a.map(r=>r[3]);};
 let v=[...input.crane_root_m,input.crane_root_angle??-.4];for(let i=0;i<24;i++){const e=error(v);if(Math.hypot(...e)<1e-7)break;const h=1e-5,j=[0,1,2].map(k=>{const w=[...v];w[k]+=h;return error(w).map((q,i)=>(q-e[i])/h);});const dv=solve([0,1,2].map(i=>j.map(c=>c[i])),e);const damp=Math.max(1,Math.abs(dv[2])/.15);v=v.map((q,i)=>q-dv[i]/damp);}
 return{root:v.slice(0,2),rootAngle:v[2],rootAngle_delta_degrees:(v[2]+.4)*180/Math.PI,residual:error(v),internal_angles_unchanged:true,facing_unchanged:true,scale_unchanged:true,upper_CN_endpoint_fixed_master:target};
}
