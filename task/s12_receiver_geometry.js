// S12-only visual 2.5D receiver model. No frame/time/rise gate.
// Existing code identifies lights[1] as the patch of lantern light on the lid,
// not a second emitter. Both lantern terms share the same transmission;
// ambient is not occluded. Unmeasured depths are explicit construction units.
export const MODEL={lampXY:[-350,760],lampZ:-1780,paperRootZ:0,boxFrontZ:-215,receiverZ:215,frontX:[1000,1860],frontRimY:800,rearRimY:760,floorY:1040,lid:[[1020,760],[1840,760],[1825,450],[1035,450]],pointSourceAA:1.5,depthBasis:'recover relative paper depth from original matrix; not measured anatomy',depthAssumption:'box depth=half860px width=430; lantern front distance equals lateral distance to box center(45degree construction), not fitted to old shadow offset'};
const W=1920,H=1080,ROI=[1010,440,1845,765],cache=new WeakMap();
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),lin=v=>(v/255)**2.2;
function inside(x,y){return y>=450&&y<=760&&x>=1035-(y-450)*15/310&&x<=1825+(y-450)*15/310}
function planeOf(row){const m=row.prop.matrix,a=m[0][0],b=m[0][1],c=m[1][0],d=m[1][1],g0=a*a+c*c,g1=b*b+d*d,g01=a*b+c*d,s2=(g0+g1+Math.hypot(g0-g1,2*g01))/2,z0=Math.sqrt(Math.max(0,s2-g0)),z1=z0>1e-8?-g01/z0:Math.sqrt(Math.max(0,s2-g1)),det=a*d-b*c;return{kx:(z0*d-z1*c)/det,ky:(-z0*b+z1*a)/det,depth:[z0,z1],scale:Math.sqrt(s2)}}
function blocked(L,P){
 const V=P.map((v,i)=>v-L[i]),D=430;
 const walls=[{n:[0,0,1],c:-215,type:'front'},{n:[1,0,-20/D],c:1010,type:'side'},{n:[1,0,20/D],c:1850,type:'side'},{n:[0,1,40/D],c:780,type:'cloth'}];
 for(const w of walls){const den=dot(w.n,V);if(Math.abs(den)<1e-9)continue;const u=(w.c-dot(w.n,L))/den;if(u<=1e-6||u>=1-1e-6)continue;const q=L.map((v,i)=>v+u*V[i]),z=q[2];if(z< -215||z>215)continue;const left=1010+20*z/D,right=1850-20*z/D,top=780-40*z/D;
  if(w.type==='front'&&q[0]>=1000&&q[0]<=1860&&q[1]>=800&&q[1]<=1040)return true;
  if(w.type==='side'&&q[1]>=top&&q[1]<=1040)return true;
  if(w.type==='cloth'&&q[0]>=left&&q[0]<=right)return true;
 }
 return false;
}
function projectedField(row,props){
 if(cache.has(props))return cache.get(props);
 const [x0,y0,x1,y1]=ROI,w=x1-x0,h=y1-y0,p=row.prop,pl=planeOf(row),L=[...MODEL.lampXY,MODEL.lampZ],rz=MODEL.receiverZ,numerator=pl.kx*(L[0]-p.root[0])+pl.ky*(L[1]-p.root[1])-L[2],src=props.trans.getContext('2d').getImageData(0,0,W,H).data,c=new OffscreenCanvas(w,h),x=c.getContext('2d'),im=x.createImageData(w,h),out=im.data;let hits=0,occluded=0;
 const sample=(sx,sy)=>{if(sx<0||sy<0||sx>=W-1||sy>=H-1)return null;const ix=Math.floor(sx),iy=Math.floor(sy),fx=sx-ix,fy=sy-iy,acc=[0,0,0,0];for(const[dx,dy,k]of[[0,0,(1-fx)*(1-fy)],[1,0,fx*(1-fy)],[0,1,(1-fx)*fy],[1,1,fx*fy]]){const j=((iy+dy)*W+ix+dx)*4,al=src[j+3]/255;acc[3]+=k*al;for(let ch=0;ch<3;ch++)acc[ch]+=k*al*lin(src[j+ch]);}return acc};
 for(let yy=0;yy<h;yy++)for(let xx=0;xx<w;xx++){const k=(yy*w+xx)*4,qx=x0+xx+.5,qy=y0+yy+.5;out[k]=out[k+1]=out[k+2]=out[k+3]=255;if(!inside(qx,qy))continue;
  const den=rz-L[2]-pl.kx*(qx-L[0])-pl.ky*(qy-L[1]);if(Math.abs(den)<1e-8)continue;const u=numerator/den;if(u<=0||u>=1)continue;const P=[L[0]+u*(qx-L[0]),L[1]+u*(qy-L[1]),L[2]+u*(rz-L[2])],s=sample(P[0],P[1]);if(!s||s[3]<1e-4)continue;if(blocked(L,P)){occluded++;continue;}hits++;for(let ch=0;ch<3;ch++)out[k+ch]=Math.round(255*(1-s[3]+s[ch]));
 }
 x.putImageData(im,0,0);
 // Thin rods use supplied existing2.5D endpoints where available. The early
 // drawing consumer has no rod depth: its hand endpoint uses constructionZ0.
 const fwd=P=>{if(P[2]<=L[2]||P[2]>=rz||blocked(L,P))return null;const u=(rz-L[2])/(P[2]-L[2]);return[L[0]+u*(P[0]-L[0])-x0,L[1]+u*(P[1]-L[1])-y0,u]};
 x.globalCompositeOperation='multiply';x.strokeStyle='rgb(14,7,3)';x.lineCap='round';
 for(const role of ['R','L']){const given=props.rods3d?.[role],a2=props.hinges[role],b2=props.free[role],a=given?.A||[a2[0],a2[1],pl.kx*(a2[0]-p.root[0])+pl.ky*(a2[1]-p.root[1])],b=given?.B||[b2[0],b2[1],0];let last=null;for(let i=0;i<=32;i++){const P=a.map((v,k)=>v+(b[k]-v)*i/32),q=fwd(P);if(q&&last){x.lineWidth=7*(q[2]+last[2])/2;x.beginPath();x.moveTo(last[0],last[1]);x.lineTo(q[0],q[1]);x.stroke()}last=q;}}
 x.globalCompositeOperation='source-over';const soft=new OffscreenCanvas(w,h),sx=soft.getContext('2d');sx.fillStyle='#fff';sx.fillRect(0,0,w,h);sx.filter=`blur(${MODEL.pointSourceAA}px)`;sx.drawImage(c,0,0);const field=sx.getImageData(0,0,w,h).data;
 const data={field,w,h,hits,occluded,plane:pl};cache.set(props,data);return data;
}
export function receiverProjectionBackground(base,row,props,light){
 const data=projectedField(row,props),[x0,y0]=ROI,{w,h,field}=data,out=new OffscreenCanvas(W,H),x=out.getContext('2d');x.drawImage(base,0,0);const patch=x.getImageData(x0,y0,w,h),rgb=patch.data;
 for(let yy=0;yy<h;yy++)for(let xx=0;xx<w;xx++){const px=x0+xx+.5,py=y0+yy+.5;if(!inside(px,py))continue;const k=(yy*w+xx)*4;
  const lamp=[0,0,0];for(const l of light.lights||[]){const d=Math.hypot(px-l.x,py-l.y)/l.r;if(d>=1)continue;const q=l.i*(1-d)**(l.falloff??2)/(1+8*d*d);for(let ch=0;ch<3;ch++)lamp[ch]+=q*l.color[ch]}
  for(let ch=0;ch<3;ch++){const ambient=light.ambient?.[ch]||0,total=ambient+lamp[ch],tr=field[k+ch]/255,factor=total>0?(ambient+lamp[ch]*tr)/total:1;rgb[k+ch]=Math.round(rgb[k+ch]*factor**(1/2.2));}
 }
 x.putImageData(patch,x0,y0);globalThis.__S12_VISIBILITY_AUDIT={source_key:row.key,receiver_pixels_hit:data.hits,blocked_caster_samples:data.occluded,relative_paper_depth_basis:data.plane.depth,model:MODEL,condition:'lamp->paper intersection before lid, not blocked by finite front/side/cloth proxies, receiver polygon hit; no frame gate'};return out;
}
