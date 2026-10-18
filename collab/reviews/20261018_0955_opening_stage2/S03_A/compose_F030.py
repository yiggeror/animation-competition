from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import json,hashlib,numpy as np
r=Path(__file__).resolve().parent;s=r.parents[1]/'astra_s03b_painted_pilot_20261018/refs/painted';base=Image.new('RGBA',(1672,941));base.paste(Image.open(s/'S03_grandma_k03_F026_t1.10.png').convert('RGBA'),(0,0))
def poly(pts,blur=1):
 m=Image.new('L',base.size);ImageDraw.Draw(m).polygon(pts,fill=255);return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m
raw=Image.open(r/'originals/S03_F030_local_connections_call08.png').convert('RGBA');arms=base.copy();arms.paste(raw.resize((850,290),Image.Resampling.LANCZOS),(400,530))
left=poly([(472,587),(527,581),(606,650),(650,654),(700,638),(753,643),(807,662),(838,699),(880,698),(880,744),(820,770),(814,799),(746,797),(675,771),(597,790),(516,818),(444,815),(425,780),(425,710),(465,649)])
# Keep the original sleeve outer contour until the shared arm boundary at y619; only the interior connection can change above that.
interior=base.getchannel('A').point(lambda a:255 if a>220 else 0).filter(ImageFilter.MinFilter(9));clip=Image.new('L',base.size,255);clip.paste(interior.crop((0,0,1672,619)),(0,0));left=ImageChops.darker(left,clip)
right=poly([(856,694),(897,674),(951,671),(1001,687),(1040,697),(1082,693),(1082,640),(1117,616),(1162,640),(1207,708),(1246,768),(1245,816),(1172,822),(1104,818),(1047,827),(1006,822),(949,822),(893,806),(865,777)])
mask=ImageChops.lighter(left,right);out=Image.composite(arms,base,mask)
headm=Image.open(r/'masks/F017_head_neck.png');head=Image.open(r/'originals/S03_F030_call07.png').convert('RGBA');out=Image.composite(head,out,headm);mask=ImageChops.lighter(mask,headm)
# Basin prop: preserve old source rim/bowl/contents exactly; follow actual upper rim contour. No global plate adjustment.
basin=poly([(554,852),(565,838),(595,826),(642,815),(700,809),(760,804),(832,802),(902,805),(967,813),(1026,822),(1082,835),(1124,850),(1124,941),(554,941)],0)
out=Image.composite(base,out,basin);mask=ImageChops.subtract(mask,basin)
for n,m in [('left',left),('right',right),('head',headm),('basin_lock',basin),('all_changes',mask)]:m.save(r/f'masks/F030_{n}.png')
p=r/'candidates/S03_F030_local_composite_v1.png';out.save(p);a=np.array(base);b=np.array(out);mm=np.array(mask);changed=np.any(a!=b,axis=2)
checks={'outside_mask_changed_pixels':int(np.sum(changed&(mm==0))),'basin_mask_changed_pixels':int(np.sum(changed&(np.array(basin)>0))),'size':out.size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(r/'F030_composition_manifest.json').write_text(json.dumps({'base':'k03','head_source':'originals/S03_F030_call07.png','arm_source':'originals/S03_F030_local_connections_call08.png','arm_raw_size':raw.size,'arm_native_crop':[400,530,1250,820],'control':'local_refs/F030_control_manifest.json','mask':'masks/F030_all_changes.png','checks':checks},indent=2))
m=json.loads((r/'manifest.json').read_text());m.pop('pending_call',None);m['outputs'].append({'frame':30,'call':8,'path':str(r/'originals/S03_F030_local_connections_call08.png'),'sha256':hashlib.sha256((r/'originals/S03_F030_local_connections_call08.png').read_bytes()).hexdigest(),'size':raw.size,'mode':raw.mode,'status':'candidate_local_connection_repair','edit_target':'local_refs/F030_positioned_generated_hands_guide.png','prompt':'prompts/F030_local_connections_call08.txt'});(r/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps(checks))
