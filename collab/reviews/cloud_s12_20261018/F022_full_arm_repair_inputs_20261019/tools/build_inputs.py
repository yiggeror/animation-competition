"""0-call repair input preparation. Existing raw pixels + construction + actual frozen prop readback."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import binary_dilation,map_coordinates
import numpy as np,json,hashlib,shutil
O=Path(__file__).resolve().parents[1];S=O.parent;R=S.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ['inputs','reference','geometry','prompts','requests']:(O/d).mkdir(exist_ok=True)
raw=S/'batch_F022_F030_production_20261019/originals/F022_raw_call01.png';props=S/'d03_F018_20261019/same_raw_fix_20261019/actual_scene/F018_code_props_actual_layer.png';canvas=S/'d03_F018_20261019/same_raw_fix_20261019/actual_scene/F018_canvas.png';prev=S/'d03_F018_20261019/same_raw_fix_20261019/candidate/F018.png'
assert sha(raw)=='938682ddf40b13e6b72dbacbabedf9502ae73bba79944b330aae6a3bedb26234';assert sha(canvas)=='46f97711aff0b9451ba72d5a413e4b42cfa6583853d9999657e12f80bb78f001';shutil.copyfile(raw,O/'inputs/01_FAILED_F022_unique_source.png')
a=np.array(Image.open(raw));pr=np.array(Image.open(props));photo=np.array(Image.open(canvas).convert('RGB'));H,W=a.shape[:2];yy,xx=np.indices((H,W));native=np.stack([xx+.5,yy+.5],2);Eold=np.array([770.,836.]);Wold=np.array([901.,877.]);axis=(Wold-Eold)/np.linalg.norm(Wold-Eold);u=(native-Eold)@axis
core=(a[:,:,3]>=8)&(xx>=742)&(yy>=778)&(yy<934)&(u>=-16);reference_solid=(a[:,:,3]>=128)&(xx>=740)&(yy>=778)&(yy<936)&(u>=-18);physical=binary_dilation(reference_solid,structure=np.ones((3,3),bool),iterations=1)&(a[:,:,3]>0)&(xx>=740)&(yy<936)&(u>=-18)
# Actual complete distal group: elbow continuation, forearm, jade, wrist, palm and ALL digits move together.
alpha=a[:,:,3].astype(float)/255*physical;prem=a[:,:,:3].astype(float)/255*alpha[:,:,None]
thumbim=Image.new('L',(W,H));ImageDraw.Draw(thumbim).polygon([(933,887),(956,884),(973,888),(985,897),(984,915),(967,921),(945,912),(931,901)],fill=255);thumb=(np.array(thumbim)>0)&physical
As=np.array([934.312497676,785.129739577]);Bs=np.array([1497.531490504,714.664205296]);LAs=np.array([951.261694392,798.906335746]);LBs=np.array([1282.198690556,773.946794448]);U=(Bs-As)/np.linalg.norm(Bs-As);N=np.array([-U[1],U[0]]);reg=np.array([275.,112.]);T=np.array([975.093564,952.418887]);G=np.array([975.714286,957.380208]);py,px=np.nonzero(thumb);points=np.stack([px+.5,py+.5],1);idx=np.argmax(points@N);source_support=points[idx]+.5*np.sign(N)
# Contact is checked against the EXISTING rasterized shaft alpha, never just a 7px formula.
wy,wx=np.indices((1080,1920));world=np.stack([wx+.5,wy+.5],2)
def rodmask(A,B):
 v=B-A;t=np.clip(((world-A)@v)/(v@v),0,1);return (pr[:,:,3]>0)&(np.linalg.norm(world-(A+t[:,:,None]*v),axis=2)<5.5)&(wx>=925)&(wx<=1000)
rod=rodmask(As,Bs);lower=rodmask(LAs,LBs);ry,rx=np.nonzero(rod);rpoints=np.stack([rx,ry],1);ly,lx=np.nonzero(lower);lpoints=np.stack([lx,ly],1)
# Sample original alpha directly into a small scene ROI for contact placement.
ys,xs=np.indices((90,100));scene_coords=np.stack([xs+900.5,ys+720.5],2)
def alpha_roi(delta,exclude_thumb=False):
 src=(scene_coords-reg)/.7-delta;arr=alpha*(~thumb if exclude_thumb else 1);return np.rint(np.clip(map_coordinates(arr,[src[:,:,1]-.5,src[:,:,0]-.5],order=1,mode='constant',cval=0),0,1)*255).astype(np.uint8)
def rastergap(mask,rp):
 y,x=np.nonzero(mask);p=np.stack([x+900,y+720],1);dd=np.maximum(abs(p[:,None,:]-rp[None,:,:])-1,0);dist=np.sqrt(np.sum(dd*dd,2));i,j=np.unravel_index(np.argmin(dist),dist.shape);return float(dist[i,j]),p[i].tolist(),rp[j].tolist()
# Solve rotation AND XY jointly; pin the visible thumb to actual top-raster edge.
# Thumb AA may blend over the shaft at contact; other fingers' ALL alpha stay clear.
allpix=np.stack([xs.ravel()+900,ys.ravel()+720],1)
def distance_field(rp):
 dd=np.maximum(abs(allpix[:,None,:]-rp[None,:,:])-1,0);ds=np.sum(dd*dd,2);ii=np.argmin(ds,axis=1);return np.sqrt(ds[np.arange(len(ii)),ii]).reshape(90,100)
upper_field=distance_field(rpoints);lower_field=distance_field(lpoints);rodlocal=np.zeros((90,100),bool)
for x,y in rpoints:
 if 900<=x<1000 and 720<=y<810:rodlocal[y-720,x-900]=True
edgeabove=np.zeros_like(rodlocal);edgeabove[:-1]=rodlocal[1:];edgeabove&=~rodlocal
T_scene=T*.7+reg;target_columns=(xs+900>=np.floor(T_scene[0]))&(xs+900<=np.ceil(T_scene[0]))
visible_thumb=thumb&(a[:,:,3]>=128);vy,vx=np.nonzero(visible_thumb);vpoints=np.stack([vx+.5,vy+.5],1)
chosen=None;debug=[]
for degrees in np.arange(0.,8.01,.5):
 th=np.deg2rad(degrees);rotation=np.array([[np.cos(th),np.sin(th)],[-np.sin(th),np.cos(th)]])
 rotated=(vpoints-Wold)@rotation.T+Wold;vispoint=rotated[np.argmax(rotated@N)]+.5*np.sign(N);dx=float(T[0]-vispoint[0]);base=float(T[1]-vispoint[1])
 def alpha_roi(delta,exclude_thumb=False):
  q=(scene_coords-reg)/.7-delta;src=(q-Wold)@rotation+Wold;arr=alpha*(~thumb if exclude_thumb else 1);return np.rint(np.clip(map_coordinates(arr,[src[:,:,1]-.5,src[:,:,0]-.5],order=1,mode='constant',cval=0),0,1)*255).astype(np.uint8)
 for dy in np.arange(base-2.8,base+2.81,.05):
  delta=np.array([dx,dy]);ar=alpha_roi(delta);visible=ar>=128;other=alpha_roi(delta,True)>0;contact=visible&edgeabove&target_columns
  if not contact.any() or np.any(visible&rodlocal):continue
  og=float(upper_field[other].min());lg=float(lower_field[ar>0].min());Et=(Eold-Wold)@rotation.T+Wold+delta
  debug.append({'deg':float(degrees),'d':delta.tolist(),'nonthumb':og,'lower':lg,'upper_projection':float(np.linalg.norm(Et-np.array([644.,684.])))});
  if og>=3 and lg>=3 and np.linalg.norm(Et-np.array([644.,684.]))<.86*293:
   cy,cx=np.nonzero(contact);chosen=(delta,ar,og,lg,[int(cx[0]+900),int(cy[0]+720)],[int(cx[0]+900),int(cy[0]+721)],rotation,degrees,int(np.count_nonzero((ar>0)&rodlocal)));break
 if chosen is not None:break

if chosen is None:
 d0=max([d for d in debug if d['deg']==0.],key=lambda d:d['nonthumb']);rotation=np.eye(2);delta=np.array(d0['d']);oo=alpha_roi(delta,True)>0;i=np.argmin(np.where(oo,upper_field,np.inf));iy,ix=np.unravel_index(i,oo.shape);q=np.array([ix+900.5,iy+720.5]);p0=(q-reg)/.7-delta;px0,py0=np.rint(p0-.5).astype(int);print(json.dumps({'source_of_nearest_non_thumb':p0.tolist(),'world_point':q.tolist(),'source_RGBA':a[py0,px0].tolist(),'classified_thumb':bool(thumb[py0,px0]),'gap':d0['nonthumb']},indent=2))
assert chosen is not None,'No visible-thumb tangent + other-AA-clear proposal.'
delta,small,othergap,lgap,hp,rp,rotation,degrees,thumb_AA_overlap=chosen;gap=0.

def sample_group(size,scene=False):
 h,w=size[1],size[0];y,x=np.indices((h,w));q=np.stack([x+.5,y+.5],2);q0=(q-reg)/.7-delta if scene else q-delta;p=(q0-Wold)@rotation+Wold;co=[p[:,:,1]-.5,p[:,:,0]-.5];al=np.clip(map_coordinates(alpha,co,order=1,mode='constant',cval=0),0,1);rgb=np.stack([map_coordinates(prem[:,:,ch],co,order=1,mode='constant',cval=0) for ch in range(3)],2);out=np.zeros((h,w,4),np.uint8);out[:,:,3]=np.rint(al*255);out[:,:,:3]=np.clip(np.rint(np.divide(rgb,al[:,:,None],out=np.zeros_like(rgb),where=al[:,:,None]>1e-10)*255),0,255);return Image.fromarray(out)
target_group=sample_group((1024,1536));world_group=sample_group((1920,1080),True);E=(Eold-Wold)@rotation.T+Wold+delta;Wn=Wold+delta;C=np.array([711.,801.]);Spt=np.array([644.,684.]);L1=.86*293;L2=.64*293;Ez=float(np.sqrt(L1**2-np.sum((E-Spt)**2)));fore_proj=float(np.linalg.norm(Wn-E));assert fore_proj<L2
# Explicit full-arm editable region: real far sleeve plus old/new complete arm corridor.
edit=Image.new('L',(1024,1536));ed=ImageDraw.Draw(edit);sleeve=[(603,635),(645,657),(692,703),(729,740),(729,779),(690,816),(634,843),(594,821),(591,766)];ed.polygon(sleeve,fill=255)
for A,B,width in [(Spt,C,66),(C,E,66),(E,Wn,56)]:ed.line([tuple(A),tuple(B)],fill=255,width=width)
motion=(np.array(target_group)[:,:,3]>0)|physical|(np.array(edit)>0);editarr=binary_dilation(motion,iterations=10);near=Image.new('L',(1024,1536));nd=ImageDraw.Draw(near);nd.polygon([(436,663),(482,644),(524,648),(560,677),(578,736),(588,808),(596,869),(580,887),(446,890),(432,813),(426,728)],fill=255);defs=json.loads((S/'d01_F000/same_raw_fix_20261019/qa/source_and_region_definitions.json').read_text());nd.polygon([tuple(p) for p in defs['skin_polygons_native'][1]],fill=255);nd.polygon([tuple(p) for p in defs['skin_polygons_native'][0]],fill=255);nearprotected=np.array(near)>0;nearprotected[:648]=True;editarr&=~nearprotected;Image.fromarray(editarr.astype(np.uint8)*255).save(O/'inputs/full_far_arm_edit_domain_GUIDE.png')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n);BG=(238,241,241);INK=(33,51,66)
def capsule(draw,A,B,r0,r1):
 v=B-A;v/=np.linalg.norm(v);n=np.array([-v[1],v[0]]);draw.polygon([tuple(A+n*r0),tuple(B+n*r1),tuple(B-n*r1),tuple(A-n*r0)],fill=(107,181,210),outline=INK,width=1)
 for p,r in [(A,r0),(B,r1)]:draw.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=(107,181,210),outline=INK,width=1)
 for t in [.3,.65]:
  p=A+t*(B-A);r=r0+t*(r1-r0);draw.ellipse((p[0]-r,p[1]-r*.24,p[0]+r,p[1]+r*.24),outline=(222,239,244))
arm=Image.new('RGBA',(1024,1536),(0,0,0,0));d=ImageDraw.Draw(arm);capsule(d,Spt,C,30,27);capsule(d,C,E,27,29);arm=Image.alpha_composite(arm,target_group)
# Real distal source pixels receive ONE rigid rotation plus XY translation, no thumb deformation.
props_native=Image.open(props).convert('RGBA').transform((1024,1536),Image.Transform.AFFINE,(.7,0,275,0,.7,112),Image.Resampling.BILINEAR)
plate=Image.alpha_composite(Image.new('RGBA',(1024,1536),(*BG,255)),arm);plate=Image.alpha_composite(plate,props_native);d=ImageDraw.Draw(plate);contour=editarr&binary_dilation(~editarr,iterations=1);ov=np.zeros((1536,1024,4),np.uint8);ov[contour]=[203,68,89,220];plate=Image.alpha_composite(plate,Image.fromarray(ov));d=ImageDraw.Draw(plate)
for p,name in [(Spt,'S hidden'),(C,'CUFF'),(E,'E target'),(Wn,'W target')]:d.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill='white',outline=INK);d.text((p[0]-35,p[1]-22),name,font=font(13),fill=INK)
d.rectangle((0,0,1024,135),fill=BG);d.text((20,18),'F022 FULL-ARM REPAIR / PREPOSITION DIAGNOSTIC',font=font(24),fill=INK);d.text((20,57),'NOT FINAL ART / no generator call / source hand remains full size',font=font(19),fill=(159,47,44));d.text((20,93),'Red boundary = editable whole far arm. Elsewhere comes ONLY from failed022.',font=font(17),fill=INK)
d.rectangle((0,1390,1024,1536),fill=BG)
for j,line in enumerate(['Native1024x1536 / .70+(275,112) fixed','Blue upper chain = volume to redraw; real distal pixels = position/shape guide','Whole distal group rotates/translates together; contact XY solved, not old-elbow hard-spin','Final output must be a COMPLETE FAR-ARM PATCH; rest transparent.']):d.text((20,1407+j*29),line,font=font(17),fill=INK)
plate.convert('RGB').save(O/'reference/target_native_full_arm_DIAGNOSTIC.png')
board=Image.new('RGB',(1600,1536),BG);board.paste(plate.convert('RGB'),(0,0));d=ImageDraw.Draw(board);d.line((1024,0,1024,1536),fill=(175,188,197),width=2);d.text((1040,22),'REAL RAW HAND / TARGET CONTACT',font=font(21),fill=INK);detail=plate.convert('RGB').crop((815,850,1024,1010)).resize((556,426),Image.Resampling.NEAREST);board.paste(detail,(1035,76))
lines=['Same raw022 hand shape and scale1.0.','ALL digits/wrist/jade/forearm move as1 rigid group.','No single-thumb pull or palm shrink.','Upper rod pixels read from frozen actual layer.','VISIBLE thumb touches actual outer rod raster.','Other digits/palm and lower rod keep real air.','Blue sleeve/upper arm must be redrawn','from fixed shoulder to the NEW elbow.','The OLD elbow is not the rotation pivot.','RED GUIDE = full editable far-arm region.','Outside it: exactly copy Image1 identity/material.','No full-body regeneration or extra old018 image.']
for j,line in enumerate(lines):d.text((1042,535+j*36),line,font=font(16),fill=INK)
masksmall=Image.fromarray(editarr.astype(np.uint8)*255).resize((256,384));board.paste(masksmall,(1044,1025));d.text((1314,1070),'WHITE = far arm',font=font(15),fill=INK);d.text((1314,1102),'guide only;',font=font(15),fill=INK);d.text((1314,1134),'NOT an API mask',font=font(15),fill=INK);d.text((1043,1452),'Reference composite only. Repaired artwork does not yet exist.',font=font(15),fill=(159,47,44));board.save(O/'inputs/02_full_arm_target_CONTACT_DIAGNOSTIC.png')
# Actual props/box context: right region copied from actualCanvas where no old person exists.
# Left shaft comes from actual cached propRGBA, so no second full018 character can compete.
context=Image.new('RGBA',(1920,1080),(*BG,255));context.paste(Image.open(canvas).convert('RGBA').crop((1000,0,1920,1080)),(1000,0));leftprops=Image.open(props).convert('RGBA');la=np.array(leftprops);la[:,1000:,3]=0
arm_world=arm.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BILINEAR);# ensure photo group has direct one-pass projection
upper_only=Image.new('RGBA',(1024,1536),(0,0,0,0));du=ImageDraw.Draw(upper_only);capsule(du,Spt,C,30,27);capsule(du,C,E,27,29);arm_world=Image.alpha_composite(upper_only.transform((1920,1080),Image.Transform.AFFINE,(1/.7,0,-275/.7,0,1/.7,-112/.7),Image.Resampling.BILINEAR),world_group)
context=Image.alpha_composite(context,arm_world);context=Image.alpha_composite(context,Image.fromarray(la));d=ImageDraw.Draw(context);d.rectangle((0,0,1920,125),fill=BG);d.text((24,20),'DIAGNOSTIC ONLY: ACTUAL FROZEN BOX / CRANE / RODS + PROPOSED ARM',font=font(29),fill=INK);d.text((24,67),'NOT A COMPLETED FRAME. No old018 person included. Raw022 distal pixels prepositioned; blue chain is construction.',font=font(21),fill=(159,47,44));d.text((30,1016),'No prop shift / no lift. Body down. Thumb only.',font=font(20),fill=INK);context.convert('RGB').save(O/'inputs/03_actual_props_target_arm_DIAGNOSTIC.png')
context.convert('RGB').crop((870,710,1000,830)).resize((780,720),Image.Resampling.NEAREST).save(O/'reference/actual_props_thumb_contact_DIAGNOSTIC6x.jpg',quality=96)
# Temporal018 is reference-only and NOT among the actual generator inputs.
comp=Image.new('RGB',(1800,625),BG);d=ImageDraw.Draw(comp)
for j,(p,label) in enumerate([(prev,'LOCKED018 TIME PREVIOUS ONLY'),(raw,'FAILED022'),(None,'PROPOSED022 CONTACT ONLY')]):
 im=Image.open(p).convert('RGBA') if p else arm;flat=Image.alpha_composite(Image.new('RGBA',(1024,1536),(*BG,255)),im).convert('RGB');tile=flat.crop((630,690,1024,1080)).resize((591,585));comp.paste(tile,(j*600+4,35));d.text((j*600+8,7),label,font=font(17),fill=INK)
comp.save(O/'reference/temporal_018_to_target_NOT_A_TOOL_INPUT.jpg',quality=95)
# Check the original box/cloth/crane region is really unchanged in the diagnostic.
assert np.array_equal(np.array(context.convert('RGB'))[447:1058,1000:1860],photo[447:1058,1000:1860])
assert not np.any((np.array(target_group)[:,:,3]>=128)&nearprotected)
yb,xb=np.nonzero(np.array(target_group)[:,:,3]>=128);right_margin=int(1023-xb.max());assert right_margin>=3
# Keep only compact facts; these are source-pixel planning results, not a certified new F022.
facts={'state':'REPAIR_INPUT_ONLY_NOT_GENERATED','source_failed022_SHA256':sha(raw),'reference_alpha_rule':'Unchanged RGB and all source alpha>=128 kept; only reference-preview sub128 fringe farther than one8-neighbour native pixel from visible body is omitted. Raw022 itself is untouched. This avoids treating near-invisible alpha4 halos as contact.','source_actual_prop_RGBA_path':str(props.relative_to(R)),'source_actual_prop_RGBA_SHA256':sha(props),'source_actualCanvas_SHA256':sha(canvas),'actual_prop_box_region_kept_xyxy':[1000,447,1860,1058],'distal_group_XY_translation_native':delta.tolist(),'distal_group_scale':1.,'distal_group_rotation_about_wrist_deg':float(degrees),'all_palm_digits_jade_forearm_same_transform':True,'single_thumb_transform':False,'native_visible_right_margin_px':right_margin,'near_right_arm_and_head_neck_protected_from_edit_domain':True,'actual_box_cloth_crane_region_RGB_byte_equal':True,'S_hidden_native':Spt.tolist(),'source_E_estimate_native':Eold.tolist(),'target_E_native':E.tolist(),'source_W_estimate_native':Wold.tolist(),'target_W_native':Wn.tolist(),'new_cuff_native':C.tolist(),'upper_length_depth_proxy_native':L1,'upper_target_depth_proxy':Ez,'forearm_projection_length_preserved_native':fore_proj,'nominal_T_SURFACE_native':T.tolist(),'nominal_G_AXIS_native':G.tolist(),'proposed_group_against_actual_prop_raster':{'visible_thumb_contour_pixel_box_gap_scene':gap,'visible_thumb_overlap_pixels':0,'thumb_contact_AA_overlap_pixels':thumb_AA_overlap,'thumb_contact_group_pixel_scene':hp,'upper_rod_pixel_scene':rp,'all_non_thumb_pixels_min_air_scene':othergap,'lower_rod_all_group_min_air_scene':lgap},'old018_in_actual_tool_inputs':False,'imagegen_calls':0,'scene_renders':0,'F026_F030_still_blocked':True}
(O/'geometry/repair_target.json').write_text(json.dumps(facts,indent=2)+'\n');print(json.dumps(facts,indent=2))
