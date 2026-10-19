// S15 · 第 6 场：鹤亮相。前 3 秒，奶奶把鹤从离床单 35 厘米的地方慢慢推过来——床单上一个又大又虚的影子渐渐变小、变清楚，
// "贴"上床单；然后接第 6 场关键镜头的亮相（低头 → 扬起脖子 → 收住），小满从抱着胳膊到看呆了。
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
].map(e=>Object.freeze({...e,end:e.start+e.hold-1,path:'/assets/chars/x15/'+e.id+'.png'})));
export function pickExposure(t) {
  if (!Number.isFinite(t) || t < 0 || t >= DURATION) throw new RangeError('S15 drawn supports t in [0,8).');
  const frame=Math.floor(t*FPS+1e-6);
  const e=EXPOSURES.find(e=>frame>=e.start && frame<=e.end);
  if(!e)throw new Error('S15 exposure gap at frame '+frame);
  return e;
}
const mapsCache=new Map();
async function drawingMaps(e) {
  if(!mapsCache.has(e.path))mapsCache.set(e.path,(async()=>{
    const r=await fetch(e.path);if(!r.ok)throw new Error('Missing S15 drawing '+e.path);
    const im=await createImageBitmap(await r.blob());
    if(im.width!==1254||im.height!==1254)throw new Error('S15 drawing native dimensions changed: '+e.path);
    return flatMaps(im,0);
  })());
  return mapsCache.get(e.path);
}
const cards = async (CARDS, cam, t) => {
  const e=pickExposure(t),maps=await drawingMaps(e),R=REGISTRATION;
  const base=xmWorld([0,0]);
  base[2]=(R.floorY-R.oy)/R.sc/100;
  const depth=cam.project(base)[2];
  CARDS.addImage([{maps,m:billboardM(cam,base,R.ox,R.oy,R.sc)}],depth);
};


export function camera(W, H, o = {}) {
  const C = o.pos || [1.48, -3.013, 0.34], T = o.target || [0.75, 0.0, 1.0], hfov = o.hfov || 60;
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const nrm = (a) => { const l = Math.hypot(...a); return a.map((v) => v / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const fwd = nrm(sub(T, C)), right = nrm(cross(fwd, [0, 0, 1])), up = cross(right, fwd);
  const focal = (W / 2) / Math.tan((hfov * Math.PI) / 360);
  const project = (P) => {
    const d = sub(P, C);
    const z = d[0] * fwd[0] + d[1] * fwd[1] + d[2] * fwd[2];
    const x = d[0] * right[0] + d[1] * right[1] + d[2] * right[2];
    const y = d[0] * up[0] + d[1] * up[1] + d[2] * up[2];
    return [W / 2 + (x / z) * focal, H / 2 - (y / z) * focal, Math.hypot(...d), focal / z];
  };
  return { C, fwd, right, up, focal, project };
}


export function billboardM(cam, base, ox, oy, sc) {
  const P = (px, py) => {
    const x = (px - ox) / sc / 100, y = (oy - py) / sc / 100;
    const r = cam.project([base[0] + cam.right[0] * x + cam.up[0] * y, base[1] + cam.right[1] * x + cam.up[1] * y, base[2] + cam.right[2] * x + cam.up[2] * y]);
    return [r[0], r[1]];
  };
  const p0 = P(0, 0), p1 = P(100, 0), p2 = P(0, 100);
  return [(p1[0] - p0[0]) / 100, (p1[1] - p0[1]) / 100, (p2[0] - p0[0]) / 100, (p2[1] - p0[1]) / 100, p0[0], p0[1]];
}


const frames=Array.from({length:192},(_,f)=>({f,id:pickExposure(f/24).id}));
const counts={};for(const r of frames)counts[r.id]=(counts[r.id]||0)+1;
const R=REGISTRATION,cam=camera(1920,1080),m=billboardM(cam,[.5,-1.45,.22],R.ox,R.oy,R.sc);
const p=([x,y])=>[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]];
console.log(JSON.stringify({counts,total:frames.length,registration:R,m,projected:{crown:p([560,28]),seat:p([540,835]),nearSole:p([825,1200]),farSole:p([965,1190]),figureMin:p([350,28]),figureMax:p([1025,1200])},cameraUnchanged:true,sheetRevealSeconds:3,fullSceneRender:false},null,2));
