from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;F=R/'F033_FINAL_LOCKED';src=F/'S08_F033_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='0f8637f7f1cf5cc01e99029da5da13c9c42bac06329e2b64d77980d997029b47';a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
# Fresh030 true visible arm envelope, not previous027 trace. Both actual elbows now above981.
near=[(726,774),(803,764),(913,813),(1067,744),(1256,685),(1269,781),(1202,819),(1082,850),(987,915),(922,948),(858,940),(784,879)]
far=[(1030,812),(1087,796),(1134,791),(1163,773),(1206,733),(1268,726),(1271,782),(1234,822),(1177,863),(1121,918),(1080,931),(1040,914),(1006,871)]
def pm(p):
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
env=pm(near)|pm(far);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue
for p in ['F033_true_near_hand_match_INDEPENDENT_FOREGROUND_footprint.png','F033_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_footprint.png']:arm|=(np.array(Image.open(F/p))>0)&alpha
box=(np.array(Image.open(F/'F033_fixed_table_box_footprint.png'))>0)&alpha;arm&=~box
parts={'body':~(arm|box),'arms':arm,'table_box':box};layers={};names={'body':'F033_body_behind_original_pixels.png','arms':'F033_forearms_elbows_original_pixels.png','table_box':'F033_table_box_original_pixels.png'}
for k,m in parts.items():
 v=a.copy();v[~m,3]=0;layers[k]=v;Image.fromarray(v).save(O/'frames'/names[k]);Image.fromarray((m&alpha).astype('uint8')*255).save(O/'masks'/f'F033_{k}_binary.png');assert np.array_equal(v[:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(int) for v in layers.values()),a[:,:,3]);assert (sum(v[:,:,3]>0 for v in layers.values())).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(1920,1080),c),Image.fromarray(a));ov=np.array(base);ov[arm,:3]=np.rint(ov[arm,:3]*.5+np.array([220,70,150])*.5).astype('uint8');ov[box,:3]=np.rint(ov[box,:3]*.5+np.array([30,190,215])*.5).astype('uint8');im=Image.fromarray(ov);ImageDraw.Draw(im).line((620,981,1300,981),fill=(230,90,20,255),width=1);im.crop((620,680,1300,1020)).resize((1360,680)).save(O/'qa'/f'F033_threeway_overlay_{tag}.png')
 table=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(table);d.rectangle((764,950,1920,981),fill='#b48b60');d.rectangle((764,981,1920,1029),fill='#6a4226');d.rectangle((785,1029,1920,1080),fill='#5a361e');out=Image.new('RGBA',(1920,1080),c);out.alpha_composite(Image.fromarray(layers['body']));out.alpha_composite(table);out.alpha_composite(Image.fromarray(layers['table_box']));out.alpha_composite(Image.fromarray(layers['arms']));out.crop((620,680,1300,1020)).resize((1360,680)).save(O/'qa'/f'F033_layer_TOPOLOGY_ONLY_NOT_CANVAS_{tag}.png')
yy,xx=np.where(arm&(np.indices(arm.shape)[0]>=981));report={'status':'PASS_EXCLUSIVE_ORIGINAL_RGBA_THREEWAY_PARTITION_ACTUAL_CANVAS_PENDING','source_sha256':sha,'source_canvas':[1920,1080],'image_generation_calls':0,'source_rgba_changed':0,'overlap_alpha_pixels':0,'rgba_reconstruction_exact':True,'all_layer_RGB_original':True,'fresh_F033_actual_arm_envelopes':[near,far],'foreground_arm_pixels':int(arm.sum()),'table_box_pixels':int(box.sum()),'box_draw_count':1,'box_alpha_in_other_layers':0,'arm_pixels_at_y981_and_below':len(xx),'table_front_y':981,'xy':[0,0],'scale':1,'note':'Both actual033 elbows above981. Three exclusive alpha layers with original RGB retained everywhere; exactRGBA reconstruction. Transparent low lever seat stays empty; rod is independent scene layer. PIL topology only, actual Canvas pending.'};(O/'LAYER_VALIDATION.json').write_text(json.dumps(report,indent=2));arts={}
for role,n in names.items():
 p=O/'frames'/n;arts[role]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':1920,'height':1080}
(O/'layer_contract.js').write_text('export const LAYER_ARTS = '+json.dumps({'033':arts},indent=2)+';\n');print(json.dumps(report,indent=2))
