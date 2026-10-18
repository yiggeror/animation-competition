import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const own=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const root=path.resolve(own,'../../../..');
const {start}=require(path.join(root,'tools/js/serve.cjs'));
const bundle=path.resolve(own,'../d08_d09_final_segment');
const assetIndex=JSON.parse(readFileSync(path.join(bundle,'asset_index.json')));
for(const r of assetIndex.rows)assert.equal(createHash('sha256').update(readFileSync(path.join(bundle,r.asset))).digest('hex'),r.sha256);
const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium'});
try {
 const page=await browser.newPage();
 await page.goto(`http://127.0.0.1:${server.address().port}/package.json`);
 const report=await page.evaluate(async index=>{
  const m=await import('/collab/reviews/cloud_s24_20261018/scene_candidate/s24_drawn.js');
  const check=(yes,note)=>{if(!yes)throw new Error(note);};
  check(m.DURATION===2.5&&m.FRAME_COUNT===60,'duration');
  check(JSON.stringify(m.CAM)===JSON.stringify({pos:[3.15,1.62,1.12],target:[1.8,.62,.98],hfov:46}),'camera');
  check(m.SCENE_CONFIG.exp===.22&&m.SCENE_CONFIG.fog===.5,'scene light');
  const frames=[];
  for(let f=0;f<60;f++) {
   const r=index.rows.find(r=>f>=r.start&&f<=r.end_inclusive),e=m.pickExposure(f/24);
   check(e.start===r.start&&e.hold===r.hold&&e.sha256===r.sha256,'native resource mapping');
   frames.push({frame:f,start:e.start,sha256:e.sha256});
  }
  check(JSON.stringify(m.registrationMatrix(1920,1080))===JSON.stringify([.7,0,0,.7,590,20]),'B registration');
  for(const t of [-1,2.5,Infinity,NaN]) {let rejected=false;try{m.pickExposure(t);}catch(e){rejected=e instanceof RangeError;}check(rejected,'range guard');}
  let rejected=false;try{m.registrationMatrix(1000,1000);}catch(e){rejected=e instanceof RangeError;}check(rejected,'aspect guard');
  const urls=[],nativeFetch=globalThis.fetch;
  globalThis.fetch=(...args)=>{urls.push(String(args[0]));return nativeFetch(...args);};
  let reason='';try{await m.renderFrame(null,0,1920,1080);}catch(e){reason=String(e);}
  check(reason.includes('final dual lock pending'),'tail lock must reject before render');
  check(urls.length===1&&urls[0].endsWith('/final_lock.json'),'no native asset or WebGL invoked');
  return {status:'PREPARATION_BROWSER_IMPORT_AND_STATIC_CONTRACT_PASS_RENDER_BLOCKED_PENDING_TAIL_LOCK',frames:60,drawings:9,all60_native_SHA_mapping:frames,camera:m.CAM,scene:m.SCENE_CONFIG,registration:m.registrationMatrix(1920,1080),actual_Canvas_frames_rendered:0,lock_gate_actually_rejected_before_asset_or_WebGL_load:true,scene_ready:false};
 },assetIndex);
 writeFileSync(path.join(own,'qa/preflight_result.json'),JSON.stringify(report,null,2)+'\n');
 console.log('PASS: real Chromium import;60f native/SHA mapping;original scene+B;actual render rejected before image/WebGL load.');
} finally {await browser.close();server.close();}
