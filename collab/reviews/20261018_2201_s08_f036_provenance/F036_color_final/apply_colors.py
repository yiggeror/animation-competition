from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,binary_erosion
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F036_input_gate';P=R/'F036_same_raw_semantic_v9';src=P/'candidates/S08_F036_same_raw_semantic_RGBA.png';assert hashlib.sha256(src.read_bytes()).hexdigest()=='32f9ab00d6679f2594de9da6cf0c0744a26c8ae60976934624d941c0c1c8c186';a=np.array(Image.open(src).convert('RGBA'));v=a.astype(float);H,W=a.shape[:2];Y,X=np.mgrid[:H,:W]
def load(p):return np.array(Image.open(p).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def ramp(x,l,h):return np.clip((x-l)/(h-l),0,1)
near=load(G/'masks/F036_near_whole_transformed_hand_footprint.png');farfull=load(G/'masks/F036_far_original_underlying_full_hand_SEAT_footprint.png');farimage=np.array(Image.open(G/'inputs/F036_original_underlying_far_hand_SEAT_RGBA.png'));far=farfull&(farimage[:,:,3]>0);box=load(G/'masks/F036_fixed_table_box_guard.png');neararm=poly([(810,785),(883,766),(1002,851),(1206,791),(1262,818),(1244,879),(1086,941),(975,956),(924,934),(853,874)]);guards=near|far|box
r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];opaque=ramp(v[:,:,3],220,252)
skin=ramp(r,165,215)*ramp(r-g,16,30)*ramp(g-b,8,20)*ramp(100-(r-g),0,18)*opaque
head=skin*((X>=825)&(X<=1105)&(Y>=415)&(Y<=755))*ramp(g,180,196);head[guards]=0
blue=ramp(b-r,25,55)*ramp(b-g,16,34)*ramp(g,58,95)*ramp(205-r,0,30)*opaque*(Y>600);blue[guards]=0
hairregion=poly([(755,300),(1000,295),(1100,365),(1100,495),(1062,507),(1020,486),(981,492),(927,534),(899,573),(831,570),(757,533)])
gray=ramp(27-(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])),0,10)*ramp(np.minimum.reduce([r,g,b]),85,130)*ramp(245-np.maximum.reduce([r,g,b]),0,25)*opaque
face_gray_protection=poly([(892,576),(904,540),(930,508),(963,478),(993,447),(1018,433),(1045,434),(1060,454),(1072,488),(1108,511),(1110,750),(830,750),(830,580)])
hair=gray*hairregion*np.clip((560-Y)/40,0,1);hair[guards|face_gray_protection]=0
mat=[('head_ear_neck_skin',head,(0,5,6)),('blue_blouse',blue,(9,3,0)),('crown_gray_hair',hair,(2,2,1))]
out=v.copy();manifest=[];ov=np.zeros_like(a)
cols=[(250,80,80),(30,220,100),(200,50,230)]
for (name,m,d),color in zip(mat,cols):
 # Smooth only inward; genuine ink, flowers, eye whites, alpha and protected hands do not enter.
 soft=gaussian_filter(m,.65);soft=np.minimum(soft,m);soft[guards]=0
 if name!='blue_blouse':soft[neararm]=0
 q=np.rint(soft*255).astype('uint8');Image.fromarray(q).save(O/'masks'/f'{name}_SOFT.png');out[:,:,:3]+=soft[:,:,None]*np.array(d)
 ov[q>0,:3]=color;ov[q>0,3]=np.maximum(ov[q>0,3],(q[q>0]*.45).astype('uint8'));manifest.append({'name':name,'max_add_RGB':d,'affected_soft_domain_pixels':int((q>0).sum()),'mask':str(O/'masks'/f'{name}_SOFT.png')})
out=np.rint(out).clip(0,255).astype('uint8');out[:,:,3]=a[:,:,3];out[guards]=a[guards];dest=O/'candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 z=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));z.convert('RGB').save(O/'qa'/f'candidate_{tag}.png');z.crop((1080,715,1370,900)).resize((1160,740)).convert('RGB').save(O/'qa'/f'wrist_{tag}.png');z.crop((700,650,1400,1010)).resize((1400,720)).convert('RGB').save(O/'qa'/f'whole_arm_{tag}.png')
 old=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.open(str(R/'F033_FINAL_LOCKED/S08_F033_grandma_match_box_RGBA.png')).convert('RGBA'));panel=Image.new('RGB',(1700,800),c[:3]);panel.paste(old.crop((620,280,1470,1080)).convert('RGB'),(0,0));panel.paste(z.crop((620,280,1470,1080)).convert('RGB'),(850,0));panel.save(O/'qa'/f'F033_F036_same_scale_{tag}.png')
 z.alpha_composite(Image.fromarray(ov));z.crop((620,285,1400,1080)).convert('RGB').save(O/'qa'/f'material_soft_masks_{tag}.png')
ch=np.any(out!=a,2);checks={'status':'FINAL_COLOR_CANDIDATE_PENDING_DUAL_REVIEW','source_shape_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'alpha_changed':int(np.any(out[:,:,3]!=a[:,:,3])),'fixed_hand_match_jade_seat_box_changed':int((ch&guards).sum()),'broad_near_arm_ROI_changed':int((ch&neararm).sum()),'actual_near_arm_skin_changed':int((ch&neararm&(skin>0)).sum()),'near_arm_policy':'Both near upperarm and near forearm skin unchanged, including sleeve-root turning shadow. Broad envelope may contain blue cloth color correction.','material_masks':manifest,'hair_bun_lower_shadow':'No correction belowY560; natural bun/ear and narrow far-arm occlusion shadows retained, not forced to lit mean.'};(O/'geometry/color_masks_and_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
