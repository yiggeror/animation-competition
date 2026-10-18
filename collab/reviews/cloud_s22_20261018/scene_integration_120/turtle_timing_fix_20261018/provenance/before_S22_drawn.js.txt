// Independent S22 Canvas scene candidate. Production routing/EDL/ready remain untouched.
import { makeTurtle, turtlePose } from '../../../../js/lamp/turtle.js';
import { drawPuppet } from '../../../../js/puppet.js';
import { CONFIG, EXPOSURES } from './resource_map.js';
export { EXPOSURES };
export const DURATION = 5, FPS = 24, TOTAL_FRAMES = 120;
export const SHEET = EXPOSURES.map(row => [row.url, row.start]);
const RW = 1920, RH = 1080;
const sstep = (a,b,x) => { const u=Math.min(1,Math.max(0,(x-a)/(b-a))); return u*u*(3-2*u); };
const bitmaps = new Map();
let TURTLE = null, SCENE = null, LIGHT = null, approved = false;
export function exposureAt(t) {
  const frame=Math.max(0,Math.min(119,Math.floor((+t||0)*24+1e-6)));
  return EXPOSURES.find(row=>frame>=row.start && frame<=row.end);
}
async function image(row) {
  if (!bitmaps.has(row.url)) bitmaps.set(row.url,(async()=>{
    const response=await fetch(row.url,{cache:'no-store'});
    if (!response.ok) throw new Error(`S22 asset HTTP ${response.status}: ${row.url}`);
    const bytes=await response.arrayBuffer();
    const digest=await crypto.subtle.digest('SHA-256',bytes);
    const hash=Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('');
    if (hash!==row.sha256) throw new Error(`S22 asset SHA mismatch: ${row.id}`);
    const bitmap=await createImageBitmap(new Blob([bytes],{type:'image/png'}));
    if (bitmap.width!==1672 || bitmap.height!==941) throw new Error(`S22 canvas mismatch: ${row.id}`);
    return bitmap;
  })());
  return bitmaps.get(row.url);
}
async function tailLock() {
  const response=await fetch(new URL('./tail_lock.json',import.meta.url),{cache:'no-store'});
  if (!response.ok) throw new Error(`S22 tail lock HTTP ${response.status}`);
  return response.json();
}
export async function preflight() {
  const resources=await Promise.all(EXPOSURES.map(async row=>{
    const im=await image(row);return {id:row.id,status:200,sha256:row.sha256,size:[im.width,im.height]};
  }));
  const lock=await tailLock();
  return {fps:FPS,duration:DURATION,frames:TOTAL_FRAMES,drawings:resources.length,resources,tailStatus:lock.status,sceneReferenceSHA256:CONFIG.sceneReferenceSHA256};
}
async function assertTailApproved() {
  if (approved) return;
  const lock=await tailLock();
  if (lock.status!=='approved' || !lock.approved_tail_commit) throw new Error('S22_TAIL_FREEZE_REQUIRED: waiting for Astra final tail lock; full scene rendering is paused.');
  for (const id of ['F108','F114']) {
    if (lock.approved_final_RGBA?.[id]!==EXPOSURES.find(row=>row.id===id).sha256) throw new Error(`S22 final tail lock SHA mismatch: ${id}`);
  }
  approved=true;
}
// This step belongs only to the approved background turtle. Human motion is
// exclusively selected from the12 drawings; no old hand action is retained.
function turtleStep(t) {
  let value=0;for(let k=0;k<4;k++) value+=sstep(1.4+k,1.72+k,t);return value;
}
function renderScene(ctx,t,W,H,im) {
  TURTLE ||= makeTurtle();
  SCENE ||= new OffscreenCanvas(RW,RH);LIGHT ||= new OffscreenCanvas(RW,RH);
  const x=SCENE.getContext('2d'),lx=LIGHT.getContext('2d'),step=turtleStep(t);
  x.setTransform(1,0,0,1,0,0);x.globalCompositeOperation='source-over';x.globalAlpha=1;x.filter='none';x.clearRect(0,0,RW,RH);
  // Approved S22 backstage cloth, folds and actual existing turtle asset.
  const g=x.createRadialGradient(1250,180,80,1150,320,1500);
  g.addColorStop(0,'#f6d7a2');g.addColorStop(.5,'#cf9152');g.addColorStop(1,'#3e2615');x.fillStyle=g;x.fillRect(0,0,RW,RH);
  x.save();x.filter='blur(5px)';x.strokeStyle='rgba(120,80,45,0.28)';x.lineWidth=3;
  for(let i=0;i<10;i++){const x0=120+i*190+30*Math.sin(i);x.beginPath();x.moveTo(x0,0);x.quadraticCurveTo(x0+20,540,x0-10,RH);x.stroke();}x.restore();
  x.save();x.filter='blur(4px)';x.globalAlpha=.9;
  const tp=turtlePose(t,{facing:1,walk:step%1>.02&&step%1<.98?1:.15,neckOut:.7});
  x.translate(1380+step*26,330-step*22);x.scale(1.2,-1.2);x.rotate(.08);drawPuppet(x,TURTLE,tp,'r');x.restore();
  // The actual RGBA frame already contains the correct one-group composition
  // and displacement. Uniform width scale only; no extra actor movement/rod.
  if(im){const sc=RW/im.width;x.drawImage(im,0,0,RW,im.height*sc);}
  lx.setTransform(1,0,0,1,0,0);lx.globalCompositeOperation='source-over';lx.globalAlpha=1;lx.filter='none';
  const lg=lx.createRadialGradient(500,-100,100,700,200,1800),fl=1+.03*Math.sin(t*11)+.02*Math.sin(t*23);
  lg.addColorStop(0,`rgb(255,${Math.round(236*Math.min(1,fl))},${Math.round(200*Math.min(1,fl))})`);lg.addColorStop(.6,'rgb(230,190,150)');lg.addColorStop(1,'rgb(90,62,48)');lx.fillStyle=lg;lx.fillRect(0,0,RW,RH);
  x.globalCompositeOperation='multiply';x.drawImage(LIGHT,0,0);x.globalCompositeOperation='source-over';
  // Approved global camera and vignette, with scene light applied once above.
  ctx.save();ctx.setTransform(W/RW,0,0,H/RH,0,0);const z=1+.05*sstep(0,5,t);ctx.translate(RW/2,RH/2);ctx.scale(z,z);ctx.translate(-RW/2,-RH/2);ctx.drawImage(SCENE,0,0);ctx.restore();
  ctx.save();ctx.setTransform(W/RW,0,0,H/RH,0,0);const v=ctx.createRadialGradient(RW*.5,RH*.45,RH*.35,RW*.5,RH*.5,RH);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,0.55)');ctx.fillStyle=v;ctx.fillRect(0,0,RW,RH);ctx.restore();
  const gi=ctx.getImageData(0,0,W,H),G=gi.data;let sd=Math.floor(t*24)*7919+22;
  const r2=()=>((sd=(sd*16807)%2147483647)/2147483647);
  for(let i=0;i<G.length;i+=4){const n=(r2()-.5)*6;G[i]+=n;G[i+1]+=n;G[i+2]+=n;}ctx.putImageData(gi,0,0);
}
// Preparation may check this approved environment without drawing pending tails.
export async function renderEnvironment(ctx,t,W,H){renderScene(ctx,+t||0,W,H,null);}
export async function renderFrame(ctx,t,W,H){await assertTailApproved();const time=Math.max(0,Math.min(DURATION,+t||0));renderScene(ctx,time,W,H,await image(exposureAt(time)));}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||0,W,H);}
