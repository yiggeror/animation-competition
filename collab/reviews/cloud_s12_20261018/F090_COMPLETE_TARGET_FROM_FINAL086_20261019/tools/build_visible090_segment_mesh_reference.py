"""Reference-construction fix: positive connected arm image meshes, rigid hands.
Actual086 image pixels only; no skin painting, inpainting, or new character art.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,hashlib
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates,binary_dilation
from write_reference090_views import write_views
O=Path(__file__).resolve().parents[1];R=O.parent;M=R/'F086_COMPLETE_actual_call01_20261019';P=R/'F086_COMPLETE_TARGET_FROM_FINAL082_20261019'
g=json.loads((O/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').read_text());B=np.asarray(Image.open(M/'candidate/F086.png').convert('RGBA'));Y,X=np.mgrid[:1536,:1024]
fixed=np.asarray(Image.open(P/'masks/FINAL082_REAL_SHINS_ANKLES_SHOES_AND_EMPTY_FIXED.png').convert('L'))>0;active=~fixed;feet=np.asarray(Image.open(P/'masks/ORIGINAL_TRUE_SHOES_ANKLES_SURROUNDING_EMPTY_HARD.png').convert('L'))>0
UT=np.asarray(g['torso_head_native_matrix']);H=np.asarray(g['hip_source_visual_proxy']);Ht=np.asarray(g['hip_target']);K=np.asarray(g['knee_support_visual_proxy'])
def rot(d):
 a=math.radians(d);return np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]])
def at(m,q):return np.asarray(m)@np.r_[q,1.]
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
curve=np.array([[1070,225],[1085,235],[1098,270],[1112,315],[1130,360],[1150,400],[1170,445],[1190,485],[1215,520],[1245,550],[1270,552],[1290,540],[1304,540],[1315,560],[1350,580],[1535,580]],float);vx=np.interp(np.arange(1536),curve[:,0],curve[:,1]);RL=rot(6)
def bodyDesired(q):
 q=np.asarray(q,float);x,y=q;xx=int(np.clip(round(x),0,1023));yy=int(np.clip(round(y),0,1535))
 if fixed[yy,xx]:return q
 if y<=800:return at(UT,q)
 if y<=925:return Ht+rot(-5+11*smooth((y-800)/125))@(q-H)
 return q+smooth((1315-y)/220)*smooth(max(0,x-(vx[yy]-24))/75)*((K+RL@(q-K))-q)
controls={}
for y in [0,150,250,350,430,480,540,600,660,720,780,820,860,900,925,970,1020,1060,1100,1140,1180,1220,1260,1290,1315,1340,1400,1535]:
 for x in [0,130,190,230,270,310,350,390,430,470,510,550,590,630,670,710,780,900,1023]:
  q=np.array([x,y],float);controls[tuple(q)]=(q,bodyDesired(q))
s=np.array([a[0] for a in controls.values()]);t=np.array([a[1] for a in controls.values()]);rbf=RBFInterpolator(t,s-t,kernel='thin_plate_spline',smoothing=.5)
y,x=np.mgrid[0:1536:2,0:1024:2];p=np.c_[x.ravel(),y.ravel()];d=np.empty_like(p,float)
for i in range(0,len(p),8000):d[i:i+8000]=rbf(p[i:i+8000])
d=d.reshape(768,512,2);sx=X+map_coordinates(d[:,:,0],[Y/2,X/2],order=1,mode='nearest');sy=Y+map_coordinates(d[:,:,1],[Y/2,X/2],order=1,mode='nearest')
inv=np.linalg.inv(np.vstack([UT,[0,0,1]]))[:2];hx=inv[0,0]*X+inv[0,1]*Y+inv[0,2];hy=inv[1,0]*X+inv[1,1]*Y+inv[1,2];head=hy<475;sx[head]=hx[head];sy[head]=hy[head]
# Retain the real central blouse behind its moving sleeves; remove only old
# distal arm/sleeve pixels beyond the visible torso envelope before warping.
front=np.interp(np.arange(1536),[0,470,500,550,600,650,780,900,1000,1535],[1024,690,680,650,605,580,575,610,660,1024])
base=B.copy();base[(Y>=480)&(Y<=880)&(X>front[Y])]=0
pm=base.astype(float)/255;pm[:,:,:3]*=pm[:,:,3:4];n=np.stack([map_coordinates(pm[:,:,i],[sy,sx],order=1,mode='constant') for i in range(4)],axis=2);v=n[:,:,3]>0;n[v,:3]/=n[v,3:4];n=np.uint8(np.clip(n*255+.5,0,255));canvas=Image.fromarray(n)
polys={'L':[(492,486),(604,488),(704,533),(810,545),(925,579),(1010,573),(1023,704),(929,715),(806,674),(700,655),(617,665),(536,608)],'R':[(477,531),(568,536),(626,595),(704,640),(809,703),(924,730),(1023,717),(1023,851),(938,861),(794,815),(686,780),(609,766),(544,728),(497,652)]}
masks={}
for role,poly in polys.items():
 im=Image.new('L',(1024,1536));ImageDraw.Draw(im).polygon(poly,fill=255);masks[role]=np.asarray(im)>0
masks['L']&=~masks['R']
def triangle(src,sp,dp,dest):
 sp=np.asarray(sp,float);dp=np.asarray(dp,float);sa=np.linalg.det(np.c_[sp,np.ones(3)]);da=np.linalg.det(np.c_[dp,np.ones(3)])
 if abs(sa)<1e-6:return None
 if da/sa<=0:raise ValueError('Inverted connected arm triangle; stop instead of covering holes.')
 lo=np.floor(dp.min(0)-1).astype(int);hi=np.ceil(dp.max(0)+1).astype(int);lo=np.maximum(lo,[0,0]);hi=np.minimum(hi,[1024,1536])
 if np.any(hi<=lo):return float(da/sa)
 C=np.linalg.solve(np.c_[dp,np.ones(3)],sp);coef=(C[0,0],C[1,0],C[2,0]+np.dot(lo,C[:2,0]),C[0,1],C[1,1],C[2,1]+np.dot(lo,C[:2,1]))
 patch=src.transform(tuple(hi-lo),Image.Transform.AFFINE,coef,Image.Resampling.BICUBIC);mask=Image.new('L',patch.size);ImageDraw.Draw(mask).polygon([tuple(p-lo) for p in dp],fill=255);aa=np.asarray(patch).copy();aa[:,:,3]=np.uint8(aa[:,:,3].astype(float)*np.asarray(mask)/255);dest.alpha_composite(Image.fromarray(aa),tuple(lo));return float(da/sa)
meshQA={}
for role in ['L','R']:
 a=g['arms_actual_source_projected_proxies_not_hidden_bones'][role];S,E,W=[np.asarray(a['source'][q]) for q in ['shoulder','elbow','wrist']];U=np.asarray(a['upper_matrix']);F=np.asarray(a['forearm_matrix']);Hand=np.asarray(a['whole_closed_hand_matrix_same_rod_angle']);G=np.asarray(a['source_true_grip'])
 path=[S-.15*(E-S),S]+[S+u*(E-S) for u in [.25,.5,.75,1]]+[E+u*(W-E) for u in [.25,.5,.75,1]]
 widths=[95,100,135,140,120,60,55,48,42,38] if role=='R' else [65,75,80,80,65,45,42,40,38,36]
 def mapped(q,i):
  if i==0:return at(U,q)
  if i==1:return at(UT,q)
  if i<5:return at(U,q)
  if i==5:return .5*at(U,q)+.5*at(F,q)
  along=float(np.dot(np.asarray(q)-E,W-E)/np.dot(W-E,W-E));remain=(1-along)*np.linalg.norm(W-E);start,end=(95.,55.) if role=='L' else (70.,35.)
  blend=smooth((start-remain)/(start-end));return (1-blend)*at(F,q)+blend*at(Hand,q)
 srcRows=[];dstRows=[]
 for i,c in enumerate(path):
  tangent=np.asarray(path[min(i+1,len(path)-1)])-np.asarray(path[max(i-1,0)]);tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]])
  row=[c-widths[i]*normal,c+widths[i]*normal];srcRows.append(row);dstRows.append([mapped(q,i) for q in row])
 v=G-W;u=((X-W[0])*v[0]+(Y-W[1])*v[1])/np.dot(v,v);hd=np.abs((X-W[0])*v[1]-(Y-W[1])*v[0])/np.linalg.norm(v)
 handMask=masks[role]&(u>=(-.55 if role=='L' else -.4))&(hd<95)
 layer=np.zeros_like(B);layer[masks[role]&~handMask]=B[masks[role]&~handMask];source=Image.fromarray(layer);out=Image.new('RGBA',(1024,1536));ratios=[]
 for i in range(len(path)-1):
  for tri in [[(i,0),(i,1),(i+1,1)],[(i,0),(i+1,1),(i+1,0)]]:
   ratio=triangle(source,[srcRows[j][k] for j,k in tri],[dstRows[j][k] for j,k in tri],out)
   if ratio is not None:ratios.append(ratio)
 hand=np.zeros_like(B);hand[handMask]=B[handMask];iv=np.linalg.inv(np.vstack([Hand,[0,0,1]]))[:2];whole=Image.fromarray(hand).transform((1024,1536),Image.Transform.AFFINE,tuple(iv.ravel()),Image.Resampling.BICUBIC);out.alpha_composite(whole);out.save(O/f'anatomy/F090_REAL086_{role}_COMPLETE_ARM_SEGMENT_MESH_REFERENCE.png');canvas.alpha_composite(out)
 meshQA[role]={'connected_triangles':len(ratios),'inverted_triangles':0,'min_positive_area_ratio':min(ratios),'whole_hand_and_bangle_rigid_with_rod':True,'source_pixel_only':True}
n=np.asarray(canvas).copy();n[fixed]=B[fixed];assert np.array_equal(n[fixed],B[fixed]);Image.fromarray(n).save(O/'anatomy/F090_COMPLETE_VISIBLE_PERSON_REFERENCE_ONLY.png')
fg0=np.asarray(Image.open(M/'layers/F086_FG_true_front_fingers.png').convert('RGBA'));own=np.zeros((1536,1024),bool)
for role in ['L','R']:
 a=fg0.copy();a[Y>=710 if role=='L' else Y<710]=0;Hmat=np.asarray(g['arms_actual_source_projected_proxies_not_hidden_bones'][role]['whole_closed_hand_matrix_same_rod_angle']);iv=np.linalg.inv(np.vstack([Hmat,[0,0,1]]))[:2];own|=np.asarray(Image.fromarray(a).transform((1024,1536),Image.Transform.AFFINE,tuple(iv.ravel()),Image.Resampling.BICUBIC))[:,:,3]>0
fg=np.zeros_like(n);fg[own]=n[own];bg=n.copy();bg[own]=0;Image.fromarray(bg).save(O/'anatomy/F090_REFERENCE_BG.png');Image.fromarray(fg).save(O/'anatomy/F090_REFERENCE_TRUE_FRONT_GRIPS.png');assert np.array_equal(np.maximum(bg,fg),n)
master=np.zeros_like(B);master[fixed]=B[fixed];Image.fromarray(master).save(O/'anatomy/FINAL086_TRUE_FIXED_SUPPORT_MASTER_NATIVE.png')
for name,a in [('F090_COMPLETE_ACTIVITY_HEAD_BODY_ARMS_THIGHS_FULL_KNEES_FOLDS',active),('REAL086_SHINS_ANKLES_SHOES_AND_BLANK_FIXED',fixed),('REAL_ORIGINAL_SHOES_ANKLES_SURROUNDING_EMPTY_HARD',feet)]:Image.fromarray(np.uint8(a)*255).save(O/f'masks/{name}.png')
write_views(O,R,M,g,B,n,bg,fg,active,fixed,feet,s,t)
g['reference_geometry_checks']['arm_mesh_reference_checks']=meshQA;g['reference_geometry_checks']['global_arm_TPS_used_in_final_reference']=False
(O/'geometry/F090_COMPLETE_PERSON_AND_RIGID_PROP_PLAN.json').write_text(json.dumps(g,indent=2)+'\n')
(O/'qa/CONNECTED_ARM_SEGMENT_MESH_REFERENCE_CHECKS.json').write_text(json.dumps({'status':'ALL_CONNECTED_ARM_TRIANGLES_POSITIVE_ORIENTATION','arms':meshQA,'model_calls':0,'actual090_full_Canvas':0,'person_is_source_pixel_reference_not_new_art':True},indent=2)+'\n')
print(json.dumps(meshQA,indent=2))
