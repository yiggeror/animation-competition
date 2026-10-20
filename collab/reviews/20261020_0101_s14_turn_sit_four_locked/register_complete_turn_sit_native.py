from pathlib import Path
from PIL import Image,ImageDraw
from scipy import ndimage
import numpy as np,json,hashlib,sys
R=Path('/workspace/scratch/f060b5601755/s14_stage_setup_inputs_20261019_0756');P=R/'x168_x179_turn_sit_zero_call';U=Path('/tmp/laidian_s14_turn_sit_20261020');f=int(sys.argv[1]);raw=U/f'X{f}_complete_body_call01_original.png';A=Image.open(raw).convert('RGBA');B=Image.open(U/f'X{f}_ONLY_COMPLETE_NEW_BODY_TARGET.png').convert('RGBA');ba=np.array(B);Y,X=np.indices(ba.shape[:2]);h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def shoe(im):
 a=np.array(im);YY,XX=np.indices(a.shape[:2]);r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);m=(YY>im.height*.77)&(a[:,:,3]>220)&(r>125)&(g<110)&(b<110)&(r>1.75*g);return np.c_[XX[m],YY[m]]
a=shoe(A);b=shoe(B);ca=a.mean(0);cb=b.mean(0);s=np.sqrt(((b-cb)**2).sum(1).mean()/((a-ca)**2).sum(1).mean());t=cb-s*ca;N=A.transform(B.size,Image.Transform.AFFINE,(1/s,0,-t[0]/s,0,1/s,-t[1]/s),Image.Resampling.BICUBIC);na=np.array(N)
# Native whole body, one global registration only. Complete semantic contours extend the technical white region.
def nativewood(a):
 r,g,b=a[:,:,:3].astype(float).transpose(2,0,1);m=(Y>880)&(X<610)&(a[:,:,3]>30)&(r>80)&(r<225)&(g>45)&(g<185)&(b>20)&(b<145)&(r-g>12)&(g-b>12);ll,n=ndimage.label(m);sz=np.bincount(ll.ravel());return ndimage.binary_dilation(ndimage.binary_fill_holes(np.isin(ll,np.where((sz>400)&(np.arange(len(sz))>0))[0])),iterations=4)
wood=nativewood(na);nativebody=(na[:,:,3]>15)&~wood&(Y<1176);ll,n=ndimage.label(nativebody);sz=np.bincount(ll.ravel());nativebody=np.isin(ll,np.where((sz>100)&(np.arange(len(sz))>0))[0]);mask=np.array(Image.open(U/f'X{f}_WHOLE_HEAD_TORSO_ARMS_HIPS_LEGS_WHITE_DOMAIN.png').convert('L'))>0;mask|=ndimage.binary_dilation(nativebody,iterations=3)
# Exact already visible stool remains behind full native character; newly revealed native seat span may be retained.
keep=np.array(Image.open(U/f'X{f}_VISIBLE_REAL_STOOL_BLACK_PROTECTION_CHECK.png').convert('L'))>0;mask[keep&~ndimage.binary_dilation(nativebody,iterations=2)]=False;mask[(Y>=1150)&(X<530)]=False;mask[Y>=1176]=False
out=Image.composite(N,B,Image.fromarray(np.uint8(mask)*255));o=np.array(out)
# Only isolated alpha dust and bright background trapped between the two calves; no figure material altered here.
ll,n=ndimage.label(o[:,:,3]>12);sz=np.bincount(ll.ravel());dust=np.isin(ll,np.where((sz<8)&(np.arange(len(sz))>0))[0]);o[dust]=0;gap=(Y>1045)&(Y<1176)&(X>590)&(X<760)&(o[:,:,:3].min(2)>210);o[gap]=0
# Same-mother semantic average RGB; exclude wood, fixed shoes, white dots and ink using the same thresholds in both figures.
mother=Image.open(R/'refs/assets/chars/x15/F000.png').convert('RGBA');mbg=Image.new('RGBA',B.size);mbg.alpha_composite(mother,(-200,100));ma=np.array(mbg)
def regions(v):
 r,g,b=v[:,:,:3].astype(float).transpose(2,0,1);ok=v[:,:,3]>245;w=nativewood(v);hair=ok&(Y<790)&(r>20)&(r<130)&(g>20)&(g<120)&(b>20)&(b<110)&(r-g<25)&(g-b<25);ll,n=ndimage.label(hair);sz=np.bincount(ll.ravel());hair=np.isin(ll,np.where((sz>1000)&(np.arange(len(sz))>0))[0]);skin=ok&~w&(Y<1176)&(r>180)&(g>120)&(b>105)&(r-g>22)&(g-b>9)&(g-b<72);cloth=ok&~w&(Y>400)&(Y<1100)&(r>190)&(g>150)&(b<130)&(r-g>6);return {'hair':ndimage.binary_erosion(hair,iterations=2),'skin':ndimage.binary_erosion(skin,iterations=2),'yellow_cloth':ndimage.binary_erosion(cloth,iterations=2)}
refs=regions(ma);regs=regions(o);before={k:o[m,:3].mean(0) for k,m in regs.items()};reference={k:ma[m,:3].mean(0)for k,m in refs.items()};cal=[]
for k in ['hair','skin','yellow_cloth']:
 delta=before[k]-reference[k];offs=np.where(abs(delta)>4,-np.sign(delta)*np.ceil(abs(delta)-3),0).astype(int)
 if not np.any(offs):continue
 # Expand semantic interiors to whole material, retaining highlights/white dots/ink and alpha.
 r,g,b=o[:,:,:3].astype(float).transpose(2,0,1)
 if k=='hair':m=ndimage.binary_dilation(regs[k],iterations=2)&(r>20)&(r<130)&(g>20)&(b>20)
 elif k=='skin':m=ndimage.binary_dilation(regs[k],iterations=2)&(r>180)&(g>120)&(b>105)&(r-g>22)&(g-b>9)&(g-b<72)
 else:m=ndimage.binary_dilation(regs[k],iterations=2)&(r>178)&(g>140)&(b<145)&(g-b>48)&(o[:,:,:3].min(2)<175)
 vals=o[:,:,:3].astype(int);vals[m]=np.clip(vals[m]+offs,0,255);o[:,:,:3]=vals.astype('uint8');cal.append({'region':k,'max_rgb_offset':offs.tolist(),'before_mean_delta':delta.tolist(),'material_pixels':int(m.sum()),'alpha_unchanged':True})
final=U/f'X{f}_complete_native_registered_candidate.png';Image.fromarray(o).save(final);Image.fromarray(np.uint8(mask)*255).save(U/f'X{f}_native_complete_return_mask.png');regs2=regions(o);palette={k:{'mother_mean_rgb':reference[k].tolist(),'mean_rgb':o[m,:3].mean(0).tolist(),'delta':(o[m,:3].mean(0)-reference[k]).tolist(),'within4':bool(abs(o[m,:3].mean(0)-reference[k]).max()<=4)}for k,m in regs2.items()};bg=Image.new('RGBA',B.size,'#f7f5ed');bg.alpha_composite(Image.fromarray(o));bg.convert('RGB').resize((793,900)).save(U/f'X{f}_COMPLETE_NATIVE_REGISTERED_REVIEW.jpg',quality=92);bg.crop((300,660,950,1050)).resize((1000,600)).convert('RGB').save(U/f'X{f}_COMPLETE_ARMS_HIPS_SEAT_AIR_DETAIL.jpg',quality=92);d={'status':'ONE_COMPLETE_NATIVE_BODY_SINGLE_SIMILARITY_CANDIDATE','frame':f,'scale':s,'translation':t.tolist(),'rotation_deg':0,'raw':str(raw),'raw_sha256':h(raw),'final':str(final),'final_sha256':h(final),'return_scope':'Whole native head neck chest both arms full skirt hips knees calves; true known stool and complete true feet restored behind. No per-limb spatial transforms.','same_mother_semantic_mean_rgb':palette,'minimal_native_material_calibration':cal,'disconnected_dust_pixels_removed':int(dust.sum()),'calf_background_bright_pixels_removed':int(gap.sum()),'entry168_dependency':'Missing150–167 actual final stance remains unresolved'};(P/f'X{f}_native_single_registration.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print(json.dumps(d,ensure_ascii=False))
