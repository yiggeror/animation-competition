// New natural-body consumer. Never falls back to old child drawings.
import {renderCustomState} from './s20_natural_cam20.js';
export const FPS=24,DURATION=127/24;
const BASE='/assets/chars/s20_natural_20261021/';
let init,sequence; const geometry=new Map();
export async function getSequenceInfo(){
 await(init||=(async()=>{const r=await fetch(BASE+'sequence.json');if(!r.ok)throw Error('Missing natural S20 sequence');sequence=await r.json();})());return sequence;
}
export async function renderFrame(ctx,t,W,H){
 const q=await getSequenceInfo(),f=Math.max(0,Math.min(q.totalFrames-1,Math.floor(t*FPS+1e-7)));
 if(f>=q.laughStart){const laugh=await import('./s20_laugh_compact8_drawn.js');return laugh.renderFrame(ctx,(144+f-q.laughStart)/FPS,W,H);}
 const row=q.states.find(s=>f>=s.start&&f<=s.end);
 if(!geometry.has(row.geometry)){const r=await fetch(row.geometry);if(!r.ok)throw Error('Missing natural S20 geometry '+row.geometry);geometry.set(row.geometry,await r.json());}
 return renderCustomState(ctx,row.sourceFrame/FPS,W,H,{people:row.people,geometry:geometry.get(row.geometry)});
}
export async function render(ctx,t,W,H){return renderFrame(ctx,+t||0,W,H);}
