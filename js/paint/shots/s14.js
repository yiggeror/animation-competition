// S14 · 搭台，10秒。原铁丝、床单、5秒亮幕与声音时基保持。
// Approved v2 supplies one real hand–pin–cloth contact at +3.2s. The other
// pin placements and lamp hanging are elided by cuts, not autonomous props.
// One source pose cannot demonstrate shaking, three placements, stool climbing
// or lamp hanging; those action gaps remain explicit in the delivery report.
import { renderPaint, loadImg } from '../paintshot.js';
export const DURATION = 10;
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const BW = 1672, BH = 941;
const WIRE = [[328, 268], [905, 250]];                    // 铁丝两头（左墙上的钉子、木柱）
const wireY = (x) => { const u = (x - WIRE[0][0]) / (WIRE[1][0] - WIRE[0][0]); return WIRE[0][1] + (WIRE[1][1] - WIRE[0][1]) * u + 14 * Math.sin(Math.PI * u); };
const SH = { x0: 392, x1: 842, bottom: 505 };              // 床单左右边、下沿
const T_HANG = 0.5, T_LAMP = 5.0, PINS = [[2.5, 0.12], [3.2, 0.5], [3.9, 0.88]];
const LAMP = [600, 330];                                   // 挂在床单后面的马灯（透过床单看到的亮点）

const canv = (w,h) => new OffscreenCanvas(w,h);
export const TIMING = { hem:1.9, contact:2.75, press:3.2, interior:3.55, establish:6.1, seated:8.5, lamp:5 };
export const PLACEMENT = {
  grandma:{x:617-853*.245,y:wireY(617)-135*.245,sc:.245},
  girl:{x:627,y:449,sc:.22},
};
const G=PLACEMENT.grandma, X=PLACEMENT.girl;
const visibleGrandma=t=>t<TIMING.hem||(t>=TIMING.contact&&t<TIMING.interior);
let A;
async function assets(){
  if(A)return A;
  const [body,arm,cloth,girl]=await Promise.all(['g14_body','g14_press_arm','g14_contact_cloth','x16_arms_crossed'].map(n=>loadImg('/assets/chars/'+n+'.png')));
  if(!body||!arm||!cloth||!girl)throw Error('S14 reviewed character layers unavailable');
  return A={body,arm,cloth,girl};
}
// A small rigid sleeve/arm/hand/pin movement. The near hand, face, trunk and feet
// never move with the press. At +3.2s original source contact lands on wireY(617).
export const armAngle=t=>-.075*(1-sstep(2.82,3.2,t));
function grandma(a,t){
 const c=canv(1024,1536),x=c.getContext('2d');
 // The contact cloth is drawn separately over the scene's single full sheet.
 x.save();x.translate(623,315);x.rotate(armAngle(t));x.translate(-623,-315);x.drawImage(a.arm,0,0);x.restore();
 x.drawImage(a.body,0,0); // fixed original cuff occludes the arm underlap
 return c;
}
function contactCloth(a,t){
 const c=canv(1024,1536),x=c.getContext('2d');x.drawImage(a.cloth,0,0);
 // Original gripped fold is constrained to the same physical sheet silhouette,
 // including the folded strip before its +0.5s drop. No floating feathered patch.
 x.globalCompositeOperation='destination-in';x.setTransform(1/G.sc,0,0,1/G.sc,-G.x/G.sc,-G.y/G.sc);x.drawImage(sheet(t),0,0);
 return c;
}
function ground(t){
 const c=canv(BW,BH),x=c.getContext('2d');x.fillStyle='rgba(36,24,18,.32)';x.filter='blur(2px)';
 const marks=visibleGrandma(t)?[[G.x+245*.245,G.y+1455*.245,17,2.8],[G.x+505*.245,G.y+1468*.245,22,3]]:[];
 if(t>=8.5)marks.push([X.x+144*.22,X.y+1149*.22,35,4],[X.x+540*.22,X.y+1149*.22,23,3]);
 for(const [px,py,rx,ry] of marks){x.beginPath();x.ellipse(px,py,rx,ry,0,0,7);x.fill();}
 return c;
}
function camera(t){
 if(t<1.9)return {x:580+4*sstep(0,1.9,t),y:419,width:760};
 if(t<2.75)return {x:690,y:455,width:300};
 if(t<3.55)return {x:567,y:312,width:330};
 if(t<6.1)return {x:731,y:432,width:320};
 if(t<8.5)return {x:620,y:401,width:680};
 return {x:690,y:581,width:460};
}

function sheet(t) {
  const c = new OffscreenCanvas(BW, BH), x = c.getContext('2d');
  const drop = .08 + .92*sstep(T_HANG, T_HANG + 0.55, t), sway = Math.exp(-Math.max(0, t - T_HANG - 0.4) * 1.6) * Math.sin((t - T_HANG) * 7) * (t > T_HANG ? 1 : 0);
  if (drop <= 0) return c;
  const wob = (t > 1.0 ? Math.exp(-(t - 1.0) * 3) * Math.sin((t - 1.0) * 30) * 3 : 0);
  // 铁丝晃一下（在底图的铁丝上补画一根）
  const top = (px) => wireY(px) + wob * Math.sin(Math.PI * (px - WIRE[0][0]) / (WIRE[1][0] - WIRE[0][0])) * Math.sin((px-617)/80); // held at the real central hand contact
  // 床单：上沿搭在铁丝上，下沿往下坠（抖开时从短到长，晃几下停住）
  const bot = (px) => { const h = SH.bottom - top(px); return top(px) + h * drop + 14 * sway * Math.sin((px - SH.x0) * 0.02); };
  const path = new Path2D(); path.moveTo(SH.x0, top(SH.x0));
  for (let px = SH.x0; px <= SH.x1; px += 10) path.lineTo(px, top(px));
  for (let px = SH.x1; px >= SH.x0; px -= 10) path.lineTo(px, bot(px));
  path.closePath();
  x.fillStyle = '#ecebe2'; x.fill(path);
  x.save(); x.clip(path);
  // 褶子：竖着的一道道明暗；搭在铁丝上的那一折是双层的（略暗）
  for (let px = SH.x0; px < SH.x1; px += 38) { const g = x.createLinearGradient(px, 0, px + 38, 0); g.addColorStop(0, 'rgba(120,110,95,0.10)'); g.addColorStop(0.5, 'rgba(255,255,250,0.06)'); g.addColorStop(1, 'rgba(120,110,95,0.10)'); x.fillStyle = g; x.fillRect(px, 0, 38, BH); }
  x.fillStyle = 'rgba(110,100,85,0.14)'; x.beginPath(); for (let px = SH.x0; px <= SH.x1; px += 10) x.lineTo(px, top(px) + 26); x.lineTo(SH.x1, 0); x.lineTo(SH.x0, 0); x.fill();
  // 褪色的印花边（下沿一圈小花）
  x.fillStyle = 'rgba(200,120,110,0.35)'; for (let px = SH.x0 + 14; px < SH.x1; px += 28) { const by = bot(px) - 14; x.beginPath(); x.arc(px, by, 4, 0, 7); x.fill(); }
  x.restore();
  x.strokeStyle = 'rgba(62,42,30,0.75)'; x.lineWidth = 2.5; x.stroke(path);
  // 衣夹：木头夹子夹在铁丝和床单上沿
  for (const [tp, u] of PINS) {
    if (t < tp || (u===.5 && visibleGrandma(t))) continue; // source hand already holds the central pin
    const px = SH.x0 + (SH.x1 - SH.x0) * u, py = top(px), k = sstep(tp, tp + 0.08, t);
    x.save(); x.translate(px, py + 2*(1-k)); x.fillStyle = '#bc965f'; x.strokeStyle = '#53402c'; x.lineWidth = .7;
    x.beginPath();x.roundRect(-3,-13,5.2,19,1);x.fill();x.stroke();
    x.strokeStyle='rgba(250,220,165,.55)';x.lineWidth=.6;x.beginPath();x.moveTo(-1,-11);x.lineTo(-1,4);x.stroke();
    x.strokeStyle='#65564b';x.lineWidth=.6;x.beginPath();x.ellipse(.4,-3,1.3,2.2,.15,0,7);x.stroke();x.restore();
  }
  return c;
}
const lit = (t) => sstep(T_LAMP, T_LAMP + 0.6, t);
const fl = (t) => 1 + 0.05 * Math.sin(t * 9.3) + 0.03 * Math.sin(t * 17.7);
const shot = {
  bg: 'bg_01_room_wide', size: [BW, BH],
  layers: async t=>{const a=await assets();const layers=[{img:ground(t),x:0,y:0,sc:1},{img:sheet(t),x:0,y:0,sc:1}];
    if(visibleGrandma(t)){layers.push({img:contactCloth(a,t),...G});layers.push({img:grandma(a,t),...G});}
    if(t>=TIMING.seated)layers.push({img:a.girl,...X});return layers;
  },
  light: (t) => {
    const L = lit(t);
    return {
      ambient: [0.022, 0.026, 0.044],
      lights: [
        { x: 520, y: 520, r: 900 * fl(t), color: [1.0, 0.62, 0.30], i: 0.75 * (1 - L), falloff: 2.0 },      // 挂上去之前：马灯搁在箱子边
        { x: LAMP[0], y: LAMP[1] + 60, r: 1300 * fl(t), color: [1.0, 0.68, 0.38], i: 0.55 * L, falloff: 1.8 }, // 挂上以后：亮床单把屋里照得暖
      ],
      exposure: 1.0, vignette: 0.5, grain: 7,
    };
  },
  glow: () => [],
  // 床单被后面的马灯透亮：在床单范围里叠一层暖光（中间亮、往边上暗）
  emit: (x, t) => {
    const L = lit(t); if (L <= 0) return;
    const m = sheet(t);
    const g = new OffscreenCanvas(BW, BH), gx = g.getContext('2d');
    const rg = gx.createRadialGradient(LAMP[0], LAMP[1], 10, LAMP[0], LAMP[1] + 40, 420);
    rg.addColorStop(0, `rgba(255,236,190,${0.95 * L})`); rg.addColorStop(0.15, `rgba(255,214,150,${0.8 * L})`); rg.addColorStop(1, `rgba(220,150,80,${0.35 * L})`);
    gx.fillStyle = rg; gx.fillRect(0, 0, BW, BH);
    gx.globalCompositeOperation = 'destination-in'; gx.drawImage(m, 0, 0);
    gx.globalCompositeOperation='source-atop';gx.globalAlpha=.35;gx.drawImage(m,0,0);gx.globalAlpha=1;
    if(t>=TIMING.seated && A){gx.globalCompositeOperation='destination-out';gx.drawImage(A.girl,X.x,X.y,A.girl.width*X.sc,A.girl.height*X.sc);}
    x.globalCompositeOperation = 'source-over'; x.globalAlpha = fl(t) * 0.97; x.drawImage(g, 0, 0); x.globalAlpha = 1;
  },
  cam: t=>{const c=camera(t);return {x:c.x,y:c.y,fit:BW/c.width};},
};
// Compose source cards directly at delivery resolution, using the unchanged
// project linear-light renderer. Both light and emission use the same camera.
export async function renderFrame(ctx,t,w,h){
 t=Math.max(0,Math.min(DURATION,t));const cam=shot.cam(t),k=cam.fit*w/BW;
 const ox=w/2-cam.x*k,oy=h/2-cam.y*k;
 const c=canv(w,h),x=c.getContext('2d');x.imageSmoothingQuality='high';x.setTransform(k,0,0,k,ox,oy);
 x.drawImage(await loadImg(shot.bg),0,0,BW,BH);
 for(const l of await shot.layers(t)){x.save();x.translate(l.x,l.y);x.scale(l.sc,l.sc);x.drawImage(l.img,0,0);x.restore();}
 const light=shot.light(t),map=l=>({...l,x:l.x*k+ox,y:l.y*k+oy,r:l.r*k});
 return renderPaint(ctx,t,w,h,{bg:c,size:[w,h],light:()=>({...light,lights:light.lights.map(map)}),glow:()=>[],
  emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);shot.emit(x,t);x.restore();},cam:()=>({x:w/2,y:h/2,fit:1})});
}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
