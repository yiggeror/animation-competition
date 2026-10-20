"""Zero new generation. Coherent native head/blouse, stationary pressure/hold groups.
All cotton/puppet pixels come from the approved canonical layers, never generated props.
"""
from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage as nd
import numpy as np,json,hashlib
R=Path(__file__).resolve().parent;B=R.parent;G=B/'F072_F078_F084_FROM_LOCKED066_INPUT_GATE_ZERO_CALL_20261019';Y,X=np.indices((1536,1024))
def load(p):return np.array(Image.open(p).convert('RGBA'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def poly(pts):
 a=Image.new('L',(1024,1536));ImageDraw.Draw(a).polygon(pts,fill=255);return np.array(a)>0
def save(a,p):Image.fromarray(a).save(p)
def comp(*aa):
 a=Image.new('RGBA',(1024,1536))
 for b in aa:a.alpha_composite(Image.fromarray(b))
 return np.array(a)
def sample(a,co):
 p=a.astype(float);p[:,:,:3]*=p[:,:,3:4]/255
 z=np.stack([nd.map_coordinates(p[:,:,k],[co[:,:,1],co[:,:,0]],order=1,mode='constant',cval=0)for k in range(4)],2)
 z[:,:,:3]=np.divide(z[:,:,:3],z[:,:,3:4]/255,out=np.zeros_like(z[:,:,:3]),where=z[:,:,3:4]>1e-8);z=np.rint(np.clip(z,0,255)).astype('uint8');z[z[:,:,3]==0]=0;return z
def affine(a,A,t):return sample(a,(np.stack([X,Y],2)-t)@np.linalg.inv(A).T)
def similarity(a,root0,point0,root1,point1):
 v=np.array(point0)-root0;w=np.array(point1)-root1;u=float(w@v/(v@v));r=float((w[1]*v[0]-w[0]*v[1])/(v@v));M=np.array([[u,-r],[r,u]]);t=np.array(root1)-M@root0
 return affine(a,M,t),dict(source_root=list(root0),source_contact=list(point0),target_root=list(root1),target_contact=list(point1),matrix=M.tolist(),translation=t.tolist(),scale=float(np.hypot(u,r)),rotation_degrees=float(np.degrees(np.arctan2(r,u))),whole_group=True,per_finger_transform=False)
def component(seed,pt=None):
 lab,_=nd.label(nd.binary_closing(seed,iterations=3))
 if pt is not None:k=int(lab[pt[1],pt[0]])
 else:
  counts=np.bincount(lab.ravel());counts[0]=0;k=int(counts.argmax())
 assert k>0
 return nd.binary_dilation(nd.binary_fill_holes(lab==k),iterations=2)
def extract(f):
 raw=load(R/f'F{f:03d}/originals/S29_F{f:03d}_call01_RAW_UNTOUCHED.png');rgb=raw[:,:,:3].astype(float)
 shirt=(rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15);skin=(rgb[:,:,0]>120)&(rgb[:,:,1]>65)&(rgb[:,:,2]>90)&(rgb[:,:,0]>rgb[:,:,2]+25);jade=(rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(rgb[:,:,1]>50)
 m=component((shirt|skin|jade)&(raw[:,:,3]>128)&(Y>=300)&(Y<1020)&(X>=40)&(X<810),(350,500))&(raw[:,:,3]>0)
 human=np.zeros_like(raw);human[m]=raw[m];human[m&(raw[:,:,3]>=128),3]=255
 fp=poly([(490,480),(660,460),(810,600),(810,820),(600,820),(490,735),(480,600)])
 fm=component((skin|jade)&m&fp)&m&fp
 nm=component(skin&m&~fm&(Y>570)&(Y<1010)&(X<610),(180,650))&m&~fm
 far=np.zeros_like(raw);far[fm]=human[fm];near=np.zeros_like(raw);near[nm]=human[nm]
 bp=poly([(287,275),(485,349),(545,405),(620,540),(500,590),(492,632),(530,725),(525,750),(438,780),(321,825),(206,938),(40,938),(75,760),(112,696),(128,640),(75,615),(70,585),(90,520),(130,450),(180,365),(240,317)])
 bm=m&bp&~(fm|nm);body=np.zeros_like(raw);body[bm]=human[bm]
 # Restore complete native head and neck from THIS raw, rather than imposing an
 # old-head/collar cut across the new naturally drawn garment root.
 hm=component((raw[:,:,3]>128)&(Y<435)&(X>195)&(X<700),(450,220))&(raw[:,:,3]>0)&(Y<435)&(X>195)&(X<700)
 head=np.zeros_like(raw);head[hm]=raw[hm];head[hm&(raw[:,:,3]>=128),3]=255
 # Same native cloth surface projection extends only the lower blouse hem into
 # the canonical lap support. No joints, hand pixels or new flower material.
 wx=np.maximum(0,1-((X-350)/220)**2)**2;sy=Y.astype(float)
 for _ in range(15):
  w=np.clip((sy-710)/70,0,1);w=w*w*(3-2*w);fade=np.clip((940-sy)/90,0,1);fade=fade*fade*(3-2*fade);sy=Y-27*wx*w*fade
 projected=sample(body,np.stack([X,sy],2));body=comp(projected,head)
 return dict(raw=raw,human=human,near=near,far=far,body=body,body_unprojected=comp(np.where(bm[:,:,None],human,0).astype('uint8'),head),shirt=shirt,m=m,head=head)
native={f:extract(f)for f in [72,78,84]}
propsp=G/'UNCHANGED_TRUE_TWO_PUPPETS_FOUR_RODS_RGBA.png';props=load(propsp)
body72=native[72]['body'];near72=native[72]['near']
far72,map72=similarity(native[72]['far'],[548.,530.],[697.,724.],[548.,530.],[660.098467936869,710.61030076984])
far78,map78=similarity(native[78]['far'],[554.,544.],[645.,755.],[548.,530.],[640.098467936869,745.61030076984])
near84,map84=similarity(native[84]['near'],[174.,615.],[432.,949.],[174.,615.],[430.,959.])
reports=[];panels=[]
for f in [72,78,84]:
 d=R/f'F{f:03d}';q=d/'reintegration_v2_semantic';q.mkdir(exist_ok=True);target=load(d/'inputs/01_UNIQUE_COMPLETE_CURRENT_TARGET_RGBA.png');clothp=d/'inputs/05_ONLY_SAME_SOURCE_CLOTH_RGBA.png';cloth=load(clothp);lip=load(G/f'F{f:03d}/SAME_MATERIAL_FRONT_FOLD_RGBA.png')
 body=body72 if f<84 else native[84]['body'];near=near72 if f<84 else near84;far=far72 if f==72 else far78
 # Clear technical/current human semantics while retaining the existing legs/
 # stool. The entire native head/body enters as one coherent surface, no neck seam.
 white=np.array(Image.open(d/'inputs/04_WHOLE_TWO_ARMS_EXPOSED_BLOUSE_WHITE_DOMAIN.png').convert('L'))>0
 rgb=target[:,:,:3].astype(float);humanclass=((rgb[:,:,1]>95)&(rgb[:,:,2]>135)&(rgb[:,:,2]>rgb[:,:,0]+15))|((rgb[:,:,0]>120)&(rgb[:,:,0]>rgb[:,:,2]+25)&(rgb[:,:,2]>90))|((rgb[:,:,1]>rgb[:,:,0]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.03)&(X>500)&(Y<810))
 edit=white|nd.binary_dilation(humanclass&(Y>275)&(Y<1010)&(X<810),iterations=3)|((Y<435)&(X>195)&(X<700))
 base=target.copy();base[edit]=0
 # Actual native cuff skin underlay, never an invented patch or an old-tech arm.
 src=native[72]if f<84 else native[84];dist=(X-548)*.535+(Y-530)*.845
 cuff=np.zeros_like(body);use=(src['far'][:,:,3]>0)&(dist>-4)&(dist<20);cuff[use]=src['far'][use]
 final=comp(base,body,cuff,cloth,props,lip,near,far)
 # Native BLUE sleeve is in front of its bare-arm opening; keep the complete
 # original cuff plane instead of stretching/cropping a new thin seam.
 cuffblue=np.zeros_like(body);bc=(body[:,:,3]>0)&(body[:,:,2]>body[:,:,0]+15)&(body[:,:,1]>95)&(((X>475)&(Y>430)&(Y<600))|((X>75)&(X<250)&(Y>540)&(Y<650)));cuffblue[bc]=body[bc];final=comp(final,cuffblue)
 if f==84:
  over=np.zeros_like(cloth);domain=(near[:,:,3]>0)&(X>=414)&(X<=448)&(Y>=951)&(Y<=965)&(cloth[:,:,3]>0);over[domain]=cloth[domain];final=comp(final,over);save(over,q/'TRUE_FRONT_EDGE_ABOVE_UNDERHOOK_RGBA.png')
 final[Y>=1100]=target[Y>=1100]
 save(body,q/'COHERENT_NATIVE_HEAD_COMPLETE_BLOUSE_RGBA.png');save(near,q/'COMPLETE_NATIVE_NEAR_ARM_HAND_RGBA.png');save(far,q/'COMPLETE_NATIVE_FAR_ARM_JADE_HAND_RGBA.png');save(final,q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_RGBA.png')
 bg=Image.new('RGBA',(1024,1536),(232,235,239,255));bg.alpha_composite(Image.fromarray(final));bg.convert('RGB').save(q/'FULL_ON_GRAY.png');bg.crop((70,275,810,1040)).convert('RGB').save(q/'COMPLETE_BOTH_ARMS_COLLAR_HEM_CONTACTS_1TO1.png');bg.crop((250,760,450,910)).resize((600,450)).convert('RGB').save(q/'FORMER_HEM_WEDGE_3X.png');bg.crop((330,865,490,1000)).resize((640,540)).convert('RGB').save(q/'TRUE_NEAR_FRONT_CONTACT_4X.png');bg.crop((560,620,750,810)).resize((570,570)).convert('RGB').save(q/'TRUE_FAR_CONTACT_3X.png')
 report=dict(frame=f,status='PENDING_ACTUAL_V2_SEMANTIC_REVIEW_NOT_PRODUCTION_LOCK',generation_calls=1,additional_generation_calls=0,source_human_body=72 if f<84 else 84,source_near_arm=72 if f<84 else 84,source_far_arm=72 if f==72 else 78,near072_078_exact_same_array=f<84,far078_084_exact_same_array=f>=78,whole_far_registration=map72 if f==72 else map78,whole_near_registration=map84 if f==84 else None,blouse_same_source_lower_hem_max_projection_dy=27,body_head_same_native_raw_coherent=True,old_head_collar_guard_removed=True,per_finger_transform=False,cloth_SHA256=sha(clothp),true_props_SHA256=sha(propsp),true_props_and_four_rods_geometry_changed=False,output_SHA256=sha(q/f'F{f:03d}_SAME_CLOTH_TRUE_PROPS_NATIVE_RGBA.png'))
 (q/'SOURCE_AND_CONTACT_CHECK.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report);panels.append(bg.convert('RGB'))
sheet=Image.new('RGB',(1536,800),(232,235,239));dr=ImageDraw.Draw(sheet)
for i,p in enumerate(panels):sheet.paste(p.resize((512,768)),(i*512,32));dr.text((i*512+8,10),f'F{[72,78,84][i]:03d}: same-source composition / pending actual review',fill='black')
sheet.save(R/'THREE_SAME_SOURCE_SEMANTIC_V2_REVIEW.png');(R/'V2_SEMANTIC_SOURCE_REPORT.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps([dict(frame=r['frame'],sha=r['output_SHA256'])for r in reports],indent=2))
