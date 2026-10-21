// S14 final190-frame source glue. Keeps actual source clocks and one-time native registrations.
import {renderFrame as renderGrandma} from '../../../collab/reviews/cloud_s14_scene_20261020/s14_scene.mjs';
import {renderTail} from '../../../collab/reviews/cloud_s14_scene_20261020/s14_tail.mjs';
export const FPS=24,DURATION=190/24;
let rows;
async function exposureRows(){return rows||=(await fetch('/collab/reviews/cloud_s14_scene_20261020/standing_drag_repair_20261021/EXPOSURES_THREE_BRIDGES_132_189.json')).json();}
export async function getSequenceInfo(){return {fps:24,totalFrames:190,grandmaPrefix:[0,131],childTail:[132,189],sourceClocks:'original f/24 retained; no second normalization',tail:await exposureRows()};}
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);if(f<0||f>=190)throw RangeError('S14 exactly190 frames');if(f<132)return renderGrandma(ctx,t,w,h,{groundFix:true,stableGrain:true});const e=(await exposureRows()).find(r=>f>=r.frame&&f<=r.through);if(!e)throw Error('Missing S14 adopted tail exposure '+f);return renderTail(ctx,t,w,h,e,{backstage:true,groundFix:true});}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h);}
