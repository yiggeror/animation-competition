from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
P=Path(__file__).parent;A=np.asarray(Image.open(P/'F116_lift_call01/S31_F116_CHARACTER.png').convert('RGBA'));hm=np.asarray(Image.open(P/'F116_lift_call01/ACTUAL_FULL_HEAD_NECK_ADOPTION_MASK.png').convert('L'))>128
G={120:[[279,230],[268,232]],129:[[298,222],[275,218]]}
for f in [120,129]:
 D=P/f'F{f}_wrist_call01';B=np.array(Image.open(D/'REGISTERED_RAW.png').convert('RGBA'));mask=Image.new('L',(1086,1448));ImageDraw.Draw(mask).polygon([(235,165),(380,165),(386,390),(425,405),(425,475),(302,480),(270,370),(235,310)],fill=255);m=np.array(mask)>128;m&=~hm
 out=A.copy();out[m]=B[m]
 # Only exposed generated shafts outside native hand contour are removed; internal fingers/shafts remain original.
 if f==120:edge=[(245,246),(253,237),(259,230),(266,227),(271,223),(280,220),(285,220),(290,225),(304,230),(320,242),(344,270)]
 else:edge=[(245,244),(256,230),(263,221),(269,218),(276,216),(284,212),(292,214),(304,221),(314,225),(342,255)]
 removed=0
 for x in range(245,343):
  yy=float(np.interp(x,[p[0]for p in edge],[p[1]for p in edge]));iy=int(np.floor(yy))-1
  removed+=int((out[165:iy,x,3]>0).sum());out[165:iy,x,:]=0
 Image.fromarray(out).save(D/f'S31_F{f}_CHARACTER_CANDIDATE.png');Image.fromarray((m*255).astype('uint8')).save(D/'ACTUAL_FOREARM_ADOPTION_MASK.png')
 qa={'status':'Candidate native whole forearm/palm registration and true rod audit pending parent','adopted':'Complete native elbow/forearm/wrist/palm, same global similarity; no local anatomy warp','headChangedPixels':int(np.any(out[hm]!=A[hm],axis=1).sum()),'outsideSemanticForearmChangedPixels':int(np.any(out[~m]!=A[~m],axis=1).sum()),'lampAndBodyRightOfX440ChangedPixels':int(np.any(out[:,440:]!=A[:,440:],axis=2).sum()),'belowY480ChangedPixels':int(np.any(out[480:]!=A[480:],axis=2).sum()),'generatedExposedStubAlphaPixelsRemoved':removed,'actualGripPoints':G[f],'registration':json.loads((D/'REGISTRATION.json').read_text())};(D/'ACTUAL_COMPOSITE_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
 c=Image.new('RGBA',(1086,1448),'#c1c4bc');c.alpha_composite(Image.fromarray(out));c.crop((225,165,500,500)).resize((550,670)).convert('RGB').save(D/'ACTUAL_FOREARM_SEAM_CLOSE.jpg',quality=95)
 print(f,{k:v for k,v in qa.items() if k!='registration'})
(P/'wrist_group_inputs/ACTUAL_GRIPS.json').write_text(json.dumps(G,indent=2)+'\n')
