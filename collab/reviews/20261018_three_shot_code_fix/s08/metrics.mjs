// Reproducible numerical evidence only. No image/video output.
import { pose, matchGeom, WICK, leverTip, lift, DURATION } from '../../../../js/anim/s08.js';
import { armSide } from '../../../../js/anim/kit.js';
import { hand } from '../../../../js/chars/hand.js';
import { NN } from '../../../../js/chars/nainai.js';
import { M } from '../../../../js/lib/figure.js';
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]),px=14*2/3;
const world=(p,P)=>[p[0]+(P.x||0),p[1]+P.y];
function farGrip(P){const A=P.armF,a=armSide('n',P,'F',A.hand);return world(hand({part(){},detail(){}},M.chain(M.t(...a.W),M.r(a.dir+A.rot)),A.hp,{size:NN.palm,z:0}).grip,P);}
let maximumReach={ratio:0},maximumWristStep240Hz={cm:0},maximumRotationStep240Hz={radians:0};
for(let i=0;i<=1440;i++){
  const t=i/240,{P}=pose(t);
  for(const side of ['N','F']){
    const a=armSide('n',P,side,P['arm'+side].hand);
    if(a.reach>maximumReach.ratio)maximumReach={ratio:a.reach,t,side};
    if(i){const Q=pose((i-1)/240).P,d=dist(world(P['arm'+side].hand,P),world(Q['arm'+side].hand,Q)),r=Math.abs(P['arm'+side].rot-Q['arm'+side].rot);
      if(d>maximumWristStep240Hz.cm)maximumWristStep240Hz={cm:d,t,side};
      if(r>maximumRotationStep240Hz.radians)maximumRotationStep240Hz={radians:r,t,side};
    }
  }
}
const contactFrames=[40,41,42,43,44,45,46].map(frame=>{const t=frame/24,{P}=pose(t);return{frame,t,head:matchGeom(P).head,wick:WICK,miss720px:dist(matchGeom(P).head,WICK)*px};});
const leverFrames=[22,23,24,27,41,78,79,80,81,82].map(frame=>{const t=frame/24,{P}=pose(t);return{frame,t,lift:lift(t),grip:farGrip(P),lever:leverTip(lift(t)),separation720px:dist(farGrip(P),leverTip(lift(t)))*px};});
console.log(JSON.stringify({evidence:'Node geometry only; no raster rendering or MP4 validation',duration:DURATION,maximumReach,maximumWristStep240Hz,maximumRotationStep240Hz,contactFrames,leverFrames},null,2));
