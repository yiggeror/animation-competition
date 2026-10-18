// S13 drawn candidate:16 native drawing states; no old A/B figure or face deformation.
// Scene room/crate/crane/light copied from the fixed original S13; shared files unchanged.
import { renderPaint, loadImg } from '/js/paint/paintshot.js';
import { makeCrane } from '/js/lamp/crane.js';
import { cranePoseOf, NECK_UP } from '/js/lamp/choreo.js';
import { drawPuppet } from '/js/puppet.js';
export const DURATION = 5;
const W=1920,H=1080;
export const PLACEMENT={x:330,y:-30,scale:.85};
const canvas=(w,h)=>new OffscreenCanvas(w,h);
export const SHEET = [
  [
    "/collab/reviews/cloud_s13_20261018/d01_first_candidate/candidates/S13_d01_uniform_registered_rgba",
    0
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d02_d04_segment/approved_local/F018_d02_eyes_up",
    18
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d02_d04_segment/approved_local/F024_d03_whole_head_right",
    24
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d02_d04_segment/approved_local/F030_d04_awake_closed_mouth",
    30
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d05_d07_segment/approved_local/F036_d05_pretend_drowsy",
    36
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d05_d07_segment/approved_local/F040_d06_yawn_start",
    40
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d05_d07_segment/approved_local/F044_d07_yawn_opening",
    44
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d08_d10_group/approved_local/F050_d08_yawn_peak",
    50
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d08_d10_group/approved_local/F058_d09_sustained_breath",
    58
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d08_d10_group/approved_local/F068_d10_yawn_release",
    68
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d11_d13_group/approved_local/F078_d11_near_closed",
    78
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d11_d13_group/approved_local/F084_d12_closed_before_turn",
    84
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d11_d13_group/approved_local/F087_d13_whole_head_turn_start",
    87
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d14_d16_group/approved_local/F090_d14_turn_left",
    90
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d14_d16_group/approved_local/F094_d15_head_arrived_hair_lags",
    94
  ],
  [
    "/collab/reviews/cloud_s13_20261018/d14_d16_group/approved_local/F100_d16_tail_settled",
    100
  ]
];
export function pick(t) {
  const f=Math.max(0,Math.min(119,Math.floor(t*24+1e-6)));
  let n=SHEET[0][0];for(const [name,start] of SHEET)if(f>=start)n=name;return n;
}
export function state(t){const f=Math.max(0,Math.min(119,Math.floor(t*24+1e-6)));return {frame:f,drawing:SHEET.findIndex(([name])=>name===pick(t))+1,path:pick(t)+'.png',placement:PLACEMENT};}
async function character(t){
  const im=await loadImg(pick(t)+'.png');
  if(!im||im.width!==1024||im.height!==1536)throw Error('S13 requires the exact1024×1536 adopted drawing: '+pick(t));
  return im;
}
let ROOM,CRANE;
async function room(){
  if(ROOM)return ROOM;
  const im=await loadImg('bg_01_room_wide');if(!im)throw Error('S13 needs the S12 room background.');
  const c=canvas(W,H),x=c.getContext('2d');
  // Same wall/floor texture crop and cedar/blue-cloth palette as S12, closer reverse angle.
  x.filter='blur(20px)';x.drawImage(im,300,330,900,506,-80,-60,W+160,H+120);x.filter='none';
  x.save();x.filter='blur(8px)';x.fillStyle='#7a3f22';x.beginPath();x.moveTo(1370,710);x.lineTo(2020,625);x.lineTo(2020,1080);x.lineTo(1370,1080);x.fill();
  x.fillStyle='#d2a676';x.beginPath();x.moveTo(1405,733);x.lineTo(1990,660);x.lineTo(1990,1020);x.lineTo(1405,1065);x.fill();
  x.strokeStyle='rgba(90,50,25,.25)';x.lineWidth=3;for(let y=780;y<1060;y+=47){x.beginPath();x.moveTo(1410,y);x.lineTo(1990,y-72);x.stroke();}
  x.fillStyle='#2f4a78';x.beginPath();x.moveTo(1330,1010);x.lineTo(1990,938);x.lineTo(2020,1080);x.lineTo(1330,1080);x.fill();
  x.restore();return ROOM=c;
}
function crane(t){
  CRANE ||= makeCrane(1.35,'plain');
  const c=canvas(W,H),x=c.getContext('2d'),sway=.012*Math.sin(t*1.3)+.006*Math.sin(t*2.7);
  x.filter='blur(7px)';x.save();x.translate(1730,870);x.scale(-1.18,-1.18);
  const pose=cranePoseOf(NECK_UP,{mode:'stand'},sway,1);drawPuppet(x,CRANE,pose,'r');x.restore();
  return c;
}
function light(t){
  const f=1+.04*Math.sin((t+8)*11)+.03*Math.sin((t+8)*23);
  return {ambient:[.03,.026,.03],lights:[
    // Reverse close-up: S12's offscreen lamp now falls from frame right/front.
    {x:1750,y:560,r:2650*f,color:[1,.64,.32],i:1.35,falloff:1.5},
    {x:1450,y:820,r:1100,color:[1,.70,.42],i:.22*f,falloff:1.6},
    // Weak colored transmission catches the near cheek while she looks at the crane.
    {x:920+8*Math.sin(t*1.3),y:570,r:135,color:[1,.22,.12],i:.10*f,falloff:1.7},
    {x:850+6*Math.sin(t*1.3),y:650,r:120,color:[.36,.75,.28],i:.055*f,falloff:1.7},
  ],exposure:1,vignette:.35,grain:5};
}
export async function renderFrame(ctx,t,w,h){
  const im=await character(t),bg=await room(),k=w/W;
  const albedo=canvas(w,h),x=albedo.getContext('2d');x.imageSmoothingQuality='high';x.scale(k,k);x.drawImage(bg,0,0);
  x.save();x.translate(PLACEMENT.x,PLACEMENT.y);x.scale(PLACEMENT.scale,PLACEMENT.scale);x.drawImage(im,0,0);x.restore();
  x.drawImage(crane(t),0,0);const L=light(t);
  return renderPaint(ctx,t,w,h,{bg:albedo,size:[w,h],light:()=>({...L,lights:L.lights.map(l=>({...l,x:l.x*k,y:l.y*k,r:l.r*k}))}),glow:()=>[],cam:()=>({x:w/2,y:h/2,fit:1})});
}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
