// Source, contract, geometry and draw-command regression only. No Canvas rasterization.
import fs from 'node:fs';import assert from 'node:assert/strict';import crypto from 'node:crypto';import path from 'node:path';import {pathToFileURL} from 'node:url';
import * as C from './contract.js';import {LAYER_ARTS} from './layer_contract.js';
const local=new URL('.',import.meta.url);
function dep(name,top){const repo=new URL('../'+name+'/',local);return fs.existsSync(new URL('package.json',repo))?repo:new URL('../../../../'+top+'/collab/reviews/'+name+'/',local);}
const base=process.argv[2]?pathToFileURL(path.resolve(process.argv[2])+'/'):dep('20261018_1828_s08_first23_scene','astra_s08_first23_scene_20261018_1828');
const lampDir=dep('20261018_1822_s08_lamp_mechanical_candidate','astra_s08_lamp_mechanical_candidate_20261018_1822');
const old=await import(new URL('contract.js',base));const lamp=await import(new URL('lamp_mechanical_candidate.js',lampDir));
const expectedAvailable=LAYER_ARTS['025']?27:25;
assert.equal(C.FRAME_COUNT,expectedAvailable);assert.equal(C.PLANNED_FRAME_COUNT,27);assert.equal(C.DURATION,C.FRAME_COUNT/24);assert.deepEqual(C.EXPOSE.slice(0,old.EXPOSE.length),old.EXPOSE);
assert.deepEqual(C.EXPOSE[old.EXPOSE.length],{start:23,hold:2,asset:'023'});if(expectedAvailable===27)assert.deepEqual(C.EXPOSE.at(-1),{start:25,hold:2,asset:'025'});
for(let f=0;f<C.FRAME_COUNT;f++)for(const sub of [0,.25,.5,.999]){
 const t=(f+sub)/24,p=C.poseAt(t),A=C.fireAt(t),M=C.mechanismAt(t);assert.equal(p.frame,f);assert.equal(A.wick,0);assert.equal(M.wick,0);assert.equal(A.lift,M.lift);assert.equal(M.lift,f>=25?.5:0);assert.equal(M.handContact,f>=23);
 if(f<23){assert.deepEqual(p,old.poseAt(t));assert.deepEqual(A,old.fireAt(t));}
 else if(f<25){assert.equal(p.asset,'023');assert.deepEqual(p.head,[1070,791]);assert.deepEqual(p.grip,[1042,828]);assert.equal(p.touching,false);}
 else{assert.equal(p.asset,'025');assert.deepEqual(p.head,[1076,794]);assert.deepEqual(p.grip,[1048,831]);assert.equal(p.touching,false);assert.equal(A.lit,true);}
}
for(const t of [-1,NaN,Infinity,C.DURATION,27/24,2,6])for(const fn of [C.frameAt,C.poseAt,C.fireAt,C.mechanismAt])assert.throws(()=>fn(t),RangeError);
let count=0;for(const [asset,roles] of Object.entries(LAYER_ARTS))for(const a of Object.values(roles)){
 const b=fs.readFileSync(new URL('frames/'+a.filename,local));assert.equal(crypto.createHash('sha256').update(b).digest('hex'),a.sha256);assert.equal(b.readUInt32BE(16),1920);assert.equal(b.readUInt32BE(20),1080);if(Number(asset)<23)assert.ok(b.equals(fs.readFileSync(new URL('frames/'+a.filename,base))));count++;
}assert.equal(count,expectedAvailable===27?24:21);assert.deepEqual(C.TABLE_BOX_CONTACT,old.TABLE_BOX_CONTACT);
class PathRecorder{constructor(){this.ops=[];}moveTo(...a){this.ops.push(['moveTo',...a]);}bezierCurveTo(...a){this.ops.push(['bezierCurveTo',...a]);}lineTo(...a){this.ops.push(['lineTo',...a]);}closePath(...a){this.ops.push(['closePath',...a]);}}
globalThis.Path2D=PathRecorder;
class CanvasRecorder{constructor(w,h){this.width=w;this.height=h;this.ops=[];}getContext(){const ops=this.ops;return new Proxy({},{get:(_,k)=>(...a)=>ops.push([k,...a]),set:(_,k,v)=>{ops.push(['set',k,v]);return true;}});}}
globalThis.OffscreenCanvas=CanvasRecorder;globalThis.__s08First27Flames={new:[],old:[]};
async function fixture(source,prior,key){
 let s=source.replace("import {renderPaint,loadImg} from '/js/paint/paintshot.js';","const renderPaint=async()=>{};const loadImg=async url=>({width:1920,height:1080,source:url.split('/').pop()});");
 s=s.replace("import {flameShape} from '/js/code/s08.js';",`const flameShape=(ctx,...a)=>globalThis.__s08First27Flames[${JSON.stringify(key)}].push(a);`);
 s=s.replace("'../20261018_1822_s08_lamp_mechanical_candidate/lamp_mechanical_candidate.js'",JSON.stringify(new URL('lamp_mechanical_candidate.js',lampDir).href));
 for(const f of ['contract.js','layer_contract.js'])s=s.replace("'./"+f+"'",JSON.stringify(new URL(f,prior?base:local).href));
 s=s.replace("new URL('./frames/'+meta.filename,import.meta.url).href","'locked-frames/'+meta.filename");
 if(!prior)s+='\nexport {lampLayerAtLift as __testLampLayerAtLift};';
 return import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
}
const source=fs.readFileSync(new URL('s08_first27_scene.js',local),'utf8'),previous=fs.readFileSync(new URL('s08_first23_scene.js',base),'utf8');
const n=await fixture(source,false,'new'),o=await fixture(previous,true,'old');
for(let f=0;f<C.FRAME_COUNT;f++){
 const t=f/24,L=await n.shot.layers(t),M=C.mechanismAt(t);assert.equal(L.length,f>=17?6:5);for(const a of L){assert.equal(a.x,0);assert.equal(a.y,0);assert.equal(a.sc,1);}
 assert.deepEqual(L[0].img.ops.filter(x=>x[0]==='rotate'),[['rotate',M.angle]]);assert.equal(L.filter(a=>a.contact).length,f>=17?1:0);n.shot.emit({},t);
 if(f<23){assert.deepEqual(L,await o.shot.layers(t));for(const fn of ['light','glow','cam'])assert.deepEqual(n.shot[fn](t),o.shot[fn](t));o.shot.emit({},t);if(f>=5)assert.deepEqual(globalThis.__s08First27Flames.new.at(-1),globalThis.__s08First27Flames.old.at(-1));}
 else{const asset=f<25?'023':'025';assert.equal(L.filter(a=>a.img.source?.includes('table_box')).length,1);assert.equal(L[4].img.source,`F${asset}_table_box_original_pixels.png`);assert.deepEqual(L[4].contact,C.TABLE_BOX_CONTACT);assert.equal(L[5].img.source,`F${asset}_forearms_elbows_original_pixels.png`);const A=C.fireAt(t),light=n.shot.light(t);assert.equal(light.lights[0].x,A.head[0]);assert.equal(light.lights[0].y,A.head[1]-14);assert.deepEqual(globalThis.__s08First27Flames.new.at(-1)[0],[A.head[0],A.head[1]+2]);}
}
// Exercise high→mid→high cache order without rasterization.
const highBefore=(await n.shot.layers(0))[0],mid1=n.__testLampLayerAtLift(.5),mid2=n.__testLampLayerAtLift(.5),highAfter=(await n.shot.layers(0))[0];
assert.equal(mid1,mid2);assert.equal(highBefore,highAfter);assert.notEqual(mid1,highBefore);
assert.deepEqual(mid1.img.ops.filter(x=>x[0]==='rotate'),[['rotate',-.6]]);
assert.deepEqual(highAfter,(await o.shot.layers(0))[0]);
// Geometry of the already-approved midpoint is tested against the unchanged fixed lamp helper.
const geometry=[];for(const lift of [0,.5]){const cv=new CanvasRecorder(1920,1080),r=lamp.lamp(cv.getContext(),lift,false),world=([x,y])=>[C.LAMP_BASE[0]-(x-lamp.LX)*C.LAMP_SCALE,C.LAMP_BASE[1]+(y-lamp.LB)*C.LAMP_SCALE];geometry.push({lift,angle:cv.ops.find(v=>v[0]==='rotate')[1],lever:world(r.lever),globeTop:world(r.globeTop)});}
assert.ok(Math.abs(geometry[0].lever[0]-1254.0390495120525)<1e-9);assert.ok(Math.abs(geometry[0].lever[1]-737.5349762791033)<1e-9);assert.ok(Math.abs(geometry[1].lever[0]-1242.1515476848717)<1e-9);assert.ok(Math.abs(geometry[1].lever[1]-750.9527302910597)<1e-9);assert.ok(Math.abs(geometry[0].globeTop[1]-geometry[1].globeTop[1]-41.62162162162162)<1e-9);
for(const method of ['layers','light','glow','emit','cam']){if(method==='layers')await assert.rejects(()=>n.shot.layers(C.DURATION),RangeError);else if(method==='emit')assert.throws(()=>n.shot.emit({},C.DURATION),RangeError);else assert.throws(()=>n.shot[method](C.DURATION),RangeError);}await assert.rejects(()=>n.renderFrame({},C.DURATION,1920,1080),RangeError);
const originalBlock=s=>s.slice(s.indexOf('async function bg()'),s.indexOf('const layerCache='));assert.equal(originalBlock(source),originalBlock(previous));const lighting=s=>s.slice(s.indexOf(' light:(t)=>{'),s.indexOf('export async function renderFrame'));assert.equal(lighting(source),lighting(previous));
const result={status:'PASS_STATIC_AND_MOCK_ONLY_NOT_CANVAS',planned_frames:27,approved_available_frames:C.FRAME_COUNT,first23_contract_samples_exact:92,first23_draw_commands_layers_and_lighting_identical:true,old_image_files_byte_equal:18,verified_layer_sha256:count,F023_frames:[23,24],F023_match_head:[1070,791],F023_match_grip:[1042,828],single_independent_code_lamp_behind_original_grip:true,no_extra_knob_or_reference_rod_layer:true,table_box_draws_per_frame:1,source_scene_blocks_and_light_functions_byte_equal:true,mechanical_geometry:geometry,F025_drawing_adopted:expectedAvailable===27,F025_frames:[25,26],F025_match_head:[1076,794],F025_match_grip:[1048,831],first_rejected_frame:C.FRAME_COUNT,all_public_frame_entry_points_reject_unapproved:true,midpoint_cache_verified:true,high_mid_high_cache_order_preserves_old_frame0:true,actual_canvas_frames:0};
fs.writeFileSync(new URL('TEST_RESULT.json',local),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
