// S26 motion only: deterministic seconds -> continuous stage-space state.
// Existing story: entrance/bark, pursuit, turtle boards, return pursuit/play.
// Planar leather turns through edge-on instead of swapping facing in one frame.
const clamp = x => Math.max(0, Math.min(1, x));
const ease = x => { const u = clamp(x); return u*u*u*(10 + u*(-15 + 6*u)); };
const ramp = (a,b,t) => ease((t-a)/(b-a));
const pulse = (a,b,c,d,t) => ramp(a,b,t)*(1-ramp(c,d,t));
const mix = (a,b,u) => a+(b-a)*u;
function track(keys,t) {
  let distance=0;
  for (let i=1;i<keys.length;i++) {
    const [a,x]=keys[i-1], [b,y]=keys[i];
    if (t<=b) {
      const u=clamp((t-a)/(b-a)), e=ease(u);
      return {x:mix(x,y,e), v:(y-x)*30*u*u*(1-u)*(1-u)/(b-a), distance:distance+Math.abs(y-x)*e};
    }
    distance+=Math.abs(y-x);
  }
  return {x:keys.at(-1)[1],v:0,distance};
}
const DOG_X=[[0,2.12],[1.4,1.84],[2.2,1.84],[5.4,1.36],[7.8,1.36],[8.8,1.24],[10.5,1.36],[11.5,1.36],[12.6,1.18],[13.4,1.20],[14.4,1.16],[18,1.35]];
const CRANE_X=[[0,1.08],[2.5,1.08],[5.2,.73],[6.5,.73],[8.2,1.78],[8.8,1.78],[10.5,1.90],[11.8,1.90],[12.7,1.75],[13.4,1.75],[14.4,1.73],[18,1.88]];
const yaw = (from,to,a,b,t) => Math.cos(mix(from,to,ramp(a,b,t)));
export function motionAt(time) {
  const t=Math.max(0,Math.min(18,time)), d=track(DOG_X,t), c=track(CRANE_X,t);
  const dogFacing=yaw(Math.PI,0,8.05,8.8,t);
  let craneYaw=Math.PI*ramp(1.7,2.5,t);
  craneYaw-=Math.PI*ramp(6.15,6.9,t);
  craneYaw+=Math.PI*ramp(10.85,11.70,t);
  craneYaw-=Math.PI*ramp(13.5,14.3,t);
  const craneFacing=Math.cos(craneYaw);
  const ride=ramp(6.05,7.8,t);
  const hop=pulse(6.35,7.05,7.65,8.35,t);
  const peck=pulse(11.85,12.45,12.85,13.35,t);
  const late=ramp(14.4,15.2,t);
  const dogRun=clamp(Math.abs(d.v)/.18);
  const craneRun=clamp(Math.abs(c.v)/.34);
  // Distance-driven strides stop when translation stops; late play adds short skips.
  const dogPhase=2*Math.PI*(d.distance/.22 + .85*Math.max(0,t-14.4)**1.18);
  const cranePhase=2*Math.PI*(c.distance/.22 + .95*Math.max(0,t-14.4)**1.18);
  const dip=pulse(5.45,6.15,7.8,8.45,t);
  const duck=pulse(11.9,12.5,12.8,13.4,t);
  const dogZ=.70-.075*dip-.045*duck+(.018*dogRun+.026*late)*Math.sin(dogPhase)**2;
  const craneZ=.68+.43*hop+(.013*craneRun+.019*late)*Math.sin(cranePhase)**2;
  const dogTilt=-.12*dip+.14*duck+.055*(dogRun+late)*Math.sin(dogPhase);
  // Turtle approaches the actual boarding point, arcs onto the hand and settles.
  // The support offset follows the SAME continuous wrist rotation as the dog.
  // Stage the boarding in space, not through the ear: rise beside the hand,
  // clear the ear, then translate over it and settle onto the support.
  const walkX=mix(1.95,1.68,ramp(0,6.05,t));
  const across=ramp(6.8,7.8,t), lifted=ramp(6.05,6.85,t);
  const turtleX=mix(walkX,d.x-dogFacing*.06,across);
  const turtleZ=mix(.45,dogZ+.285,lifted)-.04*ramp(7.05,7.8,t);
  const turtleFacing=mix(-1,dogFacing,ride);
  const turnBrace=1-dogFacing*dogFacing;
  const bark=pulse(.9,1.15,1.4,1.65,t)+pulse(1.65,1.85,2.05,2.25,t);
  return {
    dogX:d.x,dogZ,dogFacing,dogTilt,dogPhase,dogRun,
    craneX:c.x,craneZ,craneFacing,cranePhase,craneRun,hop,peck,
    turtleX,turtleZ,turtleFacing,ride,turnBrace,bark,late,
    scare:ramp(1.35,1.6,t),
    turtleWalk:mix(.85,.09,ride)*(1-.8*turnBrace),
    turtleNeck:mix(.5,.83,ride)-.35*turnBrace-.16*duck,
    turtleTilt:ride*(dogTilt*.55-.06*turnBrace+.045*late*Math.sin(dogPhase-.5)),
  };
}
