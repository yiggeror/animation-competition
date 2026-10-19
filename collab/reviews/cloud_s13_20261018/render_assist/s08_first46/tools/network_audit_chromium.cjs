// Actual new043-045 audit only. Browser selection matches the first run; no scene changes.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=path.resolve(__dirname,'../actual_network_events.jsonl');let nextPage=0;
const log=x=>fs.appendFileSync(out,JSON.stringify({utc:new Date().toISOString(),...x})+'\n');
const launch=chromium.launch.bind(chromium);
chromium.launch=async(opts={})=>{
 const browser=await launch({...opts,executablePath:'/usr/bin/chromium'});log({event:'browser_launched',version:browser.version(),executable:'/usr/bin/chromium'});
 const newPage=browser.newPage.bind(browser);
 browser.newPage=async(...args)=>{
  const page=await newPage(...args),id=nextPage++;
  page.on('response',r=>log({event:'response',page:id,url:r.url(),status:r.status(),resource_type:r.request().resourceType(),content_type:r.headers()['content-type']||null}));
  page.on('requestfailed',r=>log({event:'requestfailed',page:id,url:r.url(),failure:r.failure()}));
  page.on('pageerror',e=>log({event:'pageerror',page:id,message:String(e)}));
  page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')log({event:'console_'+m.type(),page:id,message:m.text(),location:m.location()});});
  const evaluate=page.evaluate.bind(page);
  page.evaluate=async(fn,arg)=>{
   const result=await evaluate(fn,arg);
   if(typeof arg==='number'&&typeof result==='string'&&result.startsWith('data:image/png;base64,')){
    const bytes=Buffer.from(result.split(',')[1],'base64');log({event:'actual_frame',page:id,frame:Math.round(arg*24),t:arg,PNG_SHA256:crypto.createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length});
   }
   return result;
  };
  return page;
 };
 return browser;
};
