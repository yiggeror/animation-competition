from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;G=R.parent/'F069_SHORT_PUFF_BARE_ARMS_REPAIR_GATE_20261019';Q=R/'qa/semantic_guard_correction_61sol';Q.mkdir(parents=True,exist_ok=True)
firstp=R/'candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_FIRST_REVIEW.png';v=np.array(Image.open(firstp).convert('RGBA'));n=np.array(Image.open(R/'layers/F069_NEW_whole_uniform770over1145_plus550_0.png').convert('RGBA'));s=np.array(Image.open(G/'sources/F069_ACTION_ACCEPTED_COSTUME_REVOKED.png').convert('RGBA'));sz=(v.shape[1],v.shape[0]);mask=lambda p:np.array(Image.open(p).convert('L'))>0
hands=mask(R/'masks/KEEP_actual_palms_all_digits.png');prop=mask(R/'masks/KEEP_actual_prop_slider.png');allguard=mask(R/'masks/KEEP_all_actual_source_protection.png')
# Exactly the source old long-sleeve cuff ink/AA crossing the natural far wrist entrance.
z=Image.new('L',sz);d=ImageDraw.Draw(z);d.line([(1098,645),(1093,651),(1088,658),(1093,657),(1099,660),(1103,665),(1106,672),(1107,677),(1106,681),(1109,685),(1115,685),(1120,687),(1123,690)],fill=255,width=15,joint='curve');wrist=(np.array(z)>0)&hands
# The old sleeve occluded the lower cap: this boundary and material below it are UNKNOWN in the old source,
# not a physical metal edge. Retain actual upper visible metal/red/slider; take this already drawn new returned region.
z=Image.new('L',sz);ImageDraw.Draw(z).polygon([(844,613),(850,619),(856,629),(866,624),(876,624),(882,625),(890,620),(897,615),(903,616),(910,622),(916,627),(916,660),(840,660)],fill=255);cap=binary_dilation(np.array(z)>0,iterations=4)&prop
release=wrist|cap;c=v.copy();c[release]=n[release];out=Image.fromarray(c);p=R/'candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_SECOND_REVIEW.png';out.save(p)
for name,m in [('RELEASE_old_long_sleeve_far_wrist_cuff_ink_AA',wrist),('RELEASE_old_sleeve_occlusion_false_prop',cap),('RELEASE_two_wrong_guard_ownership_regions',release),('KEEP_actual_source_protection_CORRECTED',allguard&~release)]:Image.fromarray(m.astype('uint8')*255).save(R/f'masks/{name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',14)
def bg(im,col):
 z=Image.new('RGBA',im.size,col);z.alpha_composite(im);return z.convert('RGB')
for tone,col in [('gray',(215,224,231,255)),('dark',(35,43,52,255))]:
 bg(out,col).save(Q/f'F069_second_reconnected_full_{tone}.png');box=(575,475,1295,825);bg(out.crop(box),col).resize((1440,700)).save(Q/f'F069_second_two_short_puffs_bare_arms_{tone}_2x.png')
 for name,box in [('far_wrist',(1080,640,1148,714)),('tailcap',(835,590,925,666))]:
  board=Image.new('RGB',(1200,340),(230,237,243));d=ImageDraw.Draw(board)
  for j,(tag,z)in enumerate([('FIRST: incorrect old guard',Image.fromarray(v)),('same uniform native source',Image.fromarray(n)),('SECOND: corrected ownership',out)]):
   board.paste(bg(z.crop(box),col).resize((380,280)),(j*400,40));d.text((j*400+4,7),tag,font=font,fill='#35495d')
  board.save(Q/f'{name}_first_native_second_{tone}.png')
changed=np.any(c!=v,axis=2);srcdiff=np.any(c!=s,axis=2);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={'status':'SECOND_CANDIDATE_PENDING_ACTUAL_VISUAL_REVIEW','candidate':str(p.relative_to(R)),'candidate_SHA256':sha(p),'first_candidate_preserved_SHA256':sha(firstp),'source_raw_SHA256':'20fc656468f28ca6e9c381f0bfb88e51c0099abce697f792665c9c23c1786eeb','whole_registration_only':'770/1145+[550,0], no second transform','release_pixels':{'old_far_wrist_cuff_boundary':int(wrist.sum()),'old_cloth_occlusion_false_prop':int(cap.sum()),'union':int(release.sum())},'actual_changed_pixels':int(changed.sum()),'changes_outside_two_release_masks':int((changed&~release).sum()),'remaining_true_source_protection_RGBA_changes':int(srcdiff[allguard&~release].sum()),'complete_source_palms_digits_except_reclassified_cuff_RGBA_changes':int(srcdiff[hands&~wrist].sum()),'actual_known_source_prop_except_reclassified_old_occlusion_RGBA_changes':int(srcdiff[prop&~cap].sum()),'source_head_chest_skirt_guard_RGBA_changes':{name:int(srcdiff[mask(G/'masks'/file)].sum())for name,file in [('head_collar','KEEP_actual069_head_collar.png'),('valid_chest','KEEP_actual069_valid_nonediting_chest.png'),('stable_skirt_waist','KEEP_actual069_stable_skirt.png')]},'only_pixel_operation':'copy same uniformly mapped new raw RGBA in two wrong source-guard ownership regions; no new RGB, no blur, no local transform','calls':0,'no073_no_bridge':True}
(Q/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
