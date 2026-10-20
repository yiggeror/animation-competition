// Scene functions extracted without numeric changes from actually rendered s29.js.
// Fixed source SHA256: 0aa013b4462457d0142c45e20ed806861a1450c69a60e9e39f01d1be2a6852f9.
// Later timing was re-frozen by the coordinator at23:25; later drawings are not integrated here.
// Only F036–071 is enabled. No old human warp, head switch, child puppet, or tail execution.
// Complete locked mother images already contain the real puppets and rods. Do not redraw them.
import {loadImg} from '../../paint/paintshot.js';
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
  // Same registered source-space shoe/stool contacts as the wide S29 compositor.
  const grandmaContacts = [[520,1500,138,14],[805,1450,135,12],[55,1348,30,8],[286,1435,34,9]]
    .map(([px,py,rx,ry])=>[GM.x+px*GM.sc,GM.y+py*GM.sc,rx*GM.sc,ry*GM.sc]);
  x.fillStyle = 'rgba(38,29,22,.38)'; x.filter = 'blur(1.5px)';
  for (const [px,py,rx,ry] of grandmaContacts) { x.beginPath(); x.ellipse(px,py,rx,ry,0,0,7); x.fill(); }
  x.fillStyle = 'rgba(38,29,22,.26)'; x.filter = 'blur(3px)';
  for (const [px,py,rx,ry] of [[XM.x+117,XM.y+251,59,5],[XM.x+62,XM.y+249,16,3],[XM.x+30,XM.y+244,15,3],[PH.x,PH.y+3,31,5]]) { x.beginPath(); x.ellipse(px,py,rx,ry,0,0,7); x.fill(); }
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
const shot = {
  bg:'bg_01_room_wide',size:[BW*SAMPLE,BH*SAMPLE],
  layers:async t=>{const girl=await loadImg('/assets/chars/x29_look_a.png');
    if(!girl)throw Error('Missing original source girl layer');
    // Slots 2 and 4 are intentionally never rendered by the prefix compositor.
    // Keep their placements to reproduce the cloud's exact oldGM registration.
    return [
      {img:ground(),x:0,y:0,sc:1},{img:phone(t),x:0,y:0,sc:1},
      {img:null,...GM},{img:stage(t),x:0,y:0,sc:1},
      {img:null,x:0,y:0,sc:1},{img:girl,...XM},
    ].map(L=>({...L,x:L.x*SAMPLE,y:L.y*SAMPLE,sc:L.sc*SAMPLE}));
  },
  light:t=>{const L={ambient:[.65,.68,.74],lights:[{x:780,y:60,r:1500,color:[.94,.97,1],i:.32,falloff:1.4},{x:300,y:440,r:700,color:[.55,.7,1],i:.2+.03*Math.sin(t*7),falloff:1.6},{x:600,y:350,r:450,color:[1,.65,.32],i:.09,falloff:2}],exposure:1,vignette:.16,grain:3};L.lights=L.lights.map(l=>({...l,x:l.x*SAMPLE,y:l.y*SAMPLE,r:l.r*SAMPLE}));return L;},
  glow:t=>t>=TIMING.boot?[{x:PH.x*SAMPLE,y:PH.y*SAMPLE,r:30*SAMPLE,color:[153,195,225],a:.08,core:.2}]:[],
  emit:(x,t)=>{x.scale(SAMPLE,SAMPLE);x.drawImage(phone(t,true),0,0);},
  cam:t=>t<TIMING.wider?{x:950*SAMPLE,y:450*SAMPLE,fit:BW/450}:{x:745*SAMPLE,y:519*SAMPLE,fit:BW/(746-10*smooth(8.7,12,t))},
};

export {shot as sourceShot};
