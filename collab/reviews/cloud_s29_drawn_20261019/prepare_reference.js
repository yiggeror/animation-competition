// Review-only technical diagram. All human pixels come from unchanged old identity art.
// Existing production puppet drawing functions supply props; no procedural character is drawn.
import {makeCrane} from '/js/lamp/crane.js';
import {makeTurtle,turtlePose} from '/js/lamp/turtle.js';
import {cranePoseOf,NECK_DOWN} from '/js/lamp/choreo.js';
import {drawPuppet,solve,pointOn} from '/js/puppet.js';

const R='/collab/reviews/cloud_s29_drawn_20261019/';
const load=src=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=reject;im.src=src;});
const [mother,original,camera]=await Promise.all([load(R+'sources/g29_old_identity_cutout_UNCHANGED.png'),load(R+'sources/g29_old_identity_RAW_UNCHANGED.png'),load(R+'camera/CODE_CAMERA_ONLY_F000/00000.png')]);
const canvas=(w,h)=>{const c=document.createElement('canvas');c.width=w;c.height=h;return c;};
const label=(x,text,px,py,size=20,color='#263f55')=>{x.fillStyle=color;x.font=`${size}px sans-serif`;x.fillText(text,px,py);};
const polygon=(x,pts)=>{x.beginPath();pts.forEach(([a,b],i)=>i?x.lineTo(a,b):x.moveTo(a,b));x.closePath();};
const nearHand=[[488,679],[530,664],[555,677],[577,696],[590,722],[582,751],[564,763],[541,757],[519,746],[505,728],[486,719]];
const farHand=[[701,662],[727,662],[760,676],[790,692],[811,709],[817,733],[807,761],[797,774],[783,770],[777,750],[755,740],[735,726],[713,717]];
// Cloth plane and hand contacts are proposals, not an adopted new drawing or bone measurements.
const cloth=[[350,746],[520,709],[718,714],[790,746],[884,835],[844,905],[552,922],[362,850]];
const raisedLip=[[730,714],[790,746],[817,793],[783,783],[753,752]];
const C_NEAR=[567,739],C_FAR=[791,746];
const crane=makeCrane(),turtle=makeTurtle();
const cp=cranePoseOf(NECK_DOWN,{mode:'two'},0,-1);
// Unchanged bone/joint geometry, one common lap-plane projection for both real props.
const plane=[.45,0,0,-.27],q=pointOn(crane,solve(crane,cp),'neck3',[10,0]);
const cRoot=[C_NEAR[0]+.45*q[0],C_NEAR[1]+.27*q[1]],tRoot=[441,829];
const tp=turtlePose(0,{walk:0,neckOut:0.05,facing:1,rootAngle:0});
function drawOne(x,pup,pose,root){x.save();x.translate(...root);x.scale(.45,-.27);drawPuppet(x,pup,pose,'r');x.restore();}
const project=(pup,pose,root,part,at)=>{const p=pointOn(pup,solve(pup,pose),part,at);return [root[0]+.45*(pose.facing??1)*p[0],root[1]-.27*p[1]];};
const shafts=[
 {puppet:'crane',part:'body',at:[-75,6],a:project(crane,cp,cRoot,'body',[-75,6]),b:[846,815]},
 {puppet:'crane',part:'neck3',at:[10,0],a:project(crane,cp,cRoot,'neck3',[10,0]),b:[827,840]},
 {puppet:'turtle',part:'shell',at:[0,40],a:project(turtle,tp,tRoot,'shell',[0,40]),b:[695,883]},
 {puppet:'turtle',part:'head',at:[20,0],a:project(turtle,tp,tRoot,'head',[20,0]),b:[752,898]}
];
function props(x){
 x.lineCap='round';for(const r of shafts){x.beginPath();x.moveTo(...r.a);x.lineTo(...r.b);x.strokeStyle='#594027';x.lineWidth=4;x.stroke();x.strokeStyle='#b58b54';x.lineWidth=1.8;x.stroke();}
 drawOne(x,turtle,tp,tRoot);drawOne(x,crane,cp,cRoot);
}
function clothGuide(x){
 x.save();polygon(x,cloth);x.fillStyle='#263d68';x.fill();x.clip();
 x.strokeStyle='#7690ae';x.lineWidth=1;for(let j=-100;j<1500;j+=18){x.beginPath();x.moveTo(j,650);x.lineTo(j+300,980);x.stroke();}
 x.restore();polygon(x,cloth);x.strokeStyle='#3d82a4';x.lineWidth=3;x.stroke();
 // A single open lip, no closed sack/knot or bulk invented over hidden contents.
 x.beginPath();x.moveTo(350,746);x.lineTo(520,709);x.lineTo(718,714);x.lineTo(...C_FAR);x.strokeStyle='#8ec6d2';x.lineWidth=4;x.stroke();
}
function frontLip(x){x.save();polygon(x,raisedLip);x.fillStyle='#2f4974';x.fill();x.strokeStyle='#8ec6d2';x.lineWidth=3;x.stroke();x.restore();}
function oldActualHand(x,pts){x.save();polygon(x,pts);x.clip();x.drawImage(mother,0,0);x.restore();}
const full=canvas(1024,1536),fx=full.getContext('2d');fx.fillStyle='#edf0f2';fx.fillRect(0,0,1024,1536);fx.drawImage(mother,0,0);clothGuide(fx);props(fx);frontLip(fx);oldActualHand(fx,nearHand);oldActualHand(fx,farHand);
label(fx,'S29 FIRST MOTHER / TECHNICAL INPUT ONLY',24,29,24);label(fx,'New full figure required; old human image = identity/proportion only',24,54,17);
for(const [p,name,col] of [[C_NEAR,'C1 right bare hand / crane neck3','#df7336'],[C_FAR,'C2 left bangle hand / open cloth lip','#7c56ab']]){
 fx.strokeStyle=col;fx.lineWidth=3;fx.beginPath();fx.arc(...p,14,0,Math.PI*2);fx.stroke();
 const y=p===C_NEAR?998:1030;fx.beginPath();fx.moveTo(...p);fx.lineTo(p[0]+70,y-8);fx.stroke();label(fx,name,425,y,17,col);
}
label(fx,'Hatched blue = open support-plane guide, not final cloth artwork.',28,1467,19);
label(fx,'Both puppets remain with grandma; no handover, no child/phone generation.',28,1495,17);
label(fx,'Not a native output, accepted pose, exposure sheet, or finished frame.',28,1521,17);

const identity=canvas(1560,950),ix=identity.getContext('2d');ix.fillStyle='#eef0f2';ix.fillRect(0,0,1560,950);
label(ix,'ACTUAL IDENTITY / MATERIAL ONLY - DO NOT COPY THE OLD CLOSED WRAP ACTION',20,35,23);
ix.drawImage(original,245,65,455,430,20,75,650,615);label(ix,'Silver bun + red pin / glasses / shy closed-mouth smile',20,725,20);
ix.drawImage(original,180,350,410,300,710,75,510,373);label(ix,'Actual blouse: light blue with white flowers',710,485,20);
ix.drawImage(original,675,632,125,155,1260,75,230,285);label(ix,'LEFT wrist only',1250,390,18);label(ix,'one jade bangle',1250,416,18);
ix.drawImage(original,424,755,240,85,715,545,680,241);label(ix,'Actual indigo resist-print cotton material; old bundle shape is not the target',710,825,18);
label(ix,'No inherited AB / head-up hold / cloth warp timing from 20261017.',22,918,22);

const prop=canvas(1600,960),px=prop.getContext('2d');px.fillStyle='#e9eef1';px.fillRect(0,0,1600,960);
label(px,'REAL PRODUCTION PUPPETS / lap plane and C1 contact - reference only',20,35,23);
px.save();px.translate(-500,-1000);px.scale(2,2);clothGuide(px);props(px);frontLip(px);px.restore();
label(px,'crane: existing makeCrane + one down-curved flat pose; neck3 rivet/straight segment',20,852,19);
label(px,'turtle: existing makeTurtle, retracted head; both thin flat leather pieces rest on cloth',20,882,19);
label(px,'Uniform .45 px/mm before common 0.6 lap-plane foreshortening; not a measured camera solve.',20,913,18);
label(px,'Four straight rods remain attached to true parts, laid inside cloth; none belongs to Xiaoman.',20,943,18);

const contacts=canvas(1560,1000),cx=contacts.getContext('2d');cx.fillStyle='#edf0f2';cx.fillRect(0,0,1560,1000);
label(cx,'ONE COMPLETE ACTION DOMAIN / SOFT CONTACT TARGETS, NOT ADOPTED HANDS',20,34,22);
cx.drawImage(full,165,400,745,620,20,70,1043,868);
label(cx,'C1: near RIGHT bare hand',1090,130,19);label(cx,'supports real crane neck3.',1090,160,19);
label(cx,'Thumb / fingers straddle',1090,200,18);label(cx,'the flat joint; no gap.',1090,229,18);
label(cx,'C2: far LEFT jade wrist',1090,330,19);label(cx,'pinches raised cloth lip.',1090,359,19);label(cx,'Tail feather stays BELOW lip.',1090,391,17);
label(cx,'Cloth is on thighs;',1090,435,19);label(cx,'puppets on cloth;',1090,464,19);label(cx,'fingers are foreground.',1090,493,19);
label(cx,'Redraw both entire arm chains',1090,600,17);label(cx,'and native contact edges.',1090,628,17);
label(cx,'No old hand-patch adoption.',1090,665,17);
label(cx,'Full source figure remains visible in input01; seat and feet are proportion/support references only.',20,976,18);

const cam=canvas(1920,1140),ax=cam.getContext('2d');ax.drawImage(camera,0,0);ax.fillStyle='#f0f2f3';ax.fillRect(0,1080,1920,60);
label(ax,'ACTUAL CODE FRAME t=0 - camera/light/space only. Closed bundle and legacy action are NOT the new pose.',20,1118,22);

window.referencePayload={'inputs/01_FIRST_MOTHER_COMPLETE_TECHNICAL_TARGET.png':full.toDataURL('image/png'),'inputs/02_ACTUAL_IDENTITY_MATERIAL_ONLY.png':identity.toDataURL('image/png'),'inputs/03_REAL_PUPPETS_OPEN_CLOTH_SUPPORT.png':prop.toDataURL('image/png'),'inputs/04_COMPLETE_ARMS_AND_CONTACT_TARGETS.png':contacts.toDataURL('image/png'),'inputs/05_ACTUAL_CAMERA_LIGHT_ONLY.png':cam.toDataURL('image/png')};
window.softTargets={status:'FIRST_MOTHER_INPUT_PREPARATION_ONLY_NOT_APPROVED_FOR_GENERATION',sourceHuman:'oldg29 unchanged pixels used only as identity/proportion scaffolding; not new art',newNativeOutputRequired:true,nearBareRightContact:C_NEAR,farBangleLeftClothContact:C_FAR,clothSupportPolygon:cloth,raisedFarClothLip:raisedLip,farContactDepth:'fingers -> raised cloth lip -> tail feathers -> lower cloth -> thighs',cranePose:cp,turtlePose:tp,craneRoot:cRoot,turtleRoot:tRoot,oneLapPlaneMatrix:plane,craneTruePart:'neck3',craneTruePartLocalPoint:[10,0],contactProofAfterDiagramProjection:[cRoot[0]-.45*q[0],cRoot[1]-.27*q[1]],fourTrueAttachedStraightShafts:shafts,sourceHandsAreOnlyTechnicalOcclusionExamples:true,finalNativeWholeArmsAndFingersMustBeReviewed:true,all288frameTimingPrepared:false,imagegenCalls:0};
window.referenceReady=true;
