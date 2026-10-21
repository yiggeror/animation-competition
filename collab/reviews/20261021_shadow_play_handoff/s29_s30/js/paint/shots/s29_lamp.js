// S29/S30 shared lamp / head / sheet geometry. Reviewed preparation endpoint,
// not a facial morph or a completed blow. No change to the global renderer.
import { renderShot, billboardM, S } from '../../lamp/s06_key.js';
import { loadMaps, makeLamp, flatMaps } from '../../lamp/s08_back.js';
import { composeGrandmaShadow } from './s29_shadow_bust.js';
const GR={ox:250,oy:770,sc:24}; // original lip point; 24 source pixels per cm
const FINAL=[1.43,.44,1.23];
const smooth=(a,b,t)=>{const u=Math.max(0,Math.min(1,(t-a)/(b-a)));return u*u*(3-2*u);};
let GM=null,LM=null,PUP=null;
async function ready(){
  if(GM)return;
  const maps=await loadMaps('g29_prepare_blow');
  const original=await createImageBitmap(await(await fetch('/assets/chars/g29_prepare_blow_shadow.png')).blob());
  const extension=await createImageBitmap(await(await fetch('/assets/chars/g29_neck_shoulders_20261021.png')).blob());
  const mask=composeGrandmaShadow(original,extension);
  const bounds=[-GR.ox/GR.sc*10,(GR.oy-mask.height)/GR.sc*10,(mask.width-GR.ox)/GR.sc*10,GR.oy/GR.sc*10];
  const part={part:'head',parent:null,layer:0,bounds,t:mask,r:maps.alb};
  PUP={rig:[part],parts:{head:part}};LM=preparationLamp();GM=maps;
}
export function preparationState(localTime){
  const k=smooth(0,1.1,localTime),base=[FINAL[0]-.03*(1-k),FINAL[1]-.04*(1-k),FINAL[2]];
  const L=S.lamp,m=L.y/(L.y-base[1]);
  return {base,lipSource:[GR.ox,GR.oy],pixelsPerCm:GR.sc,lamp:[L.x,L.y,L.z],lipToFlame:Math.hypot(L.x-base[0],L.y-base[1],L.z-base[2]),magnification:m,projectedLip:[L.x+(base[0]-L.x)*m,L.z+(base[2]-L.z)*m]};
}
function actor(base){
  // The backstage camera faces -y: image-left maps to world +x. From the
  // audience/front camera the very same physical head therefore faces right.
  return {pup:PUP,pose:{angles:{},rootAngle:0,facing:-1},root:[base[0],base[2]],dist:base[1]};
}
// Keep the established lamp geometry, with a transparent glass card for this
// close camera. A bounded housing material avoids the point lamp illuminating
// its own colocated metal card to orange-white; flame emission stays unchanged.
function preparationLamp(){
  const lamp=makeLamp(),glass=new OffscreenCanvas(260,460),x=glass.getContext('2d');
  x.globalAlpha=.08;x.drawImage(lamp.glass.alb,0,0);x.globalAlpha=1;
  x.strokeStyle='rgba(216,224,219,.30)';x.lineWidth=1.3;x.beginPath();x.ellipse(130,235,52,70,0,0,Math.PI*2);x.stroke();
  x.strokeStyle='rgba(243,239,218,.42)';x.lineWidth=2.5;x.lineCap='round';x.beginPath();x.moveTo(100,195);x.quadraticCurveTo(84,218,90,244);x.stroke();
  return {...lamp,metal:flatMaps(lamp.metal.alb,8,.12),glass:flatMaps(glass,8,0)};
}
// First-order projection of the same vertical x/z head plane used by the
// sheet actor. The camera may move sideways without rotating the source face.
function headM(cam,base){
  const p=cam.project(base),dx=cam.project([base[0]-1/24,base[1],base[2]]),dy=cam.project([base[0],base[1],base[2]-1/24]);
  const a=(dx[0]-p[0])/100,b=(dx[1]-p[1])/100,c=(dy[0]-p[0])/100,d=(dy[1]-p[1])/100;
  return [a,b,c,d,p[0]-a*GR.ox-c*GR.oy,p[1]-b*GR.ox-d*GR.oy];
}
const prepare={
  cam:{pos:[1.15,1.6,1.32],target:[1.52,.44,1.32],hfov:36},
  exp:.08,fluor:()=>1,fog:.2,
  sheet:t=>[actor(preparationState(t-10).base)],
  cards:async(CARDS,cam,t)=>{
    const base=preparationState(t-10).base;
    CARDS.addImage([{maps:GM,m:headM(cam,base)}],cam.project(base)[2]);
    const L=S.lamp,lb=[L.x,L.y,L.z],m=billboardM(cam,lb,LM.ox,LM.oy,LM.K);
    CARDS.addImage([{maps:LM.metal,m},{maps:LM.glass,m},{maps:LM.flame,m}],cam.project(lb)[2]);
  },
};
const frozen={
  cam:{pos:[1,-2.5,1.45],target:[1,0,1.45],hfov:43},
  exp:.65,fluor:()=>0,cards:null,fog:.45,
  // Only light and cloth continue to move. Grandma holds her breath/pose.
  sheet:()=>[actor(FINAL)],
};
export async function renderPreparation(ctx,localTime,w,h){await ready();return renderShot(ctx,10+localTime,w,h,prepare);}
export async function renderFrozenHead(ctx,s30Time,w,h){await ready();return renderShot(ctx,12+s30Time,w,h,frozen);}

