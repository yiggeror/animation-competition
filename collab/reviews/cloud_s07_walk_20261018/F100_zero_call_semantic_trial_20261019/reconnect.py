from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label,binary_fill_holes,binary_dilation
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;P=B/'F100_expanded_garment_call02_3d32acc6';S=B/'F100_local_arm_call02_input_GATE_20261019/sources';L=B/'F100_local_arm_call02_input_GATE_20261019/layers';size=(1960,1080);scale=45/64;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:Image.open(p).convert('RGBA')
def pad(z):
 o=Image.new('RGBA',size);o.alpha_composite(z);return o
def cut(z,m):return Image.fromarray(np.where(m[:,:,None],np.array(z),0).astype('uint8'))
def blend(s,n,w):
 a=np.array(s).astype(float)/255;b=np.array(n).astype(float)/255;w=w[:,:,None];alpha=a[:,:,3:4]*(1-w)+b[:,:,3:4]*w;rgb=a[:,:,:3]*a[:,:,3:4]*(1-w)+b[:,:,:3]*b[:,:,3:4]*w;rgb=np.divide(rgb,alpha,out=np.zeros_like(rgb),where=alpha>0);return Image.fromarray(np.clip(np.rint(np.concatenate([rgb,alpha],2)*255),0,255).astype('uint8'))
rawpath=P/'originals/F100_expanded_garment_call02_RAW.png';raw=load(rawpath);assert raw.size==(1024,1536)and sha(rawpath)=='b21f0b8b18e35657626575b827bddd6fc8e287a4b2cbdbc6c39a885de8793041';ra=np.array(raw);rl,_=label(ra[:,:,3]>=16);person=rl==rl[700,380];person=binary_dilation(person,iterations=2)&(ra[:,:,3]>0);onlyperson=cut(raw,person);new=Image.new('RGBA',size);new.alpha_composite(onlyperson.resize((720,1080),Image.Resampling.LANCZOS),(1240,0));na=np.array(new);rgb=na[:,:,:3].astype(int);yy,xx=np.indices(na.shape[:2]);active=na[:,:,3]>0
# Complete real short sleeve through all open fingers; selection is semantic,
# never the rectangular B boundary. No finger shortening to fit a crop.
poly=[(286,495),(307,421),(352,374),(398,337),(447,341),(477,367),(498,413),(507,471),(550,446),(622,408),(658,395),(694,397),(727,413),(755,433),(757,453),(751,466),(737,473),(716,470),(691,461),(663,463),(627,495),(574,538),(517,578),(476,599),(452,599),(423,582),(410,564),(362,578),(326,568)]
pm=Image.new('L',size);ImageDraw.Draw(pm).polygon([(1240+x*scale,y*scale)for x,y in poly],fill=255);near=(np.array(pm)>0)&active;near=binary_dilation(near,iterations=1)&active;near_layer=cut(new,near)
sourcebody=pad(load(L/'ORIGINAL16_head_chest_body_WITHOUT_competing_near_sleeve.png'));sourcepants=pad(load(S/'F095_original_whole_trousers_FIXED_ARCHIVE.png'));far=pad(load(S/'F100_far_complete_arm_jade_whole_RIGID16.png'));nf=pad(load(S/'F100_near_whole_shoe_FIXED.png'));ff=pad(load(S/'F100_far_whole_shoe_FIXED.png'));lamp=pad(load(S/'ORIGINAL_fixed_lamp_same_native_registration.png'))
# Remove returned far skin as a whole source-ownership region; the complete
# original far arm/hand/jade layer is restored between pants and blouse.
fa=np.array(far);warm=(rgb[:,:,0]>150)&(rgb[:,:,0]>rgb[:,:,1]+14)&(rgb[:,:,1]>rgb[:,:,2]+8);far_remove=binary_dilation(fa[:,:,3]>0,iterations=12)&warm&active&~near;far_remove=binary_dilation(far_remove,iterations=2)&active&~near
# Actual painted navy, including its complete coherent uppercap/hips/thighs.
navy=active&(yy>480)&(yy<1000)&(xx>1320)&(xx<1665)&(rgb[:,:,2]>=rgb[:,:,0]+4)&(rgb[:,:,2]>=rgb[:,:,1]-3)&(rgb.max(2)<130);ll,_=label(navy);count=np.bincount(ll.ravel());count[0]=0;navy=ll==count.argmax();navy=binary_dilation(binary_fill_holes(navy),iterations=2)&active&~far_remove&~near;feet=(np.array(nf)[:,:,3]>0)|(np.array(ff)[:,:,3]>0);navy &=~feet;newpants=cut(new,navy)
# Wide, slanted material overlap follows the common lower-leg direction/planes.
# No B clipping and no hard horizontal690/810/822 cover; original core remains.
mid=816+.18*(xx-1450);q=np.clip((mid+45-yy)/90,0,1);pantsw=q*q*(3-2*q);pants=blend(sourcepants,newpants,pantsw)
# Whole lower blouse material connects from the actual underarm/side cloth
# into its complete hem. Source upper chest/head are retained above a broad
# slanted underarm material overlap. No color correction is applied.
shirtpoly=[(275,575),(330,540),(415,565),(505,560),(565,555),(555,625),(510,835),(473,837),(218,765),(204,728),(243,667)]
sm=Image.new('L',size);ImageDraw.Draw(sm).polygon([(1240+x*scale,y*scale)for x,y in shirtpoly],fill=255);shirt=(np.array(sm)>0)&active&~far_remove&~near&~navy&~feet;newshirt=cut(new,shirt)
top=425+.14*(xx-1450);v=np.clip((yy-top+14)/28,0,1);shirtw=v*v*(3-2*v);shirtbody=blend(sourcebody,newshirt,shirtw)
# Natural source layer order: rear shoe, trousers, whole far arm, blouse/head,
# entire new near arm, front shoe, entire original table-supported lamp.
out=Image.new('RGBA',size)
for z in[ff,pants,far,shirtbody,near_layer,nf,lamp]:out.alpha_composite(z)
out.save(R/'candidate/F100_ORIGINAL_COLOR_full_semantic_TRIAL.png')
for n,z in[('RAW_person_common45over64_plus1240_0',new),('RAW_complete_new_near_sleeve_arm_hand',near_layer),('RAW_continuous_navy_waist_hips_both_legs',newpants),('RAW_continuous_lower_blouse_hem',newshirt),('SOURCE_complete_far_arm_hand_jade',far),('BLEND_pants_wide_slanted_same_plane_overlap',pants),('BLEND_source_head_chest_new_lower_blouse',shirtbody)]:z.save(R/f'layers/{n}.png')
for n,m in[('RAW_complete_near_sleeve_all_fingers',near),('REMOVE_RAW_far_skin_for_whole_original_group',far_remove),('RAW_complete_navy_material',navy),('RAW_complete_lower_blouse_material',shirt)]:Image.fromarray(m.astype('uint8')*255).save(R/f'masks/{n}.png')
Image.fromarray(np.rint(pantsw*255).astype('uint8')).save(R/'masks/PANTS_wide_slanted_material_overlap_NOT_HORIZONTAL.png');Image.fromarray(np.rint(shirtw*255).astype('uint8')).save(R/'masks/SHIRT_underarm_material_overlap_NOT_B_RECTANGLE.png')
old=pad(load(B/'F100_next_gate_20261019/sources/F095_dcf919f4_LOCKED_MOTHER.png'));old.alpha_composite(lamp);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for tone,col in[('gray',(213,223,231,255)),('dark',(35,43,52,255))]:
 z=Image.new('RGBA',size,col);z.alpha_composite(out);z.convert('RGB').save(R/f'qa/F100_COMPLETE_ORIGINAL_COLOR_{tone}.png');z.crop((1350,230,1780,900)).resize((645,1005)).save(R/f'qa/F100_sleeve_cloth_and_matching_overlap_{tone}.png');sheet=Image.new('RGB',(1960,1110),(235,240,245));d=ImageDraw.Draw(sheet)
 for j,(name,z)in enumerate([('095 LOCKED SOURCE + SAME FIXED LAMP',old),('100 ORIGINAL COLOR SEMANTIC TRIAL',out)]):
  bg=Image.new('RGBA',size,col);bg.alpha_composite(z);sheet.paste(bg.resize((980,1080//2)).convert('RGB'),(980*j,30));d.text((980*j+8,5),name,font=font,fill='#315269')
 sheet.crop((0,0,1960,570)).save(R/f'qa/F095_vs_F100_ORIGINAL_COLOR_{tone}.png')
rec={'status':'ONE_ORIGINAL_COLOR_COMPLETE_SEMANTIC_TRIAL_PENDING_ACTUAL_ASTRA_REVIEW','raw_sha256':sha(rawpath),'one_whole_inverse':{'scale':scale,'offset':[1240,0]},'per_part_transforms':0,'imagegen_calls':0,'source_full_far_arm_group_sha256':sha(S/'F100_far_complete_arm_jade_whole_RIGID16.png'),'source_full_shoes_restored':True,'source_whole_lamp_restored':True,'no_whole_image_color_correction':True,'no690_810_822_rectangle_cover':True,'pants_matching_overlap':'90native wide slanted smooth material overlap; center816+.18*(x−1450), original lowerleg core beyond overlap is retained. No part fit or bone change.','shirt_join':'28native broad slanted underarm material overlap; complete lowerblouse/hem from actual return, original upperchest/head from16source.','actual_adoption_limits':'First complete trial only. If real cloth/flower/plane seams appear at source protection, submit them to Astra, do not iterate or generate again.'};(R/'qa/short_trial_record.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2));print('candidate SHA256',sha(R/'candidate/F100_ORIGINAL_COLOR_full_semantic_TRIAL.png'))
