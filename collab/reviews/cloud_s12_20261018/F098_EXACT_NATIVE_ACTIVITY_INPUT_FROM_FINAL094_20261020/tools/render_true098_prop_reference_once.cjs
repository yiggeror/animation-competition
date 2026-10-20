// Code-PROP reference only. No person, full094 actual Canvas, or imagegen.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const {start}=require('../../../../../tools/js/serve.cjs');
const O=path.resolve(__dirname,'..'),out=path.join(O,'code_props/F098_TRUE_CRANE_AND_TWO_PHYSICALLY_RIGID_RODS_REFERENCE.png');
if(fs.existsSync(out))throw Error('True prop reference exists; do not redraw automatically.');
const plan=JSON.parse(fs.readFileSync(path.join(O,'geometry/F098_NATIVE_ACTIVITY_AND_TRUE_PROP_PLAN.json'),'utf8'));
fs.writeFileSync(path.join(O,'code_props/prop_reference098.html'),'<!doctype html><meta charset="utf-8"><title>True098 code prop reference only</title>');
(async()=>{const server=await start(0),browser=await chromium.launch({executablePath:'/usr/bin/chromium'});try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>errors.push(r.url()));
 await page.goto(`http://127.0.0.1:${server.address().port}/collab/reviews/cloud_s12_20261018/F098_EXACT_NATIVE_ACTIVITY_INPUT_FROM_FINAL098_20261020/code_props/prop_reference098.html`);
 const result=await page.evaluate(async cfg=>{
  const {makeCrane}=await import('/js/lamp/crane.js');const {drawPuppet,solve,pointOn}=await import('/js/puppet.js');
  const p=cfg.prop_plan,pup=makeCrane(1.35,'plain'),sol=solve(pup,p.code_pose),basis=p.paper_3D_camera_basis,K=p.mm_to_scene_scale,root=p.root_scene;
  const project=q=>[root[0]+K*(basis[0][0]*q[0]+basis[0][1]*q[1]),root[1]+K*(basis[1][0]*q[0]+basis[1][1]*q[1])];
  const locals={R:pointOn(pup,sol,'body',[-75,6]),L:pointOn(pup,sol,'neck3',[10,0])},hinges={R:project(locals.R),L:project(locals.L)};
  for(const role of ['R','L'])if(Math.hypot(...hinges[role].map((v,i)=>v-p.rods[role].hinge_scene[i]))>1e-7)throw Error('Real code hinge differs from planned '+role);
  const crane=new OffscreenCanvas(1920,1080),c=crane.getContext('2d');
  c.transform(K*basis[0][0],K*basis[1][0],K*basis[0][1],K*basis[1][1],root[0],root[1]);drawPuppet(c,pup,p.code_pose,'r');
  const rods=new OffscreenCanvas(1920,1080),r=rods.getContext('2d');
  for(const role of ['R','L']){const a=p.rods[role].free_scene,b=hinges[role];r.lineCap='round';for(const [color,width]of[['#3e2a1e',7],['#c99a52',3]]){r.strokeStyle=color;r.lineWidth=width;r.beginPath();r.moveTo(...a);r.lineTo(...b);r.stroke();}}
  const together=new OffscreenCanvas(1920,1080),x=together.getContext('2d');x.drawImage(crane,0,0);x.drawImage(rods,0,0);
  const encode=async c=>{const b=await c.convertToBlob({type:'image/png'}),bytes=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<bytes.length;i+=8192)s+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(s);};
  return {local_points_from_actual_makeCrane:locals,hinges_scene:hinges,code_pose:p.code_pose,crane:await encode(crane),rods:await encode(rods),combined:await encode(together),true_crane_draws:1,rod_reference_draws:1,person_draws:0,actual098_full_Canvas:0};
 },plan);
 const files={crane:'F098_TRUE_CRANE_ONLY_REFERENCE.png',rods:'F098_TRUE_TWO_RODS_ONLY_REFERENCE.png',combined:path.basename(out)};
 const hashes={};for(const[key,file]of Object.entries(files)){const bytes=Buffer.from(result[key],'base64');fs.writeFileSync(path.join(O,'code_props',file),bytes);hashes[file]=crypto.createHash('sha256').update(bytes).digest('hex');delete result[key];}
 result.SHA256=hashes;result.browser_errors=errors;result.status='ACTUAL_CODE_PROP_REFERENCE_ONLY_NOT_NEW_PERSON_DRAWING';fs.writeFileSync(path.join(O,'qa/TRUE_PROP_REFERENCE_READBACK.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{await browser.close();server.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
