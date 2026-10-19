// Renders only3 static, human-authored SVG construction plates; no scene/rig.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'../../../..'),PACK=path.resolve(__dirname,'..');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost'),p=path.resolve(ROOT,'.'+decodeURIComponent(u.pathname));if(!p.startsWith(ROOT+path.sep)){res.writeHead(403);return res.end();}try{const b=fs.readFileSync(p);res.setHeader('Content-Type',p.endsWith('.svg')?'image/svg+xml;charset=utf-8':p.endsWith('.ttf')?'font/ttf':'application/octet-stream');res.end(b);}catch(e){res.writeHead(404);res.end();}});await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});const page=await browser.newPage({viewport:{width:2400,height:1500},deviceScaleFactor:1}),errors=[];page.on('pageerror',e=>errors.push(e.message));const rows=[];
 for(const name of ['S20_K01_F020_handoff','S20_K02_F084_crossed_rods','S20_K03_F156_laugh_bundle']){
  const svg=path.join(PACK,'reference/svg',name+'.svg'),png=path.join(PACK,'reference',name+'.png');
  await page.goto('http://127.0.0.1:'+server.address().port+'/'+path.relative(ROOT,svg).split(path.sep).join('/'));await page.evaluate(async()=>{await document.fonts.load('24px RefSC','奶奶小满握签');await document.fonts.ready;});await page.screenshot({path:png});rows.push({source:path.relative(PACK,svg),source_sha256:sha(fs.readFileSync(svg)),PNG:path.relative(PACK,png),sha256:sha(fs.readFileSync(png)),size:[2400,1500]});console.log(name+' static construction preview rendered');
 }
 await browser.close();server.close();if(errors.length)throw new Error(errors.join('\n'));fs.writeFileSync(path.join(PACK,'provenance/reference_render.json'),JSON.stringify({static_reference_previews_only:true,scene_rendered:false,rig_or_character_warp_used:false,image_generation_calls:0,errors,files:rows},null,2)+'\n');
})().catch(e=>{console.error(e);process.exit(1);});
