// Source/EDL glue. Existing root-local clips/music remain owned by the coordinator.
export const FPS = 24;
export const SOURCE_BINDINGS = Object.freeze({
  S12:{mod:'task/s12_correct_shoulder_group140_candidate.js',frames:140,status:'final shoulder/color picture review passed'},
  S25:{mod:'js/anim/s25_continuous_v8.js',frames:108,status:'V8 adopted by user; V3/V6/V7 rejected'},
  S14:{mod:'js/paint/shots/s14.js',frames:190},
  S26:{mod:'js/lamp/shots/s26.js',frames:432},
  S27:{mod:'js/lamp/shots/s27.js',frames:120},
  S30:{mod:'js/paint/shots/s30_drawn.js',frames:196},
  S32:{mod:'js/code/s32.js',frames:360}
});
export const S20_SOURCE_REF = 'overlay/js/anim/s20_natural_20261021.js; actual cleanup patch included';
// Exact actual S20 binding is supplied by default; no private package is needed.
export function bindCurrentSources(existingShots, externalS20 = {mod:'js/anim/s20_natural_20261021.js',frames:127}) {
  if (!externalS20 || !externalS20.mod || !Number.isInteger(externalS20.frames) || externalS20.frames <= 0)
    throw Error('Supply an exact S20 module and frame count.');
  const output=existingShots.map(shot=>{
    if(shot.id==='S20')return {...shot,mod:externalS20.mod,dur:externalS20.frames/FPS,sourceProvenance:S20_SOURCE_REF};
    const b=SOURCE_BINDINGS[shot.id];return b?{...shot,mod:b.mod,dur:b.frames/FPS,sourceStatus:b.status||'current supplied source'}:{...shot};
  });
  return {SHOTS:output,TOTAL:output.reduce((s,r)=>s+r.dur,0),pictureAcceptancePending:[],audioChanged:false};
}
