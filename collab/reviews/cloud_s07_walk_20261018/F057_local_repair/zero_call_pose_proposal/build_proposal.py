#!/usr/bin/env python3
"""Zero-call rigid-pixel proposal. Keeps complete chains; no painted person or new generation."""
from pathlib import Path
import hashlib, json, math, shutil, os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/s07-rigid-proposal-mpl')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parent
REPAIR = ROOT.parent
for folder in ['reference', 'layers', 'masks', 'qa']:
    (ROOT/folder).mkdir(exist_ok=True)
source_path = REPAIR/'candidates/F057_call02_locked_domains_NOT_PASSED.png'
assert hashlib.sha256(source_path.read_bytes()).hexdigest() == 'c9ae1dfb6fde6b16f2f9a03f453a3cea68a9dab689134be9a3935d7715160360'
original = Image.open(source_path).convert('RGBA')
assert original.size == (1672,1080)
shutil.copyfile(source_path, ROOT/'reference/source_call02_same_canvas.png')
a = np.array(original)
size = original.size
reg = json.loads((REPAIR/'qa/call02_actual_review.json').read_text())['whole_figure_registration_to_world']
s,tx,ty = reg['s'],reg['tx'],reg['ty']
assert abs(s-0.36410361842105265)<1e-12
world = lambda p: np.asarray(p)*s+np.array([tx,ty])
floor = (775-ty)/s

def polygon(points):
    im=Image.new('L',size);ImageDraw.Draw(im).polygon(points,fill=255)
    return np.array(im)>0
near = polygon([(725,546),(874,546),(906,700),(907,788),(930,879),(948,934),
    (1055,950),(1055,1035),(840,1035),(837,955),(799,778),(786,735),(763,671),(742,602)])
far = polygon([(710,546),(807,546),(807,741),(758,862),(731,955),(775,957),
    (775,1035),(570,1035),(570,934),(610,856),(642,779),(694,673)]) & ~near
arm = polygon([(902,363),(930,383),(973,454),(1015,495),(1047,521),
    (1048,601),(992,610),(953,557),(912,484),(895,455),(893,405)])
# Actual blue blouse pixels are never assigned to the movable arm. Sleeve connection is a seam gate.
hsv=np.array(original.convert('RGB').convert('HSV'))
blue=(hsv[:,:,0]>125)&(hsv[:,:,0]<172)&(hsv[:,:,1]>40)&(hsv[:,:,2]>110)&(np.indices(a.shape[:2])[0]<566)
prior_hard=np.array(Image.open(REPAIR/'masks/locked_head_body_near_right_arm.png'))>0
arm &= ~blue&~prior_hard
foreground=a[:,:,3]>0
near &= foreground;far &= foreground;arm &= foreground
near &= np.indices(a.shape[:2])[0]>=566
source_yy,source_xx=np.indices(a.shape[:2])
all_pants=(source_yy>=566)&(source_yy<=1035)&(source_xx>=575)&(source_xx<=1055)&((source_yy>=625)|(source_xx>=710))&foreground
far=all_pants&~near&~arm
assert not (far&arm).any()
near_shoe = near & polygon([(842,966),(942,930),(956,944),(1055,949),(1055,1035),(839,1035)])
near_pants = near & ~near_shoe
moving=near|far|arm
static_foreground=foreground & ~moving
for name,m in [('near_complete_leg',near),('near_pants',near_pants),('near_shoe_and_ankle',near_shoe),('far_complete_leg',far),('far_complete_arm',arm)]:
    rgba=a.copy();rgba[~m]=0
    Image.fromarray(rgba).save(ROOT/f'layers/source_{name}.png')
    Image.fromarray((m*255).astype('uint8')).save(ROOT/f'masks/source_{name}.png')

def support_y(mask):
    ys=np.where(mask & (a[:,:,3]>128))[0]
    return int(ys.max())
near_sole= support_y(near_shoe)
far_sole = support_y(far & (np.indices(a.shape[:2])[0]>880))
# Visible ankle estimates are inherited from actual call02 review, with its stated uncertainty.
q=1560/1672
near_ankle=np.array([848.,884.])/q
far_ankle=np.array([614.,875.])/q
near_hip=np.array([791.,555.])
near_knee=np.array([858.,760.])
far_hip=np.array([748.,555.]);far_knee=np.array([709.,748.])
far_dy=floor-far_sole
far_delta=np.array([0.,far_dy])
target_near_x=far_ankle[0]+64/s
target_near_y=floor-(near_sole-near_ankle[1])
radius=np.linalg.norm(near_ankle-near_hip)
dx=target_near_x-near_hip[0]
target_hip=np.array([near_hip[0],target_near_y-math.sqrt(radius*radius-dx*dx)])
v0=near_ankle-near_hip;v1=np.array([target_near_x,target_near_y])-target_hip
theta=math.atan2(v1[1],v1[0])-math.atan2(v0[1],v0[0])
R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
near_t=target_hip-R@near_hip
near_ankle_new=R@near_ankle+near_t
near_knee_new=R@near_knee+near_t

# A complete rigid arm can swing from the visible sleeve outlet, but its visible reach is finite.
arm_pivot=np.array([903.,367.])
arm_elbow=np.array([914.,447.])
arm_wrist=np.array([911.,474.])/q
requested_wrist=(np.array([942.,623.])-np.array([tx,ty]))/s
arm_v=arm_wrist-arm_pivot;target_v=requested_wrist-arm_pivot
phi=math.atan2(target_v[1],target_v[0])-math.atan2(arm_v[1],arm_v[0])
AR=np.array([[math.cos(phi),-math.sin(phi)],[math.sin(phi),math.cos(phi)]])
arm_t=arm_pivot-AR@arm_pivot
arm_wrist_new=AR@arm_wrist+arm_t
arm_elbow_new=AR@arm_elbow+arm_t
actual_arm_radius=np.linalg.norm(arm_v)
target_arm_radius=np.linalg.norm(target_v)

def rigid(layer,R,t):
    # x_out=R*x_in+t. Rotation matrix determinant1; no scale/shear/warp.
    inv=R.T;off=-inv@t
    return layer.transform(size,Image.Transform.AFFINE,
        (inv[0,0],inv[0,1],off[0],inv[1,0],inv[1,1],off[1]),
        resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
layer=lambda name:Image.open(ROOT/f'layers/source_{name}.png').convert('RGBA')
canvas=Image.new('RGBA',size)
far_leg_transformed=rigid(layer('far_complete_leg'),np.eye(2),far_delta)
canvas.alpha_composite(far_leg_transformed)
arm_transformed=rigid(layer('far_complete_arm'),AR,arm_t)
arm_transformed.save(ROOT/'layers/proposal_far_complete_arm_rigid.png')
canvas.alpha_composite(arm_transformed)
canvas.alpha_composite(rigid(layer('near_pants'),R,near_t))
# Counter-rotate the unchanged shoe/ankle fragment about the transformed ankle; do not slide a shoe alone.
# Result is the same shoe orientation with its real ankle at the rotated leg endpoint and sole on775.
shoe_delta=near_ankle_new-near_ankle
near_shoe_transformed=rigid(layer('near_shoe_and_ankle'),np.eye(2),shoe_delta)
canvas.alpha_composite(near_shoe_transformed)
c=np.array(canvas)
c[static_foreground]=a[static_foreground]
c[prior_hard]=a[prior_hard]
proposal=Image.fromarray(c)
proposal.save(ROOT/'reference/rigid_preposition_NOT_ART_NOT_READY.png')
assert np.array_equal(c[static_foreground],a[static_foreground])
assert np.array_equal(c[blue & foreground],a[blue & foreground])
assert np.array_equal(c[prior_hard],a[prior_hard])

def capsule(points,radius):
    m=Image.new('L',size);draw=ImageDraw.Draw(m)
    ps=[tuple(map(float,p)) for p in points]
    if len(ps)>1:draw.line(ps,fill=255,width=radius*2+1,joint='curve')
    for x,y in ps:draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=255)
    return np.array(m)>0
hip_seam=polygon([(704,541),(878,541),(883,598),(708,598)])
# Preserve the exact blouse. Only the trousers immediately below it are eligible.
hip_seam &= ~blue
sleeve_seam=capsule([arm_pivot+[0,-2],arm_pivot+[5,15]],11)&~blue
# Ankle seam is explicit because shoe leveling changes ankle-to-cuff overlap; never mask whole legs.
ankle_seam=capsule([near_ankle_new+[-55,11],near_ankle_new+[32,-19]],10)
future_seam=hip_seam|sleeve_seam|ankle_seam
arm_dest_mask=np.array(rigid(Image.fromarray((arm*255).astype('uint8')).convert('RGBA'),AR,arm_t))[:,:,0]>128
# All distal arm pixels, including complete jade and hand, remain excluded from a future seam edit.
yy,xx=np.indices(a.shape[:2]);distal_arm=arm_dest_mask&(yy>arm_pivot[1]+45)
future_seam &= ~binary_dilation(distal_arm,iterations=3)
Image.fromarray((future_seam*255).astype('uint8')).save(ROOT/'masks/proposed_narrow_connection_only_NOT_APPROVED.png')
Image.fromarray((static_foreground*255).astype('uint8')).save(ROOT/'masks/locked_static_head_blouse_near_right_arm.png')

font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
guide_bg=Image.new('RGBA',size,(221,226,231,255));guide_bg.alpha_composite(proposal)
guide=guide_bg.convert('RGB');draw=ImageDraw.Draw(guide)
def chain(points,color):
    pts=[tuple(map(float,p)) for p in points];draw.line(pts,fill=color,width=3)
    for x,y in pts:draw.ellipse((x-5,y-5,x+5,y+5),outline=color,width=2)
chain([target_hip,near_knee_new,near_ankle_new],'#0086a6')
chain([far_hip+far_delta,far_knee+far_delta,far_ankle+far_delta],'#ad7534')
chain([arm_pivot,arm_elbow_new,arm_wrist_new],'#208d66')
draw.line((560,floor,1090,floor),fill='#5f6972',width=2)
draw.text((35,35),'F057 零调用预摆／不是画稿；完整链刚性旋转，脚底按真实鞋高接地',font=font,fill='#202c38')
draw.text((35,70),'0.364实际源配准；近腿／远臂骨点为可见图代理，衣下真实关节不可实测',font=font,fill='#202c38')
draw.text((35,105),'绿链保原整臂长度，空心红圈为942/623请求点：当前可达范围仍不足',font=font,fill='#a33d56')
x,y=requested_wrist;draw.ellipse((x-11,y-11,x+11,y+11),outline='#ba4660',width=3)
draw.line((arm_wrist_new[0],arm_wrist_new[1],x,y),fill='#ba4660',width=2)
draw.text((1100,1020),'地面775',font=font,fill='#303b45')
guide.save(ROOT/'reference/same_canvas_chain_and_support_guide.png')
overlay=Image.new('RGBA',size,(224,230,235,255));overlay.alpha_composite(proposal)
magenta=Image.new('RGBA',size,(202,44,118,0));magenta.putalpha(Image.fromarray((future_seam*110).astype('uint8')));overlay.alpha_composite(magenta)
overlay.convert('RGB').save(ROOT/'qa/narrow_seam_overlay.png')
arm_sheet=Image.new('RGB',(1000,700),(235,239,242));ad=ImageDraw.Draw(arm_sheet)
ad.text((20,15),'远臂独立层：原片段／袖口定轴旋转（整镯手同变换）',font=font,fill='#26323c')
for col,im in enumerate([layer('far_complete_arm'),arm_transformed]):
    context=im.crop((825,335,1065,635));bg=Image.new('RGBA',context.size,(195,204,211,255));bg.alpha_composite(context)
    arm_sheet.paste(bg.convert('RGB').resize((480,600),Image.Resampling.NEAREST),(10+col*500,65))
arm_sheet.save(ROOT/'qa/whole_arm_before_after_isolated.png')
comparison=Image.new('RGB',(1760,920),(244,246,248));cd=ImageDraw.Draw(comparison)
for col,(title,im) in enumerate([('同画布原图',original),('刚性预摆／不是画稿',proposal),('骨链与真实鞋底支撑',guide),('拟连接窄mask／未批准',overlay)]):
    if im.mode!='RGBA':im=im.convert('RGBA')
    bg=Image.new('RGBA',size,(221,226,231,255));bg.alpha_composite(im)
    panel=bg.crop((550,0,1100,1080)).convert('RGB').resize((430,845),Image.Resampling.LANCZOS)
    comparison.paste(panel,(5+col*440,55));cd.text((15+col*440,18),title,font=font,fill='#27333d')
comparison.save(ROOT/'qa/source_proposal_chain_mask_comparison.png')

def lengths(points):return [float(np.linalg.norm(np.array(b)-np.array(a))) for a,b in zip(points,points[1:])]
old_near=[near_hip,near_knee,near_ankle];new_near=[target_hip,near_knee_new,near_ankle_new]
old_arm=[arm_pivot,arm_elbow,arm_wrist];new_arm=[arm_pivot,arm_elbow_new,arm_wrist_new]
assert np.allclose(lengths(old_near),lengths(new_near),atol=1e-9)
assert np.allclose(lengths(old_arm),lengths(new_arm),atol=1e-9)
for matrix in [R,AR]:
    assert np.allclose(matrix.T@matrix,np.eye(2),atol=1e-12)
    assert abs(np.linalg.det(matrix)-1)<1e-12
near_bbox=(780,885,1020,1050);far_bbox=(575,900,805,1050)
sole_results={}
for name,box in [('near',near_bbox),('far',far_bbox)]:
    measured=np.array(near_shoe_transformed if name=='near' else far_leg_transformed)
    x0,y0,x1,y1=box;ys=np.where(measured[y0:y1,x0:x1,3]>128)[0]
    sole_results[name]={'actual_preposition_sole_native_y':int(ys.max()+y0),
        'actual_preposition_sole_world_y':float((ys.max()+y0)*s+ty)}
    local=measured[y0:y1,x0:x1,3]>128
    contact_y=np.indices(local.shape)[0]+y0
    contact_x=np.where(local&(contact_y>=math.floor(floor)-2))[1]+x0
    sole_results[name]['visible_near_floor_contact_x_world_interval']=[float(contact_x.min()*s+tx),float(contact_x.max()*s+tx)]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data={
    'status':'ZERO_CALL_RIGID_PROPOSAL_ONLY_ARM_REACH_GATE_UNRESOLVED',
    'new_native_calls':0,'S07_total_native_calls_unchanged':2,'accepted_F057':0,'other10_calls':0,
    'source':{'path':str(source_path.relative_to(REPAIR)),'sha256':sha(source_path),'size':list(size),'meaning':'call02 uniformly aligned and previous locked domains restored; actual art, not a skeleton figure'},
    'source_call02_native_sha256':'549cd22c715a1724d6546ede9c2b084173d5592d4dde1ac884707d0490841449',
    'registration_unchanged':reg,'construction75_1_not_used':True,'world_floor':775,'native_floor':float(floor),
    'manual_landmark_limit':'All bone chains are visible 2D proxies with hidden hip/shoulder uncertainty, not measured anatomical joints or3D bone lengths. Same point definitions carried through rigid transforms.',
    'near_complete_leg':{'source_chain_native':[p.tolist() for p in old_near],'proposal_chain_native':[p.tolist() for p in new_near],
        'rotation_deg':math.degrees(theta),'source_pivot':near_hip.tolist(),'destination_pivot':target_hip.tolist(),
        'proxy_lengths_before_native':lengths(old_near),'proxy_lengths_after_native':lengths(new_near),'scale':1,
        'shoe_method':'complete leg rotates first; same real shoe/ankle fragment counter-rotated about transformed ankle to level the sole; ankle seam explicitly pending',
        'source_real_sole_native_y':near_sole,'shoe_ankle_to_sole_native':float(near_sole-near_ankle[1])},
    'far_complete_leg':{'translation_native':far_delta.tolist(),'rotation_deg':0,'scale':1,
        'source_real_sole_native_y':far_sole,'source_ankle_native':far_ankle.tolist(),
        'proposal_ankle_world':world(far_ankle+far_delta).tolist(),'old_ankle_y758_not_forced':True},
    'support_actual_alpha128':sole_results,
    'support_limit':'Both visible shoe soles meet the same floor within raster rounding; this is geometric support only, not measured center-of-mass or dynamics.',
    'proposal_horizontal_ankle_span_world':float((near_ankle_new[0]-far_ankle[0])*s),
    'near_proposal_ankle_world':world(near_ankle_new).tolist(),
    'arm_complete_rigid':{'visible_sleeve_pivot_native':arm_pivot.tolist(),'source_chain_native':[p.tolist() for p in old_arm],
        'proposal_chain_native':[p.tolist() for p in new_arm],'rotation_deg':math.degrees(phi),'scale':1,
        'proxy_lengths_before_native':lengths(old_arm),'proxy_lengths_after_native':lengths(new_arm),
        'complete_jade_and_hand_transform_same_as_arm':True,'requested_wrist_world':[942,623],
        'actual_proposal_wrist_world':world(arm_wrist_new).tolist(),
        'visible_sleeve_to_wrist_radius_world':float(actual_arm_radius*s),
        'requested_sleeve_to_wrist_radius_world':float(target_arm_radius*s),
        'reach_deficit_world':float((target_arm_radius-actual_arm_radius)*s),
        'even_unfolded_visible_proxy_chain_max_world':float(sum(lengths(old_arm))*s),
        'finding':'Rigid swing about real sleeve preserves arm/jade/hand but cannot reach623. No stretching, detached arm translation to waist, or fictitious bone-length pass used.'},
    'actual_view_limit':'Rigid far-arm swing also puts much of the wrist behind the unchanged blouse. This is an explicit failed visibility/reach proposal, not a usable arm pose. Original complete jade/hand fragment is archived; rotated pixels use only source bicubic resampling and are not byte-identical after rotation.',
    'future_native_seam_mask':{'path':'masks/proposed_narrow_connection_only_NOT_APPROVED.png','pixels':int(future_seam.sum()),
        'domains':['trouser roots below unchanged blouse','small sleeve outlet','near cuff/ankle relevel junction'],
        'whole_leg_or_arm_mask':False,'knee_mask_pixels':0,'reason_no_knee_mask':'whole knee chain remains within one rigid leg; no knee cut was made',
        'complete_distal_arm_overlap_pixels':int((future_seam&distal_arm).sum()),'status':'proposal only; cannot generate until arm reach and mask review'},
    'static_source_foreground_changes':int(np.any(c[static_foreground]!=a[static_foreground],axis=1).sum()),
    'original_blouse_blue_pixel_changes':int(np.any(c[blue&foreground]!=a[blue&foreground],axis=1).sum()),
    'previous_complete_head_body_near_right_arm_hard_domain_changes':int(np.any(c[prior_hard]!=a[prior_hard],axis=1).sum()),
    'no_request_prepared_or_sent':True,
    'next_gate':'Astra inspect actual short-step support, fragment ownership and preserved chain lengths; resolve finite visible-arm reach to623 before authorizing any single connection call.'}
(ROOT/'proposal_checks.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:data[k] for k in ['status','new_native_calls','proposal_horizontal_ankle_span_world','support_actual_alpha128','static_source_foreground_changes','original_blouse_blue_pixel_changes']},ensure_ascii=False))
print(json.dumps(data['arm_complete_rigid'],ensure_ascii=False))
