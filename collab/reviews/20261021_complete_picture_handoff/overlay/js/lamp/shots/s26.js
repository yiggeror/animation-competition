// S26: same shot/story/light, repaired hand silhouette and continuous play.
import { makeShot, CAM_B } from './shotkit.js';
import { makeTurtle, turtlePose } from '../turtle.js';
import { makeDog, dogPose, rootForShadow } from '../handdog.js';
import { NECK_UP, NECK_LOW, NECK_DOWN, cranePoseOf, mixNeck, craneRods, turtleRods } from '../choreo.js';
import { motionAt } from './s26_motion.js';
export const DURATION = 18;
let TURTLE = null;
const DOGS = new Map();
function dogAt(f) {
  const key=f.toFixed(6);
  if (!DOGS.has(key)) {
    if (DOGS.size >= 24) DOGS.delete(DOGS.keys().next().value);
    DOGS.set(key,makeDog(1.0,f));
  }
  return DOGS.get(key);
}
const F = [1.50, .9, .80], DOG_D = .40;

export function cast(t, env) {
  TURTLE ||= makeTurtle();
  const q = motionAt(t);
  const dogRoot = rootForShadow(F,DOG_D,q.dogX,q.dogZ);
  const dPose = dogPose(t,{bark:q.bark,pant:.25+.3*q.late,facing:1,rootAngle:q.dogTilt*q.dogFacing});
  dPose.angles.jaw *= q.dogFacing; // profile is already projected in dogAt
  // Fold the neck slightly during the hop; subsequently answer the dog's feint.
  let neck=mixNeck(NECK_LOW,NECK_UP,(.4+.6*q.scare)*(1-.5*q.hop));
  neck=mixNeck(neck,NECK_DOWN,Math.max(.67*q.peck,.4*q.hop));
  neck=neck.map((v,i)=>v+.022*(q.craneRun+q.late)*(1-q.hop)*Math.sin(q.cranePhase+i*.3));
  const cRoot=[q.craneX,q.craneZ];
  const cPose=cranePoseOf(neck,{mode:'two'},.05+.04*q.craneRun-.06*q.peck,q.craneFacing);
  const walk=cranePoseOf(neck,{mode:'walk',ph:q.cranePhase},0,q.craneFacing).angles;
  // Blend to planted legs before the pivot, rather than switching walk/two.
  const amount=Math.min(1,q.craneRun+.65*q.late)*(1-q.hop);
  for(const k of ['tibia_near','tarsus_near','foot_near','tibia_far','tarsus_far','foot_far']) {
    cPose.angles[k]+=(walk[k]-cPose.angles[k])*amount;
  }
  // Both knees tuck during the existing evasive turn, so the crane clears the dog.
  for(const side of ['near','far']) {
    cPose.angles['tibia_'+side]+=(1.5-cPose.angles['tibia_'+side])*q.hop;
    cPose.angles['tarsus_'+side]+=(-2.8-cPose.angles['tarsus_'+side])*q.hop;
    cPose.angles['foot_'+side]+=(.8-cPose.angles['foot_'+side])*q.hop;
  }
  const tRoot=[q.turtleX,q.turtleZ];
  const tPose=turtlePose(t,{facing:q.turtleFacing,walk:q.turtleWalk,neckOut:q.turtleNeck,rootAngle:q.turtleTilt,headTilt:-.12*q.turnBrace});
  const turtle={pup:TURTLE,pose:tPose,root:tRoot,dist:.004,rods:turtleRods(tRoot,q.turtleFacing)};
  const craneA={pup:env.crane,pose:cPose,root:cRoot,dist:.004,rods:craneRods(env.RODS,cRoot)};
  const dog={pup:dogAt(q.dogFacing),pose:dPose,root:dogRoot,dist:DOG_D};
  return {turtle,craneA,dog};
}
let LAST=null;
const sheet=(t,env)=>{LAST=cast(t,env);return [LAST.turtle,LAST.craneA];};
const flash=()=>({pos:F,r:.62,I:.16,color:[.72,.86,1],actors:[LAST.turtle,LAST.craneA,LAST.dog]});
export const {render,renderFrame}=makeShot({sheet,flash,cam:CAM_B});
