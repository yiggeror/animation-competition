from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,hashlib
R=Path('/workspace/scratch/f060b5601755/s14_stage_setup_inputs_20261019_0756');P=R/'x168_x179_turn_sit_zero_call';U=Path('/tmp/laidian_s14_turn_sit_20261020');size=(1190,1350);Y,X=np.indices(size[::-1]);h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=Image.new('RGBA',size);base.alpha_composite(Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA'),(-200,100));ba=np.array(base)
def registered(f):
 m=json.loads((P/f'X{f}_native_single_registration.json').read_text());s=m['scale'];tx,ty=m['translation'];return Image.open(m['raw']).convert('RGBA').transform(size,Image.Transform.AFFINE,(1/s,0,-tx/s,0,1/s,-ty/s),Image.Resampling.BICUBIC)
N=registered(168)
def poly_mask(pts):
 m=Image.new('L',size);ImageDraw.Draw(m).polygon(pts,fill=255);return m

def surface(srcquad,dstquad):
 A=[];b=[]
 for (x,y),(u,v) in zip(dstquad,srcquad):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);b.extend([u,v])
 c=np.linalg.solve(np.array(A),np.array(b));w=N.transform(size,Image.Transform.PERSPECTIVE,tuple(c),Image.Resampling.BICUBIC);return w,poly_mask(dstquad)
# Exact complete known mother stool including existing lower legs and all feet.
r,g,b=ba[:,:,:3].astype(float).transpose(2,0,1);wood=(ba[:,:,3]>30)&(Y>910)&(X<560)&(r>65)&(r<229)&(g>35)&(g<188)&(b>18)&(b<148)&(r-g>10)&(g-b>10);ll,n=ndimage.label(wood);sz=np.bincount(ll.ravel());wood=np.isin(ll,np.where((sz>400)&(np.arange(len(sz))>0))[0]);wood=ndimage.binary_dilation(ndimage.binary_fill_holes(wood),iterations=2);arr=ba.copy();arr[~wood]=0;bench=Image.fromarray(arr)
# Whole planar semantic faces, not narrow top patches. The target corners retain the known stool support geometry.
surfaces=[
 ('back_left_post',[(286,978),(329,978),(311,1230),(267,1230)],[(301,972),(338,972),(318,1231),(274,1233)]),
 ('back_right_post',[(493,999),(525,999),(541,1180),(507,1180)],[(491,973),(522,973),(553,1242),(514,1244)]),
 ('near_right_complete_post',[(444,979),(489,979),(509,1276),(455,1277)],[(438,972),(487,972),(507,1284),(454,1285)]),
]
# Restore crossbars in front of far posts, then complete near post in front of the bars.
for name,sq,dq in surfaces[:2]:
 lay,ma=surface(sq,dq);bench=Image.composite(lay,bench,ma);ImageDraw.Draw(bench).line(dq+[dq[0]],fill='#66472e',width=2,joint='curve')
bar_region=(Y>=1104)&(Y<=1160)&(X>=220)&(X<=526)&wood;bench=Image.composite(base,bench,Image.fromarray(np.uint8(bar_region)*255))
name,sq,dq=surfaces[2];lay,ma=surface(sq,dq);bench=Image.composite(lay,bench,ma);ImageDraw.Draw(bench).line(dq+[dq[0]],fill='#66472e',width=2,joint='curve')
# Complete seat surface: continuous native grain from the same X168 board, bounded by the original plane.
front=[(183,925),(550,925),(555,974),(183,970)];lay,ma=surface([(184,934),(473,934),(473,971),(184,971)],front);bench=Image.composite(lay,bench,ma)
top=[(187,920),(258,915),(548,915),(550,925),(183,925)];lay,ma=surface([(191,940),(469,940),(469,950),(191,950)],[(183,915),(550,915),(550,925),(183,925)]);bench=Image.composite(lay,bench,poly_mask(top));dr=ImageDraw.Draw(bench);dr.line(top+[top[0]],fill='#765134',width=2,joint='curve');dr.line(front+[front[0]],fill='#66472e',width=2,joint='curve')
# Fixed foot silhouettes and floor pixels from original mother, unchanged.
feet=((Y>=1250)&(X<245))|((Y>=1275)&(X>430)&(X<515))|((Y>=1225)&(X>265)&(X<335))|((Y>=1234)&(X>510)&(X<558));bench=Image.composite(base,bench,Image.fromarray(np.uint8(feet&wood&~((X>530)&(Y>1190)))*255));obj=Image.new('L',size);od=ImageDraw.Draw(obj)
for pp in [front,top]+[x[2] for x in surfaces]+[[(207,969),(259,970),(219,1270),(158,1274)],[(220,1127),(526,1127),(527,1167),(217,1165)],[(324,1104),(503,1110),(504,1133),(322,1127)]]:od.polygon(pp,fill=255)
bo=np.array(bench);bo[np.array(obj)==0]=0;bench=Image.fromarray(bo);bench.save(U/'X168_X177_COMPLETE_CONTINUOUS_FIXED_STOOL.png')
bg=Image.new('RGBA',size,'#f7f5ed');bg.alpha_composite(bench);bg.crop((130,885,585,1310)).resize((546,510)).convert('RGB').save(U/'X168_X177_COMPLETE_CONTINUOUS_FIXED_STOOL_REVIEW.jpg',quality=94)
for f in [168,171,174,177]:
 origin=U/f'X{f}_complete_native_registered_candidate.png';out=Image.open(origin).convert('RGBA');a=np.array(out);nn=np.array(registered(f));r,g,b=nn[:,:,:3].astype(float).transpose(2,0,1)
 # Foreground native body only. Wood is behind it; no old covered stool silhouette is interpreted as a new figure contour.
 seed=(nn[:,:,3]>130)&(((r>210)&(g>150)&(b<160)&(g-b>85))|((r>225)&(g>135)&(b>108)&(r-g>22)&(g-b<76)))
 seed=ndimage.binary_opening(seed,iterations=1);ll,n=ndimage.label(seed);sz=np.bincount(ll.ravel());body=np.isin(ll,np.where((sz>1200)&(np.arange(len(sz))>0))[0]);body=ndimage.binary_closing(body,iterations=6);body=ndimage.binary_dilation(ndimage.binary_fill_holes(body),iterations=3)&(nn[:,:,3]>5)
 white=(nn[:,:,3]>80)&(nn[:,:,:3].min(2)>190)&(nn[:,:,0]>225)&(nn[:,:,1]>225);wl,wn=ndimage.label(white);ws=np.bincount(wl.ravel());dots=np.isin(wl,np.where((ws>8)&(ws<600)&(np.arange(len(ws))>0))[0]);nearbody=ndimage.binary_dilation(body,iterations=10);dotids=np.unique(wl[dots&nearbody]);dotids=dotids[dotids>0];body|=ndimage.binary_dilation(np.isin(wl,dotids),iterations=1)
 scope=(X>=145)&(X<=558)&(Y>=900)&(Y<=1290);scope[(Y>=1176)&(X>=527)]=False
 o=np.array(Image.composite(bench,out,Image.fromarray(np.uint8(scope&~body)*255)))
 # Whole true gripping hand, including all fingers and natural native board wrap, stays at same registration.
 if f==168:
  hand=(X>474)&(X<582)&(Y>887)&(Y<997)&(nn[:,:,3]>5);r,g,b=nn[:,:,:3].astype(float).transpose(2,0,1);skin=(r>170)&(g>95)&(b>85)&(b>.66*g)&(r-g>20);hand&=ndimage.binary_dilation(ndimage.binary_fill_holes(skin&(X>474)&(X<582)&(Y>887)&(Y<997)),iterations=3);o[hand]=nn[hand]
 final=U/f'X{f}_complete_stool_closed_FINAL_CANDIDATE.png';Image.fromarray(o).save(final);bgi=Image.new('RGBA',size,'#f7f5ed');bgi.alpha_composite(Image.fromarray(o));bgi.convert('RGB').resize((793,900)).save(U/f'X{f}_COMPLETE_STOOL_CLOSED_REVIEW.jpg',quality=93);bgi.crop((170,880,640,1080)).resize((940,400)).convert('RGB').save(U/f'X{f}_STOOL_GRIP_OR_AIR_CLOSED_DETAIL.jpg',quality=94)
 rec=json.loads((P/f'X{f}_native_single_registration.json').read_text());rec['final']=str(final);rec['final_sha256']=h(final);rec['same_source_stool_semantic_close']={'scope':'Complete continuous seat board and whole exposed post faces, all from same registered X168 native stool. No narrow top patches; original mother fixed feet and crossbars. Whole character transform unchanged.','source_native168':str(U/'X168_complete_body_call01_original.png'),'complete_stool_layer':str(U/'X168_X177_COMPLETE_CONTINUOUS_FIXED_STOOL.png'),'complete_stool_sha256':h(U/'X168_X177_COMPLETE_CONTINUOUS_FIXED_STOOL.png'),'surface_planar_texture_registration':surfaces,'whole_native_body_transform_unchanged':True};(P/f'X{f}_native_single_registration.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2));print(f,h(final))
page=Image.new('RGB',(1486,800),'#f7f5ed');page.paste(Image.open(U/'X168_X177_COMPLETE_CONTINUOUS_FIXED_STOOL_REVIEW.jpg'),(0,145));page.paste(Image.open(U/'X168_STOOL_GRIP_OR_AIR_CLOSED_DETAIL.jpg'),(546,0));page.paste(Image.open(U/'X171_STOOL_GRIP_OR_AIR_CLOSED_DETAIL.jpg'),(546,400));page.save(U/'X168_X171_COMPLETE_STOOL_AND_CONTACTS_REVIEW.jpg',quality=93)
