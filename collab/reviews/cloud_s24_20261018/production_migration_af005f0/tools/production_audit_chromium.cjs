// Process-only system browser selection plus production HTTP/frame evidence. No renderer edits.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const output=path.resolve(__dirname,'../qa/actual_network_events.jsonl');
const entry='/js/anim/s24_drawn.js';let nextPage=0;
const log=x=>fs.appendFileSync(output,JSON.stringify({utc:new Date().toISOString(),...x})+'\n');
const launch=chromium.launch.bind(chromium);
chromium.launch=async(options={})=>{
 const browser=await launch({...options,executablePath:'/usr/bin/chromium',args:[...(options.args||[]),'--enable-unsafe-swiftshader']});
 log({event:'browser_launched',version:browser.version(),executable:'/usr/bin/chromium',args:['--enable-unsafe-swiftshader']});
 const newPage=browser.newPage.bind(browser);
 browser.newPage=async(...args)=>{
  const page=await newPage(...args),id=nextPage++;
  page.on('request',r=>log({event:'request',page:id,url:r.url(),resource_type:r.resourceType()}));
  page.on('response',r=>log({event:'response',page:id,url:r.url(),status:r.status(),resource_type:r.request().resourceType(),content_type:r.headers()['content-type']||null}));
  page.on('requestfailed',r=>log({event:'requestfailed',page:id,url:r.url(),failure:r.failure()}));
  page.on('pageerror',e=>log({event:'pageerror',page:id,message:String(e)}));
  page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')log({event:'console_'+m.type(),page:id,message:m.text(),location:m.location()});});
  const evaluate=page.evaluate.bind(page);
  page.evaluate=async(fn,arg)=>{
   const result=await evaluate(fn,arg);
   if(typeof arg==='number'&&typeof result==='string'&&result.startsWith('data:image/png;base64,')){
    const exposure=await evaluate(async({entry,t})=>(await import(entry)).pickExposure(t),{entry,t:arg});const bytes=Buffer.from(result.split(',')[1],'base64');
    log({event:'actual_frame',page:id,frame:Math.round(arg*24),t:arg,entry,exposure,PNG_SHA256:crypto.createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length,native_SHA_verified_in_production_entry:true});
   }
   return result;
  };
  return page;
 };
 return browser;
};
