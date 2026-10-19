"""F032 release-only target from accepted actual020; child is immutable.
No model call. Original holding palm is removed from the unique new target.
"""
from pathlib import Path
import json,hashlib,base64,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,binary_fill_holes
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F032';I=F/'inputs';ART=F/'art'
for p in [F,I,ART,F/'qa']:p.mkdir(exist_ok=True)
status=json.loads((P/'F020/status.json').read_text());assert status['state']=='AUTHOR_ACCEPTED'
SOURCE=P/'F020'/status['accepted_png'];A=np.array(Image.open(SOURCE).convert('RGBA'));H,W=A.shape[:2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(SOURCE)==status['accepted_sha256']
g=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][2]['state']
reg=json.loads((PACK/'F000/f000_scene_gate_001/registration_input.json').read_text())
M=np.array(Image.open(PACK/'handoff_008_020_032_reference_001/F032/04_edit_white.png'))>0
yy,xx=np.indices(M.shape);M&=xx>=885
rr,gg,bb=A[:,:,:3].astype(float).transpose(2,0,1)
blue=(bb>rr+9)&(bb>gg+4)&(rr<225)&(A[:,:,3]>180)
cloth=binary_fill_holes(blue)
clothAA=binary_dilation(cloth,iterations=1)&(A[:,:,3]>20)&(bb>rr-10)&(bb>gg-5)
M[cloth|clothAA]=False
# Exact existing holding-palm footprint and bare forearm occupancy, now released.
old=Image.open(PACK/'F000/arm_correction_001/masks/protect_R_palm.png').convert('L');d=ImageDraw.Draw(old)
d.polygon([(972,420),(1028,421),(1032,466),(974,469)],fill=255)
clear=binary_dilation(np.array(old)>0,iterations=2)&M
Image.fromarray((clear*255).astype('uint8')).save(ART/'old_R_palm_forearm_clear.png')
# Preserve actual visible bamboo; only the formerly palm-hidden tail area is new.
rod=np.array(Image.open(PACK/'F008_corrected_input_001/local_masks/protect_four_real_rods.png'))>0
visible_rod=rod&~clear&(A[:,:,3]>10);M[visible_rod]=False
Image.fromarray((M*255).astype('uint8')).save(I/'04_release_only_edit_white.png')
Image.fromarray((visible_rod*255).astype('uint8')).save(ART/'source_visible_rod_protection.png')
INK='#604b41';SKIN='#fbd0ad';SHADE='#eabe9f'
def path(d,fill,stroke=INK,sw=1.4):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
def pt(p):return f'{p[0]:.4f} {p[1]:.4f}'
S,E,V=[np.array(q,float) for q in g['G_R_chain']]
v1=(E-S)/np.linalg.norm(E-S);v2=(V-E)/np.linalg.norm(V-E);n1=np.array([-v1[1],v1[0]]);n2=np.array([-v2[1],v2[0]]);nb=n1+n2;nb/=np.linalg.norm(nb)
arm=f'M{pt(S-n1*24)} Q{pt((S+E)/2-n1*23)} {pt(E-n1*20)} Q{pt(E-nb*21)} {pt(E-n2*20)} Q{pt((E+V)/2-n2*17)} {pt(V-n2*13)} L{pt(V+n2*13)} Q{pt((E+V)/2+n2*17)} {pt(E+n2*20)} Q{pt(E+nb*20)} {pt(E+n1*20)} Q{pt((S+E)/2+n1*23)} {pt(S+n1*24)} Z'
def finger(a,b,c,r0=4.5,r1=3.2):
 a=np.array(a,float);b=np.array(b,float);c=np.array(c,float);u=(c-a)/np.linalg.norm(c-a);n=np.array([-u[1],u[0]])
 D=f'M{pt(a+n*r0)} Q{pt(b+n*r0*.8)} {pt(c+n*r1)} Q{pt(c+u*r1)} {pt(c-n*r1)} Q{pt(b-n*r0*.8)} {pt(a-n*r0)} Z'
 return path(D,SKIN,sw=1.0)
w=np.array([1012,480],float);palm=np.array([978,487],float);u=(palm-w)/np.linalg.norm(palm-w)
v=np.array([u[1],-u[0]]) # thumb remains upper side for the adult's visible R palm
sc=np.linalg.norm(palm-w)/26
mat=f'matrix({u[0]*sc} {u[1]*sc} {v[0]*sc} {v[1]*sc} {w[0]} {w[1]})'
hand=f'<g transform="{mat}">'
fingers=[((31,-8),(48,-11),(63,-13)),((34,-1),(53,-2),(68,-4)),((33,7),(51,6),(65,5)),((29,13),(43,15),(56,14))]
for a,b,c in fingers:hand+=finger(a,b,c)
hand+=path('M0 -10 C12 -16 25 -18 36 -11 C43 -5 40 13 28 16 L9 14 L0 10 Z',SKIN,sw=1.2)
hand+=path('M9 -6 Q11 -17 23 -29 Q26 -32 29 -29 Q33 -26 29 -22 L22 -10 Q19 -5 15 -2 Z',SKIN,sw=1.2)
hand+=path('M13 4 Q22 5 28 0 M19 -7 Q23 -5 25 -2','none','#d0a285',.8)
for a,b,c in fingers:hand+=path(f'M{b[0]-1} {b[1]-2} l2.4 2.8','none','#d0a285',.7)
hand+='</g>'
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><desc>F032 manual release target only; mother farR complete anatomy is occluded normally by the retained source torso. Child actual020 is never redrawn.</desc>'
svg+=path(arm,SKIN)+path(f'M{pt(E+nb*5)} q4 5 10 2','none','#d0a285',1.0)+hand+'</svg>'
(ART/'adult_R_release_volume.svg').write_text(svg)
# Source identity/material reference has no complete old holding gesture.
card=Image.new('RGB',(900,600),'#eceff1');dr=ImageDraw.Draw(card);fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(str(fontpath),22)
dr.text((18,14),'020已过实物：仅奶奶头部身份及内部布/肤/发材质',font=font,fill='#263743')
head=Image.fromarray(A).crop((997,38,1219,224));bg=Image.new('RGBA',head.size,'#d9dde0');bg.alpha_composite(head);card.paste(bg.convert('RGB').resize((400,335)),(18,78))
patches=[('蓝布内部',(1090,470,1122,508)),('肤肉内部',(1057,382,1081,396)),('灰发内部',(1081,71,1116,99)),('布面/白花',(1156,461,1183,497))]
for n,(title,box) in enumerate(patches):
 x=440+(n%2)*222;y=85+(n//2)*235;dr.text((x,y-25),title,font=ImageFont.truetype(str(fontpath),17),fill='#263743');im=Image.fromarray(A).crop(box);bg=Image.new('RGBA',im.size,'#d9dde0');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize((180,180)),(x,y))
card.save(I/'03_grandma_head_internal_materials_only.png')
(F/'source_and_geometry.json').write_text(json.dumps({'accepted_actual020':str(SOURCE),'accepted_actual020_sha256':sha(SOURCE),'G_R_release_chain':g['G_R_chain'],'G_R_open_palm':[978,487],
 'whole_child_and_receiver_grips_black_protected':True,'source_visible_rods_black_protected':True,'high_jade_L_whole_arm_black_protected':True,
 'hidden_turtle_tail_ends_master_px':{role:[944,reg['rods'][role]['slope']*944+reg['rods'][role]['intercept']] for role in ['T_H','T_S']},
 'new_model_calls':0,'target_only_not_animation_art':True},ensure_ascii=False,indent=2)+'\n')
print('F032 release-only complete volume SVG ready; accepted020 entire child and both grips locked. No model call.')
