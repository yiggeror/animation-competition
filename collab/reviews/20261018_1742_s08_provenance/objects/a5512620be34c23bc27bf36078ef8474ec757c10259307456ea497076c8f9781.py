from PIL import Image,ImageDraw
from pathlib import Path
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;R=P.parent;O=R/'repair02_result_v6_final_hand_candidate';A=R/'repair02_result_v5b_semantic_cleanup';B=R/'repair02_result_v3c_farhand_preplacement'
new=Image.open(A/'candidates/F000_call02_semantic_hands_RGBA.png').convert('RGBA');old=Image.open(B/'candidates/F000_call02_farhand_up3_DIAGNOSTIC_RGBA.png').convert('RGBA');n=np.array(new);o=np.asarray(old);yy,xx=np.indices(n.shape[:2]);far=(xx>=1080)&(xx<=1216)&(yy>=805)&(yy<=849);w=np.clip((818-yy)/13,0,1);mix=np.rint(n*w[:,:,None]+o*(1-w[:,:,None])).astype('uint8');n[far]=mix[far]
# Keep the already approved actual wrist connection; rigid 4px upper palm/fingers transitions to its original wrist.
erase=Image.new('L',new.size,0);d=ImageDraw.Draw(erase);d.polygon([(1120,802),(1122,801),(1145,823),(1142,823)],fill=255);d.polygon([(1056,802),(1060,803),(1060,815),(1052,815),(1050,811),(1054,807)],fill=255)
jade=np.array(Image.open(P/'masks/F000_jade_bangle_full_protected.png'))>0;prop=np.array(Image.open(A/'masks/NEW_actual_prop_protection.png'))>0;e=(np.array(erase)>0)&~(jade|prop);n[e]=0
out=Image.fromarray(n,'RGBA');out.save(O/'candidates/F000_call02_hand_candidate_RGBA.png');Image.fromarray(e.astype('uint8')*255).save(O/'masks/remaining_old_fragment_deletions.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 b=Image.new('RGBA',out.size,col);b.alpha_composite(out);b.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for part,bb,m in [('hands',(930,728,1214,893),4),('head_and_match',(625,310,1205,860),2),('arm_chains',(590,620,1230,1020),2),('bottom',(530,976,990,1080),2)]:
  q=b.crop(bb);q.resize((q.width*m,q.height*m),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{part}_{label}.png')
orig=np.asarray(Image.open(P/'inputs/F000_registered_props_preplaced_RGBA.png'));change=np.any(n!=orig,2);checks={'status':'ZERO_CALL_HAND_CANDIDATE_PENDING_REVIEW','actual_native_calls_total':2,'new_calls':0,'far_fingers_and_upper_palm_uniform_translation':[0,-4],'wrist_transition_to_existing_natural_v3c':[805,818],'actual_props_changed':int((change&prop).sum()),'jade_changed':int((change&jade).sum()),'eye_pixels_vs_v3c_changed':int(np.any(n[488:571,806:970]!=o[488:571,806:970],2).sum()),'new_skin_drawn_or_cloned':False,'semantic_mask_source':str(A/'masks/NEW_actual_prop_protection.png'),'candidate_sha256':hashlib.sha256((O/'candidates/F000_call02_hand_candidate_RGBA.png').read_bytes()).hexdigest()};(O/'qa/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
