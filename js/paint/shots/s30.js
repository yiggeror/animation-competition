import { renderFrozenHead } from './s29_lamp.js';
// S30: TV off first at 1.1 s, footsteps to door, then actual child pulling/releasing at 4.4–7.9 s.
// Approved v2 image layers only. Feet/body fixed; rigid arm segments share the cord anchor.
// Door-side local set uses unidentifiable wall/floor texture, not bg01's north back-room door.
// Script-v3 order: TV off before pulling the fluorescent switch; fan remains running.
import { renderPaint, loadImg } from '../paintshot.js';
export const DURATION = 12;
const W=1920,H=1080,IW=1024,IH=1536,LINE='#3e2a1e',T_OFF=6,T_RELEASE=6.125,T_TV_OFF=1.1,T_TV_END=1.65;
const smooth=(a,b,t)=>{const u=Math.max(0,Math.min(1,(t-a)/(b-a)));return u*u*(3-2*u);};
const lerp=(a,b,k)=>a+(b-a)*k, add=(a,b)=>[a[0]+b[0],a[1]+b[1]], sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const rot=(p,a)=>[p[0]*Math.cos(a)-p[1]*Math.sin(a),p[0]*Math.sin(a)+p[1]*Math.cos(a)], angle=v=>Math.atan2(v[1],v[0]);
// Source-space cuff pivot, elbow, wrist and grip. No segment scaling or body translation.
const SHOULDER=[645,418],ELBOW=[689,407],WRIST=[718,277],GRIP=[727,211];
const U0=sub(ELBOW,SHOULDER),F0=sub(GRIP,ELBOW),LU=Math.hypot(...U0),LF=Math.hypot(...F0);
const PERSON={x:500,y:50,scale:.62},toShot=p=>[PERSON.x+p[0]*PERSON.scale,PERSON.y+p[1]*PERSON.scale];
const FEET=[[465,1425],[607,1438]],WIDE_TOP=[toShot(GRIP)[0],-420],CLOSE_TOP=[1180,150];
export function state(t){
  const pull=smooth(5.5,5.95,t),recover=smooth(6.2,7.65,t);let g=[GRIP[0]+2*pull,GRIP[1]+40*pull];
  if(recover>0){const a=sub([GRIP[0]+2,GRIP[1]+40],SHOULDER),b=sub([650,650],SHOULDER),th=lerp(angle(a),angle(b),recover),d=lerp(Math.hypot(...a),Math.hypot(...b),recover);g=add(SHOULDER,[Math.cos(th)*d,Math.sin(th)*d]);}
  const v=sub(g,SHOULDER),d=Math.hypot(...v),ac=Math.acos(Math.max(-1,Math.min(1,(LU*LU+d*d-LF*LF)/(2*LU*d)))),ua=angle(v)+ac,e=add(SHOULDER,[LU*Math.cos(ua),LU*Math.sin(ua)]);
  const uRot=ua-angle(U0),fRot=angle(sub(g,e))-angle(F0),fp=p=>add(e,rot(sub(p,ELBOW),fRot));
  const holding=t<T_RELEASE,dt=Math.max(0,t-T_RELEASE),recoil=holding?pull:Math.exp(-dt*8)*Math.cos(dt*18),swing=holding?0:Math.exp(-dt*1.25)*Math.sin(dt*6.5)*10;
  const tailStart=holding?fp([744,276]):[GRIP[0]+swing,GRIP[1]+40*recoil],tailEnd=holding?fp([744,321]):[GRIP[0]+swing,GRIP[1]+109+40*recoil];
  return {t,pull,recover,holding,view:t<T_TV_END?'tv':t>=4.4&&t<7.9?'person':'cord',shoulder:SHOULDER,elbow:e,wrist:fp(WRIST),grip:g,uRot,fRot,ropeGrip:holding?[...g]:null,tailStart,tailEnd,recoil,swing,feet:FEET.map(toShot),lit:t<T_OFF,cue:5.95,person:PERSON};
}
const UPPER=[[640,390],[670,376],[690,374],[710,384],[718,404],[713,420],[690,438],[657,448],[660,432],[658,425],[654,422],[657,416],[654,405],[648,397],[641,396]];
const FORE=[[667,397],[671,372],[692,286],[692,228],[704,205],[716,188],[742,188],[756,212],[759,249],[744,275],[731,355],[722,394],[711,421],[691,437],[671,422]];
const ARM_CUT=[[640,390],[665,379],[682,327],[694,278],[694,229],[704,205],[716,188],[742,188],[757,214],[759,250],[743,278],[728,361],[721,394],[711,421],[686,439],[657,448],[660,432],[658,425],[654,422],[657,416],[654,405],[648,397],[641,396]];
const OPEN_HAND=[[316,791],[347,805],[343,841],[332,875],[331,897],[314,893],[299,877],[294,848],[308,815]];
const path=(x,p)=>{x.beginPath();p.forEach(([a,b],i)=>i?x.lineTo(a,b):x.moveTo(a,b));x.closePath();};
function piece(im,keep,erase){const c=new OffscreenCanvas(IW,IH),x=c.getContext('2d');if(keep){path(x,keep);x.clip();}x.drawImage(im,0,0);if(erase){x.globalCompositeOperation='destination-out';path(x,erase);x.fill();}return c;}
let PARTS=null;
async function parts(){
  if(PARTS)return PARTS;const im=await loadImg('/assets/chars/x30_pull_cord.png');if(!im)throw Error('S30 requires x30_pull_cord.png from approved v2');
  const clean=piece(im),x=clean.getContext('2d');x.clearRect(719,0,18,188);x.clearRect(733,278,32,70);
  const fore=piece(clean,FORE),foreOpen=piece(clean,FORE);foreOpen.getContext('2d').clearRect(0,0,IW,274);
  // A small source-texture overlap closes the elbow at large rotations.
  // It samples existing skin; it adds no painted anatomy or segment scaling.
  const joint=new OffscreenCanvas(IW,IH),jx=joint.getContext('2d');jx.beginPath();jx.arc(...ELBOW,19,0,Math.PI*2);jx.clip();jx.drawImage(clean,5,7);
  return PARTS={body:piece(clean,null,ARM_CUT),upper:piece(clean,UPPER),joint,fore,foreOpen,openHand:piece(clean,OPEN_HAND)};
}
const upperTransform=(x,s)=>{x.translate(...SHOULDER);x.rotate(s.uRot);x.translate(-SHOULDER[0],-SHOULDER[1]);};
const foreTransform=(x,s)=>{x.translate(...s.elbow);x.rotate(s.fRot);x.translate(-ELBOW[0],-ELBOW[1]);};
function strokeCord(x,top,end,bend=0,width=5){x.lineCap='round';x.strokeStyle='rgba(62,42,30,.75)';x.lineWidth=width+2;x.beginPath();x.moveTo(...top);x.quadraticCurveTo((top[0]+end[0])/2+bend,(top[1]+end[1])/2,...end);x.stroke();x.strokeStyle='#e8e2cf';x.lineWidth=width;x.stroke();}
function knob(x,p,sc=1){x.save();x.translate(...p);x.scale(sc,sc);x.fillStyle='#d9c9a0';x.strokeStyle=LINE;x.lineWidth=2;x.beginPath();x.ellipse(0,10,8,14,0,0,7);x.fill();x.stroke();x.restore();}
function switchBox(x){const[cx,cy]=CLOSE_TOP;x.fillStyle='rgba(0,0,0,.2)';x.beginPath();x.ellipse(cx+10,cy+14,78,36,0,0,7);x.fill();x.fillStyle='#f1efe6';x.strokeStyle=LINE;x.lineWidth=4;x.beginPath();x.ellipse(cx,cy,74,32,0,0,7);x.fill();x.stroke();x.beginPath();x.roundRect(cx-52,cy-6,104,46,14);x.fill();x.stroke();}
function cordCloseup(t,s){const c=new OffscreenCanvas(W,H),x=c.getContext('2d');switchBox(x);const free=t>=T_RELEASE,fan=free?0:8*Math.sin(t*2.1)+3*Math.sin(t*5.3),end=[CLOSE_TOP[0]+(free?s.swing*3:fan),830+(free?s.recoil*65:0)];strokeCord(x,[CLOSE_TOP[0],CLOSE_TOP[1]+40],end,4,5);knob(x,end,1.7);return c;}
async function personLayer(s){
  const L=await parts(),c=new OffscreenCanvas(W,H),x=c.getContext('2d');
  x.fillStyle='rgba(45,29,20,.2)';for(const p of s.feet){x.beginPath();x.ellipse(p[0]-8,p[1]+2,21,4,0,0,7);x.fill();}
  const g=toShot(s.grip),ts=toShot(s.tailStart),te=toShot(s.tailEnd);strokeCord(x,WIDE_TOP,s.holding?g:te,s.holding?0:s.swing*.25,3);if(s.holding)strokeCord(x,ts,te,0,3);knob(x,te,.72);
  x.save();x.translate(PERSON.x,PERSON.y);x.scale(PERSON.scale,PERSON.scale);
  // Cuff covers the source overlap. Arm texture is rotated, never painted or stretched.
  x.save();upperTransform(x,s);x.drawImage(L.upper,0,0);x.restore();x.drawImage(L.body,0,0);
  x.save();x.translate(s.elbow[0]-ELBOW[0],s.elbow[1]-ELBOW[1]);x.drawImage(L.joint,0,0);x.restore();
  x.save();foreTransform(x,s);x.drawImage(s.holding?L.fore:L.foreOpen,0,0);
  if(!s.holding){ // Mirrored relaxed hand from the same source, not a procedural replacement.
    x.translate(...WRIST);x.scale(1.12,-1.12);x.drawImage(L.openHand,-329,-805);
  }x.restore();x.restore();return c;
}
let BGS=null;
async function backgrounds(){
  if(BGS)return BGS;const im=await loadImg('bg_01_room_wide');if(!im)throw Error('S30 requires bg_01_room_wide');
  const wall=new OffscreenCanvas(W,H),wx=wall.getContext('2d');
  // Texture-only wall strip: excludes every recognizable door, cupboard and TV.
  wx.filter='blur(9px)';wx.drawImage(im,378,295,65,270,-30,-20,W+60,H+40);wx.filter='none';
  const wide=new OffscreenCanvas(W,H),x=wide.getContext('2d');x.drawImage(wall,0,0);x.filter='blur(3px)';x.drawImage(im,820,620,300,230,-20,875,W+40,245);x.filter='none';
  x.fillStyle='rgba(65,52,40,.16)';x.fillRect(0,873,W,7);x.drawImage(im,638,310,18,225,1130,0,62,875);x.fillStyle='rgba(48,32,22,.24)';x.fillRect(1192,0,16,875);
  const close=new OffscreenCanvas(W,H),cx=close.getContext('2d');cx.drawImage(wall,0,0);cx.strokeStyle='#efeee8';cx.lineWidth=9;cx.beginPath();cx.moveTo(-20,120);cx.quadraticCurveTo(600,150,CLOSE_TOP[0]-40,CLOSE_TOP[1]-10);cx.stroke();
  return BGS={wide,close};
}
const tv=t=>t<T_TV_OFF?.25+.1*Math.sin(t*7.1)+.06*Math.sin(t*13):0;
const shot={size:[W,H],layers:async t=>{const s=state(t);return[{img:s.view==='person'?await personLayer(s):cordCloseup(t,s),x:0,y:0,sc:1}];},
  light:t=>{const lit=t<T_OFF,warm=smooth(6.4,9,t),f=1+.04*Math.sin(t*11)+.03*Math.sin(t*23);return{ambient:lit?[.64,.67,.73]:[.03,.035,.06],lights:[{x:-300,y:700,r:1500,color:[.55,.7,1],i:tv(t),falloff:1.5},{x:2400,y:900,r:2600*f,color:[1,.62,.30],i:.75*warm,falloff:1.6}],exposure:1,vignette:lit?.3:.48,grain:lit?5:7};},glow:()=>[],
  cam:t=>state(t).view==='person'?{x:W/2,y:H/2,fit:1}:{x:W/2+30*smooth(0,4.4,t),y:H/2+20*smooth(0,4.4,t),fit:1+.06*smooth(0,4.4,t)}
};

// Reuse S04 original CRT/background drawing, with room lighting retained during the separate TV switch-off.
const TV = { src: [60, 320, 340, 191] };                 // 底图里取的范围（x, y, 宽, 高）
const k = W / TV.src[2];
const SCR = [[202, 365], [282, 367], [280, 472], [202, 472]].map(([x, y]) => [(x - TV.src[0]) * k, (y - TV.src[1]) * k]);
let TVBG = null;
async function tvBg() {
  if (TVBG) return TVBG;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(2px)'; x.drawImage(im, ...TV.src, 0, 0, W, TV.src[3] * k); x.filter = 'none';
  return (TVBG = c);
}
// 屏幕：动画片（天、太阳、一只跑来跑去的小东西），扫描线；断电后压成线 → 点 → 熄
function tvScreen(x, t) {
  const [a, b, c, d] = SCR, cx = (a[0] + b[0] + c[0] + d[0]) / 4, cy = (a[1] + b[1] + c[1] + d[1]) / 4;
  const sw = (b[0] - a[0] + c[0] - d[0]) / 2, sh = (d[1] - a[1] + c[1] - b[1]) / 2;
  const u = t - T_TV_OFF;
  let sy = 1, sx = 1, bright = 1, alpha = 1;
  if (u > 0) { sy = Math.max(0.006, 1 - u / 0.1); bright = 1 + 2 * Math.min(1, u / 0.1); if (u > 0.1) { sx = Math.max(0.012, 1 - (u - 0.1) / 0.14); } if (u > 0.24) alpha = Math.max(0, 1 - (u - 0.24) / 0.15); }
  if (alpha <= 0) return;
  x.save(); x.globalAlpha = alpha;
  x.beginPath(); x.roundRect(a[0] + 8, a[1] + 10, sw - 16, sh - 18, 46); x.clip();                 // 显像管玻璃是鼓的、圆角
  if (u > 0.1) x.globalCompositeOperation = 'lighter';
  x.translate(cx, cy); x.scale(sx, sy);
  if (u <= 0.1) {
    const g = x.createLinearGradient(0, -sh / 2, 0, sh / 2); g.addColorStop(0, '#5aa9e6'); g.addColorStop(0.65, '#9fd6f5'); g.addColorStop(0.66, '#7cc56a'); g.addColorStop(1, '#4e9a45');
    x.fillStyle = g; x.fillRect(-sw / 2, -sh / 2, sw, sh);
    x.fillStyle = '#ffe680'; x.beginPath(); x.arc(sw * 0.25, -sh * 0.25, sh * 0.1, 0, 7); x.fill();
    const px = -sw * 0.35 + ((t * 0.35) % 1) * sw * 0.7, hop = Math.abs(Math.sin(t * 7)) * sh * 0.08;
    x.fillStyle = '#ff8a3d'; x.beginPath(); x.ellipse(px, sh * 0.12 - hop, sw * 0.07, sh * 0.06, 0, 0, 7); x.fill();
    x.fillStyle = 'rgba(0,0,0,0.12)'; for (let yy = -sh / 2; yy < sh / 2; yy += 6) x.fillRect(-sw / 2, yy, sw, 2);   // 扫描线
    if (u > 0) { x.fillStyle = `rgba(255,255,255,${Math.min(1, u / 0.1)})`; x.fillRect(-sw / 2, -sh / 2, sw, sh); }
  } else {
    const r = Math.max(sw, sh) * 0.6, g = x.createRadialGradient(0, 0, 0, 0, 0, r); g.addColorStop(0, `rgba(255,255,255,${Math.min(1, bright)})`); g.addColorStop(0.15, 'rgba(220,235,255,0.9)'); g.addColorStop(1, 'rgba(160,190,255,0)');
    x.fillStyle = g; x.fillRect(-sw / 2, -sh / 2, sw, sh);
  }
  x.restore();
}
const tvInsert={size:[W,H],layers:async()=>[],
  light:t=>({ambient:[.64,.67,.72],lights:[{x:1030,y:560,r:1100,color:[.55,.7,1],i:t<T_TV_OFF?.35+.1*Math.sin(t*9):.35*(1-smooth(T_TV_OFF,T_TV_OFF+.25,t)),falloff:1.6}],exposure:1,vignette:.3,grain:5}),
  glow:()=>[],emit:(x,t)=>tvScreen(x,t),cam:()=>({x:W/2,y:520,fit:1.02})};

export async function renderFrame(ctx,t,w,h){if(t>=7.9)return renderFrozenHead(ctx,t,w,h);if(t<T_TV_END){tvInsert.bg=await tvBg();return renderPaint(ctx,t,w,h,tvInsert);}const b=await backgrounds();shot.bg=state(t).view==='person'?b.wide:b.close;return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
