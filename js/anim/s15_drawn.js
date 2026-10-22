// S15 · 第 6 场：鹤亮相。前 3 秒，奶奶把鹤从离床单 35 厘米的地方慢慢推过来——床单上一个又大又虚的影子渐渐变小、变清楚，
// "贴"上床单；然后接第 6 场关键镜头的亮相（低头 → 扬起脖子 → 收住），小满从抱着胳膊到看呆了。
import { makeShot } from '/js/lamp/shots/shotkit.js';
import { cranePose, CRANE_ROOT, RODS, raiseAt, xmWorld, billboardM } from '/js/lamp/s06_key.js';
import { sstep } from '/js/lamp/choreo.js';
export const DURATION = 8;
const T0 = 3;   // 贴上床单用的时间；之后的动作 = 关键镜头的 0～5 秒
const sheet = (t, env) => {
  const u = Math.max(0, t - T0);
  const dist = 0.004 + 0.34 * (1 - sstep(0, T0, t)) ** 1.6;
  const root = [CRANE_ROOT[0] - 0.05 * (1 - sstep(0, T0, t)), CRANE_ROOT[1] + 0.005 * Math.sin(u * 1.7) - 0.012 * (1 - Math.min(1, raiseAt(u)))];
  return [{ pup: env.crane, pose: cranePose(u), root, dist, rods: RODS.map((r) => ({ ...r, hand: r.hand(root) })) }];
};
// Native complete drawings only. No old rig, head split, breathe warp or pose blend.
export const FPS = 24;
export const FRAME_COUNT = 192;
export const REGISTRATION = Object.freeze({
  native: [1254,1254], ox: 540, oy: 835, floorY: 1198,
  // Stool seat-to-floor in the actual artwork, registered to the existing 22 cm seat.
  sc: (1198-835)/22,
  status: 'STRUCTURAL_CANDIDATE_NOT_FULL_SCENE_VALIDATED'
});
export const EXPOSURES = Object.freeze([
  {id:'F000',start:0,hold:108}, {id:'F108',start:108,hold:4},
  {id:'F112',start:112,hold:4}, {id:'F116',start:116,hold:4},
  {id:'F120',start:120,hold:4}, {id:'F124',start:124,hold:8},
  {id:'F132',start:132,hold:12}, {id:'F144',start:144,hold:48},
].map(e=>Object.freeze({...e,end:e.start+e.hold-1,path:new URL('/assets/chars/x15/'+e.id+'.png',import.meta.url).href})));
export function pickExposure(t) {
  if (!Number.isFinite(t) || t < 0 || t >= DURATION) throw new RangeError('S15 drawn supports t in [0,8).');
  const frame=Math.floor(t*FPS+1e-6);
  const e=EXPOSURES.find(e=>frame>=e.start && frame<=e.end);
  if(!e)throw new Error('S15 exposure gap at frame '+frame);
  return e;
}
// Registration is one uniform transform of the WHOLE native drawing, never a body-part warp.
// F144 seat anchor (555,835) stays fixed; its native sole about1220 maps to1197, matching prior floor1198.
export const DRAWING_REGISTRATION = Object.freeze({
  F144: Object.freeze({scale:0.94,anchor:[555,835]})
});
export function wholeDrawingMatrix(m,id) {
  const r=DRAWING_REGISTRATION[id];if(!r)return m;
  const s=r.scale,dx=r.anchor[0]*(1-s),dy=r.anchor[1]*(1-s);
  return [m[0]*s,m[1]*s,m[2]*s,m[3]*s,m[0]*dx+m[2]*dy+m[4],m[1]*dx+m[3]*dy+m[5]];
}
const mapsCache=new Map();
async function drawingMaps(e) {
  if(!mapsCache.has(e.path))mapsCache.set(e.path,(async()=>{
    const r=await fetch(e.path);if(!r.ok)throw new Error('Missing S15 drawing '+e.path);
    const im=await createImageBitmap(await r.blob());
    if(im.width!==1254||im.height!==1254)throw new Error('S15 drawing native dimensions changed: '+e.path);
    // 小满坐在床单前的暗处，唯一的光是右边发亮的床单。平法线（正对镜头）让床单光从侧面掠过，人几乎看不见（10-22 用户指出）；
    // 法线整体朝床单（右）和略朝上偏，材质按布料（wrap 0.6、暗部带一点暖），她被床单照亮侧脸和手臂，仍比床单暗。
    const mk=(fill)=>{const c=new OffscreenCanvas(im.width,im.height),x=c.getContext('2d');x.drawImage(im,0,0);x.globalCompositeOperation='source-in';x.fillStyle=fill;x.fillRect(0,0,c.width,c.height);return c;};
    return {alb:im,nrm:mk('rgb(175,140,235)'),mat:mk('rgb(0,30,0)')};
  })());
  return mapsCache.get(e.path);
}
const cards = async (CARDS, cam, t) => {
  const e=pickExposure(t),maps=await drawingMaps(e),R=REGISTRATION;
  const base=xmWorld([0,0]);
  base[2]=(R.floorY-R.oy)/R.sc/100;
  const depth=cam.project(base)[2];
  CARDS.addImage([{maps,m:wholeDrawingMatrix(billboardM(cam,base,R.ox,R.oy,R.sc),e.id)}],depth);
};
export const { render, renderFrame } = makeShot({ sheet, cards });
