// S08 full144 assembly: all original character layers locked; actual Canvas review remains separate.
// Uses thirty-five unique original drawings over forty-one exposures. No later-shot fallback.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
import {flameShape} from '/js/code/s08.js';
import {lamp as drawLamp,LX,LB} from './s08_drawn_lamp.js';
import {DURATION,FRAME_COUNT,LAMP_BASE,LAMP_SCALE,LAMP_WICK,poseAt,fireAt,frameAt,TABLE_BOX_CONTACT,mechanismAt} from './s08_drawn_contract.js';
import {LAYER_ARTS} from './s08_drawn_layers.js';
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
 const roles=LAYER_ARTS[asset].table_box?['body','arms','table_box']:['body','arms'];
 if(LAYER_ARTS[asset].table_match){
  if(!LAYER_ARTS[asset].table_box)throw new Error('Table match requires the existing table-box state');
  roles.push('table_match');
 }
 if(!layerCache.has(asset))layerCache.set(asset,Promise.all(roles.map(async role=>{
  const meta=LAYER_ARTS[asset][role];
  const im=await loadImg(new URL('/assets/chars/g08/'+meta.filename,import.meta.url).href);
  if(!im)throw new Error('Locked S08 original-pixel layer missing: '+meta.filename);
  if(im.width!==meta.width||im.height!==meta.height)throw new Error('S08 registered layer canvas changed');
  return im;
 })));
 return layerCache.get(asset);
}
// High/half-lift states are cached separately; the old zero-lift function is unchanged.
const liftedLampCache=new Map();
function lampLayerAtLift(lift){
 if(lift===0)return cachedLamp ||= lampLayerAtZero();
 if(!liftedLampCache.has(lift)){
  const c=new OffscreenCanvas(W,H),x=c.getContext('2d');
  x.translate(LAMP_BASE[0],LAMP_BASE[1]);x.scale(-LAMP_SCALE,LAMP_SCALE);x.translate(-LX,-LB);
  drawLamp(x,lift,false);
  liftedLampCache.set(lift,{img:c,x:0,y:0,sc:1});
 }
 return liftedLampCache.get(lift);
}
export const shot={
 size:[W,H],
  layers:async(t)=>{const pose=poseAt(t);const [body,arms,tableBox,tableMatch]=await lockedLayers(pose.asset);return[
  lampLayerAtLift(mechanismAt(t).lift), // One independent code lamp behind the true transparent grip seat and original fingers.
  cachedStool ||= originalStoolLayer(),
  {img:body,x:0,y:0,sc:1},
  cachedFront ||= tableFront(),
  ...(tableBox?[{img:tableBox,x:0,y:0,sc:1,contact:TABLE_BOX_CONTACT}]:[]), // One original-pixel table box with attached contact shadow, only in approved table-supported states.
  ...(tableMatch?[{img:tableMatch,x:0,y:0,sc:1,contact:LAYER_ARTS[pose.asset].table_match.contact}]:[]), // Optional exclusive real match pixels; the releasing fingers stay in the front arm layer.
  {img:arms,x:0,y:0,sc:1}, // Per-pose exclusive original RGBA; no transformed hand/match.
 ];},
 light:(t)=>{
  const A=fireAt(t),lights=[];
  // Original S08 match-light parameters, attached to the actual drawing's match head.
  if(A.lit)lights.push({x:A.head[0],y:A.head[1]-14,r:780*(.85+.2*A.m),color:[1,.64,.32],i:(.55+.45*A.m)*A.flicker,falloff:1.9});
  if(A.wick>0)lights.push({x:LAMP_WICK[0],y:LAMP_WICK[1]-30,r:900+1100*A.wick,color:[1,.62,.30],i:(.35+.95*A.wick)*A.flicker,falloff:1.9});
  return {ambient:[.10,.11,.17],lights,exposure:1,vignette:.5,grain:7};
 },
 glow:(t)=>{const A=fireAt(t),out=A.lit?[{x:A.head[0],y:A.head[1]-10,r:90*(.7+.4*A.m),color:[255,190,110],a:.5,core:.25}]:[];if(A.wick>0)out.unshift({x:LAMP_WICK[0],y:LAMP_WICK[1]-25,r:150*A.flicker*(.5+A.wick),color:[255,200,120],a:.55*A.wick+.2,core:.2},{x:LAMP_WICK[0],y:LAMP_WICK[1]-70,r:260,color:[255,210,150],a:.18*A.wick,core:.4});return out;},
 emit:(x,t)=>{const A=fireAt(t);if(A.lit)flameShape(x,[A.head[0],A.head[1]+2],.42*A.m,t);if(A.wick>0)flameShape(x,[LAMP_WICK[0],LAMP_WICK[1]+2],.62*A.wick*A.flicker,t,true);
  // Original smoke clock/three-stroke formula; formal F053 gate preserves every old subframe.
  if(A.frame<53)return;
    const age = t - 2.2;
    if (age > 0 && age < 2.5) {
      const q = A.head; // Already screen-space true match-head pixels.
      x.save(); x.lineCap = 'round';
      for (let k = 0; k < 3; k++) {
        x.strokeStyle = `rgba(200,200,205,${Math.max(0, 0.22 * (1 - age / 2.5) - k * 0.05)})`; x.lineWidth = 3 + k * 4 + age * 6;
        x.beginPath(); x.moveTo(q[0], q[1]); const hh = 60 + age * 140;
        for (let s = 1; s <= 8; s++) { const u = s / 8; x.lineTo(q[0] + 18 * Math.sin(u * 5 + t * 1.7 + k) * u + 30 * u * age, q[1] - hh * u); }
        x.stroke();
      }
      x.restore();
    }
 },
 cam:(t)=>{frameAt(t);return{x:960,y:540,fit:1};},
};
export async function renderFrame(ctx,t,w,h){frameAt(t);shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,arg===''||arg==null?0:Number(arg),w,h);}
