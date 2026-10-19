"""Only the approved neck chroma patch and exactly 346 exterior alpha=1 points.
No image model calls. Run from any cwd; the previous master is read-only.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'semantic_repair_001_call003/S20_F000_call003_semantic_repair_candidate.png'
EXPECTED = '423715194ffaa08e867a0e1e3c6f6febe5de703e6c84fb2dc26d282ab6139943'
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == EXPECTED
im = Image.open(SRC).convert('RGBA'); src = np.array(im); out = src.copy()
h,w = src.shape[:2]; yy,xx=np.mgrid[:h,:w]
(HERE/'cleanup').mkdir(exist_ok=True); (HERE/'qa').mkdir(exist_ok=True)

# Hand traced INSIDE the neck plane. The jaw/face/hair/collar AA is outside.
poly = [(1081,217),(1088,212),(1098,202),(1107,195),(1112,200),
        (1120,203),(1125,214),(1127,219),(1115,229),(1102,240),
        (1084,257),(1084,249),(1089,235),(1089,227)]
p = Image.new('L',im.size); ImageDraw.Draw(p).polygon(poly,fill=255)
rgb=src[:,:,:3].astype(float); R,G,B=np.moveaxis(rgb,2,0)
inside=(np.array(p)>0)&(src[:,:,3]>=250)&(R>160)&(R-G>25)&(G-B>16)
inside &= (xx>=1077)&(xx<1138)&(yy>=190)&(yy<268)
feather=np.clip((distance_transform_edt(inside)-1)/3,0,1)
Y=rgb @ np.array([.2126,.7152,.0722])
ref=(rgb[221,1110]+rgb[229,1106])/2
refY=ref @ np.array([.2126,.7152,.0722])
target=ref[None,None,:]*(Y/refY)[:,:,None]
# A maximum 42% neutralisation of excess orange. Keep the original shadow Y.
excess=(R-G)-(ref[0]-ref[1])*(Y/refY)-4
weight=np.clip(excess/18,0,.42)*feather
fixed=np.clip(np.rint(rgb+(target-rgb)*weight[:,:,None]),0,255).astype('uint8')
neck=(weight>0)&np.any(fixed!=src[:,:,:3],axis=2)
out[neck,:3]=fixed[neck]

exterior=~((xx>=450)&(xx<1245)&(yy>=30)&(yy<930))
stray=(src[:,:,3]==1)&exterior
assert int(stray.sum()) == 346, int(stray.sum())
out[stray]=0
changed=np.any(src!=out,axis=2)
assert np.array_equal(changed,neck|stray)
assert np.array_equal(src[:,:,3][~stray],out[:,:,3][~stray])
assert not np.any(neck&~inside)
final=HERE/'cleanup/S20_F000_master_clean.png'
Image.fromarray(out).save(final)
for name,mask in [('neck_chroma_changed',neck),('alpha1_exterior_346',stray),('all_changed',changed)]:
    Image.fromarray((mask*255).astype('uint8')).save(HERE/f'cleanup/mask_{name}.png')

box=(1064,182,1143,272)
panel=Image.new('RGB',(79*6*2,90*6+30),'#ddd')
for j,a in enumerate((src,out)):
    tile=Image.fromarray(a).crop(box)
    bg=Image.new('RGBA',tile.size,'#888'); bg.alpha_composite(tile)
    panel.paste(bg.convert('RGB').resize((79*6,90*6),Image.Resampling.NEAREST),(j*79*6,30))
d=ImageDraw.Draw(panel); d.text((10,8),'BEFORE 423715',fill='black'); d.text((79*6+10,8),'AFTER / same luminance',fill='black')
panel.save(HERE/'qa/neck_before_after.png')

deltaY=(out[:,:,:3].astype(float)-rgb)@np.array([.2126,.7152,.0722])
report={
 'source':str(SRC.relative_to(HERE.parent)), 'source_sha256':EXPECTED,
 'final':'cleanup/S20_F000_master_clean.png','final_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
 'dimensions':[w,h], 'neck_bbox_limit':[1077,190,1138,268], 'neck_interior_polygon':poly,
 'same_plane_reference_pixels':[[1110,221],[1106,229]], 'neck_changed_pixels':int(neck.sum()),
 'neck_max_abs_luma_delta_8bit':float(np.abs(deltaY[neck]).max()),
 'neck_mean_luma_delta_8bit':float(deltaY[neck].mean()),
 'exterior_alpha1_removed':346,'exterior_rectangle_half_open':[450,30,1245,930],
 'alpha_changed_elsewhere':0,'RGBA_changed_outside_two_masks':0,
 'inside_rectangle_RGBA_changes_except_neck':0,
 'new_model_calls':0,'historical_model_calls':3,'new_later_states':0,
 'operation':'Limited luminance-preserving chroma attenuation; no smoothing or geometric change. Exterior alpha1 points only set to RGBA zero.'
}
(HERE/'cleanup/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
