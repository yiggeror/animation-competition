from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
R=Path('/workspace/animation-competition-s08-first14'); C=R/'collab/reviews/cloud_s12_20261018';O=C/'F034_F040_actual_20261019/F034';M=C/'F030_close_grip_from_locked026_20261019';I=C/'right_hand_lower_rod_inputs_20261019/first034_040'
for d in ['candidate','layers','masks','scene','tools','actual_scene','qa','provenance','diagnostics','contact_masks']: (O/d).mkdir(exist_ok=True)
b=np.array(Image.open(M/'candidate/F030.png').convert('RGBA'));raw=Image.open(O/'originals/F034_call01_raw.png').convert('RGBA');ra=np.array(raw)
# A single whole-board similarity, not independent hand/finger/joint transforms.
s=.48;theta=math.radians(7);A=s*np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);G=np.array([(955.3175883454596-275)/.7,(755.3437514359971-112)/.7]);g=np.array([1206.,821.]);t=G-A@g;inv=np.linalg.inv(A);v=-inv@t;coeff=tuple(np.column_stack([inv,v]).reshape(-1))
# Entire far arm and its proximal blue sleeve. Returned near arm/body are rejected context.
poly=[(397,340),(405,412),(444,485),(492,532),(596,620),(677,681),(1254,677),(1254,886),(1001,890),(760,867),(590,835),(516,794),(474,742),(441,707),(441,681),(429,612),(401,542),(382,473),(373,400)]
mask=Image.new('L',raw.size);ImageDraw.Draw(mask).polygon(poly,fill=255);sel=np.array(mask)>0;part=np.zeros_like(ra);part[sel]=ra[sel]
new=Image.fromarray(part,'RGBA').transform((1024,1536),Image.Transform.AFFINE,coeff,Image.Resampling.BICUBIC);n=np.array(new)
old=np.array(Image.open(I/'reference/actual030_far_arm_RGBA.png').convert('RGBA'))[:,:,3]>0
near=np.array(Image.open(I/'reference/actual030_near_arm_RGBA_NO_JADE.png').convert('RGBA'))[:,:,3]>0
# Original near arm is an immutable foreground occluder. Root patch stays in the existing far-side blouse domain.
y,x=np.mgrid[:1536,:1024];root=(x>=583)&(x<=706)&(y>=660)&(y<=857)
adopt=(n[:,:,3]>0)&~near&((old)|(x>=650)|(root));n[~adopt]=0
root_keep=Image.new('L',(1024,1536));ImageDraw.Draw(root_keep).polygon([(582,640),(653,640),(663,741),(686,790),(652,814),(615,832),(589,808)],fill=255)
keep_old_root=np.array(root_keep)>0
back=b.copy();back[old&~keep_old_root]=0
out=np.array(Image.alpha_composite(Image.fromarray(back,'RGBA'),Image.fromarray(n,'RGBA')));out[near]=b[near]
# Preserve every source byte outside the exact removed/adopted union.
edit=old|adopt;out[~edit]=b[~edit]
# Actual curled fingers in front of the true shaft. Thumb/rear palm are behind the shaft.
fp=[(1112,821),(1140,816),(1178,812),(1199,817),(1213,808),(1225,792),(1245,789),(1254,805),(1254,881),(1100,881),(1094,850)]
fm=Image.new('L',raw.size);ImageDraw.Draw(fm).polygon(fp,fill=255);fmn=np.array(fm.transform((1024,1536),Image.Transform.AFFINE,coeff,Image.Resampling.NEAREST))>0
fgown=fmn&adopt;fg=np.zeros_like(out);fg[fgown]=out[fgown];bg=out.copy();bg[fgown]=0
assert np.array_equal(np.maximum(bg,fg),out);assert not np.any((bg[:,:,3]>0)&(fg[:,:,3]>0));assert np.array_equal(out[near],b[near]);assert np.array_equal(out[~edit],b[~edit])
for fn,a in [('candidate/F034.png',out),('layers/F034_BG_person.png',bg),('layers/F034_FG_actual_front_fingers.png',fg),('layers/raw_far_arm_exclusive.png',part),('diagnostics/F034_single_mapping_far_arm.png',n)]:Image.fromarray(a,'RGBA').save(O/fn)
for fn,m in [('raw_far_arm_ownership.png',sel),('native_exact_edit_union.png',edit),('near030_protected.png',near),('native_front_finger_ownership.png',fgown)]:Image.fromarray(np.uint8(m)*255).save(O/'masks'/fn)
mask.save(O/'masks/raw_far_arm_ownership.png');fm.save(O/'masks/raw_front_fingers_ownership.png')
# Minimal preview is explicitly diagnostic, prior to actual Canvas.
for name,img in [('whole',Image.fromarray(out,'RGBA')),('arm',Image.fromarray(out,'RGBA').crop((540,635,1024,1035)).resize((968,800)))]:
 canvas=Image.new('RGBA',img.size,'#c5c7ca');canvas.alpha_composite(img);canvas.convert('RGB').save(O/f'diagnostics/02_native_{name}_registration.jpg')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'state':'LOCAL_SINGLE_MAPPING_CANDIDATE_NOT_YET_CANVAS','actual034_raw_SHA256':sha(O/'originals/F034_call01_raw.png'),'mother030_SHA256':sha(M/'candidate/F030.png'),'single_whole_raw_similarity':np.column_stack([A,t]).tolist(),'uniform_scale':s,'rotation_degrees':7,'source_grip_axis_estimate':g.tolist(),'target_approved_grip_axis_native':G.tolist(),'far_arm_source_polygon':poly,'front_fingers_source_polygon':fp,'no_per_joint_or_tip_warp':True,'returned_near_arm_body_not_adopted':True,'near030_RGBA_exact':True,'outside_exact_edit_union_RGBA_exact':True,'native_BG_FG_mutually_exclusive_union_exact':True,'candidate_SHA256':sha(O/'candidate/F034.png')};(O/'qa/native_scope_and_single_mapping.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'matrix':report['single_whole_raw_similarity'],'native_SHA256':report['candidate_SHA256']}))
