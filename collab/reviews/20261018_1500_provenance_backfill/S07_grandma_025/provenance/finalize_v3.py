from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
import numpy as np,json,hashlib
D=Path('astra_s07_f025_prepare_20261018_1420');W,H=1024,1536;yy,xx=np.indices((H,W));v2=np.array(Image.open(D/'candidates/F025_local_v2.png').convert('RGBA'));raw=np.array(Image.open(D/'candidates/F025_call01_registered_source.png').convert('RGBA'));prev=np.array(Image.open(D/'sources/F022_LOCKED_rgba.png').convert('RGBA'))
# Same raw source, with identical disclosed blue-material correction as v2.
pig=np.array(Image.open(D/'masks/F025_blue_material_match_v2.png')).astype(float)/255;raw[:,:,:3]=np.rint(np.clip(raw[:,:,:3].astype(float)+pig[:,:,None]*[13,9,2],0,255)).astype('uint8')
m=Image.new('L',(W,H));dr=ImageDraw.Draw(m)
dr.polygon([(326,791),(354,793),(358,813),(326,806)],fill=255)
# Narrow perimeter corrections for preposition segmentation notches. Cloth interiors stay inherited.
dr.polygon([(568,773),(590,785),(595,798),(582,793),(568,781)],fill=255)
dr.polygon([(818,999),(835,1017),(836,1031),(824,1020),(813,1004)],fill=255)
dr.polygon([(766,1178),(784,1182),(807,1182),(826,1178),(835,1174),(838,1179),(829,1187),(803,1191),(780,1189),(766,1185)],fill=255)
ma=np.array(m);out=v2.copy();out[ma>0]=raw[ma>0];m.save(D/'masks/F025_same_raw_edge_cleanup_v3.png')
# Explicit source+target movement and repair domain, before exact unmoved RGBA restoration.
u=np.zeros((H,W),bool)
for n in ['head_garment','near_upper_skin','near_forearm_hand','far_wrist_hand']:
 u|=np.array(Image.open(D/f'masks/{n}_source.png'))>0
u=ndimage.binary_dilation(u,iterations=5)
for n in ['body_head','near_sleeve','near_upper_skin','near_forearm_hand','far_wrist_hand']:
 u|=ndimage.binary_dilation(np.array(Image.open(D/f'preposition/{n}.png'))[:,:,3]>0,iterations=3)
u|=np.array(Image.open(D/'masks/F025_local_take_v2.png'))>0;u|=ma>0
# Known source-reveal pants restoration and alpha fragments removed by the input preposition.
u|=(xx>=320)&(xx<550)&(yy>=1080)&(yy<1340)
u|=(xx<420)&(yy>900)&(yy<1040);u|=(xx<326)&(yy>1090)&(yy<1340)
p=Image.new('L',(W,H));ImageDraw.Draw(p).polygon([(334,1085),(351,1043),(403,1026),(465,1031),(568,1050),(652,1115),(566,1165),(490,1120),(426,1087)],fill=255);u|=np.array(p)>0
restore=(~u)&np.any(out!=prev,axis=2);out[~u]=prev[~u]
Image.fromarray((u*255).astype('uint8')).save(D/'masks/F025_final_union_v3.png');Image.fromarray((restore*255).astype('uint8')).save(D/'masks/F025_unmoved_restore_v3.png');diff=np.any(out!=prev,axis=2);Image.fromarray((diff*255).astype('uint8')).save(D/'masks/F025_actual_diff_v3.png')
im=Image.fromarray(out);im.save(D/'candidates/F025_local_v3.png')
for n,c in [('white','white'),('gray',(85,85,85,255))]:
 bg=Image.alpha_composite(Image.new('RGBA',(W,H),c),im).convert('RGB');bg.save(D/f'review/F025_local_v3_{n}.jpg',quality=98)
 if n=='gray':bg.crop((280,725,895,1210)).resize((1045,824)).save(D/'review/F025_local_v3_connections_gray.jpg',quality=98)
# Observable colored jade centroid; not a joint center.
r,g,b=out[:,:,0].astype(float),out[:,:,1].astype(float),out[:,:,2].astype(float);jade=(g>r*1.12)&(g>b*1.1)&(r<150)&(xx>380)&(xx<510)&(yy>960)&(yy<1100)&(out[:,:,3]>200);ys,xs=np.where(jade);cent=[float(xs.mean()),float(ys.mean())]
meta={'status':'AUTHOR_V3_PENDING_REVIEW','sha256':hashlib.sha256((D/'candidates/F025_local_v3.png').read_bytes()).hexdigest(),'same_raw_cleanup_pixels':int(np.any(v2!=out,axis=2)[ma>0].sum()),'cleanup_mask_outside_delta_before_restore':0,'unmoved_RGBA_restored_pixels':int(restore.sum()),'final_changed_pixels_from_F022':int(diff.sum()),'final_union_outside_changed':int(diff[~u].sum()),'basin_and_feet_y_1351_plus_changed':int(diff[yy>1350].sum()),'near_jade_visible_centroid_asset':cent,'near_jade_visible_centroid_world':(np.array([730,375])+np.array(cent)*.2734375).tolist(),'jade_is_not_wrist_joint':True,'near_palm_contact_surface_observed_asset':[365,1056],'near_palm_contact_surface_world':[829.8046875,663.75],'imagegen_calls_this_state':1,'total_grandma_and_basin_calls':9};(D/'geometry/F025_local_v3_checks.json').write_text(json.dumps(meta,indent=2));print(meta)
