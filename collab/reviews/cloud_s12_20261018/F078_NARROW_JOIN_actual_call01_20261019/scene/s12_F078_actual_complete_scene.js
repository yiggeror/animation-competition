// Actual F078 narrow-knee connector final gate: fixed true074supports + unchanged true078active upper + one true new registered local output.
import {renderPaint,loadImg} from '../../../../../js/paint/paintshot.js';
import {shot as motherShot} from '../../F048_F052_actual_20261019/F052/scene/s12_F052_actual_arm_scene.js';
export const DURATION=79/24;
let artPromise,bgPromise;
async function art(){return artPromise ||= Promise.all(['../layers/F078_BG_person.png','../layers/F078_FG_true_front_fingers.png','../../F078_COMPLETE_TARGET_from_FINAL074_20261019/code_props/F078_TRUE_CRANE_TWO_RODS_SAME_RIGID_GRIPS.png'].map(async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('Missing actual070 art '+p);return createImageBitmap(await r.blob());}));}
async function bg(){return bgPromise ||= (async()=>{const im=await loadImg(new URL('../../F078_COMPLETE_TARGET_from_FINAL074_20261019/code_props/F078_BOX_CLOTH_UNLOADED_CONTEXT.png',import.meta.url).href);if(!im)throw Error('Missing frozen approved cloth-unloading context');const c=new OffscreenCanvas(1920,1080);c.getContext('2d').drawImage(im,0,0);return c;})();}
export const shot={...motherShot,layers:async t=>{const ls=await motherShot.layers(t),ims=await art();return [ls[0],{...ls[1],img:ims[0]},{img:ims[2],x:0,y:0,sc:1},{...ls[3],img:ims[1]},ls[4]];}};
export async function renderFrame(ctx,t,w,h){if(Math.floor(t*24+1e-9)!==78)throw RangeError('F078 one-frame diagnostic only');shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
