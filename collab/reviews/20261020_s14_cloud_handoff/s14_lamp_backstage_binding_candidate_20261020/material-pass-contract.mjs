import {frameGeometry,S15_LIGHT} from './geometry.mjs';
// Prepare inputs BEFORE original GL scene pass. Never a final Canvas warm overlay.
export function prepareMaterialPass(binding,frame,{cards,originalRoom,originalLightShader}={}){
 const state=frameGeometry(binding,frame);if(!state)return null;
 if(!cards?.alb||!cards?.nrm||!cards?.mat||!cards?.registrationEvidence)throw Error('Actual registered albedo/normal/material cards required');
 if(!originalRoom?.geometrySource||!originalRoom?.withoutOldCharacters||!originalRoom?.withoutUnrequestedScenery)throw Error('Explicit original room-only geometry required');
 if(!originalLightShader?.sceneFS||!originalLightShader?.sourceSha)throw Error('Original physical scene shader required');
 return {frame,state,sceneLight:{...S15_LIGHT,position:state.light.position},cards,
   hook:binding.hook,lowBox:binding.lowBox,originalRoom,originalLightShader,
   curtainLit:false,applyBeforeScenePass:true,postCompositeWarmLayer:false,
   outsideRange:'return null; retain original S14 from F132 and S15 unchanged'};
}
