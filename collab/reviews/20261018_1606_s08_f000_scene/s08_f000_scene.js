// Exclusive LOCAL COLLAB F000 diagnostic: locked new PNG, original scene, only lamp+35x.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
import {lamp as drawLamp,LX,LB} from '/js/code/s08.js';
import {DURATION,FRAME_COUNT,ART,LAMP_BASE,LAMP_SCALE,requireT0} from './contract.js';
export {DURATION,FRAME_COUNT};
const W=1920,H=1080,K=14,AT=[596,1793],TOP=-58,EDGE=12;
let BG = null;
async function bg() {
  if (BG) return BG;
  const room = await loadImg('bg_01_room_wide');
  if (!room) throw new Error('Original S08 background missing; placeholder refused');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(22px)'; x.drawImage(room, 980, 160, 640, 360, -80, -60, W + 160, H + 120); x.filter = 'none';   // 后墙（虚）
  x.save(); x.translate(AT[0], AT[1]); x.scale(K, K);
  // 桌面（从略高处看到一窄条），马灯就站在这一条上
  x.fillStyle = '#8a5a34'; x.fillRect(EDGE, TOP - 2.2, 200, 2.2);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.3; x.beginPath(); x.moveTo(EDGE, TOP - 2.2); x.lineTo(200, TOP - 2.2); x.stroke();
  x.restore();
  return (BG = c);
}

function lampLayerAtZero(){
  const c=new OffscreenCanvas(W,H),x=c.getContext('2d');
  x.translate(LAMP_BASE[0],LAMP_BASE[1]);x.scale(-LAMP_SCALE,LAMP_SCALE);x.translate(-LX,-LB);
  drawLamp(x,0,false); // Original complete lamp, lowered globe, no flame; old worldx1380→1415 only.
  return {img:c,x:0,y:0,sc:1};
}
function originalStoolLayer(){
  const c=new OffscreenCanvas(W,H),x=c.getContext('2d');
  x.translate(AT[0],AT[1]);x.scale(K,K);
  const cx=-3,top=45;
  x.fillStyle='#8a5b3c';x.strokeStyle='#3b2c25';x.lineWidth=1.2;
  x.beginPath();x.rect(cx-15,-top,30,4);x.fill();x.stroke();
  for(const dx of[-12,9]){x.beginPath();x.rect(cx+dx,-top+4,3,top-4);x.fill();x.stroke();}
  // Stool top is worldy1163, below1080crop, exactly as the source frame0.
  return {img:c,x:0,y:0,sc:1};
}
function tableFront() {        // 桌沿和牙板：挡住桌子底下的腿
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.translate(AT[0], AT[1]); x.scale(K, K);
  x.fillStyle = '#6a4226'; x.fillRect(EDGE, TOP, 200, 3.4); x.fillStyle = '#5a361e'; x.fillRect(EDGE + 1.5, TOP + 3.4, 200, 4.2);
  x.strokeStyle = '#3e2a1e'; x.lineWidth = 0.35; x.strokeRect(EDGE, TOP, 200, 3.4); x.strokeRect(EDGE + 1.5, TOP + 3.4, 200, 4.2);
  x.fillStyle = '#4a2c18'; x.fillRect(EDGE + 2, TOP + 7.6, 3.6, 60);       // 桌腿
  return { img: c, x: 0, y: 0, sc: 1 };
}

let artPromise,cachedLamp,cachedStool,cachedFront;
async function lockedArt(){
  if(!artPromise)artPromise=(async()=>{
    const im=await loadImg(new URL('./frames/'+ART.filename,import.meta.url).href);
    if(!im)throw new Error('Locked S08 F000 drawing missing');
    if(im.width!==ART.width||im.height!==ART.height)throw new Error('S08 F000 registered canvas changed');
    return im;
  })();
  return artPromise;
}
export const shot={
  size:[W,H],
  layers:async(t)=>{requireT0(t);return[
    cachedLamp ||= lampLayerAtZero(),
    cachedStool ||= originalStoolLayer(),
    {img:await lockedArt(),x:0,y:0,sc:1}, // Contains the actual complete hands, unlit match and matchbox.
    cachedFront ||= tableFront(), // Keep sourcey981front occlusion; two elbow tips require director review.
  ];},
  light:(t)=>{requireT0(t);return{ambient:[.10,.11,.17],lights:[],exposure:1,vignette:.5,grain:7};},
  glow:(t)=>{requireT0(t);return[];},
  emit:(x,t)=>{requireT0(t);}, // No match flame, wick flame, smoke or fire glow at0.
  cam:(t)=>{requireT0(t);return{x:960,y:540,fit:1};},
};
export async function renderFrame(ctx,t,w,h){requireT0(t);shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){const t=arg===''||arg==null?0:Number(arg);return renderFrame(ctx,t,w,h);}
