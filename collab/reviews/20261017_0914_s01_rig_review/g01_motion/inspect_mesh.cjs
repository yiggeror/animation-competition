const fs=require('fs'),path=require('path');
const p=__dirname,sd=path.join(p,'source');
(async()=>{
 const rig=JSON.parse(fs.readFileSync(path.join(sd,'g01_beans.rig.json'),'utf8'));
 const rgba=new Uint8ClampedArray(fs.readFileSync(path.join(sd,'g01_rgba.bin')));
 global.OffscreenCanvas=class {constructor(w,h){this.width=w;this.height=h;} getContext(){return {drawImage(){},getImageData(){return {data:rgba};}}}};
 const ws=fs.readFileSync(path.join(sd,'warp.js'),'utf8');const wu='data:text/javascript;base64,'+Buffer.from(ws).toString('base64');
 const ts=fs.readFileSync(path.join(sd,'test_anim.js'),'utf8').replace("'./warp.js'",JSON.stringify(wu));
 const w=await import(wu),a=await import('data:text/javascript;base64,'+Buffer.from(ts).toString('base64'));
 const B=w.bind({width:779,height:1355},rig),L=B.layers[0];
 const pts=[[390,660],[400,650],[400,610],[390,600],[450,650],[460,660],[200,500],[200,510],[220,600],[170,530],[300,720],[150,1250],[600,1100]];
 const observations=[];
 for (const q of pts){let v=-1;for(let i=0;i<L.rest.length/2;i++)if(L.rest[2*i]===q[0]&&L.rest[2*i+1]===q[1]){v=i;break;}
 if(v<0){observations.push({rest:q,missing:true});continue;}
 const ws=[];for(let k=0;k<4;k++){const id=L.i[v*4+k],ww=L.w[v*4+k];if(ww>1e-7)ws.push({name:rig.bones[id].name,weight:ww});}
 const samples=[];for(let f=0;f<144;f++){const mats=w.boneMatrices(B,a.grandmaBeans(f/24));let x=0,y=0;for(let k=0;k<4;k++){const id=L.i[v*4+k],ww=L.w[v*4+k],m=mats[id];x+=ww*(m[0]*q[0]+m[2]*q[1]+m[4]);y+=ww*(m[1]*q[0]+m[3]*q[1]+m[5]);}samples.push([x,y]);}
 const ranges=[0,1].map(k=>({min:Math.min(...samples.map(q=>q[k])),max:Math.max(...samples.map(q=>q[k]))}));
 observations.push({rest:q,weights:ws,range_source_px:ranges,peak_displacement_source_px:Math.max(...samples.map(p=>Math.hypot(p[0]-q[0],p[1]-q[1]))),f0:samples[0],f7:samples[7],f16:samples[16],f22:samples[22]});
 }
 fs.writeFileSync(path.join(p,'mesh_point_measurements.json'),JSON.stringify({method:'Original frozen warp.bind + boneMatrices and test_anim.grandmaBeans. Canvas stub supplies actual source RGBA for mesh/alpha; no drawing, no video rendering. Values are source-pixel mesh vertex coordinates, not optical video measurements.',observations},null,2));
 console.log(observations.map(o=>({rest:o.rest,weights:o.weights,peak_displacement_source_px:o.peak_displacement_source_px})));
})();
