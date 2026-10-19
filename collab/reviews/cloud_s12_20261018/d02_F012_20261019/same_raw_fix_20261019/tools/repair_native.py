"""Authorized same-raw static BLUE R-only correction; native pose stays exact."""
from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt,binary_dilation,maximum_filter,minimum_filter,gaussian_filter
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent
for q in ['candidate','masks','qa','provenance','contact_masks','scene','actual_scene']: (O/q).mkdir(exist_ok=True)
raw=P/'originals/F012_raw_call01.png';mother=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(raw)=='52c6faf1e5eda14c2930ca557b5d1624a4dea86853f8dd631dd950b7b0d89f2c'
assert sha(mother)=='95f80f2d8f56394abd4a808cc8a6f205633658a544de4ab52e1e34c4ac1ed793'
a=np.array(Image.open(raw).convert('RGBA'));m=np.array(Image.open(mother).convert('RGBA'));rgb=a[:,:,:3].astype(np.int16);alpha=a[:,:,3];out=a.copy()
def poly(pts):
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon([tuple(v) for v in pts],fill=255);return np.array(im)>0
whole=np.array(Image.open(S/'d01_F000/same_raw_fix_20261019/masks/blouse_semantic_area.png'))>0
polys={
 'far_sleeve_UNCHANGED':[(603,635),(645,657),(692,703),(729,740),(729,779),(690,816),(634,843),(594,821),(591,766)],
 'near_sleeve':[(436,663),(482,644),(524,648),(560,677),(578,736),(588,808),(596,869),(580,887),(446,890),(432,813),(426,728)],
 'collar_front':[(507,544),(605,580),(658,653),(658,781),(616,853),(566,917),(513,965),(533,1039),(493,1070),(474,1006),(496,938),(521,889),(552,841),(552,734),(521,662)]}
# Mutually exclusive measured physical faces, before any correction.
faces={};assigned=np.zeros(alpha.shape,bool)
for name in ['far_sleeve_UNCHANGED','near_sleeve','collar_front']:
 faces[name]=poly(polys[name])&whole&~assigned;assigned|=faces[name]
yy,xx=np.indices(alpha.shape)
faces['lower_hem']=(yy>=970)&whole&~assigned;assigned|=faces['lower_hem']
faces['back_waist']=whole&~assigned
source=[rgb,m[:,:,:3].astype(np.int16)]
def pigment(x):return (x[:,:,0]>65)&(x[:,:,2]>x[:,:,0]+20)&(x[:,:,2]>x[:,:,1]+15)&(np.max(x,2)>120)
selected=whole&pigment(rgb)&(alpha>=8)
# Preserve linework, flowers, dark fold boundaries; retain the existing form gradient via additive R only.
lo=minimum_filter(rgb,size=(3,3,1));hi=maximum_filter(rgb,size=(3,3,1))
ink=(np.max(rgb,2)<120)&(alpha>=8)
ridge=(np.max(hi-lo,2)>38)&(np.min(rgb,2)<150)&(alpha>=8)
line_protect=binary_dilation(ink|ridge,iterations=1)
flowers=binary_dilation((np.min(rgb,2)>210)&(np.max(rgb,2)-np.min(rgb,2)<35)&whole&(alpha>=8),iterations=1)
far_protect=binary_dilation(faces['far_sleeve_UNCHANGED'],iterations=2)
editable=selected&~line_protect&~flowers&~far_protect
edge_weight=np.clip(distance_transform_edt(editable)/2,0,1);edge_weight[~editable]=0
# Smooth physical face transitions (sigma6native px); R reductions only3..4.
reductions={'near_sleeve':4.,'back_waist':4.,'lower_hem':4.,'collar_front':4.}
num=np.zeros(alpha.shape,float);den=np.zeros(alpha.shape,float)
for name,amount in reductions.items():
 smooth=gaussian_filter(faces[name].astype(float),6);num+=amount*smooth;den+=smooth
field=np.divide(num,den,out=np.zeros_like(num),where=den>1e-8)
weight=edge_weight*np.clip(distance_transform_edt(~far_protect)/6,0,1)
out[:,:,0]=np.clip(np.rint(rgb[:,:,0]-field*weight),0,255).astype(np.uint8)
# Remove only detached alpha1..7 farther than3px from alpha>=8, preserving all fine head/glasses alpha.
solid=alpha>=8;dist=distance_transform_edt(~solid)
head_guard=(xx>=410)&(xx<=825)&(yy>=312)&(yy<=650)
remove=(alpha>0)&(alpha<8)&(dist>3)&~head_guard&~far_protect
out[remove,3]=0
changed=np.any(out[:,:,:3]!=a[:,:,:3],2)
assert np.array_equal(out[:,:,1:3],a[:,:,1:3])
assert not np.any(changed&~selected) and not np.any(changed&far_protect)
assert not np.any(changed&(line_protect|flowers))
assert np.array_equal(out[:,:,3][solid],alpha[solid])
assert np.array_equal(out[head_guard,3],a[head_guard,3])
assert np.array_equal(out[far_protect],a[far_protect])
assert np.max(rgb[:,:,0]-out[:,:,0].astype(np.int16))<=4
Image.fromarray(out).save(O/'candidate/F012.png')
for name,arr in [('R_changed',changed),('alpha_removed',remove),('protected_lineart_and_fold_ridges',line_protect),('protected_white_flowers',flowers),('far_sleeve_UNCHANGED',far_protect),('fine_head_alpha_guard',head_guard),('blue_full_pigment_measurement',selected)]:Image.fromarray(arr.astype(np.uint8)*255).save(O/f'masks/{name}.png')
Image.fromarray(np.rint(weight*255).astype(np.uint8)).save(O/'masks/R_edit_weight.png')
Image.fromarray(np.maximum(rgb[:,:,0]-out[:,:,0].astype(np.int16),0).astype(np.uint8)).save(O/'masks/R_reduction_levels0to4.png')
measure={};font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
for name,area in faces.items():
 Image.fromarray(area.astype(np.uint8)*255).save(O/f'masks/face_{name}.png')
 sels=[area&pigment(v)&(aa[:,:,3]>=128) for v,aa in [(m[:,:,:3].astype(np.int16),m),(rgb,a)]]
 means=[m[sels[0],:3].mean(0),a[sels[1],:3].mean(0),out[sels[1],:3].mean(0)]
 measure[name]={'mother_pixels':int(sels[0].sum()),'F012_measure_pixels':int(sels[1].sum()),'mother_mean_RGB':means[0].tolist(),'raw_mean_RGB':means[1].tolist(),'corrected_mean_RGB':means[2].tolist(),'raw_delta_vs_mother':(means[1]-means[0]).tolist(),'corrected_delta_vs_mother':(means[2]-means[0]).tolist(),'corrected_R_within4':bool(abs(means[2][0]-means[0][0])<=4),'RGBA_exact_raw_on_entire_face':bool(np.array_equal(out[area],a[area]))}
fullmask=np.array(Image.open(P/'qa/masks/raw_F012_blouse_blue.png'))>0
fullmother=np.array(Image.open(P/'qa/masks/locked_F000_blouse_blue.png'))>0
full_before=a[fullmask,:3].mean(0);full_after=out[fullmask,:3].mean(0);full_target=m[fullmother,:3].mean(0)
report={'source_raw_SHA256':sha(raw),'mother_SHA256':sha(mother),'corrected_candidate_SHA256':sha(O/'candidate/F012.png'),'imagegen_calls_this_task':0,'new_poses':0,'RGB_channels_changed':['R'],'R_changed_pixels':int(changed.sum()),'max_R_reduction':int(np.max(rgb[:,:,0]-out[:,:,0].astype(np.int16))),'G_B_exact_raw':True,'alpha_ge8_exact_raw':True,'all_head_guard_alpha_exact_raw':True,'lineart_fold_ridges_white_flowers_exact_raw':True,'far_sleeve_RGBA_exact_raw':bool(np.array_equal(out[far_protect],a[far_protect])),'RGB_outside_selected_blue_exact_raw':True,'pose_registration_or_geometry_transforms':0,'removed_alpha1to7_pixels':int(remove.sum()),'removed_original_alpha_values':np.unique(alpha[remove]).tolist(),'removed_alpha_RGB_exact_raw':True,'full_blue_measured_pixels':int(fullmask.sum()),'full_blue_raw_delta_vs_mother':(full_before-full_target).tolist(),'full_blue_corrected_delta_vs_mother':(full_after-full_target).tolist(),'full_blue_all_channels_within4':bool(np.max(abs(full_after-full_target))<=4),'face_measurements':measure,'face_R_reductions_requested':reductions,'face_boundary_blur_sigma_native_px':6,'edit_boundary_feather_native_px':2,'head_guard_bbox':[410,312,826,651]}
(O/'qa/native_repair_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(O/'qa/region_definitions.json').write_text(json.dumps({'polygons_native':polys,'partition_priority':['far_sleeve_UNCHANGED','near_sleeve','collar_front','lower_hem_y_ge970','remaining_back_waist'],'measurement':'Physical face area plus per-image blue pigment predicate; fixed rawF012 selection for raw/corrected comparison. G/B not changed. Whole-face means include protected ink/flower boundary blue pixels.','blue_predicate':'R>65, B>R+20, B>G+15, maxRGB>120; alpha>=128 for color means. Edit support usesalpha>=8.','source_parent_review_R_deltas':{'near_sleeve':6.51,'back_waist':6.03,'lower_hem':6.23,'collar_front':5.22,'far_sleeve':3.10},'parent_and_local_partition_note':'Parent exact masks were not supplied; local complete physical-face boundaries are saved explicitly. Local means need not equal parent sample means.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
