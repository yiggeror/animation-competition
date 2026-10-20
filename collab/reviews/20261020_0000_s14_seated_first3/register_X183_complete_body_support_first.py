from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import numpy as np,json,hashlib
P=Path(__file__).parent;R=P.parent;B=Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA');A=Image.open(P/'X183_complete_body_call01_original.png').convert('RGBA');size=B.size;Y,X=np.indices((1254,1254));s=1.;t=[-8.,-1.];N=A.transform(size,Image.Transform.AFFINE,(1,0,8,0,1,1),Image.Resampling.BICUBIC);na=np.array(N);ba=np.array(B)
# Preserve the complete new native figure, including the new continuous hips/knees/hands/legs/whole shoes.
# Only the bench is the fixed old scene object. Do not cut the body back to old knee/hand positions.
mask=(Y<810)&(X>360)&(X<1110);mask|=(Y>=740)&(X>720)&(X<1100)
for a in [na,ba]:
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);cloth=(Y>390)&(Y<950)&(X>400)&(X<1010)&(a[:,:,3]>80)&(r>178)&(g>140)&(b<140)&(g-b>48);lab,n=ndimage.label(cloth);sz=np.bincount(lab.ravel());k=np.argmax(sz[1:])+1;mask|=ndimage.binary_dilation(ndimage.binary_fill_holes(lab==k),iterations=3)
# Exclude the exact original bench where its true silhouette is visible.
r,g,b=ba[:,:,:3].astype(float).transpose(2,0,1);wood=(ba[:,:,3]>50)&(Y>800)&(X<735)&(r>85)&(r<225)&(g>50)&(g<185)&(b>20)&(b<145)&(r-g>12)&(g-b>12);lab,n=ndimage.label(wood);wk=np.zeros_like(wood)
for k in range(1,n+1):
 z=lab==k
 if z.sum()>400:wk|=z
wk=ndimage.binary_dilation(ndimage.binary_fill_holes(wk),iterations=3);mask[wk]=0
c=Image.composite(N,B,Image.fromarray(np.uint8(mask)*255));a=np.array(c);white_gap=(a[:,:,:3].min(2)>210)&(Y>920)&(Y<1080)&(X>780)&(X<890);a[white_gap]=0;lab,n=ndimage.label(a[:,:,3]>12);sz=np.bincount(lab.ravel());dust=np.isin(lab,np.where((sz<8)&(np.arange(len(sz))>0))[0]);a[dust]=0
# Same limited native-cloth correction as the prior measured complete-cloth candidate, B +2 only.
r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);w=np.clip((g-b-55)/30,0,1)*np.clip((r-140)/50,0,1);w*=((Y>395)&(Y<940)&(X>420)&(X<995)&(a[:,:,3]>0)&(b<135));w[ndimage.binary_dilation((a[:,:,:3].min(2)>175)&(a[:,:,3]>0),iterations=1)]=0;a[:,:,2]=np.clip(np.rint(a[:,:,2]+2*w),0,255).astype('uint8');c=Image.fromarray(a);fp=P/'X183_complete_physical_registered_candidate.png';c.save(fp);bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(c);bg.convert('RGB').resize((880,880)).save(P/'X183_COMPLETE_PHYSICAL_REGISTERED_REVIEW.jpg',quality=92);bg.crop((430,690,1065,1210)).resize((1016,832)).convert('RGB').save(P/'X183_COMPLETE_HIP_KNEES_HANDS_SOLES_DETAIL.jpg',quality=92)
rec={'status':'SUPPORT_FIRST_COMPLETE_BODY_SINGLE_TRANSLATION_CANDIDATE','raw':str((P/'X183_complete_body_call01_original.png').resolve()),'raw_sha256':hashlib.sha256((P/'X183_complete_body_call01_original.png').read_bytes()).hexdigest(),'scale':s,'rotation_deg':0,'translation':t,'preserved':'Complete native head/chest/hips/skirt/both arms/hands/knees/legs/whole shoes kept as one body; original wooden bench fixed. Shoe silhouette was not used to scale the person.','manual_physical_guides_native_before_translation':{'pelvis_seat_contact_approx':[451,817],'near_back_sole_heel_approx':[732,1190],'far_back_sole_heel_approx':[857,1170]},'original_physical_guides_approx':{'pelvis_seat_contact':[452,819],'near_back_sole_heel':[727,1190],'far_back_sole_heel':[846,1171]},'approx_residual_after_translation':{'pelvis_seat':[-9,-3],'near_heel':[-3,-1],'far_heel':[3,-2]},'note':'Approximate contact landmarks from actual images, not a claim of identical shoe outline. Increased forward lean is real; raw head/chest not stretched or shrunk. Parent to judge actual 180/183/186 exposure.','final':str(fp.resolve()),'final_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'superseded_bad_method':'X183_complete_registered_candidate.png scaled by the changed red-shoe outline and clipped native hands; not for locking or downstream use.'};(P/'X183_support_first_single_registration.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(json.dumps(rec,ensure_ascii=False))
