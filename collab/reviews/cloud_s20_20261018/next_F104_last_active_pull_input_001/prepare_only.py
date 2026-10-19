"""One F104 active final tug construction from terminal-approved single-grip096."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import map_coordinates,binary_dilation,binary_opening,binary_fill_holes,label
from scipy.interpolate import RBFInterpolator
F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
S=P/'F096_far_R_single_TH_contact_input_001/local_generation_001';source=S/'F096_R_single_TH_native_local_candidate.png'
assert sha(source)=='be1d3ccec0939b22203fa6ad00bb7773049694d3506f3113f47810220889430d'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
# Reconcile the APPROVED local R hand into the older complete upper layer.
# Never derive this target from the wrong double-grip native096 hand.
U0=np.array(Image.open(P/'next_F096_active_pull_input_001/generation_001/registered_complete_new_upper_whole_skirt_two_T.png').convert('RGBA'))
repaired=np.array(Image.open(S/'actual_complete_R_palm_short_wrist_rejoin_domain.png').convert('L'))>0
U0[repaired]=A[repaired]
Image.fromarray(U0).save(F/'source096_adopted_complete_upper_head_skirt_two_T.png')
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png','fixed_original_C_rods_scene_layer.png']:
 shutil.copyfile(P/'next_F096_active_pull_input_001'/name,F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';clayer=F/'fixed_original_C_rods_scene_layer.png'
assert sha(lowerfile)=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(clayer)=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'
lower=np.array(Image.open(lowerfile).convert('RGBA'));C=np.array(Image.open(clayer).convert('RGBA'))
def rot(deg):
 t=math.radians(deg);return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def polygon(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
axes=json.loads((P/'F096_far_R_single_TH_contact_input_001/fixed_axes_and_contact.json').read_text())
X=np.array(axes['fixed_X']);pinR=np.array(axes['new_R_TH_grip']);pairrot=rot(6.);pairshift=np.array([-20.,0.])
pair=lambda p:X+pairshift+pairrot@(np.array(p,float)-X)
hm,hb=axes['T_H_axis_slope_intercept'];sm,sb=axes['T_S_axis_slope_intercept']
oldpins=[pinR,np.array([481.,sm*481+sb])];oldfronts=[np.array([259.,hm*259+hb]),np.array([291.,sm*291+sb])]
newpins=[pair(p) for p in oldpins];newfronts=[pair(p) for p in oldfronts];newX=pair(X)
def elbow_for(s,w,l1,l2):
 v=w-s;d=np.linalg.norm(v);assert abs(l1-l2)<d<l1+l2
 u=v/d;along=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(l1*l1-along*along);mid=s+along*u;n=np.array([-u[1],u[0]])
 return max([mid+h*n,mid-h*n],key=lambda p:p[1])
controls=[];bones=[]
for side,s,e,w,ds in [('R',[551,393],[489,414],[465,407],[-24,-3]),('L',[690,402],[689,491],[550,491],[-9,-12])]:
 s,e,w,ds=map(lambda p:np.array(p,float),[s,e,w,ds]);ns=s+ds;nw=pair(w);l1=np.linalg.norm(e-s);l2=np.linalg.norm(w-e);ne=elbow_for(ns,nw,l1,l2)
 controls.extend([(s,ns-s),(e,ne-e),(w,nw-w)])
 angle=lambda p:math.degrees(math.atan2(p[1],p[0]));delta=lambda p,q:(angle(p)-angle(q)+180)%360-180
 bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'projected_upper_length_source_target':[float(l1),float(np.linalg.norm(ne-ns))],'projected_forearm_length_source_target':[float(l2),float(np.linalg.norm(nw-ne))],'upper_rotation_deg':delta(ne-ns,e-s),'forearm_rotation_deg':delta(nw-ne,w-e),'whole_palm_rotation_deg':6.})
# Both complete native palms AND both native shafts share one rigid map.
# This preserves the fixed single-grip topology, air and X ordering exactly.
Rcontact=polygon([(390,347),(443,339),(470,368),(472,425),(444,431),(420,427),(396,414),(389,390)])
Lcontact=polygon([(461,451),(501,449),(540,464),(556,480),(556,512),(529,526),(484,525),(464,506)])
rod_masks=[]
for (m,b),front,pin in zip([(hm,hb),(sm,sb)],oldfronts,oldpins):
 v=pin-front;length=np.linalg.norm(v);v/=length;s=(xx-front[0])*v[0]+(yy-front[1])*v[1];distance=abs((xx-front[0])*v[1]-(yy-front[1])*v[0])
 rod_masks.append((distance<8)&(s>=-5)&(s<=length+10))
contact=(Rcontact|Lcontact|rod_masks[0]|rod_masks[1])&(U0[:,:,3]>40)
for py in range(305,533,6):
 for px in range(248,558,6):
  if contact[py,px]:
   p=np.array([px,py],float);controls.append((p,pair(p)-p))
for (m,b),front,pin in zip([(hm,hb),(sm,sb)],oldfronts,oldpins):
 n=np.array([-m,1.]);n/=np.linalg.norm(n)
 for px in np.arange(front[0],pin[0]+5,14):
  for off in [-4.,0.,4.]:
   p=np.array([px,m*px+b])+off*n;controls.append((p,pair(p)-p))
for p,d in [([621,370],[-6,-3]),([650,424],[-13,-4]),([630,497],[-6,2]),([704,481],[-3,-1]),([671,550],[-1,0]),([688,604],[0,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1);alpha=U0[:,:,3]>0
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>555)&(xx<725)&(yy>338)&(yy<411)&alpha
cloth=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(U0[:,:,3]>180)&(yy>334)
guard=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(cloth,iterations=1),iterations=2)
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=binary_dilation(hair&alpha&(xx>655)&(xx<795)&(yy>280)&(yy<405),iterations=2)&alpha&~guard
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha
neck=binary_dilation(skin&(xx>586)&(xx<680)&(yy>327)&(yy<384),iterations=2)&alpha&~guard
head=((alpha&(xx>480)&(xx<795)&(yy<345))|neck|pony)&~guard;head=binary_fill_holes(head)&alpha&~guard
headpivot=np.array([625.,369.]);headrot=rot(1.5);headshift=np.array([-6.,-3.])
for py in range(140,402,12):
 for px in range(490,791,12):
  if head[py,px] and not (590<=px<=684 and py>=330):
   p=np.array([px,py],float);controls.append((p,headpivot+headrot@(p-headpivot)+headshift-p))
# The entire lower skirt and actual natural hem stay supported over fixed roots.
for py in range(630,707,14):
 for px in range(546,922,14):
  if U0[py,px,3]>100:controls.append((np.array([px,py],float),np.zeros(2)))
for p in [[549,630],[594,679],[620,684],[650,680],[690,685],[735,678],[791,680],[846,655],[911,596],[210,110],[965,110],[210,740],[965,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
unique={}
for p,d in controls:unique[tuple(np.round(p,6))]=(p,d)
controls=list(unique.values());rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=210,110,965,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sx=dx.astype(float);sy=dy.astype(float)
for _ in range(10):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=U0[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0);wa=wa0.clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros_like(crop);patch[:,:,3]=np.rint(wa*255).astype('uint8');patch[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8');patch[patch[:,:,3]<3]=0
U=np.zeros_like(A);U[y0:y1,x0:x1]=patch
Image.fromarray(U).save(F/'new_complete_upper_skirt_two_T_CONSTRUCTION_ONLY.png')
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0;oldchild=(U0[:,:,3]>0)&(xx>=850)&(xx<965);G[oldchild]=C[oldchild]
T=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));T=Image.alpha_composite(T,Image.fromarray(lower));T=np.array(Image.alpha_composite(T,Image.fromarray(U)))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);T[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(U[:,:,3]==0);T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F104_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
c=bg.crop((210,285,770,555)).convert('RGB');c.save(F/'contacts_1x_REVIEW_ONLY.png');c.resize((1680,810),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
exposed=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850)
mask=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<965);mask[exposed]=False;mask[gmask]=False
Image.fromarray(np.uint8(mask)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
box=(570,640,785,755);card=Image.new('RGB',(430,115));card.paste(bg.crop(box).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(mask)*255).convert('RGB').crop(box),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');draw=ImageDraw.Draw(card);draw.text((16,12),'096已过身份小块：脸发、衣料、鞋；无旧整姿或旧错误掌',font=font,fill='#263743')
headlayer=np.zeros_like(U0);headlayer[head]=U0[head]
for index,(box,xy,size) in enumerate([((500,145,775,378),(20,60),(330,280)),((570,350,720,440),(370,60),(300,180)),((625,540,815,655),(710,60),(300,182)),((490,835,755,935),(350,350),(530,200))]):
 src=headlayer if index==0 else (U0 if index<3 else A);im=Image.fromarray(src).crop(box);ibg=Image.new('RGBA',im.size,'#bdc1c4');ibg.alpha_composite(im);card.paste(ibg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
card.save(I/'03_096_identity_head_clothes_shoes_patches_only.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4');oldbg.alpha_composite(Image.fromarray(A));box=(210,125,940,720);paircard=Image.new('RGB',(1460,595));paircard.paste(oldbg.crop(box).convert('RGB'),(0,0));paircard.paste(bg.crop(box).convert('RGB'),(730,0));paircard.save(F/'096_left_104_target_right_same_canvas_upper_hands_1x.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[cm],A[cm]) and not np.any(mask[exposed]) and not np.any(mask[736:])
prompt=f'''只绘F104末次主动绞签/收力前蓄势的唯一白域，未安排持帧曝光。本态从已修正确096继续：远肩前送，近肩回提，近肘内收而近腕下带，胸腰反扭，完成向屏左下的末次绞拉；真实肩肘腕分别走自己的自然骨链与空间。不只是平移人物、挪头换衣纹或每三帧几像素微移。仍是096–110主动后段，未进入111后纯被动余摆、125后翻肚。
第一图唯一完整同姿目标，第二图同姿两掌和X，第三图仅正确096脸发/衣料/鞋小块，无旧整姿或旧错掌；第四图完整真实mask。正确096完整头颈体量保持，随胸腰回应，白领颈根连续，不另长大或分挪五官。
直接保持已过096单握拓扑：远R只夹T_H约({newpins[0][0]:.1f},{newpins[0][1]:.1f})，近L只夹T_S约({newpins[1][0]:.1f},{newpins[1][1]:.1f})。真实掌前X约({newX[0]:.1f},{newX[1]:.1f})，T_S在前且处于R拇指卷指夹口之外；R夹口沿T_H与X明确分开40px。两掌两杆随真实拉扯一起动，不用独挪X或缩短T_S假避接触。任何位置只能有两根独立硬直真杆，不加第三杆，不残旧轴或旧掌，不换手端/偶端。
完整上身、双臂掌腕、整头颈、整裙和两T作为一个语义组件原生重绘，露出完整腿鞋黑域固定，隐蔽腿根和整裙白域自然连续。奶奶/C、支持、相机和光照保护。不要硬裁施工轮廓或横截膝踝鞋；不要复刻任何施工变形线。输出1672×941透明完整图，不加背景、字、额外帧。若整组件漂移，只统一相似注册再自然接完整固定腿根，不分挪头、掌或杆。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F104_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_096_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F104_SINGLE_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':104,'new_image_calls':0,'submitted':False,'generation_authorized':False,'later_states_prepared':False,'frozen_exposure':False,'source096_commit':'3d5a6a7e8a2bc188d403abf3922062938be28fc7','source096_file':str(source),'source096_sha256':sha(source),'source096_complete_upper_sha256':sha(F/'source096_adopted_complete_upper_head_skirt_two_T.png'),'approved_local_R_reconciled_into_source_upper':True,'old_double_grip_source_not_reused':True,'target_is_construction_only_not_new_native_art':True,'bone_reference':bones,'projected_lengths_are_image_reference_not_3D_certification':True,'both_complete_palms_and_two_shafts_same_rigid_map':{'rotation_deg':6.,'translation_xy':pairshift.tolist(),'pivot':X.tolist()},'source_X':X.tolist(),'target_X':newX.tolist(),'new_R_pin':newpins[0].tolist(),'new_L_pin':newpins[1].tolist(),'R_pin_X_axial_separation_px':float(np.linalg.norm(newpins[0]-newX)),'T_S_outside_R_clamp_and_X_foreground_topology_retained':True,'head_uniform_scale':1.,'head_rotation_deg':1.5,'head_translation_xy':headshift.tolist(),'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'fixed_lower_RGBA_changes':0,'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'complete_visible_legs_shoes_all_black':True,'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'calls':0,'target_sha256':rows[0]['sha256'],'X':newX.tolist(),'R':newpins[0].tolist(),'L':newpins[1].tolist(),'bones':bones},ensure_ascii=False))
