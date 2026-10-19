from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;PACK=P.parent
MASTER=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=Image.open(MASTER).convert('RGBA');child=Image.open(P/'art/child_complete_new_pose.png').convert('RGBA')
assert source.size==child.size==(1672,941)
a=np.array(source);b=np.array(child);edit=np.array(Image.open(P/'inputs/04_edit_white.png'))==255
target=a.copy();target[edit]=b[edit]
# Same original lower calf/ankle contact strips and shoes. No old upper body,
# sleeve, arm or hand is reused in the child pose.
calf=np.zeros(edit.shape,bool);calf[805:,525:662]=True
target[calf]=a[calf]
assert not np.any(target[~edit]!=a[~edit])
assert not np.any(target[:,885:]!=a[:,885:])
first=P/'inputs/01_F008_unique_opaque_pose_target.png';Image.fromarray(target).save(first)
box=(535,270,1005,510)
Image.fromarray(target).crop(box).resize((1410,720),Image.Resampling.NEAREST).save(P/'inputs/02_same_view_approach_3x.png')
(P/'detail_transform.json').write_text(json.dumps({'source':'inputs/01_F008_unique_opaque_pose_target.png','source_sha256':sha(first),
 'crop_xyxy':list(box),'scale':3,'resampling':'NEAREST exact pixel replication','additional_pose_or_annotation':False},indent=2)+'\n')
def matte(im):
 bg=Image.new('RGBA',im.size,'#c6c9cb');bg.alpha_composite(im);return bg.convert('RGB')
matte(Image.fromarray(target)).save(P/'qa/full_target_gray.png')
matte(Image.open(P/'inputs/02_same_view_approach_3x.png').convert('RGBA')).save(P/'qa/approach_gray.png')
# QA only: anatomical axes are absent from all model images.
g=json.loads((P/'target_construction.json').read_text());q=matte(Image.fromarray(target));d=ImageDraw.Draw(q)
for side,col in [('R','#147b88'),('L','#815098')]:
 chain=g['frozen_008'][side+'_chain'];d.line([tuple(x) for x in chain],fill=col,width=2)
 for point in chain:
  x,y=point;d.ellipse((x-3,y-3,x+3,y+3),fill='white',outline=col,width=1)
q.save(P/'qa/frozen_bones_overlay_QA_only.png')
print('Assembled unique opaque full target + exact 3x approach. Grandma/rods/ankles source-protected. No model calls.')
