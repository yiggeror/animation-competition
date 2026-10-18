const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=process.cwd(),{start}=require(path.join(ROOT,'tools/js/serve.cjs'));
(async()=>{const server=await start(0);const browser=await chromium.launch({executablePath:'/usr/bin/chromium'});try{
 const page=await browser.newPage();await page.goto(`http://127.0.0.1:${server.address().port}/package.json`);
 const paths=['body_behind','forearms_elbows','table_box'].map(role=>`collab/reviews/20261018_2034_s08_first36_scene/frames/F033_${role}_original_pixels.png`);
 const rows=await page.evaluate(async paths=>{const rows=[];for(const path of paths){const response=await fetch('/'+path,{cache:'no-store'});const bytes=await response.arrayBuffer();const sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');rows.push({path,status:response.status,bytes:bytes.byteLength,sha256});}return rows;},paths);
 for(const r of rows){const bytes=fs.readFileSync(path.join(ROOT,r.path));if(r.status!==200||r.bytes!==bytes.length||r.sha256!==crypto.createHash('sha256').update(bytes).digest('hex'))throw new Error('Asset probe mismatch '+r.path);}
 const report={status:'PASS_SEPARATE_READ_ONLY_CHROMIUM_ARRAYBUFFER_SHA_PROBE',actual_render_frames_in_probe:0,rows,note:'The actual render response audit reported200 but Playwright response.body returned0bytes for six PNG responses;those empty-body hashes are not native-file digests. This separate browser fetch+arrayBuffer probe verifies3current frozen files without rerendering;not relabeled as original render responses.'};
 fs.writeFileSync(path.resolve(__dirname,'../qa/independent_browser_asset_sha_probe.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await browser.close();server.close();}})();
