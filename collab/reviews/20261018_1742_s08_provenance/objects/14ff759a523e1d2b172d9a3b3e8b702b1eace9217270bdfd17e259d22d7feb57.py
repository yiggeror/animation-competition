from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parent;O=R/'repair02_result_v5b_semantic_cleanup'
for sub in ['registered','candidates','masks','qa']:(O/sub).mkdir(parents=True,exist_ok=True)
import shutil
for pp in (R/'repair02_result_v5_semantic_cleanup/masks').glob('*'): shutil.copy2(pp,O/'masks'/pp.name)
base=Image.open(P/'inputs/F000_registered_props_preplaced_RGBA.png').convert('RGBA');orig=np.asarray(base).copy();reg=Image.open(R/'repair02_result_v1/registered/F000_call02_registered_RGBA.png').convert('RGBA')
oldallow=np.array(Image.open(P/'masks/F000_repair02_white_allowed_black_frozen.png'))>0
ex=np.array(Image.open(O/'masks/nonprop_blue_sleeve_and_old_palm_exclusions.png'))>0
newprop=np.array(Image.open(O/'masks/NEW_actual_prop_protection.png'))>0
fullprop=np.array(Image.open(O/'masks/NEW_actual_prop_full_footprint.png'))>0
jade=np.array(Image.open(P/'masks/F000_jade_bangle_full_protected.png'))>0
left_expanded=np.array(Image.open(P/'masks/left_hand_white_allowed.png').filter(ImageFilter.MaxFilter(13)))>0
white=(oldallow|ex|left_expanded)&~(newprop|jade);yy,xx=np.indices(white.shape)
b=orig.copy();b[ex]=0;base=Image.fromarray(b,'RGBA')
reject=Image.new('L',reg.size,0);d=ImageDraw.Draw(reject)
d.polygon([(1078,731),(1174,731),(1174,747),(1167,750),(1165,760),(1164,764),(1078,764)],fill=255)
d.polygon([(1047,785),(1055,773),(1066,756),(1069,746),(1077,741),(1085,744),(1087,752),(1081,760),(1074,762),(1060,786),(1053,789),(1047,789)],fill=255)
d.rectangle((1059,780,1067,800),fill=255)
a=np.array(reg);a[np.array(reject)>0]=0
# Keep real new thumb pixels newly uncovered by removing the incorrect old blue-sleeve protection.
near=(xx>=1047)&(xx<=1061)&(yy>=791)&(yy<=813)
blue=(a[:,:,2].astype(float)>a[:,:,0]*1.02)&(a[:,:,0]<200)&(a[:,:,2]>a[:,:,1]*.90)
a[near&blue]=0
sat=a[:,:,:3].max(2).astype(int)-a[:,:,:3].min(2).astype(int);a[white&(a[:,:,3]<32)&(sat>145)]=0
clean=Image.fromarray(a,'RGBA');shift=Image.new('RGBA',reg.size,0);shift.paste(clean,(0,-4))
left=left_expanded;w=left.astype(float)*np.clip((836-yy)/20,0,1);w[~white]=0
placed=Image.composite(shift,clean,Image.fromarray(np.rint(w*255).astype('uint8')))
pa=np.array(placed);sa=np.asarray(shift);pa[left&white,3]=sa[left&white,3];placed=Image.fromarray(pa,'RGBA')
# Internal-only blend on unchanged body seams. No old silhouette-alpha mix at the shifted palm boundary.
f=np.array(Image.open(P/'masks/F000_repair02_internal_feather.png'));f[ex]=255
f[white&(xx>=1038)&(xx<=1090)&(yy>=741)&(yy<=830)]=255
f[left&white]=255;f[~white]=0
candidate=Image.composite(placed,base,Image.fromarray(f,'L'));c=np.array(candidate)
contact=fullprop&~newprop&white;over=np.asarray(Image.alpha_composite(base,placed));c[contact]=over[contact]
# Exact preservation of actual semantic props/jade and all unchanged black-domain base pixels.
black=~white;c[black|newprop|jade]=orig[black|newprop|jade]
# Approved non-prop exclusions may be in the old black footprint, but not inside actual prop or jade.
c[ex&~(newprop|jade)&(pa[:,:,3]==0)]=0
# Delete only the parallel old contour and non-skin old blue-tail fragments. No new RGBA is painted.
edge=Image.new('L',reg.size,0);ed=ImageDraw.Draw(edge);ed.polygon([(1120,802),(1122,801),(1150,828),(1147,830)],fill=255)
erase=(np.array(edge)>0)
warm=(c[:,:,0]>140)&(c[:,:,1]>75)&(c[:,:,2]>40)&(c[:,:,0]>c[:,:,1]*1.15)
keep=np.array(Image.fromarray(warm.astype('uint8')*255).filter(ImageFilter.MaxFilter(3)))>0
erase|=near&~keep
erase&=white&~(newprop|jade);c[erase]=0
Image.fromarray(erase.astype('uint8')*255).save(O/'masks/extra_old_fragment_deletions.png')
out=Image.fromarray(c,'RGBA');out.save(O/'candidates/F000_call02_semantic_hands_RGBA.png');placed.save(O/'registered/F000_call02_far_hand_up4_actual_pixels_RGBA.png');Image.fromarray(white.astype('uint8')*255).save(O/'masks/NEW_effective_hand_allow.png');Image.fromarray(f).save(O/'masks/NEW_internal_sampling.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',reg.size,col);bg.alpha_composite(out);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,bb,m in [('hands',(930,728,1214,893),4),('near_grip',(1025,775,1077,833),8),('far_contact',(1080,735,1210,848),6),('head_and_match',(625,310,1205,860),2),('bottom',(530,976,990,1080),2),('arm_chains',(590,620,1230,1020),2)]:
  q=bg.crop(bb);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
change=np.any(c!=orig,2);checks={'status':'ZERO_CALL_SEMANTIC_MASK_REPAIR_PENDING_REVIEW','native_calls_total':2,'additional_calls':0,'far_hand_rigid_translation':[0,-4],'revision':'Previous y-3 plus1px to meet actual box outline y760 after removing mistakenly included old-palm row y761. Coordinator explicitly approved.','wrist_transition_scene_y':[816,836],'wrist_blend':'RGB transition only where permitted; source translated hand alpha, original jade restored, to avoid doubled old silhouette.','incorrect_old_prop_footprint_pixels_released':int((ex&~oldallow).sum()),'new_actual_prop_pixels_changed':int((change&newprop).sum()),'jade_pixels_changed':int((change&jade).sum()),'outside_new_allow_changed':int((change&~white).sum()),'real_new_thumb_revealed':'New raw thumb skin at1054,798/1054,801 had been obscured by blue sleeve accidentally included in old match donor. Now genuine new raw pixels are used.','new_skin_drawn_or_cloned':False,'candidate_sha256':hashlib.sha256((O/'candidates/F000_call02_semantic_hands_RGBA.png').read_bytes()).hexdigest()};(O/'qa/semantic_composite_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
