// S08 first20-frame Canvas candidate. Original room/table/lamp functions retained.
// Uses seven locked original drawings over eight exposures. No later-shot fallback.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
import {lamp as drawLamp,flameShape,LX,LB} from '/js/code/s08.js';
import {DURATION,FRAME_COUNT,LAMP_BASE,LAMP_SCALE,poseAt,fireAt,frameAt,TABLE_BOX_CONTACT} from './contract.js';
import {LAYER_ARTS} from './layer_contract.js';
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


const layerCache=new Map();let cachedLamp,cachedStool,cachedFront;
async function lockedLayers(asset){
 if(!layerCache.has(asset))layerCache.set(asset,Promise.all((LAYER_ARTS[asset].table_box?['body','arms','table_box']:['body','arms']).map(async role=>{
  const meta=LAYER_ARTS[asset][role];
  const im=await loadImg(new URL('./frames/'+meta.filename,import.meta.url).href);
  if(!im)throw new Error('Locked S08 original-pixel layer missing: '+meta.filename);
  if(im.width!==meta.width||im.height!==meta.height)throw new Error('S08 registered layer canvas changed');
  return im;
 })));
 return layerCache.get(asset);
}
export const shot={
 size:[W,H],
 layers:async(t)=>{const pose=poseAt(t);const [body,arms,tableBox]=await lockedLayers(pose.asset);return[
  cachedLamp ||= lampLayerAtZero(), // Lowered globe, no wick flame, all twenty frames.
  cachedStool ||= originalStoolLayer(),
  {img:body,x:0,y:0,sc:1},
  cachedFront ||= tableFront(),
  ...(tableBox?[{img:tableBox,x:0,y:0,sc:1,contact:TABLE_BOX_CONTACT}]:[]), // F017 only, one original-pixel box with attached contact shadow.
  {img:arms,x:0,y:0,sc:1}, // Per-pose exclusive original RGBA; no transformed hand/match.
 ];},
 light:(t)=>{
  const A=fireAt(t),lights=[];
  // Original S08 match-light parameters, attached to the actual drawing's match head.
  if(A.lit)lights.push({x:A.head[0],y:A.head[1]-14,r:780*(.85+.2*A.m),color:[1,.64,.32],i:(.55+.45*A.m)*A.flicker,falloff:1.9});
  return {ambient:[.10,.11,.17],lights,exposure:1,vignette:.5,grain:7};
 },
 glow:(t)=>{const A=fireAt(t);return A.lit?[{x:A.head[0],y:A.head[1]-10,r:90*(.7+.4*A.m),color:[255,190,110],a:.5,core:.25}]:[];},
 emit:(x,t)=>{const A=fireAt(t);if(A.lit)flameShape(x,[A.head[0],A.head[1]+2],.42*A.m,t);},
 cam:(t)=>{frameAt(t);return{x:960,y:540,fit:1};},
};
export async function renderFrame(ctx,t,w,h){frameAt(t);shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,arg===''||arg==null?0:Number(arg),w,h);}
