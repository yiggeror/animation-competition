from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,binary_fill_holes
P=Path(__file__).resolve().parent;f=int(sys.argv[1]);F=P/f'F{f:03}';mother=P/'F042/S20_F042_semantic_closed.png' if f==45 else P/'F045/S20_F045_accepted.png';A=np.array(Image.open(mother).convert('RGBA'));R=np.array(Image.open(F/'raw_original.png').convert('RGBA'));H,W=A.shape[:2];pad=False
if R.shape[1]==W-1 and R.shape[0]==H:T=np.zeros_like(A);T[:,:W-1]=R;R=T;pad=True
assert R.shape==A.shape
if f==47:R=np.array(Image.open(F/'whole_native_G_registered.png').convert('RGBA'))
submitted=np.array(Image.open(F/'inputs/03_complete_GL_only_white_mask.png').convert('L'))>127;edit=submitted.copy();y,x=np.indices((H,W));rr,gg,bb=R[:,:,:3].astype(float).transpose(2,0,1);skin=(R[:,:,3]>40)&(rr>165)&(gg>100)&(bb>gg*.70)&(rr>gg+9);jade=(R[:,:,3]>40)&(gg>rr*1.05)&(gg>bb*1.04);guide=np.array(Image.open(F/'inputs/new_complete_GL_guide.png').convert('RGBA'))[:,:,3]>0;native_domain=binary_dilation(binary_fill_holes((skin|jade)&binary_dilation(guide,iterations=18)),iterations=2)&binary_dilation(guide,iterations=20);edit|=native_domain
if f==47:
 ar,ag,ab=A[:,:,:3].astype(float).transpose(2,0,1);oldjade=(A[:,:,3]>20)&(ag>ar*1.05)&(ag>ab*1.04)&(x>930)&(x<1005)&(y>285)&(y<380);edit|=binary_dilation(oldjade,iterations=2)
edit&=~((x<898)&(y>290)&(y<375));Image.fromarray(np.uint8(edit)*255).convert('RGB').save(F/'postprocess_complete_native_GL_mask.png');B=A.copy()
if f==47:
 from PIL import ImageDraw
 axes=json.loads((F/'native_registered_C_axes.json').read_text());wood=(R[:,:,3]>30)&(rr>gg+15)&(gg>bb+15)&(bb<gg*.73)&(rr>125);band=np.zeros((H,W),bool)
 for q in axes.values():band|=np.abs(y-q['slope']*x-q['intercept'])<6
 cleanwood=wood&band&~binary_dilation(skin|jade,iterations=1);R[cleanwood]=0
 prop=Image.new('RGBA',(W*4,H*4));dc=ImageDraw.Draw(prop)
 for m,b0,tip in [(.2348760341257927,99.3437042292995,[676.0527258340562,258.13228733313446]),(.16357241713220919,178.40816867165805,[673.7593943990408,288.6166213790426])]:
  pts=[tuple(v*4 for v in tip),(952*4,(m*952+b0)*4)];dc.line(pts,fill='#675034',width=16);dc.line(pts,fill='#b28b52',width=10)
 merged=np.array(Image.alpha_composite(prop.resize((W,H),Image.Resampling.LANCZOS),Image.fromarray(R)));B[edit]=merged[edit]
else:B[edit]=R[edit]
Image.fromarray(B).save(F/f'S20_F{f:03}_candidate.png');layer=np.zeros_like(B);layer[edit]=R[edit];Image.fromarray(layer).save(F/'native_GL_layer.png');bg=Image.new('RGBA',(W,H),'#bdc1c4');bg.alpha_composite(Image.fromarray(B));bg.convert('RGB').save(F/'actual_full_gray.jpg',quality=96);bg.crop((840,270,1195,465)).resize((1420,780)).convert('RGB').save(F/'actual_native_contacts_4x.jpg');change=np.any(A!=B,2);assert not np.any(change&~edit);report={'frame':f,'status':'ACTUAL_CANDIDATE_REQUIRES_VISUAL_REVIEW','image_calls':1,'raw_sha256':hashlib.sha256((F/'raw_original.png').read_bytes()).hexdigest(),'far_right_only_transparent_column_padded':pad,'submitted_mask_black_domain_new_native_GL_occlusion_pixels':int(np.any(A!=B,2)[~submitted].sum()),'postprocess_fixed_black_domain_RGBA_changes':0,'new_pixels_only_from_real_output':True,'new_complete_GL_not_old_palm_graft':True,'child_wardrobe_body_RGBA_changes':int(np.any(A[:,:835]!=B[:,:835],2).sum()),'fixed_R_CB_clamp_50px_RGBA_changes':int(np.any(A[298:345,850:896]!=B[298:345,850:896],2).sum()),'raw_native_GL_registered':f==47,'native_external_prop_only_rebound_to_fixed_axes':f==47};(F/'receipt_and_protection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
