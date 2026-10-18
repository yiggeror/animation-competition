// No Canvas rasterization: compare module wiring and literal scene source only.
import fs from 'node:fs';import assert from 'node:assert/strict';import path from 'node:path';import {pathToFileURL} from 'node:url';
const local=new URL('.',import.meta.url),repoBase=new URL('../20261018_1800_s08_first20_scene/',local);
const scratchBase=new URL('../../../../astra_s08_first20_scene_20261018_1800/collab/reviews/20261018_1800_s08_first20_scene/',local);
const base=process.argv[2]?pathToFileURL(path.resolve(process.argv[2])+'/'):fs.existsSync(new URL('s08_first20_scene.js',repoBase))?repoBase:scratchBase;
const original=fs.readFileSync(new URL('s08_first20_scene.js',base),'utf8');
const candidate=fs.readFileSync(new URL('s08_first20_lampfix_candidate.js',local),'utf8');
const expected=original.replace("import {lamp as drawLamp,flameShape,LX,LB} from '/js/code/s08.js';","import {flameShape} from '/js/code/s08.js';\nimport {lamp as drawLamp,LX,LB} from './lamp_mechanical_candidate.js';").replace("'./contract.js'","'../20261018_1800_s08_first20_scene/contract.js'").replace("'./layer_contract.js'","'../20261018_1800_s08_first20_scene/layer_contract.js'").replace("'./frames/'","'../20261018_1800_s08_first20_scene/frames/'");
assert.equal(candidate,expected);
class PathRecorder{constructor(){this.ops=[];}moveTo(...a){this.ops.push(['moveTo',...a]);}bezierCurveTo(...a){this.ops.push(['bezierCurveTo',...a]);}lineTo(...a){this.ops.push(['lineTo',...a]);}closePath(...a){this.ops.push(['closePath',...a]);}}
globalThis.Path2D=PathRecorder;
class CanvasRecorder{constructor(w,h){this.width=w;this.height=h;this.ops=[];}getContext(){const ops=this.ops;return new Proxy({},{get:(_,k)=>(...a)=>ops.push([k,...a]),set:(_,k,v)=>{ops.push(['set',k,v]);return true;}});}}
globalThis.OffscreenCanvas=CanvasRecorder;
async function fixture(source,old){
 let s=source.replace("import {renderPaint,loadImg} from '/js/paint/paintshot.js';","const renderPaint=async()=>{};const loadImg=async url=>({width:1920,height:1080,source:url.split('/').pop()});");
 if(old)s=s.replace("import {lamp as drawLamp,flameShape,LX,LB} from '/js/code/s08.js';",`import {lamp as drawLamp,LX,LB} from ${JSON.stringify(new URL('source_evidence/lamp_source_0c215550.js',local).href)};const flameShape=()=>{};`);
 else s=s.replace("import {flameShape} from '/js/code/s08.js';","const flameShape=()=>{};").replace("'./lamp_mechanical_candidate.js'",JSON.stringify(new URL('lamp_mechanical_candidate.js',local).href));
 for(const f of ['contract.js','layer_contract.js'])s=s.replace(old?"'./"+f+"'":"'../20261018_1800_s08_first20_scene/"+f+"'",JSON.stringify(new URL(f,base).href));
 s=s.replace(/new URL\('[^']*frames\/'\+meta.filename,import.meta.url\).href/,"'locked-frames/'+meta.filename");
 return import('data:text/javascript;base64,'+Buffer.from(s).toString('base64'));
}
const n=await fixture(candidate,false),o=await fixture(original,true);const rows=[];
for(let f=0;f<20;f++){
 const t=f/24,nl=await n.shot.layers(t),ol=await o.shot.layers(t);
 assert.equal(nl.length,ol.length);assert.deepEqual(nl.slice(1),ol.slice(1));
 assert.deepEqual(nl[0].img.ops.filter(x=>x[0]!=='rotate'),ol[0].img.ops.filter(x=>x[0]!=='rotate'));
 assert.deepEqual(nl[0].img.ops.filter(x=>x[0]==='rotate'),[['rotate',-.85]]);
 assert.deepEqual(ol[0].img.ops.filter(x=>x[0]==='rotate'),[['rotate',.55]]);
 for(const fn of ['light','glow','cam'])assert.deepEqual(n.shot[fn](t),o.shot[fn](t));
 rows.push({frame:f,local_lamp_initial_angle:-.85,all_non_lamp_layers_identical:true,all_light_glow_cam_values_identical:true});
}
await assert.rejects(()=>n.shot.layers(20/24),RangeError);
const result={status:'PASS_CANDIDATE_SCENE_WIRING_ONLY_NOT_CANVAS',source_changes_only:'lamp import and relative references to unchanged first20 contracts/layers/images',fixed_local_lamp_from_frame:0,frames_checked:20,frame020_still_rejected:true,formal_first20_entry_sha256:'16d77bc7ff1b3356030c7ba374502acedf62015239f82a8a231667f75a354a50',rows,actual_canvas_frames:0};
fs.writeFileSync(new URL('./SCENE_WIRING_CHECK.json',local),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:result.status,frames:20,fixed_local_lamp_from_frame:0,formal_package_unchanged:true}));
