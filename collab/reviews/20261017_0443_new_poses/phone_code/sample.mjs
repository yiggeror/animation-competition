import fs from 'node:fs';
import {state} from './source/js/code/s05.js';
import {pressAt} from './source/js/code/phone_img.js';
import {SHOTS} from './source/js/film/edl.js';
const code=fs.readFileSync(new URL('./source/js/code/s05.js',import.meta.url),'utf8');
const defs=code.slice(code.indexOf('const T_OFF'),code.indexOf('export function state'));
const {MASH,PRESS,T_OFF}=new Function(defs+';return {MASH,PRESS,T_OFF};')();
const fps=24;
const samples=Array.from({length:96},(_,f)=>{const t=f/fps,s=state(t);return {frame:f,t,press:s.press,jumpPressed:s.game.jumpPressed,bolt:s.status.bolt,level:s.status.level,screenOn:s.screenOn};});
function runs(items,predicate){const out=[];let active=null;for(const x of items){if(predicate(x)){if(!active)active={first_frame:x.frame,last_frame:x.frame};active.last_frame=x.frame;}else if(active){out.push(active);active=null;}}if(active)out.push(active);return out.map(r=>({...r,frames:r.last_frame-r.first_frame+1,first_sample_s:r.first_frame/fps,last_sample_s:r.last_frame/fps,frame_coverage_s:(r.last_frame-r.first_frame+1)/fps}));}
const mashSamples=samples.filter(s=>s.t>=MASH[0]-.06&&s.t<=MASH.at(-1)+.18);
const intervals=MASH.map(p=>[p-.03,p+.12]);const merged=[];
for(const [a,b] of intervals){if(merged.length&&a<=merged.at(-1)[1])merged.at(-1)[1]=Math.max(b,merged.at(-1)[1]);else merged.push([a,b]);}
const timeline={};let t=0;for(const sh of SHOTS){timeline[sh.id]={start:t,duration:sh.dur,has_render_module:!!sh.mod};t+=sh.dur;}
const betweenTapMin=MASH.slice(0,-1).map((p,i)=>{const q=MASH[i+1];let min=Infinity,minT=null;for(let k=0;k<=10000;k++){const t=p+(q-p)*k/10000,v=pressAt(t,PRESS);if(v<min){min=v;minT=t;}}return {p,next:q,gap:q-p,minPress:min,min_t:minT};});
const result={commit:fs.readFileSync(new URL('./commit.txt',import.meta.url),'utf8').trim(),method:'Read-only Node import of git-show fixed source; state(f/24) for f=0..95, no renderer called.',fps,MASH,PRESS,T_OFF,samples,press_gt_half_runs:runs(samples,s=>s.press>0.5),release_le_half_runs_during_mash:runs(mashSamples,s=>s.press<=0.5),zero_press_frames_between_first_last_mash:samples.filter(s=>s.t>=MASH[0]&&s.t<=MASH.at(-1)&&s.press===0).map(s=>s.frame),mash_continuous_gt_half_union_open_intervals:merged,between_tap_min_10000_step_grid:betweenTapMin,bolt_visible_runs:runs(samples,s=>s.bolt>0),level2_runs:runs(samples,s=>s.level===2),level1_runs:runs(samples,s=>s.level===1),timeline:{S04:timeline.S04,S05:timeline.S05},planned_powercut_absolute_s:timeline.S04.start+0.6};
fs.writeFileSync(new URL('./sampling.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,samples:undefined,between_tap_min_10000_step_grid:betweenTapMin.map(({gap,minPress})=>({gap,minPress}))},null,2));
