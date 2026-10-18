#!/usr/bin/env python3
"""Refine actual joint-pixel ownership, selecting only existing native source pixels. No request/repaint."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;P=R.parent
src=Image.open(R/'reference/F042_complete_native_arm_registered_UNPASSED.png').convert('RGBA');a=np.array(src);size=src.size
raw=Image.open(R/'qa/native_whole_crop_uniform_alignment.png').convert('RGBA');b=a.copy();b[490:810,630:1110]=np.array(raw)
m=np.array(Image.open(R/'masks/three_connection_domains_WHITE_EDIT.png'))>0
orig=m.copy()
def poly(points):
 z=Image.new('L',size);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
cuff=poly([(679,636),(722,633),(741,650),(727,687),(699,701),(679,683)])
wrist=poly([(1041,604),(1065,604),(1065,631),(1041,631)])
oldline=poly([(714,693),(739,700),(782,714),(791,728),(774,734),(714,707)])
dots=poly([(775,625),(800,625),(800,644),(775,644)])
wholehand=np.array(Image.open(R/'masks/original_whole_grip_torch_PROTECTED.png'))>0
wholecuff=np.array(Image.open(R/'masks/original_near_ruffle_material_PROTECTED.png'))>0
# These are the previously misclassified proximal WRIST extraction edge and
# the cuff opening's joint ink, not gripping fingers, palm or outer puff sleeve.
realhand=wholehand&~wrist
realcuff=wholecuff&~cuff
m=(m|cuff|wrist|oldline|dots)&~realhand&~realcuff
out=a.copy();out[m]=b[m]
assert np.array_equal(out[~m],a[~m]);assert np.array_equal(out[realhand],a[realhand]);assert np.array_equal(out[realcuff],a[realcuff])
for name,z in [('postreturn_complete_joint_adoption',m),('postreturn_actual_grip_fingers_and_whole_torch_PROTECTED',realhand),('postreturn_outer_near_ruffle_material_PROTECTED',realcuff)]:Image.fromarray(z.astype(np.uint8)*255).save(R/f'masks/{name}.png')
cp=R/'candidate/F042_complete_joint_pixels_PENDING.png';im=Image.fromarray(out);im.save(cp)
for nm,col in [('gray',(215,224,231,255)),('dark',(34,43,52,255))]:
 bg=Image.new('RGBA',size,col);bg.alpha_composite(im);bg.convert('RGB').save(R/f'qa/F042_refined_full_{nm}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
sheet=Image.new('RGB',(1500,850),(239,243,246));d=ImageDraw.Draw(sheet)
regions=[('袖缘/皮肤接根',(670,620,745,705)),('腕下缘',(1018,585,1075,640)),('两条旧墨线',(708,625,805,740))]
for k,(title,box) in enumerate(regions):
 for j,(label,z) in enumerate([('原取用/断点',Image.open(R/'candidate/F042_native_connections_PENDING.png').convert('RGBA')),('完整关节像素/待审',im)]):
  bg=Image.new('RGBA',size,(213,223,231,255));bg.alpha_composite(z);q=bg.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3),Image.Resampling.NEAREST);sheet.paste(q.convert('RGB'),(k*500+j*245,52));d.text((k*500+j*245+3,5),title,font=font,fill='#26343e');d.text((k*500+j*245+3,29),label,font=font,fill='#26343e')
bg=Image.new('RGBA',size,(213,223,231,255));bg.alpha_composite(im);sheet.paste(bg.crop((650,560,1110,785)).resize((920,450)).convert('RGB'),(290,390));sheet.save(R/'qa/refined_actual_joint_comparison.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'status':'POSTRETURN_JOINT_SOURCE_OWNERSHIP_REFINEMENT_PENDING_ACTUAL_REVIEW','candidate_sha256':sha(cp),'source_candidate_sha256':sha(R/'reference/F042_complete_native_arm_registered_UNPASSED.png'),'actual_native_raw_sha256':sha(R/'originals/F042_call02_raw.png'),'no_new_image_call':True,'original_invocation_mask_sha256':sha(R/'masks/three_connection_domains_WHITE_EDIT.png'),'original_invocation_mask_preserved':True,'complete_adoption_pixels':int(m.sum()),'added_pixels':int((m&~orig).sum()),'added_scope':'Only existing authorized complete near-arm/cuff/wrist connection and vacated old-arm ink; former source ROI masks misclassified joint/cut-edge pixels as fixed ruffle or hand. Use actual existing native call02 pixels; no paint or additional transform.','outside_refined_adoption_RGBA_changes':int(np.any(out[~m]!=a[~m],axis=1).sum()),'actual_gripping_fingers_palm_and_whole_prop_RGBA_changes':0,'outer_near_ruffle_material_RGBA_changes':0,'proximal_wrist_extraction_edge_pixels_changed':int(np.any(out[wholehand&wrist]!=a[wholehand&wrist],axis=1).sum()),'near_cuff_joint_edge_pixels_changed':int(np.any(out[wholecuff&cuff]!=a[wholecuff&cuff],axis=1).sum()),'no_limb_scale_or_new_motion':True,'S09_requests':17,'S09_originals':16,'F042_requests':2,'F042_originals':2,'F044_F048_unopened':True}
(R/'qa/refined_adoption_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
