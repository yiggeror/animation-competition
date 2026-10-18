// Complete S10 review candidate: eight actual drawings, 120 frames / 5 seconds.
// Camera/composition and F000-071 light match the approved 72-frame prefix.
// Only this review module; shared implementation, ready and audio stay outside it.
import { closeShot } from './close.js';
export const DURATION = 120 / 24;
const P = '/assets/chars/g10/';
export const EXPOSURES = [
  {id:'F000',start:0,end:23,path:P+'F000.png'},
  {id:'F024',start:24,end:26,path:P+'F024.png'},
  {id:'F027_fixed',start:27,end:29,path:P+'F027.png'},
  {id:'F030',start:30,end:32,path:P+'F030.png'},
  {id:'F033',start:33,end:44,path:P+'F033.png'},
  {id:'F045',start:45,end:71,path:P+'F045.png'},
  {id:'F072',start:72,end:95,path:P+'F072.png'},
  {id:'F096',start:96,end:119,path:P+'F096.png'}];
export const SHEET = EXPOSURES.map(s=>[s.path,s.start]);
function pick(t) {
  const f=Math.max(0,Math.min(119,Math.floor(t*24+1e-6)));
  return EXPOSURES.find(s=>f>=s.start&&f<=s.end).path;
}
const clamp=x=>Math.max(0,Math.min(1,x));
const smooth=x=>{const u=clamp(x);return u*u*(3-2*u);};
const shot=closeShot({bgKey:'S10_cloud_full120',bgCrop:[980,200,520,292],blur:22,
  layers:async t=>[{img:pick(t),x:0,y:0,sc:1}],
  light:t=>{const f=t*24,q=smooth((f-12)/10),early=smooth((f-45)/27),tail=smooth((f-72)/36);return {
    ambient:[.18,.19,.23],lights:[
      {x:1950,y:820,r:1300,color:[1,.62,.30],i:.45,falloff:1.4},
      {x:500-180*early-1100*tail,y:400,r:1450,color:[.95,.96,1],i:1.05*q*(1-.15*early)*(1-tail),falloff:1.4}],
    exposure:1,vignette:.3,grain:2};},
  cam:()=>({x:960,y:540,fit:1})});
export const renderFrame=(ctx,t,W,H)=>shot.render(ctx,t,W,H);
