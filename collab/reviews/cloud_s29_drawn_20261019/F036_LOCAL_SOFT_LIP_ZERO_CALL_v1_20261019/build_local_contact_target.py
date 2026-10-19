"""Zero-call technical local target, not a native drawing or production patch.
Actual030 supplies the body; 694f59b supplies its reviewed inward arm probe.
Replace the old hard guide edge with an opaque textured rolled cloth surface.
"""
from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,'/tmp/s29-image-tools')
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.spatial import cKDTree

R=Path(__file__).resolve().parent;B=R.parent
P=B/'F036_REBUILD_FROM_ACTUAL030_ZERO_CALL_v1_20261019'
rawpath=B/'F030_REPAIR_NATIVE_call01_20261019/originals/S29_F030_REPAIR_call01_RAW_UNTOUCHED.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(rawpath)=='0c182aa0d62acf8647daa316e06cdb4bfdd9ebd6c2e6c02f1b0e2f8065ffd4e5'
raw=Image.open(rawpath).convert('RGBA');a=np.array(raw);H,W=a.shape[:2];yy,xx=np.indices((H,W))
target=np.array(Image.open(P/'layers/NEW_F036_FROM_ACTUAL030_TECHNICAL_PROBE_NOT_NATIVE.png').convert('RGBA'))
props=np.array(Image.open(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png').convert('RGBA'))
cotton=np.array(Image.open(P/'layers/ACTUAL030_CLOTH_CONTEXT_BASE_TECHNICAL_ONLY.png').convert('RGBA'))
arm=np.array(Image.open(P/'layers/COMPLETE_ACTUAL030_ARM_CONTINUOUS_TECHNICAL_PROBE_NOT_ART.png').convert('RGBA'))
oldlip=np.array(Image.open(P/'masks/NEW_FRONT_LIP_CONTINUOUS_FACE.png'))>0
near=np.array(Image.open(P/'masks/NEAR_BARE_RIGHT_ARM_PROTECTED.png'))>0
oldmove=np.array(Image.open(P/'masks/COMPLETE_MOVEMENT_DOMAIN.png'))>0
tail=np.array(Image.open(P/'masks/TRUE_OUTER_FEATHER_LINES_COMMON030.png'))>0
core=np.array(Image.open(P/'masks/TRUE_TAIL_CORE_COMMON030.png'))>0
A=np.array([731.,673.]);N=np.array([711.,670.])

# Undo the previous flat tongue/black crossguide only in its cotton pixels.
weight=np.clip((960-yy)/280,0,1)*np.clip((xx-500)/150,0,1)
mx=(xx+20*weight).astype('float32');my=(yy+3*weight).astype('float32')
cloth=cv2.remap(cotton,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
donor=a[813:860,540:607,:3]
dy=yy%(2*donor.shape[0]);dx=xx%(2*donor.shape[1])
dy=np.minimum(dy,2*donor.shape[0]-1-dy);dx=np.minimum(dx,2*donor.shape[1]-1-dx);tile=donor[dy,dx]
cloth[(cloth[:,:,3]<190)&oldlip,:3]=tile[(cloth[:,:,3]<190)&oldlip]
cloth[oldlip,3]=255
human=(arm[:,:,3]>160)|near
repair=oldlip&~human
target[repair]=cloth[repair]
restore=np.zeros_like(target);restore[repair]=props[repair]
target=np.array(Image.alpha_composite(Image.fromarray(target),Image.fromarray(restore)))

def cubic(p0,p1,p2,p3,n=180):
 t=np.linspace(0,1,n)[:,None]
 return (1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)

# A soft edge bows away from the puppet body, then turns onto OUTER tips.
# Full cloth face remains behind it. This is a shaded surface, no ink guide.
edge=np.vstack([cubic(N+[0,5],[772,691],[810,768],[824,786]),cubic([824,786],[842,805],[875,805],[902,841])[1:]])
tangent=np.gradient(edge,axis=0);normal=np.c_[-tangent[:,1],tangent[:,0]]
normal/=np.linalg.norm(normal,axis=1)[:,None]
u=np.linspace(0,1,len(edge));width=2+22*np.sin(np.pi*u)**0.75
outer=edge+normal*width[:,None]
poly=np.vstack([edge,outer[::-1]])
mi=Image.new('L',(W,H));ImageDraw.Draw(mi).polygon([tuple(p) for p in poly],fill=255)
lip=np.array(mi)>0
# Permit outer feather tips only. All unchanged bodies/rods are foreground.
allowed=tail&(xx>=812)&(yy>=783)&(xx<=885)&(yy<=839)
cover=(props[:,:,3]>0)&lip&allowed
front=lip&~((props[:,:,3]>0)&~cover)&~human
q=np.c_[xx[front],yy[front]];_,ind=cKDTree(edge).query(q)
depth=np.sum((q-edge[ind])*normal[ind],axis=1)/width[ind]
depth=np.clip(depth,0,1)
# Lit rounded thickness, broad dark inside, and a soft transition to cotton.
stops=np.array([0,.12,.29,.48,.73,1.])
factors=np.array([.94,1.16,.84,.52,.76,1.])
factor=np.interp(depth,stops,factors)
material=tile[front].astype(float)*.55+np.array([43,62,108])*.45
surface=material*factor[:,None]
rim=np.exp(-((depth-.10)/.11)**2)[:,None]
surface+=rim*np.array([4,6,9])
base=target[front,:3].astype(float)
blend=np.clip((1-depth)/.15,0,1)[:,None]
target[front,:3]=np.clip(surface*blend+base*(1-blend),0,255).round().astype('uint8')
target[front,3]=255
target[near]=a[near]

# ONE local domain joins shoulder root, elbow, bangle, palm and upper cotton.
# No old outward complete arm, head pose, or lower-body pose is an input.
domain=(oldmove|lip)&(yy<895)
protectedprops=(props[:,:,3]>0)&~cover
domain&=~near&~protectedprops
box=(440,350,960,900)
neutral=lambda im:Image.alpha_composite(Image.new('RGBA',im.size,(237,240,242,255)),im).convert('RGB')
im=Image.fromarray(target)
out=R/'01_LOCAL_TARGET_ARM_AND_CONTINUOUS_SOFT_LIP.png'
neutral(im).crop(box).resize((1040,1100),Image.Resampling.LANCZOS).save(out)
Image.fromarray(domain.astype('uint8')*255).crop(box).resize((1040,1100),Image.Resampling.NEAREST).save(R/'03_ONE_LOCAL_DOMAIN_PROTECT_NEAR_CONTACT.png')

# Audit only: same-scale pinch crops and true feather contact; never an input.
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
cmp=Image.new('RGB',(1340,1100),'#edf0f2');d=ImageDraw.Draw(cmp)
pinchbox=(620,545,890,845)
for ox,title,src,pt in [(20,'ACTUAL030 PINCH: 731,673',raw,A),(690,'LOCAL TARGET: 711,670',im,N)]:
 d.text((ox,15),title,font=font(23),fill='#23364d')
 p=neutral(src).crop(pinchbox).resize((540,600),Image.Resampling.LANCZOS)
 pd=ImageDraw.Draw(p)
 for pos,col in [(A,'#d64b38'),(N,'#167b5d')]:
  px,py=(pos-np.array(pinchbox[:2]))*2
  pd.line([(px,0),(px,600)],fill=col,width=2)
 px,py=(pt-np.array(pinchbox[:2]))*2
 pd.ellipse((px-8,py-8,px+8,py+8),outline='#167b5d' if ox>20 else '#d64b38',width=3)
 cmp.paste(p,(ox,60))
 d.text((ox,680),'SAME TRUE FEATHERS: '+('BEFORE' if ox==20 else 'THICK SOFT LIP'),font=font(20),fill='#23364d')
 source=Image.open(P/'audit/ACTUAL030_COMMON_TRUE_PROP_REFERENCE_NOT_NEW_DRAWING.png').convert('RGBA') if ox==20 else im
 cmp.paste(neutral(source).crop((785,760,900,835)).resize((575,375),Image.Resampling.NEAREST),(ox,715))
cmp.save(R/'02_SAME_SCALE_030_PINCH_AND_TRUE_TAIL_CONTACT_AUDIT_ONLY.png')

for name,mask in [('head',yy<350),('chest',(xx<455)&(yy<640)),('near_bare_hand_and_arm',near),('lowerbody',yy>=1085)]:
 assert np.array_equal(target[mask],a[mask]),name
assert not np.any(domain&near)
assert np.all(target[cover,3]==255)
assert int((cover&core).sum())<int(core.sum())*.20
common=np.array(Image.open(P/'audit/ACTUAL030_COMMON_TRUE_PROP_REFERENCE_NOT_NEW_DRAWING.png').convert('RGBA'))
fixed=(props[:,:,3]==255)&~cover&~near
assert np.array_equal(target[fixed],common[fixed])
facts={'new_imagegen_calls':0,'new_native_drawings':0,'status':'LOCAL_TARGET_ONLY_AWAITING_ASTRA_SHORT_GATE','actual030_sha256':sha(rawpath),'approved_inward_arm_reference_commit':'694f59b370b78332bf31e730898a260ec612762d','failed_outward036_not_an_input_or_geometry_source':True,'source030_pinch_xy':A.tolist(),'new_local_pinch_xy':N.tolist(),'delta_in_common030_native_pixels':(N-A).tolist(),'crop_in_common030_native_canvas':list(box),'input_display_scale':2,'single_edit_domain':'complete far shoulder sleeve/elbow/bangle/wrist/palm plus continuous upper cloth edge; near hand/neck contact, head/chest and lowerbody protected','body_checks':['head','chest','near bare hand/arm','lowerbody'],'body_checks_exact_to_actual030':True,'new_opaque_outer_feather_pixels_covered':int(cover.sum()),'conservative_core_covered':int((cover&core).sum()),'conservative_core_total':int(core.sum()),'remaining_opaque_true_parts_protected':True,'cloth_surface_technical_method':'Actual cotton interior pixels, curved finite width surface with lit thickness and broad dark inside; zero black guide strokes; not native painted art','identity_future_input_only':'head and blouse INTERNAL material crops; no full old arm or old pose','request_not_executed':True,'sources':{'inward_target':str(P/'layers/NEW_F036_FROM_ACTUAL030_TECHNICAL_PROBE_NOT_NATIVE.png'),'true_props':str(P/'layers/TRUE_ORIGINAL_PROPS_SAME_COMMON030_COORDS.png'),'arm':str(P/'layers/COMPLETE_ACTUAL030_ARM_CONTINUOUS_TECHNICAL_PROBE_NOT_ART.png')}}
(R/'SOURCE_SCOPE_AND_ZERO_CALL.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(facts,ensure_ascii=False))
