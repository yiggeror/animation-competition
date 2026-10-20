// Existing S14 tail drawings in the original painted wide shot. No S15 edits.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
let rows;
async function exposure(f){rows??=await(await fetch(new URL('./published_child_tail_exposures.json',import.meta.url))).json();return rows.find(e=>f>=e.frame&&f<=e.through);}
async function image(path){const im=await loadImg(path);if(!im)throw Error('Missing S14 tail source '+path);return im;}
export const CHILD_TO_ROOM=Object.freeze({sc:.16,x:453.6,y:458.32,floor:1198,roomFloor:650,seat:[540,591.92]});
const GM={sc:.335,x:355,y:175},LAMP=[600,330];
const COMPLETE_SHEET='/collab/reviews/20261019_2247_s14_second_clip_six_locked/grandma_fall_inputs/G027_upper_contact_repair/G027_complete_sheet_whole_registered.png';
const fl=t=>1+.05*Math.sin(t*9.3)+.03*Math.sin(t*17.7);
export function originalWideCamera(t){const u=Math.min(1,Math.max(0,t/10)),k=u*u*(3-2*u);return{x:640+20*k,y:430,fit:1.45+.08*k};}
export async function tailBinding(f,forcedExposure=null){
 const e=forcedExposure??await exposure(f);if(!e)return null;const d=e.nativeToCommonTranslation,s=e.nativeToCommonScale??1;
 return{frame:f,drawing:e.id,source:e.path,sourceSHA256:e.sha256,shot:'originalPaintWideCameraAfterHang',wholeDrawingTransform:{sc:CHILD_TO_ROOM.sc*s,x:CHILD_TO_ROOM.x+d[0]*CHILD_TO_ROOM.sc,y:CHILD_TO_ROOM.y+d[1]*CHILD_TO_ROOM.sc},sourceFloor:(CHILD_TO_ROOM.floor-d[1])/s,curtainLit:f>=132,lightEventFrame:132,diagnosticExposureOnly:e.diagnosticExposureOnly??false};
}
export async function renderTail(ctx,t,W,H,forcedExposure=null){
 const f=Math.floor(t*24+1e-6),e=forcedExposure??await exposure(f);if(!e)return false;
 const [bg,cloth,child,clothMask]=await Promise.all([image('/assets/paint/bg_01_room_wide.png'),image(new URL('./G095_FIXED_DRAWN_SHEET_AND_TWO_PEGS_RGBA.png',import.meta.url).href),image(e.path),image(COMPLETE_SHEET)]);
 const binding=await tailBinding(f,e);
 // The post-hang material/light descriptions retain the original S14 pass.
 // Curtain gain starts at the approved5.5-second return, not old5.0 seconds.
 const gain=f>=132?1:0;
 await renderPaint(ctx,t,W,H,{
  bg,size:[1672,941],
  layers:()=>[{img:cloth,...GM},{img:child,...binding.wholeDrawingTransform,contact:{a:.4,blur:4,sy:-.07,skew:.4,base:binding.sourceFloor}}],
  light:()=>({ambient:[.022,.026,.044],lights:[
   {x:520,y:520,r:900*fl(t),color:[1,.62,.30],i:.75*(1-gain),falloff:2},
   {x:LAMP[0],y:LAMP[1]+60,r:1300*fl(t),color:[1,.68,.38],i:.55*gain,falloff:1.8}
  ],exposure:1,vignette:.5,grain:7}),glow:()=>[],
  emit:x=>{
   if(!gain)return;
   const c=new OffscreenCanvas(1672,941),z=c.getContext('2d'),g=z.createRadialGradient(LAMP[0],LAMP[1],10,LAMP[0],LAMP[1]+40,420);
   g.addColorStop(0,`rgba(255,236,190,${.95*gain})`);g.addColorStop(.15,`rgba(255,214,150,${.8*gain})`);g.addColorStop(1,`rgba(220,150,80,${.35*gain})`);
   z.fillStyle=g;z.fillRect(0,0,1672,941);z.globalCompositeOperation='destination-in';z.save();z.translate(GM.x,GM.y);z.scale(GM.sc,GM.sc);z.drawImage(clothMask,0,0);z.restore();
   x.globalCompositeOperation='source-over';x.globalAlpha=fl(t)*.97;x.drawImage(c,0,0);x.globalAlpha=1;
  },cam:()=>originalWideCamera(t)
 });return true;
}
