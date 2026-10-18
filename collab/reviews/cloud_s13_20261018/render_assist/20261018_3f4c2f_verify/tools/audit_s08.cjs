// Read-only recheck of the singleF000 Canvas result, resources and existing table mask.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execFileSync}=require('child_process');
const {chromium}=require('playwright');
const root=path.resolve(process.argv[2]||'/tmp/s13_render_assist_3f4c2f'),out=path.resolve(__dirname,'..');
const commit='3f4c2f187daaeacc6b26e26260e426823f2fa6ad',mod='collab/reviews/20261018_1606_s08_f000_scene/s08_f000_scene.js';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const git=(...args)=>execFileSync('git',args,{cwd:root,encoding:'utf8'}).trim();
if(git('rev-parse','HEAD')!==commit||git('status','--porcelain','-uno'))throw Error('Wrong or changed fixed checkout');
const {start}=require(path.join(root,'tools/js/serve.cjs'));
(async()=>{
 const srv=await start(0),b=await chromium.launch({executablePath:'/usr/bin/chromium'}),p=await b.newPage();
 const resources=[],errors=[];const onResponse=r=>resources.push({path:new URL(r.url()).pathname,status:r.status()});p.on('response',onResponse);p.on('pageerror',e=>errors.push(String(e)));
 await p.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=${mod}&w=1920&h=1080`);await p.waitForFunction(()=>window.__ready||window.__error);
 const result=await p.evaluate(async mod=>{
  if(window.__error)throw Error(window.__error);await window.renderFrame(0);const data=document.getElementById('c').toDataURL('image/png');
  const m=await import('/'+mod),c=await import('/collab/reviews/20261018_1606_s08_f000_scene/contract.js'),L=await m.shot.layers(0);
  const a=new OffscreenCanvas(1920,1080),ax=a.getContext('2d');ax.drawImage(L[2].img,0,0);const A=ax.getImageData(0,0,1920,1080).data,F=L[3].img.getContext('2d').getImageData(0,0,1920,1080).data;
  const checks=[];for(const[name,roi]of[['near',[700,940,850,1005]],['far',[1000,940,1130,1005]]]){let count=0,x0=1920,y0=1080,x1=-1,y1=-1;
   for(let y=roi[1];y<roi[3];y++)for(let x=roi[0];x<roi[2];x++){const i=(y*1920+x)*4;if(A[i+3]>=128&&A[i]>A[i+1]+20&&A[i+1]>A[i+2]+10&&F[i+3]>=128){count++;x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y)}}
   checks.push({elbow:name,roi,occluded_skin_pixels:count,occluded_skin_bbox:[x0,y0,x1,y1],method:'diagnostic skin-color heuristic intersected with actual existing foreground table alpha; no image changes'})}
  return{data,art:c.ART,lamp_base:c.LAMP_BASE,table:c.ORIGINAL_TABLE,elbow_mask_checks:checks};
 },mod);
 p.off('response',onResponse);const required=[...new Set(resources.filter(r=>r.path!='/favicon.ico').map(r=>r.path))];
 const bodies=await p.evaluate(async paths=>Promise.all(paths.map(async path=>{const r=await fetch(path,{cache:'no-store'}),a=await r.arrayBuffer(),h=await crypto.subtle.digest('SHA-256',a);return{path,status:r.status,bytes:a.byteLength,sha256:Array.from(new Uint8Array(h),x=>x.toString(16).padStart(2,'0')).join('')}})),required);
 for(const row of bodies){const disk=path.join(root,row.path),rel=path.relative(root,disk);row.disk_sha256=sha(fs.readFileSync(disk));row.matches_fixed_disk=row.sha256===row.disk_sha256;row.git_blob=git('rev-parse',commit+':'+rel);row.disk_git_blob=git('hash-object',disk)}
 const bytes=Buffer.from(result.data.split(',')[1],'base64');delete result.data;
 const snap=fs.readFileSync(path.join(out,'S08/S08_F000_actual_1920x1080.png'));result.snap_vs_independent_probe_byte_identical=bytes.equals(snap);result.actual_png_sha256=sha(snap);
 result.fixed_commit=commit;result.module=mod;result.resources=resources;result.browser_native_fetch_body_audit=bodies;result.page_errors=errors;result.chromium=b.version();
 result.actual_snap_command=['node','--require','/workspace/animation-competition/collab/reviews/cloud_s13_20261018/full_scene/tools/use_system_chromium.cjs','tools/js/snap.cjs','/'+mod,'/tmp/S08_F000.png','1920','1080','0'];
 result.snap_stdout=['[page] Failed to load resource: the server responded with a status of 404 (Not Found)','/tmp/S08_F000.png'];
 await b.close();await new Promise(r=>srv.close(r));
 if(errors.length||!result.snap_vs_independent_probe_byte_identical||resources.some(r=>r.path!='/favicon.ico'&&r.status!==200)||bodies.some(r=>r.status!==200||!r.matches_fixed_disk||r.git_blob!==r.disk_git_blob))throw Error(JSON.stringify(result));
 fs.writeFileSync(path.join(out,'S08/render_resource_and_elbow_checks.json'),JSON.stringify(result,null,2)+'\n');
 console.log('PASS actual snap/probe PNG byte-identical; fixed c803; unmodified y981table clips both elbow tips; resource SHA checks pass.');
})().catch(e=>{console.error(e);process.exit(1)});
