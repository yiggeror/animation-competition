// Node-only geometry checks. They do not render frames or certify a final MP4.
import assert from 'node:assert/strict';
import test from 'node:test';
import { readFile } from 'node:fs/promises';
import { armSide } from '../../../../js/anim/kit.js';
import { hand } from '../../../../js/chars/hand.js';
import { NN } from '../../../../js/chars/nainai.js';
import { M } from '../../../../js/lib/figure.js';
import { ik2 } from '../../../../js/lib/draw.js';

const shotUrl = new URL('../../../../js/anim/s08.js', import.meta.url);
// Expose existing private pure functions without changing production exports.
let source = await readFile(shotUrl, 'utf8');
source = source.replace(/from '(\.[^']+)'/g, (_, p) => `from '${new URL(p, shotUrl).href}'`);
const shot = await import('data:text/javascript;base64,' + Buffer.from(source + '\nexport { shot, matchFlame, wickFlame, matchAt, heldAngle, handPoint, BOX_OFFSET, BOX_REST, lampLayer };\n//# sourceURL=s08-under-test.js').toString('base64'));
const { pose, matchGeom, WICK, leverTip, lift, DURATION, matchFlame, wickFlame } = shot;
const EPS = 1e-7, cmTo720 = 14 * 2 / 3;
const dist = (a,b) => Math.hypot(a[0]-b[0], a[1]-b[1]);
const world = (p,P) => [p[0]+(P.x||0), p[1]+(P.y||0)];
const near = (a,b,eps=EPS) => assert.ok(dist(a,b)<eps, `${JSON.stringify(a)} differs from ${JSON.stringify(b)} by ${dist(a,b)} cm`);
function realHand(P, side) {
  const A=P['arm'+side], a=armSide('n', P, side, A.hand);
  const g=hand({part(){},detail(){}}, M.chain(M.t(...a.W),M.r(a.dir+(A.rot||0))), A.hp, {size:NN.palm,mirror:A.mirror??false,skin:'',z:0,name:'test',lw:1,line:'',ink:''});
  return {...g, grip:world(g.grip,P),tip:world(g.tip,P),arm:a};
}
function finiteTree(v) { if(typeof v==='number') assert.ok(Number.isFinite(v)); else if(v&&typeof v==='object') Object.values(v).forEach(finiteTree); }

test('lamp contact coordinates include its actual TOP - 1.1 placement',()=>{
  // Black wick cap is fillRect(-21,-226,42,6) in the imported code/s08 lamp.
  near(WICK,[56,-58-1.1-226/18.5],1e-6);
  for(const f of [0,.2,.5,1]) near(leverTip(f),[56-(150+95*Math.cos(.55-.9*f))/18.5,-58-1.1+(-230+95*Math.sin(.55-.9*f))/18.5]);
});
test('match starts at the drawn pinch grip, not an assumed wrist offset',()=>{
  for(let frame=0;frame<2.8*24;frame++) {
    const {P}=pose(frame/24); near(matchGeom(P).base,realHand(P,'N').grip);
    assert.ok(Math.abs(dist(matchGeom(P).head,matchGeom(P).base)-4.5)<EPS);
  }
});
test('24 fps contact precedes ignition and remains through the first lit frame',()=>{
  assert.equal(DURATION,6);
  for(const frame of [41,42,43,44]) {
    const t=frame/24, {P}=pose(t);
    assert.ok(dist(matchGeom(P).head,WICK)*cmTo720<.1,`L${frame} misses wick by ${dist(matchGeom(P).head,WICK)*cmTo720} px`);
    assert.ok(matchFlame(t)>0);
  }
  for(let f=0;f<=43;f++) assert.equal(wickFlame(f/24),0);
  assert.ok(wickFlame(44/24)>0);
  assert.ok(dist(matchGeom(pose(46/24).P).head,WICK)*cmTo720>5);
});
test('left pinch is on the actual lever before lift and throughout hold',()=>{
  for(const t of [.9,.94,.95,...Array.from({length:55},(_,i)=>(24+i)/24),3.25]) {
    const {P}=pose(t); assert.equal(P.armF.hp,'pinch');
    assert.ok(dist(realHand(P,'F').grip,leverTip(lift(t)))*cmTo720<.1,`t=${t}: hand is ${dist(realHand(P,'F').grip,leverTip(lift(t)))*cmTo720}px from lever`);
  }
});
test('release clears the fixed raised lever before the single drop',()=>{
  assert.equal(lift(3.3),1); assert.equal(lift(3.4),0);
  const p=pose(3.3).P;
  assert.ok(dist(realHand(p,'F').grip,leverTip(1))>1.5);
  for(let i=1;i<=24;i++) assert.ok(lift(3.3+i/240)<=lift(3.3+(i-1)/240));
});
test('all 24 fps poses are finite, reachable, and retain fixed arm and leg bones',()=>{
  for(let f=0;f<=144;f++) {
    const {P}=pose(f/24); finiteTree(P); finiteTree(matchGeom(P));
    for(const side of ['N','F']) {
      const a=realHand(P,side).arm;
      assert.ok(a.reach<.999,`L${f} ${side} unreachable ${a.reach}`);
      assert.ok(Math.abs(dist(a.S,a.E)-NN.upper)<EPS); assert.ok(Math.abs(dist(a.E,a.W)-NN.fore)<EPS);
      const hip=[side==='N'?0:-3,NN.hipY+(P.bob||0)], foot=P['leg'+side].foot, l=ik2(hip,foot,NN.thigh,NN.shin,1);
      near(l.end,foot); assert.ok(Math.abs(dist(hip,l.joint)-NN.thigh)<EPS);assert.ok(Math.abs(dist(l.joint,l.end)-NN.shin)<EPS);
      near(world(foot,P),[side==='N'?30:26,-4.6]);
    }
  }
});
test('numeric pose parameters and held match are continuous at action boundaries',()=>{
  const times=[.12,.2,.45,.72,.75,.9,.94,.95,1.1,1.5,1.65,1.7,1.8,1.85,2.05,2.2,2.35,2.4,2.75,2.8,2.9,3.25,3.3,3.4,3.5,3.9,4.2,4.3,6];
  for(const t of times){
    const l=pose(t-1e-7).P,r=pose(t+1e-7).P;
    for(const side of ['N','F']) {near(world(l['arm'+side].hand,l),world(r['arm'+side].hand,r),1e-3);assert.ok(Math.abs(l['arm'+side].rot-r['arm'+side].rot)<1e-3,`rot discontinuity at ${t}`);}
    if(t<2.8) near(matchGeom(l).head,matchGeom(r).head,1e-3);
  }
});
test('sit-back includes a small pelvis retreat with both feet fixed',()=>{
  assert.ok((pose(4.3).P.x||0)<(pose(3.4).P.x||0)-2);
});

// Canvas command recorder: transforms actual lamp draw calls; no raster canvas,
// browser, screenshot, generated image, or video is produced by these checks.
class PathCommands { moveTo(){} lineTo(){} bezierCurveTo(){} closePath(){} }
function captureContext() {
  let matrix=[1,0,0,1,0,0], stack=[];
  const ctx={arcs:[],rects:[],translations:[],
    save(){stack.push({matrix:[...matrix],fillStyle:this.fillStyle});}, restore(){const s=stack.pop();matrix=s.matrix;this.fillStyle=s.fillStyle;},
    translate(x,y){matrix=M.chain(matrix,M.t(x,y));this.translations.push([x,y]);},
    scale(x,y){matrix=M.chain(matrix,M.s(x,y));},rotate(a){matrix=M.chain(matrix,M.r(a));},
    beginPath(){},rect(){},moveTo(){},lineTo(){},bezierCurveTo(){},quadraticCurveTo(){},closePath(){},stroke(){},fill(){},ellipse(){},
    arc(x,y,r){this.arcs.push({at:M.ap(matrix,[x,y]),r,fillStyle:this.fillStyle});},
    fillRect(x,y,w,h){this.rects.push({top:M.ap(matrix,[x+w/2,y]),w,h,fillStyle:this.fillStyle});},
    createRadialGradient(){return {addColorStop(){}};}
  };return ctx;
}
test('actual lampLayer draw commands agree with wick and lever attachment coordinates',()=>{
  const oldPath=globalThis.Path2D,oldCanvas=globalThis.OffscreenCanvas;
  globalThis.Path2D=PathCommands;
  globalThis.OffscreenCanvas=class{constructor(){this.ctx=captureContext();}getContext(){return this.ctx;}};
  try {
    for(const t of [0,.95,1.02,1.12,1.8,3.25,3.3,3.35,3.4]){
      const ctx=shot.lampLayer(t).img.ctx;
      const cap=ctx.rects.find(r=>r.fillStyle==='#2b2018'&&r.w===42);
      const knob=ctx.arcs.findLast(r=>r.r===9);
      assert.ok(cap&&knob);
      near(cap.top,[596+14*WICK[0],1793+14*WICK[1]]);
      near(knob.at,[596+14*leverTip(lift(t))[0],1793+14*leverTip(lift(t))[1]]);
    }
  } finally {globalThis.Path2D=oldPath;globalThis.OffscreenCanvas=oldCanvas;}
});
test('flame emission and light roots follow the physical head and wick',()=>{
  for(const t of [1.7,1.8,44/24,1.9,2.2]){
    const ctx=captureContext();shot.shot.emit(ctx,t);
    const M=shot.matchAt(t,pose(t).P),roots=[];
    if(matchFlame(t)>0)roots.push([596+14*M.head[0],1793+14*M.head[1]+2]);
    if(wickFlame(t)>0)roots.push([596+14*WICK[0],1793+14*WICK[1]+2]);
    assert.equal(ctx.translations.length,roots.length);roots.forEach((p,i)=>near(ctx.translations[i],p));
    const lights=shot.shot.light(t).lights;
    assert.equal(lights.length,roots.length);
  }
});
test('match and box hand-to-table transfers do not teleport',()=>{
  const a=shot.matchAt(2.8-1e-7,pose(2.8-1e-7).P),b=shot.matchAt(2.8,pose(2.8).P);
  near(a.base,b.base,1e-5);near(a.head,b.head,1e-5);
  near(shot.handPoint(pose(.72-1e-7).P,'F',shot.BOX_OFFSET),shot.BOX_REST,1e-5);
  for(const t of [3,3.4,4.25,6]) {const m=shot.matchAt(t,pose(t).P);near(m.base,b.base);near(m.head,b.head);}
});
test('240 Hz sweep has no unreachable or nonfinite pose and no hidden wrist jumps',()=>{
  let prev=null;
  for(let i=0;i<=1440;i++){
    const {P}=pose(i/240);finiteTree(P);finiteTree(matchGeom(P));
    for(const side of ['N','F']){
      const a=realHand(P,side).arm;assert.ok(a.reach<.99);
      if(prev){near(world(P['arm'+side].hand,P),world(prev['arm'+side].hand,prev),.8);assert.ok(Math.abs(P['arm'+side].rot-prev['arm'+side].rot)<.06);}
    }prev=P;
  }
});
