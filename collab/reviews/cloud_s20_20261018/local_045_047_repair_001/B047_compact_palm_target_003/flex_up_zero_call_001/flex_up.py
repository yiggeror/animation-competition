from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_fill_holes, map_coordinates

F=Path(__file__).resolve().parent; Q=F.parent; P=Q.parent; PACK=P.parent
SRC=Q/'rod_restore_zero_call_001'
B=np.array(Image.open(SRC/'F047_original_rods_restored_candidate.png').convert('RGBA'))
R=np.array(Image.open(Q/'generation_001/raw_original.png').convert('RGBA'))
H,W=B.shape[:2]; yy,xx=np.indices((H,W)); rh,rw=R.shape[:2]
ry,rx=np.indices((rh,rw)); factor=7.2; mx=840+rx/factor; my=260+ry/factor
mask=np.array(Image.open(P/'B047_continuous_palm_target/inputs/03_continuous_palm_wrist_jade_only_white.png').convert('L'))>127
rm=np.array(Image.fromarray(np.uint8(mask[260:420,840:1030])*255).resize((1368,1152),Image.Resampling.NEAREST))[:rh,:rw]>0
r,g,b=R[:,:,:3].astype(float).transpose(2,0,1)
skin=(R[:,:,3]>20)&(r>150)&(g>85)&(b>g*.67)&(r>g+9)
jade=(R[:,:,3]>20)&(g>r*1.05)&(g>b*1.04)
eligible=(R[:,:,3]>8)&rm; selected=np.zeros((rh,rw),bool)
for x in range(max(0,int((915-840)*factor)),min(rw,int((1022-840)*factor))):
    ys=np.flatnonzero(eligible[:,x]); pieces=np.split(ys,np.where(np.diff(ys)>1)[0]+1)
    for piece in pieces:
        if len(piece) and np.any((skin|jade)[piece,x]):
            selected[max(0,int(piece[0])-2):min(rh,int(piece[-1])+3),x]=True; break
selected=binary_dilation(selected,iterations=2)&rm&(R[:,:,3]>0)
native=R.copy(); native[:,:,3][~selected]=0

def smooth(t):
    t=np.clip(t,0,1); return t*t*t*(t*(t*6-15)+10)

pin=(929.,317.5435399321609)
def up(x,y):
    # One C2 continuous deformation for the complete native palm/fingers.
    # The pinch neighbourhood and all jade/wrist pixels are true zero anchors.
    radial=smooth((np.hypot(x-pin[0],y-pin[1])-6.)/8.)
    wrist=1-smooth((x-954.)/9.)
    left=smooth((x-915.)/6.)
    return 3.8*radial*wrist*left

dest_y=ry.astype(float)
source_y=dest_y.copy()
for _ in range(10): source_y=dest_y+factor*up(mx,260+source_y/factor)
alpha=native[:,:,3].astype(float)/255
premult=native[:,:,:3].astype(float)*alpha[:,:,None]
warped_a=map_coordinates(alpha,[source_y,rx],order=3,mode='constant',cval=0,prefilter=True).clip(0,1)
warped_rgb=np.stack([map_coordinates(premult[:,:,c],[source_y,rx],order=3,mode='constant',cval=0,prefilter=True) for c in range(3)],2)
warped=np.zeros_like(native)
warped[:,:,:3]=np.rint(np.divide(warped_rgb,warped_a[:,:,None],out=np.zeros_like(warped_rgb),where=warped_a[:,:,None]>1e-6)).clip(0,255).astype('uint8')
warped[:,:,3]=np.rint(warped_a*255).astype('uint8')
warped[up(mx,my)==0]=native[up(mx,my)==0]

def master(raw):
    c=Image.new('RGBA',(1368,1152)); c.alpha_composite(Image.fromarray(raw))
    out=np.zeros_like(B); out[260:420,840:1030]=np.array(c.resize((190,160),Image.Resampling.LANCZOS)); return out

original=master(native); human=master(warped)
assert np.array_equal(original,np.array(Image.open(SRC/'unchanged_native_upper_hand_layer.png').convert('RGBA')))
Image.fromarray(human).save(F/'continuous_native_upper_hand_layer.png')
axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods']
prop=Image.new('RGBA',(W*4,H*4)); d=ImageDraw.Draw(prop)
for role in ['C_N','C_B']:
    q=axes[role]; start=q['shaft_tip_master_px']; end=[952,q['slope']*952+q['intercept']]
    pts=[tuple(v*4 for v in start),tuple(v*4 for v in end)]
    d.line(pts,fill='#675034',width=16); d.line(pts,fill='#b28b52',width=10)
props=prop.resize((W,H),Image.Resampling.LANCZOS)
patch=np.array(Image.alpha_composite(props,Image.fromarray(human)))
changed=(original[:,:,3]!=human[:,:,3])|(np.any(original[:,:,:3]!=human[:,:,:3],2)&((original[:,:,3]>0)|(human[:,:,3]>0)))
domain=binary_dilation(changed,iterations=1)&(xx>=915)&(xx<965)&(yy>=270)&(yy<350)
# Keep the whole native fixed pinch neighbourhood byte-exact, including its rod.
pin_fixed=(np.hypot(xx-pin[0],yy-pin[1])<=4.)
domain &= ~pin_fixed
out=B.copy();out[domain]=patch[domain]
br,bg,bb=B[:,:,:3].astype(float).transpose(2,0,1)
right_core=(B[:,:,3]>60)&(br>150)&(bg>85)&(bb>bg*.67)&(br>bg+9)&(xx<918)&(yy>326)&(yy<377)
right=(B[:,:,3]>0)&binary_dilation(binary_fill_holes(right_core),iterations=2)&(xx<918)&(yy>326)&(yy<377)
out[right]=B[right]
Image.fromarray(out).save(F/'F047_continuous_flex_up_candidate.png')
gray=Image.new('RGBA',(W,H),'#bdc1c4');gray.alpha_composite(Image.fromarray(out))
gray.convert('RGB').save(F/'actual_full_gray.jpg',quality=96)
crop=gray.crop((840,260,1030,420)).convert('RGB');crop.save(F/'actual_contacts_1x.png')
crop.resize((760,640),Image.Resampling.NEAREST).save(F/'actual_contacts_4x.png')
assert np.array_equal(out[:,965:],B[:,965:])
assert np.array_equal(out[pin_fixed],B[pin_fixed])
assert np.array_equal(out[~domain],B[~domain])
assert np.array_equal(out[:,:835],B[:,:835])
stats={'status':'ONE_ZERO_CALL_CONTINUOUS_NATIVE_HAND_FLEX_CANDIDATE_ASTRA_GATE_PENDING','new_image_calls':0,'source_commit':'c04f3420a3054730fbba6f68875826dbbc27c605','source_raw_sha256':hashlib.sha256((Q/'generation_001/raw_original.png').read_bytes()).hexdigest(),'maximum_palm_and_fingers_lift_px':3.8,'single_continuous_field_no_finger_cuts':True,'fixed_clamp':list(pin),'fixed_clamp_RGBA_exact':True,'jade_and_wrist_x965_plus_RGBA_exact':True,'same_original_rod_layer_width_px':4,'CB_fixed_finite_endpoint':[952,axes['C_B']['slope']*952+axes['C_B']['intercept']],'source_sampling':'original resolution, premultiplied cubic inverse of continuous displacement; same pad/uniform inverse as source','changed_master_pixels':int(np.any(out!=B,2).sum()),'adopted':False,'propagated':False}
(F/'status.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(stats,ensure_ascii=False))
