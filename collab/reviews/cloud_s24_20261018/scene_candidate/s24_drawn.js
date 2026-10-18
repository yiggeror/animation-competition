// Isolated S24 scene entry. Production source, EDL, audio and ready are untouched.
// Native drawings are the only character; the inherited lamp renderer handles room/light/sheet.
import { renderShot } from '../../../../js/lamp/s06_key.js';
import { sheet as sheet23 } from '../../../../js/lamp/shots/s23.js';
import { flatMaps } from '../../../../js/lamp/s08_back.js';

export const DURATION = 2.5;
export const FPS = 24;
export const FRAME_COUNT = 60;
export const SOURCE_SCENE_COMMIT = 'c920857531ac60a63d1b09a848698854856ab657';
export const CAM = Object.freeze({pos:[3.15,1.62,1.12],target:[1.80,0.62,0.98],hfov:46});
export const SCENE_CONFIG = Object.freeze({exp:0.22,fog:0.5,sheetTimeOffset:3.4,sheetTimeScale:0.1,depthBase:[1.98,0.78,0.47]});
export const REGISTRATION = Object.freeze({native:[1024,1536],canvas:[1920,1080],scale:0.70,x:590,y:20});
const ASSET_ROOT = '/collab/reviews/cloud_s24_20261018/d08_d09_final_segment/candidates/';
export const EXPOSURES = Object.freeze([
  {id:'d01',start:0,hold:6,sha256:'0485c6fe2ee6ec05d762a6b1c531ed9764e7e77223b6cce455b54f50f99eff22'},
  {id:'d02',start:6,hold:3,sha256:'4e363b28a951d7adafcbbe7bb41700086dfa91de0c6fc20ba9bac0641d52af4c'},
  {id:'d03',start:9,hold:3,sha256:'fa1d4ae70a784d1694d27c674ad28cc9357ced1e6686f9fda8718a60daa65532'},
  {id:'d04',start:12,hold:3,sha256:'dcbe1e529b03b963f56769e4f0c381cbca5bd2735cdb75d01bbce5f0cd0296c6'},
  {id:'d05',start:15,hold:4,sha256:'3eaef2e1fa5e99c308dd46de105bb38d8e97e331f3b801763da152e2aa6ca1ce'},
  {id:'d06',start:19,hold:5,sha256:'d5f04b6b949a6b96a0c39ec8fe8850f7b2b30f00af835bbe38ddf53c66b4c1a3'},
  {id:'d07',start:24,hold:8,sha256:'44137d740ac5d07ca0258019c28cdf8f9b648d77ba79eda07f366f24503753db'},
  {id:'d08',start:32,hold:8,sha256:'cd01c1cc946011cc5d050498a16c83a84d197ca25221792e779bdd5d9d4e3e43'},
  {id:'d09',start:40,hold:20,sha256:'724d5c1c2516e4720bd1905e14b1bfd104f142fe41bc399877963886b69816b8'},
].map(e=>Object.freeze({...e,end:e.start+e.hold-1,path:ASSET_ROOT+`F${String(e.start).padStart(3,'0')}.png`})));
export const SHEET = EXPOSURES.map(e=>[e.path,e.start]);

export function pickExposure(t) {
  if (!Number.isFinite(t) || t < 0 || t >= DURATION) throw new RangeError('S24 supports only frames000–059.');
  const f = Math.floor(t*FPS+1e-6);
  const e = EXPOSURES.find(e=>f>=e.start && f<=e.end);
  if (!e) throw new RangeError('S24 exposure gap.');
  return e;
}
export function registrationMatrix(W,H) {
  if (!(W>0 && H>0) || Math.abs(W/H-16/9)>1e-9) throw new RangeError('S24 output must be16:9.');
  const k=W/1920;
  return [0.70*k,0,0,0.70*k,590*k,20*k];
}

let finalLockPromise;
async function requireFinalLock() {
  finalLockPromise ||= (async()=>{
    const response=await fetch(new URL('./final_lock.json',import.meta.url));
    if (!response.ok) throw new Error('S24 final lock record missing.');
    const lock=await response.json();
    if (lock.approved!==true || lock.status!=='ASTRA_FINAL_DUAL_LOCKED_ALL9') {
      throw new Error('S24 F032/F040 final dual lock pending; actual scene render is gated.');
    }
    if (lock.assets.length!==EXPOSURES.length) throw new Error('S24 lock asset count mismatch.');
    for (const e of EXPOSURES) {
      const r=lock.assets.find(r=>r.start===e.start);
      if (!r || r.sha256!==e.sha256 || r.hold!==e.hold) throw new Error(`S24 lock mismatch F${e.start}.`);
    }
    return lock;
  })();
  return finalLockPromise;
}
const mapCache=new Map();
async function nativeMaps(e) {
  if (!mapCache.has(e.path)) mapCache.set(e.path,(async()=>{
    const response=await fetch(e.path);
    if (!response.ok) throw new Error(`S24 native asset missing: ${e.path}`);
    const bytes=await response.arrayBuffer();
    const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
    if (digest!==e.sha256) throw new Error(`S24 native SHA mismatch: ${e.path}`);
    const native=await createImageBitmap(new Blob([bytes],{type:'image/png'}));
    if (native.width!==1024 || native.height!==1536) throw new Error('S24 native dimensions changed.');
    // Ordinary opaque diffuse material; native pigment/ink/shading remain intact.
    // No emission, face warp, pose interpolation, flip, rotation or code character.
    return flatMaps(native,0);
  })());
  return mapCache.get(e.path);
}
export async function renderFrame(ctx,t,W,H) {
  const exposure=pickExposure(t),m=registrationMatrix(W,H);
  await requireFinalLock();
  const maps=await nativeMaps(exposure);
  const shot={cam:CAM,exp:SCENE_CONFIG.exp,fog:SCENE_CONFIG.fog,
    sheet:(u,env)=>sheet23(3.4+0.1*u,env),
    cards:async(CARDS,cam)=>{
      const depth=cam.project(SCENE_CONFIG.depthBase)[2];
      CARDS.addImage([{maps,m}],depth);
    }};
  return renderShot(ctx,t,W,H,shot);
}
