// Candidate adapter only. No fabricated background or autonomous fallback rendering.
import {lamp,flameShape} from './original_lamp.mjs';
export const VIEW = Object.freeze({x:190,y:100,width:1600,height:900});
export const EXPOSURES=Object.freeze([96,102,108,114,120,126].map((start,i)=>Object.freeze({
  id:'G'+String(start).padStart(3,'0'),start,end:start+5,
  lampX:i===3?844:860,lampY:[980,980,820,716,737,737][i]
})));
export function exposureAt(t){
  if(!Number.isFinite(t))throw new TypeError('Finite S14 seconds required');
  const frame=Math.floor(t*24+1e-6);
  return EXPOSURES.find(e=>frame>=e.start&&frame<=e.end)??null;
}
function hook(ctx,front=false){
  ctx.strokeStyle='#6c5945';ctx.lineWidth=3;ctx.beginPath();
  if(front){ctx.moveTo(879,171);ctx.bezierCurveTo(880,182,872,188,862,188);}
  else {ctx.moveTo(860,64);ctx.lineTo(860,154);ctx.bezierCurveTo(886,156,884,188,862,188);}
  ctx.bezierCurveTo(848,188,842,174,846,164);ctx.stroke();
}
export function makeLampClose({loadAdopted,drawExistingBackstage,applyExistingLight}={}){
  for(const [name,fn] of Object.entries({loadAdopted,drawExistingBackstage,applyExistingLight}))
    if(typeof fn!=='function')throw new Error('Unbound production dependency: '+name);
  return async function renderClose(ctx,t,W,H){
    const e=exposureAt(t);if(!e)return false; // Caller retains F095 and resumes original shot F132.
    if(!(W>0&&H>0)||Math.abs(W/H-16/9)>1e-8)throw new Error('16:9 destination required; no stretching');
    const im=await loadAdopted(e.id);
    if(!im||im.width!==1200||im.height!==1140)throw new Error('Expected adopted whole-component 1200x1140 '+e.id);
    const k=W/VIEW.width;
    ctx.save();
    try{
      ctx.beginPath();ctx.rect(0,0,W,H);ctx.clip();
      ctx.setTransform(k,0,0,k,-VIEW.x*k,-VIEW.y*k);
      // Callback must draw actual backstage + original low box (top y980), not old wide-shot props.
      // Background must cover source [190,100,1600,900], including previously unseen right 590 source px.
      ctx.save();
      try { await drawExistingBackstage(ctx,{t,exposure:e,viewport:VIEW,curtainLit:false}); }
      finally { ctx.restore(); }
      hook(ctx);
      ctx.save();
      try {
        ctx.translate(e.lampX,e.lampY);ctx.scale(.8,.8);
        lamp(ctx,0,true,e.start<108);flameShape(ctx,[0,-226],.75,5.8);
      } finally { ctx.restore(); }
      if(e.start>=120)hook(ctx,true);
      ctx.drawImage(im,0,0); // Already registered complete limb, no rescaling or per-limb edits.
      // Existing production material/light pass; do not substitute flat technical background.
      await applyExistingLight(ctx,{t,exposure:e,viewport:VIEW,lamp:[e.lampX,e.lampY],curtainLit:false});
    }finally{ctx.restore();}
    return true;
  };
}
