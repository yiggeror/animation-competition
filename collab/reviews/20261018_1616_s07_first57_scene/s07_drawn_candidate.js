// S07 first57 frames complete: original phone and repaired hair tail remain fixed. NOT whole108 ready.
// Added locked G025/028/031/034/037. Allowed F000-F056; independent F057-F107 still throw.
// Uses original frozen 1672x941 scene/camera/props. No generated-code person/rig/flip.
import { renderPaint } from '/js/paint/paintshot.js';
import { COIL, COILC } from '/js/paint/shots/s01.js';
import { stool, EASE } from '/js/anim/kit.js';
import { darkLight, fan } from '/js/anim/s04.js';
import { tableLamp, GM_AT, GM_K } from '/js/anim/s01.js';
export const DURATION = 4.5;
export const AVAILABLE_FRAME_RANGES = [[0,56]];
const R='/collab/reviews/';
const N=new URL('./frames/',import.meta.url).href;
export const GRANDMA = [
 [0,R+'20261018_1251_pose_bases/S07_grandma_F000/production/F000_grandma_rgba.png'],
 [8,R+'20261018_1321_opening_tails/S07_grandma_008/production/F008_grandma_rgba.png'],
 [16,R+'20261018_1351_opening_locked/S07_grandma_016/production/F016_grandma_rgba.png'],
 [18,R+'20261018_1351_opening_locked/S07_grandma_018/production/F018_grandma_rgba.png'],
 [22,R+'20261018_1425_s07_partial_scene/S07_grandma_022/production/F022_grandma_rgba.png'],
 [25,N+'F025_grandma_rgba.png'],
 [28,N+'F028_grandma_rgba.png'],
 [31,N+'F031_grandma_rgba.png'],
 [34,N+'F034_grandma_rgba.png'],
 [37,N+'F037_grandma_rgba.png'],
];
export const XIAOMAN = [
 [0,R+'20261018_1152_first_candidate_and_interfaces/S07_xiaoman/candidates/F000_v2_fingers_clean_v4.png'],
 [3,R+'20261018_1232_s07_release/approved/F003_fully_released.png'],
 [6,R+'20261018_1232_s07_release/approved/F006_near_edge.png'],
 [8,R+'20261018_1232_s07_release/approved/F008_phone_landed.png'],
 [39,R+'20261018_1539_s07_tail_scene/candidates/F039_tail_phone_clear.png'],
 [43,R+'20261018_1539_s07_tail_scene/candidates/F043_tail_phone_clear.png'],
 [46,R+'20261018_1539_s07_tail_scene/candidates/F046_tail_phone_clear.png'],
 [49,R+'20261018_1539_s07_tail_scene/candidates/F049_tail_phone_clear.png'],
 [53,R+'20261018_1539_s07_tail_scene/candidates/F053_tail_phone_clear.png'],
];
export const PHONE=R+'20261018_1232_s07_release/approved/phone_landed_only_same_registration.png';
const pick=(sheet,f)=>{let p=sheet[0][1];for(const [k,q] of sheet)if(f>=k)p=q;return p;};
const clamp=v=>Math.min(1,Math.max(0,v));
export function camera(t){
 const f=Math.floor(t*24+1e-6);
 if(f>=16&&f<39){const u=clamp((t-1.05)/(1.6-1.05));return {x:1024,y:630-90*EASE.io(u),fit:1672/608};}
 if(f>=39&&f<57)return {x:605,y:637.5,fit:1672/400};
 return {x:816,y:482.5,fit:1.04};
}
let seat;
function stoolLayer(){
 if(!seat){const c=new OffscreenCanvas(1672,941),x=c.getContext('2d');x.translate(...GM_AT);x.scale(-GM_K,GM_K);stool(x,-2);seat={img:c,x:0,y:0,sc:1,contact:{a:.45,blur:3,sy:-.1,skew:.5}};}
 return seat;
}
export function authoredLayers(f){
 if(!AVAILABLE_FRAME_RANGES.some(([a,b])=>f>=a&&f<=b))throw Error('S07 partial candidate: visible drawn states missing at F'+f);
 const layers=[];
 if(f<16||f>=39){
   // F000..008 include their own phone. In supine states the separately locked phone stays behind body.
   if(f>=39)layers.push({img:PHONE,x:430,y:533,sc:.16});
   layers.push({img:pick(XIAOMAN,f),x:f<39?430:339.7325,y:f<39?533:512.485,sc:f<39?.16:.2475,contact:{a:.4,blur:3,sy:1,dx:-2,dy:3}});
 }
 if(f<39)layers.push({img:pick(GRANDMA,f),x:730,y:375,sc:.2734375,contact:{a:.45,blur:4,sy:-.07,skew:.5}});
 return layers;
}
const shot={bg:'bg_01_room_wide',size:[1672,941],
 layers:async(t)=>{const f=Math.floor(t*24+1e-6);return [
 {img:COILC,x:COIL[0]-60,y:COIL[1]-34,sc:1},tableLamp(0),stoolLayer(),...authoredLayers(f)];},
 light:t=>darkLight(t,0),
 glow:()=>[{x:COIL[0]-20,y:COIL[1]+1,r:4,color:[255,90,40],a:.9,core:.3}],
 emit:x=>fan(x,0),cam:camera};
export async function renderFrame(ctx,t,W,H){return renderPaint(ctx,t,W,H,shot);}
