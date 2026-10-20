const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;
const MIME={'.js':'text/javascript','.json':'application/json','.html':'text/html','.png':'image/png','.jpg':'image/jpeg'};
function start(port=0,repo=null){
  const roots=[ROOT,path.join(ROOT,'support')]; if(repo)roots.push(path.resolve(repo));
  const server=http.createServer((req,res)=>{
    let name;try{name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400);return res.end('Bad URL');}
    if(name==='/')name='/host.html';
    const files=roots.map(root=>({root,file:path.resolve(root,'.'+name)}));
    const hit=files.find(({root,file})=>file.startsWith(root+path.sep)&&fs.existsSync(file)&&fs.statSync(file).isFile());
    if(!hit){res.writeHead(404);return res.end('Missing '+name);}
    res.writeHead(200,{'Content-Type':MIME[path.extname(hit.file)]||'application/octet-stream','Cache-Control':'no-store'});fs.createReadStream(hit.file).pipe(res);
  });
  return new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',()=>resolve(server));});
}
module.exports={start};
if(require.main===module){const args=process.argv.slice(2),read=k=>{const i=args.indexOf(k);return i<0?null:args[i+1]};start(Number(read('--port')||0),read('--repo')).then(s=>console.log('http://127.0.0.1:'+s.address().port+'/host.html')).catch(e=>{console.error(e);process.exitCode=1;});}
