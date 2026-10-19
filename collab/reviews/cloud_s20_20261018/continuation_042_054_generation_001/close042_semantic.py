from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes,label
P=Path(__file__).resolve().parent;PACK=P.parent;F=P/'F042';I=F/'inputs';A=np.array(Image.open(F/'raw_original.png').convert('RGBA'));B=np.array(Image.open(PACK/'costume_036_039_zero_call_001/S20_F039_costume_corrected.png').convert('RGBA'));H,W=A.shape[:2];yy,xx=np.indices((H,W))
def poly(points):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon(points,fill=255);return np.array(im)>0
def warp(a,Q,t):
 inv=np.linalg.inv(Q);return np.array(Image.fromarray(a).transform((W,H),Image.Transform.AFFINE,tuple(np.column_stack([inv,-inv@np.array(t)]).ravel()),Image.Resampling.BICUBIC))
def over(a,b):return np.array(Image.alpha_composite(Image.fromarray(a),Image.fromarray(b)))
# Retain one complete new native child, with both original arms and palms.
cm=(A[:,:,3]>0)&(xx<800);cm&=~((xx>728)&(yy<335));cm&=~((xx<435)&(yy<450));cm&=~((xx<443)&(yy>=450)&(yy<500));ids,n=label(cm);sizes=np.bincount(ids.ravel());k=max(range(1,n+1),key=lambda k:sizes[k]);cm=ids==k;child=np.zeros_like(A);child[cm]=A[cm];cs=.967;ct=np.array([18.,26.]);child=warp(child,np.eye(2)*cs,ct)
cr,cg,cb=child[:,:,:3].astype(float).transpose(2,0,1);debris=(xx>680)&(xx<750)&(yy>205)&(yy<330)&(cr>145)&(cr>cg+15)&(cg>cb+15)&(cb<cg*.73);child[binary_dilation(debris,iterations=1)]=0
# Fixed mother grandma minus former bare R; unchanged jade L remains foreground.
r,g,b=B[:,:,:3].astype(float).transpose(2,0,1);area=poly([(869,347),(928,346),(959,372),(985,396),(1046,408),(1050,448),(1006,448),(949,429),(903,418),(867,409)]);clear=binary_dilation(area&(B[:,:,3]>40)&(r>170)&(g>110)&(b>g*.72)&(r>g+9),iterations=3)&area;clear|=area&(B[:,:,3]>0)&~((r<180)&(g>r*1.03)&(b>g*.95));gm=(xx>=865)&(B[:,:,3]>0)&~clear;oldwood=(xx<900)&(yy>275)&(yy<340)&((np.abs(yy-.2348760341257927*xx-99.3437042292995)<6)|(np.abs(yy-.16357241713220919*xx-178.40816867165805)<6));gm&=~oldwood;G=np.zeros_like(B);G[gm]=B[gm]
reg=json.loads((F/'grandma_whole_registration_fit.json').read_text());M=np.array(reg['matrix']);R=warp(A,M[:,:2],M[:,2]);r,g,b=R[:,:,:3].astype(float).transpose(2,0,1);skin=(R[:,:,3]>0)&(r>150)&(g>90)&(b>g*.68)&(r>g+8);region=poly([(850,294),(904,294),(933,327),(1075,265),(1090,313),(1011,444),(972,449),(886,378),(850,370)]);guide=np.array(Image.open(I/'_new_GR_contours.png'))[:,:,3]>0;rm=poly([(850,322),(868,304),(888,303),(914,332),(949,344),(989,366),(1057,266),(1090,273),(1100,330),(1020,449),(975,449),(904,386),(850,376)])&(R[:,:,3]>0)
# A single rigid transform of the entire new R arm/palm aligns its true clamp
# to the fixed C_B. It also returns its covered shoulder root to the blouse.
fits=json.loads((F/'native_registered_C_axes.json').read_text());q=fits['C_B'];targetm=.16357241713220919;theta=math.atan(targetm)-math.atan(q['slope']);Q=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);pivot=np.array([875,q['at875']]);dest=np.array([875,targetm*875+178.40816867165805]);tr=dest-Q@pivot;GR=np.zeros_like(R);GR[rm]=R[rm];GR=warp(GR,Q,tr)
# Astra-approved single continuous semantic domain: only native bare R, no L jade/forearm/blouse.
keep=poly([(850,320),(867,305),(888,301),(907,320),(916,339),(930,341),(978,372),(984,378),(989,378),(993,370),(1008,364),(1047,387),(1051,405),(1030,418),(1011,434),(992,443),(980,444),(910,384),(865,373),(850,354)]);GR[:,:,3][~keep]=0
# Rebind rigid prop axes to actual native child grips; no old palm transplant.
ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);wood=(A[:,:,3]>150)&(ar>ag+15)&(ag>ab+15)&(ab<ag*.73);trows=[]
for role,lo,hi,gx in [('T_H',335,399,473),('T_S',407,478,482)]:
 pts=[]
 for x in range(260,430):
  ys=np.flatnonzero(wood[:,x]&(np.arange(H)>lo)&(np.arange(H)<hi))
  if len(ys):pts.append([x,float(ys.mean())])
 fit=np.polyfit(np.array(pts)[:,0],np.array(pts)[:,1],1);slope=float(fit[0]);intercept=float(cs*fit[1]+ct[1]-slope*ct[0]);clamp=[cs*gx+ct[0],cs*np.polyval(fit,gx)+ct[1]];trows.append({'id':role,'slope':slope,'intercept':intercept,'native_clamp_registered_px':clamp,'front':[245 if role=='T_H' else 230,slope*(245 if role=='T_H' else 230)+intercept],'tail':[clamp[0]+25,clamp[1]+25*slope]})
props=Image.new('RGBA',(W*4,H*4));d=ImageDraw.Draw(props);C=json.loads((PACK/'cam20_crane_lamp_left_001/registration_input.json').read_text())['rods'];lines=[]
for role in ['C_N','C_B']:
 q=C[role];lines.append((q['shaft_tip_master_px'],[952,q['slope']*952+q['intercept']]))
for q in trows:lines.append((q['front'],q['tail']))
for a,b in lines:d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#675034',width=16);d.line([tuple(v*4 for v in a),tuple(v*4 for v in b)],fill='#b28b52',width=10)
out=np.array(props.resize((W,H),Image.Resampling.LANCZOS));out=over(out,GR);out=over(out,G);out=over(out,child);out[gm]=B[gm];blue=(R[:,:,3]>150)&(R[:,:,0]<180)&(R[:,:,1]>R[:,:,0].astype(float)*1.03)&(R[:,:,2]>R[:,:,1].astype(float)*.95)&(xx>=1027)&(xx<1050)&(yy>400)&(yy<454)&(out[:,:,3]<50);out[blue]=R[blue];Image.fromarray(out).save(F/'S20_F042_semantic_closed.png');Image.fromarray(GR).save(F/'semantic_closed_native_GR.png');Image.fromarray(child).save(F/'semantic_closed_native_child.png')
bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(out));bg.convert('RGB').save(F/'semantic_closed_full_gray.jpg',quality=96);bg.crop((840,290,1040,455)).resize((1000,825)).convert('RGB').save(F/'semantic_closed_GR_5x.jpg');bg.crop((440,355,690,550)).resize((1000,780)).convert('RGB').save(F/'semantic_closed_child_arms_4x.jpg')
report={'frame':42,'status':'ACTUAL_CANDIDATE_REQUIRES_VISUAL_REVIEW','image_calls':1,'raw_sha256':hashlib.sha256((F/'raw_original.png').read_bytes()).hexdigest(),'whole_child_uniform_registration':{'scale':cs,'rotation_deg':0,'translation':ct.tolist(),'native_arms_palms_preserved':True,'old_palms_pasted':False},'whole_GR_arm_palm_one_rigid_registration':{'first_global_grandma_fit':reg,'rotation_deg':math.degrees(theta),'matrix_2x3':np.column_stack([Q,tr]).tolist(),'source_actual_clamp':pivot.tolist(),'target_fixed_CB_clamp':dest.tolist(),'no_separate_hand_warp':True},'native_T_axes':trows,'fixed_G_L_head_body_native_source_rgba_changes':int(np.any(out[gm]!=B[gm],1).sum()),'costume_visual_review_required':True};(F/'semantic_closed_registration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
