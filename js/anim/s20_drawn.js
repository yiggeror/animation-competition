// Unified partial S20 entry. Missing exposures never fall back to old GL people.
import * as CAM20 from './s20_cam20_drawn.js';
import * as LAUGH from './s20_laugh_drawn.js';
export const DURATION=9,FPS=24;
export async function getSequenceInfo(){const [front,laugh]=await Promise.all([CAM20.getSequenceInfo(),LAUGH.getSequenceInfo()]);return {...front,availableIntervals:[...front.availableIntervals,[144,215]],laughManifest:laugh};}
export const renderClosure=CAM20.renderClosure;
export async function renderFrame(ctx,t,W,H){const f=Math.floor(t*24+1e-7);if(f>=144&&f<=215)return LAUGH.renderFrame(ctx,t,W,H);if(f>=132&&f<=143){const q=await CAM20.getSequenceInfo(),e=q.closure.exposures?.find(s=>f>=s.start&&f<=s.end);if(e)return CAM20.renderClosure(ctx,t,W,H,e.role)}return CAM20.renderFrame(ctx,t,W,H)}
export async function render(ctx,arg,W,H){return renderFrame(ctx,+arg||0,W,H)}
