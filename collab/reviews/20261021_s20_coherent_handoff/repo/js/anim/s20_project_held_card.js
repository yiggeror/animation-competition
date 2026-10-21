// Inverse camera-ray sampling of the actual rigid paper plane, not an affine billboard.
export function projectHeldCard(source,cam,plane,W=1920,H=1080){
 const out=new OffscreenCanvas(W,H),ctx=out.getContext('2d'),src=source.getContext('2d').getImageData(0,0,source.width,source.height),dst=ctx.createImageData(W,H),S=src.data,D=dst.data;
 const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),C=cam.C,O=plane.origin,N=plane.normal,U=plane.axisX,V=plane.axisY,n=dot(O.map((v,i)=>v-C[i]),N);
 for(let y=0;y<H;y++)for(let x=0;x<W;x++){
  const sx=(x+.5-W/2)/cam.focal,sy=(H/2-y-.5)/cam.focal,r=cam.fwd.map((v,i)=>v+sx*cam.right[i]+sy*cam.up[i]),t=n/dot(r,N);if(t<=0)continue;
  const p=C.map((v,i)=>v+t*r[i]-O[i]),u=800+2000*dot(p,U)-.5,v=700-2000*dot(p,V)-.5,ix=Math.floor(u),iy=Math.floor(v);if(ix<0||iy<0||ix>=source.width-1||iy>=source.height-1)continue;
  const fx=u-ix,fy=v-iy,j=(y*W+x)*4;let alpha=0,colors=[0,0,0];
  for(let dy=0;dy<2;dy++)for(let dx=0;dx<2;dx++){const k=((iy+dy)*source.width+ix+dx)*4,w=(dx?fx:1-fx)*(dy?fy:1-fy),a=S[k+3]*w;alpha+=a;for(let c=0;c<3;c++)colors[c]+=S[k+c]*a;}
  if(alpha){for(let c=0;c<3;c++)D[j+c]=colors[c]/alpha;D[j+3]=alpha;}
 }
 ctx.putImageData(dst,0,0);return out;
}
