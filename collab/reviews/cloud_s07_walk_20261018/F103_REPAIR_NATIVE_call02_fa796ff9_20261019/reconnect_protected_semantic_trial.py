"""Zero-call source protection trial. Every visible human pixel is real source art.

One whole native-output inverse registration, then semantic alpha extraction.
No part fitting, drawing, invented RGB, recoloring, or lamp movement.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import label, binary_dilation, binary_fill_holes, binary_closing

R = Path(__file__).resolve().parent
G = R.parent / 'F103_REPAIR_DRAFT_AFTER_call01_SHORT_SLEEVE_REAL_PANTS_20261019'
SIZE = (1960, 1080)
for d in ['candidate', 'layers', 'masks', 'qa/protected_semantic_trial']:
    (R/d).mkdir(parents=True, exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(n):
    out=Image.new('RGBA',SIZE)
    out.alpha_composite(Image.open(G/'sources'/n).convert('RGBA'))
    return out
geo=json.loads((G/'geometry/F103_actual100_common24_and_whole_grip.json').read_text())
M=np.array(geo['delta_M']); t=np.array(geo['delta_t']); iv=M.T; it=-iv@t
def common24(im):
    return im.transform(SIZE,Image.Transform.AFFINE,(*iv[0],it[0],*iv[1],it[1]),Image.Resampling.BICUBIC,fillcolor=0)
head=common24(source('F100_original_head_neck.png'))
far=common24(source('F100_far_complete_arm_hand_jade.png'))
shoes=Image.new('RGBA',SIZE)
shoes.alpha_composite(source('F100_far_whole_shoe_FIXED.png'))
shoes.alpha_composite(source('F100_near_whole_shoe_FIXED.png'))
lamp=source('ORIGINAL_whole_lamp_and_shadow_FIXED.png')
raw=Image.open(R/'originals/F103_REPAIR_call02_NATIVE_RAW.png').convert('RGBA')
assert sha(R/'originals/F103_REPAIR_call02_NATIVE_RAW.png')=='e46fdeede06edaff502a1396559e499eeda189abdf17f01f2bd3882bf2bc595c'
assert raw.size==(1024,1536)
mapped=Image.new('RGBA',SIZE)
mapped.alpha_composite(raw.resize((720,1080),Image.Resampling.LANCZOS),(1240,0))
a=np.array(mapped); rgb=a[:,:,:3].astype(int); rr,gg,bb=rgb.transpose(2,0,1); active=a[:,:,3]>0
yy,xx=np.indices(active.shape)
def poly(points):
    z=Image.new('L',SIZE);ImageDraw.Draw(z).polygon(points,fill=255);return np.array(z)>0
def complete_component(mask,roi):
    labs,n=label(mask&roi)
    counts=np.bincount(labs.ravel());counts[0]=0
    assert counts.max()>100
    m=labs==counts.argmax()
    return binary_dilation(binary_fill_holes(m),iterations=2)&active
warm=(rr>150)&(rr>gg+16)&(gg>bb+8)&(bb>70)&(a[:,:,3]>16)
near=complete_component(warm,(xx>1550)&(xx<1790)&(yy>300)&(yy<470))
blue=(bb>rr+20)&(gg>rr+10)&(bb>gg+10)&(bb>90)&(a[:,:,3]>16)
shirt=complete_component(binary_closing(blue,iterations=2),(xx>1300)&(yy<760))
shirt=binary_dilation(shirt,iterations=3)&active
far_skin=binary_dilation(binary_fill_holes(warm&(xx>1450)&(xx<1690)&(yy>400)&(yy<640)&~near),iterations=4)&active&~shirt
headclear=poly([(1510,0),(1840,0),(1840,295),(1720,330),(1610,345),(1510,300)])&active&~shirt
propclear=poly([(1600,320),(1870,320),(1870,700),(1595,700),(1595,565),(1640,525),(1640,420),(1650,380),(1650,320)])&active&~near&~shirt
neutral=(rgb.max(2)-rgb.min(2)<14)&(yy>965)
feetclear=binary_dilation(binary_fill_holes((neutral|warm)&(xx>1330)&(xx<1600)&(yy>930)&(yy<1040)),iterations=2)&active
body=a.copy();body[headclear|far_skin|propclear|feetclear]=0
near_rgba=np.zeros_like(a);near_rgba[near]=a[near]
for name,m in [('RAW_complete_near_bare_arm_whole_grip',near),('RAW_complete_blue_blouse',shirt),('REMOVE_generated_head_neck',headclear),('REMOVE_generated_far_visible_skin',far_skin),('REMOVE_generated_lamp_except_whole_near_hand',propclear),('REMOVE_generated_feet_semantic',feetclear)]:
    Image.fromarray((m*255).astype('uint8')).save(R/'masks'/f'{name}.png')
for name,im in [('ORIGINAL24_head_neck',head),('ORIGINAL24_complete_far_arm_hand_jade',far),('ORIGINAL_whole_shoes_FIXED',shoes),('ORIGINAL_whole_lamp_FIXED',lamp),('NATIVE_complete_near_bare_arm_whole_grip',Image.fromarray(near_rgba)),('NATIVE_continuous_blouse_waist_pants',Image.fromarray(body))]:
    im.save(R/'layers'/f'{name}.png')
out=Image.new('RGBA',SIZE)
for im in [far,Image.fromarray(body),head,shoes,lamp,Image.fromarray(near_rgba)]:out.alpha_composite(im)
# Original source core must stay literal; near whole hand owns wire occlusion.
o=np.array(out)
for im,protect in [(head,np.array(head)[:,:,3]>0),(shoes,np.array(shoes)[:,:,3]>0),(lamp,(np.array(lamp)[:,:,3]>0)&~near)]:
    o[protect]=np.array(im)[protect]
out=Image.fromarray(o)
candidate=R/'candidate/F103_REPAIR_call02_PROTECTED_SEMANTIC_TRIAL_PENDING_ASTRA.png'
out.save(candidate)
q=R/'qa/protected_semantic_trial'
for tone,color in [('gray',(214,224,232,255)),('dark',(35,43,52,255))]:
    bg=Image.new('RGBA',SIZE,color);bg.alpha_composite(out)
    bg.crop((1300,0,1890,1080)).save(q/f'F103_protected_trial_full_{tone}.png')
    bg.crop((1520,285,1810,485)).resize((870,600)).save(q/f'F103_original_wire_whole_grip_depth_{tone}_3x.png')
    bg.crop((1380,190,1720,720)).resize((510,795)).save(q/f'F103_neck_sleeve_continuous_waist_{tone}.png')
    bg.crop((1330,900,1590,1040)).resize((780,420)).save(q/f'F103_original_whole_shoes_join_{tone}_3x.png')
checks={'state':'ACTUAL_PROTECTED_TRIAL_PENDING_ROOT_VISUAL_REVIEW_AND_ASTRA_GATE','candidate':str(candidate.relative_to(R)),'candidate_SHA256':sha(candidate),'raw_SHA256':sha(R/'originals/F103_REPAIR_call02_NATIVE_RAW.png'),'native_registration':'45/64+[1240,0], whole image once','source_group_delta_degrees':8,'source_total_degrees':24,'source_scale':1,'lamp_transform':'identity; original full physical lamp fixed','human_pixel_sources_only':True,'new_RGB_drawing_or_color_changes':False,'native_requests_this_script':0,'F106_calls':0,'protection_RGBA_changes':{}}
for name,im,m in [('head_neck',head,np.array(head)[:,:,3]>0),('complete_shoes',shoes,np.array(shoes)[:,:,3]>0),('fixed_lamp_except_real_hand_occlusion',lamp,(np.array(lamp)[:,:,3]>0)&~near)]:
    checks['protection_RGBA_changes'][name]=int(np.any(o[m]!=np.array(im)[m],axis=1).sum())
checks['near_complete_arm_hand_pixels']=int(near.sum())
(q/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False,indent=2))
