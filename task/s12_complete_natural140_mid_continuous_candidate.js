// Local edd1fc middle and continuous mechanism candidate; all other accepted phases preserved.
import * as prior from './s12_complete_natural140_candidate.js';
import * as junction from './s12_first_terminal_mid_continuous_candidate.js';
export const FPS=24,DURATION=140/24;
export async function renderFrame(ctx,t,w,h){const f=Math.floor(t*24+1e-7);return f>=70&&f<=82?junction.renderFrame(ctx,t,w,h):prior.renderFrame(ctx,t,w,h);}
