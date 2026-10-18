// Structural mock comparison only. No pixels are rendered and this is not Canvas evidence.
import fs from 'node:fs';import assert from 'node:assert/strict';import path from 'node:path';import {pathToFileURL} from 'node:url';
import {fireAt,FRAME_COUNT,DURATION,TABLE_BOX_CONTACT} from './contract.js';
const base=process.argv[2]?pathToFileURL(path.resolve(process.argv[2])+'/'):new URL('../20261018_1721_s08_first14_scene/',import.meta.url);
const stores={};globalThis.__s08First20Tests=stores;
class FakeCanvas{constructor(w,h){this.width=w;this.height=h;this.ops=[];}getContext(){const ops=this.ops;return new Proxy({}, {get:(o,k)=>k==='createRadialGradient'?(...a)=>{ops.push([k,...a]);return{addColorStop(...v){ops.push(['addColorStop',...v]);}};}:(...a)=>ops.push([k,...a]),set:(o,k,v)=>{ops.push(['set',k,v]);return true;}});}}
globalThis.OffscreenCanvas=FakeCanvas;
async function fixture(file,key){
 stores[key]={lamp:[],flame:[],paint:[],loads:[]};
 let code=fs.readFileSync(file,'utf8');
 code=code.replace("import {renderPaint,loadImg} from '/js/paint/paintshot.js';",`const calls=globalThis.__s08First20Tests[${JSON.stringify(key)}]; const renderPaint=async(...a)=>calls.paint.push(a); const loadImg=async path=>{calls.loads.push(path);return {width:1920,height:1080,source:path.split('/').pop()};};`);
 code=code.replace("import {lamp as drawLamp,flameShape,LX,LB} from '/js/code/s08.js';",'const LX=1120,LB=950; const drawLamp=(x,...a)=>calls.lamp.push(a); const flameShape=(x,...a)=>calls.flame.push(a);');
 for(const f of ['contract.js','layer_contract.js'])code=code.replace("'./"+f+"'",JSON.stringify(new URL('./'+f,file).href));
 code=code.replace("new URL('./frames/'+meta.filename,import.meta.url).href", "'original-pixel-frame/'+meta.filename");
 return import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
}
const mod=await fixture(new URL('./s08_first20_scene.js',import.meta.url),'new');
const old=await fixture(new URL('s08_first14_scene.js',base),'old');
assert.equal(mod.FRAME_COUNT,FRAME_COUNT);assert.equal(mod.DURATION,DURATION);
for(let f=0;f<20;f++){
 const t=f/24,A=fireAt(t),ls=await mod.shot.layers(t);assert.equal(ls.length,f>=17?6:5);
 for(const L of ls){assert.equal(L.x,0);assert.equal(L.y,0);assert.equal(L.sc,1);}
 const box=ls.filter(L=>L.img.source?.includes('table_box'));
 assert.equal(box.length,f>=17?1:0);
 assert.equal(ls.filter(L=>L.contact).length,f>=17?1:0);
 if(f>=17){assert.equal(ls[4],box[0]);assert.deepEqual(box[0].contact,TABLE_BOX_CONTACT);assert.match(ls[5].img.source,/forearms_elbows/);}
 assert.deepEqual(mod.shot.cam(t),{x:960,y:540,fit:1});
 assert.equal(mod.shot.light(t).lights.length,f>=5?1:0);assert.equal(mod.shot.glow(t).length,f>=5?1:0);
 const before=stores.new.flame.length;mod.shot.emit({},t);assert.equal(stores.new.flame.length-before,f>=5?1:0);
 if(A.lit){const l=mod.shot.light(t).lights[0];assert.equal(l.x,1074);assert.equal(l.y,768);assert.deepEqual(stores.new.flame.at(-1)[0],[1074,784]);}
 if(f<14){assert.deepEqual(ls,await old.shot.layers(t));for(const name of ['light','glow','cam'])assert.deepEqual(mod.shot[name](t),old.shot[name](t));old.shot.emit({},t);if(A.lit)assert.deepEqual(stores.new.flame.at(-1),stores.old.flame.at(-1));}
}
assert.deepEqual(stores.new.lamp,[[0,false]]);assert.deepEqual(stores.old.lamp,[[0,false]]);
await mod.renderFrame({},0,1920,1080);await old.renderFrame({},0,1920,1080);
assert.deepEqual(stores.new.paint.at(-1)[4].bg,stores.old.paint.at(-1)[4].bg);
for(const method of ['layers','light','glow','emit','cam']){
 if(method==='layers')await assert.rejects(()=>mod.shot.layers(20/24),RangeError);
 else if(method==='emit')assert.throws(()=>mod.shot.emit({},20/24),RangeError);
 else assert.throws(()=>mod.shot[method](20/24),RangeError);
}
await assert.rejects(()=>mod.renderFrame({},20/24,1920,1080),RangeError);
const result={status:'PASS_MOCK_WIRING_ONLY_NOT_CANVAS',frames_checked:20,first14_mock_layer_draw_commands_and_lighting_identical:true,background_draw_commands_identical:true,loaded_original_pixel_layers:15,lamp_calls:stores.new.lamp,first14_contacts:0,F014_table_box_draws:0,F017_table_box_draws_per_frame:1,F017_contact_attached_to_box:true,F017_order:['lamp','stool','body','table_front','table_box_with_attached_contact','arms'],original_pixel_transforms:'all x0 y0 sc1',all_public_frame_entry_points_reject_020:true,canvas_render_performed:false};
fs.writeFileSync(new URL('./MODULE_WIRING_TEST.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
