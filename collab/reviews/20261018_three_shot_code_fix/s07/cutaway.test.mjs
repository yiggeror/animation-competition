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
source+='\nexport { shot as auditShot, rollSprite as auditRollSprite };\n';
const s=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const {GM_AT,GM_K,XM_AT,XM_K}=await import('../../../../js/anim/s01.js');
const {shoulderSide}=await import('../../../../js/anim/kit.js');
const {Figure}=await import('../../../../js/lib/figure.js');
const originalDraw=Figure.prototype.draw;
let drawn=[];
Figure.prototype.draw=function(){originalDraw.call(this);drawn.push(this);};
const cameraBox=t=>{const c=s.auditShot.cam(t),w=1672/c.fit,h=w*9/16;return[c.x-w/2,c.y-h/2,c.x+w/2,c.y+h/2];};
const inside=(box,p,pad=0)=>p[0]>=box[0]+pad&&p[0]<=box[2]-pad&&p[1]>=box[1]+pad&&p[1]<=box[3]-pad;
const gmWorld=(g,p)=>[GM_AT[0]+(g.flip?-1:1)*GM_K*((g.P.x||0)+p[0]),GM_AT[1]+GM_K*((g.P.y||0)+p[1])];
const apply=(m,p)=>[m.a*p[0]+m.c*p[1]+m.e,m.b*p[0]+m.d*p[1]+m.f];
const center=pts=>pts.reduce((s,p)=>[s[0]+p[0]/pts.length,s[1]+p[1]/pts.length],[0,0]);

test('camera cuts occur at F16 F39 F57, never F56; duration remains 108 frames',()=>{
 assert.equal(s.DURATION*24,108);
 const cam=t=>s.auditShot.cam(t);
 assert.deepEqual(cam(15/24),cam(0));
 assert.notDeepEqual(cam(16/24),cam(15/24));
 assert.notDeepEqual(cam(39/24),cam(38/24));
 assert.deepEqual(cam(56/24),cam(39/24));
 assert.deepEqual(cam(57/24),cam(0));
 assert.notDeepEqual(cam(57/24),cam(56/24));
 for(const t of[.66,1.62,2.35])assert.notDeepEqual(cam(t-1e-8),cam(t));
});

test('production layers exclude the other actor during each close-up',async()=>{
 for(const t of[0,.65,.66,.72,.92,1.06,1.61,1.62,1.82,1.98,2.34,2.35,4.49]){
  drawn=[];const layers=await s.auditShot.layers(t);
  const grandma=drawn.some(f=>f.parts.some(p=>p.name==='blouse'));
  const child=drawn.some(f=>f.parts.some(p=>p.name==='dress'));
  assert.equal(grandma,!(t>=1.62&&t<2.35),`grandma visibility at ${t}`);
  assert.equal(child,!(t>=.66&&t<1.62),`child visibility at ${t}`);
  assert.equal(layers.length,t<.66||t>=2.35?4:3);
 }
});

test('rise framing contains the actual head contour, knee and palm joints, plus bowl landing',async()=>{
 for(let F=16;F<=38;F++){
  const t=F/24,g=s.grandmaS07(t),box=cameraBox(t);
  drawn=[];const layers=await s.auditShot.layers(t),layer=layers.find(l=>l.x===760);
  const fig=drawn.find(f=>f.parts.some(p=>p.name==='blouse'));
  for(const p of fig.parts.filter(p=>['face','hair','bun'].includes(p.name)))for(const q of p.pts){
   const px=apply(fig.m,q),world=[layer.x+px[0]*layer.sc,layer.y+px[1]*layer.sc];
   assert.ok(inside(box,world,8),`head clipped F${F}: ${world}`);
  }
  for(const sd of['N','F'])assert.ok(inside(box,gmWorld(g,g.P['leg'+sd].knee),10),`knee clipped F${F}`);
  if(t>=.92&&t<=1.28)for(const sd of['N','F'])assert.ok(inside(box,gmWorld(g,g.P['arm'+sd].hand),10),`palm clipped F${F}`);
 }
 for(const t of[.66,.72]){
  const g=s.grandmaS07(t),box=cameraBox(t),[bx,by]=g.bowl;
  for(const x of[bx-14,bx+14])for(const y of[by-4,by+4])assert.ok(inside(box,[GM_AT[0]-GM_K*x,GM_AT[1]+GM_K*y],10),'bowl landing cropped');
 }
});

test('child close-up contains its actual supine contour and fanning hand without time restart',()=>{
 for(let F=39;F<=56;F++){
  const t=F/24,x=s.xiaomanS07(t),sprite=s.auditRollSprite(x),box=cameraBox(t);
  assert.equal(x.roll,Math.PI,'child close-up must begin after supine landing');
  for(const p of sprite.figure.parts)for(const q of p.pts){
   const px=apply(sprite.figure.m,q),world=[400+px[0]/2,520+px[1]/2];
   assert.ok(inside(box,world,8),`child/fanning-hand framing F${F}: ${p.name} ${world}`);
  }
 }
});

test('child inserts an actual iris displacement toward grandma after the offscreen footsteps',()=>{
 const t=2.02,x=s.xiaomanS07(t),active=s.auditRollSprite(x);
 const neutral=s.auditRollSprite({...x,P:{...x.P,face:{...x.P.face,look:[.3,-.5]}}});
 const iris=q=>apply(q.figure.m,center(q.figure.ops.find(o=>o.kind==='detail'&&o.z===6.01).pts));
 const a=iris(active),b=iris(neutral),v=[a[0]-b[0],a[1]-b[1]];
 assert.ok(v[0]>.2&&v[1]<-.2,`screen-space iris movement must be right/up: ${v}`);
 const g=s.grandmaS07(t),target=gmWorld(g,shoulderSide('n',g.P,'N'));
 const toward=[target[0]-(400+a[0]/2),target[1]-(520+a[1]/2)];
 const alignment=(v[0]*toward[0]+v[1]*toward[1])/(Math.hypot(...v)*Math.hypot(...toward));
 assert.ok(alignment>.9,`projected iris does not move toward grandma: ${alignment}`);
 assert.deepEqual(s.xiaomanS07(1.8).P.face.look,[.3,-.5]);
 assert.deepEqual(s.xiaomanS07(2.3).P.face.look,[.3,-.5]);
 assert.deepEqual(s.xiaomanS07(2.9).P.face.look,[.3,-.5],'no second reversed glance after the close-up');
});

test('the same lighting and continuous global action times are retained across inserts',()=>{
 const light=s.auditShot.light(0);
 for(const t of[.66,.72,1.06,1.62,1.98,2.35,4.3])assert.deepEqual(s.auditShot.light(t),light);
 assert.equal((source.match(/return renderPaint\(/g)||[]).length,1);
 assert.deepEqual(s.grandmaS07(1.82).feet.F,[-31,-4.6]);
 const walk=s.grandmaS07(1.98).P;assert.ok(Math.abs(walk.x+walk.legN.foot[0]+27)<1e-8);
 assert.equal(s.grandmaS07(1.05).P.y,37);
 assert.ok(s.grandmaS07(1.06).P.y<37);
 assert.equal(s.xiaomanS07(1.62).roll,Math.PI);
 assert.equal(s.grandmaS07(2.43).P.legN.foot[1]+s.grandmaS07(2.43).P.y,-4.6);
 assert.equal(s.grandmaS07(4.3).P.armN.hp,'grip');
 assert.equal(s.grandmaS07(4.35).lampLift,0);
 assert.ok(s.grandmaS07(4.36).lampLift>0);
});
