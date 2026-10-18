from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,math
b=Path(__file__).resolve().parents[3];o=b/'repairs/d12_local_call21';pp=b/'repairs/d12_pixel_preplace';base=Image.open(pp/'references/d12_preplace_full_1670x942.png').convert('RGBA');raw=Image.open(o/'originals/S03b_d12_call21_local_original.png').convert('RGBA');s=math.sqrt(raw.width*raw.height/(370*380));mapped=raw.transform((370,380),Image.Transform.AFFINE,(s,0,0,0,s,0),resample=Image.Resampling.BICUBIC);a=np.array(base);c=np.array(mapped);rm=np.array(Image.open(pp/'masks/REPAIR_only_old_footprint_and_connection.png'))>0;tm=np.array(Image.open(pp/'masks/target_hand_fruit_PROTECT.png'))>0;local_rm=rm[420:800,350:720];out=a.copy();region=out[420:800,350:720];region[local_rm]=c[local_rm];out[420:800,350:720]=region;p=o/'composites/S03b_d12_f28_call21_composited_candidate.png';Image.fromarray(out).save(p)
# Store the consumed connection layer and mask for reproducibility, never overwrite the raw source.
layer=np.zeros_like(a);layer[rm]=out[rm];Image.fromarray(layer).save(o/'composites/connection_layer_full.png');qa=Image.new('RGBA',base.size,(230,230,230,255));qa.alpha_composite(Image.fromarray(out));qa.crop((350,420,720,800)).resize((740,760)).save(o/'qa/composited_local_2x.png')
checks={'candidate':str(p),'size':list(base.size),'mode':'RGBA','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scale_inverse_mapping':s,'mapping':'PIL affine (s,0,0,0,s,0), bicubic; only connection repair mask consumed','crop_xyxy':[350,420,720,800],'outside_REPAIR_changed_pixels':int(np.any(out[~rm]!=a[~rm],axis=1).sum()),'PROTECT_changed_pixels':int(np.any(out[tm]!=a[tm],axis=1).sum()),'repair_pixels':int(rm.sum()),'source_vs_candidate_outside_roi_changed_pixels':int(np.any(out[:420]!=a[:420],axis=2).sum()+np.any(out[800:]!=a[800:],axis=2).sum()),'alpha_min':int(out[:,:,3].min()),'alpha_max':int(out[:,:,3].max()),'fully_transparent_pixels':int((out[:,:,3]==0).sum()),'composition':'Replace exact REPAIR pixels including alpha; do not alpha-over. All remaining original preplace RGBA preserved. Hand source foreground exact-original file retained independently.'}
(o/'logs/composite_invariants.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
ims=[Image.open(b/'outputs/chew/originals/d11_f25_call03.png').convert('RGBA'),Image.fromarray(out),Image.open(b/'outputs/chew/originals/d13_f32_call05.png').convert('RGBA')]
def bg(im):
 c=Image.new('RGBA',base.size,(230,230,230,255));c.alpha_composite(im);return c
for name,x,y in [('d11_d12_onion50',ims[0],ims[1]),('d12_d13_onion50',ims[1],ims[2])]:Image.blend(bg(x),bg(y),.5).convert('RGB').save(o/'qa'/f'{name}.jpg')
contact=Image.new('RGB',(1110,410),'white');d=ImageDraw.Draw(contact)
for j,(im,n) in enumerate(zip(ims,['d11','d12 call21 candidate','d13'])):contact.paste(bg(im).crop((350,420,720,800)),(370*j,30));d.text((370*j+8,10),n,fill='black')
contact.save(o/'qa/boundary_contact.jpg')
