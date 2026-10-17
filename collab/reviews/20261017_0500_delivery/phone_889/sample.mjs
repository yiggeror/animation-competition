import fs from 'node:fs';
import {state} from './source/js/code/s05.js';
import {SHOTS} from './source/js/film/edl.js';
const code=fs.readFileSync(new URL('./source/js/code/s05.js',import.meta.url),'utf8');
const defs=code.slice(code.indexOf('const T_OFF'),code.indexOf('export function state'));
const {MASH,PRESS,T_OFF}=new Function(defs+';return {MASH,PRESS,T_OFF};')();
const samples=Array.from({length:96},(_,frame)=>({frame,t:frame/24,...state(frame/24)}));
function runs(items,pred){const result=[];for(const s of items){if(!pred(s))continue;const last=result.at(-1);if(last&&last.last===s.frame-1)last.last=s.frame;else result.push({first:s.frame,last:s.frame});}return result.map(r=>({...r,frames:r.last-r.first+1}));}
const B=runs(samples,s=>s.press>=.5),main=B.filter(r=>r.last/24<T_OFF),late=B.filter(r=>r.first/24>=T_OFF);
const gaps=main.slice(0,-1).map((r,i)=>{const next=main[i+1];const rows=samples.filter(s=>s.frame>r.last&&s.frame<next.first);return {after_tap:i+1,frames:rows.map(s=>s.frame),press:rows.map(s=>s.press),zero_frames:rows.filter(s=>s.press===0).map(s=>s.frame)};});
let absolute=0;const timeline={};for(const s of SHOTS){timeline[s.id]={start:absolute,duration:s.dur,has_render_module:!!s.mod};absolute+=s.dur;}
const out={commit:'889e012935489265a22fd8de208cce4b3e651fed',phone_implementation_commit:'94693da567d9ff15ba3e60da6cfc944706d326f0',method:'Node imports of fixed git-show source; actual state(f/24), f0..95; B uses press>=0.5.',fps:24,MASH,PRESS,T_OFF,B_runs:B,main_B_runs:main,late_B_runs:late,max_B_frames:Math.max(...B.map(r=>r.frames)),max_main_B_frames:Math.max(...main.map(r=>r.frames)),release_between_main_B_runs:gaps,main_taps_each_have_distinct_B_run:main.length===MASH.length,partial_A_frames:samples.filter(s=>s.press>0&&s.press<.5).map(s=>s.frame),exact_half_frames:samples.filter(s=>s.press===.5).map(s=>s.frame),bolt_visible_runs:runs(samples,s=>s.status.bolt>0),level2_runs:runs(samples,s=>s.status.level===2),screenOn_runs:{full:runs(samples,s=>s.screenOn===1),dim:runs(samples,s=>s.screenOn===.35),off:runs(samples,s=>s.screenOn===0)},timeline:{S04:timeline.S04,S05:timeline.S05},planned_cut:timeline.S04.start+.6,samples};
fs.writeFileSync(new URL('./sampling.json',import.meta.url),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({...out,samples:undefined},null,2));
