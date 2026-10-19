import {createFullS28} from '../20261019_0847_s28_full192/s28_full192.mjs';
import {renderFrame as renderPhone} from '../20261019_0847_s28_full192/phone_insert.mjs';
export {DURATION,FPS,FRAME_COUNT} from '../20261019_0847_s28_full192/s28_full192.mjs';
let stage;const full=createFullS28({getStage:async()=>stage??=(await import('./stage_adapter.mjs')).renderer,renderPhone});
export const renderFrame=full.renderFrame,render=full.render;
