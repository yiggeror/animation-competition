import fs from 'node:fs';
// Synthetic bind-only probe: no production rendering or source mutation.
class Canvas {
 constructor(w,h){this.width=w;this.height=h;}
 getContext(){const W=this.width,H=this.height;return {drawImage(){},getImageData(){const data=new Uint8ClampedArray(W*H*4);for(let k=3;k<data.length;k+=4)data[k]=255;return {data};},beginPath(){},moveTo(){},lineTo(){},closePath(){},fill(){}};}
}
globalThis.OffscreenCanvas=Canvas;
const source=fs.readFileSync('/tmp/laidian-s01-rigs/audit_x01/warp_reviewed.js','utf8');
const {bind,boneMatrices}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const bones=[{name:'root',parent:null,head:[0,0],tail:[0,1]},{name:'arm',parent:'root',head:[50,50],tail:[80,50]}];
const mk=k=>({bones,layers:[{name:'arm',bones:['arm'],poly:[[20,20],[80,20],[80,80],[20,80]],exclusive:true,keepUnder:k,z:1}],pins:[{at:[60,50],bone:'root',r:12}]});
const B0=bind({width:100,height:100},mk(false),{step:10,smooth:0});
const B1=bind({width:100,height:100},mk(true),{step:10,smooth:0});
const body0=B0.layers.find(l=>l.name==='body'),body1=B1.layers.find(l=>l.name==='body'),arm=B1.layers.find(l=>l.name==='arm');
let vi=-1;for(let k=0;k<arm.rest.length;k+=2)if(arm.rest[k]===60&&arm.rest[k+1]===50)vi=k/2;
const weights=Array.from({length:4},(_,k)=>({bone:bones[arm.i[vi*4+k]]?.name,w:arm.w[vi*4+k]}));
const M=boneMatrices(B1,{arm:{rot:.2}});let q=[0,0];for(const x of weights){const m=M[bones.findIndex(b=>b.name===x.bone)];q[0]+=x.w*(m[0]*60+m[2]*50+m[4]);q[1]+=x.w*(m[1]*60+m[3]*50+m[5]);}
const same=(a,b)=>JSON.stringify(Array.from(a))===JSON.stringify(Array.from(b));
const result={consumer:'/tmp/laidian-s01-rigs/audit_x01/warp_reviewed.js',synthetic:true,noWebGLRender:true,pin:{at:[60,50],layerAllowed:['arm'],defaultRootTarget:true,weights,posedAt:q,drift:Math.hypot(q[0]-60,q[1]-50)},keepUnder:{bodyRestEqual:same(body0.rest,body1.rest),bodyTrisEqual:same(body0.tris,body1.tris),bodyHasCenterVertex:Array.from({length:body1.rest.length/2},(_,i)=>[body1.rest[i*2],body1.rest[i*2+1]]).some(([x,y])=>x===50&&y===50)},scope:'Consumer bind/transform reproduction, not actual x01 rig render'};
fs.writeFileSync('/tmp/laidian-s01-rigs/audit_x01/consumer_reproduction.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
