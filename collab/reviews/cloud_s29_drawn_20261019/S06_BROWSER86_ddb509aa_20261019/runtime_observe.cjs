// Review-only observer: use installed Chromium when the bundled executable is absent.
// The supplied producer, production source, Canvas defaults and render loop are unchanged.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=__dirname,root=process.cwd(),{chromium}=require(require.resolve('playwright',{paths:[root]}));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'collab/reviews/20261019_1250_s06_browser86_gate/MANIFEST.json')));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const data={source_commit:'ddb509aa7e8283134e76980a638c81155578f520',pid:process.pid,started_utc:new Date().toISOString(),state:'STARTING',producer:'collab/reviews/20261019_1250_s06_browser86_gate/render_s06_browser86_stream.cjs',producer_sha256:sha(path.join(root,'collab/reviews/20261019_1250_s06_browser86_gate/render_s06_browser86_stream.cjs')),playwright_default_executable:chromium.executablePath(),default_executable_exists:fs.existsSync(chromium.executablePath()),actual_executable:'/usr/bin/chromium',launch_argument_overrides:[],sourceChecks:[],responses:[],pageerrors:[],requestfailed:[],consoleErrors:[],new_imagegen_calls:0};
for(const r of [manifest.module,...manifest.assets]){const actual=sha(path.join(root,r.path));data.sourceChecks.push({path:r.path,sha256:actual,expected:r.sha256,pass:actual===r.sha256});}
if(data.sourceChecks.some(x=>!x.pass))throw Error('Frozen S06 source/PNG hash mismatch');
const write=()=>fs.writeFileSync(path.join(out,'RUNTIME_HTTP_AND_EXIT.json'),JSON.stringify(data,null,2)+'\n');write();
const originalLaunch=chromium.launch.bind(chromium);
chromium.launch=async options=>{
 const browser=await originalLaunch({...options,executablePath:'/usr/bin/chromium'});data.state='RUNNING';write();
 const originalNewPage=browser.newPage.bind(browser);
 browser.newPage=async options=>{const page=await originalNewPage(options);
  page.on('response',r=>{data.responses.push({url:r.url(),status:r.status()});write();});
  page.on('pageerror',e=>{data.pageerrors.push(String(e));write();});
  page.on('requestfailed',r=>{data.requestfailed.push({url:r.url(),failure:r.failure()});write();});
  page.on('console',m=>{if(m.type()==='error'){data.consoleErrors.push(m.text());write();}});return page;};return browser;
};
process.on('exit',code=>{data.exit_code=code;data.state=code===0?'EXITED_0':'FAILED';data.finished_utc=new Date().toISOString();data.sourceChecksAfter=data.sourceChecks.map(x=>({...x,sha256:sha(path.join(root,x.path)),pass:sha(path.join(root,x.path))===x.expected}));write();});
