// One actual F060 local heel finish diagnostic. Same fixed arm/fingers/depth, new generated heel pixels only.
import {renderPaint,loadImg} from '../../../../../../js/paint/paintshot.js';
import {shot as motherShot} from '../../../F048_F052_actual_20261019/F052/scene/s12_F052_actual_arm_scene.js';
export const DURATION=64/24;
let artPromise,bgPromise;
async function art(){return artPromise ||= Promise.all(['../layers/F060_BG_person.png','../layers/F060_FG_true_front_fingers.png'].map(async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('Missing actual056 art '+p);return createImageBitmap(await r.blob());}));}
async function bg(){return bgPromise ||= (async()=>{const im=await loadImg(new URL('../../../right_hand_lower_rod_inputs_20261019/first034_040/code_props/background_box_cloth_UNCHANGED.png',import.meta.url).href);if(!im)throw Error('Missing original unchanged room/box/cloth');const c=new OffscreenCanvas(1920,1080);c.getContext('2d').drawImage(im,0,0);return c;})();}
export const shot={...motherShot,layers:async t=>{const ls=await motherShot.layers(t);const ims=await art();return [ls[0],{...ls[1],img:ims[0]},ls[2],{...ls[3],img:ims[1]},ls[4]];}};
export async function renderFrame(ctx,t,w,h){if(Math.floor(t*24+1e-9)!==60)throw RangeError('F060 one-frame diagnostic only');shot.bg=await bg();return renderPaint(ctx,t,w,h,shot);}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
