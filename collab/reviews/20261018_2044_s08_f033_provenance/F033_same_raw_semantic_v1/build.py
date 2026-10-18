from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F033_input_gate';P=R/'F033_result_registered_nominal';src=P/'candidates/S08_F033_whole_turn_arms_candidate_RGBA.png';a=np.array(Image.open(src).convert('RGBA'));q=np.array(Image.open(P/'registered/F033_registered_scene_patch_RGBA.png').convert('RGBA'));base=np.array(Image.open(G/'inputs/F033_preplaced_body_anchor_truehands_NO_ROD_RGBA.png'));W,H=1920,1080
m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon([(1134,836),(1141,838),(1155,836),(1158,844),(1156,858),(1148,869),(1140,863),(1137,852)],fill=255);roi=np.array(m)>0
far=np.array(Image.open(G/'masks/F033_far_visible_hand_jade_TRUE_SEAT_guard.png'))>0;near=np.array(Image.open(G/'masks/F033_near_distal_palm_fingers_entire_match_guard.png'))>0;box=np.array(Image.open(G/'masks/F033_fixed_table_box_guard.png'))>0
# The released portion is exclusively old alpha0 outside true bracelet/hand. White-domain
# continuation below it takes the same raw actual contour; no generated jade replaces original jade.
truefar=far&(base[:,:,3]>0);protected=truefar|near|box
release=roi&far&(base[:,:,3]==0)
allowed=roi&~protected
# Keep the actual native forearm skin and ink contour. Raw green-bracelet overhang outside original
# true jade is not adopted: it remains old true alpha0, separately recorded.
r,g,b=[q[:,:,k].astype(int)for k in range(3)];new_green=(g-r>12)&(g-b>7)&(q[:,:,3]>0)
allowed&=~new_green
out=a.copy();out[allowed]=q[allowed]
Image.fromarray(release.astype('uint8')*255).save(O/'masks/RELEASE_old_far_alpha0_guard_outside_true_jade.png');Image.fromarray(allowed.astype('uint8')*255).save(O/'masks/ADOPT_same_raw_continuous_far_forearm_outer_edge.png');Image.fromarray((roi&new_green).astype('uint8')*255).save(O/'masks/EXCLUDE_native_jade_overhang_keep_original_jade.png')
dest=O/'candidates/S08_F033_same_raw_far_wrist_semantic_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 z=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));z.crop((1100,800,1180,880)).resize((800,800)).convert('RGB').save(O/'qa'/f'far_wrist_{tag}.png');z.crop((680,660,1300,960)).resize((1240,600)).convert('RGB').save(O/'qa'/f'whole_arms_{tag}.png');z.convert('RGB').save(O/'qa'/f'candidate_{tag}.png')
ch=(a!=out).any(2);j={'status':'SAME_RAW_SEMANTIC_FAR_WRIST_CANDIDATE','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'changed_pixels':int(ch.sum()),'outside_explicit_semantic_permission_changed':int((ch&~allowed).sum()),'true_far_hand_jade_changed':int((ch&truefar).sum()),'near_distal_fingers_match_changed':int((ch&near).sum()),'box_changed':int((ch&box).sum()),'new_released_old_alpha0_guard_pixels':int(release.sum()),'raw_source':'Same call16 registered native full frame; no local warp, no new generation.'};(O/'geometry/checks.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
