// Run from repo root: node collab/reviews/20261018_three_shot_code_fix/s03/check_s03.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { pose, DURATION } from '../../../../js/anim/s03.js';
const baseline = JSON.parse(fs.readFileSync(new URL('./frozen_poses.json', import.meta.url)));
function compare(a,b,path='') {if(typeof a==='number') assert.ok(Math.abs(a-b)<1e-10,`${path}: ${a} != ${b}`);else if(a&&typeof a==='object') {assert.deepEqual(Object.keys(a),Object.keys(b));for(const k of Object.keys(a))compare(a[k],b[k],path+'.'+k);}else assert.equal(a,b,path);}
for(const f of baseline) compare(pose(f.t),f.pose,`frozen t=${f.t}`);
assert.equal(DURATION,4);
const S=P=>{const a=P.lean||0,x=-14.6,y=-103.5+1.2+75;return[x*Math.cos(a)-y*Math.sin(a),-75+x*Math.sin(a)+y*Math.cos(a)];};
const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
let upperError=0,foreError=0,maxElbowStep=0,maxWristStep=0,minWristY=Infinity,maxWristY=-Infinity,prev=null;
for(let f=0;f<96;f++){const P=pose(f/24).P,a=P.armL,s=S(P);assert.ok([...s,...a.elbow,...a.hand].every(Number.isFinite));upperError=Math.max(upperError,Math.abs(distance(a.elbow,s)-21.5));foreError=Math.max(foreError,Math.abs(distance(a.elbow,a.hand)-19.5));if(prev){maxElbowStep=Math.max(maxElbowStep,distance(a.elbow,prev.elbow));maxWristStep=Math.max(maxWristStep,distance(a.hand,prev.hand));}prev=a;minWristY=Math.min(minWristY,a.hand[1]+P.y);maxWristY=Math.max(maxWristY,a.hand[1]+P.y);}
assert.ok(upperError<1e-10&&foreError<1e-10,'fixed segment lengths');
assert.ok(maxElbowStep<2.5,'no large elbow jump at 24fps');
assert.ok(maxWristStep<5.5,'bounded down/reach arc at 24fps');
for(const t of [34/24,44/24]){const before=pose(t-1e-7).P.armL,after=pose(t+1e-7).P.armL;assert.ok(distance(before.elbow,after.elbow)<1e-5);assert.ok(distance(before.hand,after.hand)<1e-5);}
const result={status:'STRUCTURE_ONLY_PASS',frozenPoseTimes:baseline.map(x=>x.t),frames:96,upperErrorCm:upperError,foreErrorCm:foreError,maxElbowStepCm:maxElbowStep,maxWristStepCm:maxWristStep,wristWorldYRange:[minWristY,maxWristY],actualRenderRequired:true,warning:'The local arm-only restore removes the lap-mask cut outside the bowl. Wrist still exits the frame during the down/reach; actual bowl occlusion and reentry require Opus render, not numerical acceptance.'};
console.log(JSON.stringify(result,null,2));
