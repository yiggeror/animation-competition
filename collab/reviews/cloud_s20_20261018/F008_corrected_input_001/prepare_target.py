"""Author an opaque reference target, NOT a generated/production character frame.
No image calls. Mother is used locally only for protected pixels and bounded crops.
"""
from pathlib import Path
import json,hashlib,base64,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import label
P=Path(__file__).resolve().parent;PACK=P.parent
MASTER=PACK/'F000/f000_scene_gate_001/cleanup/S20_F000_master_clean.png'
LOCK='55ce8658e3454dcb92e8408dda25bc678f856d82bbb10cd80ff06a01fa0ab0c8'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(MASTER)==LOCK
for n in ['inputs','art','local_masks','qa']:(P/n).mkdir(exist_ok=True)
A=np.array(Image.open(MASTER).convert('RGBA'));H,W=A.shape[:2]
frozen=json.loads((PACK/'handoff_008_020_032_reference_001/batch_geometry_and_requests.json').read_text())['frames'][0]['state']
assert frozen['R_palm']==[806,318] and frozen['L_palm']==[837,455]

# Preserve exactly the already approved actor-domain, then protect real four rods.
edit=Image.open(PACK/'handoff_008_020_032_reference_001/F008/04_edit_white.png').convert('L')
rod=Image.open(PACK/'F000/arm_correction_001/masks/protect_four_front_rods.png').convert('L')
e=np.array(edit);r=np.array(rod)>0;e[r]=0
Image.fromarray(e).save(P/'inputs/04_edit_white.png')
rod.save(P/'local_masks/protect_four_real_rods.png')

# Head only: face/cranium through y352 and separately masked lower ponytails.
# No old neckline, torso, sleeve or arm is included in this local crop.
hm=Image.new('L',(W,H));d=ImageDraw.Draw(hm)
d.rectangle((480,170,667,352),fill=255)
hair=np.zeros((H,W),bool)
for poly in [[(491,340),(554,340),(556,373),(547,402),(490,406)],
             [(611,338),(632,338),(636,373),(626,382),(610,363)]]:
 q=Image.new('L',(W,H));ImageDraw.Draw(q).polygon(poly,fill=255);hair|=np.array(q)>0
dark=(A[:,:,0]<145)&(A[:,:,1]<135)&(A[:,:,2]<125)
yy,xx=np.indices((H,W))
hair&=~((yy>373)&(xx>545)&(xx<580)) # exclude old collar ink beside the left ponytail
hm=np.array(hm)>0;hm|=hair&dark
head=np.zeros_like(A);head[hm]=A[hm]
cc,n=label(head[:,:,3]>0)
keep=np.unique(cc[:353]);keep=keep[keep!=0]
head[~np.isin(cc,keep)]=0 # discard disconnected old collar ink below the head cut
neck_skin=(head[:,:,0]>180)&(head[:,:,1]>125)&(head[:,:,2]>80)
for row in range(348,353):
 take=neck_skin[row]
 head[row,take,3]=np.rint(head[row,take,3]*(352-row)/4).astype('uint8')
Image.fromarray(head).save(P/'art/head_identity_only_local.png')
uri='data:image/png;base64,'+base64.b64encode((P/'art/head_identity_only_local.png').read_bytes()).decode()

INK='#684c3c';SKIN='#ffd0aa';SHADOW='#efba94';FAR='#f9c8a2';YELLOW='#f4c74d';YDARK='#dfaa38'
def path(d,fill,stroke=INK,sw=1.55,extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
def finger(a,b,c,base_radius=4,end_radius=2.9):
 a=np.array(a,float);b=np.array(b,float);c=np.array(c,float)
 u=(c-a)/np.linalg.norm(c-a);n=np.array([-u[1],u[0]])
 p=a+n*base_radius;q=c+n*end_radius;z=c-n*end_radius;t=a-n*base_radius
 mid=b+n*base_radius*.8;mid2=b-n*base_radius*.8
 curve=f'M{p[0]},{p[1]} Q{mid[0]},{mid[1]} {q[0]},{q[1]} Q{c[0]+u[0]*end_radius},{c[1]+u[1]*end_radius} {z[0]},{z[1]} Q{mid2[0]},{mid2[1]} {t[0]},{t[1]} Z'
 return path(curve,SKIN,sw=1.1)
def hand(wrist,palm,lower=False):
 # Actual five-digit outline: four separated tapered fingers + opposed thumb;
 # no circles, skeleton or grasp symbols in the model target.
 w=np.array(wrist,float);u=np.array(palm)-w;u=u/np.linalg.norm(u);v=np.array([-u[1],u[0]])
 m=f'matrix({u[0]} {u[1]} {v[0]} {v[1]} {w[0]} {w[1]})'
 jobs=[((31,-8),(45,-6),(58,-4)),((34,-1),(49,1),(64,4)),
       ((33,7),(47,10),(61,14)),((29,13),(41,18),(52,24))] if lower else [
       ((31,-8),(48,-13),(63,-17)),((34,-1),(53,-3),(68,-6)),
       ((33,7),(51,8),(65,8)),((29,13),(43,18),(56,22))]
 s=f'<g transform="{m}">'
 for i,(a,b,c) in enumerate(jobs):s+=finger(a,b,c,4.0 if i<3 else 3.5,2.8 if i<3 else 2.5)
 s+=path('M0 -7 C12 -13 25 -16 36 -11 C43 -5 40 13 28 16 L9 13 L0 7 Z',SKIN,sw=1.2)
 s+=path('M9 -6 Q11 -17 23 -29 Q26 -32 29 -29 Q33 -26 29 -22 L22 -10 Q19 -5 15 -2 Z',SKIN,sw=1.2)
 s+=path('M13 4 Q22 5 28 0 M19 -7 Q23 -5 25 -2','none','#dba786',.8)
 for a,b,c in jobs:s+=path(f'M{b[0]-1} {b[1]-1.7} l2.2 2.5','none','#dba786',.7)
 s+='</g>'
 return s

shirt='M591 386 Q618 377 639 390 Q660 399 671 424 L680 474 Q674 493 662 500 L572 502 Q565 473 573 435 Q570 411 591 386 Z'
skirt='M572 497 Q614 510 661 498 Q680 556 693 606 Q711 658 708 702 Q680 730 604 724 Q530 724 482 699 Q500 648 527 592 Q553 541 572 497 Z'
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><desc>Opaque manually authored construction target for the approved S20 F008; not a production drawing. No old child torso or low arms.</desc>'
svg+='<defs><pattern id="dots" width="35" height="31" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="3.5" fill="#fff9df"/><circle cx="27" cy="26" r="3.3" fill="#fff9df"/></pattern>'
svg+=f'<clipPath id="shirt"><path d="{shirt}"/></clipPath><clipPath id="skirt"><path d="{skirt}"/></clipPath></defs>'
# Complete near/far leg volumes under the new skirt; the original ankle pixels
# replace y805+ locally after rasterization, avoiding a source-shoe seam.
svg+=path('M545 708 Q546 735 546 752 Q537 785 539 815 L577 815 Q587 779 591 752 L591 715 Z',SKIN)
svg+=path('M596 711 L638 711 Q640 733 637 753 Q636 782 634 815 L598 815 Q593 779 595 753 Z',FAR)
svg+=path('M546 752 Q552 768 549 802 L539 805 Q537 785 546 752 Z',SHADOW,'none',0)
svg+=path('M596 753 Q607 773 607 805 L598 805 Q593 779 596 753 Z',SHADOW,'none',0)
svg+=path('M556 752 Q566 755 573 751 M607 753 Q617 756 625 753','none','#dca383',.9)
# Far L chain first: S(656,428)->E(719.0147,468.6712)->W(814,467).
svg+=path('M646 421 Q657 412 667 422 C684 435 705 445 725 455 C750 456 780 456 814 459 L817 475 C776 479 741 482 721 481 Q711 480 701 474 L646 440 Q638 431 646 421 Z',FAR)
svg+=path('M650 436 Q689 463 718 476 Q760 476 815 470 L817 475 C776 479 741 482 721 481 Q711 480 701 474 L646 440 Z',SHADOW,'none',0)
svg+=path('M711 466 Q719 472 727 467','none','#d89d7e',.9)
svg+=hand([814,467],[837,455],True)
svg+=path('M638 403 Q654 400 668 414 Q681 424 691 437 L677 458 Q658 451 647 438 Q636 424 638 403 Z',YELLOW)
svg+=path('M638 403 Q654 400 668 414 Q681 424 691 437 L677 458 Q658 451 647 438 Q636 424 638 403 Z','url(#dots)','none',0)
svg+=path('M688 437 Q679 445 677 458 M669 427 Q675 435 677 442','none',YDARK,1.2)
# Whole dress/rib cage/pelvis, not a ghost of the old body.
svg+=path(skirt,YELLOW)
svg+=f'<g clip-path="url(#skirt)">'+path('M572 501 Q548 575 511 692 L528 711 Q566 630 590 506 Z',YDARK,'none',0)+path('M640 505 Q667 600 685 711 L706 701 Q683 593 661 498 Z','#e9b53c','none',0)+path('M615 506 Q600 619 602 723','none','#f9d365',12)+f'<path d="{skirt}" fill="url(#dots)"/>'+'</g>'
svg+=path('M590 507 Q556 608 540 715 M615 509 Q597 621 585 723 M643 507 Q660 615 671 717','none','#b3892f',1.1)
svg+=path(shirt,YELLOW)
svg+=f'<g clip-path="url(#shirt)">'+path('M657 408 Q653 451 662 500 L680 474 Q675 430 657 408 Z','#e5b13a','none',0)+path('M582 433 Q574 466 580 497','none','#f9d467',8)+f'<path d="{shirt}" fill="url(#dots)"/>'+'</g>'
svg+=path('M574 496 Q617 508 661 498','none','#a77d2d',1.6)
svg+=path('M580 337 Q606 338 628 338 Q628 360 641 385 Q629 402 615 393 L588 378 Q575 372 581 350 Z',SKIN)
svg+=path('M582 341 Q588 359 607 367 L627 379 L617 388 L588 378 Q577 373 582 341 Z',SHADOW,'none',0)
# The identity head is a bounded source cut at the frozen +20,-3 offset. It has
# no old neck base/collar/body/arms and is not a full mother pose reference.
svg+=f'<image href="{uri}" x="20" y="-3" width="{W}" height="{H}"/>'
svg+=path('M588 375 Q600 384 617 389 L621 405 Q599 412 581 389 Z','#fff9e9',sw=1.2)
svg+=path('M623 382 L638 380 Q652 392 655 411 Q642 405 621 405 L617 389 Z','#fff9e9',sw=1.2)
# Near R continuous arm contour, preserving the approved S/E/W chain exactly.
svg+=path('M601 404 C620 391 652 368 675 356 C690 349 705 345 730 337 L780 322 L789 336 C759 349 724 365 696 375 Q688 379 681 377 C658 395 641 420 619 431 Q604 432 597 419 Z',SKIN)
svg+=path('M613 424 C642 409 664 386 686 371 Q730 360 787 332 L789 336 C759 349 724 365 696 375 Q688 379 681 377 C658 395 641 420 619 431 Z',SHADOW,'none',0)
svg+=path('M674 368 Q682 370 689 365','none','#d89d7e',.9)
svg+=hand([783,330],[806,318],False)
svg+=path('M591 396 Q590 385 608 386 Q627 383 640 387 Q650 391 654 399 L654 410 Q644 415 634 411 L620 425 Q609 435 597 429 Q583 420 591 396 Z',YELLOW)
svg+=path('M591 396 Q590 385 608 386 Q627 383 640 387 Q650 391 654 399 L654 410 Q644 415 634 411 L620 425 Q609 435 597 429 Q583 420 591 396 Z','url(#dots)','none',0)
svg+=path('M638 389 Q644 400 654 410 M599 394 Q608 401 608 413 M618 390 Q624 396 626 403','none',YDARK,1.1)
svg+='</svg>'
(P/'art/child_complete_new_pose.svg').write_text(svg)

# Bounded identity/material card. No full old child, old torso or arm crop.
card=Image.new('RGB',(900,600),'#eceff1');d=ImageDraw.Draw(card)
fontpath=PACK.parents[2]/'assets/fonts/NotoSansSC-VF.ttf'
font=ImageFont.truetype(str(fontpath),23)
d.text((22,14),'仅头部身份与内部材质 · 不含旧全身／旧手臂',font=font,fill='#263743')
headcrop=Image.fromarray(head).crop((480,170,670,353))
hbg=Image.new('RGBA',headcrop.size,'#d9dde0');hbg.alpha_composite(headcrop)
card.paste(hbg.convert('RGB').resize((380,366),Image.Resampling.NEAREST),(20,72))
patches=[('黄裙内布／点纹',(567,560,620,620)),('肤色内部／不含边缘',(550,766,570,797)),
         ('头发内部',(527,224,558,250)),('黄布明面',(597,625,635,671))]
for i,(label,box) in enumerate(patches):
 x=430+(i%2)*235;y=88+(i//2)*235
 d.text((x,y-28),label,font=ImageFont.truetype(str(fontpath),17),fill='#263743')
 patch=Image.fromarray(A).crop(box);pbg=Image.new('RGBA',patch.size,'#d9dde0');pbg.alpha_composite(patch)
 card.paste(pbg.convert('RGB').resize((185,180),Image.Resampling.NEAREST),(x,y))
card.save(P/'inputs/03_head_identity_internal_materials.png')
(P/'target_construction.json').write_text(json.dumps({'mother_sha256':LOCK,'frozen_008':frozen,
 'head_source_cut':'art/head_identity_only_local.png','head_offset_px':[20,-3],
 'old_child_torso_and_arms_reused':False,'ghost_body_in_target':False,'target_body_opaque':True,
 'source_ankle_lower_calf_reuse_y':[805,941],'four_rods_preserve_mask':'local_masks/protect_four_real_rods.png',
 'third_image_patches':[{'role':x,'source_box':list(b)} for x,b in patches],
 'image_model_calls':0,'character_drawings_accepted':0,'purpose':'Manual opaque INPUT target, never a finished/generated animation frame.'},ensure_ascii=False,indent=2)+'\n')
print('Prepared opaque new child SVG, bounded identity/material card and rod-protected white mask. No model calls.')
