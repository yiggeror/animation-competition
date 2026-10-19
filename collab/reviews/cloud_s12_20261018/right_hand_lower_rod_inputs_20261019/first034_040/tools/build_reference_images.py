from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy.spatial import Delaunay
from scipy.ndimage import map_coordinates,binary_dilation
ROOT=Path.cwd();P=Path('collab/reviews/cloud_s12_20261018');U=P/'right_hand_lower_rod_inputs_20261019';O=U/'first034_040';M=P/'F030_close_grip_from_locked026_20261019';S=P/'F022_full_arm_repair_20261019/uniform_map_rejoin_20261019'
for d in ['reference','inputs','geometry','prompts','requests','provenance','tools','masks','code_props','anatomy']:(O/d).mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=Image.open(M/'candidate/F030.png').convert('RGBA');B=np.array(b);H,W=B.shape[:2];OUT=(1120,1536)
shutil.copyfile(M/'candidate/F030.png',O/'reference/LOCKED_ACTUAL030_UNIQUE_MOTHER.png');master=json.loads((O/'geometry/first034_040_geometry.json').read_text());master['states']=master['states'][:2];master['status']='FIRST034_040_ONLY_INPUT_CANDIDATES_0_IMAGEGEN';(O/'geometry/first034_040_geometry.json').write_text(json.dumps(master,ensure_ascii=False,indent=2)+'\n')
for n in ['F030_actual_code_props.png','F034_actual_code_props.png','F040_actual_code_props.png','background_box_cloth_UNCHANGED.png','box_front_UNCHANGED.png','crane_only_UNCHANGED.png']:
 if not (O/'code_props'/n).exists():shutil.copyfile(U/'code_prop_reference'/n,O/'code_props'/n)
fg0=np.array(Image.open(M/'layers/F030_FG_actual_three_and_fixed_index.png').convert('RGBA'));far0=np.array(Image.open(S/'candidate/F022_far_arm_exclusive.png').convert('RGBA'))[:,:,3]>0;far0|=fg0[:,:,3]>0;far0&=B[:,:,3]>0;near0=np.array(Image.open(S/'masks/near_right_arm_protection.png'))>0;near0&=~far0;near0&=B[:,:,3]>0
F=np.zeros_like(B);N=np.zeros_like(B);F[far0]=B[far0];N[near0]=B[near0];BODY=B.copy();BODY[far0|near0]=0;assert np.array_equal(np.maximum(np.maximum(F,N),BODY),B);assert not np.any((F[:,:,3]>0)&(N[:,:,3]>0))
for n,a in [('actual030_far_arm_RGBA.png',F),('actual030_near_arm_RGBA_NO_JADE.png',N),('actual030_static_body_RGBA.png',BODY)]:Image.fromarray(a,'RGBA').save(O/'reference'/n)
Image.fromarray(np.uint8(far0)*255).save(O/'masks/source030_far_ownership.png');Image.fromarray(np.uint8(near0)*255).save(O/'masks/source030_near_ownership.png')
font=lambda s:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',s)
def pad(im):
 a=Image.new('RGBA',OUT);a.alpha_composite(im);return a
body=pad(Image.fromarray(BODY,'RGBA'));ba=np.array(body);gray=np.array(ImageOps.grayscale(body.convert('RGB')));ba[:,:,:3]=np.stack([gray]*3,axis=2);ba[:,:,3]=np.uint8(ba[:,:,3].astype(float)*.25);ghost=Image.fromarray(ba,'RGBA')
def uv(v):return v/(np.linalg.norm(v) or 1)
def normal(v):
 v=uv(v);return np.array([-v[1],v[0]])
def rigid(im,mat):
 A=np.array(mat)[:,:2];t=np.array(mat)[:,2];iv=np.linalg.inv(A);q=-iv@t;return im.transform(OUT,Image.Transform.AFFINE,tuple(iv[0])+(q[0],)+tuple(iv[1])+(q[1],),Image.Resampling.BICUBIC)
def warp_arm(a,S0,E0,W0,St,Et,Wt,mat,far=False):
 S0,E0,W0,St,Et,Wt=map(lambda x:np.array(x,float),[S0,E0,W0,St,Et,Wt]);A=np.array(mat)[:,:2];t=np.array(mat)[:,2];handv=uv(np.array([975.7142857,957.3802078])-W0)if far else uv(np.array([820.,986.])-W0);hu=uv(E0-S0);ht=uv(Et-St)
 sc=[S0-hu*90,S0,S0+.65*(E0-S0),E0,E0+.55*(W0-E0),W0-uv(W0-E0)*45,W0+handv*5]
 tc=[St-ht*90,St,St+.65*(Et-St),Et,Et+.55*(Wt-Et),Wt-uv(Wt-Et)*45*np.linalg.norm(Wt-Et)/np.linalg.norm(W0-E0),A@sc[6]+t]
 sn=[normal(E0-S0)]*3+[normal(uv(E0-S0)+uv(W0-E0)),normal(W0-E0),normal(W0-E0),normal(handv)]
 tn=[normal(Et-St)]*3+[normal(uv(Et-St)+uv(Wt-Et)),normal(Wt-Et),normal(Wt-Et),A@sn[6]]
 widths=([85,90,70,48,34,29,29]if far else[110,110,80,66,43,33,33]);src=[];dst=[]
 for c,z,n,q,w in zip(sc,tc,sn,tn,widths):
  for sign in [-1,0,1]:src.append(c+sign*n*w);dst.append(z+sign*q*w)
 src=np.array(src);dst=np.array(dst);tri=Delaunay(dst);y,x=np.mgrid[:H,:W];along=(x-W0[0])*handv[0]+(y-W0[1])*handv[1];threshold=-8 if far else -12;arm=a.copy();hand=a.copy();arm[along>=threshold+10]=0;hand[along<threshold]=0
 if far:
  jade=(a[:,:,1].astype(int)>a[:,:,0].astype(int)+15)&(a[:,:,1].astype(int)>a[:,:,2].astype(int)+5)&(a[:,:,3]>0)&(x>=842)&(x<900)&(y>=884)&(y<960);jade=binary_dilation(jade,iterations=3)
  hand[jade]=0;arm[jade]=a[jade]
 xmin=max(0,int(dst[:,0].min()-3));xmax=min(OUT[0],int(dst[:,0].max()+4));ymin=max(0,int(dst[:,1].min()-3));ymax=min(OUT[1],int(dst[:,1].max()+4));oy,ox=np.mgrid[ymin:ymax,xmin:xmax];pts=np.column_stack([ox.ravel(),oy.ravel()]);si=tri.find_simplex(pts);ok=si>=0;valid=pts[ok];ii=si[ok];bb=np.einsum('nij,nj->ni',tri.transform[ii,:2],valid-tri.transform[ii,2]);bb=np.column_stack([bb,1-bb.sum(axis=1)]);coords=np.einsum('ni,nij->nj',bb,src[tri.simplices[ii]])
 aa=arm.astype(float)/255;aa[:,:,:3]*=aa[:,:,3:4];vals=np.column_stack([map_coordinates(aa[:,:,k],[coords[:,1],coords[:,0]],order=1,mode='constant')for k in range(4)]);good=vals[:,3]>0;vals[good,:3]/=vals[good,3:4];res=np.zeros((OUT[1],OUT[0],4),np.uint8);res[valid[:,1],valid[:,0]]=np.uint8(np.clip(vals*255+.5,0,255));im=Image.fromarray(res,'RGBA');handim=rigid(Image.fromarray(hand,'RGBA'),mat);im=Image.alpha_composite(im,handim);return im,{'source_control_vertices':src.tolist(),'target_control_vertices':dst.tolist(),'distal_hand_rigid_matrix':mat,'hand_scale':1.0,'mirrored':False,'reference_only_not_drawing':True}
def plate(im):return im.transform((1024,1024),Image.Transform.AFFINE,(1/1.12,0,294.4/1.12,0,1/1.12,473.6/1.12),Image.Resampling.NEAREST)
def scene(im):return im.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BICUBIC)
metadata=[]
for state in master['states']:
 f=state['frame'];farD=state['far_arm_actual_native_estimates'];nearD=state['near_arm_actual_native_estimates'];fi,fd=warp_arm(F,[645,724],[713,887],[898,927],farD['S'],farD['E'],farD['W'],state['left_hand_native_rigid_matrix'],True)
 if f==34:ni=pad(Image.fromarray(N,'RGBA'));nd={'unchanged_actual030_near_arm':True,'hand_scale':1.,'mirrored':False}
 else:ni,nd=warp_arm(N,[495,725],[550,950],[735,998],nearD['S'],nearD['E'],nearD['W'],state['near_hand_native_rigid_matrix'])
 fi.save(O/f'anatomy/F{f:03}_full_far_arm_REFERENCE_ONLY.png');ni.save(O/f'anatomy/F{f:03}_full_near_arm_REFERENCE_ONLY.png');fv=rigid(Image.fromarray(fg0,'RGBA'),state['left_hand_native_rigid_matrix']);owns=np.array(fv)[:,:,3]>0;fa=np.array(fi);fg=np.zeros_like(fa);fg[owns]=fa[owns];rear=fa.copy();rear[owns]=0;assert np.array_equal(np.maximum(fg,rear),fa)
 target=Image.alpha_composite(ghost,fi);target=Image.alpha_composite(target,ni);target.save(O/f'anatomy/F{f:03}_full_target_guard_REFERENCE_ONLY.png');p=Image.new('RGBA',(1024,1024),'#e1e4e6');p.alpha_composite(plate(target));d=ImageDraw.Draw(p);d.text((20,16),f'F{f:03} FULL ARM TARGET / INPUT CANDIDATE / 0 IMAGEGEN',fill='#25313b',font=font(19));d.text((20,44),'Actual030 source pixels projected for anatomy; redraw complete chains, not these seams.',fill='#48535d',font=font(15));d.text((20,68),f'Left grip stays closed; upper handle rises{state["upper_handle_lift_scene"]}scene px. Crane remains cloth-supported.',fill='#25313b',font=font(15));d.line((852,104,852,1000),fill='#a75a55',width=2);d.text((860,112),'native',fill='#99423e',font=font(13));d.text((860,130),'x1024',fill='#99423e',font=font(13));d.text((20,986),'Original body stays low. Right hand has NO jade. No crane lift / no body rise.',fill='#25313b',font=font(15));p.convert('RGB').save(O/f'inputs/F{f:03}_01_complete_arm_target.png')
 ctx=Image.open(O/'code_props/background_box_cloth_UNCHANGED.png').convert('RGBA');ctx.alpha_composite(Image.open(M/'actual_scene/F030_native_ground_shadows_actual_layer.png').convert('RGBA'));ctx.alpha_composite(scene(body));ctx.alpha_composite(scene(Image.fromarray(rear,'RGBA')));ctx.alpha_composite(scene(ni));ctx.alpha_composite(Image.open(O/f'code_props/F{f:03}_actual_code_props.png').convert('RGBA'));ctx.alpha_composite(scene(Image.fromarray(fg,'RGBA')));ctx.alpha_composite(Image.open(O/'code_props/box_front_UNCHANGED.png').convert('RGBA'));ctx.convert('RGB').save(O/f'anatomy/F{f:03}_same_pose_actual_props_scene_REFERENCE.png')
 board=Image.new('RGB',(2880,1080),'#e1e4e6');board.paste(ctx.convert('RGB'),(0,0));dr=ImageDraw.Draw(board);dr.line((992,500,992,970),fill='#9e403d',width=3);dr.text((1000,920),'Native person edge x1024; guard is not usable canvas',fill='#7f2420',font=font(17));crop=ctx.crop((820,640,1040,860)).resize((880,880),Image.Resampling.NEAREST).convert('RGB');board.paste(crop,(1960,110));dr.text((20,20),f'F{f:03} SAME TARGET + ACTUAL RIG/RODS/BOX/CLOTH / REFERENCE ONLY',fill='#ffffff',font=font(26));dr.text((1960,20),'Same pose contact detail x4',fill='#25313b',font=font(24));dr.text((1960,55),'Upper held neck3 rod / lower body rod supported',fill='#25313b',font=font(16))
 # Clearly separate current palm estimate, future thumb surface and future grip axis.
 nearA=np.array(state['near_hand_native_rigid_matrix']);mp=nearA[:,:2]@np.array([820.,986.])+nearA[:,2];mp_scene=mp*.7+[275,112];T=np.array(state['right_thumb_nominal_surface_native'])*.7+[275,112];G=np.array(state['right_grip_candidate_scene']);labels=[('CURRENT MCP estimate',mp_scene,'#316f8a'),('FUTURE thumb surface T',T,'#b56b1f'),('FUTURE grip axis G',G,'#7b387c')]
 for j,(name,q,col)in enumerate(labels):
  x,y=q;dr.ellipse((x-4,y-4,x+4,y+4),outline=col,width=2);tx=1120;ty=900+j*30;dr.line((x,y,tx,ty+10),fill=col,width=2);dr.text((tx+5,ty),name,fill=col,font=font(18))
 gl=state['left_grip_scene'];dr.ellipse((gl[0]-5,gl[1]-5,gl[0]+5,gl[1]+5),outline='#2b9577',width=2);dr.text((1960,1020),'No right contact in034/040. G/T are future candidates, not MCP.',fill='#25313b',font=font(17));board.save(O/f'inputs/F{f:03}_02_same_pose_true_props_contact.png')
 # Proposed ownership masks are references, never approved production adoption.
 for name,im in [('far',fi),('near',ni)]:
  aa=np.array(im)[:,:,3]>0;Image.fromarray(np.uint8(aa)*255).save(O/f'masks/F{f:03}_candidate_new_{name}_footprint_GUARD.png')
 npg=np.array(ni)[:,:,3];fgp=np.array(fi)[:,:,3];green=(np.array(ni)[:,:,1].astype(int)>np.array(ni)[:,:,0].astype(int)+22)&(np.array(ni)[:,:,1].astype(int)>np.array(ni)[:,:,2].astype(int)+10)&(npg>=128);yn,xn=np.nonzero(npg);yf,xf=np.nonzero(fgp);metadata.append({'frame':f,'far_warp':fd,'near_warp':nd,'near_visible_bbox_guard':[int(xn.min()),int(yn.min()),int(xn.max()+1),int(yn.max()+1)],'far_visible_bbox_guard':[int(xf.min()),int(yf.min()),int(xf.max()+1),int(yf.max()+1)],'near_hand_not_mirrored':True,'near_jade_like_green_pixels':int(green.sum()),'all_near_pixels_inside_original_native_right_edge':bool(xn.max()<1024),'all_far_pixels_inside_original_native_right_edge':bool(xf.max()<1024),'far_reference_BG_FG_RGBA_union_exact':True,'moving_arms_source_pixel_reference_only_not_future_character_art':True})
# Same locked030 local identity/material patches, no alternate complete pose.
p=Image.new('RGB',(1024,1024),'#e1e4e6');d=ImageDraw.Draw(p);d.text((22,18),'INPUT3: ACTUAL030 LOCAL IDENTITY / CLOTH / NEAR SKIN ONLY',fill='#25313b',font=font(19));patches=[('NEAR ARM SKIN',(630,972,664,995),(70,130)),('ACTUAL PALM MATERIAL',(773,990,804,1010),(550,130)),('BLOUSE / FLOWER INK',(475,728,515,770),(70,560)),('IDENTITY HAIR / SKIN',(617,472,653,512),(550,560))]
for title,box,pos in patches:
 z=b.crop(box);g=Image.new('RGBA',z.size,'#e1e4e6');g.alpha_composite(z);p.paste(g.resize((360,360),Image.Resampling.NEAREST).convert('RGB'),pos);d.text((pos[0],pos[1]-30),title,fill='#25313b',font=font(18))
p.save(O/'inputs/03_actual030_local_material_identity.png');(O/'geometry/actual_source_reference_warps.json').write_text(json.dumps(metadata,indent=2)+'\n')
# Minimal whole comparison, actual captured prop context, source-art candidate arms.
a=Image.open(O/'anatomy/F034_same_pose_actual_props_scene_REFERENCE.png').convert('RGB').resize((960,540));c=Image.open(O/'anatomy/F040_same_pose_actual_props_scene_REFERENCE.png').convert('RGB').resize((960,540));out=Image.new('RGB',(1920,580),'#202426');out.paste(a,(0,40));out.paste(c,(960,40));d=ImageDraw.Draw(out);d.text((16,10),'F034 candidate: handle +28px / right unchanged',fill='white',font=font(20));d.text((976,10),'F040 candidate: handle +56px / right starts',fill='white',font=font(20));out.save(O/'034_040_overall_reference_comparison.jpg',quality=95)
print(json.dumps({'actual_first_inputs_created':[str(O/f'inputs/F{f:03}_01_complete_arm_target.png')for f in [34,40]],'near_far_bboxes':[{'frame':x['frame'],'near':x['near_visible_bbox_guard'],'far':x['far_visible_bbox_guard'],'right_native_edge_ok':x['all_near_pixels_inside_original_native_right_edge']and x['all_far_pixels_inside_original_native_right_edge']}for x in metadata],'imagegen_calls':0}))
