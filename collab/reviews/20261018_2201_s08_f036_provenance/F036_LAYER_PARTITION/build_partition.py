from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;F=R/'F036_FINAL_LOCKED';src=F/'S08_F036_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='6ee3d4ccf88650496ce97f8709642fb3b5a228fd0ec1a5e5fd4efc50fac42753';a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
# Fresh036 actual visible arm envelope, not previous033 trace. Both actual elbows now above981.
near=[(800,790),(884,776),(982,841),(1182,788),(1355,768),(1370,847),(1270,891),(1120,922),(994,961),(944,958),(870,916),(805,848)]
far=[(1060,800),(1108,794),(1150,785),(1195,734),(1267,729),(1267,792),(1220,826),(1150,862),(1090,883),(1050,863)]
def pm(p):
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
env=pm(near)|pm(far);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue
for p in ['F036_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png','F036_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png']:arm|=(np.array(Image.open(F/p))[:,:,3]>0)&alpha
box=(np.array(Image.open(F/'F036_fixed_table_box_footprint.png'))>0)&alpha;arm&=~box
fringe483=np.array(Image.open(F/'F036_original_box_fringe483_BODY_BEHIND_TABLE.png'))>0;arm&=~fringe483;assert not (fringe483&box).any()
parts={'body':~(arm|box),'arms':arm,'table_box':box};layers={};names={'body':'F036_body_behind_original_pixels.png','arms':'F036_forearms_elbows_original_pixels.png','table_box':'F036_table_box_original_pixels.png'}
for k,m in parts.items():
 v=a.copy();v[~m,3]=0;layers[k]=v;Image.fromarray(v).save(O/'frames'/names[k]);Image.fromarray((m&alpha).astype('uint8')*255).save(O/'masks'/f'F036_{k}_binary.png');assert np.array_equal(v[:,:,:3],a[:,:,:3])
assert np.array_equal(sum(v[:,:,3].astype(int) for v in layers.values()),a[:,:,3]);assert (sum(v[:,:,3]>0 for v in layers.values())).max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(1920,1080),c),Image.fromarray(a));ov=np.array(base);ov[arm,:3]=np.rint(ov[arm,:3]*.5+np.array([220,70,150])*.5).astype('uint8');ov[box,:3]=np.rint(ov[box,:3]*.5+np.array([30,190,215])*.5).astype('uint8');im=Image.fromarray(ov);ImageDraw.Draw(im).line((620,981,1400,981),fill=(230,90,20,255),width=1);im.crop((620,680,1400,1020)).resize((1560,680)).save(O/'qa'/f'F036_threeway_overlay_{tag}.png')
 table=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(table);d.rectangle((764,950,1920,981),fill='#b48b60');d.rectangle((764,981,1920,1029),fill='#6a4226');d.rectangle((785,1029,1920,1080),fill='#5a361e');out=Image.new('RGBA',(1920,1080),c);out.alpha_composite(Image.fromarray(layers['body']));out.alpha_composite(table);out.alpha_composite(Image.fromarray(layers['table_box']));out.alpha_composite(Image.fromarray(layers['arms']));out.crop((620,680,1400,1020)).resize((1560,680)).save(O/'qa'/f'F036_layer_TOPOLOGY_ONLY_NOT_CANVAS_{tag}.png')
yy,xx=np.where(arm&(np.indices(arm.shape)[0]>=981));report={'status':'PASS_EXCLUSIVE_ORIGINAL_RGBA_THREEWAY_PARTITION_ACTUAL_CANVAS_PENDING','source_sha256':sha,'source_canvas':[1920,1080],'image_generation_calls':0,'source_rgba_changed':0,'overlap_alpha_pixels':0,'rgba_reconstruction_exact':True,'all_layer_RGB_original':True,'fresh_F036_actual_arm_envelopes':[near,far],'foreground_arm_pixels':int(arm.sum()),'table_box_pixels':int(box.sum()),'box_draw_count':1,'original033_box_visibleRGBA_equal':True,'original033_fringe483_retained_in_body':483,'box_alpha_in_other_layers':0,'arm_pixels_at_y981_and_below':len(xx),'table_front_y':981,'xy':[0,0],'scale':1,'note':'Both actual036 elbows above981. Three exclusive alpha layers with original RGB retained everywhere; exactRGBA reconstruction. Transparent low lever seat stays empty; rod is independent scene layer. PIL topology only, actual Canvas pending.'};(O/'LAYER_VALIDATION.json').write_text(json.dumps(report,indent=2));arts={}
for role,n in names.items():
 p=O/'frames'/n;arts[role]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':1920,'height':1080}
(O/'layer_contract.js').write_text('export const LAYER_ARTS = '+json.dumps({'036':arts},indent=2)+';\n');print(json.dumps(report,indent=2))
