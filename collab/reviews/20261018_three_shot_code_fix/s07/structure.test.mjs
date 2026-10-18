import test from 'node:test';
import assert from 'node:assert/strict';

// Only the decorative coil's import-time Canvas calls are stubbed. No pixels
// are rendered here; all assertions below use production pose/IK functions.
const noop = () => {};
globalThis.OffscreenCanvas = class { getContext() { return new Proxy({}, { get: (_, k) => k === 'createLinearGradient' || k === 'createRadialGradient' ? () => ({ addColorStop: noop }) : noop, set: () => true }); } };
const shot = await import('../../../../js/anim/s07.js');
const { armSide } = await import('../../../../js/anim/kit.js');
const { GM_AT, GM_K, LAMP_AT, LAMP_S } = await import('../../../../js/anim/s01.js');
const distance = (a,b) => Math.hypot(a[0]-b[0],a[1]-b[1]);
const grip = (g) => { const p = g.P, a = armSide('n', p, 'N', p.armN.hand), d = a.dir + (p.armN.rot || 0); return [p.x + a.W[0] + 5.4*(.82*Math.cos(d)-.02*Math.sin(d)), p.y + a.W[1] + 5.4*(.82*Math.sin(d)+.02*Math.cos(d))]; };
test('closed hand encloses the actual cubic handle apex before lamp lift', () => {
 const g = shot.grandmaS07(4.3), target = [(LAMP_AT[0]-GM_AT[0])/GM_K,(LAMP_AT[1]-690*LAMP_S-GM_AT[1])/GM_K];
 assert.ok(distance(grip(g), target) < .05, `grip-to-handle gap ${distance(grip(g),target).toFixed(3)} cm`);
 assert.equal(g.lampLift || 0, 0);
});
test('bowl edge clears the retracted shoe sole at placement', () => {
 const g=shot.grandmaS07(.74), p=g.P;
 const furthestShoe = Math.max(...['N','F'].map(s=>p.x+p['leg'+s].foot[0]+9.2));
 assert.ok(g.bowl[0]-13-furthestShoe > .5, `bowl-shoe clearance ${g.bowl[0]-13-furthestShoe}`);
});
test('turn has a lifted foot rather than three static front views', () => {
 const g=shot.grandmaS07(1.9), p=g.P;
 const feet=['N','F','L','R'].map(s=>p['leg'+s]?.foot).filter(Boolean);
 assert.ok(feet.some(f=>f[1]+p.y < -5.5), 'no lifted turning foot');
});
test('roll exposes a continuous support transform instead of a two-frame back swap', () => {
 assert.equal(typeof shot.xiaomanS07, 'function', 'roll pose/support transform is not exposed');
 for (const t of [.62,.66,.7,.74,.78,.82,.86,.9,.94,.98,1.02]) {
  const x=shot.xiaomanS07(t);
  assert.equal(x.view,'roll');
  assert.ok(Number.isFinite(x.roll));
  assert.ok(x.support && x.support.floorY === 0);
 }
});
const world = (g, p) => [(g.flip ? -1 : 1) * (g.P.x + p[0]), g.P.y + p[1]];
const near = (a,b,eps=1e-6) => assert.ok(distance(a,b)<eps, `${a} vs ${b}`);
test('actual lower-palm contour touches both knee caps before hip lift', () => {
 for(let t=.92;t<=1.28;t+=.005) {
  const {P:p}=shot.grandmaS07(t);
  for(const sd of ['N','F']) {
   const a=armSide('n',p,sd,p['arm'+sd].hand), d=a.dir+(p['arm'+sd].rot||0);
   const lowerPalm=[a.W[0]+5.4*(.6*Math.cos(d)-.33*Math.sin(d)), a.W[1]+5.4*(.6*Math.sin(d)+.33*Math.cos(d))];
   near(lowerPalm,[p['leg'+sd].knee[0],p['leg'+sd].knee[1]-5.2]);
  }
  if(t<=1.05) assert.equal(p.y,37,'hip lifted before palm contact');
 }
});
test('all turning legs have fixed 3-D femur/shin lengths and one planted foot', () => {
 const d3=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
 for(let t=1.62;t<1.98;t+=.001) {
  const g=shot.grandmaS07(t);
  assert.ok(Object.values(g.rigs).some(r=>r.planted));
  for(const r of Object.values(g.rigs)) {
   assert.ok(Math.abs(d3(r.hip,r.knee)-35.5)<1e-8);
   assert.ok(Math.abs(d3(r.knee,r.foot)-35.5)<1e-8);
   if(r.planted) assert.equal(r.foot[1],-4.6);
  }
 }
});
test('rise/turn/walk boundaries preserve world-space knees and ankles', () => {
 for(const t of[1.62,1.98])for(const sd of['N','F'])for(const j of['knee','foot']) {
  const a=shot.grandmaS07(t-1e-7),b=shot.grandmaS07(t);
  near(world(a,a.P['leg'+sd][j]),world(b,b.P['leg'+sd][j]),1e-4);
 }
});
test('the already-correct first walking support foot remains pinned', () => {
 for(let t=1.98;t<=2.43;t+=.002) { const g=shot.grandmaS07(t); near(world(g,g.P.legF.foot),[-31,-4.6]); }
});
test('grip stays on the moving handle and lift starts after closed-hand contact', () => {
 for(let t=4.3;t<=4.5;t+=.002) {
  const g=shot.grandmaS07(t); assert.equal(g.P.armN.hp,'grip');
  near(grip(g),[(LAMP_AT[0]-GM_AT[0])/GM_K,(LAMP_AT[1]-690*LAMP_S-(g.lampLift||0)-GM_AT[1])/GM_K]);
  if(t<=4.35) assert.equal(g.lampLift,0);
 }
});
test('side-roll FK bones keep their lengths; knees and ankles stay above floor', async () => {
 const {shoulderSide,XM_LEG}=await import('../../../../js/anim/kit.js');
 for(let t=.48;t<1.08;t+=.002) {
  const x=shot.xiaomanS07(t),p=x.P,cs=Math.cos(x.roll);
  for(const sd of['N','F']) {
   const leg=p['leg'+sd],hip=XM_LEG['hip'+sd],a=p['arm'+sd],s=shoulderSide('x',p,sd);
   assert.ok(Math.abs(distance(hip,leg.knee)-20.2)<1e-8);
   assert.ok(Math.abs(distance(leg.knee,leg.foot)-19.6)<1e-8);
   assert.ok(Math.abs(distance(s,a.elbow)-12.4)<1e-8);
   assert.ok(Math.abs(distance(a.elbow,a.hand)-11.2)<1e-8);
   for(const q of[leg.knee,leg.foot]) {
    const y=x.to[1]+Math.sin(x.rot)*(q[0]-x.pivot[0])*cs+Math.cos(x.rot)*(q[1]-x.pivot[1]);
    assert.ok(y<0,`joint crosses floor at ${t}`);
   }
  }
  assert.equal(x.to[0],-1,'hip pivot slid during roll');
 }
});
