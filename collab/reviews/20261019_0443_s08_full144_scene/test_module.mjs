import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {LAYER_ARTS} from './layer_contract.js';
import {EXPOSE,FRAME_COUNT,FPS,DURATION,poseAt,fireAt,mechanismAt,frameAt} from './contract.js';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const contact={base:961,a:.2,blur:.6,sy:-.07,dx:0,dy:0};
assert.equal(FRAME_COUNT,144);assert.equal(FPS,24);assert.equal(DURATION,6);assert.equal(EXPOSE.length,41);assert.equal(Object.keys(LAYER_ARTS).length,35);
let end=0,files=0,samples=0;
for(const row of EXPOSE){assert.equal(row.start,end);end+=row.hold;assert.ok(LAYER_ARTS[row.asset]);}
assert.equal(end,144);
for(const [asset,roles]of Object.entries(LAYER_ARTS)){
 for(const meta of Object.values(roles)){
  const b=fs.readFileSync(new URL('./frames/'+meta.filename,import.meta.url));
  assert.equal(hash(b),meta.sha256);assert.equal(b.readUInt32BE(16),1920);assert.equal(b.readUInt32BE(20),1080);assert.equal(meta.width,1920);assert.equal(meta.height,1080);files++;
 }
 if(Number(asset)>=66)assert.deepEqual(roles.table_match.contact,contact);
}
for(let f=0;f<144;f++)for(const phase of [0,.25,.5,.75]){
 const t=(f+phase)/24,p=poseAt(t),a=fireAt(t),m=mechanismAt(t);assert.equal(frameAt(t),f);assert.equal(p.frame,f);assert.ok(LAYER_ARTS[p.asset]);assert.ok(p.head.every(Number.isFinite));assert.ok(Number.isFinite(a.wick)&&Number.isFinite(m.lift));samples++;
}
assert.throws(()=>poseAt(6),RangeError);assert.throws(()=>poseAt(-.01),RangeError);
console.log(JSON.stringify({passed:true,frames:144,exposures:41,uniqueAssets:35,verifiedLayerFiles:files,contractSamples:samples,all066OnwardMatchContacts:true,actualCanvasRendered:false}));
