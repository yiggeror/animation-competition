from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parent;O=R/'repair02_result_v8b_actual_hand_candidate';S=R/'repair02_result_v3c_farhand_preplacement';T=R/'repair02_result_v6_final_hand_candidate';M=R/'repair02_result_v5b_semantic_cleanup/masks'
for sub in ['candidates','qa','masks']:(O/sub).mkdir(parents=True,exist_ok=True)
base=Image.open(S/'candidates/F000_call02_farhand_up3_DIAGNOSTIC_RGBA.png').convert('RGBA');b=np.array(base);near=np.array(Image.open(T/'candidates/F000_call02_hand_candidate_RGBA.png'));jade=np.array(Image.open(P/'masks/F000_jade_bangle_full_protected.png'))>0;prop=np.array(Image.open(M/'NEW_actual_prop_protection.png'))>0;fullprop=np.array(Image.open(M/'NEW_actual_prop_full_footprint.png'))>0;ex=np.array(Image.open(M/'nonprop_blue_sleeve_and_old_palm_exclusions.png'))>0
hand=b.copy();hand[fullprop|ex]=0
# Only the existing accepted far-hand pixels are shifted one more pixel, so its wrist/outline do not change size.
shift=np.zeros_like(hand);shift[:-1]=hand[1:]
y,x=np.indices(b.shape[:2]);left=np.array(Image.open(P/'masks/left_hand_white_allowed.png').filter(ImageFilter.MaxFilter(5)))>0;left&=~(prop|jade)
w=np.clip((834-y)/16,0,1);patch=np.rint(shift*w[:,:,None]+hand*(1-w[:,:,None])).astype('uint8')
c=b.copy();c[left]=patch[left]
# Explicit contact slots: retain actual original box pixels unless actual new hand alpha covers them.
orig=np.array(Image.open(P/'inputs/F000_registered_props_preplaced_RGBA.png'));cleanorig=orig.copy();cleanorig[ex]=0;contact=fullprop&~prop&left;over=np.array(Image.alpha_composite(Image.fromarray(cleanorig,'RGBA'),Image.fromarray(patch,'RGBA')));c[contact]=over[contact]
# Adopt only the cleaned genuine near hand from the semantic-mask result; eye/body/lower-blouse remain the existing base.
nroi=(x>=1025)&(x<=1077)&(y>=775)&(y<=833);c[nroi]=near[nroi]
c[prop|jade]=orig[prop|jade]
# Delete the detached old parallel contour, without deleting actual skin or its adjacent outline.
warm=(c[:,:,0]>150)&(c[:,:,1]>85)&(c[:,:,2]>45)&(c[:,:,0]>c[:,:,1]*1.1)&(c[:,:,3]>180);keep=np.array(Image.fromarray(warm.astype('uint8')*255).filter(ImageFilter.MaxFilter(5)))>0
band=Image.new('L',base.size,0);ImageDraw.Draw(band).polygon([(1105,780),(1115,780),(1160,830),(1145,837)],fill=255);erase=(np.array(band)>0)&~keep&~(jade|prop);c[erase]=0
out=Image.fromarray(c,'RGBA');out.save(O/'candidates/F000_call02_hand_candidate_RGBA.png');Image.fromarray(erase.astype('uint8')*255).save(O/'masks/old_contour_deletions.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',base.size,col);bg.alpha_composite(out);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,bb,m in [('hands',(930,728,1214,893),4),('head_and_match',(625,310,1205,860),2),('bottom',(530,976,990,1080),2),('arm_chains',(590,620,1230,1020),2)]:
  q=bg.crop(bb);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
change=np.any(c!=orig,2);checks={'status':'ZERO_CALL_ACTUAL_HAND_CANDIDATE_PENDING_REVIEW','total_native_calls':2,'new_calls':0,'far_hand':'Existing accepted v3c hand moved rigidly one additional pixel upward (3 to4), wrist-only blend y818–834. No larger regenerated wrist adopted.','actual_prop_pixels_changed':int((change&prop).sum()),'jade_pixels_changed':int((change&jade).sum()),'eyes_vs_v3c_changed':int(np.any(c[488:571,806:970]!=b[488:571,806:970],2).sum()),'new_skin_drawn_or_cloned':False,'candidate_sha256':hashlib.sha256((O/'candidates/F000_call02_hand_candidate_RGBA.png').read_bytes()).hexdigest()};(O/'qa/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
