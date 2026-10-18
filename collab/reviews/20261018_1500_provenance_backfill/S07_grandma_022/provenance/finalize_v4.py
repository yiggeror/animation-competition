from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
import numpy as np,json,hashlib
D=Path('astra_s07_f022_prepare_20261018_1357');W,H=1024,1536;yy,xx=np.indices((H,W));im=Image.open(D/'candidates/F022_local_v3.png').convert('RGBA');a=np.array(im);prev=np.array(Image.open(D/'sources/F018_LOCKED_rgba.png').convert('RGBA'));union=np.zeros((H,W),bool)
for n in ['body_head','sleeve','near_upper_skin','near_forearm_hand','far_wrist_hand']:union|=np.array(Image.open(D/f'masks/{n}_source.png'))>0
for n in ['torso_head','near_sleeve','near_upper_skin','near_forearm_hand','far_wrist_hand','fixed_ground_basin']:union|=np.array(Image.open(D/f'preposition/{n}.png'))[:,:,3]>0
union=ndimage.binary_dilation(union,iterations=3)|(np.array(Image.open(D/'masks/F022_local_take_v3.png'))>0)
# Fixed lower body exact restoration outside source/moved/repair union. This avoids compositing alpha strengthening unchanged feet/pants.
restore=(~union)&np.any(a!=prev,axis=2);out=a.copy();out[~union]=prev[~union]
Image.fromarray((union*255).astype('uint8')).save(D/'masks/F022_final_source_target_union_v4.png');Image.fromarray((restore*255).astype('uint8')).save(D/'masks/F022_unmoved_original_restore_v4.png');diff=np.any(out!=prev,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F022_actual_diff_v4.png');im=Image.fromarray(out);im.save(D/'candidates/F022_local_v4.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB').save(D/f'review/F022_local_v4_{n}.jpg',quality=98)
wh=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),im);wh.crop((200,775,920,1340)).resize((1080,847)).convert('RGB').save(D/'review/F022_local_v4_connections.jpg',quality=98)
gr=Image.alpha_composite(Image.new('RGBA',(W,H),(85,85,85,255)),im);gr.crop((200,960,580,1330)).resize((760,740)).convert('RGB').save(D/'review/F022_local_v4_hands_gray.jpg',quality=98)
check={'previous_F018_sha256':hashlib.sha256((D/'sources/F018_LOCKED_rgba.png').read_bytes()).hexdigest(),'actual_changed_pixels_from_F018':int(diff.sum()),'outside_source_target_union_changed':int(diff[~union].sum()),'v3_to_v4_restored_pixels':int(restore.sum()),'v3_to_v4_RGB_changed':int(np.any(out[:,:,:3]!=a[:,:,:3],axis=2).sum()),'v3_to_v4_alpha_changed':int((out[:,:,3]!=a[:,:,3]).sum()),'unoccluded_near_shoe_RGBA_change':int(diff[(xx>420)&(xx<590)&(yy>1388)].sum()),'sha256':hashlib.sha256((D/'candidates/F022_local_v4.png').read_bytes()).hexdigest(),'status':'INDEPENDENT_REVIEW_PENDING'};(D/'geometry/F022_final_checks_v4.json').write_text(json.dumps(check,indent=2));print(check)
