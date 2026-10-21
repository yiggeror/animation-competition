// Local review candidate only. Original apparatus labels do not prescribe exposure lengths.
import * as old from '../js/anim/s12_early_retained_current140.js';
import * as palm from '../collab/reviews/cloud_s12_20261018/natural_arms052_20261021/s12_natural_arms052.js';
import * as low from '../collab/reviews/cloud_s12_20261018/natural_low_hold_20261021/s12_natural_low_hold.js';
import * as mid from '../collab/reviews/cloud_s12_20261018/natural_visual_mid_rise_20261021/s12_natural_visual_mid_rise.js';
import * as first from '../collab/reviews/cloud_s12_20261018/natural_first_lift_20261021/s12_natural_first_lift.js';
import * as terminal from '../collab/reviews/cloud_s12_20261018/natural_terminal_identity_20261021/s12_natural_terminal_identity.js';
import * as lift from '../collab/reviews/cloud_s12_20261018/natural_same_identity_lift_20261021/s12_natural_same_identity_lift.js';
import * as peak from '../collab/reviews/cloud_s12_20261018/natural_same_identity_peak_20261021/s12_natural_same_identity_peak.js';
import * as back from '../collab/reviews/cloud_s12_20261018/natural_same_identity_return_20261021/s12_natural_same_identity_return.js';
import * as look from '../collab/reviews/cloud_s12_20261018/natural_same_identity_look_20261021/s12_natural_same_identity_look.js';
export const DURATION=140/24,FPS=24;
export async function renderFrame(ctx,t,w,h){
 const f=Math.floor(t*24+1e-7);if(f<0||f>=140)throw Error('140 exposure local candidate only');
 if(f<48)return old.renderFrame(ctx,t,w,h);
 if(f<56)return palm.renderPhase(ctx,t,w,h);
 if(f<64)return low.renderPhase(ctx,t,w,h);
 if(f<70)return mid.renderPhase(ctx,t,w,h,70);
 if(f<76)return first.renderPhase(ctx,t,w,h,f<74?70:74);
 if(f<82)return terminal.renderPhase(ctx,t,w,h,f<80?90:94);
 if(f<96)return lift.renderPhase(ctx,t,w,h,f<84?102:f<86?106:110);
 if(f<102)return peak.renderPhase(ctx,t,w,h,120);
 if(f<108)return back.renderPhase(ctx,t,w,h,126);
 if(f<116)return lift.renderPhase(ctx,t,w,h,132);
 return look.renderPhase(ctx,t,w,h,144);
}
