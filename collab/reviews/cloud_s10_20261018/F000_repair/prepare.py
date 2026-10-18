"""User-authorized pixel preparation only; never redraws a person or their head."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

P=Path(__file__).resolve().parent
RAW=P.parent/'F000_first/originals/F000_call01_raw.png'
S=.918;TX=171.;TY=114.
v=np.array(Image.open(RAW).convert('RGBA'));a=v[:,:,3];rgb=v[:,:,:3].astype(int)
ch=np.ptp(rgb,axis=2)
yy,xx=np.indices(a.shape)
hair=(xx>=500)&(xx<=1185)&(yy<=670)&(ch<=45)
red=(xx>=520)&(xx<=600)&(yy>=355)&(yy<=470)
protected=hair|red
labels,n=ndi.label(a>0,structure=ndi.generate_binary_structure(2,1))
areas=np.bincount(labels.ravel());areas[0]=0;main=int(areas.argmax())
max_alpha=ndi.maximum(a,labels,index=np.arange(n+1))
isolated=(labels>0)&(labels!=main)&(max_alpha[labels]<=8)&~protected
distance=ndi.distance_transform_edt(a<128)
# A contextual exterior-only mask; not a whole-image alpha threshold.
exterior_colour=(a>0)&(a<=24)&(ch>=60)&(distance>1.5)&~protected
cleanup=isolated|exterior_colour
clean=v.copy();clean[:,:,3][cleanup]=0
assert np.array_equal(clean[:,:,:3],v[:,:,:3])
assert np.array_equal(clean[a>24],v[a>24])
assert not np.any(cleanup&protected)
Image.fromarray((cleanup*255).astype('uint8')).save(P/'masks/source_alpha_cleanup.png')
Image.fromarray((protected*255).astype('uint8')).save(P/'masks/source_hair_red_protection.png')
Image.fromarray(clean).save(P/'prepared/F000_source_alpha_clean_only.png')
inverse=(1/S,0,-TX/S,0,1/S,-TY/S)
def affine(array):
    # Pillow RGBA affine internally resamples premultiplied alpha. One uniform transform.
    return Image.fromarray(array).transform((1920,1080),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC)
registered=affine(clean);before=affine(v)
registered.save(P/'prepared/F000_registered_clean.png')
before.save(P/'prepared/F000_registered_before_alpha_cleanup.png')
# Local upper-chest input only: no head/face. The upper part includes a little
# lower-neck/collar context; generated pixels are only eligible below y978.
registered.crop((448,824,1472,1080)).save(P/'inputs/lower_chest_crop_1024x256.png')
# Authorized new-pixel envelope; the lower shirt edges continue their original slope.
X,Y=np.meshgrid(np.arange(1920)+.5,np.arange(1080)+.5)
left=517.-.47*(Y-978.);right=1399.+.47*(Y-978.)
allowed=(Y>=978)&(X>=left)&(X<=right)
Image.fromarray((allowed*255).astype('uint8')).save(P/'masks/authorized_band_y978_1079.png')
info={
 'source':str(RAW.relative_to(P.parent)),
 'source_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
 'source_size':[1672,941],'canvas':[1920,1080],
 'uniform_affine':[[S,0,TX],[0,S,TY],[0,0,1]],
 'inverse_affine_Pillow':list(inverse),
 'sampling':'one full-image RGBA affine BICUBIC, premultiplied alpha; no separate head transform',
 'coordinate_notes':'continuous source coordinates; raster support varies up to filter footprint',
 'anchors':{'source_crown_y':12,'target_crown_y':12*S+TY,'source_chin_y':671,'target_chin_y':671*S+TY},
 'original_bottom_continuous_y':941*S+TY,
 'band_top':978,'band_bottom_inclusive':1079,
 'band_top_left_right':[517,1399],'band_edge_dx_per_dy':.47,
 'cloth_only_request_crop':[448,824,1472,1080],
 'alpha_cleanup':{'pixel_count':int(cleanup.sum()),'isolated_particle_pixels':int(isolated.sum()),
   'local_exterior_colour_pixels':int(exterior_colour.sum()),
   'maximum_alpha_removed':int(a[cleanup].max()) if cleanup.any() else 0,
   'source_RGB_changed_pixels':0,'source_alpha_above_24_changed_pixels':0,
   'protected_gray_black_hair_and_left_red_beads_changed_pixels':0,
   'method':'isolated non-main 4-connected components max alpha<=8, except protected gray/black hair and left red beads; plus exterior low alpha<=24 chroma>=60 >1.5px from alpha>=128 core, except protected areas',
   'not_done':'no global alpha<128 cut; no 253/254 material alpha change; no face/neck RGB edits'},
 'band_generation_calls':0,'status':'prepared_not_final'}
(P/'provenance/transform_and_cleanup.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(info,ensure_ascii=False,indent=2))
