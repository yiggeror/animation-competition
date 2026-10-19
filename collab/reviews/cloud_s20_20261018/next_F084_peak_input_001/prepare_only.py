"""F079 pose construction references only; zero image calls/exposure choices."""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,binary_closing,distance_transform_edt

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
S=P/'F079_head_neck_scale_close_zero_call_001';source=S/'F079_own_head_neck_volume_closed_candidate.png';nativeS=P/'next_F079_fixed_lower_input_001/generation_001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='2a2fbbee3aaff0b6289b4bb8df756193fe70e37ab9a552af8192c13e459930af'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
Uorig=np.array(Image.open(nativeS/'registered_complete_new_upper_whole_skirt_both_T.png').convert('RGBA'))
oldhead=np.array(Image.open(S/'source_complete_head_neck_semantic_mask.png').convert('L'))>0
newhead=np.array(Image.open(S/'079_own_head_hair_neck_one_continuous_scale.png').convert('RGBA'))
body=(Uorig[:,:,3]>0)&~oldhead;rest=Uorig.copy();rest[oldhead]=0
U0=np.array(Image.alpha_composite(Image.fromarray(rest),Image.fromarray(newhead)));U0[body]=Uorig[body]
Image.fromarray(U0).save(F/'source079_corrected_complete_upper_head_skirt_T.png')
visible_head=(newhead[:,:,3]>120)&~body

previous=json.loads((P/'next_F079_fixed_lower_input_001/INPUT_MANIFEST.json').read_text())
for key,name in [('fixed_complete_lower_file','fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png'),('original_C_rods_layer','fixed_original_C_rods_scene_layer.png')]:
 shutil.copyfile(previous[key],F/name)
lowerfile=F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png';lower=np.array(Image.open(lowerfile).convert('RGBA'))
clayer=F/'fixed_original_C_rods_scene_layer.png';C=np.array(Image.open(clayer).convert('RGBA'))
assert sha(lowerfile)==previous['fixed_complete_lower_sha256'] and sha(clayer)==previous['original_C_rods_sha256']

# Actual native shaft fits outside the hands, then a tiny continuation. The
# complete native upper INCLUDING both rods is moved in one reference field;
# no old shaft is left underneath an independently drawn replacement shaft.
r,g,b=U0[:,:,:3].astype(float).transpose(2,0,1)
wood=(U0[:,:,3]>150)&(r>100)&(g>65)&(r>g+8)&(b<g*.78)
def fit(xmin,xmax,ymin,ymax):
 pts=[]
 for x in range(xmin,xmax):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>=ymin)&(np.arange(H)<ymax))
  if len(ys):pts.append([x,float(np.median(ys))])
 pts=np.array(pts);return np.polyfit(pts[:,0],pts[:,1],1)
hm,hb=fit(290,356,420,500);sm,sb=fit(270,356,320,401)
cx=(sb-hb)/(hm-sm);oldcross=np.array([cx,hm*cx+hb])
oldpins=[np.array([389.,hm*389+hb]),np.array([464.,sm*464+sb])]
oldfronts=[np.array([268.,hm*268+hb]),np.array([250.,sm*250+sb])]
def rot(deg):
 a=math.radians(deg);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
# Preserve the complete overlapping native palms and T shafts as ONE rigid
# group; solve the two real arm chains to its new wrist positions.
pair_pivot=np.array([430.,424.]);pair_shift=np.array([20.,0.]);pair_rot=rot(12.)
def pair_map(point):return pair_pivot+pair_shift+pair_rot@(point-pair_pivot)
def elbow_for(shoulder,wrist,l1,l2):
 v=wrist-shoulder;distance=np.linalg.norm(v);unit=v/distance
 along=(l1*l1-l2*l2+distance*distance)/(2*distance);height=math.sqrt(max(0.,l1*l1-along*along))
 mid=shoulder+along*unit;perp=np.array([-unit[1],unit[0]])
 candidates=[mid+height*perp,mid-height*perp];return max(candidates,key=lambda q:q[1])
body=[];bones=[];handmaps=[]
for side,shoulder,elbow,wrist,shoulder_delta in [
 ('R',[568,382],[508,433],[463,410],[2,-5]),
 ('L',[673,396],[609,496],[514,478],[3,4])]:
 shoulder=np.array(shoulder,float);elbow=np.array(elbow,float);wrist=np.array(wrist,float)
 ns=shoulder+shoulder_delta;nw=pair_map(wrist);l1=np.linalg.norm(elbow-shoulder);l2=np.linalg.norm(wrist-elbow);ne=elbow_for(ns,nw,l1,l2)
 body.extend([(shoulder,ns-shoulder),(elbow,ne-elbow),(wrist,nw-wrist)])
 handmaps.append((pair_pivot,pair_pivot+pair_shift,pair_rot))
 def angle(v):return math.degrees(math.atan2(v[1],v[0]))
 upper_angle=angle(ne-ns)-angle(elbow-shoulder);fore_angle=angle(nw-ne)-angle(wrist-elbow)
 bones.append({'side':side,'upper_rotation_deg':upper_angle,'forearm_rotation_deg':fore_angle,'hand_rotation_deg':12.,'wrist_relative_rotation_deg':12.-fore_angle,'source_shoulder_elbow_wrist':[shoulder.tolist(),elbow.tolist(),wrist.tolist()],'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],'upper_bone_lengths_px':[float(l1),float(np.linalg.norm(ne-ns))],'forearm_bone_lengths_px':[float(l2),float(np.linalg.norm(nw-ne))]})
newpins=[pair_map(q) for q in oldpins];newfronts=[pair_map(q) for q in oldfronts]
tdat=[]
for role,owner,front,pin in zip(['T_H','T_S'],['X.R','X.L'],newfronts,newpins):
 m=(pin[1]-front[1])/(pin[0]-front[0]);bb=pin[1]-m*pin[0];tdat.append({'role':role,'owner':owner,'front':front.tolist(),'pin':pin.tolist(),'slope':float(m),'intercept':float(bb)})
nx=(tdat[1]['intercept']-tdat[0]['intercept'])/(tdat[0]['slope']-tdat[1]['slope']);newcross=np.array([nx,tdat[0]['slope']*nx+tdat[0]['intercept']])
controls=list(body)
for index,points in [(0,[[401,396],[418,412]]),(1,[[474,480],[496,488]])]:
 e,ne,rr=handmaps[index]
 for point in points:
  point=np.array(point,float);controls.append((point,ne+rr@(point-e)-point))
for p,d in [([621,365],[-2,1]),([650,420],[1,2]),([621,490],[4,0]),([706,477],[0,4]),([671,550],[-1,0]),([688,604],[-.5,0])]:
 controls.append((np.array(p,float),np.array(d,float)))
# Keep the approved 079 head volume: rigid -2 degree counter-turn only.
head_pivot=np.array([628.,365.]);head_rot=rot(-2.);head_shift=np.array([-2.,0.])
for py in range(145,390,14):
 for px in range(495,785,14):
  if visible_head[py,px] and not (590<=px<=676 and py>=330):
   point=np.array([px,py],float);controls.append((point,head_pivot+head_rot@(point-head_pivot)+head_shift-point))
for point in [[570,333],[586,337],[610,330],[730,365]]:
 point=np.array(point,float)
 if visible_head[int(point[1]),int(point[0])]:controls.append((point,head_pivot+head_rot@(point-head_pivot)+head_shift-point))
for p in [[565,657],[594,679],[620,684],[650,680],[690,685],[735,678],[791,658],[831,628],[235,125],[865,125],[235,740],[865,740]]:
 controls.append((np.array(p,float),np.zeros(2)))
# Every sampled shaft point remains on its ONE new straight axis. Both source
# intersections map to the same new X, preserving hand/shaft ownership.
for index,(m,bb) in enumerate([(hm,hb),(sm,sb)]):
 front=oldfronts[index];pin=oldpins[index]
 for px in sorted(set([front[0],oldcross[0],pin[0],pin[0]+12]+list(np.arange(front[0]+18,pin[0],25)))):
  point=np.array([px,m*px+bb]);controls.append((point,pair_map(point)-point))
# Dense controls preserve all native finger and overlap contours. These are
# the ACTUAL palm/wrist ownership boundaries, not points inside the palm.
pair_domain=(xx<465)|((yy>=410)&(yy<445)&(xx<466+.8*(yy-410)))|((yy>=445)&(xx<515))
for py in range(315,532,8):
 for px in range(245,516,8):
  if pair_domain[py,px] and U0[py,px,3]>80:
   point=np.array([px,py],float);controls.append((point,pair_map(point)-point))
# Deduplicate the identical X control introduced by the two fitted axes.
unique={}
for p,d in controls:unique[tuple(np.round(p,6))]=(p,d)
controls=list(unique.values());rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=235,125,865,740;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4];field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((h,w));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
crop=U0[y0:y1,x0:x1];a=crop[:,:,3].astype(float)/255;pm=crop[:,:,:3].astype(float)*a[:,:,None];wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
out=np.zeros_like(crop);out[:,:,3]=np.rint(wa*255).astype('uint8');out[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8');U=np.zeros_like(A);U[y0:y1,x0:x1]=out;U[:,:,3][U[:,:,3]<4]=0
skirt_roi=(xx>=645)&(xx<=655)&(yy>=640)&(yy<700);solid=binary_closing(U[:,:,3]>0,iterations=2)&skirt_roi;seam=solid&(U[:,:,3]==0);_,nearest=distance_transform_edt(~((U[:,:,3]>200)&skirt_roi),return_indices=True);U[seam,:3]=U[nearest[0][seam],nearest[1][seam],:3];U[seam,3]=255
Image.fromarray(U).save(F/'new_complete_upper_skirt_both_T_CONSTRUCTION_ONLY.png')
Cpart=C.copy();Cpart[:,850:]=0;G=A.copy();G[:,:850]=0
target=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(U));T=np.array(target)
existing=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650);T[existing]=A[existing]
noise=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8);T[noise]=A[noise]
gmask=(xx>=860)&(A[:,:,3]>0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F084_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
contact=bg.crop((245,310,740,550)).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((1485,720),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png');bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
visible=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850);white=binary_dilation((U0[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<850);white[visible]=False;white[gmask]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png');Image.fromarray(np.uint8(visible)*255).save(F/'actual_retained_visible_complete_legs_shoes_mask.png')
rootbox=(570,640,785,755);card=Image.new('RGB',(430,115),'#bdc1c4');card.paste(bg.crop(rootbox).convert('RGB'),(0,0));card.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(215,0));card.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');d=ImageDraw.Draw(card);d.text((16,12),'079已过身份衣料局部：无旧整身/拳姿；完整下肢另层固定',font=font,fill='#263743')
for box,xy,size in [((505,140,770,390),(20,60),(318,300)),((535,345,730,430),(350,60),(320,140)),((615,530,800,655),(700,60),(300,203)),((490,835,755,935),(350,350),(530,200))]:
 im=Image.fromarray(A).crop(box);cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);card.paste(cb.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,585),'整裙白域，裸露完整腿鞋黑域；腿根层仅真实皮肤/腿鞋',font=font,fill='#263743');card.save(I/'03_079_identity_head_clothes_shoes_patches_only.png')
support=(yy>=760)&(xx<850)&(A[:,:,3]>0);cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support]) and np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[cm],A[cm]);assert not np.any(white[visible]) and not np.any(white[736:]);assert nx<min(q['pin'][0] for q in tdat)
angle=math.degrees(abs(math.atan(tdat[1]['slope'])-math.atan(tdat[0]['slope'])))
prompt=f'''仅绘K02/F084明确峰姿候选白域，未安排曝光。本态必须与076外伸、079减速收势有明确完整骨链差别：远R肩抬、肘部向身侧内收，腕部蓄力；近L上臂更趋垂直、前臂趋平，双腕相对各自前臂拧转。完整双掌和硬签组向身侧收卷，保留原生手指和前后遮挡。胸腰、肩带与完整头颈配合蓄力，保留之后反向回拧空间；不只挪掌几像素、改衣纹或单转两杆，也不无限拉大交角。不要提前翻肚或把一图长持到翻肚。
第一图是唯一完整同姿目标，头颈、躯干、两条完整手臂掌腕、整裙及两T杆都是新绘域，完整真实支撑下肢原位保留。第二图同姿双掌/X，第三图仅刚通过079正确头颈/衣料/鞋局部，第四图真实白黑mask。头体量严格按正确079与076基线，不逐态放大；保原生脸/表情、马尾红花和完整颈根，白领自然连续。两臂分开不互绕，上臂和前臂真实骨长不拉伸，远臂仍自然屈肘。
R只夹T_H约({newpins[0][0]:.1f},{newpins[0][1]:.1f})；L只夹T_S约({newpins[1][0]:.1f},{newpins[1][1]:.1f})。硬直杆在掌前成X约({nx:.1f},{newcross[1]:.1f})，T_S在前经过远卷指，远R不夹第二杆，不换手端或偶端。白域覆盖完整头颈躯干/双臂掌腕/整裙/T杆及必要隐蔽根部重叠，裸露整腿鞋黑；锁住原足底支持、奶奶和原C杆，不重抽、不移动、不横截膝踝鞋。整裙自然遮在完整腿根前，不能机械裁成施工轮廓。输出1672×941透明全图，同画布，不加背景、地影、字、骨架或额外帧，光由场景接入。若仅整体构图漂移，先把完整新上身/整裙/T杆统一相似注册再自然接回固定下肢，另交实际终门。'''

(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n');names=['01_unique_complete_F084_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_079_identity_head_clothes_shoes_patches_only.png','04_complete_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
m={'status':'F084_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':84,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'source079_commit':'4848cab5e41b6b4d0c8e7ad223865f192eade7a6','source079_final_file':str(source),'source079_sha256':sha(source),'source_upper_component_sha256':sha(F/'source079_corrected_complete_upper_head_skirt_T.png'),'target_method':'construction-only continuous complete upper/skirt/T pose reference; native final art not generated','controls':[[p.tolist(),d.tolist()] for p,d in controls],'bone_reference':bones,'T_rods':tdat,'source_X':oldcross.tolist(),'target_X':newcross.tolist(),'target_X_angle_degrees':angle,'fixed_complete_lower_file':str(lowerfile),'fixed_complete_lower_sha256':sha(lowerfile),'fixed_lower_RGBA_changes':0,'original_C_rods_layer':str(clayer),'original_C_rods_sha256':sha(clayer),'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'actual_visible_original_C_RGBA_changes':0,'visible_complete_legs_shoes_all_black':True,'natural_skirt_occlusion_no_naked_leg_horizontal_cut':True,'inputs':rows}
compare_box=(235,125,865,720);three=Image.new('RGB',(1890,595),'#bdc1c4')
state_paths=[P/'next_F076_fixed_lower_input_001/generation_001/F076_uniform_registered_upper_fixed_full_lower_candidate.png',source,I/'01_unique_complete_F084_target_REVIEW_ONLY.png']
for index,path in enumerate(state_paths):
 im=Image.open(path).convert('RGBA');cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);three.paste(cb.crop(compare_box).convert('RGB'),(630*index,0))
three.save(F/'076_passed_079_passed_084_target_same_canvas_upper_hands_1x.png')
m['three_state_compare_crop_fixed']=list(compare_box);m['three_state_order']=['076 passed','079 corrected passed','084 target'];m['three_state_individual_alignment_applied']=False
m['head_reference']='passed corrected079, rigid -2 degree counter-turn with scale1; no head enlargement';m['head_requested_uniform_scale']=1.;m['head_counter_rotation_deg']=-2.
m['peak_bone_chain_sentence']='远肩抬起、远肘向身侧内收，近上臂更趋垂直而前臂趋平，完整骨链蓄力配合头胸腰形成峰姿，腕部保留反向余量。';m['palm_T_group_rigid_rotation_deg']=12.;m['palm_T_group_translation_xy']=[20.,0.]
(F/'INPUT_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'new_calls':0,'X':newcross.tolist(),'angle':angle,'pins':[q['pin'] for q in tdat],'bones':bones},ensure_ascii=False))
