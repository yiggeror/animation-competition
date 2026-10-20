from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,math
from scipy import ndimage
P=Path(__file__).parent;R=P.parent;srcpath=R/'x197_x208_zero_call/X197_complete_registered_candidate.png';src=Image.open(srcpath).convert('RGBA');basepath=P/'X180_complete_registered_candidate.png';base=Image.open(basepath).convert('RGBA');size=base.size;changes=[]
parts=[('near_right',[(537,547),(551,541),(567,535),(584,523),(600,516),(620,509),(635,516),(645,529),(642,536),(635,541),(628,539),(621,529),(614,531),(606,538),(595,542),(583,544),(575,553),(566,559),(558,562),(561,569),(553,576),(542,578),(537,573)],[[560,558],[620,526]],[[568,575],[626,559]]),('far_left',[(709,526),(728,525),(750,521),(774,518),(787,533),(785,546),(773,548),(759,541),(744,548),(721,554),(710,551)],[[715,554],[765,540]],[[735,576],[785,568]])]
original_array=np.array(base)
for name,poly,sp,tp in parts:
 sp=np.array(sp,float);tp=np.array(tp,float);u=sp[1]-sp[0];v=tp[1]-tp[0];s=np.linalg.norm(v)/np.linalg.norm(u);ang=math.atan2(v[1],v[0])-math.atan2(u[1],u[0]);M=s*np.array([[math.cos(ang),-math.sin(ang)],[math.sin(ang),math.cos(ang)]]);t=tp[0]-M@sp[0];inv=np.linalg.inv(M);off=-inv@t;tr=(*inv[0],off[0],*inv[1],off[1]);mask=Image.new('L',size);ImageDraw.Draw(mask).polygon(poly,fill=255);sa=np.array(src);sr,sg,sb=sa[:,:,:3].astype(float).transpose(2,0,1);yellow=(sr>150)&(sg>110)&(sb<150)&(sg-sb>40)&(sa[:,:,3]>30);cut=(np.array(mask)>0)&yellow;cut=ndimage.binary_dilation(cut,iterations=3)&(sa[:,:,3]>20);mask=Image.fromarray(np.uint8(cut)*255).filter(ImageFilter.GaussianBlur(.3));patch=src.transform(size,Image.Transform.AFFINE,tr,Image.Resampling.BICUBIC);pm=mask.transform(size,Image.Transform.AFFINE,tr,Image.Resampling.BICUBIC);base=Image.composite(patch,base,pm)
 # Fill only any exposed old straight cuff edge between the real ruffle and the existing native arm.
 arr=np.array(base);orig=original_array;pa=np.array(pm);xlo,xhi=(566,633) if name=='near_right' else (733,791)
 for xx in range(xlo,xhi):
  col=orig[540:605,xx];skincol=(col[:,0]>180)&(col[:,1]>130)&(col[:,2]>110)&(col[:,2]>.65*col[:,1])&(col[:,3]>200);ys=np.where(skincol)[0]+540;cy=np.where(pa[530:595,xx]>100)[0]+530
  if len(ys) and len(cy):
   yold=int(ys.min());yn=int(cy.max())+1
   if yn<yold+2:arr[yn:yold+2,xx]=orig[min(yold+4,604),xx]
 base=Image.fromarray(arr);changes.append({'part':name,'complete_cuff_source_polygon':poly,'scale':s,'rotation_deg':math.degrees(ang),'translation':t.tolist(),'source_fit_points':sp.tolist(),'target_upper_arm_cuff_points':tp.tolist()})
p=P/'X180_complete_cuff_restored_CANDIDATE.png';base.save(p);bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(base);bg.convert('RGB').resize((880,880)).save(P/'X180_CUFF_RESTORED_COMPLETE_REVIEW.jpg',quality=92);bg.crop((520,510,815,625)).resize((1180,460)).convert('RGB').save(P/'X180_BOTH_COMPLETE_RUFFLED_CUFFS_RESTORED_DETAIL.jpg',quality=95)
r={'status':'ZERO_CALL_COMPLETE_CUFF_EDGE_RETURN_CANDIDATE','source_locked197':str(srcpath.resolve()),'source_sha256':hashlib.sha256(srcpath.read_bytes()).hexdigest(),'pre_cuff_body':str(basepath.resolve()),'pre_cuff_body_sha256':hashlib.sha256(basepath.read_bytes()).hexdigest(),'final':str(p.resolve()),'final_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':changes,'scope':'Only two whole cloth cuff edge strips returned to native upper-arm contacts. Native shoulder/puff sleeve volume and both entire arm bone chains untouched. No image generation.'};(P/'X180_complete_cuff_restoration.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
