// Actual-source contact footprints. No ellipse substitutes, no character warp.
const CACHE=new WeakMap(),REPORT={};
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
export function currentGroundingReport(){return JSON.parse(JSON.stringify(REPORT));}
const boxes={
 workStool:[[348,1165,398,1182],[600,1165,650,1182],[400,1147,432,1163],[569,1147,600,1163]],
 grandmaFloor:[[387,1010,489,1029],[501,1000,622,1019]],
 child:[[320,1140,390,1165],[614,1154,680,1176],[435,1096,493,1121],[674,1108,727,1135]]
};
function footprint(img,box){
 const [x0,y0,x1,y1]=box.map(Math.round),w=x1-x0,h=y1-y0;
 const c=new OffscreenCanvas(w,h),x=c.getContext('2d');x.drawImage(img,-x0,-y0);
 const p=x.getImageData(0,0,w,h),a=p.data;let base=-1;
 for(let yy=h-1;yy>=0&&base<0;yy--)for(let xx=0;xx<w;xx++)if(a[(yy*w+xx)*4+3]>128){base=yy;break;}
 if(base<0)return null;
 let mass=0,cx=0;
 for(let yy=0;yy<h;yy++)for(let xx=0;xx<w;xx++){
  const i=(yy*w+xx)*4;
  // The real lower-foot alpha shape supplies the footprint. Nothing is expanded.
  if(yy<base-9||yy>base||a[i+3]<=128)a[i+3]=0;
  else{mass+=a[i+3];cx+=xx*a[i+3];}
  a[i]=a[i+1]=a[i+2]=0;
 }
 x.putImageData(p,0,0);return{img:c,x0,y0,base,cx:mass?cx/mass:w/2};
}
function walkingSoleBox(img){
 const c=new OffscreenCanvas(img.width,img.height),x=c.getContext('2d');x.drawImage(img,0,0);
 const a=x.getImageData(0,0,c.width,c.height).data;let bottom=-1;
 const red=(i)=>a[i+3]>180&&a[i]>150&&a[i+1]<100&&a[i+2]<110&&a[i]>a[i+1]*2&&a[i]>a[i+2]*1.8;
 for(let yy=c.height-1;yy>=950&&bottom<0;yy--)for(let xx=800;xx<c.width;xx++)if(red((yy*c.width+xx)*4)){bottom=yy;break;}
 if(bottom<0)return null;let left=c.width,right=0;
 for(let yy=Math.max(950,bottom-18);yy<=bottom;yy++)for(let xx=800;xx<c.width;xx++)if(red((yy*c.width+xx)*4)){left=Math.min(left,xx);right=Math.max(right,xx);}
 return[left-5,bottom-12,right+6,Math.min(c.height,bottom+7)];
}
function material(img,kind,id,nativeStoolOffset,groundedSoleRegions){
 let map=CACHE.get(img);if(!map){map=new Map();CACHE.set(img,map);}const key=kind+':'+id+':'+JSON.stringify([nativeStoolOffset,groundedSoleRegions]);if(map.has(key))return map.get(key);
 let rects=(kind==='grandmaFloor'?boxes.grandmaFloor:kind==='child'?boxes.child:boxes.workStool).map(b=>[...b]);
 if(kind==='child'){
  const dx=nativeStoolOffset?.[0]??(id.includes('141')?-52:id.includes('144')?-26:0),dy=nativeStoolOffset?.[1]??0;rects=rects.map(b=>[b[0]+dx,b[1]+dy,b[2]+dx,b[3]+dy]);
  // Current-source diagnostic support: only lowest standing sole, never hanging feet.
  if(groundedSoleRegions!==undefined)rects.push(...groundedSoleRegions);
  else if(!/^[CDE]_/.test(id)){const sole=walkingSoleBox(img);if(sole)rects.push(sole);}
 }
 const feet=rects.map(b=>footprint(img,b)).filter(Boolean);const value={feet};map.set(key,value);return value;
}
export function groundedShadowLayers(img,M,{kind,id='',light,castAlpha=.12,nativeStoolOffset,groundedSoleRegions}){
 const {feet}=material(img,kind,id,nativeStoolOffset,groundedSoleRegions),layers=[];
 const supports=feet.map(f=>({x:M.x+(f.x0+f.cx)*M.sc,y:M.y+(f.y0+f.base)*M.sc}));
 const slope=p=>clamp((p.x-light[0])/Math.max(50,p.y-light[1]),-1.2,1.2);
 if(feet.length){
  const bottom=Math.max(...feet.map(f=>f.y0+f.base)),p={x:supports.reduce((v,q)=>v+q.x,0)/supports.length,y:M.y+bottom*M.sc};
  layers.push({img,...M,alpha:0,contact:{a:castAlpha,blur:2.1,sy:-.12,skew:slope(p),base:bottom}});
 }
 feet.forEach((f,i)=>{
  const pos={x:M.x+f.x0*M.sc,y:M.y+f.y0*M.sc,sc:M.sc};
  layers.push({img:f.img,...pos,alpha:0,contact:{a:.65,blur:.5,sy:-.65,skew:slope(supports[i]),base:f.base}});
 });
 REPORT[kind]={id,sourceScale:M.sc,light,supports,footNative:feet.map(f=>[f.x0+f.cx,f.y0+f.base]),contactMethod:'Real lower-foot alpha, exact per-foot bottom; native paint contact projection; no ellipse, no common nominal floor1198.',castSlopes:supports.map(slope)};
 return layers;
}
