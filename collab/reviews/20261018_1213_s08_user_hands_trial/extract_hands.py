from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import numpy as np,json,hashlib
p=Path(__file__).resolve().parent;im=Image.open(p/'originals/user_latest_atlas.png').convert('RGBA');a=np.array(im)
polys={
'left_hand_box':[(855,500),(885,502),(901,525),(920,525),(938,521),(956,516),(1040,513),(1086,502),(1103,502),(1136,539),(1139,568),(1120,578),(1115,607),(1103,625),(1081,626),(1070,643),(1048,649),(1033,666),(1009,670),(989,661),(967,651),(946,639),(929,626),(913,610),(893,613),(876,629),(851,636),(831,625),(817,603),(813,572),(820,540),(831,521)],
'right_hand_match':[(729,669),(765,662),(808,654),(823,660),(843,674),(866,685),(894,703),(920,650),(922,627),(938,621),(947,630),(941,647),(929,655),(907,706),(915,733),(908,745),(880,749),(868,758),(855,761),(846,779),(824,785),(813,799),(786,802),(773,791),(763,783),(746,778),(729,778)]}
records={}
for name,pts in polys.items():
 m=Image.new('L',im.size,0);ImageDraw.Draw(m).polygon(pts,fill=255);ma=np.array(m);out=a.copy();out[:,:,3]=np.minimum(out[:,:,3],ma)
 rgb=out[:,:,:3].astype(int);mx=rgb.max(2);mn=rgb.min(2)
 fringe=(mx-mn>100)&(((rgb[:,:,0]>180)&(rgb[:,:,1]<115))|((rgb[:,:,1]>180)&(rgb[:,:,2]<100))|((rgb[:,:,2]>160)&(rgb[:,:,0]<100)))
 edge=np.array(m.filter(ImageFilter.MinFilter(7)))==0;clean=(out[:,:,3]<24)|(fringe&edge)
 if name=='right_hand_match':
  cloth=(rgb[:,:,2]>rgb[:,:,0]*.98)&(rgb[:,:,2]>rgb[:,:,1]*1.02)&(rgb[:,:,2]>65)
  cloth=np.array(Image.fromarray((cloth*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)))>0
  clean|=cloth
 out[clean,3]=0;keep=Image.fromarray(out);bb=keep.getbbox();cro=keep.crop(bb);cro.save(p/'candidates'/f'{name}.png');m.save(p/'masks'/f'{name}_selection.png');Image.fromarray(out[:,:,3]).save(p/'masks'/f'{name}_actual_alpha.png')
 records[name]={'source_crop_xyxy':bb,'size':cro.size,'source_polygon':pts,'source_rgb_preserved':True,'alpha_only_cleanup_pixels':int(np.sum(clean&(a[:,:,3]>0)&(ma>0))),'sha256':hashlib.sha256((p/'candidates'/f'{name}.png').read_bytes()).hexdigest()}
combined=Image.new('RGBA',im.size)
for name,r in records.items():combined.alpha_composite(Image.open(p/'candidates'/f'{name}.png'),r['source_crop_xyxy'][:2])
bb=combined.getbbox();combined.crop(bb).save(p/'candidates/hands_and_props_registered.png');records['registered_union']={'source_crop_xyxy':bb,'size':combined.crop(bb).size}
preview=Image.new('RGB',(1200,440),'#e5e5e5');c=combined.crop((640,470,1160,820));preview.paste(c,(20,20),c);preview.paste((35,35,35),(600,0,1200,440));preview.paste(c,(620,20),c);preview.save(p/'qa/hands_on_light_dark.png')
json.dump({'source_sha256':hashlib.sha256((p/'originals/user_latest_atlas.png').read_bytes()).hexdigest(),'source_size':im.size,'parts':records,'status':'trial-only; not whole-arm approval; no pose or camera changed','coordinates':'all boxes/polygons are original 1717x916 atlas pixels; no scale or pose transform'},open(p/'manifest.json','w'),ensure_ascii=False,indent=2)
