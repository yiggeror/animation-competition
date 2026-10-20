import assert from 'node:assert/strict';
import {exposureAt,makeLampClose} from './lamp_close.mjs';
const calls=[];
globalThis.Path2D=class {constructor(){return new Proxy({}, {get:()=>()=>{}});}};
const ctx=new Proxy({}, {get:(o,k)=>o[k]??((...a)=>{calls.push([k,...a]);if(k==='createRadialGradient')return {addColorStop(){}};}),set:(o,k,v)=>(o[k]=v,true)});
assert.throws(()=>makeLampClose(),/Unbound/);
const renderer=makeLampClose({loadAdopted:async id=>({width:1200,height:1140,id}),drawExistingBackstage:async()=>calls.push(['background']),applyExistingLight:async()=>calls.push(['light'])});
for(let f=0;f<240;f++){
  const inside=f>=96&&f<=131;
  assert.equal(!!exposureAt(f/24),inside);
  const before=calls.length;
  assert.equal(await renderer(ctx,f/24,1920,1080),inside);
  if(!inside)assert.equal(calls.length,before);
  else {
    assert.equal(exposureAt(f/24).start,96+6*Math.floor((f-96)/6));
    const ops=calls.slice(before);assert.deepEqual(ops.find(x=>x[0]==='setTransform'),['setTransform',1.2,0,0,1.2,-228,-120]);
    assert.ok(ops.findIndex(x=>x[0]==='background')<ops.findIndex(x=>x[0]==='drawImage'));
    assert.ok(ops.findIndex(x=>x[0]==='drawImage')<ops.findIndex(x=>x[0]==='light'));
    assert.equal(ops.at(-1)[0],'restore');
  }
}
await assert.rejects(()=>renderer(ctx,4,1000,1000),/16:9/);
console.log(JSON.stringify({status:'STATIC_IMPORT_AND_MOCK_ONLY',timelineFramesChecked:240,activeFrames:36,range:[96,131],outsideFramesUntouched:true,missingBackgroundFailsClosed:true,geometryAPIExecution:true,actualCAM:false},null,2));
