import assert from 'node:assert/strict';
import {makeLampClose} from './lamp_close.mjs';
globalThis.Path2D=class {constructor(){return new Proxy({}, {get:()=>()=>{}});}};
function mock(){const stack=[];const x={ctm:[1,0,0,1,0,0],globalAlpha:1,save(){stack.push({ctm:[...this.ctm],alpha:this.globalAlpha});},restore(){assert.ok(stack.length);const s=stack.pop();this.ctm=s.ctm;this.globalAlpha=s.alpha;},setTransform(...v){this.ctm=v;},get depth(){return stack.length;}};return new Proxy(x,{get:(o,k)=>k in o?o[k]:(()=>k==='createRadialGradient'?{addColorStop(){}}:undefined)});}
const x=mock();let checked=false;
await makeLampClose({loadAdopted:async()=>({width:1200,height:1140}),drawExistingBackstage:async c=>{c.setTransform(99,0,0,99,100,100);c.globalAlpha=.1;},applyExistingLight:async c=>{assert.deepEqual(c.ctm,[1.2,0,0,1.2,-228,-120]);assert.equal(c.globalAlpha,1);checked=true;}})(x,4,1920,1080);
assert.ok(checked);assert.equal(x.depth,0);
for(const failing of ['background','lamp','light']){
 const c=mock();if(failing==='lamp')c.translate=()=>{if(c.depth===2)throw new Error('injected lamp failure');};
 const render=makeLampClose({loadAdopted:async()=>({width:1200,height:1140}),drawExistingBackstage:async()=>{if(failing==='background')throw new Error('background');},applyExistingLight:async()=>{if(failing==='light')throw new Error('light');}});
 await assert.rejects(()=>render(c,4,1920,1080));assert.equal(c.depth,0);assert.deepEqual(c.ctm,[1,0,0,1,0,0]);
}
console.log('PASS: callback CTM/alpha isolated; background/lamp-entry/light error paths balance Canvas save stack. Mock only.');
