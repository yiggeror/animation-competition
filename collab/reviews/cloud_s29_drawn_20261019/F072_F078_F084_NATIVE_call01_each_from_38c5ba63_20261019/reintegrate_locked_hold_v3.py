"""Zero calls. Keep accepted066 static torso/pressure cells for072/078; native084 release.
Only an existing held pose is reused. No technical limb, random cloth or code figure.
"""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
# Reuse the archived v2 source's pure extraction/registration definitions only;
# never run its diagnostic composites or its main block. Both sources are retained.
defs=(R/'reintegrate_semantic_v2.py').read_text().split('native={f:extract(f)for f in [72,78,84]}')[0]
exec(compile(defs,str(R/'reintegrate_semantic_v2.py'),'exec'),globals())
N=B/'F054_F060_F066_NATIVE_call01_each_from_e5c66f8f_20261019/F066/reintegration'
lockedp=G/'LOCKED066_ACTUAL_REFERENCE_RGBA.png';locked=load(lockedp);oldcloth=load(G/'LOCKED066_SAME_SOURCE_CLOTH_RGBA.png');propsp=G/'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png';props=load(propsp)
oldnear=load(N/'EXACT_NATIVE_NEAR_FULL_BARE_ARM_FOREGROUND_RGBA.png');oldfar=load(N/'ONE_SIMILARITY_COMPLETE_FAR_SLEEVE_ARM_JADE_HAND_RGBA.png')
rgb=oldfar[:,:,:3].astype(float);skin=(rgb[:,:,0]>120)&(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,2]>90);jade=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
oldfm=component((skin|jade)&(oldfar[:,:,3]>128))&(oldfar[:,:,3]>0)
lr=locked[:,:,:3].astype(float);blue=(lr[:,:,1]>95)&(lr[:,:,2]>135)&(lr[:,:,2]>lr[:,:,0]+15)
navy=(lr[:,:,2]>lr[:,:,0]+8)&(lr[:,:,1]<120)&(X>=499)&(Y>=620)&(Y<820)
native={f:extract(f)for f in [72,78,84]}
far72,reg72=similarity(native[72]['far'],[548.,530.],[697.,724.],[548.,530.],[660.098467936869,710.61030076984])
far78,reg78=similarity(native[78]['far'],[554.,544.],[645.,755.],[548.,530.],[640.098467936869,745.61030076984])
near84,reg84=similarity(native[84]['near'],[174.,615.],[432.,949.],[174.,615.],[430.,959.])
panels=[];reports=[]
for f in [72,78,84]:
 d=R/f'F{f:03d}';q=d/'reintegration_v3_locked_hold';q.mkdir(exist_ok=True);clothp=d/'inputs/05_ONLY_SAME_SOURCE_CLOTH_RGBA.png';cloth=load(clothp);lip=load(G/f'F{f:03d}/SAME_MATERIAL_FRONT_FOLD_RGBA.png')
 # Flattened066 contains faint historical arm/cotton AA outside its separated
 # limb alpha. Remove the complete semantic field, not merely bright skin or
 # navy pixels, so old outlines and isolated blossoms cannot float behind it.
 farclear=poly([(502,560),(582,490),(645,535),(790,610),(795,735),(650,735),(575,650)])
 uppercloth=(X>=499)&(Y>=620)&(Y<820)
 base=locked.copy();remove=oldfm|farclear|uppercloth
 if f==84:remove|=oldnear[:,:,3]>0
 base[remove]=0;restoreblue=remove&blue&((X<535)|(Y<600));base[restoreblue]=locked[restoreblue]
 # Known original cuff skin underlay only: no jade/hand or old pose returns.
 dist=(X-548)*.535+(Y-530)*.845;cuff=np.zeros_like(locked);use=oldfm&(dist>=-4)&(dist<20);cuff[use]=locked[use]
 if f==84:
  base[(Y<435)&(X>195)&(X<700)]=0;body=native[84]['body_unprojected']
 else:body=np.zeros_like(locked)  # already accepted coherent066 held torso/head
 near=oldnear if f<84 else near84;far=far72 if f==72 else far78
 final=comp(base,body,cuff,cloth,props,lip,near,far)
 # Preserve the fixed native sleeve opening in front of its actual upper arm.
 sleeve=np.zeros_like(locked);src=locked if f<84 else body;sr=src[:,:,:3].astype(float);sblue=(sr[:,:,1]>95)&(sr[:,:,2]>135)&(sr[:,:,2]>sr[:,:,0]+15);dom=sblue&(src[:,:,3]>0)&(((X>475)&(Y>430)&(Y<600))|((X>75)&(X<250)&(Y>540)&(Y<650)));sleeve[dom]=src[dom];final=comp(final,sleeve)
 if f>=78:
  # The old static sleeve's shorter cuff cannot border the NEW naturally drawn
  # upper-arm silhouette. Restore the ENTIRE native078 cuff/proximal-arm joint
  # from the SAME single registered group, not a thin painted wedge or finger fix.
  M=np.array(reg78['matrix']);t=np.array(reg78['translation']);joint=affine(native[78]['human'],M,t)
  jointdomain=poly([(480,505),(555,450),(612,484),(626,532),(525,600),(480,565)])
  final[jointdomain]=joint[jointdomain];save((jointdomain*255).astype('uint8'),q/'COMPLETE_NATIVE078_CUFF_PROXIMAL_JOINT_DOMAIN.png');save(joint,q/'ONE_REGISTERED_NATIVE078_COMPLETE_HUMAN_JOINT_SOURCE_RGBA.png')
 if f==84:
  edge=np.zeros_like(cloth);domain=(near[:,:,3]>0)&(X>=414)&(X<=448)&(Y>=951)&(Y<=965)&(cloth[:,:,3]>0);edge[domain]=cloth[domain];final=comp(final,edge);save(edge,q/'SAME_SOURCE_FRONT_EDGE_ABOVE_INDEX_RGBA.png')
 final[Y>=1100]=locked[Y>=1100]
 save(near,q/'COMPLETE_NEAR_NATIVE_ARM_HAND_RGBA.png');save(far,q/'COMPLETE_FAR_NATIVE_ARM_JADE_HAND_RGBA.png');save(final,q/f'F{f:03d}_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_RGBA.png')
 bg=Image.new('RGBA',(1024,1536),(232,235,239,255));bg.alpha_composite(Image.fromarray(final));bg.convert('RGB').save(q/'FULL_ON_GRAY.png');bg.crop((70,275,810,1040)).convert('RGB').save(q/'COMPLETE_ARMS_COLLAR_HEM_CONTACTS_1TO1.png');bg.crop((250,760,450,910)).resize((600,450)).convert('RGB').save(q/'HEM_AND_PRESS_SUPPORT_3X.png');bg.crop((330,865,490,1000)).resize((640,540)).convert('RGB').save(q/'NEAR_REAL_FRONT_PINCH_4X.png');bg.crop((560,620,750,810)).resize((570,570)).convert('RGB').save(q/'FAR_REAL_CLOTH_PINCH_3X.png')
 bg.crop((480,440,640,615)).resize((640,700)).convert('RGB').save(q/'COMPLETE_FAR_CUFF_UPPERARM_JOINT_4X.png')
 r=dict(frame=f,status='PENDING_ACTUAL_V3_REVIEW_NOT_PRODUCTION_LOCK',generation_calls_state=1,additional_calls=0,existing066_static_head_blouse_near_pressure_cells_reused=f<84,old066_whole_pose_sent_to_image_tool=False,new_native_near_source=66 if f<84 else 84,new_native_far_source=72 if f==72 else 78,far078_084_exact_reuse=f>=78,near072_078_exact066_reuse=f<84,one_whole_far_group_registration=reg72 if f==72 else reg78,one_whole_near_group_registration=reg84 if f==84 else None,per_finger_transform=False,cloth_SHA256=sha(clothp),original_props_SHA256=sha(propsp),props_four_rods_geometry_changed=False,protected_legs_RGBA_changes=int(np.any(final[Y>=1100]!=locked[Y>=1100],1).sum()),output_SHA256=sha(q/f'F{f:03d}_SAME_SOURCE_CLOTH_TRUE_PROPS_NATIVE_RGBA.png'))
 (q/'SOURCE_CONTACT_AND_REUSE_CHECK.json').write_text(json.dumps(r,indent=2)+'\n');reports.append(r);panels.append(bg.convert('RGB'))
sheet=Image.new('RGB',(1536,800),(232,235,239));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(panels):sheet.paste(p.resize((512,768)),(i*512,32));dr.text((i*512+8,10),f'F{[72,78,84][i]:03d}: actual canonical-cloth composition, pending review',fill='black')
sheet.save(R/'THREE_V3_CANONICAL_CLOTH_NATIVE_REVIEW.png');(R/'V3_SOURCE_REUSE_REPORT.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps([dict(frame=r['frame'],sha=r['output_SHA256'])for r in reports],indent=2))
