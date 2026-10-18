// Candidate covers only frames000–040. Never hold this fragment through the full shot.
export const WIDTH=1920, HEIGHT=1080, FPS=24, FRAME_COUNT=41, DURATION=41/24;
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
});
export function frameAt(t){
 if(!Number.isFinite(t)||t<0||t>=DURATION)throw new RangeError('S08 first41 candidate covers only frames000–040; F041 and later not supplied');
 return Math.min(FRAME_COUNT-1,Math.floor(t*FPS+1e-9));
}
export function poseAt(t){const frame=frameAt(t);let row=EXPOSE[0];for(const r of EXPOSE){if(r.start>frame)break;row=r;}return {frame,asset:row.asset,...CONTACTS[row.asset]};}
const flicker=t=>1+.06*Math.sin(t*9.3)+.04*Math.sin(t*17.7)+.03*Math.sin(t*31);
export function fireAt(t){
 const pose=poseAt(t); // validate range even when unlit
 const m=pose.frame<5?0:t<.4?1.6-(t-.2)*3.75:.85+.06*Math.sin(t*19);
 return {frame:pose.frame,head:pose.head,lit:m>0,m,flicker:flicker(t),wick:0,lift:mechanismAt(t).lift};
}

// Contact is derived only from the isolated F017 box alpha, never from the character.
// Measured alpha bottom row970; nominal lower edge971. Small contact candidate: actual Canvas gate still required.
export const TABLE_BOX_CONTACT=Object.freeze({base:970,a:.22,blur:.65,sy:-.055,dx:0,dy:0});

// F023 holds high, F025 holds halfway, and F027 holds the low lever with fully raised globe.
export const PLANNED_FRAME_COUNT=41;
export function mechanismAt(t){
 const frame=frameAt(t),lift=frame>=27?1:frame>=25?.5:0,angle=-.85+.5*lift;
 const lever=[LAMP_BASE[0]-(150+Math.cos(angle)*95)*LAMP_SCALE,LAMP_BASE[1]+(-230+Math.sin(angle)*95)*LAMP_SCALE];
 return {frame,lift,angle,lever,globeRise:110*LAMP_SCALE*lift,handContact:frame>=23,wick:0};
}
