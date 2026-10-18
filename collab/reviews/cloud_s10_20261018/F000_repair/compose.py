"""Attach only the authorized generated lower-chest band. Upper image stays byte-identical."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

P=Path(__file__).resolve().parent
base=np.array(Image.open(P/'prepared/F000_registered_clean.png').convert('RGBA'))
donor=np.array(Image.open(P/'prepared/cloth_donor_registered_crop.png').convert('RGBA'))
out=base.copy(); changed_allowed=np.array(Image.open(P/'masks/authorized_band_y978_1079.png'))>0
band=np.zeros_like(base); row_maps=[]
for gy in range(978,1080):
    cy=gy-824
    valid=np.flatnonzero(donor[cy,:,3]>=128)
    sl,sr=float(valid.min()),float(valid.max())
    dl=69.-.47*(gy-978);dr=951.+.47*(gy-978)
    x=np.arange(1024,dtype=float)
    sx=sl+(x-dl)*(sr-sl)/(dr-dl)
    # This tiny contour adjustment applies only to newly generated cloth, never the original person.
    premul=donor[cy,:,:3].astype(float)*(donor[cy,:,3:4]/255.)
    alpha=ndi.map_coordinates(donor[cy,:,3].astype(float),[sx],order=1,mode='constant',cval=0)
    colors=np.column_stack([ndi.map_coordinates(premul[:,c],[sx],order=1,mode='constant',cval=0) for c in range(3)])
    colors=np.divide(colors,alpha[:,None]/255.,out=np.zeros_like(colors),where=alpha[:,None]>0)
    pixels=np.column_stack((colors,alpha)).clip(0,255).round().astype('uint8')
    band[gy,448:1472]=pixels
    row_maps.append({'canvas_y':gy,'donor_crop_y':cy,'donor_left_right':[sl,sr],'target_left_right':[dl,dr]})
out[changed_allowed]=band[changed_allowed]
assert np.array_equal(out[:978],base[:978])
assert np.array_equal(out[~changed_allowed],base[~changed_allowed])
unblended=out.copy()
Image.fromarray(out).save(P/'qa/F000_unblended_band.png')
Image.fromarray(band).save(P/'prepared/generated_band_registered.png')
# Match only the new blue fabric's low-frequency tone. Preserve the generated
# flower and contour shapes; a per-column high-frequency correction would smear petals.
blue=(base[977,:,3]>240)&(out[978,:,3]>240)&(base[977,:,2].astype(float)-base[977,:,0]>30)&(out[978,:,2].astype(float)-out[978,:,0]>30)&(base[977,:,0]>60)&(out[978,:,0]>60)
offset=np.median(base[977,blue,:3].astype(float)-out[978,blue,:3].astype(float),axis=0)
for gy in range(978,1026):
    weight=(1.-(gy-978)/48.)**2
    colors=out[gy,:,:3].astype(float)
    chroma=colors.max(1)-colors.min(1)
    fabric=np.clip((chroma-20)/30,0,1)*np.clip((colors[:,2]-colors[:,0]-15)/30,0,1)*np.clip(colors.min(1)/80,0,1)
    use=changed_allowed[gy]
    out[gy,use,:3]=(colors[use]+offset[None,:]*fabric[use,None]*weight).clip(0,255).round().astype('uint8')
assert np.array_equal(out[:978],base[:978])
assert np.array_equal(out[~changed_allowed],base[~changed_allowed])
Image.fromarray(out).save(P/'candidate/F000_repaired.png')
Image.fromarray(out[930:1026,450:1470]).save(P/'qa/chest_join_native.png')
Image.fromarray(((out!=base).any(2)*255).astype('uint8')).save(P/'masks/actual_new_band_pixels.png')
# Compare continuous cloth body at the seam, excluding outer transparency.
inside=(base[977,:,3]>240)&(out[978,:,3]>240)
delta=np.abs(unblended[978,inside,:3].astype(int)-base[977,inside,:3].astype(int))
info={'status':'assembled_pending_visual_check','candidate':'candidate/F000_repaired.png',
      'sha256':hashlib.sha256((P/'candidate/F000_repaired.png').read_bytes()).hexdigest(),
      'new_pixel_range_y':[978,1079],
      'generated_pixels_adopted_above_y978':0,
      'changed_pixels_outside_authorized_mask':0,
      'all_RGBA_pixels_y0_977_identical_to_registered_clean_source':True,
      'donor_uniform_registration_file':'provenance/cloth_donor_registration.json',
      'local_new_band_contour_adjustment':'row-wise x mapping between donor alpha>=128 outline and continuation x=517-.47*(y-978), 1399+.47*(y-978); affects only new generated band',
      'row_maps':row_maps,
      'unblended_seam_RGB_absolute_delta_median':float(np.median(delta)),
      'unblended_seam_RGB_absolute_delta_mean':float(delta.mean()),
      'new_band_colour_join':'rows978-1025 only: add median blue-fabric RGB offset, excluding white petals and black contours, with quadratic weight (1-(y-978)/48)^2; original y<978 unchanged',
      'blue_fabric_RGB_offset':offset.tolist(),
      'full_person_regeneration':False,'new_pose_generation':False}
(P/'provenance/band_composition.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in info.items() if k!='row_maps'})
