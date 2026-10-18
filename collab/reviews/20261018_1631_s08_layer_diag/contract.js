// One-frame composition diagnostic, never a substitute for completeS08.
export const WIDTH=1920,HEIGHT=1080,FPS=24,FRAME_COUNT=1,DURATION=1/FPS;
export const ART={filename:'S08_F000_grandma_match_box_RGBA.png',sha256:'c803571d4a6446e783fcbeb7aef41d65c1862ff3bf78a9a53f34b4631170e3f3',width:1920,height:1080,x:0,y:0,sc:1};
export const LAMP_BASE=Object.freeze([1415,965.6]),LAMP_SCALE=14/18.5;
export const LAMP_WICK=Object.freeze([1415,965.6-226*LAMP_SCALE]);
export const ORIGINAL_TABLE=Object.freeze({left_x:764,surface_rear_y:950.2,front_y:981});
export function requireT0(t){if(!Number.isFinite(t)||t!==0)throw new RangeError('S08 first-mother diagnostic permits only t=0; future states are not supplied');return 0;}
