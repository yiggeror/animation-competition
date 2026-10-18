from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;src=R/'F020_FINAL_LOCKED/S08_F020_grandma_match_box_RGBA.png';sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='ff4fad4d91762f7a5e8687741d0d09747e466474b91c4f4d0d8f9df032d516e6';a=np.array(Image.open(src).convert('RGBA'));alpha=a[:,:,3]>0
near=[(645,825),(677,805),(706,786),(735,779),(746,809),(764,851),(787,892),(831,884),(883,867),(930,850),(975,825),(1006,806),(1042,799),(1062,810),(1065,836),(1052,868),(1027,890),(994,899),(956,894),(928,912),(885,936),(843,962),(801,986),(774,999),(749,993),(727,973),(706,943),(686,906),(667,865)]
# New020 actual elbow unfolds forward; far forearm lifts to the relaxed empty hand. Not017 arm trace.
far=[(948,830),(974,798),(1025,778),(1056,782),(1075,840),(1155,803),(1217,740),(1285,740),(1295,812),(1221,880),(1105,930),(1007,940),(970,899)]
hand=[(1145,804),(1183,781),(1217,741),(1284,740),(1290,811),(1221,852),(1190,870),(1154,861)]
match=[(1025,832),(1058,776),(1073,777),(1075,795),(1042,840)]
def pm(polys):
 m=Image.new('L',(1920,1080));d=ImageDraw.Draw(m)
 for p in polys:d.polygon(p,fill=255)
 return np.array(m)>0
env=pm([near,far]);r,g,b=[a[:,:,k].astype(int) for k in range(3)];skin=(r-b>24)&(r-g>10)&(r>115)&alpha&env;arm=binary_dilation(binary_fill_holes(skin),iterations=2)&env&alpha;blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100);arm&=~blue;arm|=pm([hand,match])&alpha
box=(np.array(Image.open(R/'F020_input_gate/masks/F020_box_fixed_on_table_guard.png'))>0)&alpha;arm&=~box
parts={'body':~(arm|box),'arms':arm,'table_box':box};layers={};names={'body':'F020_body_behind_original_pixels.png','arms':'F020_forearms_elbows_original_pixels.png','table_box':'F020_table_box_original_pixels.png'}
for k,m in parts.items():
 v=a.copy();v[~m,3]=0;layers[k]=v;Image.fromarray(v).save(O/'frames'/names[k]);Image.fromarray((m&alpha).astype('uint8')*255).save(O/'masks'/f'F020_{k}_binary.png');assert np.array_equal(v[:,:,:3],a[:,:,:3])
alpha_sum=sum(v[:,:,3].astype(int) for v in layers.values());assert np.array_equal(alpha_sum,a[:,:,3]);overlap=sum(v[:,:,3]>0 for v in layers.values());assert overlap.max()==1
reb=Image.fromarray(layers['body']);reb=Image.alpha_composite(reb,Image.fromarray(layers['table_box']));reb=Image.alpha_composite(reb,Image.fromarray(layers['arms']));assert np.array_equal(np.array(reb),a)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 base=Image.alpha_composite(Image.new('RGBA',(1920,1080),c),Image.fromarray(a));ov=np.array(base);ov[arm,:3]=np.rint(ov[arm,:3]*.5+np.array([220,70,150])*.5).astype('uint8');ov[box,:3]=np.rint(ov[box,:3]*.5+np.array([30,190,215])*.5).astype('uint8');im=Image.fromarray(ov);ImageDraw.Draw(im).line((620,981,1240,981),fill=(230,90,20,255),width=1);im.crop((610,730,1240,1020)).resize((1260,580)).save(O/'qa'/f'F020_threeway_overlay_{tag}.png')
 table=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(table);d.rectangle((764,950,1920,981),fill='#b48b60');d.rectangle((764,981,1920,1029),fill='#6a4226');d.rectangle((785,1029,1920,1080),fill='#5a361e');out=Image.new('RGBA',(1920,1080),c);out.alpha_composite(Image.fromarray(layers['body']));out.alpha_composite(table);out.alpha_composite(Image.fromarray(layers['table_box']));out.alpha_composite(Image.fromarray(layers['arms']));out.crop((610,730,1240,1020)).resize((1260,580)).save(O/'qa'/f'F020_layer_TOPOLOGY_ONLY_NOT_CANVAS_{tag}.png')
yy,xx=np.where(arm&(np.indices(arm.shape)[0]>=981));report={'status':'PASS_EXCLUSIVE_ORIGINAL_RGBA_THREEWAY_PARTITION_ACTUAL_CANVAS_PENDING','source_sha256':sha,'source_canvas':[1920,1080],'image_generation_calls':0,'source_rgba_changed':0,'overlap_alpha_pixels':0,'rgba_reconstruction_exact':True,'all_layer_RGB_original':True,'new_F020_far_arm_trace':far,'near_arm_005_body_with020_hand_envelope':near,'foreground_arm_pixels':int(arm.sum()),'table_box_pixels':int(box.sum()),'box_draw_count':1,'box_alpha_in_other_layers':0,'arm_pixels_at_y981_and_below':len(xx),'below_front_bbox':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],'table_front_y':981,'xy':[0,0],'scale':1,'note':'Three mutually exclusive alpha layers, every RGB original. Exact preplaced box mask removed from both character layers, drawn once as table_box after table and before arms. New020 accepted upward-reaching actual arm trace; near hand/match shifted12left5down. PIL topology only, actual Canvas pending.'};(O/'LAYER_VALIDATION.json').write_text(json.dumps(report,indent=2));arts={}
for role,n in names.items():
 p=O/'frames'/n;arts[role]={'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':1920,'height':1080}
(O/'layer_contract.js').write_text('export const LAYER_ARTS = '+json.dumps({'020':arts},indent=2)+';\n');files=[p for p in O.rglob('*') if p.is_file() and p.name!='LOCAL_TO_COLLAB.tsv'];(O/'LOCAL_TO_COLLAB.tsv').write_text('local_path\tsuggested_collab_relative_path\tsha256\tbytes\n'+''.join(f'{p}\tcollab/s08_f020_layers_20261018/{p.relative_to(O)}\t{hashlib.sha256(p.read_bytes()).hexdigest()}\t{p.stat().st_size}\n' for p in files));print(json.dumps(report,indent=2))
