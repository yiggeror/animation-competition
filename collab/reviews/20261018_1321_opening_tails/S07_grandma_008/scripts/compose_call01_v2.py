from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import numpy as np,json,hashlib
D=Path('astra_s07_f008_prepare_20261018_1249');W,H=1024,1536
base=np.array(Image.open(D/'preposition/F008_preposition_NOT_FINAL.png').convert('RGBA'));reg=np.array(Image.open(D/'candidates/F008_call01_registered_source.png').convert('RGBA'));new=reg.copy();yy,xx=np.indices((H,W))
# Explicit regional shirt correction: match original blue pigment, preserve whites/ink/skin.
region=Image.new('L',(W,H));dr=ImageDraw.Draw(region);dr.polygon([(495,700),(720,690),(903,1100),(889,1130),(760,1125),(590,1055),(592,1020),(651,969),(665,935),(650,903),(614,928),(550,975),(505,930)],fill=255)
rgb=reg[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];blue=np.clip((b-r-15)/40,0,1)*np.clip((r-38)/35,0,1)*np.clip((225-r)/40,0,1)*(np.array(region)/255)*(reg[:,:,3]>100)
# Quantified stable sleeve/waist medians differ by (18..23,6..11,-3..0).
delta=np.array([20,8,-1]);new[:,:,:3]=np.clip(rgb+blue[:,:,None]*delta,0,255).astype('uint8');Image.fromarray(new).save(D/'candidates/F008_call01_registered_palette_matched.png')
mask=Image.open(D/'masks/local_connection_edit_mask_PROPOSAL.png').convert('L');dr=ImageDraw.Draw(mask)
# Same-call continuous near arm patch to original jade rear edge; remove old upper cut and side white sliver.
dr.polygon([(636,879),(751,876),(765,939),(754,968),(704,1008),(613,1055),(602,1041),(608,1018),(648,983),(661,956),(657,929),(639,911)],fill=255)
# Far arm's old upper double contour; original actual hand/forefinger remains.
dr.polygon([(491,945),(554,927),(564,958),(546,973),(494,970)],fill=255)
# Right waist seam and tiny old-edge scraps at repair boundary.
dr.polygon([(771,1020),(849,1023),(892,1096),(883,1126),(839,1152),(790,1154),(777,1115)],fill=255)
# Feather inward only; no alpha outside explicit selected domain.
m=np.array(mask);soft=np.minimum(m,np.array(mask.filter(ImageFilter.GaussianBlur(2))));soft[(m==255)&(np.array(mask.filter(ImageFilter.MinFilter(11)))==255)]=255
# Hard protect basin+both hands+bracelet exact raster, excluding nearby old background.
protect=Image.new('L',(W,H));pd=ImageDraw.Draw(protect);pd.polygon([(300,970),(428,946),(483,946),(490,971),(603,987),(615,1010),(612,1059),(581,1080),(320,1090)],fill=255)
pr=np.array(protect)>0;soft[pr]=0
# Final mask includes RGB-correction domain only where selected; registration source outside unused.
Image.fromarray(soft).save(D/'masks/F008_local_repair_v2_mask.png');w=soft[:,:,None].astype(float)/255;out=np.rint(base*(1-w)+new*w).astype('uint8')
# Preserve original seated bottom below y1151 and all legs. The new rounded hip surface may fill above that support only.
out[1151:]=base[1151:];soft[1151:]=0;Image.fromarray(soft).save(D/'masks/F008_local_repair_v2_mask.png')
c=Image.fromarray(out);c.save(D/'candidates/F008_local_v2.png')
for n,bg in [('white','white'),('gray',(150,150,150,255))]:
 im=Image.alpha_composite(Image.new('RGBA',(W,H),bg),c).convert('RGB');im.save(D/f'review/F008_local_v2_{n}.jpg',quality=97)
 if n=='white': im.crop((360,810,920,1180)).resize((1120,740)).save(D/'review/F008_local_v2_join_detail.jpg',quality=97)
actual=np.any(base!=out,axis=2);Image.fromarray((actual*255).astype('uint8')).save(D/'masks/F008_local_v2_actual_diff.png');json.dump({'outside_mask_changed_pixels':int(actual[soft==0].sum()),'hand_basin_protect_changed_pixels':int(actual[pr].sum()),'source_call':1,'sha256':hashlib.sha256((D/'candidates/F008_local_v2.png').read_bytes()).hexdigest(),'palette_shirt_delta_reference':[20,8,-1],'palette_correction_applied_only_within_explicit_shirt_and_selected_repair_mask':True,'state':'AUTHOR_REVIEW_PENDING'},open(D/'geometry/F008_local_v2_checks.json','w'),indent=2)
