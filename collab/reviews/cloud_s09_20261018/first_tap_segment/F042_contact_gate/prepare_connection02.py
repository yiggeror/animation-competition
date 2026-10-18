from pathlib import Path
import json,hashlib,shutil,math
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from scipy.ndimage import binary_dilation,binary_erosion
P=Path(__file__).resolve().parent;R=P/'connection_call02'
assert not (R/'requests/execution_state.json').exists()
for n in ['reference','masks','requests','originals','candidate','qa']:(R/n).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=P/'whole_arm_trial/F042_whole_arm_06deg_UNPASSED.png';dest=R/'reference/F042_complete_native_arm_registered_UNPASSED.png';shutil.copyfile(src,dest)
im=Image.open(dest).convert('RGBA');a=np.array(im);size=im.size
cuff=np.array(Image.open(P/'whole_arm_trial/source_complete_near_cuff_material_guard.png'))>0
rigid=np.array(Image.open(P.parent/'reference/F031_rigid_whole_torch_and_grip.png').convert('RGBA'));rg=np.zeros_like(rigid[:,:,3]);rg[59:]=rigid[:-59,:,3];hand=rg>0
layer=Image.open(P/'whole_arm_trial/native_complete_near_arm_source.png').convert('RGBA');rad=math.radians(-6);rot=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]]);tr=np.array([-58.620561322995854,76.1285099336501]);inv=rot.T;it=-inv@tr
moved=layer.transform(size,Image.Transform.AFFINE,(inv[0,0],inv[0,1],it[0],inv[1,0],inv[1,1],it[1]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));arm=np.array(moved)[:,:,3]>0
Image.fromarray(arm.astype(np.uint8)*255).save(R/'masks/actual_complete_registered_arm_material.png')
def poly(points):
 m=Image.new('L',size);ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
# The earlier yellow ROI included exposed bodice and old-arm ink, not just the ruffle.
cuff &= poly([(639,672),(646,652),(673,626),(715,608),(750,607),(773,618),(781,630),(776,640),(754,633),(735,632),(717,649),(700,677),(699,705),(683,716),(663,713),(641,697)])
cuff_edit=poly([(682,637),(720,635),(740,651),(727,684),(701,699),(681,683)])&~cuff
wrist_edit=poly([(1011,565),(1045,565),(1073,610),(1066,632),(1034,632),(1013,607)])&~hand
# Actual old-ink envelopes verified against the pixels, not the contaminated arm extraction mask.
old_line=poly([(716,696),(735,701),(778,716),(782,724),(767,725),(718,707)])&~cuff
old_dots=poly([(776,627),(795,627),(795,642),(776,642)])&~cuff
edit=(cuff_edit|wrist_edit|old_line|old_dots)&~hand&~cuff
Image.fromarray(edit.astype(np.uint8)*255).save(R/'masks/three_connection_domains_WHITE_EDIT.png');Image.fromarray(hand.astype(np.uint8)*255).save(R/'masks/original_whole_grip_torch_PROTECTED.png');Image.fromarray(cuff.astype(np.uint8)*255).save(R/'masks/original_near_ruffle_material_PROTECTED.png')
crop=(630,490,1110,810);im.crop(crop).save(R/'reference/F042_connections_crop_RGBA.png');Image.fromarray(edit.astype(np.uint8)*255).crop(crop).save(R/'masks/F042_connections_crop_WHITE_EDIT.png')
bg=Image.new('RGBA',size,(212,222,230,255));bg.alpha_composite(im);wash=Image.new('RGBA',size,(205,40,116,0));wash.putalpha(Image.fromarray(edit.astype(np.uint8)*115));bg.alpha_composite(wash);bg.crop(crop).resize((960,640)).convert('RGB').save(R/'qa/actual_complete_connections_input_and_mask.png')
prompt='''Edit ONLY the WHITE regions in image2, on the already-positioned transparent lower-arm artwork in image1. This is a minimal drawing connection repair for F042. Keep the480x320crop framing. Do not crop, zoom, move, rotate, mirror, resize or relight anything. Return the same transparent crop.

The single foreground arm, elbow and original gripping wrist are ALREADY at the correct first-contact position. The complete original hand/flashlight and original receiving palm are fixed. Do not change the pose or perform another downward motion. Keep the entire correct arm, original dark outer contour and both original upper-arm/forearm proportions fixed outside white. No new hand, sleeve, elbow, bracelet or object.

WHITE REGION1, at the left sleeve opening: remove only the redundant inner parallel black arc on the skin. The original yellow ruffle and its original black edge are BLACK-LOCKED and already correct. Make the skin naturally meet that one existing ruffle edge. There must be one sleeve opening and a single continuous attached upper arm, no second cuff line, detached skin strip, narrow flesh bridge or hole. Keep the existing skin flat fill and warm shadow separately; do not brighten or yellow the skin.

WHITE REGION2, at the right wrist's LOWER edge: join the actual forearm to the BLACK-LOCKED original gripping wrist with one smooth natural skin contour. Remove the small V-shaped notch and projecting skin tongue at this artificial extraction boundary. The original hand, fingers and grip remain untouched; draw only the small adjacent forearm connection and exterior contour, with no cut line across the skin. Preserve wrist width and orientation, do not stretch, shorten or move the forearm or wrist.

WHITE REGION3, the tiny patches below the upper arm and on the exposed yellow dress: remove obsolete OLD ARM ink slivers and black dots, restoring the small continuous yellow cloth with its original white-dot pattern and gentle shading. These are vacated old-arm contours, not garment fold lines. Do not touch the correct current arm contour, far sleeve/arm, skirt or original yellow ruffle.

Keep the existing clean2D animation ink and exact source palette. No white seam, extra crease, text, background, ground, guide line, mask colors, blur, glow or new objects. Make the minimum actual local connection inside white and return the same transparent crop.'''
(R/'requests/prompt.txt').write_text(prompt+'\n');args={'prompt':prompt,'referenced_image_paths':[str(R/'reference/F042_connections_crop_RGBA.png'),str(R/'masks/F042_connections_crop_WHITE_EDIT.png')],'transparent_background':True};(R/'requests/arguments.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
meta={'status':'PREPARED_ACTUAL_MINIMUM_F042_CONNECTION_REPAIR_NOT_EXECUTED','frame':42,'source_candidate_sha256':sha(dest),'crop_xyxy':list(crop),'mask_pixels':int(edit.sum()),'whole_hand_torch_mask_overlap':int((edit&hand).sum()),'original_near_ruffle_material_overlap':int((edit&cuff).sum()),'source_pose':'Single real native042 complete arm, one rigidR-6deg+t[-58.6205613,76.1285099], scale1. Not accepted due cuff duplicate arc and wristV. No per-segment transform or limb stretch.','specific_gate_failures':'61sol actual review: duplicate cuff arc691..714/644..680, wrist lower V1048..1055/612..620, small obsolete source-arm ink.','new_pose':False,'F044_F048_unopened':True};(R/'preparation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
freeze={'status':'PREPARED_NOT_EXECUTED','arguments_sha256':sha(R/'requests/arguments.json'),'prompt_sha256':sha(R/'requests/prompt.txt'),'inputs':[{'path':p,'sha256':sha(p)} for p in args['referenced_image_paths']],'source_full_sha256':sha(dest),'operation_mask_sha256':sha(R/'masks/three_connection_domains_WHITE_EDIT.png')};(R/'requests/input_freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n');print(json.dumps(meta,ensure_ascii=False))
