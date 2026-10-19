"""Actual whole native trousers + unchanged five real source layers; no paint."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
import numpy as np
from scipy.ndimage import binary_dilation,binary_erosion,binary_fill_holes,label

P=Path(__file__).resolve().parent
F=P/'frozen_input_65330a56'
raw=Image.open(P/'originals/F090_call02_RAW.png').convert('RGBA')
a=np.array(raw);r=a[:,:,:3].astype(int);yy,xx=np.indices(a.shape[:2]);fg=a[:,:,3]>0
scope=(yy>=560)&(yy<=1360)&(xx>=210)&(xx<=830)
navy=scope&(a[:,:,3]>=128)&(r[:,:,0]<115)&(r[:,:,1]<125)&(r[:,:,2]<140)&(r[:,:,2]-r[:,:,0]>3)&(r[:,:,1]-r[:,:,0]>=0)
labs,n=label(navy);counts=np.bincount(labs.ravel());counts[0]=0;navy=labs==counts.argmax()
edge=binary_dilation(navy,iterations=3)&scope&fg&(r.max(axis=2)<150)
mask=binary_fill_holes(navy|edge)&scope&fg
extracted=np.where(mask[:,:,None],a,0).astype('uint8')
Image.fromarray(mask.astype('uint8')*255).save(P/'masks/RAW_whole_native_trousers_material.png')
Image.fromarray(extracted).save(P/'production_layers/RAW_whole_native_trousers_EXTRACTED_ORIGINAL_RGB.png')
# Exactly the approved whole canvas inverse; zero fit, translation or limb scale.
local=Image.fromarray(extracted).resize((540,810),Image.Resampling.LANCZOS)
pants=Image.new('RGBA',(1672,1080));pants.alpha_composite(local,(1080,250))
pants.save(P/'production_layers/F090_call02_actual_whole_trousers_ORIGINAL_COLOR.png')
layers={}
for src in sorted((F/'production_reference_layers').glob('*.png')):
    dst=P/'production_layers'/('SOURCE_'+src.name)
    shutil.copyfile(src,dst);layers[src.stem]=Image.open(dst).convert('RGBA')
farshoe=layers['F090_far_shoe_ankle_LANDED']
order=[farshoe,pants,layers['F090_far_complete_arm_jade_hand'],layers['F090_body_head_blouse'],layers['F090_near_complete_arm'],layers['F090_near_shoe_ankle_SUPPORT_FIXED']]
candidate=Image.new('RGBA',(1672,1080))
for layer in order:candidate.alpha_composite(layer)
candidate.save(P/'candidate/F090_call02_complete_trousers_PENDING_ASTRA.png')
for tone,col in [('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
    bg=Image.new('RGBA',candidate.size,col);bg.alpha_composite(candidate)
    bg.save(P/f'qa/F090_call02_restored_five_layers_full_{tone}.png')
    bg.crop((1180,520,1570,1040)).resize((780,1040)).save(P/f'qa/F090_call02_waist_both_legs_ankles_{tone}.png')
    bg.crop((1240,535,1530,665)).resize((1160,520)).save(P/f'qa/F090_call02_actual_waist_seam_{tone}.png')
    bg.crop((1185,925,1570,1035)).resize((1155,330)).save(P/f'qa/F090_call02_actual_restored_ankle_cuffs_{tone}.png')

# Compare genuine cloth interiors, excluding outline/AA and no color correction.
pa=np.array(pants);interior=binary_erosion(pa[:,:,3]>=240,iterations=3)
ar=F/'sources/approved_original_source_archive_NOT_REQUEST'
palette={}
for key in ['F057','F062']:
    im=np.array(Image.open(ar/f'{key}_palette_ARCHIVE_NOT_REQUEST.png').convert('RGBA'))
    ma=np.array(Image.open(ar/f'{key}_actual_pants_material_mask.png').convert('L'))>0
    core=binary_erosion(ma&(im[:,:,3]>=240),iterations=3)
    vals=im[:,:,:3][core]
    palette[key]={'pixels':len(vals),'interior_mean_RGB':vals.mean(axis=0).tolist()}
palette['call02']={'pixels':int(interior.sum()),'interior_mean_RGB':pa[:,:,:3][interior].mean(axis=0).tolist(),'original_RGB_correction':[0,0,0]}

# Cuffs must meet genuine source ankle pixels with the complete native legs.
connections={}
for side,key in [('near','F090_near_shoe_ankle_SUPPORT_FIXED'),('far','F090_far_shoe_ankle_LANDED')]:
    foot=np.array(layers[key]);fr=foot[:,:,:3].astype(int)
    skin=(foot[:,:,3]>=128)&(fr[:,:,0]>160)&(fr[:,:,0]-fr[:,:,1]>12)&(fr[:,:,1]-fr[:,:,2]>10)
    connections[side]={'actual_pants_to_source_skin_overlap_pixels_alpha128':int((skin&(pa[:,:,3]>=128)).sum()),'actual_pants_to_source_skin_3px_neighbor_pixels':int((skin&binary_dilation(pa[:,:,3]>=128,iterations=3)).sum()),'no_connector_or_bridge_drawn':True}

base=Image.new('RGBA',(1672,1080))
for z in [farshoe,layers['F090_far_complete_arm_jade_hand'],layers['F090_body_head_blouse'],layers['F090_near_complete_arm'],layers['F090_near_shoe_ankle_SUPPORT_FIXED']]:base.alpha_composite(z)
b=np.array(base);c=np.array(candidate)
# All opaque unchanged front source body/arms/nearfoot pixels remain exact.
front=Image.new('RGBA',(1672,1080))
for z in order[2:]:front.alpha_composite(z)
ff=np.array(front);opaque=ff[:,:,3]==255
assert np.array_equal(c[opaque],ff[opaque])
record={'status':'CANDIDATE_ASSEMBLED_PENDING_ACTUAL_ROOT_ASTRA_REVIEW','raw_to_native':'whole135/256+1080,250 only; no fitting','source_layers_files_byte_identical':5,'new_pants_source':'one actual call02 complete waist/pelvis/both legs; original RGB, no recolor or connector paint','raw_whole_pants_material_pixels':int(mask.sum()),'native_pants_alpha128_pixels':int((pa[:,:,3]>=128).sum()),'opaque_front_original_material_pixels_RGBA_verified':int(opaque.sum()),'opaque_front_original_material_RGBA_changes':0,'source_far_whole_shoe_layer_kept_complete':True,'native_front_pants_may_naturally_occlude_back_far_shoe_pixels_alpha128':int(((np.array(farshoe)[:,:,3]>=128)&(pa[:,:,3]>=128)).sum()),'actual_ankle_connections':connections,'material_interiors':palette,'no_technical_color_or_guide_layer_adopted':True,'no_waist_or_ankle_filler_drawn':True,'F095_unopened':True}
(P/'qa/assembly_source_and_material_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
