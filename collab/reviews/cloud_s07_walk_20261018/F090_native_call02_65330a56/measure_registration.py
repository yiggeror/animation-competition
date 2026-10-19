"""Measure the actual call02 under the approved whole inverse only; no fit."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label

P=Path(__file__).resolve().parent
F=P/'frozen_input_65330a56'
expected=Image.open(F/'sources/approved_reference_native/A_real_five_layers_no_old_pants_540x810.png').convert('RGBA')
actual=Image.open(P/'originals/F090_call02_RAW.png').convert('RGBA').resize((540,810),Image.Resampling.LANCZOS)


def soles(im):
    a=np.array(im);rgb=a[:,:,:3].astype(int)
    mask=(a[:,:,3]>=128)&(rgb.min(axis=2)>145)&(np.ptp(rgb,axis=2)<65)
    mask[:735]=False;mask[790:]=False
    labs,count=label(mask);rows=[]
    for i in range(1,count+1):
        y,x=np.where(labs==i)
        if len(x)>150:rows.append({'pixels':len(x),'bbox_native_crop_local_halfopen':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],'centroid_xy':[float(x.mean()),float(y.mean())]})
    return sorted(rows,key=lambda v:v['centroid_xy'][0])


def blouse(im):
    a=np.array(im);r=a[:,:,:3].astype(int)
    z=(a[:,:,3]>=128)&(r[:,:,2]>110)&(r[:,:,2]-r[:,:,0]>20)&(r[:,:,1]-r[:,:,0]>12)
    z[320:]=False
    labs,_=label(z);counts=np.bincount(labs.ravel());counts[0]=0
    y,x=np.where(labs==counts.argmax())
    return {'actual_blue_material_bbox_native_crop_local_halfopen':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1],'centroid_xy':[float(x.mean()),float(y.mean())],'pixels':len(x)}


e=soles(expected);a=soles(actual)
assert len(e)==len(a)==2
delta=[[a[i]['centroid_xy'][j]-e[i]['centroid_xy'][j]for j in range(2)]for i in range(2)]
eb=blouse(expected);ab=blouse(actual)
record={'status':'ACTUAL_MEASUREMENTS_ONLY_REQUIRES_VISUAL_VOLUME_AND_SEAM_REVIEW','fixed_transform':'whole135/256 ->540x810; native origin1080,250; no fitting','frozen_sole_material_components':e,'actual_sole_material_components':a,'actual_minus_frozen_sole_material_centroid_delta_native_px':delta,'frozen_blouse_blue_material':eb,'actual_blouse_blue_material':ab,'measurement_limits':'Material centers and bboxes are not anatomical ankle, pelvis or bone measurements. Threshold masks measure actual visible alpha128 material; no hidden shoe-layer alpha or technical volume used.'}
(P/'qa/actual_shoe_and_blouse_registration.json').write_text(json.dumps(record,indent=2)+'\n')
bg=Image.new('RGBA',(540,810),(35,43,52,255));bg.alpha_composite(actual);d=ImageDraw.Draw(bg)
for rows,col in [(e,'cyan'),(a,'orange')]:
    for row in rows:d.rectangle(tuple(row['bbox_native_crop_local_halfopen']),outline=col,width=1)
bg.crop((60,685,530,795)).resize((1410,330)).save(P/'qa/expected_cyan_actual_orange_soles_call02.png')
print(json.dumps(record))
