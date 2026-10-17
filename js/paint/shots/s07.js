// S07 candidate · 5 s. An editorial cut enters the LAST part of the flop;
// it does not claim to animate the missing prone/side/supine turn.
// A: shoulders finish settling on the mat, then the empty right palm fans.
// B: cut to grandma already at the cabinet; the reach is articulated.
// Walking, closing the fingers and carrying the lamp to S08 are NOT implemented.
// The cabinet action reaches the lamp base only; it is not a completed retrieval.
import { renderPaint, loadImg } from '../paintshot.js';
import { COIL, COILC } from './s01.js';
import { lamp as drawLamp, LX, LB } from '../../code/s08.js';
export const DURATION = 5;
const BW = 1672, BH = 941, CUT = 2.65;
const ss = (a, b, x) => { const u = Math.max(0, Math.min(1, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const mix = (a, b, k) => a + (b - a) * k;
const rot = (p, o, a) => { const c = Math.cos(a), s = Math.sin(a), dx = p[0] - o[0], dy = p[1] - o[1]; return [o[0] + c * dx - s * dy, o[1] + s * dx + c * dy]; };
const blend = (a, b, k) => [mix(a[0], b[0], k), mix(a[1], b[1], k)];
const canvas = (w, h) => new OffscreenCanvas(w, h);
const path = (x, poly) => { x.beginPath(); poly.forEach((p, i) => i ? x.lineTo(...p) : x.moveTo(...p)); x.closePath(); };
// Full native coordinates retained in both mattes; no cropped-image origin guesses.
const X = { x: 354, y: 515, sc: 0.225 };
const G = { x: 1142, y: 254, sc: 0.235 };
const ARM_X = [[1163,611],[1234,605],[1253,657],[1310,700],[1383,734],[1490,729],[1495,844],[1360,845],[1232,766],[1182,714],[1156,653]];
const ARM_G = [[582,351],[604,293],[615,235],[649,157],[672,69],[713,29],[763,39],[767,112],[715,163],[698,254],[664,343],[640,404],[612,389]];
let parts;
function isolate(im, poly) {
  const arm = canvas(im.width, im.height), ax = arm.getContext('2d');
  path(ax, poly); ax.clip(); ax.drawImage(im, 0, 0);
  const body = canvas(im.width, im.height), bx = body.getContext('2d');
  bx.drawImage(im, 0, 0); bx.globalCompositeOperation = 'destination-out'; path(bx, poly); bx.fill();
  return { arm, body };
}
async function assets() {
  if (!parts) parts = Promise.all([loadImg('/assets/chars/x07_flop.png'), loadImg('/assets/chars/g07_tiptoe.png')]).then(([x, g]) => ({ x: isolate(x, ARM_X), g: isolate(g, ARM_G) }));
  return parts;
}
// Texture triangles preserve painted anatomy and avoid a rotating cardboard arm.
// Every joint uses continuous skin weights; no new character pixels are drawn.
function tri(x, im, src, dst) {
  const [p, q, r] = src, [a, b, c] = dst;
  const den = (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);
  const A = ((b[0]-a[0])*(r[1]-p[1])-(c[0]-a[0])*(q[1]-p[1]))/den;
  const C = ((c[0]-a[0])*(q[0]-p[0])-(b[0]-a[0])*(r[0]-p[0]))/den;
  const B = ((b[1]-a[1])*(r[1]-p[1])-(c[1]-a[1])*(q[1]-p[1]))/den;
  const D = ((c[1]-a[1])*(q[0]-p[0])-(b[1]-a[1])*(r[0]-p[0]))/den;
  const mid=[(a[0]+b[0]+c[0])/3,(a[1]+b[1]+c[1])/3];
  const cover=dst.map(p=>{const d=Math.hypot(p[0]-mid[0],p[1]-mid[1]);return [p[0]+.32*(p[0]-mid[0])/d,p[1]+.32*(p[1]-mid[1])/d];});
  x.save(); path(x, cover); x.clip(); x.transform(A,B,C,D,a[0]-A*p[0]-C*p[1],a[1]-B*p[0]-D*p[1]); x.drawImage(im,0,0); x.restore();
}
function mesh(x, im, box, deform) {
  const [x0,y0,x1,y1] = box, step = 18;
  for(let py=y0;py<y1;py+=step) for(let px=x0;px<x1;px+=step) {
    const qx=Math.min(px+step,x1),qy=Math.min(py+step,y1), a=[px,py],b=[qx,py],c=[qx,qy],d=[px,qy];
    tri(x,im,[a,b,c],[deform(a),deform(b),deform(c)]); tri(x,im,[a,c,d],[deform(a),deform(c),deform(d)]);
  }
}
function child(P, t) {
  const c=canvas(1536,1024), x=c.getContext('2d'); x.drawImage(P.body,0,0);
  const lift=ss(.30,.86,t), wave=lift*Math.sin(Math.max(0,t-.86)*Math.PI*4.4);
  const shoulder=[1190,626], elbow=[1240,703], wrist=[1370,766];
  const a=-.29*lift, b=(-1.15+.23*wave)*lift, w=.12*wave;
  mesh(x,P.arm,[1152,594,1500,850], p => {
    const fore=rot(p,elbow,b), hand=rot(rot(p,wrist,w),elbow,b);
    const flex=blend(p,blend(fore,hand,ss(1350,1400,p[0])),ss(1224,1280,p[0]));
    return rot(flex,shoulder,a);
  });
  return c;
}
function grandma(P,t) {
  const c=canvas(1024,1536), x=c.getContext('2d');x.drawImage(P.body,0,0);
  const k=1-ss(CUT+.16,CUT+1.35,t), hold=.003*Math.sin(t*8)*(1-k);
  // The wrist and elbow unfold toward the lamp BASE. This is a contact
  // candidate only: the available open hand cannot yet grasp the high bail.
  // Both forefeet and the torso remain at their established world positions.
  mesh(x,P.arm,[570,20,780,412],p=> {
    const q=rot(p,[632,249],-.18*k+hold);
    const h=rot(q,rot([681,134],[632,249],-.18*k+hold),-.48*k);
    return blend(p,blend(q,h,1-ss(115,170,p[1])),1-ss(300,360,p[1]));
  });
  return c;
}
let props;
function floorProps() {
  if(props)return props;
  const c=canvas(BW,BH),x=c.getContext('2d');
  // Same wall socket as the master plate; cable stays inserted and the phone is dead.
  const cable=new Path2D();cable.moveTo(35,605);cable.bezierCurveTo(38,648,57,668,105,680);cable.bezierCurveTo(205,713,283,714,345,700);
  x.lineCap='round';x.strokeStyle='#403e36';x.lineWidth=3.5;x.stroke(cable);x.strokeStyle='#c9c6b6';x.lineWidth=1.6;x.stroke(cable);
  x.fillStyle='#d7d1bd';x.strokeStyle='#625e52';x.lineWidth=.8;x.beginPath();x.roundRect(28,597,13,12,2);x.fill();x.stroke();
  x.save();x.translate(367,695);x.rotate(-.10);x.scale(1,.70);
  x.fillStyle='#22272c';x.strokeStyle='#10171d';x.lineWidth=1.8;x.beginPath();x.roundRect(-23,-12,46,24,4);x.fill();x.stroke();
  x.fillStyle='#080c12';x.beginPath();x.roundRect(-20,-9,40,18,2);x.fill();
  x.strokeStyle='#69808a';x.lineWidth=.8;x.beginPath();x.moveTo(-17,-7);x.lineTo(12,-7);x.stroke();
  x.fillStyle='#c9c6b6';x.fillRect(-29,-2,7,4);x.restore();
  return props=c;
}
let lamp;
function lampImage() {
  if(lamp)return lamp;
  const c=canvas(700,1000),x=c.getContext('2d');x.translate(350-LX,980-LB);drawLamp(x,0,false);return lamp=c;
}
function shadows(t) {
  const c=canvas(BW,BH),x=c.getContext('2d');x.filter='blur(3px)';x.fillStyle='rgba(10,14,19,.36)';
  const lift=ss(.30,.86,t), elbow=rot([1240,703],[1190,626],-.29*lift);
  // Back of head, shoulder blade, hip and both shoe soles share the mat plane.
  // The fanning elbow's contact shadow follows its joint; palm shadow fades on lift.
  for(const [cx,cy,rx,ry] of [[638,636,29,6],[604,650,35,6],[536,658,54,7],[448,668,28,3],[391,663,20,3],[402,693,22,4],[X.x+elbow[0]*X.sc,X.y+elbow[1]*X.sc+2,11,3],[G.x+407*G.sc,G.y+1418*G.sc+1,8,2],[G.x+580*G.sc,G.y+1440*G.sc+1,9,2]]){x.beginPath();x.ellipse(cx,cy,rx,ry,0,0,7);x.fill();}
  x.globalAlpha=1-lift;x.beginPath();x.ellipse(674,697,15,3,0,0,7);x.fill();
  return c;
}
const shot={
 bg:'bg_01_room_wide',size:[BW,BH],
 layers:async t=>{
  const P=await assets(),fall= -8*(1-ss(0,.20,t))+2.1*Math.sin((t-.20)*20)*Math.exp(-Math.max(0,t-.20)*12)*ss(.20,.24,t);
  return [
   {img:floorProps(),x:0,y:0,sc:1}, {img:shadows(t),x:0,y:0,sc:1},
   {img:COILC,x:COIL[0]-60,y:COIL[1]-34,sc:1},
   {img:child(P.x,t),x:X.x,y:X.y+fall,sc:X.sc},
   // A 1px nudge follows the cabinet cornice slope (-0.65); no unsupported lift.
   {img:lampImage(),x:1326-ss(3.98,4.15,t),y:267+.65*ss(3.98,4.15,t),sc:.080,ox:350,oy:980},
   {img:grandma(P.g,t),...G},
  ];
 },
 light:()=>({ambient:[.030,.042,.072],lights:[{x:1200,y:250,r:600,color:[.52,.65,1],i:.065,falloff:1.2}],shafts:[{poly:[[0,170],[150,120],[760,760],[330,941],[0,941]],color:[.5,.62,.95],i:.30,soft:70}],exposure:1,vignette:.32,grain:5}),
 glow:()=>[{x:COIL[0]-20,y:COIL[1]+1,r:3,color:[255,90,40],a:.65,core:.3}],
 cam:t=> t<CUT?{x:520,y:650,fit:3.30+.06*ss(0,CUT,t)}:{x:1292,y:412,fit:2.10+.05*ss(CUT,5,t)},
};
// Compose each camera crop at native detail. Compositing tiny people into the
// 1672px wide master first and then magnifying it made the outlines stair-step.
const crops = [{ x:240, y:492.5, w:560, h:315, scale:3 }, { x:882, y:181.375, w:820, h:461.25, scale:2 }];
const backgrounds = [];
async function localShot(t) {
  const n=t<CUT?0:1, C=crops[n], S=C.scale;
  const point=p=>[(p[0]-C.x)*S,(p[1]-C.y)*S];
  if(!backgrounds[n]) {
    const c=canvas(C.w*S,Math.round(C.h*S)),x=c.getContext('2d');x.imageSmoothingQuality='high';
    x.drawImage(await loadImg('bg_01_room_wide'),C.x,C.y,C.w,C.h,0,0,c.width,c.height);backgrounds[n]=c;
  }
  return {
    bg:backgrounds[n],size:[backgrounds[n].width,backgrounds[n].height],
    layers:async t=>(await shot.layers(t)).map(L=>({...L,x:(L.x-C.x)*S,y:(L.y-C.y)*S,sc:L.sc*S})),
    light:t=>{const L=shot.light(t);return {...L,lights:L.lights.map(l=>({...l,x:(l.x-C.x)*S,y:(l.y-C.y)*S,r:l.r*S})),shafts:L.shafts.map(s=>({...s,poly:s.poly.map(point),soft:s.soft*S}))};},
    glow:t=>shot.glow(t).map(g=>({...g,x:(g.x-C.x)*S,y:(g.y-C.y)*S,r:g.r*S})),
    cam:t=>{const c=shot.cam(t);return{x:(c.x-C.x)*S,y:(c.y-C.y)*S,fit:c.fit*C.w/BW};},
  };
}
export async function renderFrame(ctx,t,W,H){t=Math.max(0,Math.min(DURATION,t));return renderPaint(ctx,t,W,H,await localShot(t));}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||0,W,H);}
