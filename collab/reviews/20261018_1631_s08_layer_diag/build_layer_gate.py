from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_fill_holes,binary_dilation
import numpy as np,hashlib,json
D=Path(__file__).resolve().parent;W=D.parents[2];src=W/'astra_s08_first_mother_20261018_1433/F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png'
expected='c803571d4a6446e783fcbeb7aef41d65c1862ff3bf78a9a53f34b4631170e3f3';assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
im=Image.open(src).convert('RGBA');a=np.array(im);h,w=a.shape[:2];r,g,b=[a[:,:,k].astype(int) for k in range(3)];alpha=a[:,:,3]>0
# Broad hand-traced actual-arm envelopes, not a rectangular below-table reveal.
near=[(652,824),(682,807),(710,791),(735,783),(742,795),(759,844),(787,894),(837,870),(879,848),(926,818),(968,798),(1009,781),(1042,776),(1062,791),(1061,827),(1053,847),(1036,863),(1008,879),(980,881),(961,878),(923,903),(887,930),(850,954),(816,978),(799,989),(783,999),(768,1003),(751,1000),(737,986),(723,969),(707,943),(690,909),(675,871)]
far=[(993,850),(1046,825),(1081,884),(1122,845),(1146,815),(1207,825),(1214,844),(1195,875),(1161,922),(1127,961),(1098,988),(1078,1000),(1058,1001),(1040,990),(1027,971),(1018,947),(1008,916)]
env=Image.new('L',(w,h));ed=ImageDraw.Draw(env);ed.polygon(near,fill=255);ed.polygon(far,fill=255);en=np.array(env)>0
skin=(r-b>24)&(r-g>10)&(r>115)&alpha&en
skin=binary_fill_holes(skin)
mask=binary_dilation(skin,iterations=2)&en&alpha
# Do not lift blue torso pigment into the table-front plane.
blue=(b-r>35)&(b-g>12)&(np.maximum.reduce([r,g,b])>100)
mask &= ~blue
# Original hand+box+jade and near match are whole original-pixel props above the edge.
prop=Image.new('L',(w,h));pd=ImageDraw.Draw(prop)
pd.polygon([(1088,737),(1168,737),(1183,747),(1190,775),(1194,804),(1213,824),(1215,850),(1186,862),(1150,851),(1140,827),(1112,805),(1090,783)],fill=255)
pd.polygon([(1047,788),(1071,753),(1085,752),(1088,772),(1061,808)],fill=255)
mask |= (np.array(prop)>0)&alpha
# Preserve all existing RGBA at each selected pixel and exclusively partition its alpha.
front=a.copy();back=a.copy();front[~mask,3]=0;back[mask,3]=0
Image.fromarray(mask.astype('uint8')*255).save(D/'masks/forearms_elbows_FOREGROUND_binary.png')
Image.fromarray(front).save(D/'frames/F000_forearms_elbows_original_pixels.png');Image.fromarray(back).save(D/'frames/F000_body_behind_original_pixels.png')
# Pixel partition proves no redraw, movement, duplicated semi-transparent pixels, or alpha resampling.
assert np.array_equal(front[mask],a[mask]);assert np.array_equal(back[~mask],a[~mask]);assert not np.any((front[:,:,3]>0)&(back[:,:,3]>0));assert np.array_equal(front[:,:,3].astype(int)+back[:,:,3].astype(int),a[:,:,3])
rebuild=Image.alpha_composite(Image.fromarray(back),Image.fromarray(front));assert np.array_equal(np.array(rebuild),a)
roi=(620,725,1230,1025)
def comp(x,bg=(224,224,221,255)):
 out=Image.new('RGBA',(w,h),bg);out.alpha_composite(x);return out
full=comp(im);frontgray=comp(Image.fromarray(front));backgray=comp(Image.fromarray(back))
ov=np.array(full).copy();ov[mask,:3]=np.round(ov[mask,:3]*.4+np.array([245,57,154])*.6).astype('uint8');ov=Image.fromarray(ov)
for pic in [full,frontgray,backgray,ov]:ImageDraw.Draw(pic).line((620,981,1230,981),fill=(243,112,30,255),width=1)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
board=Image.new('RGB',(1220,660),(244,243,238));dd=ImageDraw.Draw(board)
for i,(pic,label) in enumerate([(full,'LOCKED SOURCE / orange = original table front y981'),(ov,'BINARY SEMANTIC FOREGROUND / pink'),(backgray,'BODY BACK / table still occludes lower torso'),(frontgray,'ORIGINAL ARMS + HANDS / no redraw or shift')]):
 x=(i%2)*610;y=(i//2)*330;dd.text((x+8,y+5),label,font=font,fill=(24,24,24));board.paste(pic.crop(roi).convert('RGB'),(x,y+28))
board.save(D/'references/F000_layer_gate_4panel.jpg',quality=97)
# Non-Canvas neutral topology demonstration. Uses exact source table geometry only.
table=Image.new('RGBA',(w,h));td=ImageDraw.Draw(table);td.rectangle((764,981,1920,1028.6),fill='#6a4226');td.rectangle((785,1028.6,1920,1080),fill='#5a361e');td.rectangle((764,981,1920,1028.6),outline='#3e2a1e',width=5)
old=comp(im);old.alpha_composite(table);new=comp(Image.fromarray(back));new.alpha_composite(table);new.alpha_composite(Image.fromarray(front))
compare=Image.new('RGB',(1220,340),(244,243,238));q=ImageDraw.Draw(compare)
for i,(pic,label) in enumerate([(old,'TOPOLOGY ONLY: source behind original front'),(new,'TOPOLOGY ONLY: original elbows in front')]):q.text((i*610+8,4),label,font=font,fill=(24,24,24));compare.paste(pic.crop(roi).convert('RGB'),(i*610,30))
compare.save(D/'references/F000_layer_order_topology_NOT_CANVAS.jpg',quality=97)
y,x=np.where(mask & (np.indices(mask.shape)[0]>=981));report={'status':'INPUT_LAYER_GATE_PENDING_COORDINATOR','source':str(src),'source_sha256':expected,'source_canvas':[w,h],'mask':'masks/forearms_elbows_FOREGROUND_binary.png','binary_mask_values':[0,255],'foreground_selected_pixels':int(mask.sum()),'selected_y981_and_below':len(x),'selected_lower_bbox_inclusive':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'exact_original_rgba_partition':True,'reassembled_RGBA_equal_source':True,'overlap_alpha_pixels':0,'image_generation_calls':0,'new_canvas_renders':0,'physical_read':'elbows rest at/over near table lip; near elbow at left corner, not a claim of elbows deep on tabletop','mask_method':'hand-traced full real-arm envelopes; warm skin region and actual contour included, blue torso excluded; original whole hands/props included','actual_geometry_unchanged':{'table_front_y':981,'character_sc':1,'character_xy':[0,0],'lamp_only_dx':35},'reference_warning':'neutral PIL layer-order reference demonstrates topology only; final lighting/occlusion requires actual Canvas single frame'}
(D/'LAYER_GATE.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
