// Process-only browser selection and evidence collection. No scene/renderer edits.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const output=path.resolve(__dirname,'../qa/actual_browser_events.jsonl');
const entry='/collab/reviews/20261018_2034_s08_first36_scene/contract.js';
let nextPage=0;
const log=d=>fs.appendFileSync(output,JSON.stringify({utc:new Date().toISOString(),...d})+'\n');
const launch=chromium.launch.bind(chromium);
chromium.launch=async(options={})=>{
 const browser=await launch({...options,executablePath:'/usr/bin/chromium',args:[...(options.args||[]),'--enable-unsafe-swiftshader']});
 log({event:'browser_launched',version:browser.version(),executable:'/usr/bin/chromium',args:['--enable-unsafe-swiftshader']});
 const newPage=browser.newPage.bind(browser);
 browser.newPage=async(...args)=>{
  const page=await newPage(...args),id=nextPage++,pending=new Set();
  page.on('response',response=>{
   const task=(async()=>{
    const url=new URL(response.url());
    if(url.origin.startsWith('http://127.0.0.1:')){
     const r={event:'resource',page:id,path:decodeURIComponent(url.pathname),status:response.status()};
     if(/\.(js|json|png|cjs)$/.test(url.pathname)&&response.ok()){
      const data=await response.body();r.sha256=crypto.createHash('sha256').update(data).digest('hex');r.bytes=data.length;
     }
     log(r);
    }
   })().catch(e=>log({event:'audit_error',page:id,message:String(e)}));
   pending.add(task);task.finally(()=>pending.delete(task));
  });
  page.on('pageerror',e=>log({event:'pageerror',page:id,message:String(e)}));
  page.on('requestfailed',r=>log({event:'requestfailed',page:id,url:r.url(),failure:r.failure()}));
  page.on('console',m=>{if(m.type()==='error'||m.type()==='warning')log({event:'console_'+m.type(),page:id,message:m.text()});});
  const evaluate=page.evaluate.bind(page);
  page.evaluate=async(fn,arg)=>{
   const result=await evaluate(fn,arg);
   if(typeof arg==='number'&&typeof result==='string'&&result.startsWith('data:image/png;base64,')){
    const exposure=await evaluate(async({entry,t})=>(await import(entry)).poseAt(t),{entry,t:arg});
    const png=Buffer.from(result.split(',')[1],'base64');
    log({event:'actual_frame',page:id,frame:Math.round(arg*24),t:arg,exposure,png_sha256:crypto.createHash('sha256').update(png).digest('hex'),png_bytes:png.length});
   }
   return result;
  };
  const close=page.close.bind(page);
  page.close=async(...args)=>{await Promise.all([...pending]);return close(...args);};
  return page;
 };
 return browser;
};
