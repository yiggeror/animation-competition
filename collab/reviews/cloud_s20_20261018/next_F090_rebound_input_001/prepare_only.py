"""F090 rebound input construction only. No image tool, exposure or later state."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,binary_fill_holes,label

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=P/'F084_two_domains_close_zero_call_001';source=S/'F084_two_domains_closed_candidate.png'
assert sha(source)=='4df5d046a399f90aa798ca2cba2bd09e0cf7977eacb1058036bfabf52ddce448'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
orig=np.array(Image.open(P/'next_F084_peak_input_001/generation_001/registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'))
oldhead=np.array(Image.open(S/'source_complete_head_neck_semantic_mask.png'))>0
newhead=np.array(Image.open(S/'084_own_head_hair_neck_one_continuous_scale.png').convert('RGBA'))
body=(orig[:,:,3]>0)&~oldhead;rest=np.zeros_like(A);rest[body]=A[body]
U0=np.array(Image.alpha_composite(Image.fromarray(rest),Image.fromarray(newhead)));U0[body]=A[body]
Image.fromarray(U0).save(F/'source084_corrected_complete_upper_head_skirt_T.png')
visible_head=(newhead[:,:,3]>100)&~body
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png','fixed_original_C_rods_scene_layer.png']:
 shutil.copyfile(P/'next_F084_peak_input_001'/name,F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';clayer=F/'fixed_original_C_rods_scene_layer.png'
assert sha(lowerfile)=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(clayer)=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'))
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def polygon(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def axis_fit(x0,x1,y0,y1):
 r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1)
 wood=(U0[:,:,3]>180)&(r>120)&(g>70)&(r>g+12)&(b<g*.8)
 points=[]
 for x in range(x0,x1):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>=y0)&(np.arange(H)<y1))
  if len(ys):points.append((x,float(np.median(ys))))
 return np.polyfit(np.array(points)[:,0],np.array(points)[:,1],1)
hm,hb=axis_fit(290,350,384,443);sm,sb=axis_fit(308,355,277,350)
oldx=(sb-hb)/(hm-sm);oldX=np.array([oldx,hm*oldx+hb])
axes=[(hm,hb,284.,418.),(sm,sb,300.,465.)]
def strip(m,b,x0,x1,width=5.2):
 return (abs(yy-m*xx-b)/math.sqrt(1+m*m)<width)&(xx>=x0-4)&(xx<=x1+3)
Rhand=polygon([(397,330),(441,320),(468,336),(487,370),(495,389),(495,419),(478,425),(460,423),(448,417),(435,396),(419,391),(400,365)])
Lhand=polygon([(429,418),(453,416),(469,430),(485,420),(508,435),(532,463),(532,495),(508,513),(477,513),(451,498),(442,460),(430,445)])&~Rhand
Rarm=polygon([(395,326),(443,319),(472,338),(492,373),(520,365),(527,346),(566,338),(582,350),(579,395),(563,430),(539,430),(494,428),(459,428),(446,419),(434,399),(417,392),(396,368)])
Larm=polygon([(428,418),(453,416),(470,430),(486,420),(511,438),(527,461),(585,479),(610,437),(605,398),(622,371),(661,361),(692,372),(711,397),(710,436),(691,473),(667,486),(626,524),(602,538),(515,508),(478,515),(449,501),(441,460),(429,445)])
rr,gg,bb=U0[:,:,:3].astype(float).transpose(2,0,1)
collar=(rr>190)&(gg>185)&(bb>175)&(abs(rr-gg)<20)&(abs(gg-bb)<20)&(xx>555)&(xx<723)&(yy>337)&(yy<405)&(U0[:,:,3]>100)
collar=binary_dilation(binary_opening(collar,iterations=1),iterations=2)
headkeep=(newhead[:,:,3]>0)&~body
Rarm&=~headkeep&~collar;Larm&=~headkeep&~collar
skin=(rr>165)&(gg>95)&(bb>gg*.65)&(rr>gg+12)&(U0[:,:,3]>0)&(xx>390)&(xx<700)&(yy>315)&(yy<555)&~headkeep&~collar
cc,nn=label(skin);sizes=np.bincount(cc.ravel());skin&=sizes[cc]>45
skinCut=binary_dilation(binary_fill_holes(skin),iterations=3)&~headkeep&~collar
farSleeve=polygon([(520,365),(527,346),(566,338),(582,350),(579,395),(563,430),(539,430)])
nearSleeve=polygon([(605,398),(622,371),(661,361),(692,372),(711,397),(710,436),(691,473),(653,475),(615,446)])
Rarm=((binary_dilation(Rarm,iterations=3)&skinCut)|farSleeve)&~headkeep&~collar
Larm=((binary_dilation(Larm,iterations=3)&skinCut)|nearSleeve)&~headkeep&~collar
shaft_masks=[strip(*axes[0]),strip(*axes[1])]
groups=[]
for hand,mask,(m,b,xf,xp) in zip([Rarm,Larm],shaft_masks,axes):
 q=np.zeros_like(U0);ownership=(hand|mask)&(U0[:,:,3]>0);q[ownership]=U0[ownership]
 # Each role gets a complete shaft at the old overlap. Clone its own actual
 # native cross-section 30px away; the other old shaft never enters its group.
 v=np.array([1.,m]);v/=np.linalg.norm(v);nearX=(np.hypot(xx-oldX[0],yy-oldX[1])<10)&mask
 sy=yy-v[1]*30;sx=xx-v[0]*30
 clone=np.stack([map_coordinates(U0[:,:,k].astype(float),[sy,sx],order=1,mode='constant',cval=0) for k in range(4)],2)
 q[nearX]=np.rint(clone[nearX]).clip(0,255).astype('uint8')
 groups.append(q)
# The two complete limbs are independent semantic layers because the source
# near thumb touches the far wrist: a shared field would fold that boundary.
contact_ownership=skinCut|shaft_masks[0]|shaft_masks[1]
no_contacts=U0.copy();no_contacts[contact_ownership]=0

def elbow_for(s,w,l1,l2):
 v=w-s;dist=np.linalg.norm(v);assert abs(l1-l2)<dist<l1+l2
 u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(l1*l1-along*along);mid=s+along*u;perp=np.array([-u[1],u[0]])
 return max([mid+height*perp,mid-height*perp],key=lambda q:q[1])
controls=[];bones=[];maps=[]
for side,s,e,w,ds,dw,degrees in [('R',[555,383],[535,405],[489,401],[5,7],[4,15],2.),('L',[665,420],[600,510],[513,483],[-5,-8],[-5,-18],-2.)]:
 s,e,w,ds,dw=map(lambda x:np.array(x,float),[s,e,w,ds,dw]);ns=s+ds;nw=w+dw;l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow_for(ns,nw,l1,l2);rr=rot(degrees)
 maps.append((w,nw,rr));controls.append((s,ns-s))
 angle=lambda v:math.degrees(math.atan2(v[1],v[0]));delta=lambda a,b:(angle(a)-angle(b)+180)%360-180
 bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'upper_bone_lengths_px':[float(l1),float(np.linalg.norm(ne-ns))],'forearm_bone_lengths_px':[float(l2),float(np.linalg.norm(nw-ne))],'upper_rotation_deg':delta(ne-ns,e-s),'forearm_rotation_deg':delta(nw-ne,w-e),'whole_palm_own_T_rotation_deg':degrees,'wrist_translation_xy':dw.tolist()})
def handmap(point,index):
 w,nw,rr=maps[index];return nw+rr@(np.asarray(point)-w)
for p,d in [([621,366],[-2,2]),([650,424],[-5,-3]),([621,490],[-4,2]),([706,477],[-7,-3]),([671,550],[-3,0]),([688,604],[-1,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
headpivot=np.array([628.,365.]);headrot=rot(-1.5);headshift=np.array([-2.,2.])
for py in range(145,402,12):
 for px in range(495,786,12):
  if visible_head[py,px] and not (590<=px<=684 and py>=330):
   point=np.array([px,py],float);controls.append((point,headpivot+headrot@(point-headpivot)+headshift-point))
for p in [[565,657],[594,679],[620,684],[650,680],[690,685],[735,678],[791,658],[831,628],[240,120],[860,120],[240,740],[860,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
unique={}
for p,d in controls:unique[tuple(np.round(p,6))]=(p,d)
controls=list(unique.values());rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=235,115,865,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(9):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=no_contacts[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
out=np.zeros_like(crop);out[:,:,3]=np.rint(wa*255).astype('uint8');out[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');out[out[:,:,3]<3]=0
bodyU=np.zeros_like(A);bodyU[y0:y1,x0:x1]=out
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
def arm_forward(points,index):
 spec=bones[index];s,e,w=np.array(spec['source_shoulder_elbow_wrist']);ns,ne,nw=np.array(spec['target_shoulder_elbow_wrist']);vu=e-s;vf=w-e;l1=np.linalg.norm(vu);l2=np.linalg.norm(vf)
 tu=np.clip((points-s)@vu/(l1*l1),0,1);tf=np.clip((points-e)@vf/(l2*l2),0,1)
 du=np.linalg.norm(points-(s+tu[:,None]*vu),axis=1);df=np.linalg.norm(points-(e+tf[:,None]*vf),axis=1)
 arc=np.where(du<df,tu*l1,l1+tf*l2);wf=smooth((arc-l1+12)/24);wh=smooth((arc-l1-l2+15)/15)
 upper=ns+(points-s)@rot(spec['upper_rotation_deg']).T
 fore=ne+(points-e)@rot(spec['forearm_rotation_deg']).T
 hand=nw+(points-w)@maps[index][2].T
 blend=upper*(1-wf[:,None])+fore*wf[:,None]
 return blend*(1-wh[:,None])+hand*wh[:,None]
U=np.zeros_like(A)
newaxes=[]
for index,(group,(m,b,xf,xp)) in enumerate(zip(groups,axes)):
 ay,ax=np.mgrid[230:570,250:750];dest=np.column_stack([ax.ravel(),ay.ravel()]).astype(float);coords=dest.copy()
 for _ in range(12):coords=dest-(arm_forward(coords,index)-coords)
 sy,sx=coords[:,1].reshape(ax.shape),coords[:,0].reshape(ax.shape)
 aa=group[:,:,3].astype(float)/255;pm=group[:,:,:3].astype(float)*aa[:,:,None]
 wa=map_coordinates(aa,[sy,sx],order=1,mode='constant',cval=0)
 wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=1,mode='constant',cval=0) for k in range(3)],2)
 patch=np.zeros(ax.shape+(4,),np.uint8);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
 moved=np.zeros_like(A);moved[230:570,250:750]=patch
 # R complete limb/TH behind torso, then L complete limb/TS in the foreground.
 U=np.array(Image.alpha_composite(Image.fromarray(U),Image.fromarray(moved)))
 if index==0:U=np.array(Image.alpha_composite(Image.fromarray(U),Image.fromarray(bodyU)))
 front=handmap([xf,m*xf+b],index);pin=handmap([xp,m*xp+b],index);nm=(pin[1]-front[1])/(pin[0]-front[0]);nb=pin[1]-nm*pin[0]
 newaxes.append({'role':['T_H','T_S'][index],'owner':['X.R','X.L'][index],'front':front.tolist(),'pin':pin.tolist(),'slope':float(nm),'intercept':float(nb)})
cc,count=label(U[:,:,3]>2);sizes=np.bincount(cc.ravel());main=int(np.argmax(sizes[1:])+1)
probes=[[570,295],[626,367],[560,390],[539,411],[493,416],[660,412],[592,500],[508,465],[625,440],[669,535],[690,630]]
assert all(cc[y,x]==main for x,y in probes)
detached=(cc>0)&(cc!=main);assert np.max(sizes[np.unique(cc[detached])],initial=0)<100
U[detached]=0
Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
nx=(newaxes[1]['intercept']-newaxes[0]['intercept'])/(newaxes[0]['slope']-newaxes[1]['slope']);newX=[float(nx),float(newaxes[0]['slope']*nx+newaxes[0]['intercept'])]
assert nx<min(q['pin'][0] for q in newaxes)
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0
target=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(U));T=np.array(target)
existing=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);T[existing]=A[existing]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(U[:,:,3]==0);T[fringe]=A[fringe]
gmask=(xx>=860)&(A[:,:,3]>0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F090_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
box=(260,245,745,555);contact=bg.crop(box).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((contact.width*3,contact.height*3),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
visible=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);white=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<850);white[visible]=False;white[gmask]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
Image.fromarray(np.uint8(visible)*255).save(F/'actual_retained_visible_complete_legs_shoes_mask.png')
rootbox=(570,640,785,755);card=Image.new('RGB',(430,115),'#bdc1c4');card.paste(bg.crop(rootbox).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');d=ImageDraw.Draw(card);d.text((16,12),'084已过身份局部：脸发、衣料、鞋；无旧整身或旧双掌姿态',font=font,fill='#263743')
for index,(box,xy,size) in enumerate([((505,145,770,375),(20,60),(318,276)),((570,350,710,430),(350,60),(320,183)),((620,535,800,650),(700,60),(300,192)),((490,835,755,935),(350,350),(530,200))]):
 origin=newhead if index==0 else (U0 if index<3 else A)
 im=Image.fromarray(origin).crop(box);cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);card.paste(cb.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,585),'头颈体量按唯一090目标；整裙白域，完整裸露腿鞋黑域',font=font,fill='#263743');card.save(I/'03_084_identity_head_clothes_shoes_patches_only.png')
comparebox=(235,125,865,720);three=Image.new('RGB',(1890,595),'#bdc1c4')
states=[P/'F079_head_neck_scale_close_zero_call_001/F079_own_head_neck_volume_closed_candidate.png',source,I/'01_unique_complete_F090_target_REVIEW_ONLY.png']
for index,path in enumerate(states):
 im=Image.open(path).convert('RGBA');cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);three.paste(cb.crop(comparebox).convert('RGB'),(630*index,0))
three.save(F/'079_passed_084_passed_090_target_same_canvas_upper_hands_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[cm],A[cm])
assert not np.any(white[visible]) and not np.any(white[736:])
prompt=f'''只绘F090峰后反向开始的唯一候选白域，未安排持帧曝光。第一图为唯一完整同姿目标：远R肩开始落、肘和腕真实下收，近L肩肘腕回抬，两条完整前臂各走自己的骨链；胸腰从084峰值蓄力回弹，完整头颈随胸肩回弹。不是整体平移084，不回贴079，不只改衣纹或几像素，尚未翻肚，不生成后态。第二图为同姿两掌/X，第三图仅刚过084脸发、衣料和鞋局部，不含旧整身或竞争动作，第四图为实际完整白黑mask。
严格保持唯一目标内正确084头发/完整头脸/下颏/马尾/红花的体量；不要逐态放大或另换头。颈部连续接回白领，头胸腰共同回应。肩、肘、腕顺接，真实上臂和前臂骨长，远臂有自然屈肘，近臂完整；腕与指腹自然，不切指、断腕或软绳臂。
小满全图任何位置只能有两根硬直杆：远R只夹T_H，近L只夹T_S；绝不画连接双掌的第三杆，不保留旧轴双影，不换手端/偶端。T_H夹点约({newaxes[0]['pin'][0]:.1f},{newaxes[0]['pin'][1]:.1f})，T_S夹点约({newaxes[1]['pin'][0]:.1f},{newaxes[1]['pin'][1]:.1f})，掌前X约({newX[0]:.1f},{newX[1]:.1f})，T_S是X处前层，R不夹第二杆。
完整头颈、躯干、双臂掌腕、整裙和两T杆白域新绘，完整真实露出腿鞋黑域原位固定。隐蔽腿根过渡在整裙白域内，整裙自然遮住完整腿根，不按施工mask机械裁轮廓，不横截膝踝鞋。奶奶、原C杆、相机、光照与足底支撑固定；灯光由场景接入，不画死在人物纹理。输出1672×941透明全图，同画布，不加背景/地影/字/骨架/额外帧。如只整体构图漂移，先将完整新上身、头颈、双臂掌腕、整裙和两T杆统一相似注册后自然接回固定下肢，不分别挪掌杆。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F090_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_084_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png']
rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r['path'] for r in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F090_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':90,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'later_states_prepared':False,'source084_commit':'2c7142b2129bf0bff3b55295d2b067f6f237008c','source084_final_file':str(source),'source084_sha256':sha(source),'source084_corrected_upper_sha256':sha(F/'source084_corrected_complete_upper_head_skirt_T.png'),'target_method':'construction-only native084 two independent rigid complete palm+own shaft groups and continuous actual bone-chain/torso/head pose reference; not newly generated native art','source_actual_joint_locations_are_image_reference_not_3D_bone_certification':True,'bone_reference':bones,'T_rods':newaxes,'source_X':oldX.tolist(),'target_X':newX,'T_S_foreground_at_X':True,'native_old_shaft_pixels_removed_before_new_complete_two_role_layers':True,'old_hidden_shaft_cross_sections_reconstructed_from_each_own084_shaft_30px_away':True,'head_uniform_scale':1.,'head_torso_rebound_rotation_deg':-1.5,'head_translation_xy':headshift.tolist(),'head_source':'passed corrected084 complete own head-neck volume','fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_RGBA_changes':0,'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'visible_complete_legs_shoes_all_black':True,'natural_skirt_occlusion_no_naked_leg_horizontal_cut':True,'inputs':rows,'three_state_compare_crop_fixed':list(comparebox),'three_state_order':['079 passed','084 passed','090 construction target'],'three_state_individual_alignment_applied':False}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'calls':0,'X':newX,'pins':[q['pin'] for q in newaxes],'four_input_sha256':[q['sha256'] for q in rows]},ensure_ascii=False))
