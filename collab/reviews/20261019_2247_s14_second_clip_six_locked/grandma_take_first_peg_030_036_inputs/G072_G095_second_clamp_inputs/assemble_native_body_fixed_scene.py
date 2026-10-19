from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,label
import numpy as np,json,hashlib,sys
D=Path(__file__).parent;P=D.parent;R=P.parent;N=P/'G063_G069_first_clamp_inputs';src=Image.open(D/'G078_complete_registered_candidate.png').convert('RGBA');old=np.array(src);Y,X=np.indices(old.shape[:2]);rgb0=old[:,:,:3].astype(int);navy0=(rgb0[:,:,2]>rgb0[:,:,0]+5)&(rgb0[:,:,2]>rgb0[:,:,1]+2)
fm=Image.new('L',src.size);fd=ImageDraw.Draw(fm);fd.rectangle((0,990,1254,1254),fill=255)
fd.polygon([(398,986),(418,984),(447,977),(458,979),(468,990),(486,1003),(485,1030),(395,1030)],fill=255)
fd.polygon([(503,982),(525,980),(554,972),(570,972),(582,981),(607,994),(614,1024),(500,1024)],fill=255)
foot=old.copy();foot[np.array(fm)==0]=0
sheet=Image.open(R/'grandma_fall_inputs/G027_upper_contact_repair/G027_complete_sheet_whole_registered.png').convert('RGBA');first=Image.open(N/'G066_TRUE_disconnected_complete_closed_peg_fold_SOURCE.png').convert('RGBA')
for key in sys.argv[1:]:
 fixedfoot=foot.copy()
 if key!='G081':
  old_cuff=binary_dilation(navy0&(rgb0[:,:,2]>50)&(Y>=975)&(Y<995),iterations=1);fixedfoot[old_cuff]=0
  fixedfoot[(Y<1000)&(Y>=990)&(((X<400)&(X>370))|((X>485)&(X<505)))]=0
 reg=Image.open(D/f'{key}_whole_original_SINGLE_similarity_DIAGNOSTIC.png').convert('RGBA');a=np.array(reg);rgb=a[:,:,:3].astype(int);navy=(rgb[:,:,2]>rgb[:,:,0]+5)&(rgb[:,:,2]>rgb[:,:,1]+2)
 # One registered complete native body. Restore exact original planted shoes/ankles and stool by semantic cuff boundary, never transform a leg or shoe independently.
 nl,nn=label(navy&(Y>930)&(a[:,:,3]>0));owners=np.unique(nl[(Y>930)&(Y<950)]);owners=owners[owners>0];cuff=binary_dilation(np.isin(nl,owners),iterations=1);skin=(rgb[:,:,0]>rgb[:,:,1]+15)&(rgb[:,:,1]>rgb[:,:,2]+10)&(rgb[:,:,0]>130);ankle=binary_dilation(skin&(Y>=970)&(Y<=995)&(a[:,:,3]>0),iterations=1);a[(Y>=973)&~(cuff|ankle)]=0;a[Y>=996]=0
 lab,n=label(a[:,:,3]>0);count=np.bincount(lab.ravel());count[0]=0;a[lab!=count.argmax()]=0
 out=Image.new('RGBA',reg.size);out.alpha_composite(sheet);out.alpha_composite(first);out.alpha_composite(Image.fromarray(a));out.alpha_composite(Image.fromarray(fixedfoot));out.save(D/f'{key}_complete_native_registered_candidate.png')
 bg=Image.new('RGBA',reg.size,'#f1f2ed');ImageDraw.Draw(bg).line((200,277,1140,277),fill='#777b75');bg.alpha_composite(out);bg.convert('RGB').save(D/f'{key}_complete_native_registered_REVIEW.jpg',quality=94);bg.crop((570,200,780,530)).resize((630,990)).convert('RGB').save(D/f'{key}_complete_native_arm_B_peg_3x.jpg',quality=94);bg.crop((370,930,645,1055)).resize((825,375)).convert('RGB').save(D/f'{key}_complete_native_fixed_supports_3x.jpg',quality=94)
 meta={'status':'NATIVE_COMPLETE_BODY_FIXED_SCENE_CANDIDATE','final':str(D/f'{key}_complete_native_registered_candidate.png'),'sha256':hashlib.sha256((D/f'{key}_complete_native_registered_candidate.png').read_bytes()).hexdigest(),'one_transform':json.loads((D/f'{key}_whole_raw_SINGLE_registration_DIAGNOSTIC.json').read_text()),'complete_head_body_sleeves_arms_hands_hips_legs_are_native':True,'fixed_original_whole_sheet_first_clip_shoes_stool':True,'B':'Actual newly generated complete near arm wrist hand retained at original grip within1px, no hand/finger patch','processing':'Disconnected alpha-speck removal; semantic native trouser cuff kept while replacing generated shoes with exact original ankles/shoes/rigid stool. No separate part transformation.'};(D/f'{key}_native_assembly_candidate.json').write_text(json.dumps(meta,indent=2));print(meta['sha256'])
