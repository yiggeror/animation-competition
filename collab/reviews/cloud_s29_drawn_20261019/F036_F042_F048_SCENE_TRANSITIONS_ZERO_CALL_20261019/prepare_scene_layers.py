from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
Q=B/'F042_F048_SINGLE_WHOLE_CLOTH_REPAINT_20261019'
feather=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png').convert('L'))>0
props=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))[:,:,3]>0
reference=B/'F036_CONTINUOUS_SLEEVE_CLOTH_sameM_zero_call_20261019/candidate/F036_CONTINUOUS_SLEEVE_CLOTH_SAME_M_TRIAL.png'
sources=[{'state':36,'source':str(reference),'used':str(reference),'sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'changed_pixels':0}]
for f in [42,48]:
 p=Q/f'F{f:03d}/REINTEGRATED_RGBA.png';raw=np.array(Image.open(p).convert('RGBA'));cloth=np.array(Image.open(Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png').convert('RGBA'))
 # Only the visible turned-lip/tip intersection, anchored to locked036's
 # tiny T junction. This is not an all-cloth or all-puppet foreground mask.
 # The contour follows the short sloped turn at the existing feather tips.
 points=([(828,798),(833,798),(844,804),(853,811),(850,815),(841,810),(833,805)] if f==42 else [(827,798),(832,797),(844,804),(852,810),(849,814),(841,810),(832,805)])
 m=Image.new('L',(1024,1536));ImageDraw.Draw(m).polygon(points,fill=255)
 front=(np.array(m)>0)&feather&(cloth[:,:,3]>=250)
 result=raw.copy();result[front]=cloth[front]
 changed=np.any(result!=raw,2);assert not (changed&~feather).any();assert not (changed&props&~front).any()
 out=R/f'F{f:03d}_FRONT_LIP_OVER_OUTER_FEATHER_RGBA.png';Image.fromarray(result).save(out)
 Image.fromarray(front.astype('uint8')*255).save(R/f'F{f:03d}_ONLY_TRUE_FRONT_LIP_FEATHER_INTERSECTION.png')
 y,x=np.where(front)
 sources.append({'state':f,'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'used':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native_cotton_layer':str(Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png'),'native_cotton_layer_sha256':hashlib.sha256((Q/f'F{f:03d}/EXTRACTED_ONE_NATIVE_CLOTH.png').read_bytes()).hexdigest(),'front_lip_semantic_contour':points,'feather_intersection_pixels':int(front.sum()),'intersection_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())] if len(x) else None,'changed_pixels':int(changed.sum()),'RGBA_changes_outside_original_feather':int((changed&~feather).sum()),'all_other_puppet_and_rod_RGBA_changes':int((changed&props&~front).sum()),'all_person_RGBA_changes':int((changed&~feather).sum())})
 # Include exact normal-size native junction as well as a 3x inspection view.
 g=Image.new('RGBA',(1024,1536),(236,239,242,255));g.alpha_composite(Image.fromarray(result));g.crop((710,730,910,880)).convert('RGB').save(R/f'F{f:03d}_TAIL_NORMAL_SIZE.png')
repo=R.parents[3]
for s in sources:s['usedURL']='/'+str(Path(s['used']).relative_to(repo))
plan={'global_frames':list(range(36,49)),'fps':24,'source_state_starts':[36,42,48],'exposure_within_short_clip':[{'state':36,'frames':[36,41],'count':6},{'state':42,'frames':[42,47],'count':6},{'state':48,'frames':[48,48],'count':1}],'scope':'Both frozen switches at042 and048 are included. Clip ends at048 first frame; no unsupported last-state end/next state is inferred.','sources':sources,'generation_calls':0}
(R/'SOURCES_EXPOSURE_AND_T_LAYER.json').write_text(json.dumps(plan,indent=2)+'\n')
sheet=Image.new('RGB',(900,250),(236,239,242));d=ImageDraw.Draw(sheet)
for i,s in enumerate(sources):
 im=Image.open(s['used']).convert('RGBA');g=Image.new('RGBA',im.size,(236,239,242,255));g.alpha_composite(im);sheet.paste(g.crop((710,730,910,880)).resize((300,225)).convert('RGB'),(300*i,25));d.text((300*i+5,5),str(s['state']),fill='black')
sheet.save(R/'FINAL_NATIVE_T_JUNCTIONS.png')
print(json.dumps([{'state':s['state'],'sha256':s['sha256'],'changed_pixels':s['changed_pixels']} for s in sources],indent=2))
