// Review prefix F000-071 only: six actual drawings, 72 frames / 3 seconds.
// F072/F096 have not been drawn; no missing state is substituted here.
import { closeShot } from '../../../../js/anim/close.js';
export const DURATION = 72 / 24;
const P = '/collab/reviews/cloud_s10_20261018/';
export const SHEET = [[P+'F000_repair/candidate/F000_repaired.png',0],
  [P+'F024_027_030/candidate/F024.png',24],
  [P+'F027_fix_033_045/candidate/F027_fixed.png',27],
  [P+'F024_027_030/candidate/F030.png',30],
  [P+'F027_fix_033_045/candidate/F033.png',33],
  [P+'F027_fix_033_045/candidate/F045.png',45]];
function pick(t) { const f=Math.min(71,Math.floor(t*24+1e-6));let p=SHEET[0][0];for(const [n,start] of SHEET)if(f>=start)p=n;return p; }
const clamp = x => Math.max(0,Math.min(1,x));
const smooth = x => {const u=clamp(x);return u*u*(3-2*u);};
const shot=closeShot({bgKey:'S10_cloud_prefix72',bgCrop:[980,200,520,292],blur:22,
  layers:async t=>[{img:pick(t),x:0,y:0,sc:1}],
  light:t=>{const f=t*24,q=smooth((f-12)/10),release=smooth((f-45)/27);return {
    ambient:[.18,.19,.23],lights:[
      {x:1950,y:820,r:1300,color:[1,.62,.30],i:.45,falloff:1.4},
      {x:500-180*release,y:400,r:1450,color:[.95,.96,1],i:1.05*q*(1-.15*release),falloff:1.4}],
    exposure:1,vignette:.3,grain:2};},
  cam:()=>({x:960,y:540,fit:1})});
export const renderFrame=(ctx,t,W,H)=>shot.render(ctx,t,W,H);
