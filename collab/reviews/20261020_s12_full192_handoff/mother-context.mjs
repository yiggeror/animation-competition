/* Extracted approved F052 context, no diagnostic prop raster or single-frame wrapper. */
export function createMotherContext({loadImg}) {
const W=1920,H=1080,LINE="#3e2a1e";
const BOX={x0:1000,x1:1860,rim:800,back:760,floor:1040,lidH:310};
const REGISTRATION={scale:.7,x:275,y:112};
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
async function backgroundWithPressure() {
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

return {backgroundWithPressure,front,nativeContactShadows,BOX,REGISTRATION};
}
