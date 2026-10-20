import { renderPreparation } from './s29_lamp.js';
// S29 · 收（12 秒）。候选镜头，尚未写入 EDL。
// script-v3：手机留在竹席、线仍插着；小满左手始终保留乌龟签。
// 0–4.8 收布近景，4.8 切祖孙同框，5.5 与既有开机音同步亮锁屏，8.1 开始转看奶奶。
// 奶奶图只能承担已包住皮影、最后收拢布瓣的一段；不冒称折鹤颈/逐件收偶/转身吹灯已完成。
// 原件：anim_29_grandma_wrap d794f131…；xiaoman A f5596f90…（均经静图独审有限采用）。
import { renderPaint, loadImg } from '../paintshot.js';
import { makeTurtle, turtlePose } from '../../lamp/turtle.js';
import { drawPuppet, solve, pointOn } from '../../puppet.js';

export const DURATION = 12;
const BW = 1672, BH = 941, SAMPLE = 2;
const smooth = (a, b, t) => { const u = Math.max(0, Math.min(1, (t - a) / (b - a))); return u * u * (3 - 2 * u); };
export const TIMING = { wider: 4.8, boot: 5.5, turnStart: 8.1, turnEnd: 8.42 };
// Full original canvases are retained: scales use anatomical height, not equal source-canvas size.
// Grandma is at the east opening of the existing S14 sheet; girl stays on the mat's east end.
export const PLACEMENT = {
  grandma: { x: 790, y: 315, sc: 0.235 },
  xiaoman: { x: 470, y: 420, sc: 0.19 },
  phone: { x: 665, y: 681, w: 57, h: 27, rot: -0.12 },
};
const GM = PLACEMENT.grandma, XM = PLACEMENT.xiaoman, PH = PLACEMENT.phone;
const canv = (w, h) => new OffscreenCanvas(w, h);
const path = (x, points) => { x.beginPath(); points.forEach(([px, py], i) => i ? x.lineTo(px, py) : x.moveTo(px, py)); x.closePath(); };
let ASSETS;
async function assets() {
  if (ASSETS) return ASSETS;
  const [grandma, girl] = await Promise.all([loadImg('/assets/chars/g29_wrap.png'), loadImg('/assets/chars/x29_look_a.png')]);
  if (!grandma || !girl) throw Error('S29 requires the reviewed grandma and Xiaoman A derived layers.');
  // B will be installed as an isolated head/neck layer, never a second whole-body dissolve.
  const headB = await loadImg('/assets/chars/x29_head_b.png');
  if(!headB)throw Error('S29 requires the reviewed B head/neck derived layer.');
  const headA = canv(1024,1536), hx = headA.getContext('2d'); hx.save(); path(hx, HEAD_A); hx.clip(); hx.drawImage(girl,0,0); hx.restore();
  return ASSETS = { grandma, girl, headA, headB };
}

// A continuous displacement field carries fingers, wrist and the actual printed cloth together.
// The lower package, thighs, stool, shoes and face stay fixed; no rigid whole-person jiggle.
export function clothDisplacement(px, py, t) {
  const gather = smooth(0.9, 2.2, t), settle = smooth(2.25, 3.8, t);
  const nudge = Math.sin(Math.PI * smooth(2.45, 3.2, t));
  const v = Math.max(0, 1 - Math.abs(py - 720) / 165);
  const l = Math.exp(-(((px - 535) / 132) ** 2)) * v;
  const r = Math.exp(-(((px - 768) / 115) ** 2)) * v;
  return [l * (11 * gather - 3 * settle) - r * (28 * gather - 5 * settle), (l + r) * (10 * gather + 6 * settle + 2 * nudge)];
}
// Triangle texture mapping only touches the hand/cloth band. Every edge uses one shared field.
function triangle(x, im, src, dst) {
  const [a, b, c] = src, [A, B, C] = dst;
  const det = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1]);
  const m11 = ((B[0] - A[0]) * (c[1] - a[1]) - (C[0] - A[0]) * (b[1] - a[1])) / det;
  const m21 = ((C[0] - A[0]) * (b[0] - a[0]) - (B[0] - A[0]) * (c[0] - a[0])) / det;
  const m12 = ((B[1] - A[1]) * (c[1] - a[1]) - (C[1] - A[1]) * (b[1] - a[1])) / det;
  const m22 = ((C[1] - A[1]) * (b[0] - a[0]) - (B[1] - A[1]) * (c[0] - a[0])) / det;
  // A slight clip overlap prevents Canvas2D antialias cracks between adjacent triangles.
  const mid = [(A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3];
  const out = dst.map(p => { const dx = p[0] - mid[0], dy = p[1] - mid[1], d = Math.hypot(dx, dy); return [p[0] + dx / d * 0.55, p[1] + dy / d * 0.55]; });
  x.save(); path(x, out); x.clip(); x.transform(m11, m12, m21, m22, A[0] - m11 * a[0] - m21 * a[1], A[1] - m12 * a[0] - m22 * a[1]); x.drawImage(im, 0, 0); x.restore();
}
function grandmaLayer(im, t) {
  const c = canv(1024, 1536), x = c.getContext('2d');
  const top = 555, bottom = 885;
  x.drawImage(im, 0, 0, 1024, top, 0, 0, 1024, top);
  x.drawImage(im, 0, bottom, 1024, 1536 - bottom, 0, bottom, 1024, 1536 - bottom);
  const transform = p => { const d = clothDisplacement(...p, t); return [p[0] + d[0], p[1] + d[1]]; };
  for (let y = top; y < bottom; y += 22) for (let xx = 0; xx < 1024; xx += 32) {
    const xe = Math.min(1024, xx + 32), ye = Math.min(bottom, y + 22);
    const a = [xx, y], b = [xe, y], c0 = [xe, ye], d = [xx, ye];
    for (const tr of [[a, b, c0], [a, c0, d]]) triangle(x, im, tr, tr.map(transform));
  }
  return c;
}

// The mask boundary runs inside the white collar, while retaining the shoulder/sleeve pixels.
const HEAD_A = [[180, 65], [860, 65], [860, 665], [600, 665], [592, 617], [573, 601], [552, 584], [543, 607], [536, 640], [518, 643], [490, 631], [464, 613], [439, 585], [424, 559], [412, 558], [388, 575], [367, 599], [351, 627], [180, 627]];
function girlLayer(A, t) {
  if (!A.headB || t <= TIMING.turnStart) return A.girl;
  const c = canv(1024,1536), x = c.getContext('2d'); x.drawImage(A.girl,0,0);
  x.save(); x.globalCompositeOperation='destination-out'; path(x,HEAD_A); x.fill(); x.restore();
  const k=smooth(TIMING.turnStart,TIMING.turnEnd,t);
  // A short two-pose turn: no face mesh or head dissolve. The actual approved
  // B pose supplies the lifted jaw/eyes; a small rigid anticipation/settle keeps
  // the hair, skull and face coherent. The A collar remains the foreground seam.
  const before=k<.5, p=before?k*2:(1-k)*2;
  const head=before?A.headA:A.headB, angle=before?-.035*p:.025*p;
  x.save();x.translate(515,625);x.rotate(angle);x.translate(-515,-625+(before?-2:2)*p);x.drawImage(head,0,0);x.restore();
  // Reapply the original A collar only; shoulder, hands, rod and all lower-body pixels never change.
  const collar=[[[420,559],[431,574],[454,600],[483,625],[511,639],[529,642],[539,660],[534,678],[520,691],[502,695],[482,689],[455,675],[425,650],[398,622],[367,599],[389,579]],[[545,589],[558,597],[580,607],[595,634],[592,664],[580,686],[566,689],[553,685],[540,669],[531,647],[539,619]]];
  for(const poly of collar){x.save();path(x,poly);x.clip();x.drawImage(A.girl,0,0);x.restore();}
  return c;
}

// S14's same wire, sheet bounds, clothespins and lamp center are retained after power returns.
function stage(t) {
  const c = canv(BW, BH), x = c.getContext('2d');
  const top = px => 268 - 18 * (px - 328) / 577 + 14 * Math.sin(Math.PI * (px - 328) / 577);
  const bottom = px => 505 + 1.8 * Math.sin((px - 392) / 92 + t * 2.3);
  const p = new Path2D(); p.moveTo(392, top(392));
  for (let px = 392; px <= 842; px += 9) p.lineTo(px, top(px));
  for (let px = 842; px >= 392; px -= 9) p.lineTo(px, bottom(px)); p.closePath();
  x.fillStyle = '#e8e8de'; x.fill(p); x.save(); x.clip(p);
  for (let px = 392; px < 842; px += 38) { const g = x.createLinearGradient(px, 0, px + 38, 0); g.addColorStop(0, 'rgba(120,110,95,.1)'); g.addColorStop(.5, 'rgba(255,255,250,.06)'); g.addColorStop(1, 'rgba(120,110,95,.1)'); x.fillStyle = g; x.fillRect(px, 250, 38, 260); }
  x.fillStyle = 'rgba(200,120,110,.35)'; for (let px = 406; px < 842; px += 28) { x.beginPath(); x.arc(px, bottom(px) - 14, 4, 0, 7); x.fill(); }
  // The burning lamp remains behind the sheet; daylight overwhelms most of its warmth.
  const glow = x.createRadialGradient(600, 330, 5, 600, 370, 180); glow.addColorStop(0, 'rgba(255,219,149,.2)'); glow.addColorStop(1, 'rgba(255,219,149,0)'); x.fillStyle = glow; x.fillRect(392, 250, 450, 260);
  x.restore(); x.strokeStyle = 'rgba(62,42,30,.6)'; x.lineWidth = 1.8; x.stroke(p);
  for (const u of [.12,.5,.88]) { const px = 392 + 450 * u; x.fillStyle = '#c99a5c'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 1.5; x.beginPath(); x.roundRect(px - 4, top(px) - 14, 8, 26, 2); x.fill(); x.stroke(); }
  return c;
}
let GROUND;
function ground() {
  if (GROUND) return GROUND;
  const c = canv(BW, BH), x = c.getContext('2d');
  x.fillStyle = 'rgba(38,29,22,.26)'; x.filter = 'blur(3px)';
  for (const [px,py,rx,ry] of [[GM.x+140,GM.y+337,31,4],[GM.x+193,GM.y+320,28,4],[GM.x+40,GM.y+297,10,3],[GM.x+85,GM.y+315,10,3],[XM.x+117,XM.y+251,59,5],[XM.x+62,XM.y+249,16,3],[XM.x+30,XM.y+244,15,3],[PH.x,PH.y+3,31,5]]) { x.beginPath(); x.ellipse(px,py,rx,ry,0,0,7); x.fill(); }
  x.filter = 'none';
  // A few old bean shells remain at the mat's edge, scaled to the native room plane.
  for (const [px,py,a] of [[754,703,.3],[721,709,-.6],[772,681,.6],[792,715,-.2],[729,675,.9]]) { x.save(); x.translate(px,py); x.rotate(a); x.fillStyle='#7d934b';x.strokeStyle='#586338';x.lineWidth=.6;x.beginPath();x.ellipse(0,0,6,1.8,0,0,7);x.fill();x.stroke();x.restore(); }
  return GROUND = c;
}
function phone(t, screenOnly = false) {
  const c = canv(BW, BH), x = c.getContext('2d');
  if (!screenOnly) {
    x.lineCap='round';x.strokeStyle='#817c6e';x.lineWidth=2.6;x.beginPath();x.moveTo(PH.x-32,PH.y+3);x.bezierCurveTo(490,690,320,668,151,671);x.bezierCurveTo(72,670,33,639,34,604);x.stroke();
    x.strokeStyle='#e2e1d7';x.lineWidth=1.65;x.stroke();
  }
  x.translate(PH.x,PH.y);x.rotate(PH.rot);
  if (!screenOnly) {
    x.fillStyle='#e9e8df';x.strokeStyle='#423f38';x.lineWidth=.6;x.beginPath();x.roundRect(-PH.w/2-4,-1,5,3.5,.8);x.fill();x.stroke();
    x.fillStyle='#26282c';x.strokeStyle='#141516';x.lineWidth=1;x.beginPath();x.roundRect(-PH.w/2,-PH.h/2,PH.w,PH.h,4);x.fill();x.stroke();
  }
  x.beginPath();x.roundRect(-PH.w/2+2,-PH.h/2+1.8,PH.w-4,PH.h-3.6,2.6);x.fillStyle=t<TIMING.boot?'#090c10':'#577a9d';x.fill();
  if(t<TIMING.boot){x.strokeStyle='#d6e0d8';x.lineWidth=.8;x.strokeRect(-5,-3.3,10,4.8);x.fillStyle='#82bc7f';x.fillRect(-4,-2.3,1.1,2.8);}
  else {
    const g=x.createLinearGradient(0,-10,0,10);g.addColorStop(0,'#41688a');g.addColorStop(1,'#94b9c6');x.fillStyle=g;x.fill();
    x.fillStyle='#f0f6f7';x.textAlign='center';x.font='500 8px "Noto Sans SC"';x.fillText('22:40',0,0.4);
    x.font='2.8px "Noto Sans SC"';x.fillText('星期六  ·  充电中 2%',0,6.2);
    x.fillStyle='#d0e7db';x.fillRect(19,-9,4,2);x.fillStyle='#71bd78';x.fillRect(19.3,-8.7,.7,1.4);
  }
  return c;
}
let TURTLE;
function turtleLayer() {
  const c=canv(BW,BH),x=c.getContext('2d'); TURTLE ||= makeTurtle();
  const pose=turtlePose(0,{facing:-1,walk:0,neckOut:.35,rootAngle:0}),TK=.68;
  // Exact extrapolation of A's painted short rod: (634,1012) -> (829,906).
  const a=[810,916.33], end=[1120,747.85];
  x.translate(XM.x,XM.y);x.scale(XM.sc,XM.sc);
  x.strokeStyle='#48351f';x.lineWidth=12;x.lineCap='round';x.beginPath();x.moveTo(...a);x.lineTo(...end);x.stroke();
  x.strokeStyle='#ba9059';x.lineWidth=8;x.stroke();
  const pm=pointOn(TURTLE,solve(TURTLE,pose),'shell',[0,40]);
  x.translate(end[0]-pm[0]*TK,end[1]+pm[1]*TK);x.scale(TK,-TK);drawPuppet(x,TURTLE,pose,'r');
  return c;
}
const shot = {
  bg:'bg_01_room_wide',size:[BW*SAMPLE,BH*SAMPLE],
  layers:async t=>{const A=await assets();return [
    {img:ground(),x:0,y:0,sc:1},{img:phone(t),x:0,y:0,sc:1},
    {img:grandmaLayer(A.grandma,t),...GM},
    {img:stage(t),x:0,y:0,sc:1},
    {img:turtleLayer(),x:0,y:0,sc:1},{img:girlLayer(A,t),...XM},
  ].map(L=>({...L,x:L.x*SAMPLE,y:L.y*SAMPLE,sc:L.sc*SAMPLE}));},
  light:t=>{const L={ambient:[.65,.68,.74],lights:[{x:780,y:60,r:1500,color:[.94,.97,1],i:.32,falloff:1.4},{x:300,y:440,r:700,color:[.55,.7,1],i:.2+.03*Math.sin(t*7),falloff:1.6},{x:600,y:350,r:450,color:[1,.65,.32],i:.09,falloff:2}],exposure:1,vignette:.16,grain:3};L.lights=L.lights.map(l=>({...l,x:l.x*SAMPLE,y:l.y*SAMPLE,r:l.r*SAMPLE}));return L;},
  glow:t=>t>=TIMING.boot?[{x:PH.x*SAMPLE,y:PH.y*SAMPLE,r:30*SAMPLE,color:[153,195,225],a:.08,core:.2}]:[],
  emit:(x,t)=>{x.scale(SAMPLE,SAMPLE);x.drawImage(phone(t,true),0,0);},
  cam:t=>t<TIMING.wider?{x:950*SAMPLE,y:450*SAMPLE,fit:BW/450}:{x:745*SAMPLE,y:519*SAMPLE,fit:BW/(746-10*smooth(8.7,12,t))},
};
// Compose the flat cards directly at the requested camera resolution, then use the
// project's unchanged linear-light paint renderer. This avoids first shrinking a
// 1536px portrait to a tiny room card and enlarging it again for the hand close-up.
// Light centers/radii and emission receive exactly the same camera transform.
export async function renderFrame(ctx,t,w,h){
  t=Math.max(0,Math.min(DURATION,t));
  if(t>=10)return renderPreparation(ctx,t-10,w,h);
  const camera=shot.cam(t), k=camera.fit*w/shot.size[0];
  const ox=w/2-camera.x*k, oy=h/2-camera.y*k;
  const albedo=canv(w,h), ax=albedo.getContext('2d');
  ax.imageSmoothingQuality='high';ax.setTransform(k,0,0,k,ox,oy);
  const bg=await loadImg(shot.bg);ax.drawImage(bg,0,0,...shot.size);
  for(const L of await shot.layers(t)){
    ax.save();ax.globalAlpha=L.alpha??1;ax.translate(L.x,L.y);ax.scale(L.sc,L.sc);ax.drawImage(L.img,0,0);ax.restore();
  }
  const light=shot.light(t), map=L=>({...L,x:L.x*k+ox,y:L.y*k+oy,r:L.r*k});
  const local={bg:albedo,size:[w,h],light:()=>({...light,lights:light.lights.map(map)}),glow:()=>shot.glow(t).map(map),
    emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);shot.emit(x,t);x.restore();},
    cam:()=>({x:w/2,y:h/2,fit:1})};
  return renderPaint(ctx,t,w,h,local);
}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}

