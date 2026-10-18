import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import * as C from './contract.js';
import {LAYER_ARTS} from './layer_contract.js';
const base=process.argv[2]?pathToFileURL(path.resolve(process.argv[2])+'/'):new URL('../20261018_1721_s08_first14_scene/',import.meta.url);
const old=await import(new URL('contract.js',base));
assert.equal(C.WIDTH,1920);assert.equal(C.HEIGHT,1080);assert.equal(C.FPS,24);
assert.equal(C.FRAME_COUNT,20);assert.equal(C.DURATION,20/24);
assert.deepEqual(C.EXPOSE.slice(0,6),old.EXPOSE);
assert.deepEqual(C.EXPOSE.slice(6),[{start:14,hold:3,asset:'014'},{start:17,hold:3,asset:'017'}]);
for(const k of ['LAMP_BASE','LAMP_SCALE','ORIGINAL_TABLE','LAMP_WICK'])assert.deepEqual(C[k],old[k]);
for(const k of Object.keys(old.CONTACTS))assert.deepEqual(C.CONTACTS[k],old.CONTACTS[k]);
const expected=['000','000','000','003','003','005','006','006','006','009','009','009','005','005','014','014','014','017','017','017'];
for(let f=0;f<20;f++)for(const sub of [0,.25,.5,.999]){
 const t=(f+sub)/24,p=C.poseAt(t),A=C.fireAt(t);assert.equal(C.frameAt(t),f);assert.equal(p.asset,expected[f]);
 assert.equal(A.lit,f>=5);assert.equal(A.wick,0);assert.equal(A.lift,0);assert.deepEqual(A.head,C.CONTACTS[p.asset].head);
 assert.equal(p.touching,f===3||f===4);
 if(f<14){assert.deepEqual(p,old.poseAt(t));assert.deepEqual(A,old.fireAt(t));}
}
for(const t of [-1,NaN,Infinity,20/24,1,6])for(const fn of [C.frameAt,C.poseAt,C.fireAt])assert.throws(()=>fn(t),RangeError);
assert.equal(C.poseAt(19.999/24).asset,'017');
assert.deepEqual(C.TABLE_BOX_CONTACT,{base:970,a:.22,blur:.65,sy:-.055,dx:0,dy:0});
let count=0;
for(const [asset,roles] of Object.entries(LAYER_ARTS))for(const a of Object.values(roles)){
 const p=new URL('./frames/'+a.filename,import.meta.url),bytes=fs.readFileSync(p);
 assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),a.sha256);
 assert.equal(bytes.readUInt32BE(16),1920);assert.equal(bytes.readUInt32BE(20),1080);count++;
 if(Number(asset)<14)assert.ok(bytes.equals(fs.readFileSync(new URL('frames/'+a.filename,base))));
}
assert.equal(count,15);assert.equal(LAYER_ARTS['014'].table_box,undefined);assert.ok(LAYER_ARTS['017'].table_box);
const source=fs.readFileSync(new URL('./s08_first20_scene.js',import.meta.url),'utf8');
const prior=fs.readFileSync(new URL('s08_first14_scene.js',base),'utf8');
const block=s=>s.slice(s.indexOf('async function bg()'),s.indexOf('const layerCache='));
assert.equal(block(source),block(prior));
const light=s=>s.slice(s.indexOf(' light:(t)=>{'),s.indexOf('export async function renderFrame'));
assert.equal(light(source),light(prior));
const result={status:'PASS_STATIC_CONTRACT_ONLY',frames:20,fps:24,duration:20/24,first14_contract_samples_byte_equivalent:56,old_image_files_byte_equal:10,all_layer_sha256_verified:15,original_room_table_lamp_stool_functions_byte_equal:true,original_light_glow_emit_camera_functions_byte_equal:true,scene_function_block_sha256:crypto.createHash('sha256').update(block(source)).digest('hex'),frame020_and_later_rejected:true,first_match_flame_frame:5,wick_flame_frames:0,lamp_lift_frames:0,box_contact_actual_canvas:'PENDING',actual_canvas_render_performed:false};
fs.writeFileSync(new URL('./TEST_RESULT.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
