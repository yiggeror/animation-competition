from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter,ImageFont
import numpy as np,math,json,hashlib
from scipy.ndimage import binary_fill_holes
P=Path('astra_s07_grandma_draw_20261018_1124');D=Path('astra_s07_f008_prepare_20261018_1249');raw=Image.open(D/'sources/F000_LOCKED_rgba.png').convert('RGBA');r=np.array(raw);W,H=raw.size;k=280/1024;yy,xx=np.indices((H,W))
def poly(pts):
 m=Image.new('L',(W*4,H*4));ImageDraw.Draw(m).polygon([(x*4,y*4) for x,y in pts],fill=255);return m.resize((W,H),Image.Resampling.LANCZOS)
def tf(im,M,T):
 iv=np.linalg.inv(M);q=-iv@T;return im.transform((W,H),Image.Transform.AFFINE,(iv[0,0],iv[0,1],q[0],iv[1,0],iv[1,1],q[1]),Image.Resampling.BICUBIC)
def frag(mask):
 a=r.copy();a[:,:,3]=((a[:,:,3].astype(np.uint16)*np.array(mask).astype(np.uint16)+127)//255).astype('uint8');return Image.fromarray(a)
# Preserve the entire held-object + hand + already-reviewed visible arm cluster together.
block=Image.open(P/'basin_full_repair/candidates/complete_basin_F000_positioned.png').getchannel('A').point(lambda x:255 if x>3 else 0)
for name in ['near_hand_positioned','far_hand_forearm_union_positioned']:
 block=ImageChops.lighter(block,Image.open(P/'preposition'/f'{name}.png').getchannel('A').point(lambda x:255 if x>3 else 0))
near_arm=poly([(686,892),(735,885),(779,891),(783,913),(782,936),(772,955),(746,975),(700,1005),(651,1036),(638,1010),(631,990),(637,971),(662,951),(692,928),(709,917),(705,895)])
block=ImageChops.lighter(block,near_arm).filter(ImageFilter.MaxFilter(3));block.save(D/'masks/held_cluster_source_mask.png')
# Upper-body envelope includes original head, neck and blue shirt; arms held above are excluded.
blue=(r[:,:,2]>r[:,:,0]*1.12)&(r[:,:,0]>63)&(r[:,:,1]>95)&(r[:,:,3]>3)&(yy<1145)&(xx>520)
blue_mask=Image.fromarray((blue*255).astype('uint8')).filter(ImageFilter.MaxFilter(7));blue_mask=Image.fromarray((binary_fill_holes(np.array(blue_mask)>0)*255).astype('uint8'));body_env=poly([(398,335),(905,335),(905,1140),(816,1142),(731,1090),(661,1057),(606,1025),(574,977),(545,881),(541,760),(569,689),(574,664),(436,666)])
head=Image.fromarray((((yy<710)&(xx>390)&(xx<850))*255).astype('uint8'));body=ImageChops.darker(ImageChops.lighter(blue_mask,head),body_env);body=ImageChops.subtract(body,block);body.save(D/'masks/upper_body_source_mask.png')
removed=ImageChops.lighter(body,block);ba=r.copy();ba[:,:,3]=((r[:,:,3].astype(np.uint16)*(255-np.array(removed)).astype(np.uint16)+127)//255).astype('uint8');ba[yy<1035,3]=0;legs=Image.fromarray(ba);legs.save(D/'preposition/fixed_lower_body_with_gaps.png')
pivot=(np.array([929,670.9])-[730,375])/k;theta=math.radians(-11);R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);T=pivot-R@pivot;delta=np.array([-11,3])/k
upper=tf(frag(body),R,T);cluster=tf(frag(block),np.eye(2),delta);upper.save(D/'preposition/upper_body_rotated.png');cluster.save(D/'preposition/held_cluster_translated.png');pre=Image.alpha_composite(Image.alpha_composite(legs,upper),cluster);pre.save(D/'preposition/F008_preposition_NOT_FINAL.png')
# Deliberate connection repair regions; this guide is not a finished frame.
edit=Image.new('L',(W,H));dr=ImageDraw.Draw(edit)
for box in [(620,848,776,961),(493,927,585,1005),(586,982,878,1154),(388,1014,550,1080)]:dr.ellipse(box,fill=255)
# Protected complete held cluster, original head and untouched legs stay out of repaint except join boundary.
protect=np.array(cluster.getchannel('A'));ma=np.array(edit);ma[protect>230]=0;edit=Image.fromarray(ma);edit.save(D/'masks/local_connection_edit_mask_PROPOSAL.png')
white=Image.alpha_composite(Image.new('RGBA',(W,H),'white'),pre);white.convert('RGB').save(D/'preposition/F008_preposition_white.jpg',quality=96)
over=np.zeros((H,W,4),dtype=np.uint8);over[:,:,:3]=[230,50,142];over[:,:,3]=(ma.astype(np.uint16)*105//255).astype('uint8');guide=Image.alpha_composite(white,Image.fromarray(over));gd=ImageDraw.Draw(guide);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
for i,s in enumerate(['F008 PREPOSITION / INPUT PROPOSAL, NOT DRAWN FINAL','F000 locked pixels: torso/head -11deg about seated hip proxy.', 'Whole held basin+hands+visible arms translated -11,+3scene.', 'Pink: sleeve/waist connections and old basin reveal. No rescaling.', 'Hip proxy is construction, not measured anatomy. Legs/seat stay fixed.']):gd.text((20,22+i*27),s,font=font,fill='#26343c')
guide.convert('RGB').save(D/'review/F008_mask_guide.jpg',quality=96)
# Adjacent onion skin: expected whole torso motion, fixed lower body and exact rigid held cluster.
onion=Image.blend(Image.alpha_composite(Image.new('RGBA',(W,H),'white'),raw),white,.5);onion.convert('RGB').save(D/'review/F000_F008_onion.jpg',quality=96)
meta={'status':'PENDING_INPUT_REVIEW_NO_GENERATION','previous_locked_sha256':hashlib.sha256((D/'sources/F000_LOCKED_rgba.png').read_bytes()).hexdigest(),'frozen_commit':'af8bfe2f85f568c77897017d50c752a587d70221','torso_head_rigid_rotation_degrees':-11,'construction_pivot_world':[929,670.9],'held_cluster_translation_scene':[-11,3],'F008_basin_rim_center_world':[857.52,647.81],'F008_near_material_contact_world':[861.72,655.51],'F008_far_material_contact_world':[849.22,638.81],'basin_width_depth_design_scene':[79.1,21.7],'lower_body':'original F000 pixels retained; only old basin exposed area and waist joins may be restored','timing_basis':'F008 code image read for early forward bend only. Previous linear F008 reach sample was NOT frozen; this new mild bend follows slow-start lowering between .2 and .72sec. Exact proposed intermediate pose requires input review.','generation_calls':0};(D/'geometry/F008_proposal.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta))
