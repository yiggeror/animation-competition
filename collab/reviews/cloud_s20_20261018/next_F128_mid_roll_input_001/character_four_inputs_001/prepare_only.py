"""F128: four review inputs, zero image calls; construction is not native art.

Keep the passed finite mechanism separate from character redraw inputs. One
continuous TPS field links head/neck/chest, complete arms and the whole skirt.
"""
from pathlib import Path
import hashlib, json, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import (map_coordinates, binary_dilation, binary_opening,
                           binary_fill_holes, label)
from scipy.interpolate import RBFInterpolator

F=Path(__file__).resolve().parent; P=F.parents[1]
I=F/'inputs'; I.mkdir(parents=True,exist_ok=True)
M=F.parent/'finite_current_branch_scene_001'
GEO=json.loads((M/'candidate_geometry.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=P/'next_F120_passive_decay_input_001'
source=S/'generation_001/F120_uniform_registered_upper_fixed_full_lower_candidate.png'
assert sha(source)=='40d73e42505d5e7c83dc22d33511e5a2e4862dc35b5a4ff210e50eca8ef2bf5c'
A=np.array(Image.open(source).convert('RGBA')); H,W=A.shape[:2]
yy,xx=np.indices((H,W))
upper_source=S/'generation_001/registered_complete_new_upper_whole_skirt_two_T.png'
U0=np.array(Image.open(upper_source).convert('RGBA'))
erase=np.array(Image.open(M/'old_exterior_T_erase_mask.png').convert('L'))>0
Uclean=U0.copy(); Uclean[erase]=0
# Remove only thin outlying C-coloured spill around the hair on this owned
# construction copy. The actual original C layer underneath remains untouched.
# This avoids carrying tiny old rod fragments with the rigidly moving head.
thick=binary_opening(Uclean[:,:,3]>100,iterations=3)
thick_recover=binary_dilation(thick,iterations=3)
hair_spill=(xx>700)&(yy>250)&(yy<390)&(Uclean[:,:,3]>0)&~thick_recover
Uclean[hair_spill]=0
Image.fromarray(Uclean).save(F/'source120_complete_upper_old_exterior_T_cleared_COPY.png')
for name in ['fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png',
             'fixed_original_C_rods_scene_layer.png']:
    shutil.copyfile(S/name,F/name)
lower=np.array(Image.open(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png').convert('RGBA'))
C=np.array(Image.open(F/'fixed_original_C_rods_scene_layer.png').convert('RGBA'))
assert sha(F/'fixed_complete_lower_skin_roots_legs_shoes_no_old_skirt_edge.png')=='da1ef7ce8167179f7268edfe1bd70781551f937a18d33c4a12bc62b17ae8e7c4'
assert sha(F/'fixed_original_C_rods_scene_layer.png')=='47c3ece2f53c7e8b1bea4e3248a65a2518855bc6546f525bf809db62f5ec454e'

def rot(deg):
    t=math.radians(deg)
    return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])

def elbow(s,w,l1,l2,near):
    v=w-s; d=np.linalg.norm(v); assert abs(l1-l2)<d<l1+l2
    u=v/d; c=(l1*l1-l2*l2+d*d)/(2*d)
    h=math.sqrt(l1*l1-c*c); n=np.array([-u[1],u[0]]); mid=s+c*u
    return min([mid+h*n,mid-h*n],key=lambda p:np.linalg.norm(p-near))

controls=[]; bones=[]; palms=[]
for old,ds in zip(GEO['bones'],[[4,-3],[5,-2]]):
    s,e,w=np.array(old['source_SH_E_WR'],float); ds=np.array(ds,float)
    dp=np.array(old['palm_translation']); ns=s+ds; nw=w+dp
    l1=np.linalg.norm(e-s); l2=np.linalg.norm(w-e); ne=elbow(ns,nw,l1,l2,e)
    controls.extend([(s,ds),(e,ne-e),(w,dp)])
    side=old['side']; palm=np.array(Image.open(M/f'complete_palm120_{side}_mask.png').convert('L'))>0
    palms.append(palm)
    # A dense rigid translation domain keeps the complete same-volume palm;
    # the intervening whole-arm field joins it to elbow and sleeve naturally.
    palm_constraint=binary_dilation(palm,iterations=8)
    for py in range(345,580,4):
        for px in range(365,525,4):
            if palm_constraint[py,px]: controls.append((np.array([px,py],float),dp))
    pin=np.array(GEO['frames']['120']['rods'][len(bones)]['B_master'])
    controls.append((pin,dp))
    bones.append({'side':side,'source_shoulder_elbow_wrist':[s.tolist(),e.tolist(),w.tolist()],
                  'target_shoulder_elbow_wrist':[ns.tolist(),ne.tolist(),nw.tolist()],
                  'projected_upper_length_source_target':[float(l1),float(np.linalg.norm(ne-ns))],
                  'projected_forearm_length_source_target':[float(l2),float(np.linalg.norm(nw-ne))],
                  'palm_translation':dp.tolist(),'whole_palm_scale':1,'whole_palm_rotation_deg':0})

# All identity texture samples below come from accepted F120, not old code poses.
r,g,b=Uclean[:,:,:3].astype(float).transpose(2,0,1); alpha=Uclean[:,:,3]>0
white=(r>190)&(g>185)&(b>175)&(abs(r-g)<20)&(abs(g-b)<20)&(xx>580)&(xx<760)&(yy>335)&(yy<417)&alpha
cloth=(r>170)&(g>100)&(b<g*.65)&((g-b)>1.5*(r-g))&(Uclean[:,:,3]>180)&(yy>335)
guard=binary_dilation(binary_opening(white,iterations=1),iterations=2)|binary_dilation(binary_opening(cloth,iterations=1),iterations=2)
hair=((r<180)&(g<140)&(b<130)&(r>g+6))|((r>150)&(r>g*1.6)&(r>b*1.5))
pony=binary_dilation(hair&alpha&(xx>690)&(xx<840)&(yy>270)&(yy<414),iterations=2)&alpha&~guard
skin=(r>170)&(g>100)&(b>g*.65)&(r>g+12)&alpha
neck=binary_dilation(skin&(xx>590)&(xx<700)&(yy>330)&(yy<390),iterations=2)&alpha&~guard
head=((alpha&(xx>490)&(xx<840)&(yy<351))|neck|pony)&~guard
head=binary_fill_holes(head)&alpha&~guard
headpivot=np.array([636.,374.]); headrot=rot(1.5); headshift=np.array([7.,-4.])
for py in range(140,420,10):
    for px in range(495,840,10):
        if head[py,px] and not (590<=px<=700 and py>=339):
            p=np.array([px,py],float)
            controls.append((p,headpivot+headrot@(p-headpivot)+headshift-p))
# Head +1.5 degrees raises leftward attention as the turtle flips; the neck and
# chest recoil backward/up slightly, tapering into an anchored lower skirt.
for p,d in [([636,374],[7,-4]),([620,438],[6,-3]),([620,500],[2,-1]),
            ([708,490],[1,0]),([668,555],[0,0]),([688,604],[0,0]),
            ([559,402],[5,-3]),([710,414],[5,-2])]:
    controls.append((np.array(p,float),np.array(d,float)))
for py in range(620,711,14):
    for px in range(548,1000,14):
        if Uclean[py,px,3]>100: controls.append((np.array([px,py],float),np.zeros(2)))
for p in [[555,635],[601,659],[625,666],[644,666],[710,675],[790,675],
          [845,663],[970,591],[350,110],[1010,110],[350,740],[1010,740]]:
    controls.append((np.array(p,float),np.zeros(2)))
controls=list({tuple(np.round(p,6)):(p,d) for p,d in controls}.values())
rbf=RBFInterpolator(np.array([p for p,d in controls]),np.array([d for p,d in controls]),
                    kernel='thin_plate_spline',degree=1,smoothing=0)
control_error=float(np.max(np.linalg.norm(rbf(np.array([p for p,d in controls]))-
                                        np.array([d for p,d in controls]),axis=1)))
assert control_error<1e-6
palm_field_errors=[]
for palm,old in zip(palms,GEO['bones']):
    py,px=np.nonzero(palm)
    measured=rbf(np.column_stack([px,py]))
    errs=np.linalg.norm(measured-np.array(old['palm_translation']),axis=1)
    palm_field_errors.append({'side':old['side'],'sampled_source_palm_pixels':len(px),
                              'max_translation_residual_px':float(errs.max()),
                              'mean_translation_residual_px':float(errs.mean())})
    print("PALM_FIELD_AUDIT",old["side"],float(errs.max()),np.column_stack([px,py])[int(errs.argmax())].tolist(),flush=True)
    assert errs.max()<0.5
# Premultiplied resampling of ONE complete semantic upper layer, not separate
# arm cutouts. No gray fill, fake texture or disconnected pasted sleeve roots.
x0,y0,x1,y1=350,110,1020,740; h,w=y1-y0,x1-x0
gy,gx=np.mgrid[0:h:2,0:w:2]
field=rbf(np.column_stack([gx.ravel()+x0,gy.ravel()+y0])).reshape(gy.shape+(2,))
dy,dx=np.indices((h,w)); sx=dx.astype(float); sy=dy.astype(float)
for _ in range(16):
    vx=map_coordinates(field[:,:,0],[sy/2,sx/2],order=3,mode='nearest')
    vy=map_coordinates(field[:,:,1],[sy/2,sx/2],order=3,mode='nearest')
    sx=dx-vx; sy=dy-vy
crop=Uclean[y0:y1,x0:x1]; a=crop[:,:,3].astype(float)/255
pm=crop[:,:,:3].astype(float)*a[:,:,None]
wa0=map_coordinates(a,[sy,sx],order=3,mode='constant',cval=0); wa=wa0.clip(0,1)
wc=np.stack([map_coordinates(pm[:,:,k],[sy,sx],order=3,mode='constant',cval=0) for k in range(3)],2)
patch=np.zeros_like(crop); patch[:,:,3]=np.rint(wa*255).astype('uint8')
patch[:,:,:3]=np.rint(np.divide(wc,wa0[:,:,None],out=np.zeros_like(wc),where=wa0[:,:,None]>1e-6)).clip(0,255).astype('uint8')
patch[patch[:,:,3]<3]=0
U=np.zeros_like(A); U[y0:y1,x0:x1]=patch
Image.fromarray(U).save(F/'one_continuous_upper_head_arms_whole_skirt_CONSTRUCTION_ONLY.png')

# Original 7mm finite shafts project to this width on the master image. The
# character target contains only near-palm pieces, each stopping at its own B.
rodwidth=4.083333333333328
high=Image.new('RGBA',(W*4,H*4)); draw=ImageDraw.Draw(high)
shorts=[]
for row,length in zip(GEO['frames']['128']['rods'],[26.,32.]):
    aa=np.array(row['A_master']); bb=np.array(row['B_master'])
    q=bb+(aa-bb)/np.linalg.norm(aa-bb)*length
    pts=[tuple(q*4),tuple(bb*4)]
    draw.line(pts,fill=(91,53,24,255),width=round(rodwidth*4))
    draw.line(pts,fill=(202,151,72,255),width=round((rodwidth-1.5)*4))
    rad=rodwidth/2*4
    for pp in [q*4,bb*4]:draw.ellipse((pp[0]-rad,pp[1]-rad,pp[0]+rad,pp[1]+rad),fill=(177,120,49,255))
    shorts.append({'id':row['id'],'A_full_mechanism_only':aa.tolist(),'B_exact':bb.tolist(),
                   'short_contact_start':q.tolist(),'short_contact_length_px':length,
                   'external_tail_after_B_px':0})
rods=high.resize((W,H),Image.Resampling.LANCZOS)
Image.fromarray(np.array(rods)).save(F/'finite_axis_short_contact_segments_ONLY.png')
owned=Image.alpha_composite(rods,Image.fromarray(U)); Uwith=np.array(owned)
Image.fromarray(Uwith).save(F/'new_complete_upper_whole_skirt_with_short_contacts_CONSTRUCTION_ONLY.png')
Cpart=C.copy(); Cpart[:,850:]=0
G=A.copy(); G[:,:850]=0; oldchild=(U0[:,:,3]>0)&(xx>=850); G[oldchild]=C[oldchild]
T=Image.alpha_composite(Image.fromarray(Cpart),Image.fromarray(G))
T=Image.alpha_composite(T,Image.fromarray(lower)); T=np.array(Image.alpha_composite(T,owned))
visible=(lower[:,:,3]>0)&(U0[:,:,3]==0)&(Uwith[:,:,3]==0)&(yy>=650)&(xx<850)
T[visible]=A[visible]
fringe=(yy>=736)&(xx<850)&(A[:,:,3]>0)&(A[:,:,3]<=8)&(Uwith[:,:,3]==0); T[fringe]=A[fringe]
gmask=(xx>=850)&(A[:,:,3]>0)&(U0[:,:,3]==0)
assert not np.any(gmask&(Uwith[:,:,3]>0)); T[gmask]=A[gmask]
Image.fromarray(T).save(I/'01_unique_complete_F128_target_REVIEW_ONLY.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4'); bg.alpha_composite(Image.fromarray(T))
bg.convert('RGB').save(F/'complete_target_gray_REVIEW_ONLY.jpg',quality=96)
contactbox=(350,345,750,580)
c=bg.crop(contactbox).convert('RGB'); c.save(F/'contacts_1x_REVIEW_ONLY.png')
c.resize((1200,705),Image.Resampling.NEAREST).save(I/'02_same_pose_dual_palms_finite_contacts_3x.png')

# The real mask includes the whole old/new redraw domain, hidden roots and
# natural sleeve/chest rejoining. All full exposed legs/shoes and G/C are black.
exposed=(lower[:,:,3]>0)&(Uwith[:,:,3]==0)&(yy>=650)&(xx<850)
mask=binary_dilation((Uclean[:,:,3]>0)|(Uwith[:,:,3]>0),iterations=8)&(xx<1020)
mask=binary_fill_holes(mask); mask[exposed]=False; mask[gmask]=False; mask[736:]=False
Image.fromarray(np.uint8(mask)*255).convert('RGB').save(I/'04_complete_upper_whole_skirt_white_full_legs_black_mask.png')
box=(550,620,825,760); card=Image.new('RGB',(550,140))
card.paste(bg.crop(box).convert('RGB'),(0,0))
card.paste(Image.fromarray(np.uint8(mask)*255).convert('RGB').crop(box),(275,0))
card.save(F/'whole_skirt_hidden_roots_target_left_mask_right_1x.png')

font=ImageFont.truetype(str(P.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'),19)
card=Image.new('RGB',(1080,640),'#e7ebee'); d=ImageDraw.Draw(card)
d.text((16,12),'120已过身份小块：整脸发、白圆领、密白花纹、红露趾鞋；无旧双臂杆姿',font=font,fill='#263743')
cc,_=label(head&(Uclean[:,:,3]>100)); ident=int(cc[230,650]); assert ident>0
identity_head=binary_dilation(cc==ident,iterations=1)&head
headlayer=np.zeros_like(Uclean); headlayer[identity_head]=Uclean[identity_head]
patches=[((500,135,835,405),(20,70),(335,270)),
         ((593,351,668,399),(395,95),(225,144)),
         ((650,550,860,650),(690,85),(315,150)),
         ((490,835,755,935),(350,375),(530,200))]
for index,(box,xy,size) in enumerate(patches):
    src=headlayer if index==0 else (Uclean if index<3 else A)
    im=Image.fromarray(src).crop(box); ibg=Image.new('RGBA',im.size,'#bdc1c4'); ibg.alpha_composite(im)
    card.paste(ibg.convert('RGB').resize(size,Image.Resampling.LANCZOS),xy)
for xy,text in [((22,350),'整头体量与脸发'),((395,255),'白圆领'),((690,255),'密白织物花纹'),((350,590),'原红露趾鞋：完整保留')]:
    d.text(xy,text,font=font,fill='#263743')
card.save(I/'03_120_identity_head_collar_cloth_shoes_patches_only.png')
oldbg=Image.new('RGBA',(W,H),'#bdc1c4'); oldbg.alpha_composite(Image.fromarray(A))
box=(350,125,1020,720); paircard=Image.new('RGB',(1340,595))
paircard.paste(oldbg.crop(box).convert('RGB'),(0,0)); paircard.paste(bg.crop(box).convert('RGB'),(670,0))
paircard.save(F/'120_left_128_target_right_same_canvas_upper_hands_1x.png')

support=(yy>=760)&(xx<850)&(A[:,:,3]>0)
cm=(C[:,:,3]>0)&(U0[:,:,3]==0)&(Uwith[:,:,3]==0)&(xx<850)
assert np.array_equal(T[support],A[support])
assert np.array_equal(T[gmask],A[gmask]) and np.array_equal(T[visible],A[visible])
assert np.array_equal(T[cm],A[cm]) and not np.any(mask[exposed]) and not np.any(mask[736:])
semantic_cc,n=label(mask)
assert semantic_cc[230,650]>0 and semantic_cc[230,650]==semantic_cc[600,700]

prompt='''只绘F128在125–131龟偶翻转中段的唯一新人物上身。不是132完成翻肚，不提前合杆或放手。四输入依次为完整同姿目标、同姿双掌有限杆接触、120身份局部、真实完整黑白mask。第一图是施工参考，不是可直接采用的新原生绘图。
小满看到龟偶翻起产生轻微惊吓后收：整头保持正确体量，连带颈根、胸口、双肩小幅向后上方收，视线随龟偶抬起；双肘软弯，身体保持站稳。头与颈胸应连续，不能冻住整个上身只挪双手，也不能只扭脸或分挪五官。参考头部整体约顺时针1.5度、向右7向上4像素，颈胸跟随，腰裙向固定腿根自然衰减。不要夸张后仰或主动用力拉杆。
严格保留1672×941完整目标中两握点：R只单握T_H，中心(400.3988637166487,402.6996190692074)；L只单握T_S，中心(463.6082671920906,508.76677359903914)。保持两只完整手掌的体量和位置，肩肘腕用合理骨长重新自然接回；不要双夹、交到另一掌、合掌或多指。人物输入只保留掌内及掌外很短接触段，T_H朝向A_H(338.2626054104362,291.37892098338426)，T_S朝向A_S(319.83489249979783,457.5233847386403)，每根在自己B握点终止，没有外伸自由尾。
原龟偶、原长杆和翻转机制均是外部接景参照，本次不生成龟偶或长杆。不得把有限杆延长到另一只手，不加第三横杆，不强制保留旧X交叉。不要重画参考里已清掉的120旧外露杆。
完整整头颈、胸腰、双肩双臂双掌、白圆领、黄色密白花裙的整个上身与整裙白域必须同一语义组件原生重绘。特别自然补接施工中的袖下、胸腰和隐蔽腿根，不机械照抄缺口、灰填块、施工折线或断缝。保留120脸发、白圆领、密白布纹和红露趾鞋身份；头体积、脚、投影骨长合理。灯光由场景接入，不在纹理画死扫光。
真实mask整头颈胸、完整双臂掌、整裙及隐蔽腿根白；完整外露裸腿和鞋、奶奶和C杆黑固定。不得横截膝踝鞋、改奶奶或C。透明背景，1672×941完整图，无字、额外帧、背景和物体。若整组件构图漂移，只允许整组件一次统一相似注册接回完整固定腿根，不单独挪头或掌。'''
(F/'prompt_prepared_NOT_SUBMITTED_zh.txt').write_text(prompt+'\n')
names=['01_unique_complete_F128_target_REVIEW_ONLY.png',
       '02_same_pose_dual_palms_finite_contacts_3x.png',
       '03_120_identity_head_collar_cloth_shoes_patches_only.png',
       '04_complete_upper_whole_skirt_white_full_legs_black_mask.png']
rows=[{'order':i+1,'path':str((I/name).resolve()),'sha256':sha(I/name),
       'size':list(Image.open(I/name).size)} for i,name in enumerate(names)]
(F/'tool_args_prepared_NOT_SUBMITTED.json').write_text(json.dumps({
    'prompt':prompt,'transparent_background':True,
    'referenced_image_paths':[r['path'] for r in rows]},ensure_ascii=False,indent=2)+'\n')
baseline={'status':'MECHANISM_INPUT_BASELINE_ESTABLISHED_THIS_ACTUAL_ASTRA_GATE',
          'date':'2026-10-20','source_gate_commit':'a4f70c3a4d0e11d57d17cb32783ed7763dcb6cae',
          'candidate_geometry_sha256':sha(M/'candidate_geometry.json'),
          'historical_candidate_status_preserved':True,
          'meaning':'These roots, poses, scale, facing, camera, A-B lengths and F128 grips are accepted now for this F128 input preparation only; not previously frozen, not an exposure freeze.',
          'source_turtle_scale':1.3,'camera':GEO['camera'],'registration':GEO['reg'],
          'F120_root_pose_rods':GEO['frames']['120'],
          'F128_root_pose_rods':GEO['frames']['128'],
          'original_source_F120_unchanged':True,'new_image_calls':0}
(F/'MECHANISM_INPUT_BASELINE_THIS_GATE.json').write_text(json.dumps(baseline,ensure_ascii=False,indent=2)+'\n')
manifest={'status':'F128_FOUR_INPUTS_ZERO_CALL_ACTUAL_INPUT_GATE_PENDING','submitted':False,
          'generation_authorized':False,'new_image_calls':0,'raw_outputs':0,'retries':0,
          'frame_label_only':128,'timing':'125-131 middle flip, not132 complete',
          'later_states_prepared':False,'frozen_exposure':False,
          'source120_commit':'63758f3229c6fdbaa02e8b8e23eec2921fa6ce3f',
          'source120':str(source),'source120_sha256':sha(source),
          'source_complete_upper_sha256':sha(upper_source),
          'mechanism_input_baseline':'MECHANISM_INPUT_BASELINE_THIS_GATE.json',
          'target_is_continuous_construction_only_not_native_art':True,
          'whole_head_scale':1,'whole_head_rotation_deg':1.5,
          'whole_head_pivot':headpivot.tolist(),'whole_head_translation':headshift.tolist(),
          'neck_chest_shoulder_recoil':True,'whole_upper_one_TPS_field':True,
          'TPS_control_max_residual_px':control_error,'complete_palm_field_audit':palm_field_errors,
          'bone_reference_2D_only':bones,
          'short_contacts_only_not_puppet_or_long_rods':shorts,
          'actual_support_foreground_RGBA_changes':0,'actual_grandma_foreground_RGBA_changes':0,
          'actual_visible_original_C_RGBA_changes':0,'fixed_visible_lower_RGBA_changes':0,
          'full_visible_legs_shoes_and_GC_mask_black':True,
          'complete_semantic_mask_connected_head_to_whole_skirt':True,
          'inputs':rows}
(F/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(F/'FOUR_INPUT_SHA256SUMS').write_text(''.join(r['sha256']+'  inputs/'+Path(r['path']).name+'\n' for r in rows))
print(json.dumps({'calls':0,'control_error_px':control_error,'bones':bones,
                  'inputs':rows},ensure_ascii=False))
