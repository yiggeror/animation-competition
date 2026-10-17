// 3-second throwaway motion probe. No shot/EDL/audio dependency, pose swaps,
// camera edits or whole-card displacement. World geometry is in 960x540 pixels.
import { pieces, XM } from './xiaoman_proof.js';
import { limbIK, ap1 } from '../cut/rig.js';
import { drawPieces } from '../cut/render.js';
export const DURATION=3, FPS=24;
export const CONFIG={s:4.3,floor:480,toeN:[492,480],toeF:[465,480],ropeX:550,ropeTop:62,restGripY:190,pull:29,localGrip:[0,2.7],toe:[7.8,4.5],heel:[-3,4.5]};
const C=CONFIG,clamp=v=>Math.max(0,Math.min(1,v));
const smooth=(a,b,t)=>{const u=clamp((t-a)/(b-a));return u*u*u*(10+u*(-15+6*u));};
const mix=(a,b,u)=>a+(b-a)*u;
const rot=(p,a)=>[Math.cos(a)*p[0]-Math.sin(a)*p[1],Math.sin(a)*p[0]+Math.cos(a)*p[1]];
const plus=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const scale=(p,k)=>[p[0]*k,p[1]*k];
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
function leg(hip,toe,a){
 const ankle=sub(toe,scale(rot(C.toe,a),C.s));
 const ik=limbIK(hip,ankle,XM.thigh*C.s,XM.shin*C.s,1,0,1);
 return {ankle,angles:[ik.upper,ik.fore,a-ik.upper-ik.fore]};
}
export function stateAt(t){
 t=Math.max(0,Math.min(DURATION,t));
 const up=smooth(.28,1.03,t),down=smooth(2.08,2.66,t),lift=up*(1-down);
 const pre=Math.sin(Math.PI*smooth(.12,.42,t));
 const pull=smooth(1.25,1.72,t),release=smooth(1.85,2.05,t);
 const ropeReturn=smooth(2.05,2.29,t);
 const extension=C.pull*pull*(1-ropeReturn);
 const ropeTail=t>2.29?1.3*Math.sin((t-2.29)*19)*Math.exp(-(t-2.29)*7):0;
 const ropeGrip=[C.ropeX,C.restGripY+extension+ropeTail];
 const held=t>=1.22&&t<=1.85;
 const close=smooth(1.06,1.22,t)*(1-release);
 const reach=smooth(.24,1.08,t)*(1-smooth(2.05,2.78,t));
 const footN=.50*lift,footF=.46*lift;
 const ankleN=sub(C.toeN,scale(rot(C.toe,footN),C.s));
 const ankleF=sub(C.toeF,scale(rot(C.toe,footF),C.s));
 const ankleRise=(ankleN[1]+ankleF[1])/2-(C.floor-C.toe[1]*C.s);
 const landing=3.2*Math.sin(Math.PI*smooth(2.46,2.96,t));
 const recoil=pull*(1-smooth(2.08,2.60,t));
 const root=[449+13*lift-1.6*recoil,349+ankleRise+3.0*pre+2.5*recoil+landing];
 const lean=.01+.055*lift-.035*recoil;
 const hipN=plus(root,[.8*C.s,0]),hipF=plus(root,[-.8*C.s,0]);
 const ln=leg(hipN,C.toeN,footN),lf=leg(hipF,C.toeF,footF);
 const shoulder=(side)=>plus(plus(root,[0,-8*C.s]),scale(rot(side==='N'?[.6,-19.4]:[-.8,-19.6],lean),C.s));
 const sn=shoulder('N'),sf=shoulder('F');
 const wristAbs=mix(-.27,-2.45+.35*recoil,reach);
 // Desired palm contact is continuous, with one target while closing/pulling.
 // After release it withdraws while the unheld cord returns independently.
 const gripForHand=[C.ropeX,C.restGripY+C.pull*pull];
 const targetWrist=sub(gripForHand,scale(rot(C.localGrip,wristAbs),C.s));
 const relaxRel=plus(scale(rot([0,XM.upper],-.12+lean),C.s),scale(rot([0,XM.fore],-.37+lean),C.s));
 const restWrist=plus(sn,relaxRel);
 const wrist=[mix(restWrist[0],targetWrist[0],reach)+5*Math.sin(Math.PI*reach),mix(restWrist[1],targetWrist[1],reach)];
 const arm=limbIK(sn,wrist,XM.upper*C.s,XM.fore*C.s,-1,lean,1);
 const farTarget=plus(sf,[(-4-2*lift)*C.s,(17.7-.8*lift)*C.s]);
 const far=limbIK(sf,farTarget,XM.upper*C.s,XM.fore*C.s,-1,lean,1);
 const headTilt=-.09*smooth(.08,.8,t)*(1-smooth(2.10,2.85,t))+.025*recoil;
 const pigLag=.045*Math.sin(t*7)*Math.sin(Math.PI*clamp((t-.2)/2.7));
 const P={x:root[0],y:root[1],s:C.s,lean,head:{tilt:headTilt},pig:[pigLag,-pigLag*.7],face:{eye:'open',look:reach,mouth:'smile',cheek:.75},
  legN:{angles:ln.angles},legF:{angles:lf.angles},
  armN:{angles:[arm.upper,arm.fore],wrist:wristAbs-(lean+arm.upper+arm.fore),curl:close},
  armF:{angles:[far.upper,far.fore],wrist:-.18-(lean+far.upper+far.fore),curl:.12+.1*lift}};
 const result=pieces(P),T=result.T;
 const joint=n=>ap1(T[n].M,[0,0]);
 const grip=ap1(T.handN.M,scale(C.localGrip,1));
 const toeN=ap1(T.footN.M,C.toe),toeF=ap1(T.footF.M,C.toe);
 const heelN=ap1(T.footN.M,C.heel),heelF=ap1(T.footF.M,C.heel);
 const joints=Object.fromEntries(Object.keys(T).map(n=>[n,joint(n)]));
 const bones=[];
 for(const side of ['N','F'])for(const [a,b,nominal] of [['up','fore',XM.upper],['fore','hand',XM.fore],['thigh','shin',XM.thigh],['shin','foot',XM.shin]])bones.push({name:a+side,from:joint(a+side),to:joint(b+side),length:dist(joint(a+side),joint(b+side)),nominal:nominal*C.s});
 const metrics={t,root,lean,lift,curl:close,held,ropeGrip,grip,requestedWrist:wrist,actualWrist:joint('handN'),wristError:dist(wrist,joint('handN')),gripError:dist(grip,ropeGrip),toeN,toeF,heelN,heelF,toeErrorN:dist(toeN,C.toeN),toeErrorF:dist(toeF,C.toeF),heelHeightN:C.floor-heelN[1],heelHeightF:C.floor-heelF[1],joints,bones,fingers:result.handJoints};
 return {P,...result,metrics,ropeGrip,grip,close,held};
}
function background(ctx){
 ctx.fillStyle='#eee9dd';ctx.fillRect(0,0,960,540);
 ctx.fillStyle='#d9d1bd';ctx.fillRect(0,C.floor,960,60);
 ctx.strokeStyle='#a79b84';ctx.lineWidth=1.4;ctx.beginPath();ctx.moveTo(0,C.floor);ctx.lineTo(960,C.floor);ctx.stroke();
 ctx.fillStyle='rgba(50,40,25,.13)';ctx.beginPath();ctx.ellipse(458,C.floor+2,55,5,0,0,7);ctx.fill();
 // Fixed pull-switch housing; the cord pays out on pull and retracts on release.
 ctx.fillStyle='#706b61';ctx.strokeStyle='#514d44';ctx.lineWidth=1.5;ctx.beginPath();ctx.roundRect(C.ropeX-11,43,22,20,5);ctx.fill();ctx.stroke();
 ctx.fillStyle='#aba597';ctx.fillRect(C.ropeX-6,46,12,3);
}
function rope(ctx,S){
 const [x,y]=S.ropeGrip;
 ctx.strokeStyle='#635440';ctx.lineWidth=2.8;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(C.ropeX,C.ropeTop);ctx.lineTo(x,y+11);ctx.stroke();
 ctx.strokeStyle='#c4b18f';ctx.lineWidth=1.1;ctx.stroke();
 ctx.fillStyle='#9b784b';ctx.strokeStyle='#5c4630';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(x,y+13,3.2,4.5,0,0,7);ctx.fill();ctx.stroke();
}
function overlay(ctx,S){
 const m=S.metrics;ctx.save();ctx.lineWidth=1.6;
 for(const b of m.bones){ctx.strokeStyle=b.name.endsWith('N')?'#078ab0':'#bd4388';ctx.beginPath();ctx.moveTo(...b.from);ctx.lineTo(...b.to);ctx.stroke();}
 for(const [n,p] of Object.entries(m.joints)){if(!/^(hip|torso|head|up|fore|hand|thigh|shin|foot)/.test(n))continue;ctx.fillStyle=n.endsWith('F')?'#bd4388':'#078ab0';ctx.beginPath();ctx.arc(...p,2.5,0,7);ctx.fill();}
 for(const p of [m.toeN,m.toeF]){ctx.strokeStyle='#168851';ctx.beginPath();ctx.arc(...p,5,0,7);ctx.stroke();}
 ctx.strokeStyle='#e34b24';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(...m.grip,5,0,7);ctx.stroke();
 ctx.fillStyle='#292b2c';ctx.font='14px sans-serif';ctx.fillText(`t ${m.t.toFixed(3)}  heel ${m.heelHeightN.toFixed(2)} px  grip ${m.gripError.toFixed(3)} px`,30,30);
 ctx.restore();
}
export function renderFrame(ctx,t,W,H,opts={}){
 const S=stateAt(t);ctx.save();ctx.setTransform(W/960,0,0,H/540,0,0);background(ctx);rope(ctx,S);
 drawPieces(ctx,S.pieces,'paper',{s:C.s,shadow:[.6,1],shadowBlur:.55,shadowColor:'rgba(45,34,22,.13)'});
 if(opts.skeleton||globalThis.__DEBUG?.skeleton)overlay(ctx,S);
 ctx.restore();return S.metrics;
}
export const render=(ctx,t,W,H)=>renderFrame(ctx,+t||0,W,H);
