// Read frozen source audits; redirect their report to this exclusive delivery directory.
const fs=require('fs'),path=require('path'),{fileURLToPath}=require('url');const write=fs.writeFileSync.bind(fs);
fs.writeFileSync=(p,...args)=>{const s=p instanceof URL?fileURLToPath(p):String(p),n=path.basename(s);if(n!=='TEST_RESULT.json')throw Error('Unexpected source audit write: '+s);return write(path.resolve(__dirname,'../static_'+n),...args);};
