"""Derive the authorized F020 opaque target from accepted actual F008.
Only source head/material/feet/protected grandma pixels are reused; old pose is
never submitted as another full-body model reference. No image model call here.
"""
from pathlib import Path
import json,hashlib,base64,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F020';I=F/'inputs';ART=F/'art'
for x in [F,I,ART,F/'qa']:x.mkdir(exist_ok=True)
s=json.loads((P/'F008/status.json').read_text());assert s['state']=='AUTHOR_ACCEPTED'
SOURCE=P/'F008'/s['accepted_png'];A=np.array(Image.open(SOURCE).convert('RGBA'));H,W=A.shape[:2]
g=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][1]['state']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==s['accepted_sha256']
headmask=Image.new('L',(W,H));d=ImageDraw.Draw(headmask)
d.rectangle((495,165,692,349),fill=255)
# Only hair/neck-free identity components below the jaw, never a source sleeve.
for poly in [[(510,335),(572,335),(573,375),(566,406),(506,406)],[(634,334),(655,336),(660,375),(648,389),(631,365)]]:
 z=Image.new('L',(W,H));ImageDraw.Draw(z).polygon(poly,fill=255)
 dark=(A[:,:,0]<145)&(A[:,:,1]<135)&(A[:,:,2]<125)
 arr=np.array(headmask);arr[(np.array(z)>0)&dark]=255;headmask=Image.fromarray(arr)
hm=np.array(headmask)>0;head=np.zeros_like(A);head[hm]=A[hm]
cc,n=label(head[:,:,3]>0);keep=np.unique(cc[:350]);keep=keep[keep!=0];head[~np.isin(cc,keep)]=0
skin=(head[:,:,0]>180)&(head[:,:,1]>125)&(head[:,:,2]>80)
for y in range(345,350):head[y,skin[y],3]=np.rint(head[y,skin[y],3]*(349-y)/4).astype('uint8')
Image.fromarray(head).save(ART/'accepted008_head_identity_only.png')
uri='data:image/png;base64,'+base64.b64encode((ART/'accepted008_head_identity_only.png').read_bytes()).decode()
INK='#684c3c';SKIN='#ffd0aa';SHADOW='#efba94';FAR='#f9c8a2';YELLOW='#f4c74d';YDARK='#dfaa38'
def path(d,fill,stroke=INK,sw=1.45):return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'
def point(p):return f'{p[0]:.4f} {p[1]:.4f}'
def full_arm(chain,fill):
 S,E,W=map(lambda p:np.array(p,float),chain)
 v1=(E-S)/np.linalg.norm(E-S);v2=(W-E)/np.linalg.norm(W-E)
 n1=np.array([-v1[1],v1[0]]);n2=np.array([-v2[1],v2[0]]);nb=n1+n2;nb/=np.linalg.norm(nb)
 a=S-n1*15;b=E-n1*12;c=E-n2*12;d=W-n2*7;e=W+n2*7;f=E+n2*12;h=E+n1*12;j=S+n1*15
 up=(S+E)/2-n1*17;fp=(E+W)/2-n2*10;fb=(E+W)/2+n2*10;ub=(S+E)/2+n1*16
 D=f'M{point(a)} Q{point(up)} {point(b)} Q{point(E-nb*13)} {point(c)} Q{point(fp)} {point(d)} L{point(e)} Q{point(fb)} {point(f)} Q{point(E+nb*12)} {point(h)} Q{point(ub)} {point(j)} Z'
 return path(D,fill)+path(f'M{point(E+nb*5)} q 4 2 9 -1','none','#d69e7e',.9)
def closed_hand(wrist,palm):
 w=np.array(wrist,float);u=np.array(palm)-w;u/=np.linalg.norm(u);v=np.array([-u[1],u[0]])
 transform=f'matrix({u[0]} {u[1]} {v[0]} {v[1]} {w[0]} {w[1]})'
 z=f'<g transform="{transform}">'
 z+=path('M0 -7 C8 -15 24 -21 38 -14 Q50 -10 46 4 Q45 16 34 20 L17 17 Q6 12 0 7 Z',SKIN,sw=1.2)
 for D in ['M27 -17 Q39 -20 44 -15 Q48 -11 43 -7 L31 -5 Q24 -8 27 -17 Z',
           'M29 -9 Q42 -11 47 -6 Q50 -2 44 2 L32 3 Q26 0 29 -9 Z',
           'M30 0 Q43 -1 46 4 Q47 9 40 11 L31 10 Q26 7 30 0 Z',
           'M29 8 Q40 8 42 13 Q43 17 37 20 L28 17 Q24 14 29 8 Z']:
  z+=path(D,SKIN,sw=1.0)
 z+=path('M8 -7 C12 -24 30 -23 34 -13 Q38 -9 34 -3 L24 4 Q16 12 10 5 Z',SKIN,sw=1.25)
 z+=path('M15 -8 Q21 -13 27 -9 M22 0 Q26 2 30 -1','none','#d69e7e',.8)
 return z+'</g>'
header=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
hands=closed_hand(g['R_chain'][2],g['R_palm'])+closed_hand(g['L_chain'][2],g['L_palm'])
(ART/'closed_hand_coverage.svg').write_text(header+hands+'</svg>')
shirt='M611 382 Q638 373 659 386 Q680 399 691 424 L700 474 Q694 493 682 500 L582 502 Q575 473 593 435 Q590 411 611 382 Z'
skirt='M582 497 Q624 510 681 498 Q693 556 701 606 Q716 658 713 702 Q690 730 614 724 Q540 724 492 699 Q510 648 537 592 Q563 541 582 497 Z'
svg=header+'<desc>Opaque F020 construction derived from accepted actual F008; only authorized shared-load key, not production art.</desc>'
svg+='<defs><pattern id="dots" width="35" height="31" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="3.5" fill="#fff9df"/><circle cx="27" cy="26" r="3.3" fill="#fff9df"/></pattern>'
svg+=f'<clipPath id="shirt"><path d="{shirt}"/></clipPath><clipPath id="skirt"><path d="{skirt}"/></clipPath></defs>'
svg+=path('M550 708 Q550 735 550 752 Q539 785 539 815 L577 815 Q589 779 595 752 L596 715 Z',SKIN)
svg+=path('M599 711 L641 711 Q642 733 640 753 Q636 782 634 815 L598 815 Q595 779 598 753 Z',FAR)
svg+=full_arm(g['L_chain'],FAR)+closed_hand(g['L_chain'][2],g['L_palm'])
svg+=path('M658 404 Q674 403 688 417 Q700 427 711 441 L696 461 Q678 455 667 441 Q656 425 658 404 Z',YELLOW)
svg+=path('M658 404 Q674 403 688 417 Q700 427 711 441 L696 461 Q678 455 667 441 Q656 425 658 404 Z','url(#dots)','none',0)
svg+=path(skirt,YELLOW)
svg+=f'<g clip-path="url(#skirt)">'+path('M582 501 Q558 575 521 692 L538 711 Q576 630 600 506 Z',YDARK,'none',0)+path('M660 505 Q681 600 697 711 L711 701 Q699 593 681 498 Z','#e9b53c','none',0)+f'<path d="{skirt}" fill="url(#dots)"/>'+'</g>'
svg+=path('M600 507 Q566 608 550 715 M625 509 Q607 621 595 723 M663 507 Q674 615 686 717','none','#b3892f',1.1)
svg+=path(shirt,YELLOW)+f'<g clip-path="url(#shirt)">'+path('M677 408 Q673 451 682 500 L700 474 Q695 430 677 408 Z','#e5b13a','none',0)+f'<path d="{shirt}" fill="url(#dots)"/>'+'</g>'
svg+=path('M584 496 Q637 508 681 498','none','#a77d2d',1.6)
svg+=path('M600 333 Q626 334 648 334 Q648 356 661 381 Q649 398 635 389 L608 374 Q595 368 601 346 Z',SKIN)
svg+=f'<image href="{uri}" x="20" y="-4" width="{W}" height="{H}"/>'
svg+=path('M608 371 Q620 380 637 385 L641 401 Q619 408 601 385 Z','#fff9e9',sw=1.2)
svg+=path('M643 378 L658 376 Q672 388 675 407 Q662 401 641 401 L637 385 Z','#fff9e9',sw=1.2)
svg+=full_arm(g['R_chain'],SKIN)+closed_hand(g['R_chain'][2],g['R_palm'])
svg+=path('M611 388 Q610 377 628 378 Q647 375 660 379 Q670 383 674 391 L674 402 Q664 407 654 403 L640 417 Q629 427 617 421 Q603 412 611 388 Z',YELLOW)
svg+=path('M611 388 Q610 377 628 378 Q647 375 660 379 Q670 383 674 391 L674 402 Q664 407 654 403 L640 417 Q629 427 617 421 Q603 412 611 388 Z','url(#dots)','none',0)
svg+=path('M658 381 Q664 392 674 402 M619 386 Q628 393 628 405','none',YDARK,1.1)
svg+='</svg>'
(ART/'child_F020_complete_pose.svg').write_text(svg)
# A crop-only identity/material card from the accepted real predecessor.
card=Image.new('RGB',(900,600),'#eceff1');dr=ImageDraw.Draw(card);fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf';font=ImageFont.truetype(str(fontpath),22)
dr.text((18,14),'已过008实物：仅头部身份与内部材质，无完整旧臂/全身',font=font,fill='#263743')
h=Image.fromarray(head).crop((497,165,693,349));bg=Image.new('RGBA',h.size,'#d9dde0');bg.alpha_composite(h);card.paste(bg.convert('RGB').resize((392,368)),(18,75))
patches=[('衣布/点纹',(600,545,650,602)),('肤肉内部',(750,455,773,470)),('头发内部',(545,225,573,252)),('黄布中面',(625,625,657,672))]
for n,(title,box) in enumerate(patches):
 x=435+(n%2)*225;y=85+(n//2)*235;dr.text((x,y-25),title,font=ImageFont.truetype(str(fontpath),17),fill='#263743');im=Image.fromarray(A).crop(box);bg=Image.new('RGBA',im.size,'#d9dde0');bg.alpha_composite(im);card.paste(bg.convert('RGB').resize((180,180)),(x,y))
card.save(I/'03_accepted008_head_materials_only.png')
(F/'source_and_geometry.json').write_text(json.dumps({'source_actual_F008':str(SOURCE),'source_actual_sha256':sha(SOURCE),'frozen_F020_geometry':g,'head_delta_from_008':[20,-4],'full_old_mother_or_full_old_pose_as_model_reference':False,'new_model_calls':0,'purpose':'authorized F020 single-state target; actual F008 accepted predecessor'},ensure_ascii=False,indent=2)+'\n')
print('F020 opaque shared-load target SVG and crop-only actual008 identity/materials prepared; no model call.')
