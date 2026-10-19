// Candidate covers only frames000–095. Never hold this fragment through the full shot.
export const WIDTH=1920, HEIGHT=1080, FPS=24, FRAME_COUNT=96, DURATION=96/24;
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
 {start:61,hold:3,asset:'061'},
 {start:64,hold:2,asset:'064'},
 {start:66,hold:3,asset:'066'},
 {start:69,hold:3,asset:'069'},
 {start:72,hold:3,asset:'072'},
 {start:75,hold:3,asset:'072'}, // approved exact settle reuse
 {start:78,hold:2,asset:'078'}, // fingers release before mechanism return
 {start:80,hold:2,asset:'078'}, // character exact, independent rod/globe return
 {start:82,hold:6,asset:'078'}, // globe settled, empty hands unchanged
 {start:88,hold:3,asset:'088'},
 {start:91,hold:3,asset:'091'},
 {start:94,hold:2,asset:'094'},
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
 '061':{head:[1310.1876968280087,879.6050802415948],grip:[1265.937907797672,893.56775085902],touching:false,wickTouch:false},
 '064':{head:[1282.6806826223356,928.1901186474938],grip:[1236.6785550080258,934.2567696970257],touching:false,wickTouch:false},
 '066':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '069':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '072':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '078':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '088':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '091':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},
 '094':{head:[1253.6806826223356,954.1901186474938],touching:false,wickTouch:false,tableFixed:true},


});
export function frameAt(t){
 if(!Number.isFinite(t)||t<0||t>=DURATION)throw new RangeError('S08 candidate covers frames000–095 only; F096 and later not supplied');
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
export const PLANNED_FRAME_COUNT=96;
export function mechanismAt(t){
 const frame=frameAt(t),pressed=frame>=27?1:frame>=25?.5:0;
 // F078/F079 release at low rod. First return sample080 is halfway,081 fully home;082 settled.
 const returnPhase=frame<80?0:Math.min(1,Math.max(0,(t*FPS-79)/2));
 const lift=pressed*(1-returnPhase),angle=-.85+.5*lift;
 const lever=[LAMP_BASE[0]-(150+Math.cos(angle)*95)*LAMP_SCALE,LAMP_BASE[1]+(-230+Math.sin(angle)*95)*LAMP_SCALE];
 return {frame,lift,angle,lever,globeRise:110*LAMP_SCALE*lift,handContact:frame>=23&&frame<78,wick:wickAt(t)};
}

// Only wick ignition samples advance one24fps frame to the original first-positive sample.
// Match/flicker/global t stay unchanged. Frames000–042 remain exactly dark.
export function wickAt(t){
 const frame=frameAt(t);if(frame<43)return 0;
 const u=Math.min(1,Math.max(0,(t+1/FPS-1.8)/(2.15-1.8)));
 const first=.55*(1-(1-u)*(1-u)); // original EASE.out first ignition
 // Original S08 second brightness curve(3.4..4.2), gated until globe-settle frame082.
 const v=frame<82?0:Math.min(1,Math.max(0,(t-3.4)/(4.2-3.4)));
 return first+.45*v*v*(3-2*v);
}

// Candidate shadow from the actual fixed match sprite; final tabletop raster gate remains required.
export const TABLE_MATCH_CONTACT=Object.freeze({"base":961,"a":0.2,"blur":0.6,"sy":-0.07,"dx":0,"dy":0});
