from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parent;O=ROOT/'repair02_result_v3c_farhand_preplacement'
for s in ['registered','candidates','masks','qa','geometry']:(O/s).mkdir(parents=True,exist_ok=True)
base=Image.open(P/'inputs/F000_registered_props_preplaced_RGBA.png').convert('RGBA'); reg=Image.open(ROOT/'repair02_result_v1/registered/F000_call02_registered_RGBA.png').convert('RGBA')
allow=Image.open(P/'masks/F000_repair02_white_allowed_black_frozen.png').convert('L');feather=Image.open(P/'masks/F000_repair02_internal_feather.png').convert('L')
prot=Image.open(P/'masks/F000_prop_core_protected.png').convert('L');jade=Image.open(P/'masks/F000_jade_bangle_full_protected.png').convert('L')
# Reject only the new raw's unwanted props; no skin painted or extended.
reject=Image.new('L',reg.size,0);d=ImageDraw.Draw(reject)
d.polygon([(1078,731),(1174,731),(1174,747),(1167,750),(1165,760),(1164,764),(1078,764)],fill=255)
d.polygon([(1047,785),(1055,773),(1066,756),(1069,746),(1077,741),(1085,744),(1087,752),(1081,760),(1074,762),(1060,786),(1053,789),(1047,789)],fill=255)
d.rectangle((1059,780,1067,788),fill=255)
a=np.array(reg); white=np.asarray(allow)>0; rejection=(np.asarray(reject)>0)
sat=a[:,:,:3].max(2).astype(int)-a[:,:,:3].min(2).astype(int);noise=white&(a[:,:,3]<32)&(sat>145)
a[rejection|noise]=0;clean=Image.fromarray(a,'RGBA')
# One rigid 3 px upward displacement of the complete new far palm/fingers.
shift=Image.new('RGBA',reg.size,0);shift.paste(clean,(0,-3))
left=Image.open(P/'masks/left_hand_white_allowed.png').convert('L')
y,x=np.indices((1080,1920));w=np.asarray(left).astype(float)/255
# Entire palm and digits retain one source transform. Only the wrist-side 20 px blends back.
w*=np.clip((836-y)/20,0,1)
w[~white]=0;wm=Image.fromarray(np.rint(w*255).astype('uint8'))
placed=Image.composite(shift,clean,wm)
# Do not mix the old base prop ghosts back in immediately around protected props.
f=np.array(feather); f[white&(x>=1038)&(x<=1090)&(y>=741)&(y<=830)]=255
f[white&(x>=1078)&(x<=1190)&(y>=730)&(y<=806)]=255
sample=Image.fromarray(f,'L');candidate=Image.composite(placed,base,sample)
b=np.asarray(base);c=np.array(candidate);fullprop=np.asarray(Image.open(P/'masks/F000_preplaced_full_prop_pixels.png'))>0;contact=fullprop & (np.asarray(prot)==0) & white;contact_over=np.asarray(Image.alpha_composite(base,placed));c[contact]=contact_over[contact];black=~white;hard=(np.asarray(prot)>0)|(np.asarray(jade)>0);c[black|hard]=b[black|hard];candidate=Image.fromarray(c,'RGBA')
candidate.save(O/'candidates/F000_call02_farhand_up3_DIAGNOSTIC_RGBA.png');placed.save(O/'registered/F000_call02_same_raw_farhand_up3_RGBA.png');wm.save(O/'masks/far_hand_uniform_up3_wrist_blend.png');sample.save(O/'masks/final_internal_sampling.png');Image.fromarray(rejection.astype('uint8')*255).save(O/'masks/rejected_generated_props.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',reg.size,col);bg.alpha_composite(candidate);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,box,m in [('hands',(930,728,1214,893),4),('eyes',(820,496,961,565),5),('head_and_match',(625,310,1205,860),2),('bottom',(530,976,990,1080),2),('arm_chains',(590,620,1230,1020),2)]:
  q=bg.crop(box);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
change=np.any(c!=b,2);checks={'status':'ZERO_CALL_SAME_RAW_FAR_HAND_PREPLACEMENT_DIAGNOSTIC_NOT_APPROVED','actual_total_generation_calls':2,'additional_generation_calls':0,'far_palm_and_fingers_translation_scene_pixels':[0,-3],'wrist_blend_scene_y':[816,836],'near_hand_geometry_changed':False,'before_contact_measurement':'frozen box opaque bottom y761; new raw skin first y764-766 at x1096-1124, gap median2px','black_changed_pixels':int((change&black).sum()),'jade_changed_pixels':int((change&(np.asarray(jade)>0)).sum()),'frozen_props_changed_pixels':int((change&(np.asarray(prot)>0)).sum()),'method':'One rigid far-hand translation; wrist-only internal mask blend, no arm deformation, no generated props adopted. Original props/jade restored bit for bit. No painting or morphology to invent contact.'}
(O/'geometry/placement_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
