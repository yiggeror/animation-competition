import fs from 'node:fs';import {pathToFileURL} from 'node:url';
class NullPath{moveTo(){}lineTo(){}closePath(){}arc(){}quadraticCurveTo(){}}
globalThis.Path2D=NullPath;globalThis.OffscreenCanvas=class{constructor(w,h){this.width=w;this.height=h}getContext(){return new Proxy({},{get:(o,k)=>o[k]??(()=>{}),set:(o,k,v)=>(o[k]=v,true)})}};
const url=p=>pathToFileURL(process.cwd()+'/'+p);const{makeTurtle,turtlePose}=await import(url('js/lamp/turtle.js'));const{solve,pointOn}=await import(url('js/puppet.js'));
function extract(src,sig){let st=src.indexOf(sig),at=src.indexOf('{',st),level=1,i=at+1;for(;level;i++){if(src[i]==='{')level++;if(src[i]==='}')level--}return src.slice(st,i).replace(/^export /,'')}
// Camera has a default object literal before its body; start from the exact body marker.
function cameraExtract(src){const st=src.indexOf('export function camera('),at=src.indexOf(') {',st)+2;let level=1,i=at+1;for(;level;i++){if(src[i]==='{')level++;if(src[i]==='}')level--}return src.slice(st,i).replace(/^export /,'')}
const src=fs.readFileSync('js/lamp/s06_key.js','utf8'),camera=Function('return '+cameraExtract(src))(),billboardM=Function('return '+extract(src,'export function billboardM('))();
const sstep=(a,b,x)=>{let u=Math.max(0,Math.min(1,(x-a)/(b-a)));return u*u*(3-2*u)};const turtleState=Function('turtlePose','sstep','return '+extract(fs.readFileSync('js/lamp/shots/s20.js','utf8'),'function turtleState('))(turtlePose,sstep);
const frozen=JSON.parse(fs.readFileSync('assets/chars/g20/frozen_stage.json')),cam=camera(1920,1080,frozen.geometry.camera),r=frozen.registration.pair_registration,pup=makeTurtle(1.3),states={};
for(const f of Array.from({length:37},(_,i)=>i+96)){const T=turtleState(f/24),sol=solve(pup,T.pose);states[f]={...T,points:{T_H:pointOn(pup,sol,'head',[20,0]),T_S:pointOn(pup,sol,'shell',[0,40])}}}
states.frozen0={root:frozen.geometry.turtle_root_m,pose:frozen.geometry.puppet_poses.turtle,points:Object.fromEntries([['T_H','head',[20,0]],['T_S','shell',[0,40]]].map(([id,p,at])=>[id,pointOn(pup,solve(pup,frozen.geometry.puppet_poses.turtle),p,at)]))};
fs.writeFileSync(new URL('./model_probe.json',import.meta.url),JSON.stringify({camera:frozen.geometry.camera,camera_basis:{C:cam.C,fwd:cam.fwd,right:cam.right,up:cam.up,focal:cam.focal},reg:r,pm:billboardM(cam,r.base_world_m,r.ox,r.oy,r.pixels_per_cm),states},null,2));console.log('Geometry-only probe exported; no humans, render or image call.');
