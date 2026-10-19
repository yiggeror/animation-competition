// S12 F012 ONLY diagnostic, actual time .5. Actual native art, no old G/groupM/action/rig pose logic.
import {renderPaint,loadImg} from '../../../../../../js/paint/paintshot.js';
import {makeCrane} from '../../../../../../js/lamp/crane.js';
import {drawPuppet} from '../../../../../../js/puppet.js';
export const DURATION=13/24;
const W=1920,H=1080,LINE='#3e2a1e';
export const BOX={x0:1000,x1:1860,rim:800,back:760,floor:1040,lidH:310};
export const REGISTRATION=Object.freeze({scale:.70,x:275,y:112});
let setupPromise;
async function setup(){
 setupPromise ||= (async()=>{
  const [poseData,contactData]=await Promise.all(['../../../geometry/three_key_pose_proposal.json','../qa/native_alpha_contacts_registration.json'].map(async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('missingF000data '+p);return r.json()}));
  const nativePath=new URL('../candidate/F012.png',import.meta.url).href,r=await fetch(nativePath);if(!r.ok)throw Error('missingF000native');const bytes=await r.arrayBuffer();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==contactData.native_candidate_SHA256)throw Error('F000 native SHA changed');
  const person=await createImageBitmap(new Blob([bytes],{type:'image/png'}));if(person.width!==1024||person.height!==1536)throw Error('F000 native canvas changed');
  const masks=await Promise.all(contactData.contacts.map(async c=>({...c,img:await loadImg(new URL(c.path,import.meta.url).href)})));
  if(masks.some(c=>!c.img))throw Error('missing F000 contactmask');
  return {person,masks,A:poseData.states[0],crane:makeCrane(1.35,'plain')};
 })();return setupPromise;
}
let ROOM = null;
async function room() {
  if (ROOM) return ROOM;
  const im = await loadImg('bg_01_room_wide');
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.filter = 'blur(24px)'; x.drawImage(im, 300, 330, 900, 506, -80, -60, W + 160, H + 120); x.filter = 'none';
  const g = x.createLinearGradient(0, 860, 0, H); g.addColorStop(0, '#77736c'); g.addColorStop(1, '#8a857b');
  x.fillStyle = g; x.fillRect(0, 860, W, H - 860);
  return (ROOM = c);
}
const lidPoly = (h) => [[BOX.x0 + 20, BOX.back], [BOX.x1 - 20, BOX.back], [BOX.x1 - 35, BOX.back - h], [BOX.x0 + 35, BOX.back - h]];
async function bgF000() {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.drawImage(await room(), 0, 0);
  // 箱盖内侧（浅色樟木板）+ 鹤的透光斑
  const lp = lidPoly(BOX.lidH), path = new Path2D(); lp.forEach((p, i) => (i ? path.lineTo(...p) : path.moveTo(...p))); path.closePath();
  x.fillStyle = '#7a3f22'; x.strokeStyle = LINE; x.lineWidth = 5; x.fill(path); x.stroke(path);
  x.save(); x.clip(path);
  x.fillStyle = '#d2a676'; x.fillRect(BOX.x0 + 40, BOX.back - BOX.lidH + 22, BOX.x1 - BOX.x0 - 80, BOX.lidH - 30);
  x.strokeStyle = 'rgba(90,50,25,0.22)'; x.lineWidth = 2;
  for (let i = 1; i < 8; i++) { const yy = BOX.back - BOX.lidH * i / 8; x.beginPath(); x.moveTo(BOX.x0 + 40, yy); x.lineTo(BOX.x1 - 40, yy + Math.sin(i) * 3); x.stroke(); }
  x.restore();
  // 箱子里：叠好的蓝印花布（箱沿到后沿一条）
  x.fillStyle = '#2f4a78'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(BOX.x0 + 10, BOX.rim); x.lineTo(BOX.x1 - 10, BOX.rim); x.lineTo(BOX.x1 - 22, BOX.back + 4); x.lineTo(BOX.x0 + 22, BOX.back + 4); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = 'rgba(235,235,225,0.7)';
  for (let i = 0; i < 16; i++) { const cx = BOX.x0 + 50 + i * 52, cy = BOX.rim - 16 + (i % 2) * 6; x.beginPath(); x.arc(cx, cy, 4, 0, 7); x.fill(); x.beginPath(); x.arc(cx + 26, cy - 9, 2.5, 0, 7); x.fill(); }
  clothPressureFold(x);
  return c;
}

function clothPressureFold(x){
 x.save();
 const path=new Path2D();path.moveTo(1010,800);path.lineTo(1850,800);path.lineTo(1838,764);path.lineTo(1022,764);path.closePath();x.clip(path);
 // A small blue cloth fold dips under the visible right belly edge;wood/box geometry stays untouched.
 x.fillStyle='rgba(17,29,49,0.44)';x.beginPath();x.moveTo(1438,793);
 x.bezierCurveTo(1462,790,1489,800,1510,797);x.bezierCurveTo(1524,795,1537,789,1547,790);
 x.lineTo(1547,796);x.bezierCurveTo(1524,801,1496,802,1475,799);x.lineTo(1438,798);x.closePath();x.fill();
 x.strokeStyle='rgba(12,19,31,0.72)';x.lineWidth=1.5;x.lineCap='round';x.beginPath();x.moveTo(1445,796);
 x.bezierCurveTo(1466,795,1486,801,1509,797);x.stroke();
 x.strokeStyle='rgba(110,139,176,0.42)';x.lineWidth=1;x.beginPath();x.moveTo(1486,787);x.quadraticCurveTo(1512,794,1538,788);x.stroke();
 x.restore();
}
let FRONT = null;
function front() {
  if (FRONT) return FRONT;
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  const g = x.createLinearGradient(0, BOX.rim, 0, BOX.floor); g.addColorStop(0, '#9a5530'); g.addColorStop(1, '#6e3a1e');
  x.fillStyle = 'rgba(20,10,5,0.35)'; x.beginPath(); x.ellipse((BOX.x0 + BOX.x1) / 2, BOX.floor, (BOX.x1 - BOX.x0) / 2 + 30, 18, 0, 0, 7); x.fill();
  x.fillStyle = g; x.strokeStyle = LINE; x.lineWidth = 5; x.beginPath(); x.rect(BOX.x0, BOX.rim, BOX.x1 - BOX.x0, BOX.floor - BOX.rim); x.fill(); x.stroke();
  x.fillStyle = '#3d2014'; x.fillRect(BOX.x0, BOX.rim, BOX.x1 - BOX.x0, 12);
  x.strokeStyle = 'rgba(60,30,15,0.35)'; x.lineWidth = 2;
  for (let i = 0; i < 8; i++) { const yy = BOX.rim + 34 + i * 26; x.beginPath(); x.moveTo(BOX.x0 + 5, yy); for (let xx = BOX.x0 + 5; xx < BOX.x1; xx += 60) x.lineTo(xx, yy + Math.sin(xx * 0.01 + i) * 4); x.stroke(); }
  x.fillStyle = '#c9a046'; x.strokeStyle = LINE; x.lineWidth = 3;
  for (const [cx, s] of [[BOX.x0, 1], [BOX.x1, -1]]) { x.beginPath(); x.moveTo(cx + 36 * s, BOX.rim); x.lineTo(cx, BOX.rim); x.lineTo(cx, BOX.rim + 60); x.closePath(); x.fill(); x.stroke(); }
  const mx = (BOX.x0 + BOX.x1) / 2; x.beginPath(); x.roundRect(mx - 34, BOX.rim + 14, 68, 74, 8); x.fill(); x.stroke();
  x.fillStyle = '#7a5a1e'; x.beginPath(); x.arc(mx, BOX.rim + 58, 8, 0, 7); x.fill();
  return (FRONT = c);
}


function nativeContactShadows(masks){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),B=REGISTRATION;
 for(const m of masks){
  x.save();x.globalAlpha=.34;x.filter='blur(3px)';
  x.translate(B.x,B.y+B.scale*m.native_contact_base_y);
  x.transform(B.scale,0,.04*B.scale,-.10*B.scale,0,0);x.translate(0,-m.native_contact_base_y);x.drawImage(m.img,0,0);x.restore();
 }
 return {img:c,x:0,y:0,sc:1};
}
function propAndRestingRods(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
let cachedShadows,cachedProps;
const sstep=(a,b,x)=>{const u=Math.max(0,Math.min(1,(x-a)/(b-a)));return u*u*(3-2*u)};
export const shot={size:[W,H],layers:async(t)=>{
 const d=await setup(),B=REGISTRATION;
 return [cachedShadows ||=nativeContactShadows(d.masks),{img:d.person,x:B.x,y:B.y,sc:B.scale},cachedProps ||=propAndRestingRods(d),{img:front(),x:0,y:0,sc:1}];
},light:(t)=>{const f=1+.04*Math.sin(t*11)+.03*Math.sin(t*23);return {ambient:[.03,.026,.03],lights:[{x:-350,y:760,r:2700*f,color:[1,.64,.32],i:1.25,falloff:1.5},{x:1350,y:560,r:760,color:[1,.7,.42],i:.35*f,falloff:1.6}],exposure:1,vignette:.5,grain:7}},glow:()=>[],cam:t=>({x:960+20*sstep(2,8,t),y:540-10*sstep(2,8,t),fit:1+.04*sstep(2,8,t)})};
export async function renderFrame(ctx,t,w,h){if(!Number.isFinite(t)||Math.floor(t*24+1e-9)!==12||t>=DURATION)throw RangeError('S12 diagnostic supports F012 only. F000 and F018+ are not rendered here.');shot.bg=await bgF000();return renderPaint(ctx,t,w,h,shot)}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h)}
