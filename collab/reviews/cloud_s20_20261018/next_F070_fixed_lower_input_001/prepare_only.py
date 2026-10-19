"""F070 upper/whole-skirt input with an independent fixed full lower layer."""
from pathlib import Path
import json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation,median_filter

F=Path(__file__).resolve().parent;P=F.parent;I=F/'inputs';I.mkdir(parents=True,exist_ok=True)
source=P/'F067_near_leg_support_root_zero_call_001/F067_near_support_and_root_closed_candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='80a84871aaaa4eddd621e457fa4dae0b95494332d788119ae650ff85356e1dd8'
A=np.array(Image.open(source).convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W));r,g,b=A[:,:,:3].astype(float).transpose(2,0,1)
yellow=(A[:,:,3]>120)&(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(yy>630)&(yy<710)
hem=np.full(W,np.nan)
for x in range(540,835):
    ys=np.flatnonzero(yellow[:,x])
    if not len(ys):continue
    last=int(ys.max());q=np.arange(last,min(last+5,H));edge=int(q[np.argmin(r[q,x]+g[q,x]+b[q,x])])
    if edge+1<H and r[edge+1,x]<180 and b[edge+1,x]<g[edge+1,x]*.65:edge+=1
    hem[x]=edge
ok=np.isfinite(hem);hem=np.interp(np.arange(W),np.flatnonzero(ok),hem[ok]);med=median_filter(hem,size=7);hem[hem-med>=4]=med[hem-med>=4]
flesh=(r>170)&(g>100)&(b>g*.65)&(r>g+15)
garment=(yy>=650)&(yy<=hem[xx])&(xx<835)&(A[:,:,3]>4)&~flesh
visible_lower=(yy>=650)&(xx<835)&(A[:,:,3]>0)&~garment

# Actual passed067 full legs/shoes are retained independently. Near hidden root
# is the already approved component; the far hidden matte uses its own skin,
# never old shoes at new ankles. All visible source lower pixels are restored.
near=np.array(Image.open(P/'F067_near_leg_support_root_zero_call_001/067_registered_near_leg_with_proximal_connection.png').convert('RGBA'))
far_shape=Image.new('L',(W,H));ImageDraw.Draw(far_shape).polygon([(590,650),(654,650),(657,706),(655,760),(648,800),(638,838),(647,865),(647,895),(642,914),(594,935),(490,935),(490,881),(565,850),(580,827),(585,780),(590,725)],fill=255)
physical_lower=(np.array(far_shape)>0)|(near[:,:,3]>0)
visible_lower&=physical_lower
farcap=np.zeros_like(A);src_y=705;lo,hi=594,644
for y in range(650,706):
    left=594+.08*(y-705);right=650+.015*(y-705)
    for x in range(int(math.floor(left)),int(math.ceil(right))+1):
        u=np.clip((x-left)/(right-left),0,1);sx=lo+u*(hi-lo)
        farcap[y,x,:3]=[int(round(np.interp(sx,np.arange(W),A[src_y,:,c]))) for c in range(3)];farcap[y,x,3]=255
lower=np.array(Image.alpha_composite(Image.fromarray(farcap),Image.fromarray(near)))
lower[visible_lower]=A[visible_lower];lower[:,835:]=0
Image.fromarray(lower).save(F/'fixed_complete_lower_067_roots_legs_shoes.png')
Image.fromarray(np.uint8(visible_lower)*255).save(F/'source067_actual_visible_lower_reference_mask.png')

# Upper source is the passed drawing's head/torso/arms/whole skirt and T rods.
# Lower body is excluded as one semantic layer, not cropped at knees/ankles.
upper=np.array(Image.open(P/'next_F067_candidate_input_001/generation_001/native_complete_child_and_T_rods.png').convert('RGBA'))
upper[650:]=0;upper[garment]=A[garment];upper[:,:425]=0
controls=[([440,396],[-5,-3]),([455,400],[-5,-3]),([496,410],[-4,-3]),([539,430],[-2,-2]),([559,397],[-2,0]),([475,437],[4,3]),([501,455],[4,3]),([524,455],[4,3]),([625,478],[2,2]),([662,415],[-2,1]),([628,414],[-2,1]),([646,481],[-1,1]),([650,618],[-1,1]),([622,154],[-2,1]),([578,197],[-2,1]),([569,286],[-2,1]),([710,320],[-2,1]),([632,367],[-2,1]),([560,667],[0,0]),([600,683],[0,0]),([640,688],[0,0]),([680,686],[0,0]),([730,676],[0,0]),([780,650],[0,0]),([415,135],[0,0]),([835,135],[0,0]),([415,720],[0,0]),([835,720],[0,0])]
rbf=RBFInterpolator(np.array([q[0] for q in controls],float),np.array([q[1] for q in controls],float),kernel='thin_plate_spline',degree=1,smoothing=0)
x0,y0,x1,y1=415,135,835,720;ch,cw=y1-y0,x1-x0;gy,gx=np.mgrid[0:ch:4,0:cw:4];field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,));dy,dx=np.indices((ch,cw));sy=dy.astype(float);sx=dx.astype(float)
for _ in range(7):
    vx=map_coordinates(field[:,:,0],[sy/4,sx/4],order=3,mode='nearest');vy=map_coordinates(field[:,:,1],[sy/4,sx/4],order=3,mode='nearest');sx=dx-vx;sy=dy-vy
c=upper[y0:y1,x0:x1];a=c[:,:,3].astype(float)/255;pm=c[:,:,:3].astype(float)*a[:,:,None]
wa=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0).clip(0,1);wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
new=np.zeros_like(c);new[:,:,3]=np.rint(wa*255).astype('uint8');new[:,:,:3]=np.rint(np.divide(wc,wa[:,:,None],out=np.zeros_like(wc),where=wa[:,:,None]>1e-6)).clip(0,255).astype('uint8')
new_upper=np.zeros_like(A);new_upper[y0:y1,x0:x1]=new;new_upper[:,:,3][new_upper[:,:,3]<4]=0
Image.fromarray(new_upper).save(F/'new_upper_whole_skirt_construction_only.png')

props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props)
def rod(draw,ends):
    pts=[tuple(v*4 for v in p) for p in ends];draw.line(pts,fill='#675034',width=16);draw.line(pts,fill='#b28b52',width=10)
axes=json.loads((P/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
for role in ['C_N','C_B']:
    q=axes[role];rod(d,[q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]])
tdat=[]
for role,front,pin in [('T_H',[323,480],[435,393]),('T_S',[301,317],[479,440])]:
    m=(pin[1]-front[1])/(pin[0]-front[0]);b0=pin[1]-m*pin[0];tail=[pin[0]+20,m*(pin[0]+20)+b0];rod(d,[front,tail]);tdat.append({'role':role,'owner':'X.R' if role=='T_H' else 'X.L','front':front,'pin':pin,'tail':tail,'slope':m,'intercept':b0})
G=A.copy();G[:,:835]=0
target=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));target=Image.alpha_composite(target,Image.fromarray(lower));target=Image.alpha_composite(target,Image.fromarray(new_upper))
q=tdat[1];over=Image.new('RGBA',(W*4,H*4));rod(ImageDraw.Draw(over),[[425,q['slope']*425+q['intercept']],[465,q['slope']*465+q['intercept']]])
target=Image.alpha_composite(target,over.resize((W,H),Image.Resampling.LANCZOS));T=np.array(target);T[:,835:]=A[:,835:];T[736:]=A[736:]
Image.fromarray(T).save(I/'01_unique_complete_F070_fixed_lower_target_REVIEW_ONLY.png')
box=(280,295,735,545);contact_bg=Image.new('RGBA',(W,H),'#bdc1c4');contact_bg.alpha_composite(Image.fromarray(T));contact_bg.crop(box).convert('RGB').resize((1365,750),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_clamps_X_3x.png')

# The mask follows the real skirt occlusion. Every target-visible leg/shoe is
# black; white is only the new upper, WHOLE skirt, shafts and hidden overlap.
visible_fixed=(lower[:,:,3]>0)&(new_upper[:,:,3]==0)&(yy>=650)&(xx<835)
white=binary_dilation((upper[:,:,3]>0)|(new_upper[:,:,3]>0),iterations=8)&(xx<835)
white|=(xx>280)&(xx<550)&(yy>295)&(yy<500)
white[visible_fixed]=False;white[:,835:]=False
Image.fromarray(np.uint8(white)*255).convert('RGB').save(I/'04_new_upper_whole_skirt_white_full_legs_black_mask.png')
Image.fromarray(np.uint8(visible_fixed)*255).save(F/'actual_retained_visible_whole_legs_and_shoes_mask.png')
font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),20);card=Image.new('RGB',(1080,640),'#e7ebee');cd=ImageDraw.Draw(card)
cd.text((16,12),'067已过身份局部：头颈/服鞋；完整支撑下肢另层固定，无旧整身/拳姿',font=font,fill='#263743')
for b1,xy,size in [((515,140,765,390),(20,60),(300,300)),((550,340,725,425),(350,60),(320,155)),((615,535,790,660),(700,60),(300,214)),((490,835,755,935),(350,350),(530,200))]:
    im=Image.fromarray(A).crop(b1);bg=Image.new('RGBA',im.size,'#bdc1c4');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
cd.text((20,585),'下肢从隐蔽根部至双鞋整层保留；不是旧鞋接新踝，裸露腿鞋均黑域',font=font,fill='#263743');card.save(I/'03_067_identity_head_clothes_shoes_patches_only.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(T));bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
bg.crop(box).convert('RGB').save(F/'contacts_1x_REVIEW_ONLY.png');bg.crop((480,800,795,935)).convert('RGB').save(F/'fixed_support_1x_REVIEW_ONLY.png')
rootbox=(575,650,770,750);root=Image.new('RGB',(390,100),'#bdc1c4');root.paste(bg.crop(rootbox).convert('RGB'),(0,0));root.paste(Image.fromarray(np.uint8(white)*255).convert('RGB').crop(rootbox),(195,0));root.save(F/'under_hem_target_left_mask_right_boundary_1x.png')
q1,q2=tdat;cx=(q2['intercept']-q1['intercept'])/(q1['slope']-q2['slope']);cross=[cx,q1['slope']*cx+q1['intercept']];angle=math.degrees(abs(math.atan(q2['slope'])-math.atan(q1['slope'])))
assert np.array_equal(T[736:],A[736:]);assert np.array_equal(T[:,835:],A[:,835:]);assert np.array_equal(lower[visible_lower],A[visible_lower]);assert not np.any(white[visible_fixed]);assert not np.any(white[736:]);assert cx<min(q1['pin'][0],q2['pin'][0])
prompt='''仅绘F070候选白域，未冻结曝光。第一图是唯一完整新动作target，同时展示新头胸双臂整裙和独立固定的067完整支撑下肢；第二图为同姿双掌/X，第三图仅067头颈服鞋局部，第四图白绘黑保。裸露完整腿鞋为黑域：从裙下隐蔽根部、整腿到双鞋原层保留，实际足支持/地线不动，不重抽腿鞋，不把旧鞋接新脚踝，也不在裸露腿上设水平切口。
仍在058–077首次绞签窗，延续064→067方向：肩肘带腕相对转动，远R左上、近L右下，头颈胸盆协调微前探。只自然新绘完整头颈、躯干、双臂掌腕、整条裙及必要隐藏根部重叠，保两前臂各自连续、真实骨长；不重复067只转两杆，不跳084峰。黄裙在固定腿根前遮挡，腕皮肤连续、无闭合腕环；原生一拇四指，不贴旧拳。
R只夹T_H约(435,393)，前端(323,480)；L只夹T_S约(479,440)，前端(301,317)。双掌前硬杆X继续推进，T_S在前；它经过远卷指仅是遮挡，远R不能夹第二杆，不换端点、不弯杆加杆。白圆领、密集乳白点黄泡袖裙和肤色按067实物；衣鞋小块不供旧整身姿势。奶奶锁047黑域不动。输出1672×941透明全图，同画布，不裁缩、不加背景/地影/字/骨架或额外帧；场景光后接。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n');paths=[I/n for n in ['01_unique_complete_F070_fixed_lower_target_REVIEW_ONLY.png','02_same_pose_dual_clamps_X_3x.png','03_067_identity_head_clothes_shoes_patches_only.png','04_new_upper_whole_skirt_white_full_legs_black_mask.png']]
rows=[{'order':i+1,'path':str(p.resolve()),'sha256':sha(p),'size':list(Image.open(p).size)} for i,p in enumerate(paths)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({'prompt':prompt,'transparent_background':True,'referenced_image_paths':[r1['path'] for r1 in rows]},ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F070_FIXED_FULL_LOWER_AND_NEW_UPPER_WHOLE_SKIRT_INPUT_ASTRA_GATE_PENDING','frame_label':70,'new_image_calls':0,'submitted':False,'generation_authorized':False,'frozen_exposure':False,'source067_final_file':str(source),'source067_sha256':sha(source),'fixed_full_lower_layer':str(F/'fixed_complete_lower_067_roots_legs_shoes.png'),'fixed_lower_sha256':sha(F/'fixed_complete_lower_067_roots_legs_shoes.png'),'visible_lower_source_pixels_RGBA_exact':True,'target_all_y736_plus_support_RGBA_exact':True,'all_target_visible_legs_shoes_mask_black':True,'new_white_domain':'head neck torso both full arms hands whole skirt T rods and hidden root overlap only','natural_occlusion_boundary_no_exposed_horizontal_cut':True,'far_hidden_root_matte':'same far-leg skin continued behind skirt only; visible lower source pixels restored exact','near_hidden_root_source':'already approved full native near-leg component from fb7cc408','target_upper_method':'construction-only continuous upper/whole-skirt field; retained lower never warped','controls':controls,'T_rods':tdat,'X_master':cross,'X_angle_degrees':angle,'inputs':rows,'unchanged_cues_seconds':{'entangle':[2.4,4.6],'flip':5.5,'cut':6.0}}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'candidate':70,'X':cross,'angle':angle,'calls':0,'support_pixels_changed':0,'bare_legs_white_mask_pixels':int(np.count_nonzero(white&visible_fixed))},ensure_ascii=False))
