"""Extract real generated arms; trial source-only restoration on frozen044.

No drawn anatomy, skin fill, segmented limb transform, or new image call.
This initial registration is diagnostic and requires actual seam review.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import numpy as np
from scipy.ndimage import binary_dilation, binary_fill_holes, label

P = Path(__file__).resolve().parent
F = P / 'frozen_input_e6619045/sources'
S = P / 'adoption_sources'
raw = Image.open(P / 'originals/F063_local_repair_call01_RAW.png').convert('RGBA')
a = np.array(raw)
rgb = a[:, :, :3].astype(int)
fg = a[:, :, 3] > 0


def poly(points):
    z = Image.new('L', raw.size)
    ImageDraw.Draw(z).polygon(points, fill=255)
    return np.array(z) > 0


def actual_skin(domain):
    warm = domain & fg & (rgb[:, :, 0] > 150) & (rgb[:, :, 1] > 95) & (rgb[:, :, 0]-rgb[:, :, 1] > 12) & (rgb[:, :, 0]-rgb[:, :, 1] < 115) & (rgb[:, :, 1]-rgb[:, :, 2] > 10) & (rgb[:, :, 1]-rgb[:, :, 2] < 100)
    warm = binary_fill_holes(warm) & domain & fg
    edge = binary_dilation(warm, iterations=4) & domain & fg
    ink = (rgb.max(axis=2) < 145) | ((rgb[:, :, 0]-rgb[:, :, 1] > 8) & (rgb[:, :, 1]-rgb[:, :, 2] > 7) & (rgb[:, :, 1]-rgb[:, :, 2] < 100))
    z = binary_fill_holes(warm | (edge & ink)) & domain & fg
    labs, _ = label(z)
    counts = np.bincount(labs.ravel()); counts[0] = 0
    z = labs == counts.argmax()
    # Retain true weak boundary alpha only when it remains immediately next to
    # the selected actual arm; RGB is never recolored or filled.
    z |= binary_dilation(z, iterations=3) & domain & fg & (a[:, :, 3] < 128)
    return z


near_domain = poly([(127,693),(254,696),(400,775),(735,600),(890,608),(928,653),(924,730),(903,765),(861,797),(810,815),(760,806),(639,868),(425,980),(300,992),(205,963),(135,867)])
far_domain = poly([(605,775),(742,775),(800,916),(1007,835),(1280,800),(1280,990),(1040,990),(884,1095),(747,1112),(685,1080),(600,940)])
near = actual_skin(near_domain)
far = actual_skin(far_domain) & ~near

mother = Image.open(F / 'F044_fe70_PRODUCTION_MOTHER_ARCHIVE_NOT_REQUEST.png').convert('RGBA')
m = np.array(mother)


def source_mask(name):
    return np.array(Image.open(S / name).convert('L')) > 0


def frozen_mask(name):
    return np.array(Image.open(F / name).convert('L')) > 0


my, mx = np.indices(m.shape[:2])
mrgb = m[:,:,:3].astype(int)
fd = Image.new('L',mother.size)
ImageDraw.Draw(fd).polygon([(919,653),(1035,653),(1083,704),(1240,696),(1240,805),(1091,847),(1000,865),(919,820)],fill=255)
fd = np.array(fd)>0
old_far_skin = fd & (m[:,:,3]>0) & (mrgb[:,:,0]>150) & (mrgb[:,:,1]>95) & (mrgb[:,:,0]-mrgb[:,:,1]>12) & (mrgb[:,:,0]-mrgb[:,:,1]<115) & (mrgb[:,:,1]-mrgb[:,:,2]>10) & (mrgb[:,:,1]-mrgb[:,:,2]<100)
old_far_ink = (mrgb.max(axis=2)<145) | ((mrgb[:,:,0]-mrgb[:,:,1]>8)&(mrgb[:,:,1]-mrgb[:,:,2]>7)&(mrgb[:,:,1]-mrgb[:,:,2]<100))
old_far = binary_fill_holes(old_far_skin | (binary_dilation(old_far_skin,iterations=4)&fd&(m[:,:,3]>0)&old_far_ink)) & fd & (m[:,:,3]>0)
old = source_mask('F044_complete_old_near_arm_actual_mask.png') | (np.array(Image.open(S/'F063_source_same_rigid_unit_original.png'))[:,:,3]>0) | old_far
hard = frozen_mask('F044_NATIVE_GUARD_head_neck_collar_actual.png') | frozen_mask('F044_NATIVE_GUARD_near_ruffle_actual_material.png') | (source_mask('F044_stable_skirt_semantic_guard_frozen_PRE063.png') & ~old_far)
old &= (m[:, :, 3] > 0) & ~hard
base = m.copy(); base[old] = 0

# One common whole raw-to-native mapping, the input gate's initial width inverse.
# No per-arm fitting or any source body transform. This is a trial, not a pass.
scale = 700 / 1282
offset = np.array([585., 233.])
inv = 1 / scale
coefficients = (inv, 0., -offset[0]*inv, 0., inv, -offset[1]*inv)
layers = {}
for name, mask in [('near_complete_arm', near), ('far_complete_arm', far)]:
    z = np.where(mask[:, :, None], a, 0).astype('uint8')
    Image.fromarray(z).save(P / f'production_layers/RAW_{name}_EXTRACTED_ONLY.png')
    Image.fromarray(mask.astype('uint8')*255).save(P / f'masks/RAW_{name}_semantic_material.png')
    mapped = Image.fromarray(z).transform(mother.size, Image.Transform.AFFINE, coefficients, resample=Image.Resampling.BICUBIC, fillcolor=(0,0,0,0))
    layers[name] = mapped
    mapped.save(P / f'production_layers/TRIAL_registered_{name}_NOT_ACCEPTED.png')

prop = Image.open(S / 'F063_true_rigid_prop_only_frozen_target.png').convert('RGBA')
# The genuine old source prop has an old-hand occlusion. Only real new prop
# pixels lying inside that missing-source domain may repair it; never invent
# tube colors or adopt the generated head/body/background.
prop_domain = poly([(447,665),(533,652),(767,609),(896,590),(1048,530),(1166,496),(1215,498),(1243,522),(1252,569),(1250,707),(1221,736),(1151,741),(1071,727),(1027,711),(926,736),(839,771),(542,793),(472,781),(450,752)])
prop_color = ((rgb[:,:,0]-rgb[:,:,1] > 100) & (rgb[:,:,1]-rgb[:,:,2] < 45)) | (np.ptp(rgb,axis=2) < 45) | (rgb.max(axis=2) < 145)
new_prop_mask = prop_domain & fg & ~near & ~far & prop_color
new_prop_raw = np.where(new_prop_mask[:,:,None],a,0).astype('uint8')
new_prop_mapped = Image.fromarray(new_prop_raw).transform(mother.size,Image.Transform.AFFINE,coefficients,resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
theta = np.deg2rad(78.508)
rot = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
trans = np.array([1049.533,598.588])-rot@np.array([1134.519,470.])
ri = rot.T; rt = -ri@trans
old_missing = Image.open(S/'F063_old_grip_human_exclusion_at_original_source.png').convert('L').transform(mother.size,Image.Transform.AFFINE,(*ri[0],rt[0],*ri[1],rt[1]),resample=Image.Resampling.NEAREST)
missing = np.array(old_missing)>0
mapped_prop_array = np.array(new_prop_mapped)
repair = np.where(missing[:,:,None],mapped_prop_array,0).astype('uint8')
repair[(np.array(prop)[:,:,3]>=128)] = 0
Image.fromarray(repair).save(P/'production_layers/TRIAL_actual_prop_old_grip_occlusion_repair_NOT_ACCEPTED.png')
Image.fromarray(new_prop_raw).save(P/'production_layers/RAW_actual_prop_EXTRACTED_CONTEXT_NOT_WHOLE_ADOPTED.png')
Image.fromarray(missing.astype('uint8')*255).save(P/'masks/ORIGINAL_prop_hand_occlusion_missing_source_domain.png')
prop.alpha_composite(Image.fromarray(repair))
trial = Image.new('RGBA',mother.size)
# Actual frozen torso/sleeves naturally occlude the rear upper arm. Foreground
# new near arm is composited afterward; no raw clothing patch is taken.
for layer in [layers['far_complete_arm'], Image.fromarray(base), prop, layers['near_complete_arm']]:
    trial.alpha_composite(layer)
out = np.array(trial)
out[hard] = m[hard]
trial = Image.fromarray(out)
trial.save(P / 'candidate/F063_frozen044_arm_registration_TRIAL_NOT_ACCEPTED.png')
Image.fromarray(old.astype('uint8')*255).save(P / 'masks/F044_actual_old_arm_unit_removal_NOT_CLOTH_REPAINT.png')
Image.fromarray(hard.astype('uint8')*255).save(P / 'masks/F044_exact_head_ruffle_skirt_protection.png')
for tone, color in [('gray',(213,223,231,255)), ('dark',(35,43,52,255))]:
    bg = Image.new('RGBA', mother.size, color); bg.alpha_composite(trial)
    bg.save(P / f'qa/F063_frozen044_arm_registration_TRIAL_{tone}.png')
    bg.crop((620,565,1305,865)).resize((1370,600)).save(P / f'qa/F063_frozen044_sleeve_wrist_prop_seams_TRIAL_{tone}.png')

record = {'status':'INITIAL_REGISTERED_TRIAL_REQUIRES_ACTUAL_SEAM_REVIEW', 'mapping': {'common_whole_uniform_scale':scale,'offset':offset.tolist(),'no_segmented_limb_transform':True}, 'new_actual_raw_material_only':['near complete arm skin/hand/ink/AA','far complete arm skin/hand/ink/AA','necessary genuinely new tube material within original old-grip occlusion only'], 'prop_source':'original source044 genuine prop pixels rigidly rotated once in approved prior gate; no technical human pixels', 'raw_head_face_clothing_pixels_adopted':0, 'new_raw_silver_edge_adopted':0, 'necessary_new_actual_tube_repair_alpha128_pixels':int((repair[:,:,3]>=128).sum()), 'note':'Original genuine prop-only target already has its complete old source silver ring. Do not assert local raw prop or exact hand/prop registration without actual review. Correct original PRE063 stable skirt guard is used; the broader archived044 waist-region mask contains old skin and is not an all-clothing hard mask.', 'frozen_hard_RGBA_changes':int(np.any(out[hard]!=m[hard],axis=1).sum()), 'old_arm_unit_pixels_removed':int(old.sum()), 'actual_new_raw_near_pixels':int(near.sum()),'actual_new_raw_far_pixels':int(far.sum()), 'finished_candidate_accepted':False}
(P / 'qa/initial_registration_checks_NOT_PASS.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
