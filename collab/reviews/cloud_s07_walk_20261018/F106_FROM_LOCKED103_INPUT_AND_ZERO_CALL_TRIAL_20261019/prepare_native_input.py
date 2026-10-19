from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parent;B=R.parent;S=B/'F103_REPAIR_NATIVE_call02_fa796ff9_20261019'
G=B/'F103_REPAIR_DRAFT_AFTER_call01_SHORT_SLEEVE_REAL_PANTS_20261019'
T=B/'F100_103_106_closing_batch_20261019/next_states_61sol/reference'
for d in ['sources','layers','candidate','qa','masks','requests','inputs_1024x1536','reference_native','geometry']:(R/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=S/'candidate/F103_REPAIR_call02_PROTECTED_SEMANTIC_TRIAL_PENDING_ASTRA.png'
assert sha(sp)=='06443a17f780d7a72a293c27686099ffaf72ba827b00e3290059c3061cd2ad90'
for n,p in {'F103_LOCKED06443a17.png':sp,'ORIGINAL_physical_lamp_NO_table_shadow.png':T/'existing_lamp_object_same_registration.png','ORIGINAL_table_shadow_NOT_lifted.png':T/'existing_lamp_shadow_same_registration.png'}.items():shutil.copyfile(p,R/'sources'/n)
src=Image.open(sp).convert('RGBA');a=np.array(src);size=src.size;yy,xx=np.indices(a.shape[:2]);dy=-12.359119141727836
near=np.array(Image.open(S/'masks/RAW_complete_near_bare_arm_whole_grip.png').convert('L'))>0
hand=near&(((xx-1690)*.75-(yy-357)*.66)>=0)
hz=np.zeros_like(a);hz[hand]=a[hand]
lamp=Image.open(R/'sources/ORIGINAL_physical_lamp_NO_table_shadow.png').convert('RGBA')
grp=lamp.copy();grp.alpha_composite(Image.fromarray(hz));grp.save(R/'layers/F103_ONE_actual_complete_hand_and_entire_physical_lamp_NO_shadow.png')
lift=lambda im:im.transform(size,Image.Transform.AFFINE,(1,0,0,0,1,-dy),Image.Resampling.BICUBIC,fillcolor=0)
moved=lift(grp);moved.save(R/'layers/F106_ONE_same_actual_complete_hand_and_entire_physical_lamp_LIFTED.png')
mhand=np.array(lift(Image.fromarray((hand*255).astype('uint8')).convert('RGBA')))[:,:,0]>0
mlamp=np.array(lift(lamp))[:,:,3]>0
guardgrp=np.array(moved)[:,:,3]>0
head=np.array(Image.open(S/'layers/ORIGINAL24_head_neck.png'))[:,:,3]>0
far=np.array(Image.open(S/'layers/ORIGINAL24_complete_far_arm_hand_jade.png'))[:,:,3]>0
shoes=np.array(Image.open(S/'layers/ORIGINAL_whole_shoes_FIXED.png'))[:,:,3]>0
def poly(ps):
 im=Image.new('L',size);ImageDraw.Draw(im).polygon(ps,fill=255);return np.array(im)>0
# Complete old/new short sleeve, true bare arm and wrist corridors plus vacated
# blouse material. The reference white domain is never a tool executable mask.
domain=poly([(1440,225),(1570,220),(1660,295),(1708,300),(1732,338),(1703,377),(1660,420),(1618,474),(1550,478),(1490,425),(1440,360)])
white=binary_dilation(domain|near|np.array(lift(Image.fromarray((near*255).astype('uint8')).convert('RGBA')))[:,:,0].astype(bool),iterations=8)
white&=~(head|far|shoes|guardgrp)
waist=(yy>=500)&(yy<1080)&~(mlamp|guardgrp)
white&=~waist
Image.fromarray((white*255).astype('uint8')).save(R/'masks/WHITE_complete_old_new_short_sleeve_bare_arm_waist_vacancy_CONNECTION.png')
for name,m in [('KEEP_moved_same_whole_hand_lamp',guardgrp),('KEEP_moved_same_complete_hand',mhand),('KEEP_moved_entire_physical_lamp',mlamp),('KEEP_original_head',head),('KEEP_original_far_complete_arm_hand_jade',far),('KEEP_original_whole_shoes',shoes),('KEEP_original_waist_legs_shoes',waist),('OLD_complete_near_bare_arm_and_hand',near)]:Image.fromarray((m*255).astype('uint8')).save(R/'masks'/f'{name}.png')
A=Image.open(R/'candidate/F106_ZERO_CALL_WHOLE_BARE_ARM_AND_GRIP_LAMP_TRANSLATION_TRIAL.png').convert('RGBA')
# A is a placement reference, with no old arm under the raised true volume.
# Its visible vacated blouse strip is UNKNOWN to reconstruct in B, not final art.
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',13)
ImageDraw.Draw(A).text((1248,10),'F106 LOCAL ARM INPUT / SAME TRUE GRIP+LAMP LIFTED / NOT FINAL',font=font,fill='#427d98')
Bim=Image.fromarray((white*255).astype('uint8')).convert('RGBA');C=A.copy();cd=ImageDraw.Draw(C)
chain=[(1552,260),(1575,378),(1605,430),(1690,345),(1743.939126549811,322.54435707010913)]
cd.line(chain,fill='#9455a2',width=2)
for x,y in chain:cd.rectangle((x-2,y-2,x+2,y+2),fill='#9455a2')
cd.text((1250,775),'Real short sleeve + whole bare arm volume; guides are NOT bones.',font=font,fill='#427d98')
D=Image.new('RGBA',size);dd=ImageDraw.Draw(D)
for box,xy,sc in [((1485,245,1585,375),(1260,80),2.5),((1560,370,1590,405),(1630,100),4),((1480,445,1540,485),(1300,650),3)]:
 z=src.crop(box);D.alpha_composite(z.resize((round(z.width*sc),round(z.height*sc)),Image.Resampling.LANCZOS),xy)
dd.text((1250,25),'LOCKED103 SHORT SLEEVE / ADJACENT BARE SKIN ONLY',font=font,fill='#427d98')
dd.text((1250,900),'No old open hand / no alternative grip or body pose.',font=font,fill='#427d98')
for letter,im in [('A',A),('B',Bim),('C',C),('D',D)]:
 im.crop((1240,0,1960,1080)).save(R/f'reference_native/{letter}_F106_720x1080.png')
 im.crop((1240,0,1960,1080)).resize((1024,1536),Image.Resampling.NEAREST if letter=='B' else Image.Resampling.LANCZOS).save(R/f'inputs_1024x1536/{letter}_F106_PREPARED.png')
for tone,col in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
 board=Image.new('RGB',(1364,1024),(231,238,244))
 for j,letter in enumerate('ABCD'):
  im=Image.open(R/f'inputs_1024x1536/{letter}_F106_PREPARED.png').convert('RGBA');bg=Image.new('RGBA',im.size,col);bg.alpha_composite(im);board.paste(bg.resize((341,512)).convert('RGB'),(j*341,0))
 bg=Image.new('RGBA',size,col);bg.alpha_composite(A);board.paste(bg.crop((1480,235,1810,485)).resize((660,500)).convert('RGB'),(0,524));board.paste(bg.crop((1570,300,1870,700)).resize((600,500)).convert('RGB'),(700,524));board.save(R/f'qa/F106_four_actual_inputs_and_grip_{tone}.png')
prompt='''Create ONE local F106 illustration edit only, on the unchanged 1024x1536 transparent composition of A. The only mother is the ACTUAL locked F103, SHA256 06443a17f780d7a72a293c27686099ffaf72ba827b00e3290059c3061cd2ad90. A already places the SAME actual complete closed right hand (whole palm, all four curled fingers and opposing thumb) and the SAME entire physical lantern together upward by native (0,-12.359119141727836), equal to world (0,-4.5). Their relationship, registration, scale, angle and real wire enclosure are FROZEN. Do not move or redraw the lamp to meet a new hand. Do not independently fit, resize, rotate or redesign any hand, finger, bail, glass, frame, fuel body or base. The original curved bail is naturally behind the complete front fingers and in front of the rear palm; never expose a wire through the hand or draw a new line on skin.

Rearticulate ONLY the complete near right shoulder-to-short-sleeve, bare upper arm, ONE anatomical elbow, bare forearm and natural wrist so this single continuous arm naturally connects the unchanged body to that already raised whole hand. Preserve the real blue flower SHORT sleeve ending at the upper arm. Draw actual matching bare skin from its true hem onward; never add long cloth, a wrist cuff, blue sleeve capsules or round artificial joints. A/C show the real103 cloth and actual whole bare-arm volume placed at the new height, not a second arm or final certified anatomy. Their little vacated strip below the old arm and the provisional sleeve boundary are UNKNOWN, not holes to preserve: reconstruct the newly exposed continuous SAME blue flower blouse naturally across the complete underarm/chest connection. Do not trace an old arm edge into cloth, leave a transparent crescent, overlap two arms, paste a wrist bridge or add a chest rectangle. The old103 near arm/hand underneath has been removed.

B opens the COMPLETE old/new arm corridors, short sleeve root and hem, underarm, elbow, forearm, full wrist entrance and necessary exposed blouse connection. It is a semantic editing reference, not an executable hard mask. C repeats ONE complete short-sleeve-to-bare-arm-to-whole-hand placement; its thin guide is NOT final anatomy or measured bone. D supplies only real103 short sleeve, immediately adjacent skin and internal actual blouse material, with no old open-hand pose. Finish this entire connection as coherent natural source-matching illustration. Keep the original color and ink; no global recolor, gray technical waist panel, apron, extra garment or duplicate person.

The body/head remain at the accepted24degree lean with NO movement or rescaling. Preserve the original head/neck, complete far left arm/hand/jade group, whole continuous waist and navy trousers, both complete shoes and original foot contacts. Preserve the already raised same whole gripping hand and full physical lantern. The lamp has now lifted4.5world above the table but remains completely DARK: no emission, beam, glow or lit wick. The table support shadow is separate stationary context, NOT part of the moving lamp group; do not translate it with the lamp or paint a new room/table. No new body pose or following action. Remove labels, guides and construction marks. Return one transparent actual F106 drawing only; no contact sheet or extra output. This is the single necessary local full-arm request; actual cuff/elbow/wrist and full-hand enclosure will be reviewed before adoption.'''
prompt=prompt+'\n';(R/'requests/prompt_FINAL_EXACT.txt').write_text(prompt)
args={'prompt':prompt,'referenced_image_paths':[str((R/f'inputs_1024x1536/{l}_F106_PREPARED.png').resolve())for l in 'ABCD'],'transparent_background':True}
(R/'requests/arguments_FINAL_EXACT.json').write_text(json.dumps(args,ensure_ascii=False,indent=2)+'\n')
checks={'locked103_commit':'84334c3f7b0ab72e9e700ae3e165617945ef615e','locked103_SHA256':sha(sp),'one_complete_same_hand_and_entire_lamp_group_native_translation':[0,dy],'world_translation':[0,-4.5],'rotation':0,'scale':1,'body_head_fararm_waist_legs_shoes_transform':'identity from locked103','shadow_transform':[0,0],'shadow_in_lifted_group':False,'whole_tool_mapping':'1024x1536; whole inverse45/64+[1240,0]','zero_call_trial_status':'HOLD actual cuff edge and vacated blouse strip, local native connection necessary','calls_before_request':0,'input_SHA256':{l:sha(R/f'inputs_1024x1536/{l}_F106_PREPARED.png')for l in 'ABCD'},'prompt_SHA256':sha(R/'requests/prompt_FINAL_EXACT.txt'),'white_guard_overlap_pixels':int((white&(head|far|shoes|guardgrp|waist)).sum())}
assert checks['white_guard_overlap_pixels']==0
(R/'geometry/frozen_same_actual_hand_lamp_lift.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
