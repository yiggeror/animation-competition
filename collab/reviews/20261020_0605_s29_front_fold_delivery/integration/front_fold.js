// Candidate only: reuse audited projection, bounded to F090–115. Not CAM approval.
import {loadImg, renderPaint} from '../../paint/paintshot.js';
import {sourceShot} from './scene_source.js';
import {FPS,resolveFrame} from './front_fold_exposure.js';
const canvas = (w,h) => {const c = document.createElement('canvas'); c.width=w; c.height=h; return c;};
export async function renderFrameIndex(ctx, f, w=1920, h=1080) {
  const row=resolveFrame(f); // Fail before loading or drawing anything outside the exact table.
  if (w!==1920 || h!==1080) throw new RangeError('Only the audited 1920×1080 registration is enabled');
  const t=f/FPS, mother=await loadImg(row.url);
  if(!mother) throw Error('Missing locked S29 state '+row.state);
  const camera=sourceShot.cam(t), k=camera.fit*w/sourceShot.size[0], ox=w/2-camera.x*k, oy=h/2-camera.y*k;
  const albedo=canvas(w,h), ax=albedo.getContext('2d'); ax.imageSmoothingQuality='high'; ax.setTransform(k,0,0,k,ox,oy);
  const bg=await loadImg(sourceShot.bg); if(!bg)throw Error('Missing actual background'); ax.drawImage(bg,0,0,...sourceShot.size);
  const sourceLayers=await sourceShot.layers(t), oldGM=sourceLayers[2], GM={...oldGM,y:oldGM.y+30/k};
  for(let i=0;i<sourceLayers.length;i++){
    if(i===4)continue;
    const L=i===2?GM:sourceLayers[i], img=i===2?mother:L.img;
    ax.save(); ax.globalAlpha=L.alpha??1; ax.translate(L.x,L.y); ax.scale(L.sc,L.sc); ax.drawImage(img,0,0); ax.restore();
  }
  const light=sourceShot.light(t), map=L=>({...L,x:L.x*k+ox,y:L.y*k+oy,r:L.r*k});
  const local={bg:albedo,size:[w,h],light:()=>({...light,lights:light.lights.map(map)}),glow:()=>sourceShot.glow(t).map(map),
    emit:x=>{x.save();x.setTransform(k,0,0,k,ox,oy);sourceShot.emit(x,t);x.restore();},cam:()=>({x:w/2,y:h/2,fit:1})};
  await renderPaint(ctx,t,w,h,local);
  const s=k*GM.sc, offset=[ox+k*GM.x,oy+k*GM.y];
  return {globalFrame:f,state:row.state,t,camera,light,sourceSHA256:row.sha256,wholeMotherSceneMatrix:[s,0,0,s,...offset],uniformDownwardAdjustment:30,oldGrandmaWarpNotDrawn:true,oldChildTurtleExcluded:true};
}
