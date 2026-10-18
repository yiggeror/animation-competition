from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;F=R/'F030_FINAL_LOCKED';src=F/'S08_F030_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='ef53ba49d805d2a9eb2cf934f62b2098a07e924250fcbbd5070cb33fcbba6bc8';a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
# Fresh030 true visible arm envelope, not previous027 trace. Both actual elbows now above981.
near=[(680,770),(770,750),(895,800),(1010,730),(1170,695),(1170,840),(1070,860),(950,920),(880,955),(810,940),(730,875)]
far=[(1017,797),(1044,782),(1077,778),(1116,789),(1154,790),(1189,736),(1263,724),(1267,780),(1228,820),(1178,858),(1112,899),(1080,922),(1046,915),(1012,887),(988,852)]
def pm(p):
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
env=pm(near)|pm(far);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue
for p in ['F030_true_near_hand_match_footprint.png','F030_whole_closed_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png']:arm|=(np.array(Image.open(F/p))>0)&alpha
box=(np.array(Image.open(F/'F030_fixed_table_box_footprint.png'))>0)&alpha;arm&=~box
parts={'body':~(arm|box),'arms':arm,'table_box':box};layers={};names={'body':'F030_body_behind_original_pixels.png','arms':'F030_forearms_elbows_original_pixels.png','table_box':'F030_table_box_original_pixels.png'}
for k,m in parts.items():
 v=a.copy();v[~m,3]=0;layers[k]=v;Image.fromarray(v).save(O/'frames'/names[k]);Image.fromarray((m&alpha).astype('uint8')*255).save(O/'masks'/f'F030_{k}_binary.png');assert np.array_equal(v[:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(int) for v in layers.values()),a[:,:,3]);assert (sum(v[:,:,3]>0 for v in layers.values())).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(1920,1080),c),Image.fromarray(a));ov=np.array(base);ov[arm,:3]=np.rint(ov[arm,:3]*.5+np.array([220,70,150])*.5).astype('uint8');ov[box,:3]=np.rint(ov[box,:3]*.5+np.array([30,190,215])*.5).astype('uint8');im=Image.fromarray(ov);ImageDraw.Draw(im).line((620,981,1300,981),fill=(230,90,20,255),width=1);im.crop((620,680,1300,1020)).resize((1360,680)).save(O/'qa'/f'F030_threeway_overlay_{tag}.png')
 table=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(table);d.rectangle((764,950,1920,981),fill='#b48b60');d.rectangle((764,981,1920,1029),fill='#6a4226');d.rectangle((785,1029,1920,1080),fill='#5a361e');out=Image.new('RGBA',(1920,1080),c);out.alpha_composite(Image.fromarray(layers['body']));out.alpha_composite(table);out.alpha_composite(Image.fromarray(layers['table_box']));out.alpha_composite(Image.fromarray(layers['arms']));out.crop((620,680,1300,1020)).resize((1360,680)).save(O/'qa'/f'F030_layer_TOPOLOGY_ONLY_NOT_CANVAS_{tag}.png')
yy,xx=np.where(arm&(np.indices(arm.shape)[0]>=981));report={'status':'PASS_EXCLUSIVE_ORIGINAL_RGBA_THREEWAY_PARTITION_ACTUAL_CANVAS_PENDING','source_sha256':sha,'source_canvas':[1920,1080],'image_generation_calls':0,'source_rgba_changed':0,'overlap_alpha_pixels':0,'rgba_reconstruction_exact':True,'all_layer_RGB_original':True,'fresh_F030_actual_arm_envelopes':[near,far],'foreground_arm_pixels':int(arm.sum()),'table_box_pixels':int(box.sum()),'box_draw_count':1,'box_alpha_in_other_layers':0,'arm_pixels_at_y981_and_below':len(xx),'table_front_y':981,'xy':[0,0],'scale':1,'note':'Both actual030 elbows above981. Three exclusive alpha layers with original RGB retained everywhere; exactRGBA reconstruction. Transparent low lever seat stays empty; rod is independent scene layer. PIL topology only, actual Canvas pending.'};(O/'LAYER_VALIDATION.json').write_text(json.dumps(report,indent=2));arts={}
for role,n in names.items():
 p=O/'frames'/n;arts[role]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':1920,'height':1080}
(O/'layer_contract.js').write_text('export const LAYER_ARTS = '+json.dumps({'030':arts},indent=2)+';\n');print(json.dumps(report,indent=2))
