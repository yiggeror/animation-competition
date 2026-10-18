// Candidate covers only frames 000–013. Never hold this fragment through the full shot.
export const WIDTH=1920, HEIGHT=1080, FPS=24, FRAME_COUNT=14, DURATION=14/24;
export const LAMP_BASE=Object.freeze([1415,965.6]), LAMP_SCALE=14/18.5;
export const ORIGINAL_TABLE=Object.freeze({left_x:764,surface_rear_y:950.2,front_y:981});
export const LAMP_WICK=Object.freeze([1415,965.6-226*LAMP_SCALE]);
export const EXPOSE=Object.freeze([
 {start:0,hold:3,asset:'000'}, {start:3,hold:2,asset:'003'},
 {start:5,hold:1,asset:'005'}, {start:6,hold:3,asset:'006'},
 {start:9,hold:3,asset:'009'}, {start:12,hold:2,asset:'005'},
]);
// Read from the locked original image and its approved contact-coordinate ledger.
// Coordinates are screen-space source pixels; no hand or match transformation is applied.
export const CONTACTS=Object.freeze({
 '000':{head:[1076,764],grip:[1048,801],striker:[1092,750,1158,759],touching:false},
 '003':{head:[1124,755],grip:[1096,792],striker:[1092,750,1158,759],touching:true},
 '005':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
 '006':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
 '009':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
});
export function frameAt(t){
 if(!Number.isFinite(t)||t<0||t>=DURATION)throw new RangeError('S08 first14 candidate covers only frames 000–013; no later poses are supplied');
 return Math.min(FRAME_COUNT-1,Math.floor(t*FPS+1e-9));
}
export function poseAt(t){const frame=frameAt(t);let row=EXPOSE[0];for(const r of EXPOSE){if(r.start>frame)break;row=r;}return {frame,asset:row.asset,...CONTACTS[row.asset]};}
const flicker=t=>1+.06*Math.sin(t*9.3)+.04*Math.sin(t*17.7)+.03*Math.sin(t*31);
export function fireAt(t){
 const pose=poseAt(t); // validate range even when unlit
 const m=pose.frame<5?0:t<.4?1.6-(t-.2)*3.75:.85+.06*Math.sin(t*19);
 return {frame:pose.frame,head:pose.head,lit:m>0,m,flicker:flicker(t),wick:0,lift:0};
}
