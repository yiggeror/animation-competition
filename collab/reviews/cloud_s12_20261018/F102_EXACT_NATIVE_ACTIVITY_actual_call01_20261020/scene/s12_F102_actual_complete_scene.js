// Unique raw102, one whole-original affine correction; qualified final098 support.
import {renderPaint,loadImg} from '../../../../../js/paint/paintshot.js';
import {shot as motherShot} from '../../F048_F052_actual_20261019/F052/scene/s12_F052_actual_arm_scene.js';
export const DURATION=103/24;
let artPromise,bgPromise;
async function art(){return artPromise ||= Promise.all(['../layers/F102_BG_person.png','../layers/F102_FG_true_front_fingers.png','../../F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020/code_props/F102_TRUE_CRANE_AND_TWO_PHYSICALLY_RIGID_RODS_REFERENCE.png'].map(async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('Missing actual102 art '+p);return createImageBitmap(await r.blob());}));}
async function bg(){return bgPromise ||= (async()=>{const im=await loadImg(new URL('../../F102_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020/code_props/F102_BOX_CLOTH_UNLOAD_CONTEXT_REFERENCE.png',import.meta.url).href);if(!im)throw Error('Missing102 context');const c=new OffscreenCanvas(1920,1080);c.getContext('2d').drawImage(im,0,0);return c;})();}
export const shot={...motherShot,layers:async t=>{const ls=await motherShot.layers(t),ims=await art();return [ls[0],{...ls[1],img:ims[0]},{img:ims[2],x:0,y:0,sc:1},{...ls[3],img:ims[1]},ls[4]];}};
export async function renderFrame(ctx,t,w,h){if(Math.floor(t*24+1e-9)!==102)throw RangeError('F102 one-frame diagnostic only');shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
