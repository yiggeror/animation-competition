from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np, math,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;P=R/'F033_FINAL_LOCKED';src=P/'S08_F033_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47';im=Image.open(src).convert('RGBA');W,H=im.size
near=Image.open(P/'F033_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png').convert('RGBA');far=Image.open(P/'F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png').convert('RGBA');box=Image.open(P/'F033_fixed_table_box_RGBA.png').convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
old={'near_shoulder':(742,704),'near_sleeve_exit':(810,814),'near_elbow':(895,881),'near_wrist':(1092.22326308,763.59126049),'far_shoulder':(1030,690),'far_sleeve_exit':(1074,835),'far_elbow':(1081,879),'far_wrist':(1140,829),'neck_skin_root':(901,690),'collar_V':(899,735),'face_center':(929,546),'cranium_center':(886,478)}
head=(1335,785);oldhead=(1230,707);angle=5.;th=math.radians(angle);c,s=math.cos(th),math.sin(th)
def tf(p):q=np.array(p)-oldhead;return np.array([c*q[0]-s*q[1]+head[0],s*q[0]+c*q[1]+head[1]])
new={'near_shoulder':(808,717),'far_shoulder':(1059,697),'neck_skin_root':(956,704),'collar_V':(958,750),'face_center':(989,562),'cranium_center':(946,494),'far_wrist':old['far_wrist'],'near_wrist':tf(old['near_wrist']).tolist()}
U=float(np.linalg.norm(np.array(old['near_elbow'])-old['near_shoulder']));F=float(np.linalg.norm(np.array(old['near_wrist'])-old['near_elbow']));sh=np.array(new['near_shoulder']);wr=np.array(new['near_wrist']);v=wr-sh;L=np.linalg.norm(v);e=v/L;aa=(U*U-F*F+L*L)/(2*L);h=math.sqrt(U*U-aa*aa);candidates=[sh+aa*e+k*h*np.array([-e[1],e[0]]) for k in (-1,1)];el=max(candidates,key=lambda z:z[1]);new['near_elbow']=el.tolist();new['near_sleeve_exit']=(sh+.55*(el-sh)).tolist()
# Far-arm source manually annotated on the actual027 silhouette; modest target, whole chain must be redrawn behind the near arm.
new['far_elbow']=(1101,881);new['far_sleeve_exit']=(1090,823)
knob=(1233.9532049683,766.8943738424);pivot=(1301.4864864865,791.5459459459)
nearnew=near.transform((W,H),Image.Transform.AFFINE,(c,s,oldhead[0]-c*head[0]-s*head[1],-s,c,oldhead[1]+s*head[0]-c*head[1]),Image.Resampling.BICUBIC)
nearnew.save(O/'qa/F036_real_near_hand_PREPARATION_RGBA.png')
def point(d,p,label,col):
 x,y=p;d.ellipse((x-4,y-4,x+4,y+4),fill=col);d.text((x+7,y+5),label,font=small,fill=col)
def rod(d):d.line((knob,pivot),fill=(58,42,34),width=5);x,y=knob;d.ellipse((x-6.81,y-6.81,x+6.81,y+6.81),fill=(58,42,34))
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 a=Image.alpha_composite(Image.new('RGBA',(W,H),bg),im);d=ImageDraw.Draw(a);rod(d)
 for chain,col in [(['far_shoulder','far_sleeve_exit','far_elbow','far_wrist'],(40,165,185)),(['near_shoulder','near_sleeve_exit','near_elbow','near_wrist'],(200,74,106))]:
  d.line([old[k] for k in chain],fill=col,width=2)
  for k in chain:point(d,old[k],k.replace('_',' '),col)
 d.text((580,275),'F033 ACTUAL LOCKED SOURCE: approximate screen-joint proxies',font=font,fill=(70,90,115));d.text((580,298),f'Near shoulder-elbow {U:.1f}px; elbow-wrist {F:.1f}px. Not 3D bone lengths.',font=font,fill=(70,90,115));a.crop((550,265,1445,1045)).convert('RGB').save(O/'qa'/f'F033_actual_chain_{tag}.png')
 # Only construction artwork; no warped body or invented painted hand.
 a=Image.new('RGBA',(W,H),bg);d=ImageDraw.Draw(a);scale=14/18.5;d.rectangle((1415-170*scale,965.6-560*scale,1415-144*scale,965.6-120*scale),fill=(153,62,52));cy=965.6-314*scale;d.ellipse((1415-130*scale,cy-18*scale,1415+130*scale,cy+18*scale),fill=(117,52,45));d.rectangle((1398,794,1432,814),fill=(193,157,80));rod(d);a.alpha_composite(box)
 # Full chest-neck-head coordination. All actual identity planes will be painted from027.
 ns,fs=new['near_shoulder'],new['far_shoulder'];nr=new['neck_skin_root'];cv=new['collar_V'];hc=new['cranium_center']
 d.polygon([ns,(610,1080),(985,1080),fs],fill=(211,226,236),outline=(70,115,145));d.line((ns,nr,fs),fill=(70,115,145),width=3);d.line((nr,cv,(887,922),(850,1080)),fill=(70,115,145),width=3)
 d.ellipse((hc[0]-140,hc[1]-162,hc[0]+143,hc[1]+162),outline=(70,115,145),width=3);d.line(((hc[0]-55,hc[1]+55),(hc[0]+114,hc[1]+71)),fill=(70,115,145),width=2);d.line(((hc[0]+2,hc[1]+157),nr),fill=(70,115,145),width=3)
 d.line((fs,new['far_sleeve_exit'],new['far_elbow'],new['far_wrist']),fill=(147,158,166),width=35);d.line((fs,new['far_sleeve_exit'],new['far_elbow'],new['far_wrist']),fill=(59,110,135),width=2);a.alpha_composite(far)
 d=ImageDraw.Draw(a);d.line((ns,new['near_sleeve_exit'],new['near_elbow'],new['near_wrist']),fill=(235,213,186),width=45);d.line((ns,new['near_sleeve_exit'],new['near_elbow'],new['near_wrist']),fill=(154,105,74),width=2);a.alpha_composite(nearnew)
 d=ImageDraw.Draw(a);x,y=head;d.line([(x,y+2),(x-9.3,y-10),(x-7,y-24),(x,y-32),(x+7,y-24),(x+9.3,y-10),(x,y+2)],fill=(191,100,38),width=2)
 for k in ['near_shoulder','near_elbow','near_wrist','far_elbow','neck_skin_root']:point(d,new[k],k.replace('_',' '),(36,98,130))
 d.text((580,275),'F036 FIRST STRUCTURE GATE - real hands; unpainted body construction',font=font,fill=(70,90,115));d.text((580,298),'Actual033 screen proxies guide036 only; elbow moves forward with torso.',font=font,fill=(70,90,115));d.text((580,321),'Helper pipe / rim geometry only. Near hand passes in FRONT of left pipe.',font=small,fill=(70,90,115))
 a.crop((550,265,1445,1080)).convert('RGB').save(O/'qa'/f'F036_whole_chain_gate_{tag}.png');a.crop((1060,650,1490,930)).resize((1290,840)).convert('RGB').save(O/'qa'/f'F036_real_hand_contact_gate_{tag}.png')
report={'status':'FIRST_F036_STRUCTURE_GATE_ONLY_NO_REQUEST_OR_NATIVE_CALL','source':str(src),'source_sha256':sha,'source_points_screen_approx':old,'target_points_screen_approx':new,'near_chain_proxy_lengths_033':[U,F],'near_chain_proxy_lengths_036':[float(np.linalg.norm(el-sh)),float(np.linalg.norm(wr-el))],'projection_note':'Manual screen proxies with5-10px uncertainty. Conserved2D segment lengths are a conservative first construction baseline, NOT anatomical bone lengths or a demand to flatten3D perspective. Natural elbow, sleeve volume and projected changes remain actual-image review.','near_group_transform':{'scale':1,'clockwise_rotation_deg':5,'source_match_head':oldhead,'target_match_head':head,'visible_exit':tf((1194.9191346191965,737.3699338842536)).tolist(),'visible_segment_px':46.400431},'far_hand_jade_alpha0_seat':'Complete original033 underlying far hand restored behind moving near hand; true low grip and alpha0 seat preserved.149 old outside/ink guards and31 originaljade AA underlay treated by033 contract, not blindly hard-locked.','body_change':'Near shoulder+66,+13, far shoulder+29,+7; neck root+55,+14; head+60,+16; coherent whole chest yaw/lean toward lamp. Actual eye gaze to lower new match head. Fullbody painting, not a translated face or stretched arm.','near_elbow_change':(el-np.array(old['near_elbow'])).tolist(),'next_step':'After coordinator/reviewer structure gate, prepare one actual five-image edit input and explicit mask. Reserved logicalcall17, not submitted.'};(O/'geometry/F036_first_structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))

from scipy.ndimage import distance_transform_edt
fa=np.array(far)[:,:,3]>128;na=np.array(nearnew)[:,:,3]>128
fm=Image.new('L',(W,H));d=ImageDraw.Draw(fm);x,y=head;d.polygon([(x,y+2),(x-9.3,y-10),(x-7,y-24),(x,y-32),(x+7,y-24),(x+9.3,y-10)],fill=255);fm=np.array(fm)>0
seat=Image.new('L',(W,H));ImageDraw.Draw(seat).ellipse((knob[0]-5,knob[1]-5,knob[0]+5,knob[1]+5),fill=255);seat=np.array(seat)>0
report['actual_033_far_hand_occluded_by_true036_near_visible_px']=int((fa&na).sum());report['near_visible_over_low_knob_core_px']=int((seat&na).sum());report['flame_envelope_min_far_hand_px']=float(distance_transform_edt(~fa)[fm].min());report['flame_envelope_far_visible_overlap_px']=int((fm&fa).sum());report['flame_depth_note']='036 endpoint is past the left pipe. Full033→036 sweep crosses pipe projection: near hand, match and independent flame are in front of pipe; real Canvas depth gate still required. Geometry is NOT a2Dclear path. This structure image draws no real flame asset.'
(O/'geometry/F036_first_structure.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
