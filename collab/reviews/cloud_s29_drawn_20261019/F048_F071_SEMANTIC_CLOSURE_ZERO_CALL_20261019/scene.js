// Review-only actual camera/light; complete drawn states switch on frozen starts.
import {loadImg,renderPaint} from '/js/paint/paintshot.js';
import {sourceShot} from '/js/paint/shots/s29.js?readonlyShotExport=1';
const plan=await (await fetch('./SOURCES_EXPOSURE_AND_T_LAYER.json')).json();
const drawings=new Map();for(const s of plan.sources){const img=await loadImg(s.usedURL);if(!img)throw Error('Missing locked state '+s.state);drawings.set(s.state,img);}
const W=1920,H=1080,frame=document.getElementById('frame');
const canvas=()=>{const c=document.createElement('canvas');c.width=W;c.height=H;return c;};
window.renderActual=async f=>{
 if(!Number.isInteger(f)||f<48||f>71)throw Error('Only approved short048–071');
 const t=f/24,state=f<54?48:f<60?54:f<66?60:66,mother=drawings.get(state);
 const camera=sourceShot.cam(t),k=camera.fit*W/sourceShot.size[0],ox=W/2-camera.x*k,oy=H/2-camera.y*k;
 const albedo=canvas(),ax=albedo.getContext('2d');ax.imageSmoothingQuality='high';ax.setTransform(k,0,0,k,ox,oy);
 const bg=await loadImg(sourceShot.bg);if(!bg)throw Error('Missing actual background');ax.drawImage(bg,0,0,...sourceShot.size);
 const sourceLayers=await sourceShot.layers(t),oldGM=sourceLayers[2],GM={...oldGM,y:oldGM.y+30/k};
 for(let i=0;i<sourceLayers.length;i++){
  if(i===4)continue; // Locked director decision: no turtle handed to child.
  const L=i===2?GM:sourceLayers[i],img=i===2?mother:L.img;
  ax.save();ax.globalAlpha=L.alpha??1;ax.translate(L.x,L.y);ax.scale(L.sc,L.sc);ax.drawImage(img,0,0);ax.restore();
 }
 const light=sourceShot.light(t),map=L=>({...L,x:L.x*k+ox,y:L.y*k+oy,r:L.r*k});
 const local={bg:albedo,size:[W,H],light:()=>({...light,lights:light.lights.map(map)}),glow:()=>sourceShot.glow(t).map(map),emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);sourceShot.emit(x,t);x.restore();},cam:()=>({x:W/2,y:H/2,fit:1})};
 await renderPaint(frame.getContext('2d'),t,W,H,local);
 const s=k*GM.sc,offset=[ox+k*GM.x,oy+k*GM.y];
 return {png:frame.toDataURL('image/png'),geometry:{globalFrame:f,localFrame:f-48,state,t,camera,light,wholeMotherSceneMatrix:[s,0,0,s,...offset],uniformDownwardAdjustment:30,oldGrandmaWarpNotDrawn:true,oldChildTurtleExcluded:true}};
};
window.ready=true;
