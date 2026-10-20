import {createFullS28} from './timeline.js';
import {renderFrame as renderPhone} from './phone_insert.js';
export {DURATION,FPS,FRAME_COUNT} from './timeline.js';
let stage;const full=createFullS28({getStage:async()=>stage??=(await import('./stage_adapter.js')).renderer,renderPhone});
export const renderFrame=full.renderFrame,render=full.render;
