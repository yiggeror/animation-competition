from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_closing,binary_dilation
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;OLD=B/'F100_zero_call_semantic_trial_20261019';S=B/'F100_local_arm_call02_input_GATE_20261019/sources';L=B/'F100_local_arm_call02_input_GATE_20261019/layers';sz=(1960,1080)
for d in['candidate','layers','masks','qa']:(R/d).mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:Image.open(p).convert('RGBA')
def pad(im):
 z=Image.new('RGBA',sz);z.alpha_composite(im);return z
def cut(im,m):return Image.fromarray(np.where(m[:,:,None],np.array(im),0).astype('uint8'))
new=load(OLD/'layers/RAW_person_common45over64_plus1240_0.png');a=np.array(new);rgb=a[:,:,:3].astype(int);active=a[:,:,3]>0;yy,xx=np.indices(a.shape[:2])
# One connected REAL blue garment material, closing ink then filling complete white
# flower holes. Selection follows source material, never an underarm mixed seam.
def cloth_material(im):
 z=np.array(im);c=z[:,:,:3].astype(int);ac=z[:,:,3]>0
 blue=(c[:,:,2]>c[:,:,0]+20)&(c[:,:,1]>c[:,:,0]+10)&(c[:,:,2]>c[:,:,1]+10)&ac
 blue=binary_closing(blue,iterations=2)&ac;lab,_=label(blue);ct=np.bincount(lab.ravel());ct[0]=0;core=lab==ct.argmax()
 return binary_dilation(binary_fill_holes(core),iterations=2)&ac
blouse=cloth_material(new)
# The already-approved complete near-arm layer includes the SAME raw short sleeve.
# Its color/placement is unchanged; this union keeps the full actual shoulder/cuff.
near=load(OLD/'layers/RAW_complete_new_near_sleeve_arm_hand.png');na=np.array(near);nmask=na[:,:,3]>0
blouse&=~((rgb[:,:,0]>150)&(rgb[:,:,0]>rgb[:,:,1]+14)&(rgb[:,:,1]>rgb[:,:,2]+8))
# Restore all actual shirt material, including its real ink/AA/flowers, through the
# near-layer short sleeve; skin stays a separate unchanged approved ownership layer.
nearblue=cloth_material(near);blouse|=nearblue
shirt=cut(new,blouse)
sourcehead=pad(load(L/'ORIGINAL16_head_chest_body_WITHOUT_competing_near_sleeve.png'));s=np.array(sourcehead);scloth=cloth_material(sourcehead)
# Real source head/hair/glasses and flesh, with no retained source-chest cloth.
sc=s[:,:,:3].astype(int);skin=(sc[:,:,0]>145)&(sc[:,:,0]>sc[:,:,1]+12)&(sc[:,:,1]>sc[:,:,2]+8)&(s[:,:,3]>0)
sl,_=label(skin);seed=sl[190,1660];ss=sl==seed if seed else skin
headmask=(s[:,:,3]>0)&(yy<300)&~scloth
headmask|=binary_fill_holes(ss)&(s[:,:,3]>0)&(yy<300)
headneck=cut(sourcehead,headmask)
pants=load(OLD/'layers/BLEND_pants_wide_slanted_same_plane_overlap.png');far=load(OLD/'layers/SOURCE_complete_far_arm_hand_jade.png');ff=pad(load(S/'F100_far_whole_shoe_FIXED.png'));nf=pad(load(S/'F100_near_whole_shoe_FIXED.png'));lamp=pad(load(S/'ORIGINAL_fixed_lamp_same_native_registration.png'))
out=Image.new('RGBA',sz)
for z in[ff,pants,far,headneck,shirt,near,nf,lamp]:out.alpha_composite(z)
out.save(R/'candidate/F100_WHOLE_RAW_BLOUSE_final_RGBA_PENDING_ASTRA.png')
shirt.save(R/'layers/WHOLE_actual_call02_blouse_from_neck_to_full_hem.png');headneck.save(R/'layers/ORIGINAL16_head_hair_face_glasses_neck_NO_old_chest.png')
Image.fromarray(blouse.astype('uint8')*255).save(R/'masks/WHOLE_RAW_blouse_material_NO_underarm_blend.png');Image.fromarray(headmask.astype('uint8')*255).save(R/'masks/ORIGINAL16_actual_head_neck_material.png')
old095=pad(load(B/'F100_next_gate_20261019/sources/F095_dcf919f4_LOCKED_MOTHER.png'));old095.alpha_composite(lamp);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for tone,col in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 comp=Image.new('RGBA',sz,col);comp.alpha_composite(out);comp.convert('RGB').save(R/f'qa/F100_whole_blouse_{tone}.png');sheet=Image.new('RGB',(1440,1110),(233,239,244));dr=ImageDraw.Draw(sheet)
 for j,(title,img)in enumerate([('095 LOCKED / fixed original lamp',old095),('100 WHOLE RAW BLOUSE / original head-neck',out)]):
  z=Image.new('RGBA',sz,col);z.alpha_composite(img);sheet.paste(z.crop((1240,0,1960,1080)).convert('RGB'),(j*720,30));dr.text((j*720+8,5),title,font=font,fill='#36536b')
 sheet.save(R/f'qa/F095_F100_same_frame_{tone}.png');board=Image.new('RGB',(1320,820),(233,239,244));bd=ImageDraw.Draw(board)
 for j,(box,title)in enumerate([((1510,190,1715,345),'SOURCE head/neck + RAW collar/shoulder'),((1440,300,1660,500),'Whole RAW shoulder/cuff/underarm, NO blend')]):
  c=comp.crop(box).resize((660,700),Image.Resampling.NEAREST);board.paste(c.convert('RGB'),(j*660,45));bd.text((j*660+8,8),title,font=font,fill='#36536b')
 board.save(R/f'qa/neck_collar_shoulder_underarm_{tone}_close.png')
q={'status':'ONE_ZERO_CALL_WHOLE_BLOUSE_SEMANTIC_REINTEGRATION_PENDING_ACTUAL_REVIEW','raw_source_sha256':'b21f0b8b18e35657626575b827bddd6fc8e287a4b2cbdbc6c39a885de8793041','one_common_inverse':{'scale':45/64,'offset':[1240,0]},'new_color_generation_or_color_correction':False,'raw_garment_RGB_original':True,'old_chest_blend_layer_used':False,'SHIRT_underarm_mix_mask_used':False,'retained_layers_unchanged':{str(p.relative_to(B)):sha(p) for p in[OLD/'layers/RAW_complete_new_near_sleeve_arm_hand.png',OLD/'layers/BLEND_pants_wide_slanted_same_plane_overlap.png',OLD/'layers/SOURCE_complete_far_arm_hand_jade.png',S/'F100_near_whole_shoe_FIXED.png',S/'F100_far_whole_shoe_FIXED.png',S/'ORIGINAL_fixed_lamp_same_native_registration.png']},'layer_order':['source_farshoe','unchanged_passed_pants','unchanged_complete_fararm_hand_jade','source16_head_hair_face_glasses_neck','whole_raw_continuous_blouse','unchanged_raw_near_sleeve_arm_hand','source_nearshoe','source_whole_lamp'],'actual_blouse_material_pixels':int(blouse.sum()),'candidate_sha256':sha(R/'candidate/F100_WHOLE_RAW_BLOUSE_final_RGBA_PENDING_ASTRA.png'),'calls':0,'git':0};(R/'qa/short_checks.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))
