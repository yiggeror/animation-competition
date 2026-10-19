// S28 full192 dispatch. Stage and phone use different existing renderers.
export const FPS=24, DURATION=8, FRAME_COUNT=192, PHONE_FIRST_FRAME=132;
export function routeFrame(frame){if(!Number.isInteger(frame)||frame<0||frame>=FRAME_COUNT)throw new RangeError('S28 binds integer frames000–191 only');return{frame,time:frame/FPS,part:frame<PHONE_FIRST_FRAME?'stage':'phone'};}
export function routeTime(t){if(!Number.isFinite(t)||t<0||t>=DURATION)throw new RangeError('S28 time must be0≤t<8s');return{frame:Math.min(191,Math.floor(t*FPS+1e-9)),time:t,part:t<5.5?'stage':'phone'};}
export function createFullS28({getStage,renderPhone}){async function renderFrame(ctx,t,W,H){const q=routeTime(t);if(q.part==='stage')return(await getStage()).renderFrame(ctx,t,W,H);return renderPhone(ctx,t,W,H);}return{renderFrame,async render(ctx,arg,W,H){let t;if(typeof arg==='string'&&arg.trim().startsWith('{'))t=Number(JSON.parse(arg).t??0);else t=Number(arg??0);return renderFrame(ctx,t,W,H);}};}
