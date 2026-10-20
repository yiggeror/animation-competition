from PIL import Image,ImageDraw
import numpy as np,json
from pathlib import Path
p=Path(__file__).resolve().parent;base=Image.open(p/'ORIGINAL_UPPER_AUTHORITY.png').convert('RGBA');raw=Image.open(p/'RAW_FULL_CANVAS.png').convert('RGBA')
# One intact paired-leg component, no independent limb scaling or drawn pixels.
mask=Image.new('L',raw.size);ImageDraw.Draw(mask).polygon([(690,850),(825,850),(875,1010),(890,1334),(530,1334),(530,1100),(610,980)],fill=255)
a=np.array(raw);a[:,:,3]=np.minimum(a[:,:,3],np.array(mask)); yellowraw=(a[:,:,0]>140)&(a[:,:,1]>120)&(a[:,:,2]<120)&(a[:,:,1].astype(int)-a[:,:,2].astype(int)>70); a[yellowraw]=0;part=Image.fromarray(a)
P=np.array([[743.,1290.],[843.,1275.]]);Q=np.array([[726.,1299.],[817.,1283.]])
u=P[1]-P[0];v=Q[1]-Q[0];scale=np.linalg.norm(v)/np.linalg.norm(u);angle=np.arctan2(v[1],v[0])-np.arctan2(u[1],u[0]);A=scale*np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]]);scale=1350/1335;angle=0.;A=np.eye(2)*scale;t=np.array([-30.,-5.]);anchor=P.mean(axis=0)@A.T+t; factor=1.02; A*=factor;scale*=factor;t=anchor-factor*(anchor-t);inv=np.linalg.inv(A);off=-inv@t;fit=part.transform(base.size,Image.Transform.AFFINE,(*inv[0],off[0],*inv[1],off[1]),Image.Resampling.BICUBIC)
b=np.array(base);y,x=np.indices(b.shape[:2]);old=((y>875)&(x>600)&(x<900))|((y>1000)&(x>530)&(x<900));old &= ~((x>870)&(y<1100));old &= ~((x<625)&(y<1000)); cm=Image.new('L',base.size);ImageDraw.Draw(cm).polygon([(600,850),(775,850),(821,905),(790,890),(755,899),(701,929),(666,944),(622,943),(600,934)],fill=255);old &= ~(np.array(cm)>0)
# Keep source yellow dress pixels even where lower extraction boundary overlaps hem.
yellow=(b[:,:,0]>140)&(b[:,:,1]>120)&(b[:,:,2]<120)&(b[:,:,1].astype(int)-b[:,:,2].astype(int)>70)&(y<950);old &= ~yellow
armmask=Image.new('L',base.size);ImageDraw.Draw(armmask).polygon([(807,723),(867,719),(860,800),(908,899),(963,980),(965,1024),(935,1034),(901,982),(872,900),(816,815)],fill=255);old &= ~((y<1100)&(x>(830+.5*(y-850))))
skin=(b[:,:,0]>100)&(b[:,:,1]>60)&(b[:,:,2]>50)&(b[:,:,0]>b[:,:,1]*1.1)&(b[:,:,0]<b[:,:,1]*1.8)&(b[:,:,1]>b[:,:,2]*1.05)&(b[:,:,1]<b[:,:,2]*1.8)
old |= skin&(np.array(cm)>0)&(y>875)&(x>650)
# Restore complete original front hem, including white dots and ink, not just yellow.
frontmask=Image.new('L',base.size);ImageDraw.Draw(frontmask).polygon([(775,860),(800,860),(809,874),(816,883),(822,892),(823,902),(819,900),(815,894),(812,891),(807,889),(801,889),(795,890),(790,892),(783,882)],fill=255);old[(np.array(frontmask)>0)&~skin]=False
backmask=Image.new('L',base.size);ImageDraw.Draw(backmask).polygon([(672,936),(696,925),(710,936),(690,938)],fill=255);backregion=np.array(backmask)>0;back=np.zeros_like(b);back[backregion]=b[backregion];old |= backregion
b[old]=0;out=Image.alpha_composite(Image.alpha_composite(Image.fromarray(back),fit),Image.fromarray(b));allowed=old|(np.array(fit)[:,:,3]>0); oa=np.array(out);ba=np.array(base);oa[~allowed]=ba[~allowed];out=Image.fromarray(oa);out.save(p/'PAIR_ONLY_CANDIDATE_NOT_LOCKED.png');bg=Image.new('RGBA',base.size,'#edf0f1');bg.alpha_composite(out);bg.convert('RGB').save(p/'PAIR_ONLY_FULL.jpg',quality=95);bg.crop((500,830,950,1350)).convert('RGB').save(p/'PAIR_ONLY_KNEES_FEET.jpg',quality=95)
# Verify exactly no change outside union of old and transformed candidate domain.
allowed=old|(np.array(fit)[:,:,3]>0);o=np.array(out);src=np.array(base);changed=np.any(o!=src,axis=2);report={'source':'exec-4119ddc6-fd79-4218-8832-d3b0b7bb0dd8','status':'SINGLE_PAIRED_LEG_DIAGNOSTIC_NOT_ADOPTED','scale':float(scale),'rotation_degrees':float(np.degrees(angle)),'translation':t.tolist(),'source_foot_bbox_corners':P.tolist(),'target_foot_bbox_corners':Q.tolist(),'mapped_foot_bbox_corners':(P@A.T+t).tolist(),'foot_corner_residuals':(P@A.T+t-Q).tolist(),'protected_domain_pixel_changes':int((changed&~allowed).sum()),'warning':'Toe bounding-box landmarks are not exact contact points; original hem boundary and natural body proportions require visual review. New upper body and stool not used.'};(p/'PAIR_FIT_CHECK.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
