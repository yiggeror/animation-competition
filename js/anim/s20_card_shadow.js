// Shadow geometry follows the same adopted screen card as the visible paper.
// The card's affine screen registration is unprojected onto its real sheet
// plane; the original lamp projection then sees those same effective points.
import {drawPuppet} from '../puppet.js';
const cache=new Map();
export function alignedCardShadow({pup,pose,root,ox,oy,w,h,cam,matrix,rods}){
 const key=JSON.stringify([pup.name,pose,root,cam.C,cam.focal,matrix,rods.map(r=>[r.id,r.A_world,r.end_world])]);if(cache.has(key))return cache.get(key);
 const source=new OffscreenCanvas(w,h),sx=source.getContext('2d');sx.translate(ox,oy);sx.scale(2,-2);drawPuppet(sx,pup,pose,'t');
 const alpha=sx.getImageData(0,0,w,h).data;let x0=w,y0=h,x1=0,y1=0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++)if(alpha[(y*w+x)*4+3]){x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+1);y1=Math.max(y1,y+1)}
 const world=(x,y)=>{const px=matrix[0]*x+matrix[2]*y+matrix[4],py=matrix[1]*x+matrix[3]*y+matrix[5],u=(px-960)/cam.focal,v=(540-py)/cam.focal,ray=cam.fwd.map((n,i)=>n+u*cam.right[i]+v*cam.up[i]),t=(.004-cam.C[1])/ray[1];return[cam.C[0]+t*ray[0],cam.C[2]+t*ray[2]]};
 const corners=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]].map(p=>world(...p)),minX=Math.min(...corners.map(p=>p[0]))-.002,maxX=Math.max(...corners.map(p=>p[0]))+.002,minZ=Math.min(...corners.map(p=>p[1]))-.002,maxZ=Math.max(...corners.map(p=>p[1]))+.002,K=1400;
 const texture=new OffscreenCanvas(Math.ceil((maxX-minX)*K),Math.ceil((maxZ-minZ)*K)),tx=texture.getContext('2d'),dest=p=>{const q=world(...p);return[(q[0]-minX)*texture.width/(maxX-minX),(maxZ-q[1])*texture.height/(maxZ-minZ)]};
 function triangle(a,b,c){const p=dest(a),q=dest(b),r=dest(c),S=[b[0]-a[0],b[1]-a[1],c[0]-a[0],c[1]-a[1]],det=S[0]*S[3]-S[2]*S[1],D=[q[0]-p[0],q[1]-p[1],r[0]-p[0],r[1]-p[1]],m=[(D[0]*S[3]-D[2]*S[1])/det,(D[1]*S[3]-D[3]*S[1])/det,(-D[0]*S[2]+D[2]*S[0])/det,(-D[1]*S[2]+D[3]*S[0])/det];tx.save();const center=[(p[0]+q[0]+r[0])/3,(p[1]+q[1]+r[1])/3],expanded=[p,q,r].map(z=>{const n=Math.hypot(z[0]-center[0],z[1]-center[1]);return[z[0]+.5*(z[0]-center[0])/n,z[1]+.5*(z[1]-center[1])/n]});tx.beginPath();expanded.forEach((z,i)=>i?tx.lineTo(...z):tx.moveTo(...z));tx.closePath();tx.clip();tx.setTransform(...m,p[0]-m[0]*a[0]-m[2]*a[1],p[1]-m[1]*a[0]-m[3]*a[1]);tx.drawImage(source,0,0);tx.restore()}
 for(let y=y0;y<y1;y+=20)for(let x=x0;x<x1;x+=20){const a=[x,y],b=[Math.min(x+20,x1),y],c=[Math.min(x+20,x1),Math.min(y+20,y1)],d=[x,Math.min(y+20,y1)];triangle(a,b,c);triangle(a,c,d)}
 const empty=new OffscreenCanvas(1,1),parts={plane:{bounds:[(minX-root[0])*1000,(minZ-root[1])*1000,(maxX-root[0])*1000,(maxZ-root[1])*1000],t:texture,r:texture}},rig=[{part:'plane',parent:null,at:[0,0],layer:0}];
 for(const r of rods){rig.push({part:r.id,parent:'plane',at:[(r.A_world[0]-root[0])*1000,(r.A_world[2]-root[1])*1000],layer:1});parts[r.id]={bounds:[0,0,.0001,.0001],t:empty,r:empty}}
 const actor={pup:{name:pup.name+'_card_shadow',rig,parts},pose:{angles:{},rootAngle:0,facing:1},root,dist:.004,rods:rods.map(r=>({part:r.id,at:[0,0],hand:[r.end_world[0],r.end_world[2],r.end_world[1]]}))};cache.set(key,actor);return actor;
}
