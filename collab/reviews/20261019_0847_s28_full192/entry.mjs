import {createFullS28} from './s28_full192.mjs';
import {renderFrame as renderPhone} from './phone_insert.mjs';
export {DURATION,FPS,FRAME_COUNT} from './s28_full192.mjs';
let stage;const full=createFullS28({getStage:async()=>stage??=(await import('./stage_adapter.mjs')).renderer,renderPhone});
export const renderFrame=full.renderFrame,render=full.render;
