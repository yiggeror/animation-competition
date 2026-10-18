from pathlib import Path
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,binary_erosion
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parent;G=R/'F030_input_gate';P=R/'F030_same_raw_semantic_v6';src=P/'candidates/F030_projected_forearm_UNCLEAN_DIAGNOSTIC_RGBA.png';assert hashlib.sha256(src.read_bytes()).hexdigest()=='6a5f8f2b56acebd7ad62dcc0001c145c5146b5154fc5e2a3eb32a803ff81ca45';a=np.array(Image.open(src).convert('RGBA'));v=a.astype(float);H,W=a.shape[:2];Y,X=np.mgrid[:H,:W]
def load(p):return np.array(Image.open(p).convert('L'))>0
def poly(p):
 m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(p,fill=255);return np.array(m)>0
def ramp(x,l,h):return np.clip((x-l)/(h-l),0,1)
near=load(G/'masks/F030_near_whole_transformed_hand_footprint.png');far=load(G/'masks/F030_far_hand_jade_TRUE_ALPHA0_SEAT_guard.png');box=load(G/'masks/F030_fixed_table_box_guard.png');neararm=load(P/'masks/projected_near_forearm_actual_alpha.png');guards=near|far|box
r,g,b=v[:,:,0],v[:,:,1],v[:,:,2];opaque=ramp(v[:,:,3],220,252)
skin=ramp(r,165,215)*ramp(r-g,16,30)*ramp(g-b,8,20)*ramp(100-(r-g),0,18)*opaque
head=skin*((X>=735)&(X<=1015)&(Y>=400)&(Y<=735));head[guards]=0
farregion=poly([(973,834),(1022,803),(1081,789),(1161,798),(1183,845),(1094,899),(1050,910),(1000,881)])
fararm=skin*farregion;fararm[guards|neararm]=0
blue=ramp(b-r,25,55)*ramp(b-g,16,34)*ramp(g,58,95)*ramp(205-r,0,30)*opaque*(Y>600);blue[guards]=0
hairregion=poly([(665,305),(929,285),(1008,356),(1010,477),(967,514),(908,510),(857,510),(795,537),(744,534),(680,519)])
gray=ramp(27-(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])),0,10)*ramp(np.minimum.reduce([r,g,b]),85,130)*ramp(245-np.maximum.reduce([r,g,b]),0,25)*opaque
hair=gray*hairregion*np.clip((535-Y)/40,0,1);hair[guards]=0
mat=[('head_ear_neck_skin',head,(0,6,11)),('far_arm_skin',fararm,(0,5,9)),('blue_blouse',blue,(6,3,4)),('crown_gray_hair',hair,(2,3,3))]
out=v.copy();manifest=[];ov=np.zeros_like(a)
cols=[(250,80,80),(230,150,20),(30,220,100),(200,50,230)]
for (name,m,d),color in zip(mat,cols):
 # Smooth only inward; genuine ink, flowers, eye whites, alpha and protected hands do not enter.
 soft=gaussian_filter(m,.65);soft=np.minimum(soft,m);soft[guards]=0
 q=np.rint(soft*255).astype('uint8');Image.fromarray(q).save(O/'masks'/f'{name}_SOFT.png');out[:,:,:3]+=soft[:,:,None]*np.array(d)
 ov[q>0,:3]=color;ov[q>0,3]=np.maximum(ov[q>0,3],(q[q>0]*.45).astype('uint8'));manifest.append({'name':name,'max_add_RGB':d,'affected_soft_domain_pixels':int((q>0).sum()),'mask':str(O/'masks'/f'{name}_SOFT.png')})
out=np.rint(out).clip(0,255).astype('uint8');out[:,:,3]=a[:,:,3];out[guards]=a[guards];dest=O/'candidates/S08_F030_whole_turn_same_raw_final_color_RGBA.png';Image.fromarray(out).save(dest)
for tag,c in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 z=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.fromarray(out));z.convert('RGB').save(O/'qa'/f'candidate_{tag}.png');z.crop((965,730,1115,855)).resize((900,750)).convert('RGB').save(O/'qa'/f'wrist_{tag}.png');z.crop((650,640,1320,1015)).resize((1340,750)).convert('RGB').save(O/'qa'/f'whole_arm_{tag}.png')
 old=Image.alpha_composite(Image.new('RGBA',(W,H),c),Image.open('/workspace/scratch/f060b5601755/astra_s08_f027_parallel_20261018_1812/F027_FINAL_LOCKED/S08_F027_grandma_match_box_RGBA.png').convert('RGBA'));panel=Image.new('RGB',(1620,800),c[:3]);panel.paste(old.crop((530,280,1340,1080)).convert('RGB'),(0,0));panel.paste(z.crop((530,280,1340,1080)).convert('RGB'),(810,0));panel.save(O/'qa'/f'F027_F030_same_scale_{tag}.png')
 z.alpha_composite(Image.fromarray(ov));z.crop((550,285,1310,1080)).convert('RGB').save(O/'qa'/f'material_soft_masks_{tag}.png')
ch=np.any(out!=a,2);checks={'status':'FINAL_COLOR_CANDIDATE_PENDING_DUAL_REVIEW','source_shape_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'alpha_changed':int(np.any(out[:,:,3]!=a[:,:,3])),'fixed_hand_match_jade_seat_box_changed':int((ch&guards).sum()),'near_arm_changed':int((ch&neararm).sum()),'material_masks':manifest,'hair_bun_lower_shadow':'No correction belowY535; natural changed shadow preserved, not forced to crown or lit mean.'};(O/'geometry/color_masks_and_checks.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
