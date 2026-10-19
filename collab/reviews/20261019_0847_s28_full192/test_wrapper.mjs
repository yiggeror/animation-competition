import assert from 'node:assert/strict';
import {routeFrame,routeTime,createFullS28,DURATION} from './s28_full192.mjs';
assert.equal(DURATION,8);for(let f=0;f<192;f++)assert.equal(routeFrame(f).part,f<132?'stage':'phone');
assert.equal(routeTime(5.5-1e-8).part,'stage');assert.equal(routeTime(5.5).part,'phone');assert.equal(routeFrame(191).part,'phone');
for(const f of[-1,192,NaN,Infinity,1.5])assert.throws(()=>routeFrame(f));for(const t of[-1,8,NaN])assert.throws(()=>routeTime(t));
const calls=[];const full=createFullS28({getStage:async()=>({renderFrame:async(...args)=>calls.push(['stage',args[1]])}),renderPhone:async(...args)=>calls.push(['phone',args[1]])});
await full.renderFrame(null,131/24,1920,1080);await full.renderFrame(null,132/24,1920,1080);await full.render(null,JSON.stringify({t:191/24}),1920,1080);
assert.deepEqual(calls,[['stage',131/24],['phone',132/24],['phone',191/24]]);console.log('PASS all192 frame routes, exactcut,192reject, and renderer dispatch');
