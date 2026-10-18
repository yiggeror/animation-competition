// LOCAL COLLAB S04 CANDIDATE. No shared helper, production module, EDL or audio changes.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
import {COIL,COILC,FAN} from '/js/paint/shots/s01.js';
import {lamp as drawLamp,LX,LB} from '/js/code/s08.js';
import {key} from '/js/lib/core.js';
import {DURATION,FRAME_COUNT,CUT,PHONE,REGISTRATION,ASSET_INFO,frameIndex,frameAssets,isDark} from './s04_drawn_timeline.js';
export {DURATION,FRAME_COUNT,CUT,PHONE};
const BW=1672,BH=941;
const fanSpin=(t)=>(!isDark(t)?1:Math.exp(-(t-CUT)/1.4));
const FRAMES=new URL('/assets/chars/s04/',import.meta.url), verifiedImages=new Map();
async function lockedImage(name) {
  if(!verifiedImages.has(name)) verifiedImages.set(name,(async()=>{
    const expected=ASSET_INFO[name];if(!expected) throw new Error('Unlisted S04 asset: '+name);
    const im=await loadImg(new URL(name,FRAMES).href);if(!im) throw new Error('Missing S04 drawing: '+name);
    if(im.width!==expected.width||im.height!==expected.height) throw new Error('S04 registered canvas changed: '+name);
    return im;
  })());
  return verifiedImages.get(name);
}
export const LAMP_AT = [1262, 642], LAMP_S = 0.17;
export function tableLamp(lift = 0) {
  const c = new OffscreenCanvas(220, 200), x = c.getContext('2d');
  x.translate(110, 170 - lift); x.scale(-LAMP_S, LAMP_S); x.translate(-LX, -LB); drawLamp(x, 0, false);
  x.setTransform(1, 0, 0, 1, 0, 0); x.fillStyle = '#c9a25a'; x.strokeStyle = '#3e2a1e'; x.lineWidth = 1; x.beginPath(); x.rect(150, 162, 18, 7); x.fill(); x.stroke();   // 火柴盒
  return { img: c, x: LAMP_AT[0] - 110, y: LAMP_AT[1] - 170, sc: 1 };
}

function stool(x,cx,top=30) {
  x.fillStyle='#8a5b3c';x.strokeStyle='#3b2c25';x.lineWidth=1.2;
  x.beginPath();x.rect(cx-15,-top,30,4);x.fill();x.stroke();
  for(const dx of [-12,9]){x.beginPath();x.rect(cx+dx,-top+4,3,top-4);x.fill();x.stroke();}
}
function originalStoolLayer() {
  const c=new OffscreenCanvas(560,640),x=c.getContext('2d');
  x.scale(2,2);x.translate(935-780,775-470);x.scale(-2.77,2.77);stool(x,-2);
  return {img:c,x:780,y:470,sc:.5,contact:{a:.45,blur:3,sy:-.1,skew:.5}};
}
// Keep the source r14 halo in the scene, but remove coverage of the entire real
// Xiaoman silhouette: its opaque phone back and fingers must never become a blue screen.
function occludedPhoneHalo(xiaoman) {
  const c=new OffscreenCanvas(64,64),x=c.getContext('2d');
  const gr=x.createRadialGradient(32,32,0,32,32,14);
  gr.addColorStop(0,'rgba(170,205,255,0.45)');gr.addColorStop(.3,'rgba(170,205,255,0.225)');gr.addColorStop(1,'rgba(170,205,255,0)');
  x.fillStyle=gr;x.fillRect(18,18,28,28);
  x.globalCompositeOperation='destination-out';x.imageSmoothingQuality='high';
  x.drawImage(xiaoman,REGISTRATION.X.x-(PHONE[0]-32),REGISTRATION.X.y-(PHONE[1]-32),xiaoman.width*REGISTRATION.X.sc,xiaoman.height*REGISTRATION.X.sc);
  return c;
}
let cachedLamp,cachedStool,cachedPhoneHalo;
export const darkLight = (t, phoneLit = 1) => ({
  ambient: [0.11, 0.13, 0.19],   // 停电后的月光底子：人物轮廓和动作要看得清
  lights: phoneLit > 0 ? [{ x: PHONE[0], y: PHONE[1] - 6, r: 120, color: [0.6, 0.75, 1.0], i: 0.75 * phoneLit, falloff: 1.8 }] : [],
  shafts: [{ poly: [[0, 170], [150, 120], [760, 760], [330, 941], [0, 941]], color: [0.5, 0.62, 0.95], i: 0.38, soft: 70 }],
  exposure: 1.0, vignette: 0.5, grain: 8,
});
const brightLight = { ambient: [0.64, 0.67, 0.73], lights: [{ x: 780, y: 60, r: 1500, color: [0.94, 0.97, 1.0], i: 0.32, falloff: 1.4 }, { x: 300, y: 440, r: 700, color: [0.55, 0.7, 1.0], i: 0.35, falloff: 1.6 }], exposure: 1.0, vignette: 0.3, grain: 5 };
export function fan(x, spin) {
  x.save(); x.translate(FAN[0], FAN[1] + 12); x.scale(1, 0.14);
  if (spin > 0.3) for (let k = 0; k < 3; k++) { x.fillStyle = `rgba(225,215,190,${0.18 * Math.min(1, spin * 1.4)})`; x.beginPath(); x.ellipse(0, 0, 175 - k * 4, 175 - k * 4, 0, 0, 7); x.fill(); }
  else { x.fillStyle = 'rgba(70,60,50,0.8)'; for (let b = 0; b < 3; b++) { const a = b * 2.09 + (1 - spin) * 9; x.save(); x.rotate(a); x.fillRect(40, -5, 135, 10); x.restore(); } }
  x.restore();
}
export const shot={
  bg:'bg_01_room_wide',size:[BW,BH],
  layers:async(t)=>{
    const keys=frameAssets(frameIndex(t));const [X,G]=await Promise.all([lockedImage(keys.X),lockedImage(keys.G)]);
    cachedPhoneHalo ||= occludedPhoneHalo(X);
    return [
      {img:COILC,x:COIL[0]-60,y:COIL[1]-34,sc:1},
      cachedLamp ||= tableLamp(),
      {img:X,...REGISTRATION.X,contact:{a:.4,blur:3,sy:1,dx:-2,dy:3}},
      cachedStool ||= originalStoolLayer(),
      {img:G,...REGISTRATION.G,contact:{a:.45,blur:4,sy:-.07,skew:.5}},
    ];
  },
  light: (t) => (!isDark(t) ? brightLight : darkLight(t)),
  glow: (t) => (!isDark(t) ? [] : [{ x: COIL[0] - 20, y: COIL[1] + 1, r: 4, color: [255, 90, 40], a: 0.9, core: 0.3 }]),
  emit: (x, t) => {
    // 电视：灭的一瞬间缩成一个亮点再消失
    if (!isDark(t)) { x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = 'rgba(110,150,210,0.1)'; x.beginPath(); x.roundRect(206, 370, 72, 98, 10); x.fill(); x.restore(); }
    else { const u = key(t, [[CUT, 0], [CUT + 0.35, 1]]); if (u < 1) { const r = 34 * (1 - u) + 2; x.save(); x.globalCompositeOperation = 'lighter'; x.fillStyle = `rgba(220,235,255,${1 - u * 0.7})`; x.beginPath(); x.ellipse(242, 419, r, r * (1 - u) + 1.5, 0, 0, 7); x.fill(); x.restore(); } }
    fan(x, fanSpin(t));
    if (isDark(t)) {
      x.save(); x.globalCompositeOperation = 'lighter';
      x.drawImage(cachedPhoneHalo, PHONE[0] - 32, PHONE[1] - 32); x.restore();
    }
  },
  cam: (t) => ({ x: BW / 2 - 20, y: BH / 2 + 12, fit: 1.04 }),
};
export async function renderFrame(ctx,t,W,H) {
  frameAssets(frameIndex(t));
  if(!await loadImg('bg_01_room_wide')) throw new Error('Original S04 background required; placeholder refused');
  return renderPaint(ctx,t,W,H,shot);
}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||0,W,H);}
