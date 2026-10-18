import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

// Call/geometry audit, NOT raster rendering. Real character/Figure functions run;
// this canvas recorder only tracks image consumers, compositing state and matrices.
const mult=(a,b)=>[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
class Context {
 constructor(canvas){this.canvas=canvas;this.m=[1,0,0,1,0,0];this.globalAlpha=1;this.globalCompositeOperation='source-over';this.stack=[];this.images=[];}
 save(){this.stack.push({m:[...this.m],a:this.globalAlpha,c:this.globalCompositeOperation});}
 restore(){const s=this.stack.pop();this.m=s.m;this.globalAlpha=s.a;this.globalCompositeOperation=s.c;}
 getTransform(){const[a,b,c,d,e,f]=this.m;return{a,b,c,d,e,f};}
 setTransform(...v){if(v.length===1){const o=v[0];v=[o.a,o.b,o.c,o.d,o.e,o.f];}this.m=v;}
 transform(...v){this.m=mult(this.m,v);}
 translate(x,y){this.transform(1,0,0,1,x,y);}
 scale(x,y){this.transform(x,0,0,y,0,0);}
 rotate(a){this.transform(Math.cos(a),Math.sin(a),-Math.sin(a),Math.cos(a),0,0);}
 drawImage(source){this.images.push({source,alpha:this.globalAlpha,mode:this.globalCompositeOperation});}
 clearRect(){this.images=[];}
 createLinearGradient(){return{addColorStop(){}};}
 createRadialGradient(){return{addColorStop(){}};}
}
class Canvas {
 constructor(width,height){this.width=width;this.height=height;this.ctx=new Proxy(new Context(this),{get:(o,k)=>k in o?(typeof o[k]==='function'?o[k].bind(o):o[k]):()=>{}});}
 getContext(){return this.ctx;}
}
globalThis.OffscreenCanvas=Canvas;
globalThis.Path2D=class{constructor(){return new Proxy(this,{get:()=>()=>{}})}};
const sourceUrl=new URL('../../../../js/anim/s07.js',import.meta.url);
let source=await readFile(sourceUrl,'utf8');
source=source.replace(/from (['"])(\.\.?\/[^'"]+)\1/g,(_,q,p)=>`from ${q}${new URL(p,sourceUrl)}${q}`);
// Expose private render helpers in this isolated test module, without changing
// their code or substituting a stub renderer for the production character art.
source+='\nexport { rollingLayer as auditRollingLayer, turnLayer as auditTurnLayer, upperTurnSprite as auditUpperTurnSprite, rollSprite as auditRollSprite };\n';
const s=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
function leaves(canvas,out=[]){for(const call of canvas.ctx.images){assert.equal(call.alpha,1,'character image composited at fractional opacity');assert.equal(call.mode,'source-over','character images use additive blending');if(call.source.ctx.images.length)leaves(call.source,out);else out.push(call.source);}return out;}
test('turn consumes exactly one opaque upper-body drawing at every encoded turn frame',()=>{
 for(let L=39;L<=47;L++){const g=s.grandmaS07(L/24),r=s.auditTurnLayer(g);assert.equal(leaves(r.img).length,1,`L${L}: more than one face/body image consumed`);}
});
test('roll consumes exactly one opaque character drawing through both view changes',()=>{
 for(let L=12;L<=27;L++){const x=s.xiaomanS07(L/24),r=s.auditRollingLayer(x,s.xmPhone(L/24));assert.equal(leaves(r.img).length,1,`L${L}: mixed side/back drawings`);}
});

function landmark(sprite) { const m=sprite.figure.m,p=sprite.head; return [m.a*p[0]+m.c*p[1]+m.e,m.b*p[0]+m.d*p[1]+m.f]; }
const gap=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
test('selected upper-body Figure has one face and head x/y are continuous at view boundaries',()=>{
 const dt=.36*Math.sqrt(1/12), times=[1.62+dt,1.98-dt];
 for(const t of times){
  const a=s.auditUpperTurnSprite(s.grandmaS07(t-1e-7)),b=s.auditUpperTurnSprite(s.grandmaS07(t+1e-7));
  for(const q of[a,b])assert.equal(q.figure.parts.filter(p=>p.name==='face').length,1);
  const pa=landmark(a),pb=landmark(b); assert.ok(Math.abs(pa[0]-pb[0])/(2*2.77)<1e-4);
  assert.ok(gap(pa,pb)/(2*2.77)<1e-4,'head x/y anchor is discontinuous at opaque view change');
 }
});
test('roll has one visible head silhouette and bounded head anchors at surface changes',()=>{
 const dt=.44*Math.sqrt((Math.acos(.66)/Math.PI)/2),times=[.64+dt,1.08-dt];
 for(const t of times){
  const a=s.auditRollSprite(s.xiaomanS07(t-1e-7)),b=s.auditRollSprite(s.xiaomanS07(t+1e-7));
  for(const q of[a,b]){assert.equal(q.figure.parts.filter(p=>p.name==='hair').length,1);assert.ok(q.figure.parts.filter(p=>p.name==='face').length<=1);}
  const d=gap(landmark(a),landmark(b))/(2*1.97);assert.ok(d<1e-4,`roll head anchor jumped ${d.toFixed(3)}cm`);
 }
});
