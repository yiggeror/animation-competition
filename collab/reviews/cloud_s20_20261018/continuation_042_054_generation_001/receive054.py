from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_dilation
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F054';A=np.array(Image.open(P/'F047/S20_F047_accepted.png').convert('RGBA'));R=np.array(Image.open(F/'raw_original.png').convert('RGBA'));H,W=A.shape[:2];pad=R.shape[1]==W-1
if pad:T=np.zeros_like(A);T[:,:W-1]=R;R=T
assert R.shape==A.shape;yy,xx=np.indices((H,W));rr,gg,bb=R[:,:,:3].astype(float).transpose(2,0,1);wood=(R[:,:,3]>40)&(rr>gg+10)&(gg>bb+10)&(bb<gg*.73);area=(R[:,:,3]>0)&(xx<835);area&=~((xx<440)&(yy<470));area&=~((xx>735)&(yy<335));Cwood=(xx>680)&(xx<835)&(yy>220)&(yy<335)&wood;area&=~binary_dilation(Cwood,iterations=1);ids,n=label(area);sizes=np.bincount(ids.ravel());main=max(range(1,n+1),key=lambda k:sizes[k]);area=ids==main;child=np.zeros_like(R);child[area]=R[area]
# One native complete child: no old palms, hands, legs or feet pasted back.
newT=[]
for role,lo,hi,gx,frontx in [('T_H',330,435,477,245),('T_S',430,520,500,230)]:
 pts=[]
 for x in range(260,430):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>lo)&(np.arange(H)<hi))
  if len(ys):pts.append([x,float(np.mean(ys))])
 fit=np.polyfit(np.array(pts)[:,0],np.array(pts)[:,1],1);m,b=float(fit[0]),float(fit[1]);cp=[gx,m*gx+b];newT.append({'id':role,'slope':m,'intercept':b,'native_clamp':cp,'front':[frontx,m*frontx+b],'tail':[gx+25,m*(gx+25)+b]})
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props);axes=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];lines=[]
for role in ['C_N','C_B']:
 q=axes[role];lines.append((q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]))
for q in newT:lines.append((q['front'],q['tail']))
for a,b in lines:d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#675034',width=16);d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#b28b52',width=10)
G=A.copy();G[:,:835]=0;out=Image.alpha_composite(props.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(G));out=Image.alpha_composite(out,Image.fromarray(child));B=np.array(out);B[:,835:]=A[:,835:];Image.fromarray(B).save(F/'S20_F054_candidate.png');Image.fromarray(child).save(F/'native_complete_child.png');bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96);bg.crop((440,340,735,550)).resize((1180,840)).convert('RGB').save(F/'actual_native_child_arms_4x.jpg');bg.crop((490,780,735,935)).resize((735,465)).convert('RGB').save(F/'actual_support_feet_3x.jpg');report={'frame':54,'image_calls':1,'status':'ACTUAL_CANDIDATE_REQUIRES_VISUAL_REVIEW','raw_sha256':hashlib.sha256((F/'raw_original.png').read_bytes()).hexdigest(),'far_right_only_transparent_column_pad':pad,'new_child_all_one_native_layer':True,'uniform_registration':'identity; original support kept without local changes','old_palm_or_foot_transplant':False,'fixed_G_all_RGBA_changes':int(np.any(A[:,835:]!=B[:,835:],2).sum()),'native_T_axes':newT,'no_X_before058':True};(F/'receipt_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
