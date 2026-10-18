// Diagnostic controls only: same fixed runtime, temporarily omit box contact in memory.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('playwright');const {start}=require(path.resolve('tools/js/serve.cjs'));
const P=path.resolve(__dirname,'..');
(async()=>{const srv=await start(0);let browser;
 try{
  browser=await chromium.launch();const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready===true||window.__error,null,{timeout:60000});assert.equal(await page.evaluate(()=>window.__error),undefined);
  const contract=await page.evaluate(async()=>{const c=await import('/collab/reviews/20261018_1828_s08_first23_scene/contract.js');let rejected=false;try{c.frameAt(23/24);}catch(e){rejected=e instanceof RangeError;}return{count:c.FRAME_COUNT,duration:c.DURATION,missing23_guard_rejected:rejected,frame23_render_called:false,states:Array.from({length:23},(_,f)=>({frame:f,pose:c.poseAt(f/24),fire:c.fireAt(f/24)}))};});
  assert.equal(contract.count,23);assert.equal(contract.missing23_guard_rejected,true);
  fs.mkdirSync(path.join(P,'diagnostic'),{recursive:true});
  for(const f of[20,22]){
   const data=await page.evaluate(async f=>{const mod=await import('/collab/reviews/20261018_1828_s08_first23_scene/s08_first23_scene.js');const old=mod.shot.layers;await window.renderFrame(f/24);const adopted=document.getElementById('c').toDataURL('image/png');const layers=await old(f/24);const contacts=layers.filter(l=>l.contact).map(l=>l.contact);mod.shot.layers=async t=>(await old(t)).map(l=>l.contact?{...l,contact:undefined}:l);try{await window.renderFrame(f/24);return{adopted,without:document.getElementById('c').toDataURL('image/png'),contacts};}finally{mod.shot.layers=old;}},f);
   const actual=Buffer.from(data.adopted.split(',')[1],'base64');assert(actual.equals(fs.readFileSync(path.resolve(`build/S08_first23/${String(f).padStart(5,'0')}.png`))));
   assert.equal(data.contacts.length,1);assert.equal(data.contacts[0].base,970);
   fs.writeFileSync(path.join(P,`diagnostic/F${String(f).padStart(3,'0')}_without_box_contact_ACTUAL_CONTROL.png`),Buffer.from(data.without.split(',')[1],'base64'));
  }
  assert.equal(errors.length,0);fs.writeFileSync(path.join(P,'contract_and_diagnostic_runtime.json'),JSON.stringify({fixed_commit:'d6071b76c8b069c7112134320a69058b896ff1f5',status:'PASS_FIXED_ACTUAL_CONTACT_CONTROLS_AND_RANGE_GUARD',page_errors:errors,adopted20_22_rerenders_byte_equal_main23:true,diagnostic_contact_omission_only:'in-memory shot.layers;no file/source changes',...contract},null,2)+'\n');
  console.log('PASS adopted20/22 diagnostic rerenders byte-equal main23;one box contact base970;no source edits;23pure guard rejects;no023 render');
 }finally{if(browser)await browser.close();srv.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
