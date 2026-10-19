// Run frozen command audits while retaining all writes exclusively in this delivery directory.
const fs=require('fs'),path=require('path'),{fileURLToPath}=require('url');const write=fs.writeFileSync.bind(fs);
fs.writeFileSync=(p,...args)=>{const s=p instanceof URL?fileURLToPath(p):String(p),n=path.basename(s);if(!['TEST_RESULT.json','TEST_FIRST53_RESULT.json','FIRE_SHAKE_049_050.json'].includes(n))throw Error('Unexpected source audit write: '+s);return write(path.resolve(__dirname,'../static_'+n),...args);};
