// Review-only actual F036 camera/light. No production source is changed.
import {loadImg,renderPaint} from '/js/paint/paintshot.js';
import {sourceShot} from '/js/paint/shots/s29.js?readonlyShotExport=1';
const query=new URLSearchParams(location.search),src=query.get('candidate');
if(!src)throw Error('Explicit registered native candidate PNG required');
const t=36/24,W=1920,H=1080;
const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
const camera=sourceShot.cam(t),k=camera.fit*W/sourceShot.size[0];
const ox=W/2-camera.x*k,oy=H/2-camera.y*k;
const mother=await loadImg(src);if(!mother)throw Error('Registered native candidate unavailable');
const albedo=canvas(W,H),ax=albedo.getContext('2d');ax.imageSmoothingQuality='high';ax.setTransform(k,0,0,k,ox,oy);
const bg=await loadImg(sourceShot.bg);ax.drawImage(bg,0,0,...sourceShot.size);
const sourceLayers=await sourceShot.layers(t),originalGM=sourceLayers[2];
const uniformGM={...originalGM,y:originalGM.y+30/k};
for(let i=0;i<sourceLayers.length;i++){
 if(i===4)continue; // Locked director decision: both puppets remain with grandma.
 const L=i===2?uniformGM:sourceLayers[i],img=i===2?mother:L.img;
 ax.save();ax.globalAlpha=L.alpha??1;ax.translate(L.x,L.y);ax.scale(L.sc,L.sc);ax.drawImage(img,0,0);ax.restore();
}
const light=sourceShot.light(t),map=L=>({...L,x:L.x*k+ox,y:L.y*k+oy,r:L.r*k});
const local={bg:albedo,size:[W,H],light:()=>({...light,lights:light.lights.map(map)}),glow:()=>sourceShot.glow(t).map(map),
 emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);sourceShot.emit(x,t);x.restore();},cam:()=>({x:W/2,y:H/2,fit:1})};
const final=document.getElementById('frame');await renderPaint(final.getContext('2d'),t,W,H,local);
const s=k*uniformGM.sc,offset=[ox+k*uniformGM.x,oy+k*uniformGM.y],toScene=p=>p.map((v,i)=>v*s+offset[i]);
window.payload={'02_FORMAL_F036.png':final.toDataURL()};
window.geometry={frame:36,time:t,actualCamera:camera,actualLight:light,candidateURL:src,wholeMotherSceneMatrix:[s,0,0,s,...offset],
 sourceMotherLayerReplacement:2,sourceOldChildTurtleExcluded:4,originalGMPlacement:{x:originalGM.x,y:originalGM.y,sc:originalGM.sc},
 unchangedPriorUniformMotherDownwardOutputAdjustment:30,sourceOldGrandmaWarpNotDrawn:true,sourceOldABTurnNotUsed:t<8.1,
 newImagegenCalls:0,scope:'One actual F036 camera candidate only; no full-shot or production acceptance'};
window.ready=true;
