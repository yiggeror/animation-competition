// Existing S06 repair: 86 frames / two unplug-replug attempts, six locked arm drawings + one eye overlay.
import {renderPaint,loadImg} from '../paint/paintshot.js';
export const SIZE=[1672,941],DURATION=86/24,SOCKET=[450,886],PHONE_PORT=[888,685];
export const APPROVED_ENDPOINTS={0:{usb:[421,721],base:[450,886]},6:{usb:[421,721],base:[450,886]},11:{usb:[421.7,676.7],base:[450.3,840.6]},14:{usb:[421.7,659],base:[449.4,822]},18:{usb:[422.7,640.4],base:[450.3,806.1]},27:{usb:[421.7,696],base:[449,858]}};
// All six arm states locked by parent; local candidate factory, production integration remains with coordinator.
export const SHEET_000_033_CANDIDATE=[[0,0],[6,6],[11,11],[14,14],[18,18],[14,21],[11,24],[27,27],[6,30]];
export const SHEET_86_UNIQUE=[[0,0,false],[6,6,false],[11,11,false],[14,14,false],[18,18,false],[14,21,false],[11,24,false],[27,27,false],[6,30,false],[0,34,true],[0,40,false],[6,43,false],[27,46,false],[11,49,false],[14,52,false],[18,55,false],[14,59,false],[11,62,false],[27,66,false],[6,70,false],[0,74,false],[0,78,true]];
const poly=(c,p,f,s='#655b4c',w=1.8)=>{c.beginPath();c.moveTo(...p[0]);for(const q of p.slice(1))c.lineTo(...q);c.closePath();c.fillStyle=f;c.fill();if(s){c.strokeStyle=s;c.lineWidth=w;c.stroke();}};
function path(c,p){c.beginPath();c.moveTo(...p[0]);for(let i=1;i+2<p.length;i+=3)c.bezierCurveTo(...p[i],...p[i+1],...p[i+2]);}
function cord(c,p,w=4.1,floor=false){c.save();c.lineCap='round';c.lineJoin='round';if(floor){c.translate(0,3);c.filter='blur(2.8px)';c.strokeStyle='rgba(35,29,22,.24)';c.lineWidth=w+4;path(c,p);c.stroke();c.translate(0,-3);c.filter='none';}c.strokeStyle='#716b5e';c.lineWidth=w+2.2;path(c,p);c.stroke();c.strokeStyle='#d5d0bd';c.lineWidth=w;path(c,p);c.stroke();c.restore();}
function ellipse(c,x,y,rx,ry,a,blur){c.save();c.filter=`blur(${blur}px)`;c.fillStyle=`rgba(31,27,21,${a})`;c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill();c.restore();}
export function neutralFloorAndMat(room,makeCanvas=(w,h)=>new OffscreenCanvas(w,h)){
 const cv=makeCanvas(...SIZE),c=cv.getContext('2d');
 // Approved-room concrete albedo only. Moonlight remains in the shared paint stage.
 c.drawImage(room,820,640,390,220,0,0,...SIZE);
 const mat=[[728,-30],[1705,-30],[1705,907],[904,900],[728,757]];
 c.save();c.filter='blur(6px)';poly(c,mat,'rgba(43,32,17,.27)',null);c.restore();poly(c,mat,'#c8ae78','#887348',3);
 c.save();c.beginPath();c.moveTo(...mat[0]);for(const p of mat.slice(1))c.lineTo(...p);c.closePath();c.clip();
 for(let x=715,i=0;x<1730;x+=11,i++){c.strokeStyle=i%3===0?'rgba(93,70,37,.35)':'rgba(114,89,49,.27)';c.lineWidth=1.1;c.beginPath();c.moveTo(x,-30);c.lineTo(x+18,940);c.stroke();c.strokeStyle='rgba(236,214,164,.27)';c.beginPath();c.moveTo(x+2,-30);c.lineTo(x+20,940);c.stroke();}
 for(let y=45;y<940;y+=112){c.strokeStyle='rgba(107,82,43,.15)';c.lineWidth=1.4;c.beginPath();c.moveTo(720,y);c.lineTo(1680,y+15);c.stroke();}c.restore();
 c.strokeStyle='#907444';c.lineWidth=5;c.beginPath();c.moveTo(728,757);c.lineTo(904,900);c.lineTo(1672,907);c.stroke();
 c.strokeStyle='#e0c793';c.lineWidth=1.5;for(let x=906;x<1672;x+=9){const y=900+(x-904)*7/768;c.beginPath();c.moveTo(x,y-2);c.lineTo(x+3,y+2);c.stroke();}return cv;
}
export function drawNearStrip(c,base=SOCKET){
 cord(c,[[304,898],[238,927],[118,936],[-15,907]],5.4,true);ellipse(c,530,929,242,10,.24,4.5);
 poly(c,[[300,876],[356,909],[762,917],[759,935],[354,927],[300,896]],'#c9c1af');poly(c,[[300,876],[697,884],[762,917],[356,909]],'#e8e2d2');
 c.strokeStyle='#5b564a';c.lineWidth=3.2;c.lineCap='round';for(const[x,y]of[...(base[1]<883?[[430,884],[462,886]]:[]),[576,895],[596,896],[661,899],[680,900]]){c.beginPath();c.moveTo(x,y-2);c.lineTo(x+1.4,y+4);c.stroke();}c.fillStyle='#888679';c.beginPath();c.ellipse(721,912,3,2,0,0,Math.PI*2);c.fill();
 const lift=Math.max(0,886-base[1]);ellipse(c,455+lift*.08,889,45+lift*.1,4+lift*.055,lift<3?.27:.13,lift<3?2:5+lift*.04);
}
export function drawBodyContact(c){ellipse(c,1382,858,230,25,.15,10);ellipse(c,1333,868,53,10,.26,4);ellipse(c,1580,826,110,12,.18,7);}
export function drawPhoneCable(c,usb=[421,721]){
 const[x,y]=usb;
 // Flexible USB cord turns gently from the top plug, then drops below both ends.
 // Midspan rests at mat/floor height; foreground arm naturally occludes it.
 const p=[[x,y],[x,y-17],[x-30,y-17],[390,770],[388,826],[494,849],[628,830],[756,813],[831,743],PHONE_PORT];
 c.save();c.translate(0,4);c.filter='blur(3.1px)';c.strokeStyle='rgba(31,26,21,.22)';c.lineWidth=6;path(c,[[390,793],[402,835],[505,849],[628,830]]);c.stroke();c.restore();
 cord(c,p,3.6,false);
}
export function drawPhoneConnector(c){c.save();c.translate(...PHONE_PORT);c.rotate(.31);c.fillStyle='#c8c5b9';c.strokeStyle='#655f54';c.lineWidth=1;c.beginPath();c.roundRect(-5,-2.4,7,4.8,1);c.fill();c.stroke();c.restore();}
export const MOONLIGHT={ambient:[.16,.18,.26],lights:[],shafts:[{poly:[[0,0],[610,0],[1219,941],[0,941]],color:[.5,.62,.95],i:.42,soft:105}],exposure:1,vignette:.5,grain:8};
export function makeS06Shot({room,characters,endpoints=APPROVED_ENDPOINTS,eyePhone=null,sheet=SHEET_000_033_CANDIDATE,through=33,makeCanvas=(w,h)=>new OffscreenCanvas(w,h)}){
 const bg=neutralFloorAndMat(room,makeCanvas);return{size:SIZE,bg,light:()=>MOONLIGHT,cam:()=>({x:836,y:470.5,fit:1}),layers:async t=>{
  const f=Math.floor(t*24+1e-6);if(f<0||f>85)throw new RangeError('S06 is exactly frames 000–085');if(f>through)throw new Error('S06 requested beyond reviewed through-frame; no silent hold');let k=0,eye=false;for(const[key,at,glance]of sheet)if(f>=at){k=key;eye=!!glance;}if(eye&&!eyePhone)throw new Error('Independent phone-glance eye asset not yet approved; no fake full86 render');
  if(!characters[k]||!endpoints[k])throw new Error(`Unapproved/missing S06 F${String(k).padStart(3,'0')}; no silent hold over an unmade action`);
  const under=makeCanvas(...SIZE),u=under.getContext('2d');drawNearStrip(u,endpoints[k].base);drawBodyContact(u);drawPhoneCable(u,endpoints[k].usb);
  const over=makeCanvas(...SIZE);drawPhoneConnector(over.getContext('2d'));return[{img:under,x:0,y:0,sc:1},{img:characters[k],x:0,y:0,sc:1},...(eye?[{img:eyePhone,x:0,y:0,sc:1}]:[]),{img:over,x:0,y:0,sc:1}];}};
}

// Production adapter only: shared paint pipeline, existing background, and seven locked PNGs.
export const FRAME_COUNT=86;
export const SHEET=SHEET_86_UNIQUE;
const ROOT='/assets/chars/s06/';
const ARM_FILES={0:'S06_F000.png',6:'S06_F006.png',11:'S06_F011.png',14:'S06_F014.png',18:'S06_F018.png',27:'S06_F027.png'};
let shotPromise;
async function requiredImage(path){
 const im=await loadImg(path);
 if(!im)throw new Error('S06 missing locked image: '+path);
 if(im.width!==1672||im.height!==941)throw new Error('S06 registered canvas changed: '+path);
 return im;
}
export function productionShot(){
 if(!shotPromise)shotPromise=(async()=>{
  const [room,eyePhone,...arms]=await Promise.all([requiredImage('/assets/paint/bg_01_room_wide.png'),requiredImage(ROOT+'S06_EYES_PHONE.png'),...Object.values(ARM_FILES).map(p=>requiredImage(ROOT+p))]);
  const characters=Object.fromEntries(Object.keys(ARM_FILES).map((k,i)=>[k,arms[i]]));
  return makeS06Shot({room,characters,eyePhone,sheet:SHEET_86_UNIQUE,through:85});
 })();
 return shotPromise;
}
export async function renderFrame(ctx,t,W,H){return renderPaint(ctx,t,W,H,await productionShot());}

export const FPS=24;
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
