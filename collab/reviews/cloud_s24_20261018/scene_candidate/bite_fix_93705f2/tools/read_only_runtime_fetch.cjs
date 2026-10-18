// Read-only HTTP byte verification in browser; never imports a scene or calls renderFrame.
const {chromium}=require('playwright'),{start}=require('../../../../../../tools/js/serve.cjs');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
(async()=>{
 const root=process.cwd(),out=path.resolve(__dirname,'../qa'),manifest=JSON.parse(fs.readFileSync(path.join(out,'runtime_source_manifest.json'))),native=JSON.parse(fs.readFileSync(path.join(out,'native9_baseline.json'))).rows;
 const rows=[...manifest.runtime_inputs,...native,{path:'collab/reviews/cloud_s24_20261018/scene_candidate/final_lock.json'}].map(r=>({...r,sha256:r.sha256||crypto.createHash('sha256').update(fs.readFileSync(path.join(root,r.path))).digest('hex')}));
 const srv=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium'}),page=await browser.newPage();
 try{
  await page.goto(`http://127.0.0.1:${srv.address().port}/package.json`);
  const results=await page.evaluate(async rows=>{const out=[];for(const row of rows){const response=await fetch('/'+row.path,{cache:'reload'}),bytes=await response.arrayBuffer(),sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');out.push({path:row.path,status:response.status,bytes:bytes.byteLength,sha256,expected:row.sha256,pass:response.ok&&sha256===row.sha256});}return out;},rows);
  fs.writeFileSync(path.join(out,'read_only_runtime_fetch.json'),JSON.stringify({status:results.every(r=>r.pass)?'READ_ONLY_HTTP_ALL_SHA_PASS':'FAIL',browser:browser.version(),renderFrame_calls:0,rows:results},null,2)+'\n');
  if(!results.every(r=>r.pass))throw new Error(JSON.stringify(results.filter(r=>!r.pass)));
  console.log(JSON.stringify({HTTP_SHA_pass:results.length,renderFrame_calls:0}));
 }finally{await browser.close();srv.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
