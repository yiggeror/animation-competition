from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];G=R/'F005_input_gate';O=R/'F005_result_semantic_v4'
for d in ['candidates','masks','geometry','qa']:(O/d).mkdir(parents=True,exist_ok=True)
base=Image.open(R/'F005_result_nominal/candidates/S08_F005_local_arm_candidate_RGBA.png').convert('RGBA');raw=Image.open(R/'F005_result_nominal/registered/F005_registered_scene_patch_RGBA.png').convert('RGBA');orig=Image.open(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png').convert('RGBA');f3=Image.open(R/'F003_FINAL_LOCKED/S08_F003_grandma_match_box_RGBA.png').convert('RGBA');b=np.array(base);q=np.array(raw);out=b.copy();old=np.array(Image.open(G/'masks/F005_scene_white_allowed_black_frozen.png'))>0

def poly(name,pts):
 m=Image.new('L',base.size,0);ImageDraw.Draw(m).polygon(pts,fill=255);m.save(O/'masks'/name);return np.array(m)>0
# Explicit false-hand band, outside the real dark finger contour. Old far-arm skin is not hand anatomy.
band=poly('RELEASE_false_old_arm_band_at_near_fingers.png',[(1052,837),(1052,847),(1046,859),(1042,872),(1031,882),(1018,890),(1001,895),(982,898),(979,902),(1003,901),(1024,895),(1043,884),(1056,871),(1064,854),(1064,837)])
# Continue same raw outer upperarm beyond original white-mask truncation to its forearm intersection.
join=poly('RELEASE_far_upperarm_outer_mask_step.png',[(1061,870),(1074,870),(1085,891),(1085,902),(1074,902),(1065,884)])
leftjoin=poly('RELEASE_far_upperarm_left_boundary_continuity.png',[(984,894),(1007,894),(1019,915),(1037,951),(1037,957),(1016,957),(1005,926),(993,903)])
frontjoin=poly('RELEASE_narrow_far_forearm_diagonal_seam_continuity.png',[(1073,889),(1095,872),(1117,851),(1139,825),(1144,829),(1122,857),(1099,881),(1078,902),(1072,901)])
rawmask=band|join|leftjoin|frontjoin
# Take registered same-raw continuous skin/alpha only in these explicit regions, internally feathered.
m=Image.fromarray(rawmask.astype('uint8')*255);f=np.array(m.filter(ImageFilter.GaussianBlur(.45)),dtype=float)/255;f[~rawmask]=0
ba=b[:,:,3]/255;qa=q[:,:,3]/255;alpha=qa*f+ba*(1-f);premul=q[:,:,:3]*qa[:,:,None]*f[:,:,None]+b[:,:,:3]*ba[:,:,None]*(1-f[:,:,None]);v=np.dstack((np.clip(np.rint(premul/np.maximum(alpha[:,:,None],1e-9)),0,255).astype('uint8'),np.rint(alpha*255).astype('uint8')));out[rawmask]=v[rawmask]
# Restore the unchanged original blue sleeve interior, eliminating native crop's rectangular color-grade edge.
cloth=poly('RESTORE_original_near_sleeve_interior.png',[(638,768),(735,759),(744,780),(741,793),(731,787),(718,787),(699,797),(677,810),(654,823),(638,831)])
m=Image.fromarray(cloth.astype('uint8')*255);f=np.array(m.filter(ImageFilter.GaussianBlur(.6)),float)/255;f[~cloth]=0;o=np.array(f3);out=np.rint(out*(1-f[:,:,None])+o*f[:,:,None]).astype('uint8')
# Re-reveal fixed far hand from its exact approved F000 RGBA; don't alpha-stack it over F003 and thicken antialias.
far=np.array(Image.open(G/'masks/F005_far_hand_box_jade_protected.png'))>0;out[far]=np.array(orig)[far];Image.fromarray(far.astype('uint8')*255).save(O/'masks/RESTORE_exact_F000_far_hand_box_jade_RGBA_no_alpha_stack.png')
a=Image.fromarray(out,'RGBA');dest=O/'candidates/S08_F005_semantic_seam_candidate_RGBA.png';a.save(dest);allowed=rawmask|cloth|far;Image.fromarray((old|allowed).astype('uint8')*255).save(O/'masks/FINAL_actual_semantic_union.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',a.size,col);bg.alpha_composite(a);bg.convert('RGB').save(O/'qa'/f'candidate_{label}.png')
 for name,bb,z in [('whole_arm',(585,615,1235,1045),2),('contact',(970,725,1220,920),4),('near_cuff',(625,750,790,880),4),('far_sleeve_restore',(930,760,1090,930),4)]:
  t=bg.crop(bb);t.resize((t.width*z,t.height*z),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'candidate_{name}_{label}.png')
 # Same-scale comparison for actual stroke separation.
 panel=Image.new('RGB',(1920,1080),col[:3]);panel.paste(Image.alpha_composite(Image.new('RGBA',a.size,col),f3).resize((960,540)).convert('RGB'),(0,270));panel.paste(bg.resize((960,540)).convert('RGB'),(960,270));panel.save(O/'qa'/f'F003_to_F005_same_scale_{label}.png')
change=np.any(out!=b,2);hand=np.array(Image.open(G/'masks/F005_preplaced_hand_match_protected.png'))>0;pm=np.array(Image.open(G/'masks/F005_match_protected.png'))>0;checks={'status':'F005_SEMANTIC_SEAM_CANDIDATE_PENDING_REVIEW','actual_native_calls_total':5,'new_calls':0,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_pixels':int(change.sum()),'changed_outside_explicit_regions':int((change&~allowed).sum()),'hand_cutout_changes_outside_explicit_false_band_and_boundary_join':int((change&hand&~band&~leftjoin).sum()),'match_changed':int((change&pm).sum()),'far_hand_box_jade_diff_from_original_F000_RGBA':int(np.any(out[far]!=np.array(orig)[far],axis=1).sum()),'false_old_arm_band_pixels':int(band.sum()),'narrow_boundary_continuity_pixels':int((leftjoin|frontjoin).sum()),'notes':'Same single raw; exact F000 far hand RGBA replaces accidentally alpha-stacked reveal; actual true hand contour, match and fixed box/jade preserved. Only explicit false old-arm band and outer upperarm mask step released. Near sleeve original cloth restored. No new drawing or added call.'};(O/'geometry/checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
