// S07 complete108 drawn candidate. First57 camera/person/contact choreography preserved.
// F057+ eleven locked whole drawings, one fixed registration; F100+ embedded original physical lamp replaces tableLamp.
// Actual whole-scene rendering still required before ready.
import { renderPaint } from '/js/paint/paintshot.js';
import { COIL, COILC } from '/js/paint/shots/s01.js';
import { stool, EASE } from '/js/anim/kit.js';
import { darkLight, fan } from '/js/anim/s04.js';
import { tableLamp, GM_AT, GM_K } from '/js/anim/s01.js';
export const DURATION = 4.5;
export const AVAILABLE_FRAME_RANGES = [[0,107]];
export const GRANDMA_WALK = [[57,"/assets/chars/g07/F057.png"],[62,"/assets/chars/g07/F062.png"],[68,"/assets/chars/g07/F068.png"],[73,"/assets/chars/g07/F073.png"],[79,"/assets/chars/g07/F079.png"],[84,"/assets/chars/g07/F084.png"],[90,"/assets/chars/g07/F090.png"],[95,"/assets/chars/g07/F095.png"],[100,"/assets/chars/g07/F100.png"],[103,"/assets/chars/g07/F103.png"],[106,"/assets/chars/g07/F106.png"]];
export const WALK_REGISTRATION={s:0.36410361842105265,x:627.0254537171638,y:402.7604324894813};
export const LAMP_EMBEDDED_FROM=100;
export const GRANDMA = [[0,"/assets/chars/g07/F000.png"],[8,"/assets/chars/g07/F008.png"],[16,"/assets/chars/g07/F016.png"],[18,"/assets/chars/g07/F018.png"],[22,"/assets/chars/g07/F022.png"],[25,"/assets/chars/g07/F025.png"],[28,"/assets/chars/g07/F028.png"],[31,"/assets/chars/g07/F031.png"],[34,"/assets/chars/g07/F034.png"],[37,"/assets/chars/g07/F037.png"]];
export const XIAOMAN = [[0,"/assets/chars/x07/F000.png"],[3,"/assets/chars/x07/F003.png"],[6,"/assets/chars/x07/F006.png"],[8,"/assets/chars/x07/F008.png"],[39,"/assets/chars/x07/F039.png"],[43,"/assets/chars/x07/F043.png"],[46,"/assets/chars/x07/F046.png"],[49,"/assets/chars/x07/F049.png"],[53,"/assets/chars/x07/F053.png"]];
export const PHONE="/assets/chars/x07/phone_landed.png";
const pick=(sheet,f)=>{let p=sheet[0][1];for(const [k,q] of sheet)if(f>=k)p=q;return p;};
const clamp=v=>Math.min(1,Math.max(0,v));
export function camera(t){
 const f=Math.floor(t*24+1e-6);
 if(f>=16&&f<39){const u=clamp((t-1.05)/(1.6-1.05));return {x:1024,y:630-90*EASE.io(u),fit:1672/608};}
 if(f>=39&&f<57)return {x:605,y:637.5,fit:1672/400};
 return {x:816,y:482.5,fit:1.04};
}
// Original S01 matchbox is independent of the lamp lift. Keep its original lit layer slot.
let matchbox;
export function tableMatchboxOnly(){
 if(!matchbox){const c=new OffscreenCanvas(220,200),x=c.getContext('2d');
 x.fillStyle='#c9a25a';x.strokeStyle='#3e2a1e';x.lineWidth=1;
 x.beginPath();x.rect(150,162,18,7);x.fill();x.stroke();
 matchbox={img:c,x:1152,y:472,sc:1};}
 return matchbox;
}
let seat;
function stoolLayer(){
 if(!seat){const c=new OffscreenCanvas(1672,941),x=c.getContext('2d');x.translate(...GM_AT);x.scale(-GM_K,GM_K);stool(x,-2);seat={img:c,x:0,y:0,sc:1,contact:{a:.45,blur:3,sy:-.1,skew:.5}};}
 return seat;
}
export function authoredLayers(f){
 if(!AVAILABLE_FRAME_RANGES.some(([a,b])=>f>=a&&f<=b))throw Error('S07 frame outside [0,107]: '+f);
 const layers=[];
 if(f<16||f>=39){
   // F000..008 include their own phone. In supine states the separately locked phone stays behind body.
   if(f>=39)layers.push({img:PHONE,x:430,y:533,sc:.16});
   layers.push({img:pick(XIAOMAN,f),x:f<39?430:339.7325,y:f<39?533:512.485,sc:f<39?.16:.2475,contact:{a:.4,blur:3,sy:1,dx:-2,dy:3}});
 }
 if(f<39)layers.push({img:pick(GRANDMA,f),x:730,y:375,sc:.2734375,contact:{a:.45,blur:4,sy:-.07,skew:.5}});
 if(f>=57){
   const at={x:WALK_REGISTRATION.x,y:WALK_REGISTRATION.y,sc:WALK_REGISTRATION.s};
   const contact={a:.45,blur:4,sy:-.07,skew:.5};
   if(f>=100){
     // Shadow ownership: human alpha only; the visible full drawing owns the physical lamp/table ellipse.
     const id=f>=106?'F106':f>=103?'F103':'F100';
     layers.push({img:'/assets/chars/g07/'+id+'_person_shadow.png',...at,alpha:0,contact});
     layers.push({img:pick(GRANDMA_WALK,f),...at});
   }else layers.push({img:pick(GRANDMA_WALK,f),...at,contact});
 }
 return layers;
}
const shot={bg:'bg_01_room_wide',size:[1672,941],
 layers:async(t)=>{const f=Math.floor(t*24+1e-6);return [
 {img:COILC,x:COIL[0]-60,y:COIL[1]-34,sc:1},...(f<LAMP_EMBEDDED_FROM?[tableLamp(0)]:[tableMatchboxOnly()]),stoolLayer(),...authoredLayers(f)];},
 light:t=>darkLight(t,0),
 glow:()=>[{x:COIL[0]-20,y:COIL[1]+1,r:4,color:[255,90,40],a:.9,core:.3}],
 emit:x=>fan(x,0),cam:camera};
export async function renderFrame(ctx,t,W,H){return renderPaint(ctx,t,W,H,shot);}
