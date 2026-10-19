// Actual S12 F018 only audit. Process browser selection; no shared renderer changes.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=path.resolve(__dirname,'../qa/actual_canvas_network_events.jsonl');let nextPage=0;
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
    // Read back the SAME cached actual layers for diagnostic alpha checks; never call renderFrame again.
    const aux=await evaluate(async(t)=>{
     const mod=await import('../'+new URLSearchParams(location.search).get('mod'));
     const layers=await mod.shot.layers(t),result={};
     for(const [name,index] of [['person_registered',1],['code_props',2],['native_ground_shadows',0]]){
      const layer=layers[index],c=new OffscreenCanvas(1920,1080),x=c.getContext('2d');
      x.translate(layer.x,layer.y);x.scale(layer.sc,layer.sc);x.drawImage(layer.img,0,0);
      const b=await c.convertToBlob({type:'image/png'});result[name]=await new Promise(resolve=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.readAsDataURL(b);});
     }
     return result;
    },arg);
    for(const [name,data] of Object.entries(aux)){
     const b=Buffer.from(data.split(',')[1],'base64'),p=path.resolve(__dirname,'../actual_scene/F018_'+name+'_actual_layer.png');fs.writeFileSync(p,b);
     log({event:'actual_cached_layer_readback',frame:18,t:arg,name,PNG_SHA256:crypto.createHash('sha256').update(b).digest('hex'),bytes:b.length});
    }
   }
   return result;
  };
  return page;
 };
 return browser;
};
