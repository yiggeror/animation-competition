// Project the actual fixed-size held paper onto the sheet from the existing lamp.
// Inverse ray/plane sampling is exact for this flat puppet and avoids clipped mesh tiles.
import {drawPuppet} from '../puppet.js';
export function heldCardShadow({pup,pose,plane,lamp,rods=[],w=1600,h=1400,ox=800,oy=700}){
 const src=new OffscreenCanvas(w,h),sx=src.getContext('2d');sx.translate(ox,oy);sx.scale(2,-2);drawPuppet(sx,pup,pose,'t');
 const pixels=sx.getImageData(0,0,w,h).data;
 const minX=.25,maxX=2.35,minZ=.12,maxZ=1.94,K=900,W=Math.ceil((maxX-minX)*K),H=Math.ceil((maxZ-minZ)*K);
 const texture=new OffscreenCanvas(W,H),tx=texture.getContext('2d'),out=tx.createImageData(W,H),D=out.data;
 const L=[lamp.x,lamp.y,lamp.z],O=plane.origin,N=plane.normal,U=plane.axisX,V=plane.axisY;
 const distance=N[0]*(O[0]-L[0])+N[1]*(O[1]-L[1])+N[2]*(O[2]-L[2]),dy=.004-L[1];
 for(let y=0;y<H;y++){
  const dz=maxZ-(y+.5)/K-L[2];
  for(let x=0;x<W;x++){
   const dx=minX+(x+.5)/K-L[0],den=N[0]*dx+N[1]*dy+N[2]*dz,k=distance/den;
   if(!(k>0&&k<1))continue; // Paper must lie between this lamp and the receiving sheet.
   const px=L[0]+k*dx-O[0],py=L[1]+k*dy-O[1],pz=L[2]+k*dz-O[2];
   const u=ox+2000*(px*U[0]+py*U[1]+pz*U[2]),v=oy-2000*(px*V[0]+py*V[1]+pz*V[2]);
   if(u<0||u>=w-1||v<0||v>=h-1)continue;
   const ix=Math.floor(u),iy=Math.floor(v),fx=u-ix,fy=v-iy,i=(iy*w+ix)*4,j=(y*W+x)*4;
   const a=(1-fx)*(1-fy),b=fx*(1-fy),c=(1-fx)*fy,d=fx*fy;
   for(let ch=0;ch<4;ch++)D[j+ch]=pixels[i+ch]*a+pixels[i+4+ch]*b+pixels[i+w*4+ch]*c+pixels[i+w*4+4+ch]*d;
  }
 }
 tx.putImageData(out,0,0);
 const cast=p=>{const k=(.004-L[1])/(p[1]-L[1]);return[(L[0]+k*(p[0]-L[0])-minX)*K,(maxZ-L[2]-k*(p[2]-L[2]))*K]};
 for(const rod of rods){
  let A=rod.A_world,B=rod.B_world;const dy=B[1]-A[1];let lo=0,hi=1;
  if(Math.abs(dy)<1e-9){if(A[1]<=.004||A[1]>=lamp.y-.002)continue;}
  else{const t0=(.00401-A[1])/dy,t1=(lamp.y-.002-A[1])/dy;lo=Math.max(0,Math.min(t0,t1));hi=Math.min(1,Math.max(t0,t1));if(lo>=hi)continue;const from=A;A=from.map((v,i)=>v+lo*(B[i]-v));B=from.map((v,i)=>v+hi*(B[i]-v));}
  tx.strokeStyle='#21160d';tx.lineWidth=5;tx.lineCap='round';tx.beginPath();tx.moveTo(...cast(A));tx.lineTo(...cast(B));tx.stroke();
 }
 return {pup:{name:'held_turtle_projected_shadow',rig:[{part:'plane',parent:null,at:[0,0],layer:0}],parts:{plane:{bounds:[minX*1000,minZ*1000,maxX*1000,maxZ*1000],t:texture,r:texture}}},pose:{angles:{},rootAngle:0,facing:1},root:[0,0],dist:0,rods:[]};
}
