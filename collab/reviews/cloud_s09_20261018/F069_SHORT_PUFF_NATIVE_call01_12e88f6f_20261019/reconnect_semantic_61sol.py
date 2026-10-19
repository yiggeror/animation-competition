from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;G=R.parent/'F069_SHORT_PUFF_BARE_ARMS_REPAIR_GATE_20261019'
for d in ['candidate','layers','masks','qa/semantic_reconnection_61sol']:(R/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rawp=R/'originals/F069_SHORT_PUFF_TWO_BARE_ARMS_NATIVE_RAW.png';sp=G/'sources/F069_ACTION_ACCEPTED_COSTUME_REVOKED.png';raw=Image.open(rawp).convert('RGBA');src=Image.open(sp).convert('RGBA');a=np.array(src);assert raw.size==(1145,1374);assert sha(rawp)=='20fc656468f28ca6e9c381f0bfb88e51c0099abce697f792665c9c23c1786eeb'
z=raw.resize((770,924),Image.Resampling.LANCZOS);native=Image.new('RGBA',src.size);native.alpha_composite(z,(550,0));n=np.array(native);native.save(R/'layers/F069_NEW_whole_uniform770over1145_plus550_0.png')
def m(n):return np.array(Image.open(G/'masks'/n).convert('L'))>0
hands=m('KEEP_actual069_complete_palms_all_digits.png');prop=m('KEEP_actual069_visible_prop_slider.png');head=m('KEEP_actual069_head_collar.png');skirt=m('KEEP_actual069_stable_skirt.png');chest=m('KEEP_actual069_valid_nonediting_chest.png');fixed=hands|prop|head|skirt|chest
im=Image.new('L',src.size);ImageDraw.Draw(im).polygon([(578,480),(950,480),(1040,542),(1290,490),(1300,778),(1150,830),(948,830),(918,800),(674,800),(602,715),(575,650)],fill=255);domain=np.array(im)>0
# One complete native front/sleeves/bare-arm material domain; transparent returned vacancies clear former long sleeve, not painted fills.
adopt=domain&~fixed;c=a.copy();c[adopt]=n[adopt];c[fixed]=a[fixed]
cand=Image.fromarray(c);p=R/'candidate/F069_SHORT_PUFF_BARE_ARMS_semantic_RECONNECTED_FIRST_REVIEW.png';cand.save(p)
for name,v in [('ADOPT_complete_native_front_two_short_sleeves_bare_arms',adopt),('KEEP_all_actual_source_protection',fixed),('KEEP_actual_palms_all_digits',hands),('KEEP_actual_prop_slider',prop)]:Image.fromarray(v.astype('uint8')*255).save(R/f'masks/{name}.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',15)
def bg(im,col):
 out=Image.new('RGBA',im.size,col);out.alpha_composite(im);return out.convert('RGB')
for tone,col in [('gray',(215,224,231,255)),('dark',(35,43,52,255))]:
 bg(cand,col).save(R/f'qa/semantic_reconnection_61sol/F069_reconnected_full_{tone}.png')
 box=(575,475,1295,825);bg(cand.crop(box),col).resize((1440,700)).save(R/f'qa/semantic_reconnection_61sol/F069_two_puffs_elbows_wrists_palms_{tone}_2x.png')
 board=Image.new('RGB',(1440,740),(230,237,243));dr=ImageDraw.Draw(board)
 for j,(name,img)in enumerate([('original accepted hands / revoked long sleeves',src),('same new raw uniform inverse',native),('FIRST semantic source protection reconnection',cand)]):
  board.paste(bg(img.crop(box),col).resize((480,234)),(j*480,30));dr.text((j*480+5,5),name,font=font,fill='#35495d')
 for j,b in enumerate([(650,600,845,780),(940,660,1145,825),(960,565,1135,680),(1080,610,1275,720)]):
  board.paste(bg(cand.crop(b),col).resize((350,300)),(j*360,350))
 board.save(R/f'qa/semantic_reconnection_61sol/F069_before_newraw_reconnected_connections_{tone}.png')
changes=np.any(c!=a,axis=2);checks={'candidate':str(p.relative_to(R)),'candidate_SHA256':sha(p),'source_raw_SHA256':sha(rawp),'source_original069_SHA256':sha(sp),'only_registration':{'raw':[1145,1374],'scale':770/1145,'native_size':[770,924],'offset':[550,0],'native_canvas':list(src.size)},'actual_original_source_RGBA_changes':{name:int(changes[v].sum())for name,v in [('head_hair_neck_collar',head),('stable_skirt_waist',skirt),('valid_nonediting_chest',chest),('whole_palms_all_digits',hands),('visible_torch_slider',prop)]},'all_protection_RGBA_changes':int(changes[fixed].sum()),'adoption_outside_complete_semantic_domain':int((changes&~domain).sum()),'actual_new_native_adopted_pixels':int(adopt.sum()),'new_raw_cloth_skin_continuous_material_only':True,'independent_hand_prop_or_arm_fit':False,'raw_whole_image_adopted':False,'status':'FIRST_ACTUAL_SEMANTIC_CANDIDATE_NOT_LOCKED_PENDING_VISUAL_REVIEW','calls':0,'scope':'No073 or bridges. Input labels are not adopted; head/context outside one complete front domain stays actual original source. No old cuff or long sleeve restored deliberately. Any source-returned wrist/prop attachment conflict must be reviewed, not patched or fitted.'}
(R/'qa/semantic_reconnection_61sol/checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
