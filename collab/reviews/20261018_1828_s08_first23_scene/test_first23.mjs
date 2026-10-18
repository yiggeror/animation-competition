// Contracts and mock draw commands only. This does not render Canvas pixels.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import path from 'node:path';import {pathToFileURL} from 'node:url';
import * as C from './contract.js';import {LAYER_ARTS} from './layer_contract.js';
const local=new URL('.',import.meta.url);
function dep(name,top){const repo=new URL('../'+name+'/',local);return fs.existsSync(new URL('package.json',repo))?repo:new URL('../../../../'+top+'/collab/reviews/'+name+'/',local);}
const base=process.argv[2]?pathToFileURL(path.resolve(process.argv[2])+'/'):dep('20261018_1800_s08_first20_scene','astra_s08_first20_scene_20261018_1800');
const fixed=process.argv[3]?pathToFileURL(path.resolve(process.argv[3])+'/'):dep('20261018_1822_s08_lamp_mechanical_candidate','astra_s08_lamp_mechanical_candidate_20261018_1822');
const old=await import(new URL('contract.js',base));
assert.equal(C.FRAME_COUNT,23);assert.equal(C.DURATION,23/24);assert.equal(C.FPS,24);assert.deepEqual(C.EXPOSE.slice(0,-1),old.EXPOSE);assert.deepEqual(C.EXPOSE.at(-1),{start:20,hold:3,asset:'020'});
for(let f=0;f<23;f++)for(const sub of [0,.25,.5,.999]){
 const t=(f+sub)/24,p=C.poseAt(t),A=C.fireAt(t);assert.equal(p.frame,f);assert.equal(A.wick,0);assert.equal(A.lift,0);
 if(f<20){assert.deepEqual(p,old.poseAt(t));assert.deepEqual(A,old.fireAt(t));}
 else{assert.equal(p.asset,'020');assert.deepEqual(p.head,[1062,787]);assert.deepEqual(p.grip,[1034,824]);assert.equal(p.touching,false);assert.equal(A.lit,true);}
}
for(const t of [-1,NaN,Infinity,23/24,1,6])for(const fn of [C.frameAt,C.poseAt,C.fireAt])assert.throws(()=>fn(t),RangeError);
let count=0;for(const [asset,roles] of Object.entries(LAYER_ARTS))for(const a of Object.values(roles)){
 const b=fs.readFileSync(new URL('frames/'+a.filename,local));assert.equal(crypto.createHash('sha256').update(b).digest('hex'),a.sha256);assert.equal(b.readUInt32BE(16),1920);assert.equal(b.readUInt32BE(20),1080);if(Number(asset)<20)assert.ok(b.equals(fs.readFileSync(new URL('frames/'+a.filename,base))));count++;
}assert.equal(count,18);assert.deepEqual(C.TABLE_BOX_CONTACT,old.TABLE_BOX_CONTACT);
class PathRecorder{constructor(){this.ops=[];}moveTo(...a){this.ops.push(['moveTo',...a]);}bezierCurveTo(...a){this.ops.push(['bezierCurveTo',...a]);}lineTo(...a){this.ops.push(['lineTo',...a]);}closePath(...a){this.ops.push(['closePath',...a]);}}
globalThis.Path2D=PathRecorder;
class CanvasRecorder{constructor(w,h){this.width=w;this.height=h;this.ops=[];}getContext(){const ops=this.ops;return new Proxy({},{get:(_,k)=>(...a)=>ops.push([k,...a]),set:(_,k,v)=>{ops.push(['set',k,v]);return true;}});}}
globalThis.OffscreenCanvas=CanvasRecorder;const calls={new:[],old:[]};globalThis.__first23Flame=calls;
async function fixture(source,prior,key){
 let s=source.replace("import {renderPaint,loadImg} from '/js/paint/paintshot.js';","const renderPaint=async()=>{};const loadImg=async url=>({width:1920,height:1080,source:url.split('/').pop()});");
 s=s.replace("import {flameShape} from '/js/code/s08.js';",`const flameShape=(ctx,...a)=>globalThis.__first23Flame[${JSON.stringify(key)}].push(a);`);
 s=s.replace(prior?"'./lamp_mechanical_candidate.js'":"'../20261018_1822_s08_lamp_mechanical_candidate/lamp_mechanical_candidate.js'",JSON.stringify(new URL('lamp_mechanical_candidate.js',fixed).href));
 for(const f of ['contract.js','layer_contract.js'])s=s.replace(prior?"'../20261018_1800_s08_first20_scene/"+f+"'":"'./"+f+"'",JSON.stringify(new URL(f,prior?base:local).href));
 s=s.replace(/new URL\('[^']*frames\/'\+meta.filename,import.meta.url\).href/,"'locked-frames/'+meta.filename");
 return import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
}
const source=fs.readFileSync(new URL('s08_first23_scene.js',local),'utf8'),previous=fs.readFileSync(new URL('s08_first20_lampfix_candidate.js',fixed),'utf8');
const n=await fixture(source,false,'new'),o=await fixture(previous,true,'old');
for(let f=0;f<23;f++){
 const t=f/24,L=await n.shot.layers(t);assert.equal(L.length,f>=17?6:5);for(const a of L){assert.equal(a.x,0);assert.equal(a.y,0);assert.equal(a.sc,1);}
 assert.deepEqual(L[0].img.ops.filter(x=>x[0]==='rotate'),[['rotate',-.85]]);
 assert.equal(L.filter(a=>a.contact).length,f>=17?1:0);n.shot.emit({},t);
 if(f<20){assert.deepEqual(L,await o.shot.layers(t));for(const fn of ['light','glow','cam'])assert.deepEqual(n.shot[fn](t),o.shot[fn](t));o.shot.emit({},t);if(f>=5)assert.deepEqual(calls.new.at(-1),calls.old.at(-1));}
 else{assert.equal(L.filter(a=>a.img.source?.includes('table_box')).length,1);assert.equal(L[4].img.source,'F020_table_box_original_pixels.png');assert.deepEqual(L[4].contact,C.TABLE_BOX_CONTACT);assert.equal(L[5].img.source,'F020_forearms_elbows_original_pixels.png');const light=n.shot.light(t);assert.equal(light.lights.length,1);assert.equal(light.lights[0].x,1062);assert.equal(light.lights[0].y,773);assert.deepEqual(calls.new.at(-1)[0],[1062,789]);}
}
for(const method of ['layers','light','glow','emit','cam']){
 if(method==='layers')await assert.rejects(()=>n.shot.layers(23/24),RangeError);else if(method==='emit')assert.throws(()=>n.shot.emit({},23/24),RangeError);else assert.throws(()=>n.shot[method](23/24),RangeError);
}await assert.rejects(()=>n.renderFrame({},23/24,1920,1080),RangeError);
const functions=s=>s.slice(s.indexOf('async function bg()'),s.indexOf('const layerCache='));assert.equal(functions(source),functions(previous));
const lighting=s=>s.slice(s.indexOf(' light:(t)=>{'),s.indexOf('export async function renderFrame'));assert.equal(lighting(source),lighting(previous));
const result={status:'PASS_STATIC_AND_MOCK_ONLY_ACTUAL_CANVAS_PENDING',frames:23,fps:24,duration:23/24,first20_fixed_lamp_contract_sample_points_exact:80,first20_fixed_lamp_draw_commands_and_lighting_equal:true,old_image_files_byte_equal:15,all_layer_sha256_verified:18,F020_hold:[20,21,22],F020_match_head:[1062,787],F020_grip:[1034,824],F020_box_draws_per_frame:1,F020_box_contact_unchanged_from017:true,lamp_initial_angle_all_frames:-.85,lamp_lift_all_frames:0,wick_flame_all_frames:0,original_scene_and_lighting_functions_bytes_equal:true,all_public_frame_entry_points_reject023:true,actual_canvas_frames:0};
fs.writeFileSync(new URL('TEST_RESULT.json',local),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
