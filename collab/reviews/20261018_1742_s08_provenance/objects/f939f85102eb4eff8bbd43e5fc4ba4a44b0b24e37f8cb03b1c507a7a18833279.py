from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import numpy as np,json
P=Path(__file__).resolve().parent;R=P.parent;S=R/'repair02_result_v3c_farhand_preplacement';O=R/'repair02_result_v4_edge_cleanup'
im=Image.open(S/'candidates/F000_call02_farhand_up3_DIAGNOSTIC_RGBA.png').convert('RGBA');a=np.array(im);base=a.copy();reg=np.array(Image.open(S/'registered/F000_call02_same_raw_farhand_up3_RGBA.png').convert('RGBA'))
# Only unwanted old silhouette fragments are deleted. No hand pixels are invented or cloned.
near=Image.new('L',im.size,0);d=ImageDraw.Draw(near);d.polygon([(1054,792),(1059,792),(1059,802),(1056,808),(1052,812),(1048,812),(1048,808),(1052,804),(1053,800),(1051,800)],fill=255)
blue=(a[:,:,2].astype(float)>a[:,:,0]*1.05)&(a[:,:,0]<160)&(a[:,:,2]>a[:,:,1]*.90)
clear=(np.asarray(near)>0)&blue
fragments=Image.new('L',im.size,0);d=ImageDraw.Draw(fragments);d.polygon([(1058,786),(1063,787),(1063,799),(1059,802),(1057,800)],fill=255)
clear|=(np.asarray(fragments)>0)
far=Image.new('L',im.size,0);d=ImageDraw.Draw(far);d.polygon([(1121,804),(1124,803),(1148,825),(1150,829),(1144,827),(1127,812)],fill=255)
clear|=(np.asarray(far)>0)&(reg[:,:,3]<160)
# The original jade and prop bodies remain immutable, even if a cleanup outline intersects them.
jade=np.asarray(Image.open(P/'masks/F000_jade_bangle_full_protected.png'))>0;prop=np.asarray(Image.open(P/'masks/F000_prop_core_protected.png'))>0
clear&=~(jade|prop);a[clear]=0;out=Image.fromarray(a,'RGBA');out.save(O/'candidates/F000_call02_edge_cleanup_DIAGNOSTIC_RGBA.png');Image.fromarray(clear.astype('uint8')*255).save(O/'masks/actual_deleted_fragment_pixels.png')
change=np.any(a!=base,2)
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',im.size,col);bg.alpha_composite(out);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,b,m in [('hands',(930,728,1214,893),4),('near_grip',(1025,775,1077,833),8),('far_contact',(1080,735,1210,848),6),('head_and_match',(625,310,1205,860),2)]:
  c=bg.crop(b);c.resize((c.width*m,c.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
checks={'status':'SAME_RAW_FRAGMENT_DELETION_ONLY_NOT_APPROVED','generation_calls_total':2,'new_generation_calls':0,'deleted_pixels':int(clear.sum()),'changed_outside_explicit_cleanup_pixels':int((change&~clear).sum()),'jade_changed_pixels':int((change&jade).sum()),'frozen_props_changed_pixels':int((change&prop).sum()),'hand_translation_relative_v3c':False,'new_hand_pixels_drawn_or_cloned':False,'unresolved':'Box contact bright old donor strip and side-thumb gap may require real local drawing; this deletion pass does not synthesize replacement fingers or palm.'};(O/'qa/edge_cleanup_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
