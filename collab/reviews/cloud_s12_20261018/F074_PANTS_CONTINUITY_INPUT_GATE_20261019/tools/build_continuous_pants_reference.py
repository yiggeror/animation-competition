"""REFERENCE CONSTRUCTION ONLY. Source074 cloth pixels remapped as one whole pants
volume towards070 support envelope; never adopted as actual anatomy repair.
All outside semantic pants, both current074 shoes/ankles and blue hem hard exact.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np,json,hashlib,runpy
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.interpolate import RBFInterpolator
O=Path(__file__).resolve().parents[1];R=O.parent;ns=runpy.run_path(str(O/'tools/build_semantic_masks.py'));sem=ns['semantic_pants'];S=R/'F074_COMPLETE_actual_call01_20261019';M=R/'F070_COMPLETE_actual_call01_20261019'
A,P,blue,feet,core=sem(S/'candidate/F074.png');B,Q,_,_,_=sem(M/'candidate/F070.png');allowed=np.asarray(Image.open(O/'masks/PROPOSED_WHOLE_PANTS_PLUS_2PX_CONNECTION_ALLOWED.png').convert('L'))>0
# Only support ENVELOPE geometry comes from070, no070 RGB/alpha pixels adopted.
def profile(mask):
 y,x=np.where(mask);lo=np.full(1536,np.nan);hi=lo.copy()
 for yy in np.unique(y):
  xx=x[y==yy];lo[yy]=xx.min();hi[yy]=xx.max()
 valid=np.isfinite(lo);lo=np.interp(np.arange(1536),np.where(valid)[0],lo[valid]);hi=np.interp(np.arange(1536),np.where(valid)[0],hi[valid]);return gaussian_filter1d(lo,3),gaussian_filter1d(hi,3),int(y.max())
L,V,base074=profile(P);L70,V70,base070=profile(Q)
# The complete hip/thigh region blends into the corrected near/far knee/shin envelope.
# Current074 waist/hem stays still and current074 ankle/cuff points stay fixed.
def forward(p):
 x,y=p;iy=int(np.clip(round(y),0,1535));v=np.clip((y-1010)/130,0,1);v=v*v*(3-2*v)
 f=np.clip((x-L[iy])/max(1,V[iy]-L[iy]),0,1);pull=np.clip(V[iy]-V70[iy],0,30)*v
 tail=float(np.median(np.clip(V[1260:1301]-V70[1260:1301],0,30)));tailBlend=np.clip((y-1240)/50,0,1);pull=pull*(1-tailBlend)+tail*v*tailBlend
 dx=-pull*f**1.15
 # Match support thickness without a one-shin scaling operation; both whole thighs/hips participate.
 dy=0. # Current074 ankle/ground height stays exact; smooth complete cloth flow avoids a pinched bottom junction.
 return np.array([x+dx,y+dy])
source=[];target=[]
for yy in range(880,1361,30):
 for xx in range(120,761,35):
  s=np.array([xx,yy],float);source.append(s);target.append(forward(s))
src=np.array(source);dst=np.array(target);rbf=RBFInterpolator(dst,src-dst,kernel='thin_plate_spline',smoothing=.15)
y,x=np.mgrid[0:1536:2,0:1024:2];p=np.c_[x.ravel(),y.ravel()];disp=np.empty_like(p,dtype=float)
for k in range(0,len(p),8000):disp[k:k+8000]=rbf(p[k:k+8000])
disp=disp.reshape(768,512,2);Y,X=np.mgrid[:1536,:1024];dx=map_coordinates(disp[:,:,0],[Y/2,X/2],order=1,mode='nearest');dy=map_coordinates(disp[:,:,1],[Y/2,X/2],order=1,mode='nearest')
cloth=np.zeros_like(A);cloth[allowed]=A[allowed];a=cloth.astype(float)/255;a[:,:,:3]*=a[:,:,3:4];w=np.stack([map_coordinates(a[:,:,i],[Y+dy,X+dx],order=1,mode='constant')for i in range(4)],axis=2);good=w[:,:,3]>0;w[good,:3]/=w[good,3:4];w=np.uint8(np.clip(w*255+.5,0,255));w[~allowed]=0
# This is ONLY an illustrated source-pixel pose reference. The eventual new cloth must be drawn.
t=A.copy();t[allowed]=0;targetImage=Image.alpha_composite(Image.fromarray(t),Image.fromarray(w));t=np.array(targetImage);t[~allowed]=A[~allowed];assert np.array_equal(t[~allowed],A[~allowed]);assert np.array_equal(t[feet],A[feet]);assert np.array_equal(t[blue],A[blue]);targetImage=Image.fromarray(t)
targetImage.save(O/'reference/COMPLETE074_PANTS_TARGET_REFERENCE_ONLY_NOT_REPAIR.png');Image.fromarray(w).save(O/'reference/WHOLE_PANTS_SOURCE074_TEXTURE_GEOMETRY_REFERENCE_ONLY.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
box=(0,850,760,1380);scale=1.5
first=Image.new('RGB',(1140,960),'#e1e4e6');d=ImageDraw.Draw(first);d.text((18,18),'F074 WHOLE PANTS CONTINUITY / LOCAL DRAWING INPUT ONLY',font=font(23),fill='#25313b');d.text((18,55),'Current074 hips + BOTH thighs -> qualified070 knee/shin volume -> current074 ankles/shoes.',font=font(18),fill='#25313b');c=targetImage.crop(box);base=Image.new('RGBA',c.size,'#e1e4e6');base.alpha_composite(c);first.paste(base.resize((1140,795),Image.Resampling.LANCZOS).convert('RGB'),(0,95));d.text((18,904),'Blue hem / upper body / hands / BOTH shoes + bare ankles HARD PROTECTED.',font=font(18),fill='#25313b');d.text((18,932),'Source074 pixels are POSE REFERENCE ONLY; draw one natural full pants volume.',font=font(17),fill='#25313b');first.save(O/'inputs/01_COMPLETE_HIPS_THIGHS_KNEES_SHINS_TARGET_REFERENCE_ONLY.png')
# Same position true ground and current074 props. Ground source is unchanged actual074 cached layer.
T=R/'F074_COMPLETE_TARGET_from_LOCKED070_20261019';ctx=Image.open(T/'code_props/F074_BACKGROUND_WITH_CLOTH_UNLOADING_REFERENCE.png').convert('RGBA');ctx.alpha_composite(Image.open(S/'actual_scene/F074_native_ground_shadows_actual_layer.png'))
fg=np.asarray(Image.open(S/'layers/F074_FG_true_front_fingers.png').convert('RGBA'));own=fg[:,:,3]>0;back=t.copy();back[own]=0;front=np.zeros_like(t);front[own]=t[own]
def scene(img):return img.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
ctx.alpha_composite(scene(Image.fromarray(back)));ctx.alpha_composite(Image.open(S/'actual_scene/F074_code_props_actual_layer.png'));ctx.alpha_composite(scene(Image.fromarray(front)));ctx.alpha_composite(Image.open(S/'actual_scene/F074_box_front_actual_layer.png'));ctx.save(O/'reference/SAME074_GROUND_PROPS_CONTEXT_REFERENCE_ONLY.png')
second=Image.new('RGB',(1920,1160),'#e1e4e6');second.paste(ctx.convert('RGB'));d=ImageDraw.Draw(second);d.text((18,18),'SAME LOCAL PANTS TARGET / TRUE CURRENT074 GROUND + SHADOW + BOX/RODS',font=font(24),fill='white');d.text((18,1100),'Reference composite ONLY. No actual074 Canvas rerender, no new character drawing, no old whole body.',font=font(21),fill='#25313b');second.save(O/'inputs/02_SAME_POSITION_TRUE_GROUND_CONTEXT_REFERENCE_ONLY.png')
third=Image.new('RGB',(1024,650),'#e1e4e6');d=ImageDraw.Draw(third);d.text((18,18),'CURRENT074 MATERIAL + NATURAL KNEE FOLD ONLY / NO ALTERNATE POSE',font=font(21),fill='#25313b')
sourceImage=Image.fromarray(A)
for title,bbox,pos,size in [('074 NAVY MATERIAL',(330,1050,430,1150),(35,125),(420,420)),('074 FOLD / REDRAW NATURAL ROUND KNEE',(550,1150,650,1250),(550,125),(420,420))]:
 c=sourceImage.crop(bbox);b=Image.new('RGBA',c.size,'#e1e4e6');b.alpha_composite(c);third.paste(b.resize(size,Image.Resampling.NEAREST).convert('RGB'),pos);d.text((pos[0],pos[1]-36),title,font=font(15),fill='#25313b')
third.save(O/'inputs/03_ONLY_CURRENT074_PANTS_MATERIAL_KNEE_FOLD.png')
proof={'status':'REFERENCE_ONLY_NOT_ADOPTED_REPAIR','source074_native_SHA256':hashlib.sha256((S/'candidate/F074.png').read_bytes()).hexdigest(),'qualified070_support_native_SHA256':hashlib.sha256((M/'candidate/F070.png').read_bytes()).hexdigest(),'whole_semantic_pants_allowed_pixels':int(allowed.sum()),'reference_outside_allowed_RGBA_changes':int(np.count_nonzero(np.any(t[~allowed]!=A[~allowed],axis=1))),'reference_current074_both_shoes_bare_ankles_RGBA_changes':int(np.count_nonzero(np.any(t[feet]!=A[feet],axis=1))),'reference_blue_hem_RGBA_changes':int(np.count_nonzero(np.any(t[blue]!=A[blue],axis=1))),'whole_texture_and_fold_reference_changed_inside':int(np.count_nonzero(np.any(t!=A,axis=2)&allowed)),'old070_RGB_or_alpha_pixels_adopted':0,'source074_current_shoes_ankles_fixed':True,'reference_not_bone_measurement_or_bone_chain_proof':True,'source_pants_base_y':base074,'support_reference_pants_base_y':base070,'controls_source':src.tolist(),'controls_target':dst.tolist(),'new_model_calls':0,'new_actual_Canvas':0}
(O/'geometry/WHOLE_PANTS_REFERENCE_AND_PROTECTION.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if not k.startswith('controls')},indent=2))
