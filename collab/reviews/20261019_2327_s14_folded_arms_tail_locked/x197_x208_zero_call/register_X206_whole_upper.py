from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,hashlib
from scipy import ndimage
P=Path(__file__).parent;R=P.parent;B=Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA');A=Image.open(P/'X206_complete_upper_call01_original.png').convert('RGBA');size=B.size
Y,X=np.indices((size[1],size[0]))
def collar(im):
 a=np.array(im);sel=(Y>365)&(Y<462)&(X>525)&(X<730)&(a[:,:,3]>220)&(a[:,:,:3].min(2)>210);labels,n=ndimage.label(sel);keep=np.zeros_like(sel)
 for k in range(1,n+1):
  z=labels==k
  if z.sum()>180:keep|=z
 return np.c_[X[keep],Y[keep]]
b=collar(B);a=collar(A);ca=a.mean(0);cb=b.mean(0);s=np.sqrt(((b-cb)**2).sum(1).mean()/((a-ca)**2).sum(1).mean());t=cb-s*ca
N=A.transform(size,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),Image.Resampling.BICUBIC)
# Use the complete native dress through its real hem, avoiding a technical waist cut.
# All head, complete legs and the rigid stool are exact F000 pixels. Native cloth is one piece.
na=np.array(N);ba=np.array(B)
def cloth(arr):
 sel=(arr[:,:,0]>178)&(arr[:,:,1]>145)&(arr[:,:,2]<132)&(arr[:,:,3]>90)&(Y>395)&(Y<940)&(X>420)&(X<985)
 lab,num=ndimage.label(sel);largest=max(range(1,num+1),key=lambda k:(lab==k).sum());return ndimage.binary_dilation(ndimage.binary_fill_holes(lab==largest),iterations=3)
cm=cloth(na)|cloth(ba);soft=cm.astype(float)
soft[(Y>=405)&(Y<744)&(X>430)&(X<1045)]=1
soft[(Y>=744)&(Y<778)&(X>780)&(X<925)]=1
# Exact complete original head/ponytails/neck/collar, with shape boundaries rather than a straight crop.
hm=Image.new('L',size);hd=ImageDraw.Draw(hm);hd.rectangle((0,0,1254,404),fill=255)
hd.polygon([(435,315),(552,315),(543,413),(514,460),(464,451),(439,407)],fill=255)
hd.polygon([(655,318),(716,318),(731,392),(721,417),(689,408),(662,386)],fill=255)
hd.polygon([(542,373),(593,390),(643,411),(665,402),(675,382),(712,410),(715,445),(690,455),(667,441),(660,433),(639,461),(597,449),(560,412)],fill=255)
soft[(np.array(hm)>0)&((ba[:,:,3]>16)|(Y<405)|(na[:,:,0]<145)|(na[:,:,1]<130))]=0
sk=(Y>744)&(X>710)&(ba[:,:,0]>150)&(ba[:,:,1]>100)&(ba[:,:,2]>95)&(ba[:,:,2]>.65*ba[:,:,1])&(ba[:,:,3]>200)
lab,num=ndimage.label(sk);leg=np.zeros_like(sk)
for k in range(1,num+1):
 z=lab==k
 if z.sum()>10000:leg|=z
leg=ndimage.binary_dilation(ndimage.binary_fill_holes(leg),iterations=3);soft[leg]=0
m=Image.fromarray(np.uint8(soft*255));c=Image.composite(N,B,m)
# One final reviewer-requested semantic join cleanup, no extra transform.
clean_arr=np.array(c);maskarr=np.array(m)
shoulder=(X>=490)&(X<=522)&(Y>=442)&(Y<=475)
true_old_hair=(ba[:,:,3]>16)&(ba[:,:,0]<145)&(ba[:,:,1]<130)&(ba[:,:,2]<115)&(Y<447)
shoulder &= ~true_old_hair
clean_arr[shoulder]=na[shoulder];maskarr[shoulder]=255
# Preserve the whole native hem outline through two old-layer edge returns.
cn=cloth(na);hem=(ndimage.binary_dilation(cn,iterations=2)&~ndimage.binary_erosion(cn,iterations=7))&(Y>735)&(Y<925)&(X>650)&(X<950)
clean_arr[hem]=na[hem];maskarr[hem]=255
c=Image.fromarray(clean_arr);m=Image.fromarray(maskarr)
fp=P/'X206_complete_registered_candidate.png';c.save(fp)
N.save(P/'X206_whole_raw_SINGLE_similarity.png');m.save(P/'X206_complete_upper_semantic_return_mask.png')
for name,im in [('X206_complete_registered_REVIEW.jpg',c),('X206_whole_raw_single_REVIEW.jpg',N)]:
 bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(im);bg.convert('RGB').save(P/name,quality=92)
bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(c);bg.crop((470,365,970,820)).resize((1000,910)).convert('RGB').save(P/'X206_full_sleeves_arms_waist_DETAIL.jpg',quality=92)
r={'status':'SINGLE_NATIVE_UPPER_PAIR_REGISTERED_CANDIDATE','scale':s,'rotation_deg':0,'translation':t.tolist(),'anchor':'complete white collar shape, uniform similarity only','collar_source_center':ca.tolist(),'collar_target_center':cb.tolist(),'raw_sha256':hashlib.sha256((P/'X206_complete_upper_call01_original.png').read_bytes()).hexdigest(),'final_sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'fixed':'Exact F000 head/neck/collar, complete legs and rigid stool/feet. Native dress/arm pair is kept complete through real hem, same single transform; seat contact remains at the original seat.','new_pose_progress':'Near right forearm folds in foreground and right hand tucks beside opposite upper arm. Far left palm keeps upper-arm contact. Two elbows remain distinct; final ease-in to exactF000 follows.','cloth_return':'Complete native dress through hem, no waist cut or half-white dots. Exact original legs and stool retained; native hip contact remains naturally on fixed original seat.'};(P/'X206_native_single_registration.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
