"""One native062 material patch at identity; held actual060/062/063 exposure only."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_dilation, binary_erosion
import hashlib, json, numpy as np, subprocess, tempfile

R=Path(__file__).resolve().parent; B=R.parent
D=B/'F060_F062_ZERO_CALL_LAYER_DIAGNOSTIC_20261019'
N=B/'F060_F062_NATIVE_from_APPROVED6940a80f_20261019'
for d in ['candidate','masks','qa','geometry','exposure']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths={
 'actual_native062_whole_common_inverse':N/'F062/qa/F062_whole_fixed770x924_inverse.png',
 'untouched_native062_raw':N/'F062/originals/F062_call01_RAW.png',
 'before_frozen_rigid_prop':D/'candidate/F062_REAL_WHOLE_PROP_front_of_forearm_behind_actual_fingers_DIAGNOSTIC.png',
 'frozen_real_prop_source':D/'sources/REAL_PROP_original_NO_HUMAN.png',
 'frozen_rigid_prop_layer':D/'layers/ONE_REAL_PROP_R52_SCALE1_actual_mouth_registration.png',
 'complete_current_near_hand':D/'masks/KEEP_F062_actual_complete_near_hand_fingers.png',
 'approved060_complete_head_skirt':D/'candidate/F060_complete_head_skirt_source_REVIEW.png',
 'locked063':B/'F063_zero_call_semantic_reintegration_20261019/candidate/F063_zero_call_semantic_RECONNECTED.png',
 'frozen_prop_geometry':D/'geometry/one_rigid_source_transform_and_limits.json'}
raw=Image.open(paths['actual_native062_whole_common_inverse']).convert('RGBA')
before=Image.open(paths['before_frozen_rigid_prop']).convert('RGBA');a=np.array(raw);b=np.array(before)
assert sha(paths['untouched_native062_raw'])=='714b1f4cf42862669a1545c01a391fd1a2b1b26edfcfaae38dfb1637a3de9b27'
assert sha(paths['before_frozen_rigid_prop'])=='44a956e5a70a79c0182f68893dede8dbdb7477d63f905ecc7c2a01717dfa06a9'
g=json.loads(paths['frozen_prop_geometry'].read_text()); M=np.array(g['one_prop_transform']['M']);t=np.array(g['one_prop_transform']['t']);iv=M.T;it=-iv@t
pa=np.array(Image.open(paths['frozen_real_prop_source']));yy,xx=np.indices(pa.shape[:2])
# Include the real old cutout edge across the whole barrel width, not the earlier narrow conservative UNKNOWN box.
cutout_src=(xx>=1060)&(xx<=1200)&(yy>=370)&(yy<=552)&(pa[:,:,3]==0)
hole=np.array(Image.fromarray(cutout_src.astype('uint8')*255).transform(raw.size,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.NEAREST,fillcolor=0))>0
hand=np.array(Image.open(paths['complete_current_near_hand']).convert('L'))>0
prop=np.array(Image.open(paths['frozen_rigid_prop_layer']))[:,:,3]>0
def polygon(points):
    im=Image.new('L',raw.size);ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
key_points=[(1062,611),(1107,557),(1131,548),(1166,578),(1149,616),(1098,640)]
surface_points=[(1025,590),(1025,560),(1130,490),(1170,425),(1200,422),(1255,505),(1222,560),(1134,617),(1080,638),(1025,638)]
key=polygon(key_points);surface=polygon(surface_points)
# The old cutout's artificial boundary is replaceable; the known physical exterior away from it is protected.
outer=(prop&~binary_erosion(prop,iterations=3))&~binary_dilation(hole,iterations=9)
patch=(binary_dilation(hole,iterations=5)|key)&surface&(a[:,:,3]>0)&~hand&~outer
# Identity registration: complete actual source RGBA, no fill color, blending, warp, scale, or part fit.
out=b.copy();out[patch]=a[patch];after=Image.fromarray(out);changed=np.any(out!=b,axis=2)
assert not changed[~patch].any() and not changed[hand].any() and not changed[outer].any()
assert np.array_equal(out[patch],a[patch])
ys,xs=np.where(patch);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
assert bbox[1]>=490 and bbox[3]<=640
assert np.array_equal(out[:490],b[:490]) and np.array_equal(out[640:],b[640:])
candidate=R/'candidate/F062_NATIVE_REAL_TUBE_AND_KEY_IDENTITY_PATCH_PENDING_ASTRA.png';after.save(candidate)
for name,z in [('ADOPT_native062_one_true_material_patch.png',patch),('KEEP_actual_complete_current_hand.png',hand),('KEEP_known_real_outer_contour_away_from_old_cutout.png',outer),('REPLACE_old_cutout_and_edge_context.png',hole)]:Image.fromarray(z.astype('uint8')*255).save(R/'masks'/name)
source_index={name:{'commit':('10262cd16d1f3b81b38f0d49f44a3c063a2fa17c' if name in ['actual_native062_whole_common_inverse','untouched_native062_raw','locked063'] else 'da4b8c8df5209c0a81b0fb965d48b3b5d99402a2'),'path':str(p.relative_to(B.parents[2])),'sha256':sha(p)} for name,p in paths.items()}
check={'status':'ONE_NATIVE062_REAL_MATERIAL_IDENTITY_PATCH_PENDING_ACTUAL_ROOT_AND_ASTRA','sources':source_index,
 'material_registration':{'M':[[1,0],[0,1]],'translation_xy':[0,0],'scale':1,'rotation_deg':0,'source_grid':[1672,941],'prior_whole_raw_inverse':'770/1145 and placement[550,0], frozen before this repair; not a new patch fit'},
 'frozen_physical_prop_transform_unchanged':g['one_prop_transform'],'adopted_material_pixels':int(patch.sum()),'RGBA_changed_pixels':int(changed.sum()),'patch_bbox_xyxy':bbox,
 'complete_current_hand_RGBA_changes':int(changed[hand].sum()),'known_exterior_contour_RGBA_changes':int(changed[outer].sum()),'outside_patch_RGBA_changes':int(changed[~patch].sum()),'adopted_RGBA_difference_from_same_position_native062':int(np.any(out[patch]!=a[patch],axis=1).sum()),
 'lamp_head_and_front_end_y_lt490_RGBA_changes':int(changed[:490].sum()),'new_tail_and_lower_arms_y_ge640_RGBA_changes':int(changed[640:].sum()),
 'complete_two_original_arms':'Candidate unchanged outside local barrel/key material domain; original complete near hand explicitly protected. Donor is the same raw062 on the same whole-frame inverse, so any native human pixels at the border are also identical.',
 'exact_source_key_polygon':key_points,'material_domain_polygon':surface_points,'old_cutout_source_xyxy':[1060,370,1201,553],
 'seam_fix':'Adoption crosses the artificial old hole edge and its AA and takes complete actual native key face. Earlier skin/gold color heuristics excluded red highlights and left diagonal old cut pixels; no such palette rejection is used for the authorized real barrel material.',
 'new_native_requests':0,'new_raw_outputs':0,'new_RGB_or_alpha_drawing':False,'full_raw_top_or_whole_prop_reextraction':False,'candidate_sha256':sha(candidate)}
(R/'geometry/exact_source_patch_and_protection_checks.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def bg(z,tone):
    col=(35,43,52,255) if tone=='dark' else (215,224,231,255);w=Image.new('RGBA',z.size,col);w.alpha_composite(z);return w.convert('RGB')
for tone in ['gray','dark']:
    bg(after,tone).save(R/f'qa/F062_full_actual_repair_{tone}.png')
    board=Image.new('RGB',(1600,570),(224,232,239));dr=ImageDraw.Draw(board)
    for j,(name,z)in enumerate([('Actual native062 continuous barrel/key',raw),('Before: rigid prop with old cutout',before),('After: same-position true material',after)]):
        board.paste(bg(z,tone).crop((990,490,1200,690)).resize((525,500)),(j*533,35));dr.text((j*533+3,8),name,font=font,fill='black')
    board.save(R/f'qa/F062_ACTUAL_NATIVE_before_after_local_{tone}.png')
    # Actual nine decoded frames:060x2/062x1/063x6 at24fps;31px QA strip below the untouched drawing.
    images={60:Image.open(paths['approved060_complete_head_skirt']).convert('RGBA'),62:after,63:Image.open(paths['locked063']).convert('RGBA')}
    seq=[60]*2+[62]+[63]*6;refs={}
    for n,z in images.items():
        q=Image.new('RGBA',(1672,972),(35,43,52,255) if tone=='dark' else (215,224,231,255));q.alpha_composite(z);ImageDraw.Draw(q).text((10,946),f'ACTUAL F{n:03d}  060x2 -> 062x1 -> 063x6  /24fps / zero-call material repair',font=font,fill='#d4e1eb' if tone=='dark' else '#233d52');refs[n]=np.array(q.convert('RGB'))
    video=R/f'exposure/S09_F060x2_F062x1_F063x6_{tone}_ACTUAL9f_24fps.mp4'
    with tempfile.TemporaryDirectory(prefix='s09-062-repair-') as tmp:
        tmp=Path(tmp)
        for i,n in enumerate(seq):Image.fromarray(refs[n]).save(tmp/f'{i:02d}.png')
        subprocess.run(['ffmpeg','-v','error','-y','-framerate','24','-i',str(tmp/'%02d.png'),'-frames:v','9','-an','-c:v','libx264','-crf','12','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));vs=probe['streams'];assert len(vs)==1 and vs[0]['avg_frame_rate']=='24/1' and int(vs[0]['nb_read_frames'])==9
    dec=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-']),np.uint8).reshape((-1,972,1672,3));assert len(dec)==9
    cls=[]
    for i,z in enumerate(dec):
        scores={n:float(np.abs(z.astype(float)-v.astype(float)).mean()) for n,v in refs.items()};got=min(scores,key=scores.get);assert got==seq[i];cls.append({'clip_frame':i,'scene_frame':60+i,'expected_source':seq[i],'actual_nearest_source':got,'MAE':scores[got]})
    sheet=Image.new('RGB',(1500,650),(224,232,239));sd=ImageDraw.Draw(sheet)
    for j,i in enumerate([1,2,3]):
        z=Image.fromarray(dec[i]);sheet.paste(z.crop((550,0,1320,924)).resize((500,600)),(j*500,35));sd.text((j*500+5,8),f'ACTUAL decoded sceneF{60+i:03} / sourceF{seq[i]:03}',font=font,fill='black')
    sheet.save(R/f'qa/ACTUAL9f_decoded_060_062_063_transition_{tone}.png')
    close=Image.new('RGB',(1500,520),(224,232,239));cd=ImageDraw.Draw(close)
    for j,i in enumerate([1,2,3]):
        z=Image.fromarray(dec[i]);close.paste(z.crop((850,440,1300,830)).resize((500,433)),(j*500,35));cd.text((j*500+5,8),f'DECODE sourceF{seq[i]:03} full grip/receiver',font=font,fill='black')
    close.save(R/f'qa/ACTUAL9f_decoded_full_hands_prop_{tone}.png')
    (R/f'qa/actual9f_{tone}_decode_checks.json').write_text(json.dumps({'video':str(video.relative_to(R)),'sha256':sha(video),'fps':24,'frames':9,'duration':9/24,'no_audio':True,'all_actual_decoded_classifications':cls,'probe':probe},indent=2)+'\n')
print(json.dumps({'candidate_sha256':sha(candidate),'pixels':int(patch.sum()),'bbox':bbox,'hand_RGBA_changes':int(changed[hand].sum()),'gray9f_SHA':sha(R/'exposure/S09_F060x2_F062x1_F063x6_gray_ACTUAL9f_24fps.mp4'),'dark9f_SHA':sha(R/'exposure/S09_F060x2_F062x1_F063x6_dark_ACTUAL9f_24fps.mp4')},indent=2))
