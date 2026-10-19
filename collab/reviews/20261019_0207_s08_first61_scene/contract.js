// Candidate covers only frames000–060. Never hold this fragment through the full shot.
export const WIDTH=1920, HEIGHT=1080, FPS=24, FRAME_COUNT=61, DURATION=61/24;
export const LAMP_BASE=Object.freeze([1415,965.6]), LAMP_SCALE=14/18.5;
export const ORIGINAL_TABLE=Object.freeze({left_x:764,surface_rear_y:950.2,front_y:981});
export const LAMP_WICK=Object.freeze([1415,965.6-226*LAMP_SCALE]);
export const EXPOSE=Object.freeze([
 {start:0,hold:3,asset:'000'}, {start:3,hold:2,asset:'003'},
 {start:5,hold:1,asset:'005'}, {start:6,hold:3,asset:'006'},
 {start:9,hold:3,asset:'009'}, {start:12,hold:2,asset:'005'},
 {start:14,hold:3,asset:'014'}, {start:17,hold:3,asset:'017'},
 {start:20,hold:3,asset:'020'},
 {start:23,hold:2,asset:'023'},
 {start:25,hold:2,asset:'025'},
 {start:27,hold:3,asset:'027'},
 {start:30,hold:3,asset:'030'},
 {start:33,hold:3,asset:'033'},
 {start:36,hold:2,asset:'036'},
 {start:38,hold:3,asset:'038'},
 {start:41,hold:2,asset:'041'},
 {start:43,hold:3,asset:'043'},
 {start:46,hold:3,asset:'046'},
 {start:49,hold:2,asset:'049'},
 // Approved F051 reverse shake is exact F046 RGBA; reuse originals, no new transforms.
 {start:51,hold:2,asset:'046'},
 // Approved F053 character/gaze is exact F051/F046; only code flame/smoke changes.
 {start:53,hold:5,asset:'046'},
 {start:58,hold:3,asset:'058'},
]);
// Read from the locked original image and its approved contact-coordinate ledger.
// Coordinates are screen-space source pixels; no hand or match transformation is applied.
export const CONTACTS=Object.freeze({
 '000':{head:[1076,764],grip:[1048,801],striker:[1092,750,1158,759],touching:false},
 '003':{head:[1124,755],grip:[1096,792],striker:[1092,750,1158,759],touching:true},
 '005':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
 '006':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
 '009':{head:[1074,782],grip:[1046,819],striker:[1092,750,1158,759],touching:false},
 '014':{head:[1074,782],grip:[1046,819],touching:false},
 '017':{head:[1074,782],grip:[1046,819],touching:false},
 '020':{head:[1062,787],grip:[1034,824],touching:false},
 '023':{head:[1070,791],grip:[1042,828],touching:false},
 '025':{head:[1076,794],grip:[1048,831],touching:false},
 '027':{head:[1082,797],grip:[1054,834],touching:false},
 '030':{head:[1148,717],grip:[1116.881786,751.418843],touching:false},
 '033':{head:[1230,707],grip:[1194.9191346191965,737.3699338842536],touching:false},
 '036':{head:[1335,785],grip:[1297.4057137582938,812.1968682383957],touching:false},
 '038':{head:[1390,788],grip:[1351.033861314945,813.19206295596],touching:false},
 // touching remains striker-contact; wickTouch denotes the new unlit-wick contact.
 '041':{head:[1415,794.572972972973],grip:[1375.442494558651,818.8258854425643],touching:false,wickTouch:true},
 '043':{head:[1415,794.572972972973],grip:[1375.442494558651,818.8258854425643],touching:false,wickTouch:true},
 '046':{head:[1350,782.572972972973],grip:[1310.442494558651,806.8258854425643],touching:false,wickTouch:false},
 '049':{head:[1352.1936211377067,825.7393602711344],grip:[1307.7068893620028,838.9276390032729],touching:false,wickTouch:false},
 '058':{head:[1333.5355768960655,827.4023133073218],grip:[1292.0148191055773,848.1152723548265],touching:false,wickTouch:false},
});
export function frameAt(t){
 if(!Number.isFinite(t)||t<0||t>=DURATION)throw new RangeError('S08 first61 candidate covers only frames000–060; F061 and later not supplied');
 return Math.min(FRAME_COUNT-1,Math.floor(t*FPS+1e-9));
}
export function poseAt(t){const frame=frameAt(t);let row=EXPOSE[0];for(const r of EXPOSE){if(r.start>frame)break;row=r;}return {frame,asset:row.asset,...CONTACTS[row.asset]};}
const flicker=t=>1+.06*Math.sin(t*9.3)+.04*Math.sin(t*17.7)+.03*Math.sin(t*31);
export function fireAt(t){
 const pose=poseAt(t); // validate range even when unlit
 const m=pose.frame<5||pose.frame>=53?0:t<.4?1.6-(t-.2)*3.75:.85+.06*Math.sin(t*19);
 return {frame:pose.frame,head:pose.head,lit:m>0,m,flicker:flicker(t),wick:wickAt(t),lift:mechanismAt(t).lift};
}

// Contact is derived only from the isolated F017 box alpha, never from the character.
// Measured alpha bottom row970; nominal lower edge971. Small contact candidate: actual Canvas gate still required.
export const TABLE_BOX_CONTACT=Object.freeze({base:970,a:.22,blur:.65,sy:-.055,dx:0,dy:0});

// F023 holds high, F025 holds halfway, and F027 holds the low lever with fully raised globe.
export const PLANNED_FRAME_COUNT=61;
export function mechanismAt(t){
 const frame=frameAt(t),lift=frame>=27?1:frame>=25?.5:0,angle=-.85+.5*lift;
 const lever=[LAMP_BASE[0]-(150+Math.cos(angle)*95)*LAMP_SCALE,LAMP_BASE[1]+(-230+Math.sin(angle)*95)*LAMP_SCALE];
 return {frame,lift,angle,lever,globeRise:110*LAMP_SCALE*lift,handContact:frame>=23,wick:wickAt(t)};
}

// Only wick ignition samples advance one24fps frame to the original first-positive sample.
// Match/flicker/global t stay unchanged. Frames000–042 remain exactly dark.
export function wickAt(t){
 const frame=frameAt(t);if(frame<43)return 0;
 const u=Math.min(1,Math.max(0,(t+1/FPS-1.8)/(2.15-1.8)));
 return .55*(1-(1-u)*(1-u)); // original EASE.out (quadratic), first ignition branch only
}
