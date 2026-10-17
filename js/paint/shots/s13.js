// S13 · 木箱旁的近景，5 秒。A 好奇凝视一拍，察觉被看，短转开，假哈欠。
// Reviewed A torso/collar stays fixed; B contributes aligned head/neck/braids only.
// No whole-picture dissolve, face mesh, new hand or newly generated pose.
import { renderPaint, loadImg } from '../paintshot.js';
import { makeCrane } from '../../lamp/crane.js';
import { cranePoseOf, NECK_UP } from '../../lamp/choreo.js';
import { drawPuppet } from '../../puppet.js';
export const DURATION = 5;
const W=1920,H=1080,SW=1024,SH=1536;
const smooth=(a,b,t)=>{const k=Math.max(0,Math.min(1,(t-a)/(b-a)));return k*k*(3-2*k);};
export const PLACEMENT={x:330,y:-30,scale:.85};
export const TIMING={curiousEnd:1,turnStart:1.2,turnEnd:1.55,yawnPeak:2.25,yawnClose:4.25};
const PIVOT=[530,1045],MOUTH=[370,827];
export function state(t){
  const k=smooth(TIMING.turnStart,TIMING.turnEnd,t),pose=k<.5?'A':'B';
  const edge=pose==='A'?k*2:(1-k)*2;
  const notice=.014*smooth(1,1.2,t);
  const yawn=smooth(1.45,2.25,t)*(1-smooth(3.05,4.25,t));
  const angle=pose==='A'?notice+.022*edge:-.026*edge-.014*yawn;
  const dy=pose==='A'?2*edge:3*edge-3*yawn;
  return {t,pose,turn:k,angle,dy,mouthScale:.18+.82*yawn,pivot:PIVOT,placement:PLACEMENT,
    sourceLowerCutShotY:PLACEMENT.y+1465*PLACEMENT.scale};
}
const canvas=(w,h)=>new OffscreenCanvas(w,h);
let ASSETS;
async function assets(){
  if(ASSETS)return ASSETS;
  const names=['body_a','head_a','head_b','mouth_b'];
  const images=await Promise.all(names.map(n=>loadImg('/assets/chars/x13_'+n+'.png')));
  if(images.some(x=>!x))throw Error('S13 requires the reviewed A/B derived layers.');
  return ASSETS=Object.fromEntries(names.map((n,i)=>[n,images[i]]));
}
function girl(A,s){
  const c=canvas(SW,SH),x=c.getContext('2d');
  // Head is rigid around the neck root; A's unchanged collar is reapplied in front.
  x.save();x.translate(PIVOT[0],PIVOT[1]+s.dy);x.rotate(s.angle);x.translate(-PIVOT[0],-PIVOT[1]);
  x.drawImage(s.pose==='A'?A.head_a:A.head_b,0,0);
  if(s.pose==='B'){
    // Only the original mouth aperture changes height; skull, eyes, nose and jaw do not deform.
    x.save();x.translate(...MOUTH);x.scale(1,s.mouthScale);x.drawImage(A.mouth_b,-MOUTH[0],-MOUTH[1]);x.restore();
  }
  x.restore();x.drawImage(A.body_a,0,0);return c;
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
  const s=state(t),A=await assets(),bg=await room(),k=w/W;
  // Compose at delivery resolution before the unchanged linear-light renderer.
  const albedo=canvas(w,h),x=albedo.getContext('2d');x.imageSmoothingQuality='high';x.scale(k,k);x.drawImage(bg,0,0);
  x.save();x.translate(PLACEMENT.x,PLACEMENT.y);x.scale(PLACEMENT.scale,PLACEMENT.scale);x.drawImage(girl(A,s),0,0);x.restore();
  x.drawImage(crane(t),0,0);const L=light(t);
  return renderPaint(ctx,t,w,h,{bg:albedo,size:[w,h],light:()=>({...L,lights:L.lights.map(l=>({...l,x:l.x*k,y:l.y*k,r:l.r*k}))}),glow:()=>[],cam:()=>({x:w/2,y:h/2,fit:1})});
}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
