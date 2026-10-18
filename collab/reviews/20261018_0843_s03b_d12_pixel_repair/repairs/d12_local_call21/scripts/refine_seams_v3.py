from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,math
b=Path(__file__).resolve().parents[3];o=b/'repairs/d12_local_call21';pp=b/'repairs/d12_pixel_preplace';v=o/'seams_v3';v.mkdir(exist_ok=True);a=np.array(Image.open(pp/'references/d12_preplace_full_1670x942.png').convert('RGBA'));oldrm=np.array(Image.open(pp/'masks/REPAIR_only_old_footprint_and_connection.png'))>0;oldtm=np.array(Image.open(pp/'masks/target_hand_fruit_PROTECT.png'))>0;fg=np.array(Image.open(pp/'references/target_hand_fruit_exact_pixels_full.png').convert('RGBA'));H,W=a.shape[:2]
# Only the artificial terminal wrist cut, not palm/finger/fruit, is released.
request=np.zeros((H,W),bool)
request[640:659,449:469]=True
request[656:671,489:501]=True
request[644:675,554:567]=True
request[665:670,486:563]=True
release=oldtm&request
rm=oldrm|release;core=oldtm&~release
raw=Image.open(o/'originals/S03b_d12_call21_local_original.png').convert('RGBA');s=math.sqrt(raw.width*raw.height/(370*380));mapped=raw.transform((370,380),Image.Transform.AFFINE,(s,0,0,0,s,0),resample=Image.Resampling.BICUBIC);gen=np.zeros_like(a);gen[420:800,350:720]=np.array(mapped);out=a.copy();out[rm]=gen[rm]
# A narrow RGB-only fabric corridor straddles the reviewed diagonal tonal seam.
def blue(z):
 z=z.astype(float);return (z[:,:,2]>110)&(z[:,:,0]<.88*z[:,:,2])&(z[:,:,1]<.98*z[:,:,2])&(z[:,:,0]>45)&(z[:,:,3]>245)
ygrid,xgrid=np.indices((H,W));vx,vy=46.,28.;L=(vx*vx+vy*vy)**.5
along=((xgrid-548)*vx+(ygrid-623)*vy)/L
signed=((xgrid-548)*(-vy)+(ygrid-623)*vx)/L
fmask=(along>=-4)&(along<=L+4)&(np.abs(signed)<=5)&blue(a)&blue(gen)&(~core)
weight=np.clip((signed+5)/10,0,1)[:,:,None]
rgb=np.rint(a[:,:,:3]*(1-weight)+gen[:,:,:3]*weight).clip(0,255).astype('uint8');out[fmask,:3]=rgb[fmask]
# Alpha remains exactly as already composited: never feather transparency/black lines.
rm |= fmask
Image.fromarray(out).save(v/'S03b_d12_f28_call21_seams_v3_candidate.png')
for name,m in [('REPAIR_v3',rm),('PROTECT_core_v3',core),('released_wrist_edge_pixels',release),('sleeve_RGB_feather_only',fmask)]:Image.fromarray((m*255).astype('uint8')).save(v/f'{name}.png')
y,x=np.where(release);coords=np.stack([x,y],axis=1).tolist();(v/'released_coordinates_xy.json').write_text(json.dumps(coords))
report={'parent_candidate':'composites/S03b_d12_f28_call21_composited_candidate.png','new_candidate':'seams_v3/S03b_d12_f28_call21_seams_v3_candidate.png','same_generated_source':str(o/'originals/S03b_d12_call21_local_original.png'),'additional_image_calls':0,'released_old_protection_pixels':int(release.sum()),'released_regions_xyxy':[[449,640,469,659],[489,656,501,671],[554,644,567,675],[486,665,563,670]],'left_corner_rule':'Reviewer-approved narrow palm-root boundary rectangle released; main palm/finger/fruit core stays protected.','new_protect_pixels':int(core.sum()),'old_protect_changed_pixels':int(np.any(out[oldtm]!=a[oldtm],axis=1).sum()),'core_protect_changed_pixels':int(np.any(out[core]!=a[core],axis=1).sum()),'outside_REPAIR_v3_changed_pixels':int(np.any(out[~rm]!=a[~rm],axis=1).sum()),'rgb_feather_pixels':int(fmask.sum()),'feather_rule':'Opaque blue fabric within +/-5px of diagonal (548,623) to (594,651), RGB blend from source to same call21 layer; expanded REPAIR records this corridor. Alpha, black outlines, white flowers, and skin not blended.','feather_alpha_changed_pixels':int((out[:,:,3][fmask]!=np.where(oldrm|release,gen[:,:,3],a[:,:,3])[fmask]).sum()),'sha256':hashlib.sha256((v/'S03b_d12_f28_call21_seams_v3_candidate.png').read_bytes()).hexdigest()};(v/'seam_repair_log.json').write_text(json.dumps(report,indent=2))
bg=Image.new('RGBA',(W,H),(230,230,230,255));bg.alpha_composite(Image.fromarray(out));bg.crop((430,620,620,730)).resize((760,440)).save(v/'wrist_sleeve_seams_4x.png');bg.crop((350,420,720,800)).resize((740,760)).save(v/'local_2x.png');print(json.dumps(report,indent=2))
