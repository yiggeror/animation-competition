import {createS28StageCandidate,freezeS27End,bitmapLayer,project} from './s28_stage_candidate.mjs';
import {renderShot,S,billboardM,DEBUG} from '../../../js/lamp/s06_key.js';
import {cast} from '../../../js/lamp/shots/s26.js';
import * as choreo from '../../../js/lamp/choreo.js';
import {drawPuppet,solve,pointOn} from '../../../js/puppet.js';
import {makeLamp} from '../../../js/lamp/s08_back.js';
const geometry=await(await fetch('./geometry.json')).json();
DEBUG.cam=null;DEBUG.proxy=false;DEBUG.sheetRes=650;DEBUG.fog=0;DEBUG.bloom=.35;
const lamp=makeLamp();
const sheetAtEnd=freezeS27End(cast,choreo,geometry);
const renderer=await createS28StageCandidate({assetsRoot:'../20261019_0820_s28_locked_stage_assets/',repoRoot:'../../../',bindingsFile:'FRAME_BINDINGS.json',localRoot:'./local/',geometry,renderShot,sceneState:S,sheetAtEnd,drawPuppet,extraLayers:async({hostCam,cam})=>{const base=[S.lamp.x,S.lamp.y,S.lamp.z],m=billboardM(hostCam,base,lamp.ox,lamp.oy,lamp.K).map(v=>v/cam.scale),z=project(base,cam)[2];return['metal','glass','flame'].map(k=>bitmapLayer({maps:lamp[k],m,depthCamera:z,cam,id:'lamp_'+k}));}});
const canvas=document.querySelector('canvas');const ctx=canvas.getContext('2d');
window.renderer=renderer;window.ready=true;window.renderS28=async(frame)=>{const before=[S.occ,S.occBack],t=performance.now();await renderer.renderFrame(ctx,frame/24,1920,1080);const out=renderer.getLast();const actors=sheetAtEnd(0,{crane:(await import('../../../js/lamp/crane.js')).makeCrane(1.35,'plain'),RODS:(await import('../../../js/lamp/s06_key.js')).RODS});let contactError=0;actors.forEach((a,i)=>{const sol=solve(a.pup,a.pose);a.rods.forEach((r,j)=>{const p=pointOn(a.pup,sol,r.part,r.at),P=[a.root[0]+(a.pose.facing??1)*p[0]/1000,a.dist,a.root[1]+p[1]/1000],Q=geometry.rods[i*2+j].part_world_m;contactError=Math.max(contactError,Math.hypot(...P.map((v,k)=>v-Q[k])));});});return{...out.meta,elapsedMs:performance.now()-t,statistics:out.stats,sceneProxyRestored:S.occ===before[0]&&S.occBack===before[1],maxOriginalPuppetContactErrorM:contactError,png:canvas.toDataURL('image/png'),foreground:await canvasURL(out.alb),shadow:await canvasURL(out.shadow)};};
async function canvasURL(c){const b=await c.convertToBlob({type:'image/png'});return new Promise(r=>{const x=new FileReader();x.onload=()=>r(x.result);x.readAsDataURL(b);});}
