// Diagnostic controls only: same fixed runtime, temporarily omit box contact in memory.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('playwright');const {start}=require(path.resolve('tools/js/serve.cjs'));
const P=path.resolve(__dirname,'..');
(async()=>{const srv=await start(0);let browser;
 try{
  browser=await chromium.launch();const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://127.0.0.1:${srv.address().port}/dev/view.html?mod=collab/reviews/20261018_1800_s08_first20_scene/s08_first20_scene.js&w=1920&h=1080`);
  await page.waitForFunction(()=>window.__ready===true||window.__error,null,{timeout:60000});assert.equal(await page.evaluate(()=>window.__error),undefined);
  const contract=await page.evaluate(async()=>{const c=await import('/collab/reviews/20261018_1800_s08_first20_scene/contract.js');let rejected=false;try{c.frameAt(20/24);}catch(e){rejected=e instanceof RangeError;}return{count:c.FRAME_COUNT,duration:c.DURATION,missing20_guard_rejected:rejected,frame20_render_called:false,states:Array.from({length:20},(_,f)=>({frame:f,pose:c.poseAt(f/24),fire:c.fireAt(f/24)}))};});
  assert.equal(contract.count,20);assert.equal(contract.missing20_guard_rejected,true);
  fs.mkdirSync(path.join(P,'diagnostic'),{recursive:true});
  for(const f of[17,19]){
   const data=await page.evaluate(async f=>{const mod=await import('/collab/reviews/20261018_1800_s08_first20_scene/s08_first20_scene.js');const old=mod.shot.layers;await window.renderFrame(f/24);const adopted=document.getElementById('c').toDataURL('image/png');const layers=await old(f/24);const contacts=layers.filter(l=>l.contact).map(l=>l.contact);mod.shot.layers=async t=>(await old(t)).map(l=>l.contact?{...l,contact:undefined}:l);try{await window.renderFrame(f/24);return{adopted,without:document.getElementById('c').toDataURL('image/png'),contacts};}finally{mod.shot.layers=old;}},f);
   const actual=Buffer.from(data.adopted.split(',')[1],'base64');assert(actual.equals(fs.readFileSync(path.resolve(`build/S08_first20/${String(f).padStart(5,'0')}.png`))));
   assert.equal(data.contacts.length,1);assert.equal(data.contacts[0].base,970);
   fs.writeFileSync(path.join(P,`diagnostic/F${String(f).padStart(3,'0')}_without_box_contact_ACTUAL_CONTROL.png`),Buffer.from(data.without.split(',')[1],'base64'));
  }
  assert.equal(errors.length,0);fs.writeFileSync(path.join(P,'contract_and_diagnostic_runtime.json'),JSON.stringify({fixed_commit:'6f73473a8230ed7a1b236f32605e622769d29109',status:'PASS_FIXED_ACTUAL_CONTACT_CONTROLS_AND_RANGE_GUARD',page_errors:errors,adopted17_19_rerenders_byte_equal_main20:true,diagnostic_contact_omission_only:'in-memory shot.layers;no file/source changes',...contract},null,2)+'\n');
  console.log('PASS adopted17/19 diagnostic rerenders byte-equal main20;one box contact base970;no source edits;20pure guard rejects;no020 render');
 }finally{if(browser)await browser.close();srv.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
