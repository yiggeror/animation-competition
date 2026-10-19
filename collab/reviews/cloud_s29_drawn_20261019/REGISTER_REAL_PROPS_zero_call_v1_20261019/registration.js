// Own review compositor. All human pixels are the approved single native mother.
// Original production geometry/raster drawing is used ONLY for the actual props.
import {makeCrane} from '/js/lamp/crane.js';
import {makeTurtle,turtlePose} from '/js/lamp/turtle.js';
import {cranePoseOf,NECK_DOWN} from '/js/lamp/choreo.js';
import {drawPuppet,solve,pointOn} from '/js/puppet.js';
import {loadImg,renderPaint} from '/js/paint/paintshot.js';
import {sourceShot} from '/js/paint/shots/s29.js?readonlyShotExport=1';

const R='/collab/reviews/cloud_s29_drawn_20261019/REGISTER_REAL_PROPS_zero_call_v1_20261019/';
const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
const mode=new URLSearchParams(location.search).get('mode')||'scene';
const crane=makeCrane(),turtle=makeTurtle();
const cp=cranePoseOf(NECK_DOWN,{mode:'two'},0,-1);
const tp=turtlePose(0,{walk:0,neckOut:.05,facing:1,rootAngle:0});
const plane={sx:.55,sy:-.33};
const C1=[536,750],C2=[845,744];
const q=pointOn(crane,solve(crane,cp),'neck3',[10,0]);
const craneRoot=[C1[0]-plane.sx*cp.facing*q[0],C1[1]-plane.sy*q[1]];
const turtleRoot=[426,880];
const project=(pup,pose,root,part,at)=>{
  const p=pointOn(pup,solve(pup,pose),part,at);
  return [root[0]+plane.sx*(pose.facing??1)*p[0],root[1]+plane.sy*p[1]];
};
const rods=[
 {puppet:'crane',part:'body',at:[-75,6],end:[973,903]},
 {puppet:'crane',part:'neck3',at:[10,0],end:[945,931]},
 {puppet:'turtle',part:'shell',at:[0,40],end:[869,967]},
 {puppet:'turtle',part:'head',at:[20,0],end:[864,989]},
].map(r=>({...r,start:r.puppet==='crane'?project(crane,cp,craneRoot,r.part,r.at):project(turtle,tp,turtleRoot,r.part,r.at)}));
const geom={status:'REAL_ORIGINAL_PROPS_REGISTERED_TO_APPROVED_RAW_MOTHER_PENDING_ASTRA',
 imagegenCallsThisStage:0,nearBareRightPalmTarget:C1,farBangleLeftClothPinch:C2,
 originalCraneDefaultScale:1.35,originalTurtleDefaultScale:1.3,
 commonLapProjection:plane,craneRoot,turtleRoot,cranePose:cp,turtlePose:tp,
 neck3TruePartLocalPoint:[10,0],neck3NotRivetCenter:true,
 neck3ProjectedPoint:project(crane,cp,craneRoot,'neck3',[10,0]),
 neck3ContactErrorPx:Math.hypot(...project(crane,cp,craneRoot,'neck3',[10,0]).map((v,i)=>v-C1[i])),
 pointOnFacingApplication:'pointOn excludes facing; apply facing ONCE before common lap plane',
 fourRealStraightRods:rods,
 depthOrder:'original thighs -> repaired original cloth base -> rods -> complete original turtle/crane -> original raised cloth lip -> original near palm',
 originalPuppetPartsReshaped:false,independentHumanPartTransforms:false,
 sourceCameraTime:0,actualCameraOnlyNoOldActionAdoption:true};
if(mode==='props'){
 const p=canvas(1024,1536),x=p.getContext('2d');
 x.lineCap='round';
 for(const r of rods){
  x.beginPath();x.moveTo(...r.start);x.lineTo(...r.end);
  x.strokeStyle='#4d3924';x.lineWidth=4;x.stroke();
  x.strokeStyle='#b58b54';x.lineWidth=2;x.stroke();
 }
 for(const [pup,pose,root] of [[turtle,tp,turtleRoot],[crane,cp,craneRoot]]){
  x.save();x.translate(...root);x.scale(plane.sx,plane.sy);drawPuppet(x,pup,pose,'r');x.restore();
 }
 window.payload={'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png':p.toDataURL()};
 window.geometry=geom;window.ready=true;
}else{
 const W=1920,H=1080,t=0,camera=sourceShot.cam(t);
 const k=camera.fit*W/sourceShot.size[0],ox=W/2-camera.x*k,oy=H/2-camera.y*k;
 const mother=await loadImg(R+'layers/REGISTERED_COMPLETE_MOTHER_ORIGINAL_PROPS.png');
 const albedo=canvas(W,H),ax=albedo.getContext('2d');ax.imageSmoothingQuality='high';
 ax.setTransform(k,0,0,k,ox,oy);
 const bg=await loadImg(sourceShot.bg);ax.drawImage(bg,0,0,...sourceShot.size);
 const sourceLayers=await sourceShot.layers(t);
 const originalGM=sourceLayers[2];
 // One complete-card translation only: the new source crown is higher than the
 // old source crown. Keep actual camera, scale and X; move ALL mother/prop pixels
 // down 30 output pixels to retain a small top margin. No body-part adjustment.
 const uniformGM={...originalGM,y:originalGM.y+30/k};
 for(let i=0;i<sourceLayers.length;i++){
  if(i===4)continue; // director: both puppets stay with grandma; old child turtle is not inherited.
  const L=i===2?uniformGM:sourceLayers[i],img=i===2?mother:L.img;
  ax.save();ax.globalAlpha=L.alpha??1;ax.translate(L.x,L.y);ax.scale(L.sc,L.sc);ax.drawImage(img,0,0);ax.restore();
 }
 const light=sourceShot.light(t),map=L=>({...L,x:L.x*k+ox,y:L.y*k+oy,r:L.r*k});
 const local={bg:albedo,size:[W,H],
  light:()=>({...light,lights:light.lights.map(map)}),
  glow:()=>sourceShot.glow(t).map(map),
  emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);sourceShot.emit(x,t);x.restore();},
  cam:()=>({x:W/2,y:H/2,fit:1})};
 const final=document.getElementById('frame');await renderPaint(final.getContext('2d'),t,W,H,local);
 const scale=k*uniformGM.sc,offset=[ox+k*uniformGM.x,oy+k*uniformGM.y];
 const toScene=p=>p.map((v,i)=>v*scale+offset[i]);
 Object.assign(geom,{actualScene:[W,H],sourceShotCamera:camera,entireMotherAndAllLayersUniformTransform:{scale,offset,matrix:[scale,0,0,scale,...offset]},
   nearPalmScene:toScene(C1),farClothScene:toScene(C2),sourceLayerIndicesExcluded:[4],
   exclusionReason:'old child-held turtle conflicts with latest Opus S28/S29 no-handover decision',
   sourceStageAndLightKept:true,oldMotherClothWarpOrOldTimingInherited:false});
 geom.wholeMotherRegistrationAdjustment={outputDownPx:30,reason:'retain new native crown within unchanged actual close camera',sourcePlacement:originalGM,reviewPlacement:uniformGM};
 window.payload={'scene/S29_F000_FORMAL_CAMERA_REAL_ORIGINAL_PROPS.png':final.toDataURL()};
 for(const [name,center] of [['C1_NEAR_PALM_ORIGINAL_NECK3',toScene(C1)],['C2_FAR_PINCH_CLOTH_OVER_TAIL',toScene(C2)]]){
  const bx=Math.round(center[0]-150),by=Math.round(center[1]-135),c=canvas(300,270);
  c.getContext('2d').drawImage(final,bx,by,300,270,0,0,300,270);
  window.payload[`contacts/${name}_ACTUAL_FORMAL_CROP.png`]=c.toDataURL();
 }
 window.geometry=geom;window.ready=true;
}
