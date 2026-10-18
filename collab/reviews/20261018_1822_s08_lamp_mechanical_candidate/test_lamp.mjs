// Command recorder and endpoint math only; explicitly not a Canvas-render test.
import assert from 'node:assert/strict';import fs from 'node:fs';import crypto from 'node:crypto';
import * as C from './lamp_mechanical_candidate.js';import * as O from './source_evidence/lamp_source_0c215550.js';
const scale=14/18.5,base=[1415,965.6];
class PathRecorder{constructor(){this.ops=[];}moveTo(...a){this.ops.push(['moveTo',...a]);}bezierCurveTo(...a){this.ops.push(['bezierCurveTo',...a]);}lineTo(...a){this.ops.push(['lineTo',...a]);}closePath(...a){this.ops.push(['closePath',...a]);}}
globalThis.Path2D=PathRecorder;
function invoke(lamp,lift){const ops=[];const ctx=new Proxy({},{get:(_,k)=>(...a)=>ops.push([k,...a]),set:(_,k,v)=>{ops.push(['set',k,v]);return true;}});const result=lamp(ctx,lift,false);return{ops,result};}
const world=([x,y])=>[base[0]-(x-C.LX)*scale,base[1]+(y-C.LB)*scale];
const point=(a,b,tol=1e-9)=>a.forEach((v,i)=>assert.ok(Math.abs(v-b[i])<tol,`${a} != ${b}`));
const expected=[[1254.039,737.535],[1242.15,750.95],[1233.953,766.894]];
const states=[];
for(const [i,lift] of [0,.5,1].entries()){
 const n=invoke(C.lamp,lift),o=invoke(O.lamp,lift),lever=world(n.result.lever),rot=n.ops.filter(x=>x[0]==='rotate');
 assert.equal(rot.length,1);assert.equal(rot[0][1],-.85+lift*.5);
 // Expected values rounded in the approved diagram, exact values follow source transform.
 point(lever,expected[i],i===1?.005:.001);
 assert.deepEqual(n.ops.filter(x=>x[0]!=='rotate'),o.ops.filter(x=>x[0]!=='rotate'));
 assert.deepEqual(n.result.wick,o.result.wick);assert.deepEqual(n.result.globeTop,o.result.globeTop);
 const rise=(world(invoke(C.lamp,0).result.globeTop)[1]-world(n.result.globeTop)[1]);assert.ok(Math.abs(rise-lift*110*scale)<1e-9);
 if(lift===1){point(n.result.lever,o.result.lever);assert.deepEqual(n.ops,o.ops);}
 states.push({frame:[23,25,27][i],lift,angle:rot[0][1],lever_screen:lever,old_lever_screen:world(o.result.lever),wick_screen:world(n.result.wick),globe_top_screen:world(n.result.globeTop),globe_rise:rise,non_lever_commands_identical:true});
}
assert.ok(states[0].lever_screen[1]<states[1].lever_screen[1]&&states[1].lever_screen[1]<states[2].lever_screen[1]);
assert.ok(states[0].globe_top_screen[1]>states[1].globe_top_screen[1]&&states[1].globe_top_screen[1]>states[2].globe_top_screen[1]);
for(let j=0;j<=100;j++){
 const lift=j/100,n=invoke(C.lamp,lift),o=invoke(O.lamp,lift);
 assert.deepEqual(n.ops.filter(x=>x[0]!=='rotate'),o.ops.filter(x=>x[0]!=='rotate'));
 assert.deepEqual(n.result.wick,o.result.wick);assert.deepEqual(n.result.globeTop,o.result.globeTop);
}
const oldSource=fs.readFileSync(new URL('./source_evidence/lamp_source_0c215550.js',import.meta.url),'utf8');
const newSource=fs.readFileSync(new URL('./lamp_mechanical_candidate.js',import.meta.url),'utf8');
assert.equal(newSource,oldSource.replace('const la = 0.55 - lift * 0.9;','const la = -0.85 + lift * 0.5;'));
const first=invoke(C.lamp,0);point(world(first.result.lever),states[0].lever_screen);
const result={status:'PASS_LOCAL_MECHANICAL_CONTRACT_ONLY_NOT_CANVAS',only_source_change:'const la = 0.55 - lift * 0.9; → const la = -0.85 + lift * 0.5;',all_other_lamp_source_bytes_identical:true,non_lever_commands_compared_at_lifts:101,pivot_screen:world([C.LX+150,C.LB-230]),lever_length_screen:95*scale,frame000_lever_screen:world(first.result.lever),frame000_equals_023_unpressed:true,frame027_endpoint_all_draw_commands_unchanged:true,states,actual_canvas_frames:0};
fs.writeFileSync(new URL('./MECHANICAL_CHECK.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
