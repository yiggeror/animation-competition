"""F073 construction references only: 0 image calls, no exposure decision."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,distance_transform_edt,binary_closing

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
S=P/'F070_uniform_registration_zero_call_001';source=S/'F070_uniform_registered_upper_fixed_full_lower_candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='1d12ca876cd3cc9a58aabb3d90c6195e31d15360f8bafaeb44aae81945c4d28a'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
U0=np.array(Image.open(S/'070_complete_new_upper_whole_skirt_both_T_one_similarity.png').convert('RGBA'))
oldlower=P/'next_F070_fixed_lower_input_001/fixed_complete_lower_067_roots_legs_shoes.png'
lower=np.array(Image.open(oldlower).convert('RGBA'))
# Retain the approved proximal cleanup; eliminate any remaining old garment
# ink hidden under the complete 070 skirt. Only same-leg skin RGB changes;
# hidden/visible leg geometry, alpha, knees, ankles and shoes are never moved.
oldpatch=np.array(Image.open(S/'same_far_leg_skin_old_skirt_residue_cleanup_only.png').convert('RGBA'))
oldmask=np.array(Image.open(S/'old_skirt_residue_cleanup_mask.png').convert('L'))>0
lower[oldmask,:3]=oldpatch[oldmask,:3]
r,g,b=lower[:,:,:3].astype(float).transpose(2,0,1)
interior=((xx>=598)&(xx<=646))|((xx>=660)&(xx<=706))
hidden_old_edge=interior&(yy>=683)&(yy<=690)&(lower[:,:,3]>200)&(((r<245)&(g<190))|(b<g*.7))
cy,cx=np.where(hidden_old_edge);lower[cy,cx,:3]=A[700,cx,:3]
# The far hidden-root matte retains an old hem transition at y687. Rebuild
# only its internal skin RGB between two rows of that same far leg; keep its
# silhouette and alpha, and restore passed visible pixels in the target below.
root_skin_matte=(xx>=598)&(xx<=646)&(yy>=680)&(yy<=697)&(lower[:,:,3]>200)
ry,rx=np.where(root_skin_matte);mix=(ry-676)/24
lower[ry,rx,:3]=np.rint(lower[676,rx,:3]*(1-mix[:,None])+A[700,rx,:3]*mix[:,None]).astype('uint8')
Image.fromarray(lower).save(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png')
Image.fromarray(np.uint8(hidden_old_edge)*255).save(F/'hidden_old_skirt_edge_RGB_cleanup_mask.png')

# Remove only exterior old T shafts before the construction field; complete
# human anatomy and clamp interiors remain one continuous reference layer.
upper=U0.copy();r,g,b=upper[:,:,:3].astype(float).transpose(2,0,1)
skin=(upper[:,:,3]>20)&(r>170)&(g>100)&(b>g*.65)&(r>g+15)
guard=binary_dilation(skin,iterations=3)
wood=(upper[:,:,3]>0)&(r>70)&(g>45)&(r>g+6)&(b<g*.8)
remove=((xx<410)|wood)&(xx<550)&(yy>299)&(yy<500)&~guard
upper[remove]=0
controls=[
 ([427,387],[-11,-4]),([445,399],[-10,-4]),([455,417],[-10,-4]),([480,421],[-8,-4]),([536,435],[-5,-2]),([559,394],[-3,0]),
 ([474,446],[7,9]),([500,465],[7,7]),([526,470],[6,6]),([620,484],[3,4]),([661,423],[-1,2]),
 ([620,365],[-2,1]),([650,416],[-3,2]),([630,482],[-1,1]),([704,472],[-1,1]),([671,548],[-1,1]),([688,602],[-1,1]),
 ([620,165],[-2,1]),([553,245],[-2,1]),([572,315],[-2,1]),([706,300],[-2,1]),([740,342],[-2,1]),
 ([565,657],[0,0]),([594,679],[0,0]),([620,685],[0,0]),([650,681],[0,0]),([690,686],[0,0]),([735,680],[0,0]),([791,658],[0,0]),([830,628],[0,0]),
 ([395,135],[0,0]),([850,135],[0,0]),([395,730],[0,0]),([850,730],[0,0])]
points=np.array([q[0] for q in controls],float);delta=np.array([q[1] for q in controls],float)
rbf=RBFInterpolator(points,delta,kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=395,135,850,730;h,w=y1-y0,x1-x0;gy,gx=np.mgrid[0:h:4,0:w:4]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,))
dy,dx=np.indices((h,w));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
 vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
c=upper[y0:y1,x0:x1];alpha=c[:,:,3].astype(float)/255;pm=c[:,:,:3].astype(float)*alpha[:,:,None]
wa=map_coordinates(alpha,[sy,sx],order=3,mode='constant',cval=0).clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
out=np.zeros_like(c);out[:,:,3]=np.rint(wa*255).astype('uint8');out[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8')
U=np.zeros_like(A);U[y0:y1,x0:x1]=out;U[:,:,3][U[:,:,3]<4]=0
# Close the thin technical seam only inside the construction's whole skirt;
# preserve its natural outer hem and make the intended garment continuous.
skirt_roi=(xx>=645)&(xx<=655)&(yy>=640)&(yy<700)
garment_solid=binary_closing(U[:,:,3]>0,iterations=2)&skirt_roi
seam=garment_solid&(U[:,:,3]==0)
_,nearcloth=distance_transform_edt(~((U[:,:,3]>200)&skirt_roi),return_indices=True)
U[seam,:3]=U[nearcloth[0][seam],nearcloth[1][seam],:3];U[seam,3]=255
Image.fromarray(U).save(F/'new_complete_upper_whole_skirt_CONSTRUCTION_ONLY.png')

def rod(draw,ends):
 pts=[tuple(v*4 for v in p) for p in ends];draw.line(pts,fill='#675034',width=16);draw.line(pts,fill='#b28b52',width=10)
axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
C=Image.new('RGBA',(W*4,H*4));cd=ImageDraw.Draw(C)
for role in ['C_N','C_B']:
 q=axes[role];rod(cd,[q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]])
C=C.resize((W,H),Image.Resampling.LANCZOS);C.save(F/'fixed_original_C_rods_scene_layer.png')
Cpart=np.array(C);Cpart[:,835:]=0
G=A.copy();G[:,:835]=0
Tprops=Image.new('RGBA',(W*4,H*4));td=ImageDraw.Draw(Tprops);tdat=[]
for role,front,pin in [('T_H',[305,484],[416,383]),('T_S',[288,333],[481,455])]:
 m=(pin[1]-front[1])/(pin[0]-front[0]);b0=pin[1]-m*pin[0];tail=[pin[0]+20,m*(pin[0]+20)+b0];rod(td,[front,tail]);tdat.append({'role':role,'owner':'X.R' if role=='T_H' else 'X.L','front':front,'pin':pin,'tail':tail,'slope':m,'intercept':b0})
target=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G));target=Image.alpha_composite(target,Tprops.resize((W,H),Image.Resampling.LANCZOS));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(U))
q=tdat[1];overlay=Image.new('RGBA',(W*4,H*4));rod(ImageDraw.Draw(overlay),[[395,q['slope']*395+q['intercept']],[465,q['slope']*465+q['intercept']]])
target=Image.alpha_composite(target,overlay.resize((W,H),Image.Resampling.LANCZOS));T=np.array(target)
existing_visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(U[:,:,3]==0)&(yy>=650)
T[existing_visible]=A[existing_visible]
support_noise=(yy>=736)&(xx<835)&(A[:,:,3]>0)&(A[:,:,3]<=8);T[support_noise]=A[support_noise]
gmask=(xx>=860)&(A[:,:,3]>0);T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F073_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
contact=bg.crop((280,295,740,545)).convert('RGB');contact.save(F/'contacts_1x_REVIEW_ONLY.png');contact.resize((1380,750),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')
support=bg.crop((480,800,795,935)).convert('RGB');support.save(F/'fixed_support_1x_REVIEW_ONLY.png')

# Real full mask follows the natural skirt hem. Visible complete legs/shoes
# are all black; hidden roots behind the whole white skirt may overlap.
visible_fixed=(lower[:,:,3]>0)&(U[:,:,3]==0)&(yy>=650)&(xx<850)
white=binary_dilation((upper[:,:,3]>0)|(U[:,:,3]>0),iterations=8)&(xx<850)
white|=(xx>280)&(xx<550)&(yy>295)&(yy<500)
white[visible_fixed]=False;white[gmask]=False;white[:,850:]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_new_upper_whole_skirt_white_full_legs_black_mask.png')
Image.fromarray(np.uint8(visible_fixed)*255).save(F/'actual_retained_visible_complete_legs_shoes_mask.png')
rootbox=(570,645,780,755);crop=bg.crop(rootbox).convert('RGB');crop.save(F/'under_hem_target_1x_REVIEW_ONLY.png')
boundary=Image.new('RGB',(420,110),'#bdc1c4');boundary.paste(crop,(0,0));boundary.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(210,0));boundary.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
lg=Image.new('RGBA',(W,H),'#bdc1c4');lg.alpha_composite(Image.fromarray(lower));lg.crop((580,645,735,715)).convert('RGB').resize((465,210),Image.Resampling.NEAREST).save(F/'fixed_lower_root_skin_only_3x.png')

font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');d=ImageDraw.Draw(card)
d.text((16,12),'070已过身份局部：头颈/衣料/鞋，无旧整身或拳姿；下肢另层固定',font=font,fill='#263743')
for box,xy,size in [((515,140,770,390),(20,60),(306,300)),((545,345,730,430),(350,60),(320,147)),((615,530,800,655),(700,60),(300,203)),((490,835,755,935),(350,350),(530,200))]:
 im=Image.fromarray(A).crop(box);cb=Image.new('RGBA',im.size,'#bdc1c4');cb.alpha_composite(im);card.paste(cb.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
d.text((20,585),'整裙白域；裸露完整腿鞋黑域；独立腿层仅皮肤/腿鞋/隐蔽根部',font=font,fill='#263743');card.save(I/'03_070_identity_head_clothes_shoes_patches_only.png')
q1,q2=tdat;cx=(q2['intercept']-q1['intercept'])/(q1['slope']-q2['slope']);cross=[cx,q1['slope']*cx+q1['intercept']];angle=math.degrees(abs(math.atan(q2['slope'])-math.atan(q1['slope'])))
supportmask=(yy>=760)&(xx<835)&(A[:,:,3]>0)
assert np.array_equal(T[supportmask],A[supportmask]) and np.array_equal(T[gmask],A[gmask]) and not np.any(white[visible_fixed]) and not np.any(white[736:])
assert cx<min(q1['pin'][0],q2['pin'][0])
prompt='''仅绘F073单态候选白域，未安排曝光。严格采用第一张唯一完整同姿target：新头颈、胸腰、肩肘带动完整双臂掌腕及整裙；固定已过070的完整支撑下肢、奶奶和原C杆。第二张是同姿双掌/X，第三张仅070身份衣料鞋小块，第四张白绘黑保真实mask。不能把技术mask当人体横截线；整裙保持自然完整，遮在独立保留的真实皮肤/完整腿鞋及隐蔽根部前，原足支持/地线不动，不重抽腿鞋。
仍在058–077第一次绞签，沿067→070继续：远R连肩肘掌腕向左上，近L连肩肘掌腕向右下，头颈胸腰协调微前探；两前臂分开连续、骨长自然，不只转杆冻结上身，不反向、不提前跳084峰。R仅夹T_H约(416,383)，其前端(305,484)；L仅夹T_S约(481,455)，前端(288,333)。硬直双杆X在双掌前继续推进，T_S在前；近杆经过远卷指是遮挡，不能让远手夹第二杆。保持原生一拇四指、腕皮肤连续，不拼旧拳或画腕环。
白域为完整新头颈、躯干、两条完整手臂掌腕、整裙、T杆及必要隐蔽根部重叠；裸露完整腿鞋和锁奶奶黑域。服装为070实物白圆领、密集乳白点黄泡袖裙，皮肤/红凉鞋身份按局部小块。输出1672×941透明全图，同画布，不裁缩、不加背景、地影、文字、骨架或额外帧；场景光后接。若仅整体构图漂移，后续先把完整上身整裙和两T杆统一相似注册再交实际终门，不通过移动下肢来接。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F073_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_070_identity_head_clothes_shoes_patches_only.png','04_new_upper_whole_skirt_white_full_legs_black_mask.png'];rows=[{'order':i+1,'path':str((I/n).resolve()),'sha256':sha(I/n),'size':list(Image.open(I/n).size)} for i,n in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[q['path'] for q in rows]},ensure_ascii=False,indent=2)+'\n')
m={'status':'F073_ZERO_CALL_FOUR_INPUTS_ASTRA_GATE_PENDING','frame_label_only':73,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'source070_commit':'e10e2b6532fc45a24ae4e6ab4c3814769bc09cd0','source070_final_file':str(source),'source070_sha256':sha(source),'source_upper_component_sha256':sha(S/'070_complete_new_upper_whole_skirt_both_T_one_similarity.png'),'fixed_complete_lower_file':str(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png'),'fixed_complete_lower_sha256':sha(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png'),'fixed_lower_alpha_geometry_unchanged':True,'passed_proximal_cleanup_pixels':int(oldmask.sum()),'additional_hidden_old_garment_RGB_residue_pixels':int(hidden_old_edge.sum()),'hidden_cleanup_material':'same respective fixed leg skin row700; proximal skin matte only, visible passed070 restored where exposed; no body geometry or leg/shoe transformation','target_upper_method':'construction-only continuous upper/whole-skirt pose field; never final native art','controls':controls,'T_rods':tdat,'X_master':cross,'X_angle_degrees':angle,'both_full_legs_shoes_visible_mask_all_black':True,'actual_support_y760_plus_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,'original_C_rods_layer':str(F/'fixed_original_C_rods_scene_layer.png'),'original_C_rods_sha256':sha(F/'fixed_original_C_rods_scene_layer.png'),'natural_skirt_occlusion_no_naked_leg_horizontal_cut':True,'inputs':rows,'unchanged_cues_seconds':{'entangle':[2.4,4.6],'flip':5.5,'cut':6.0}}
m['far_hidden_root_skin_RGB_matte_cleanup_pixels']=int(root_skin_matte.sum());m['native_far_curled_fingers_preserved']=True
(F/'INPUT_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'frame_label':73,'new_calls':0,'X':cross,'angle':angle,'hidden_old_edge_pixels':int(hidden_old_edge.sum()),'root_skin_RGB_matte_pixels':int(root_skin_matte.sum()),'support_and_grandma_changed':0},ensure_ascii=False))
