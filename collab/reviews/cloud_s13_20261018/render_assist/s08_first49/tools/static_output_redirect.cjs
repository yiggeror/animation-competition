// Redirect only the source audit's two report writes; never edit the frozen source packet.
const fs=require('fs'),path=require('path'),{fileURLToPath}=require('url');const write=fs.writeFileSync.bind(fs);
fs.writeFileSync=(p,...args)=>{const s=p instanceof URL?fileURLToPath(p):String(p),n=path.basename(s);if(!['TEST_RESULT.json','WICK_WITHDRAWAL_046_048.json'].includes(n))throw Error('Unexpected source audit write: '+s);return write(path.resolve(__dirname,'../static_'+n),...args);};
