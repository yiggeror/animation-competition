"""Three zero-call full-volume DRAWING TARGETS, never production drawings.

Human pixels are the locked real mother, temporarily articulated as a contact
probe. Complete native arms/cloth MUST be drawn after Astra's target gate.
Original props, rods, near support hand and lower-body registration are fixed.
"""
from pathlib import Path
import sys,json,math,hashlib
sys.path.insert(0,'/tmp/s29-image-tools')
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy import ndimage

R=Path(__file__).resolve().parent;P=R.parent/'REGISTER_REAL_PROPS_zero_call_v1_20261019'
for d in ['native_probes','targets','contacts','masks','geometry','prompts','qa']:(R/d).mkdir(exist_ok=True)
im=Image.open(P/'layers/REGISTERED_COMPLETE_MOTHER_ORIGINAL_PROPS.png').convert('RGBA');raw=np.array(im)
base=Image.open(P/'layers/MOTHER_CLOTH_BASE_NO_GENERATED_PROPS.png').convert('RGBA')
props=Image.open(P/'layers/REAL_ORIGINAL_TWO_PUPPETS_FOUR_RODS.png').convert('RGBA')
near=Image.open(P/'layers/ORIGINAL_NEAR_PALM_FOREGROUND.png').convert('RGBA')
oldlip=Image.open(P/'layers/ORIGINAL_RAISED_CLOTH_LIP.png').convert('RGBA')
W,H=im.size
def poly_mask(points):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
# Derive HUMAN masks from the prop-free native mother. A skin palette on the
# registered whole image would incorrectly classify tan leather as fingers.
rgb=np.array(base)[:,:,:3].astype('int16')
skin=(rgb[:,:,0]>185)&(rgb[:,:,0]>rgb[:,:,1]+16)&(rgb[:,:,1]>rgb[:,:,2]+9)
S=np.array([525.,465.]);E=np.array([641.,632.]);V=np.array([778.,680.]);C=np.array([845.,744.])
L1=float(np.linalg.norm(E-S));L2=float(np.linalg.norm(V-E))
upperpoly=[[513,439],[559,438],[595,476],[626,521],[647,562],[644,587],
           [669,610],[681,624],[667,655],[640,672],[606,646],[576,612],
           [548,577],[532,536],[522,487]]
forepoly=[[618,591],[655,600],[711,622],[767,643],[792,653],[799,681],
          [792,709],[766,717],[723,705],[677,693],[642,680],[615,659],[598,632]]
handpoly=[[768,637],[810,648],[849,670],[881,686],[899,705],[902,738],
          [891,773],[872,781],[851,756],[834,744],[821,719],[797,711],
          [775,716],[754,713],[741,695],[740,675],[751,650]]
upper=poly_mask(upperpoly)&(raw[:,:,3]>0)
fore=poly_mask(forepoly)&ndimage.binary_dilation(skin,iterations=2)
green=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.05)&(rgb[:,:,1]>65)
hand=poly_mask(handpoly)&ndimage.binary_dilation(skin|green,iterations=2)
yy0,xx0=np.indices((H,W))
def disk(p,r):return (xx0-p[0])**2+(yy0-p[1])**2<=r*r
# Overlapping true-pixel joint neighborhoods close the temporary pose probe;
# final anatomy still requires a coherent native redraw, not pasted segments.
upper |= (disk(S,54)&(xx0>493)&(raw[:,:,3]>0)) | (disk(E,44)&ndimage.binary_dilation(skin,iterations=2))
fore |= (disk(E,44)|disk(V,37))&ndimage.binary_dilation(skin,iterations=2)
hand |= disk(V,45)&ndimage.binary_dilation(skin|green,iterations=2)
# Erase the WHOLE original far-arm exterior, including its original ink edge.
# Do not leave a disconnected old elbow outline alongside the new target.
boundary=np.interp(yy0[:,0],[0,430,485,530,576,611,661,710,1535],
                   [520,510,519,529,540,549,540,540,540])[:,None]
old_exterior=(xx0>=boundary)&(yy0>=430)&(yy0<710)
old_hand_region=(xx0>733)&(xx0<923)&(yy0>=630)&(yy0<790)
erase=old_exterior | (old_hand_region&ndimage.binary_dilation(skin|green,iterations=3))
for name,m in [('SOURCE_FAR_UPPER_SHOULDER_SLEEVE',upper),('SOURCE_FAR_FOREARM',fore),('SOURCE_FAR_HAND_BANGLE_TOGETHER',hand)]:
 Image.fromarray(m.astype('uint8')*255).save(R/f'masks/{name}.png')

def segment(mask):
 a=np.zeros_like(raw);a[mask]=raw[mask];return Image.fromarray(a)
def rot(a):
 return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def place(image,source_pivot,target_pivot,theta):
 rr=rot(theta);tr=np.asarray(target_pivot)-rr@np.asarray(source_pivot)
 mat=np.c_[rr,tr].astype('float32')
 a=np.array(image).astype('float32');alpha=a[:,:,3:4]/255;a[:,:,:3]*=alpha
 b=cv2.warpAffine(a,mat,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
 b=np.clip(b,0,255);aa=b[:,:,3:4]/255
 b[:,:,:3]=np.divide(b[:,:,:3],aa,out=np.zeros_like(b[:,:,:3]),where=aa>1e-6)
 return Image.fromarray(np.clip(b,0,255).round().astype('uint8')),mat
def ik(wrist):
 d=wrist-S;dd=float(np.linalg.norm(d));u=d/dd
 aa=(L1*L1-L2*L2+dd*dd)/(2*dd);hh=math.sqrt(max(0,L1*L1-aa*aa))
 choices=[S+aa*u+sg*hh*np.array([-u[1],u[0]]) for sg in [1,-1]]
 # Keep the elbow below the shoulder and on the original lower branch.
 return max(choices,key=lambda p:p[1])
def cubic(a,b,c,d,n=40):
 t=np.linspace(0,1,n)[:,None];return ((1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d)).tolist()
def line(draw,pts,fill,width):draw.line([tuple(p) for p in pts],fill=fill,width=width,joint='curve')
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=lambda n:ImageFont.truetype(fontpath,n)

# Same material pinch point A for all three targets. The anchor is an area of
# supported cotton, not a stiff paper hinge. Lower cloth, two props and rods stay.
hinge_in=[874,874];hinge_out=[966,928]
states=[
 {'frame':24,'pinch':[827,700],'hand_deg':-8,'name':'LIFT HELD EDGE',
  'left_controls':[[888,740],[930,829]],
  'intent':'Lift the same cotton edge. Keep the support palm and both puppets still.'},
 {'frame':30,'pinch':[785,688],'hand_deg':-16,'name':'FOLD IN TOWARD PUPPET',
  'left_controls':[[898,734],[930,827]],
  'intent':'Carry the same pinched material point inward; cloth remains continuous.'},
 {'frame':36,'pinch':[742,718],'hand_deg':-4,'name':'FIRST NEW TAIL COVER',
  'left_controls':[[840,755],[930,827]],
  'intent':'The leading cotton fold first overlaps the visible outer feather area.'},
]
records=[]
prop_a=np.array(props);py,px=np.indices((H,W))
tailcore=(prop_a[:,:,0]<27)&(prop_a[:,:,1]<21)&(prop_a[:,:,2]<17)&(prop_a[:,:,3]>100)&(px>=800)&(py>=754)&(py<=820)
Image.fromarray(tailcore.astype('uint8')*255).save(R/'masks/CONSERVATIVE_ORIGINAL_BLACK_TAIL_CORE.png')
for st in states:
 f=st['frame'];A=np.array(st['pinch'],dtype=float);theta=math.radians(st['hand_deg'])
 wrist=A+rot(theta)@(V-C);elbow=ik(wrist)
 a1=math.atan2(*(elbow-S)[::-1])-math.atan2(*(E-S)[::-1])
 a2=math.atan2(*(wrist-elbow)[::-1])-math.atan2(*(V-E)[::-1])
 up,m1=place(segment(upper),S,S,a1);fo,m2=place(segment(fore),E,elbow,a2);ha,m3=place(segment(hand),C,A,theta)
 b=np.array(base);b[erase]=0
 # Cloth formerly hidden by the OLD hand has no native pixels. Reconstruct a
 # smooth supported edge there; do not leave the old fingers as white notches.
 support_edge=cubic([791,711],[841,749],[918,845],[989,915])
 support_mask=poly_mask([[553,709],[650,723],[741,709],[791,711]]+support_edge+[[947,1047],[898,1000],[822,1012],[750,1010],[638,955],[609,953],[521,1000],[311,917],[287,899],[457,746]])
 old_grip_area=(xx0>=710)&(xx0<926)&(yy0>=709)&(yy0<807)
 b[old_grip_area&~support_mask]=0
 missing=old_grip_area&support_mask&(b[:,:,3]==0)
 donor0=np.array(base)[832:875,554:668,:3]
 b[missing,:3]=donor0[yy0[missing]%donor0.shape[0],xx0[missing]%donor0.shape[1]];b[missing,3]=253
 target=Image.fromarray(b)
 target=Image.alpha_composite(target,up);target=Image.alpha_composite(target,fo)
 body_before_cloth=target.copy()
 # Existing near-side lip stays foreground; the far edge is the moving flap.
 lip=np.array(oldlip);lip[:,710:]=0
 left=cubic(A,*st['left_controls'],hinge_in)
 bottom=cubic(hinge_in,[895,900],[940,929],hinge_out)
 B=A+rot(theta)@np.array([28.,12.])
 right=cubic(hinge_out,np.array(st['left_controls'][1])+[70,35],np.array(st['left_controls'][0])+[45,10],B)
 gripedge=cubic(B,B+rot(theta)@[-8.,-2.],A+rot(theta)@[8.,-2.],A)
 outline=left+bottom+right+gripedge
 flapmask=Image.new('L',(W,H));ImageDraw.Draw(flapmask).polygon([tuple(p) for p in outline],fill=255)
 # Actual cloth pixels used as a volume/contact material probe only. The next
 # native drawing must redraw soft cotton and the complete far arm together.
 donor=np.array(base)[832:875,554:668,:3]
 yy,xx=np.indices((H,W));dy=yy%(2*donor.shape[0]);dx=xx%(2*donor.shape[1])
 dy=np.minimum(dy,2*donor.shape[0]-1-dy);dx=np.minimum(dx,2*donor.shape[1]-1-dx)
 tex=donor[dy,dx].astype('float32')
 shade=(.88+.11*np.cos((xx-A[0])*.026)+.04*np.sin((yy-A[1])*.021))[:,:,None]
 # The FULL opaque cotton face rises BEHIND the resting puppet/rod group.
 # Only its turning leading lip comes in FRONT at F036. This is one connected
 # folded sheet with two depth faces, not a narrow handle or an empty cloth hole.
 backleft=cubic(A,A+[8,42],np.array(hinge_in)+[-38,-45],hinge_in)
 backoutline=backleft+bottom+right+gripedge
 backmask=Image.new('L',(W,H));ImageDraw.Draw(backmask).polygon([tuple(p) for p in backoutline],fill=255)
 backrgba=np.dstack([np.clip(tex*shade*.9,0,255).astype('uint8'),np.array(backmask)])
 target=Image.alpha_composite(target,Image.fromarray(backrgba))
 target=Image.alpha_composite(target,props)
 target=Image.alpha_composite(target,Image.fromarray(lip))
 rgba=np.dstack([np.clip(tex*shade,0,255).astype('uint8'),np.array(flapmask)])
 flap=Image.fromarray(rgba)
 # Curved cotton folds, not a rigid triangle or grid.
 crease=Image.new('RGBA',(W,H));cd=ImageDraw.Draw(crease)
 line(cd,left,('#1c2f56'),4)
 fold=cubic(A,A+[50,60],[887,851],hinge_out)
 line(cd,fold,(14,24,49,100),7);crease=crease.filter(ImageFilter.GaussianBlur(2.2))
 crease.putalpha(Image.fromarray((np.array(crease.getchannel('A')).astype(float)*np.array(flapmask)/255).astype('uint8')))
 flap=Image.alpha_composite(flap,crease)
 if f<36:
  # Before the first cover the ENTIRE lifted sheet/lip is still behind the
  # resting originals, including fine antialiased feather tips, not just cores.
  target=Image.alpha_composite(body_before_cloth,Image.fromarray(backrgba))
  target=Image.alpha_composite(target,flap)
  target=Image.alpha_composite(target,props)
  target=Image.alpha_composite(target,Image.fromarray(lip))
 else:target=Image.alpha_composite(target,flap)
 target=Image.alpha_composite(target,near)
 target=Image.alpha_composite(target,ha)
 # The unchanged support palm is restored from the LOCKED registered source
 # exactly once, including its real ink and original alpha.
 na=np.array(target);near_mask=np.array(near.getchannel('A'))>0;na[near_mask]=raw[near_mask];target=Image.fromarray(na)
 native=R/f'native_probes/F{f:03d}_WHOLE_TARGET_REAL_PIXEL_PROBE_NOT_NEW_DRAWING.png';target.save(native)
 flapmask.save(R/f'masks/F{f:03d}_ACTUAL_MOVING_CLOTH_SURFACE.png')
 backmask.save(R/f'masks/F{f:03d}_FULL_CONTINUOUS_REAR_CLOTH_FACE.png')
 npalm=np.array(near.getchannel('A'))>0;haA=np.array(ha.getchannel('A'))>0
 moving=np.array(flapmask)>0
 record={**st,'status':'TECHNICAL_REAL_PIXEL_CONTACT_TARGET_ONLY_NOT_NEW_NATIVE_DRAWING',
  'source_shoulder_soft':S.tolist(),'source_elbow_soft':E.tolist(),'source_wrist_soft':V.tolist(),
  'target_shoulder_soft':S.tolist(),'target_elbow_soft':elbow.tolist(),'target_wrist_from_whole_hand':wrist.tolist(),
  'projected_upperarm_length':float(np.linalg.norm(elbow-S)),'projected_forearm_length':float(np.linalg.norm(wrist-elbow)),
  'soft_lengths_not_measured_3D_bones':True,'hidden_shoulder_pick_uncertainty_px':25,
  'material_pinch_UV_ID':'same original held lip A; no regrip','opposing_pad_cloth_edge_B':B.tolist(),'actual_cloth_mask_at_pinch':bool(moving[int(A[1]),int(A[0])]),
  'moving_cloth_over_near_palm_pixels':int(np.sum(moving&npalm)),
  'actual_original_black_tail_core_pixels_covered':int(np.sum(moving&tailcore)),
  'actual_original_black_tail_core_total':int(tailcore.sum()),
  'full_opaque_cloth_rear_face_connected_to_A_and_lap':bool(np.array(backmask)[int(A[1]),int(A[0])]>0),
  'fold_surface_depth':'full continuous rear cotton face -> original props/rods -> turning front lip -> original near palm / far pinch',
  'turning_lip_in_front_of_props_this_state':bool(f>=36),
  'all_original_tail_tips_remain_in_front_of_lifted_cloth_before_036':bool(f<36),
  'near_palm_exact_RGBA_from_locked_mother':bool(np.array_equal(np.array(target)[npalm],raw[npalm])),
  'moving_cloth_minX':int(np.where(moving)[1].min()),'near_palm_fixed':[536,750],
  'elbow_chain_branch':'same lower elbow branch, no segment scaling',
  'human_matrices_reference_only':{'upper':m1.tolist(),'forearm':m2.tolist(),'hand_and_bangle_together':m3.tolist()},
  'whole_cloth_anchor_area':[hinge_in,hinge_out],
  'original_props_rods_positions_unchanged':True,'no_new_native_calls':True,
  'guide_limit':'Temporary actual-pixel articulation may show elbow/sleeve seams. All three final native drawings must redraw the COMPLETE far shoulder/sleeve/elbow/wrist/hand and coherent soft cotton, never adopt this collage.'}
 records.append(record)
 # Complete figure + full arm chain. Technical label and limb traces make the
 # probe impossible to mistake for an imagegen original or accepted drawing.
 sheet=Image.new('RGB',(1360,1670),'#edf0f2');bg=Image.new('RGBA',(W,H),(237,240,242,255));bg.alpha_composite(target)
 sheet.paste(bg.convert('RGB'),(20,80));d=ImageDraw.Draw(sheet)
 d.text((24,14),f'S29 F{f:03d} - {st["name"]}',font=font(26),fill='#23364d')
 d.text((24,48),'TECHNICAL TARGET / REAL PIXEL PROBE / 0 NEW DRAWINGS',font=font(20),fill='#ad481e')
 def pt(p):return tuple(np.array(p)+[20,80])
 line(d,[pt(S),pt(elbow),pt(wrist),pt(A)],'#da853c',3)
 for label,p in [('S',S),('E',elbow),('W',wrist),('A',A)]:
  x,y=pt(p);d.ellipse((x-5,y-5,x+5,y+5),fill='#f69a45');d.text((x+7,y-14),label,font=font(20),fill='#8d461b')
 lines=[f'F{f:03d}: {st["name"]}','',f'A same cloth point',f'{st["pinch"]}',f'Hand + bangle {st["hand_deg"]} deg','',
        'WHOLE FAR ARM',f'Upper ~{L1:.1f}px',f'Forearm ~{L2:.1f}px','soft proxy, not 3D bones','',
        'NEAR RIGHT PALM','Bare wrist; fixed C1','[536,750] / neck3','',
        'BOTH REAL PUPPETS','4 original straight rods','Same lap placement','',
        'CONTINUOUS COTTON','A joins the held edge','Supported fold area','[874,874]-[966,928]','',
        'DEPTH:','far fingers','raised cotton fold','tail / original rods','lower cloth','both thighs','',
        'REDRAW NEXT:','complete far arm','natural pinch / fingers','soft opaque cotton','',
        'NO HANDOVER','NO PHONE POSES','NO NEW GENERATION']
 y=92
 for t in lines:d.text((1062,y),t,font=font(17),fill='#263f55');y+=30
 d.text((24,1626),'Guide only: redraw coherent native anatomy and cloth after Astra approval; do not adopt this articulated collage.',font=font(19),fill='#ad481e')
 sheet.save(R/f'targets/F{f:03d}_COMPLETE_NEW_VOLUME_TARGET_TECHNICAL.png')
 # Actual target crops: unchanged C1 and full far arm/pinch/cloth support area.
 contact=Image.new('RGB',(1540,1040),'#edf0f2');dc=ImageDraw.Draw(contact)
 dc.text((20,12),f'F{f:03d} ACTUAL TARGET CONTACTS - NOT A NEW DRAWING',font=font(25),fill='#ad481e')
 nearcrop=bg.crop((410,650,640,850)).resize((460,400));contact.paste(nearcrop.convert('RGB'),(20,80))
 farcrop=bg.crop((465,430,1000,960)).resize((963,954));contact.paste(farcrop.convert('RGB'),(550,70))
 dc.text((20,500),'C1 actual locked near palm',font=font(20),fill='#263f55')
 dc.text((20,532),'Original neck3 enters below fingers.',font=font(18),fill='#263f55')
 dc.text((20,580),f'A={st["pinch"]}; cloth mask meets A.',font=font(18),fill='#263f55')
 dc.text((20,612),f'Moving cloth over near palm: {record["moving_cloth_over_near_palm_pixels"]}px',font=font(17),fill='#263f55')
 dc.text((20,660),'Right: complete far shoulder-to-pinch',font=font(18),fill='#263f55')
 dc.text((20,692),'plus fold returning to lap support.',font=font(18),fill='#263f55')
 dc.text((20,760),'Temporary elbow/wrist seams are',font=font(18),fill='#ad481e')
 dc.text((20,792),'guides, never adopted human pixels.',font=font(18),fill='#ad481e')
 contact.save(R/f'contacts/F{f:03d}_COMPLETE_ARM_AND_TWO_CONTACTS_TARGET.png')

(R/'geometry/THREE_ACTUAL_TARGETS.json').write_text(json.dumps({'status':'FIRST_THREE_TARGETS_PREPARATION_ONLY_0_IMAGEGEN_CALLS',
 'locked_mother_commit':'545341eacd51a363c28da6d9ae7eada2c62c97a9','shot_seconds':12,'shot_frames':288,'fps':24,
 'locked_mother_hold_inclusive':[0,23],'cloth_sound_start_seconds':1.0,'phone_sound_seconds':5.5,
 'partial_exposures_only':[[24,29],[30,35],[36,None]],'F036_end_not_invented':True,
 'later_cover_requires_support_hand_release_first':True,'phone_look_later_independent_input':True,
 'targets':records},indent=2)+'\n')
print(json.dumps({'targets':[v['frame'] for v in records],'new_calls':0,'moving_cloth_near_palm_overlap':[v['moving_cloth_over_near_palm_pixels'] for v in records],
 'pinch_connected':[v['actual_cloth_mask_at_pinch'] for v in records]},indent=2))
