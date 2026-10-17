import fs from 'node:fs';
import {turtlePose} from '/workspace/animation-competition/js/lamp/turtle.js';
import {solve,pointOn} from '/workspace/animation-competition/js/puppet.js';
import {sstep} from '/workspace/animation-competition/js/lamp/choreo.js';
const src=fs.readFileSync('/workspace/animation-competition/js/lamp/shots/s20.js','utf8');
const state=new Function('turtlePose','sstep',src.match(/function turtleState\(t\) \{[\s\S]*?\n\}/)[0]+';return turtleState;')(turtlePose,sstep);
const key=fs.readFileSync('/workspace/animation-competition/js/lamp/s06_key.js','utf8');
const camera=new Function(key.match(/export function camera\(W, H, o = \{\}\) \{[\s\S]*?\n\}/)[0].replace('export ','')+';return camera;')();
const cam=camera(960,540,{pos:[3.05,1.5,1.18],target:[1.5,.42,.95],hfov:58});
// Geometry only: exact shell/neck/head attachment chain from makeTurtle(1.3); no canvas or rendering.
const rig=[{part:'shell',parent:null,at:[0,0]},{part:'neck0',parent:'shell',at:[110*1.3,14*1.3]},{part:'neck1',parent:'neck0',at:[32*1.3,0]},{part:'neck2',parent:'neck1',at:[32*1.3,0]},{part:'head',parent:'neck2',at:[32*1.3,0]}];
const records=[];
for(const frame of [0,143]){
 const T=state(frame/24),sol=solve({rig},T.pose);
 const W=mm=>cam.project([T.root[0]+mm[0]/1000,.004,T.root[1]+mm[1]/1000]);
 const q0=W([0,0]),q1=W([100,0]),q2=W([0,100]);
 const a=[(q1[0]-q0[0])/100,(q1[1]-q0[1])/100,(q2[0]-q0[0])/100,(q2[1]-q0[1])/100];
 const m=[a[0]/2,a[1]/2,-a[2]/2,-a[3]/2,q0[0]-a[0]*600/2+a[2]*500/2,q0[1]-a[1]*600/2+a[3]*500/2];
 const pm=pointOn({rig},sol,'head',[20,0]),f=T.pose.facing;
 const shown=[q0[0]+a[0]*f*pm[0]+a[2]*pm[1],q0[1]+a[1]*f*pm[0]+a[3]*pm[1]];
 const px=[600+f*pm[0]*2,500-pm[1]*2];
 const fixed=[m[0]*px[0]+m[2]*px[1]+m[4],m[1]*px[0]+m[3]*px[1]+m[5]];
 const old=cam.project([T.root[0]+f*pm[0]/1000,.004,T.root[1]+pm[1]/1000]).slice(0,2);
 records.push({frame,t:frame/24,displayed_head_anchor:shown,new_rod_endpoint:fixed,new_formula_gap_px:Math.hypot(fixed[0]-shown[0],fixed[1]-shown[1]),old_rod_endpoint:old,old_formula_gap_px:Math.hypot(old[0]-shown[0],old[1]-shown[1])});
}
fs.writeFileSync('/tmp/laidian-audit-latest-independent/s20_geometry.json',JSON.stringify({method:'Independent geometry recomputation from current functions and minimal turtle attachment chain; not pixel detection, no rendering',records},null,2)+'\n');
console.log(JSON.stringify(records,null,2));
