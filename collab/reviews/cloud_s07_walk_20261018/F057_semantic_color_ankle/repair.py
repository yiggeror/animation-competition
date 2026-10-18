#!/usr/bin/env python3
"""Authorized material-wise palette correction and old ankle-tail cleanup; zero generation."""
from pathlib import Path
import hashlib,json,datetime
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.ndimage import binary_closing,binary_fill_holes,binary_dilation

R=Path(__file__).resolve().parent;B=R.parent
for d in ['masks','candidate','qa','provenance']:(R/d).mkdir(exist_ok=True)
source=B/'F057_connection_call03/candidate/F057_call03_minimum_connections_PENDING.png'
mother=B/'F057_local_repair/sources/G037/production/F037_grandma_rgba.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)=='1b166dc6e0ba1367eec70544c80bd690abab643299c85e9a317d1e64c1ce7919'
assert sha(mother)=='4ebf2dc030fc8afd1cc53fb0269b31b0e4b7c4c416019ec47c3a045341ac4f8a'
im=Image.open(source).convert('RGBA');a=np.array(im);f=a[:,:,:3].astype(float);hsv=np.array(im.convert('RGB').convert('HSV')).astype(float)
y,x=np.indices(a.shape[:2]);lum=f@np.array([.2126,.7152,.0722]);active=a[:,:,3]>0
smooth=lambda z:np.clip(z,0,1)**2*(3-2*np.clip(z,0,1))
skin=(hsv[:,:,0]>=8)&(hsv[:,:,0]<=32)&(hsv[:,:,1]>=35)&(hsv[:,:,1]<=185)&(f[:,:,0]>170)&active
skin_weight=skin.astype(float)*smooth((hsv[:,:,1]-30)/15)*smooth((f[:,:,0]-170)/35)
head=(y<245)&(x>785)&(x<940)
near=(y>=340)&(y<625)&(x>=610)&(x<790)
far=(y>=350)&(y<625)&(x>=885)&(x<1000)
ear=np.exp(-(((x-812)/17)**4+((y-157)/24)**4))
neckmask=Image.new('L',im.size);ImageDraw.Draw(neckmask).polygon([(806,179),(839,189),(863,201),(851,239),(816,225),(805,202)],fill=255)
neck=np.array(neckmask.filter(ImageFilter.GaussianBlur(5))).astype(float)/255
ear*=1-neck
facew=skin_weight*head*(1-ear-neck)
earw=skin_weight*head*ear
neckw=skin_weight*head*neck
nearhand=smooth((y-524)/22)
farhand=smooth((y-514)/30)
weights={'face':facew,'ear':earw,'neck':neckw,
 'near_arm':skin_weight*near*(1-nearhand),'far_arm':skin_weight*far*(1-farhand),
 'near_hand':skin_weight*near*nearhand,'far_hand':skin_weight*far*farhand}
deltas={'face':[-10,-8,-9],'ear':[-8,-3,3],'neck':[-10,-19,-23],
 'near_arm':[-6,-12.5,-21.5],'far_arm':[-5,-8,-14],
 'near_hand':[-3,-8,-22],'far_hand':[-3,-8,-22]}
shirt=(y>=195)&(y<=556)&(x>=670)&(x<940)&active&(hsv[:,:,0]>=130)&(hsv[:,:,0]<=172)&(hsv[:,:,1]>=35)
weights['blue_blouse']=shirt.astype(float)*smooth((hsv[:,:,1]-30)/18)*smooth((lum-105)/35)
deltas['blue_blouse']=[18,0,-23]
pants=(y>=544)&(y<=968)&(x>=598)&(x<=888)&active&(hsv[:,:,0]>=130)&(hsv[:,:,0]<=180)&(hsv[:,:,1]>=30)&(f[:,:,2]<130)
weights['trousers']=pants.astype(float)*smooth((lum-27)/17)*smooth((hsv[:,:,1]-30)/18)
deltas['trousers']=[0,0,-6]
flower_core=(y>=195)&(y<=556)&(x>=670)&(x<940)&active&(f.min(axis=2)>190)&(hsv[:,:,1]<65)
flowers=binary_dilation(binary_fill_holes(binary_closing(flower_core,iterations=2)),iterations=1)
eye_core=head&(x>=870)&(y>=95)&(y<=160)&active&(hsv[:,:,1]<70)&(lum>215)
white_eye=binary_dilation(eye_core,iterations=1)
for name in weights:weights[name][flowers|white_eye]=0
delta=np.zeros_like(f)
for name,w in weights.items():
    delta+=w[:,:,None]*np.array(deltas[name])[None,None,:]
    Image.fromarray(np.rint(w*255).astype(np.uint8)).save(R/f'masks/{name}_weight.png')
out=a.copy();out[:,:,:3]=np.rint(np.clip(f+delta,0,255)).astype(np.uint8)

# Review the whole cuff→ankle→shoe opening. Clear only the old diagonal tail
# outside the real heel, tapering to its junction; do not erase the main hem.
tail=Image.new('L',im.size);ImageDraw.Draw(tail).polygon([(775,969),(782,968),(788,967),(791,967),(790,969),(788,970),(787,972),(784,974),(775,974)],fill=255)
tailarr=np.array(tail)>0
tailarr &= (a[:,:,3]>0)
tailarr &= (y>=967)&(y<=974)&(x>=775)&(x<=791)
out[tailarr]=0
Image.fromarray(tailarr.astype(np.uint8)*255).save(R/'masks/old_ankle_tail_removed.png')
candidate=R/'candidate/F057_semantic_color_and_ankle_PENDING.png';Image.fromarray(out).save(candidate)

# Immutable geometry/neutral-material checks. Skin and material RGB may change;
# alpha/position change only in the explicitly removed obsolete tail.
changed=np.any(out!=a,axis=2);alpha_changed=out[:,:,3]!=a[:,:,3]
assert np.array_equal(alpha_changed,tailarr)
assert np.array_equal(out[:,:,3][~tailarr],a[:,:,3][~tailarr])
neutral=(hsv[:,:,1]<=30)&active
ink=(lum<=27)&active
hair=(y<216)&(x>=700)&(x<928)&(hsv[:,:,1]<35)&active
jade=(x>=900)&(x<971)&(y>=490)&(y<543)&(hsv[:,:,0]>=45)&(hsv[:,:,0]<130)&active
feet=(y>=985)&active
ankle_skin=(y>=930)&skin
for n,m in [('neutral_white_gray',neutral),('complete_white_flowers',flowers),('white_eye_frames',white_eye),('dark_ink',ink),('gray_hair',hair),('jade',jade),('feet_and_soles',feet),('ankle_skin',ankle_skin)]:
    assert not changed[m&~tailarr].any(),n
    Image.fromarray(m.astype(np.uint8)*255).save(R/f'masks/protected_{n}.png')
reg=json.loads((B/'F057_connection_call03/preparation_checks.json').read_text())['registration_unchanged']
inv=(1/reg['s'],0,-reg['tx']/reg['s'],0,1/reg['s'],-reg['ty']/reg['s'])
world=Image.fromarray(out).transform((1672,941),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC)
world.save(R/'candidate/F057_semantic_color_and_ankle_world_PENDING.png')
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
for name,bgc in [('gray',(105,112,121,255)),('dark',(32,40,48,255))]:
    sheet=Image.new('RGB',(1500,1070),(242,244,247));dr=ImageDraw.Draw(sheet)
    for col,(title,z) in enumerate([('修前：6a6e269同原图',a),('分区颜色／旧踝尾清理',out)]):
        bg=Image.new('RGBA',im.size,bgc);bg.alpha_composite(Image.fromarray(z));cropped=bg.crop((570,0,1010,1050)).resize((440,1050),Image.Resampling.LANCZOS)
        sheet.paste(cropped.convert('RGB'),(col*470+10,20));dr.text((col*470+12,0),title,font=font,fill='#223344')
        for k,box in enumerate([(790,55,933,242),(630,355,786,617),(891,362,985,612),(755,936,885,982)]):
            q=bg.crop(box);q.thumbnail((260,240),Image.Resampling.LANCZOS);factor=min(260/q.width,240/q.height);q=q.resize((int(q.width*factor),int(q.height*factor)),Image.Resampling.LANCZOS)
            if col==1:sheet.paste(q.convert('RGB'),(970,k*255+25))
    sheet.save(R/f'qa/full_body_and_materials_{name}.png')
ankles=Image.new('RGB',(1500,560),(242,244,247));dr=ImageDraw.Draw(ankles)
for col,z in enumerate([a,out]):
    bg=Image.new('RGBA',im.size,(105,112,121,255));bg.alpha_composite(Image.fromarray(z));q=bg.crop((755,936,890,986)).resize((675,250),Image.Resampling.NEAREST);ankles.paste(q.convert('RGB'),(col*750+10,45));dr.text((col*750+10,10),'原图' if col==0 else '零调用清尾至汇合／主裤边与鞋口保留',font=font,fill='#223344')
    q=bg.crop((774,961,805,980)).resize((310,190),Image.Resampling.NEAREST);ankles.paste(q.convert('RGB'),(col*750+150,340))
ankles.save(R/'qa/whole_ankle_before_after.png')

summary=[]
for name,w in weights.items():
    q=(w>.8)&(a[:,:,3]>200)
    if q.any():summary.append({'part':name,'fully_weighted_pixels':int(q.sum()),'delta_RGB':deltas[name],
        'before_median_RGB':np.median(a[q,:3],axis=0).tolist(),'after_median_RGB':np.median(out[q,:3],axis=0).tolist()})
report={'status':'SEMANTIC_COLOR_AND_OLD_ANKLE_TAIL_PENDING_ACTUAL_REVIEW','source_commit':'6a6e2699c262b9d3b42f61a499a7c42ddc856191','source_sha256':sha(source),'G037_sha256':sha(mother),
 'authorization':'Astra explicit per-material correction and old ankle-tail cleanup; no whole-person redraw',
 'new_native_calls':0,'S07_native_calls_total':3,'in_flight':False,
 'native_size':list(im.size),'registration_unchanged':reg,'part_colors':summary,
 'ear_neck_sampling':'G037 actual unpremultiplied ear median243/195/157 and neckfill243/184/142 from corresponding skin-only patches, alpha>180; face/arm/hand corrections follow Astra measured ranges. Different anatomy/lighting limits exact per-pixel matching.',
 'RGB_changed_pixels':int(np.any(out[:,:,:3]!=a[:,:,:3],axis=2).sum()),'alpha_changed_pixels':int(alpha_changed.sum()),
 'alpha_changes_outside_old_tail':0,'old_tail_bbox':[775,967,792,975],
 'old_tail_removed_pixels':int(tailarr.sum()),'old_tail_alpha128_pixels':int((tailarr&(a[:,:,3]>128)).sum()),
 'protected_white_gray_ink_hair_jade_feet_ankle_skin_changes':0,'geometry_or_articulation_changes':0,
 'candidate_sha256':sha(candidate),'body_palette_limit':'Separate smooth skin parts and colored fabric only; neutral white/gray, dark ink, hair, jade and alpha frozen. No one RGB delta applied to whole image.'}
(R/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(R/'provenance/source_and_authority.json').write_text(json.dumps({'source_path':str(source.relative_to(B)),'source_commit':report['source_commit'],'source_sha256':sha(source),'G037_path':str(mother.relative_to(B)),'G037_sha256':sha(mother),'scope':report['authorization'],'native_calls':0},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
