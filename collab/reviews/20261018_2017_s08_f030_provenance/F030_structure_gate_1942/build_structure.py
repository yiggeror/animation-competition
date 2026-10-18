from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np, math,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;P=R.parent/'astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED';src=P/'S08_F027_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='2dc0ee2bc06b4b872e0f79cbf4c1bd19b2ccaa160cba9b5feefd45f2a8e268ac';im=Image.open(src).convert('RGBA');W,H=im.size
near=Image.open(P/'F027_true_near_hand_match_RGBA.png').convert('RGBA');far=Image.open(P/'F027_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png').convert('RGBA');box=Image.open(P/'F027_fixed_table_box_RGBA.png').convert('RGBA')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
old={'near_shoulder':(668,683),'near_sleeve_exit':(695,813),'near_elbow':(782,948),'near_wrist':(959,881),'far_shoulder':(994,680),'far_sleeve_exit':(1007,795),'far_elbow':(1063,882),'far_wrist':(1140,829),'neck_skin_root':(834,689),'collar_V':(840,736),'face_center':(866,535),'cranium_center':(826,480)}
head=(1148,717);oldhead=(1082,797);angle=5.;th=math.radians(angle);c,s=math.cos(th),math.sin(th)
def tf(p):q=np.array(p)-oldhead;return np.array([c*q[0]-s*q[1]+head[0],s*q[0]+c*q[1]+head[1]])
new={'near_shoulder':(712,694),'far_shoulder':(1006,680),'neck_skin_root':(868,693),'collar_V':(874,740),'face_center':(904,539),'cranium_center':(864,484),'far_wrist':old['far_wrist'],'near_wrist':tf(old['near_wrist']).tolist()}
U=float(np.linalg.norm(np.array(old['near_elbow'])-old['near_shoulder']));F=float(np.linalg.norm(np.array(old['near_wrist'])-old['near_elbow']));sh=np.array(new['near_shoulder']);wr=np.array(new['near_wrist']);v=wr-sh;L=np.linalg.norm(v);e=v/L;aa=(U*U-F*F+L*L)/(2*L);h=math.sqrt(U*U-aa*aa);candidates=[sh+aa*e+k*h*np.array([-e[1],e[0]]) for k in (-1,1)];el=max(candidates,key=lambda z:z[1]);new['near_elbow']=el.tolist();new['near_sleeve_exit']=(sh+.47*(el-sh)).tolist()
# Far-arm source manually annotated on the actual027 silhouette; modest target, whole chain must be redrawn behind the near arm.
new['far_elbow']=(1070,886);new['far_sleeve_exit']=(1020,795)
knob=(1233.9532049683,766.8943738424);pivot=(1301.4864864865,791.5459459459)
nearnew=near.transform((W,H),Image.Transform.AFFINE,(c,s,oldhead[0]-c*head[0]-s*head[1],-s,c,oldhead[1]+s*head[0]-c*head[1]),Image.Resampling.BICUBIC)
def point(d,p,label,col):
 x,y=p;d.ellipse((x-4,y-4,x+4,y+4),fill=col);d.text((x+7,y+5),label,font=small,fill=col)
def rod(d):d.line((knob,pivot),fill=(58,42,34),width=5);x,y=knob;d.ellipse((x-6.81,y-6.81,x+6.81,y+6.81),fill=(58,42,34))
for tag,bg in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 a=Image.alpha_composite(Image.new('RGBA',(W,H),bg),im);d=ImageDraw.Draw(a);rod(d)
 for chain,col in [(['far_shoulder','far_sleeve_exit','far_elbow','far_wrist'],(40,165,185)),(['near_shoulder','near_sleeve_exit','near_elbow','near_wrist'],(200,74,106))]:
  d.line([old[k] for k in chain],fill=col,width=2)
  for k in chain:point(d,old[k],k.replace('_',' '),col)
 d.text((580,275),'F027 ACTUAL LOCKED SOURCE: approximate screen-joint proxies',font=font,fill=(70,90,115));d.text((580,298),f'Near shoulder-elbow {U:.1f}px; elbow-wrist {F:.1f}px. Not 3D bone lengths.',font=font,fill=(70,90,115));a.crop((550,265,1370,1045)).convert('RGB').save(O/'qa'/f'F027_actual_chain_{tag}.png')
 # Only construction artwork; no warped body or invented painted hand.
 a=Image.new('RGBA',(W,H),bg);d=ImageDraw.Draw(a);rod(d);a.alpha_composite(box)
 # Full chest-neck-head coordination. All actual identity planes will be painted from027.
 ns,fs=new['near_shoulder'],new['far_shoulder'];nr=new['neck_skin_root'];cv=new['collar_V'];hc=new['cranium_center']
 d.polygon([ns,(595,1080),(940,1080),fs],fill=(211,226,236),outline=(70,115,145));d.line((ns,nr,fs),fill=(70,115,145),width=3);d.line((nr,cv,(855,922),(814,1080)),fill=(70,115,145),width=3)
 d.ellipse((hc[0]-140,hc[1]-162,hc[0]+143,hc[1]+162),outline=(70,115,145),width=3);d.line(((hc[0]-55,hc[1]+55),(hc[0]+114,hc[1]+71)),fill=(70,115,145),width=2);d.line(((hc[0]+2,hc[1]+157),nr),fill=(70,115,145),width=3)
 d.line((fs,new['far_sleeve_exit'],new['far_elbow'],new['far_wrist']),fill=(147,158,166),width=35);d.line((fs,new['far_sleeve_exit'],new['far_elbow'],new['far_wrist']),fill=(59,110,135),width=2);a.alpha_composite(far)
 d=ImageDraw.Draw(a);d.line((ns,new['near_sleeve_exit'],new['near_elbow'],new['near_wrist']),fill=(235,213,186),width=45);d.line((ns,new['near_sleeve_exit'],new['near_elbow'],new['near_wrist']),fill=(154,105,74),width=2);a.alpha_composite(nearnew)
 d=ImageDraw.Draw(a);x,y=head;d.line([(x,y+2),(x-9.3,y-10),(x-7,y-24),(x,y-32),(x+7,y-24),(x+9.3,y-10),(x,y+2)],fill=(191,100,38),width=2)
 for k in ['near_shoulder','near_elbow','near_wrist','far_elbow','neck_skin_root']:point(d,new[k],k.replace('_',' '),(36,98,130))
 d.text((580,275),'F030 FIRST STRUCTURE GATE - real hands; unpainted body construction',font=font,fill=(70,90,115));d.text((580,298),'Near upper/forearm proxy lengths remain source027. Elbow moves forward/up.',font=font,fill=(70,90,115));d.text((580,321),'Chest, both shoulders, collar, neck and head turn together; NOT a pasted-head move.',font=small,fill=(70,90,115))
 a.crop((550,265,1370,1080)).convert('RGB').save(O/'qa'/f'F030_whole_chain_gate_{tag}.png');a.crop((950,650,1315,925)).resize((1095,825)).convert('RGB').save(O/'qa'/f'F030_real_hand_contact_gate_{tag}.png')
report={'status':'FIRST_F030_STRUCTURE_GATE_ONLY_NO_REQUEST_OR_NATIVE_CALL','source':str(src),'source_sha256':sha,'source_points_screen_approx':old,'target_points_screen_approx':new,'near_chain_proxy_lengths_027':[U,F],'near_chain_proxy_lengths_030':[float(np.linalg.norm(el-sh)),float(np.linalg.norm(wr-el))],'projection_note':'Manual screen proxies with5-10px uncertainty. Conserved2D segment lengths are a conservative first construction baseline, NOT anatomical bone lengths or a demand to flatten3D perspective. Natural elbow, sleeve volume and projected changes remain actual-image review.','near_group_transform':{'scale':1,'clockwise_rotation_deg':5,'source_match_head':oldhead,'target_match_head':head,'visible_exit':tf((1054,834)).tolist(),'visible_segment_px':46.400431},'far_hand_jade_alpha0_seat':'Original027 RGBA unchanged at same fixed low lever contact; released183 proximal collar remains outside guard','body_change':'Near shoulder+44,+11, far shoulder+12,0; neck root+34,+4; head+38,+4; coherent small chest yaw/lean, natural neck turn and eye gaze to the raised real match head. Full-body natural painting, no code body stretch.','near_elbow_change':(el-np.array(old['near_elbow'])).tolist(),'next_step':'After coordinator/reviewer structure gate, prepare one actual five-image edit input and explicit mask. Reserved logicalcall15, not submitted.'};(O/'geometry/F030_first_structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
