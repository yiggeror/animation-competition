// Geometry-only mechanism probe. No renderer, person rig, image call or scene run.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
const F=path.dirname(fileURLToPath(import.meta.url));
const P=path.resolve(F,'../..');
const root=path.resolve(P,'../../..');
const snap=path.join(P,'F000/f000_scene_gate_001/source_snapshot/js');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
// Original makeTurtle constructs textures while declaring its rig. This no-op
// canvas adapter lets the unchanged model declare the exact rig without rendering.
class NullPath{moveTo(){} lineTo(){} closePath(){} arc(){} quadraticCurveTo(){}}
globalThis.Path2D=NullPath;
globalThis.OffscreenCanvas=class{constructor(w,h){this.width=w;this.height=h;}getContext(){return new Proxy({},{get:(o,k)=>o[k]??(()=>{}),set:(o,k,v)=>(o[k]=v,true)});}};
const {makeTurtle,turtlePose}=await import(pathToFileURL(path.join(snap,'lamp/turtle.js')));
const {solve,pointOn}=await import(pathToFileURL(path.join(snap,'puppet.js')));
function functionText(text,signature){const start=text.indexOf(signature);if(start<0)throw Error(signature);let at=text.lastIndexOf('{',text.indexOf('\n',start)),level=1,i=at+1;for(;level&&i<text.length;i++){if(text[i]==='{')level++;if(text[i]==='}')level--;}return text.slice(start,i).replace(/^export /,'');}
const cameraSource=fs.readFileSync(path.join(snap,'lamp/s06_key.js'),'utf8');
const camera=Function('return '+functionText(cameraSource,'export function camera('))();
const billboardM=Function('return '+functionText(cameraSource,'export function billboardM('))();
const shotSource=fs.readFileSync(path.join(root,'js/lamp/shots/s20.js'),'utf8');
const sstep=(a,b,x)=>{const u=Math.min(1,Math.max(0,(x-a)/(b-a)));return u*u*(3-2*u);};
const turtleState=Function('turtlePose','sstep','return '+functionText(shotSource,'function turtleState('))(turtlePose,sstep);
const CAM20={pos:[3.05,1.5,1.18],target:[1.5,.42,.95],hfov:58};
const cam=camera(1920,1080,CAM20);
const reg=JSON.parse(fs.readFileSync(path.join(P,'cam20_lower_only_plus2_zero_call_003/registration_input.json'),'utf8')).pair_registration;
const pm=billboardM(cam,reg.base_world_m,reg.ox,reg.oy,reg.pixels_per_cm);
const pup=makeTurtle(1.3),bindings={T_H:{holder:'X.R',part:'head',at:[20,0]},T_S:{holder:'X.L',part:'shell',at:[0,40]}};
const states={};
for(const frame of [120,128]){const t=frame/24,state=turtleState(t),sol=solve(pup,state.pose);states[frame]={frame,time:t,flip_fraction:sstep(5.2,5.5,t),source_root_m:state.root,pose:state.pose,sol,points:Object.fromEntries(Object.entries(bindings).map(([id,b])=>[id,pointOn(pup,sol,b.part,b.at)]))};}
const sources=['lamp/turtle.js','lamp/crane.js','puppet.js','lamp/s06_key.js'].map(p=>({path:path.join(snap,p),sha256:sha(path.join(snap,p))}));sources.push({path:path.join(root,'js/lamp/shots/s20.js'),sha256:sha(path.join(root,'js/lamp/shots/s20.js'))});
if(sha(path.join(root,'js/lamp/turtle.js'))!==sha(path.join(snap,'lamp/turtle.js')))throw Error('Current turtle differs from preserved original model.');
const result={status:'GEOMETRY_ONLY_NOT_PRODUCTION_RENDER',new_image_calls:0,scene_renders:0,no_person_code_called:true,camera:CAM20,output_canvas:[1920,1080],camera_basis:{C:cam.C,right:cam.right,up:cam.up,fwd:cam.fwd,focal:cam.focal},approved_people_registration:reg,people_to_CAM20_matrix:pm,turtle_scale:1.3,bindings,old_cross_remap_never_used:true,rig:pup.rig,bounds:Object.fromEntries(pup.rig.map(j=>[j.part,pup.parts[j.part].bounds])),states,sources};
fs.writeFileSync(path.join(F,'source_model_probe.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({camera:CAM20,states:Object.fromEntries(Object.entries(states).map(([k,s])=>[k,{flip_fraction:s.flip_fraction,rootAngle:s.pose.rootAngle,points:s.points}]))}));
