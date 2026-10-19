import {renderFrame} from '../20261019_0901_s28_float_depth/entry_full192.mjs';
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
window.renderFullS28=async frame=>{
  if(!Number.isInteger(frame)||frame<0||frame>191)throw new RangeError('S28 frame must be000–191');
  const start=performance.now(),meta=await renderFrame(ctx,frame/24,1920,1080);
  if(frame<132&&(!meta?.materialDepthUpload?.startsWith('RGBA32F/NEAREST')||meta.floatUpload?.floatMatUploads!==1||!meta.floatUpload.methodsRestored||!meta.floatUpload.originalProgramSlotsUnchanged||!meta.debugOverridesRestored))throw new Error('S28 float stage gate failed at'+frame);
  return{frame,time:frame/24,part:frame<132?'stage':'phone',elapsedMs:performance.now()-start,meta:meta??null,png:canvas.toDataURL('image/png')};
};
window.ready=true;
