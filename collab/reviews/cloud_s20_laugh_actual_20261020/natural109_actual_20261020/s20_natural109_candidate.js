// Actual short adjacency: no failed107 body, no diagnostic paper raster.
import {renderCustomState} from '../../../../js/anim/s20_cam20_drawn.js';
export const DURATION=8,FPS=24;
const BASE='/collab/reviews/cloud_s20_laugh_actual_20261020/natural109_actual_20261020/';
const states=[{key:104,start:104,end:106,geometry:'F104_FINITE_BOUNDARY.json',people:'F104_PEOPLE_NO_DETACHED_WOOD.png'},{key:'natural109',start:107,end:110,geometry:'F109_RENDER_GEOMETRY.json',people:'PAIR109_NATIVE_COMPOSITE.png'},{key:112,start:111,end:112,geometry:'F112_FINITE_BOUNDARY.json',people:'F112_PEOPLE_NO_DETACHED_WOOD.png'}];
let prepared;
export async function getSequenceInfo(){await(prepared||=Promise.all(states.map(async s=>s.data=await fetch(BASE+s.geometry).then(r=>r.json()))));return{fps:24,totalFrames:192,availableIntervals:[[104,112]],status:'NATURAL109_ADJACENCY_CANDIDATE_NOT_MOTION_ACCEPTANCE',states:states.map(({data,...s})=>s),knownGap:'No qualified whole natural107; new109 is provisionally four exposures, no interpolation or paper pose alteration to hide missing action.'};}
export async function renderFrame(ctx,t,w,h){await getSequenceInfo();const f=Math.floor(t*24+1e-7),s=states.find(s=>f>=s.start&&f<=s.end);if(!s)throw RangeError('Only104–112 adjacency is bound');return renderCustomState(ctx,t,w,h,{geometry:s.data,people:BASE+s.people});}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||109/24,w,h);}
