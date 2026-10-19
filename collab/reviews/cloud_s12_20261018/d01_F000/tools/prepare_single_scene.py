from pathlib import Path
import json,hashlib,subprocess,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();P=R/'collab/reviews/cloud_s12_20261018';O=P/'d01_F000';M=O/'contact_masks';M.mkdir();S=O/'scene';S.mkdir();im=Image.open(O/'candidate/F000.png').convert('RGBA');alpha=np.asarray(im)[:,:,3];stats={}
for threshold in [1,8,32,128,200]:
 yy,xx=np.where(alpha>=threshold);stats[str(threshold)]={'count':int(len(xx)),'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]}
# Individual same-pose alpha patches. Far knee/shin ground contact is naturally occluded by the near leg.
patches=[
 ('R_knee',[(465,1230),(632,1215),(638,1290),(490,1318)],1305,True),
 ('R_shin',[(218,1222),(480,1215),(505,1318),(195,1323)],1309,True),
 ('R_shoe',[(43,1224),(216,1192),(232,1305),(53,1330)],1310,True),
 ('L_knee',[(596,1114),(654,1130),(657,1206),(610,1220)],1218,False),
 ('L_shin',[(209,1106),(466,1108),(585,1190),(198,1215)],1213,False),
 ('L_shoe',[(20,1110),(209,1095),(218,1196),(35,1250)],1243,True)]
rows=[]
for name,poly,base,visible in patches:
 mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).polygon(poly,fill=255);a=np.minimum(alpha,np.asarray(mask));out=np.zeros((*alpha.shape,4),np.uint8);out[:,:,3]=a;Image.fromarray(out).save(M/f'{name}.png');rows.append({'name':name,'source_alpha_polygon_native':poly,'native_contact_base_y':base,'path':f'../contact_masks/{name}.png','alpha_pixels_nonzero':int(np.count_nonzero(a)),'visible_ground_contact_gate':visible,'note':'Actual native alpha patch;near body will cover occluded far knee/shin shadow. No independent proof of hidden joint anatomy.'})
B={'scale':.70,'x':275,'y':112};opaque_bottom=stats['128']['bbox'][3]-1;y0=B['y']+B['scale']*opaque_bottom
u=(191/24-2)/6;ss=u*u*(3-2*u);fit=1+.04*ss;cy=540-10*ss;ym=540+fit*(y0-cy)
meta={'native_candidate_SHA256':hashlib.sha256((O/'candidate/F000.png').read_bytes()).hexdigest(),'native_size':list(im.size),'alpha_diagnostics':stats,'registration':B,'reference_provisional_registration':{'scale':.75,'x':300,'y':100},'registration_reason':'Uniform placement fitted to actual complete native figure;reference placement was explicitly provisional.No warp/pose rotation or camera/box change. Astra must review this actual registration.','actual_opaque_bottom_scene_F000':y0,'F000_opaque_bottom_margin':1080-y0,'same_F000_pose_end_camera_numeric_margin':1080-ym,'end_camera_note':'Diagnostic applying original final camera to the SAME first-mother alpha only;not a rendered or generatedF191 pose,not proof of finalC feet.','contacts':rows,'all_six_contacts_independently_visible':False,'hidden_far_knee_shin_note':'Far knee/shin ground contacts are occluded;do not claim six independently visible contact shadows.'}
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
# Keep source room/lid/box/front unchanged, remove the old transmitted-light projection for F000.
src=(R/'js/paint/shots/s12.js').read_text();room=src[src.index('let ROOM = null;'):src.index('async function bg(')];bg=src[src.index('async function bg('):src.index('// 箱子前板')];i=bg.index('  const show =');j=bg.index('  x.restore();\n  // 箱子里',i);bg=bg[:i]+bg[j:];bg=bg.replace('async function bg(t, A, R, M)','async function bgF000()');front=src[src.index('let FRONT = null;'):src.index('const shot = {')]
header="""// S12 F000 ONLY candidate. Actual native art, no old G/groupM/action/rig pose logic.
import {renderPaint,loadImg} from '../../../../../js/paint/paintshot.js';
import {makeCrane} from '../../../../../js/lamp/crane.js';
import {drawPuppet} from '../../../../../js/puppet.js';
export const DURATION=1/24;
const W=1920,H=1080,LINE='#3e2a1e';
export const BOX={x0:1000,x1:1860,rim:800,back:760,floor:1040,lidH:310};
export const REGISTRATION=Object.freeze({scale:.70,x:275,y:112});
let setupPromise;
async function setup(){
 setupPromise ||= (async()=>{
  const [poseData,contactData]=await Promise.all(['../../geometry/three_key_pose_proposal.json','../qa/native_alpha_contacts_registration.json'].map(async p=>{const r=await fetch(new URL(p,import.meta.url));if(!r.ok)throw Error('missingF000data '+p);return r.json()}));
  const nativePath=new URL('../candidate/F000.png',import.meta.url).href,r=await fetch(nativePath);if(!r.ok)throw Error('missingF000native');const bytes=await r.arrayBuffer();
  const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');if(hash!==contactData.native_candidate_SHA256)throw Error('F000 native SHA changed');
  const person=await createImageBitmap(new Blob([bytes],{type:'image/png'}));if(person.width!==1024||person.height!==1536)throw Error('F000 native canvas changed');
  const masks=await Promise.all(contactData.contacts.map(async c=>({...c,img:await loadImg(new URL(c.path,import.meta.url).href)})));
  if(masks.some(c=>!c.img))throw Error('missing F000 contactmask');
  return {person,masks,A:poseData.states[0],crane:makeCrane(1.35,'plain')};
 })();return setupPromise;
}
"""
footer="""
function nativeContactShadows(masks){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),B=REGISTRATION;
 for(const m of masks){
  x.save();x.globalAlpha=.34;x.filter='blur(3px)';
  x.translate(B.x,B.y+B.scale*m.native_contact_base_y);
  x.transform(B.scale,0,.04*B.scale,-.10*B.scale,0,0);x.translate(0,-m.native_contact_base_y);x.drawImage(m.img,0,0);x.restore();
 }
 return {img:c,x:0,y:0,sc:1};
}
function propAndRestingRods(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
let cachedShadows,cachedProps;
const sstep=(a,b,x)=>{const u=Math.max(0,Math.min(1,(x-a)/(b-a)));return u*u*(3-2*u)};
export const shot={size:[W,H],layers:async(t)=>{
 const d=await setup(),B=REGISTRATION;
 return [cachedShadows ||=nativeContactShadows(d.masks),{img:d.person,x:B.x,y:B.y,sc:B.scale},cachedProps ||=propAndRestingRods(d),{img:front(),x:0,y:0,sc:1}];
},light:(t)=>{const f=1+.04*Math.sin(t*11)+.03*Math.sin(t*23);return {ambient:[.03,.026,.03],lights:[{x:-350,y:760,r:2700*f,color:[1,.64,.32],i:1.25,falloff:1.5},{x:1350,y:560,r:760,color:[1,.7,.42],i:.35*f,falloff:1.6}],exposure:1,vignette:.5,grain:7}},glow:()=>[],cam:t=>({x:960+20*sstep(2,8,t),y:540-10*sstep(2,8,t),fit:1+.04*sstep(2,8,t)})};
export async function renderFrame(ctx,t,w,h){if(t<0||t>=DURATION)throw RangeError('S12 candidate supports F000 only. No later exposure authorized.');shot.bg=await bgF000();return renderPaint(ctx,t,w,h,shot)}
export async function render(ctx,arg,w,h){return renderFrame(ctx,+arg||0,w,h)}
"""
(S/'s12_F000_scene.js').write_text(header+room+bg+front+footer)
(O/'qa/scene_preparation.json').write_text(json.dumps({'source_reference_commit':'09c6a981b83a4300021ad053713d5cb846326edf','source_room_box_light_camera':'js/paint/shots/s12.js','room_and_front_functions_byte_copied':True,'box_dimensions_and_original_camera_unchanged':True,'old_person_G_groupM_action_rig_used':False,'F000_transmitted_colour_drawn':False,'native_person_only_no_code_character':True,'native_person_registration':B,'registration_Astra_freeze_pending':True,'code_crane_plane_degrees':55,'code_crane_squash_used':False,'initial_crane_root':json.loads((P/'geometry/three_key_pose_proposal.json').read_text())['states'][0]['points_scene']['crane_root']},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'native_alpha':stats,'placement':B,'F000_opaque_foot_margin':1080-y0,'same_F000_final_camera_numeric_margin':1080-ym,'only_single_frame_entry':True},ensure_ascii=False))
