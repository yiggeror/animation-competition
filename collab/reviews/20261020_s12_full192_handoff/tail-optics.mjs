/* Exact tail-enabled original bg/room body; injected original image loader. */
export function createTailOptics({loadImg}) { const W=1920,H=1080,LINE="#3e2a1e",BOX={x0:1000,x1:1860,rim:800,back:760,floor:1040,lidH:310};
const sstep = (a, b, x) => { const u = Math.min(1, Math.max(0, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
const drawCrane=()=>{throw Error("Legacy crane fallback forbidden")};
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
async function bg(t, A, R, M, tail = null) {
  const c = new OffscreenCanvas(W, H), x = c.getContext('2d');
  x.drawImage(await room(), 0, 0);
  // 箱盖内侧（浅色樟木板）+ 鹤的透光斑
  const lp = lidPoly(BOX.lidH), path = new Path2D(); lp.forEach((p, i) => (i ? path.lineTo(...p) : path.moveTo(...p))); path.closePath();
  x.fillStyle = '#7a3f22'; x.strokeStyle = LINE; x.lineWidth = 5; x.fill(path); x.stroke(path);
  x.save(); x.clip(path);
  x.fillStyle = '#d2a676'; x.fillRect(BOX.x0 + 40, BOX.back - BOX.lidH + 22, BOX.x1 - BOX.x0 - 80, BOX.lidH - 30);
  x.strokeStyle = 'rgba(90,50,25,0.22)'; x.lineWidth = 2;
  for (let i = 1; i < 8; i++) { const yy = BOX.back - BOX.lidH * i / 8; x.beginPath(); x.moveTo(BOX.x0 + 40, yy); x.lineTo(BOX.x1 - 40, yy + Math.sin(i) * 3); x.stroke(); }
  const show = sstep(0.55, 1.0, A.rise);
  if (show > 0) {
    // 马灯在左前方：影子往右上偏、放大，边缘有点虚；鹤透出来的颜色乘到木板上
    const proj = new OffscreenCanvas(W, H), px = proj.getContext('2d');
    px.fillStyle = '#fff'; px.fillRect(0, 0, W, H);
    const cen = M.transformPoint(new DOMPoint(R.root[0], R.root[1]));
    px.save(); px.filter = 'blur(6px)'; px.globalAlpha = show; px.globalCompositeOperation = 'multiply';
    px.setTransform(new DOMMatrix().translate(cen.x + 240 + 300 * A.sway, cen.y - 70).scale(1.4).translate(-cen.x, -cen.y).multiply(M));
    if (tail) { const result = tail.drawTransmitted(px); if (result != null && typeof result.then === 'function') throw new TypeError('Tail transmission draw must be synchronous'); } else drawCrane(px, R, A, 't');
    px.strokeStyle = 'rgba(70,45,30,0.7)'; px.lineWidth = 9;
    for (const [a, b] of R.rods) { px.beginPath(); px.moveTo(...a); px.lineTo(...b); px.stroke(); }
    px.restore();
    x.globalCompositeOperation = 'multiply'; x.drawImage(proj, 0, 0); x.globalCompositeOperation = 'source-over';
  }
  x.restore();
  // 箱子里：叠好的蓝印花布（箱沿到后沿一条）
  x.fillStyle = '#2f4a78'; x.strokeStyle = LINE; x.lineWidth = 4;
  x.beginPath(); x.moveTo(BOX.x0 + 10, BOX.rim); x.lineTo(BOX.x1 - 10, BOX.rim); x.lineTo(BOX.x1 - 22, BOX.back + 4); x.lineTo(BOX.x0 + 22, BOX.back + 4); x.closePath(); x.fill(); x.stroke();
  x.fillStyle = 'rgba(235,235,225,0.7)';
  for (let i = 0; i < 16; i++) { const cx = BOX.x0 + 50 + i * 52, cy = BOX.rim - 16 + (i % 2) * 6; x.beginPath(); x.arc(cx, cy, 4, 0, 7); x.fill(); x.beginPath(); x.arc(cx + 26, cy - 9, 2.5, 0, 7); x.fill(); }
  return c;
}

return (t,p)=>bg(t,p.A,p.R,new DOMMatrix(),p);}
