from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
b=Path(__file__).resolve().parents[3];o=b/'repairs/d12_pixel_preplace';src=b/'outputs/chew/originals/d11_f25_call03.png';im=Image.open(src).convert('RGBA');a=np.array(im);W,H=im.size;dx,dy=38,28
# Guard follows the true object/body occlusion edge; other outer edges use original alpha.
poly=[(380,455),(475,455),(480,470),(486,490),(502,503),(516,507),(527,558),(535,586),(514,594),(517,607),(521,621),(524,639),(454,639),(380,639)]
guard=Image.new('L',(W,H));ImageDraw.Draw(guard).polygon(poly,fill=255);m=(np.array(guard)>0)&(a[:,:,3]>0)
# Tight row-by-row occlusion contour separates the fruit/hand outline from original blouse.
knots=[(548,521),(550,522),(554,523),(558,524),(562,525),(566,526),(570,528),(574,529),(578,530),(582,531),(584,531),(586,526),(588,520),(590,515),(592,510),(594,510),(598,512),(602,514),(606,516),(610,517),(614,518),(618,519),(622,519),(626,520),(630,521),(634,522),(639,523)]
for yy in range(548,640):
 limit=int(round(np.interp(yy,[k[0] for k in knots],[k[1] for k in knots])))
 m[yy,limit+1:]=False
# Remaining sure-blue/white-flower pixels at the narrow contact seam do not belong to the object.
blue=(a[:,:,2].astype(float)>a[:,:,0]*1.10)&(a[:,:,2].astype(float)>a[:,:,1]*1.10)&(a[:,:,2]>55)
white=(a[:,:,0]>200)&(a[:,:,1]>200)&(a[:,:,2]>220)
seam=np.zeros(m.shape,bool);seam[548:640,510:536]=True
m &= ~(seam&(blue|white))
# Preserve enclosed original white-rind pixels; only exterior connected gaps are cut away.
from collections import deque
inv=~m; exterior=np.zeros(m.shape,bool);q=deque()
for yy,xx in [(450,x) for x in range(370,551)]+[(650,x) for x in range(370,551)]+[(y,370) for y in range(450,651)]+[(y,550) for y in range(450,651)]:
 if inv[yy,xx] and not exterior[yy,xx]:exterior[yy,xx]=True;q.append((yy,xx))
while q:
 yy,xx=q.popleft()
 for ny,nx in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
  if 450<=ny<=650 and 370<=nx<=550 and inv[ny,nx] and not exterior[ny,nx]:exterior[ny,nx]=True;q.append((ny,nx))
box=np.zeros(m.shape,bool);box[450:651,370:551]=True;m |= box&inv&(~exterior)&(a[:,:,3]>0)
source_mask=Image.fromarray((m*255).astype('uint8'));source_mask.save(o/'masks/source_hand_fruit_mask.png')
ys,xs=np.where(m);tm=np.zeros(m.shape,bool);tm[ys+dy,xs+dx]=True;target_mask=Image.fromarray((tm*255).astype('uint8'));target_mask.save(o/'masks/target_hand_fruit_PROTECT.png')
# Clear source pixels; insert the translated exact original RGBA samples, not an alpha-over.
pre=a.copy();pre[m]=[0,0,0,0];foreground=np.zeros_like(a);foreground[ys+dy,xs+dx]=a[ys,xs];pre=np.array(Image.alpha_composite(Image.fromarray(pre),Image.fromarray(foreground)));Image.fromarray(pre).save(o/'references/d12_preplace_full_1670x942.png')
cut=np.zeros_like(a);cut[m]=a[m];Image.fromarray(cut).save(o/'references/source_hand_fruit_isolated_full.png')
tcut=foreground;Image.fromarray(tcut).save(o/'references/target_hand_fruit_exact_pixels_full.png')
# Only old footprint, local arm connection and sleeve opening are eligible for later repair.
repair=source_mask.filter(ImageFilter.MaxFilter(9));rd=ImageDraw.Draw(repair)
rd.polygon([(438,612),(522,608),(591,647),(612,683),(590,712),(557,753),(516,773),(465,766),(431,716)],fill=255)
# Include narrow original cuff connection, not the whole sleeve or torso.
rd.polygon([(518,614),(558,627),(597,661),(609,692),(589,708),(566,693),(543,658)],fill=255)
rr=np.array(repair)>0;rr[tm]=False;repair=Image.fromarray((rr*255).astype('uint8'));repair.save(o/'masks/REPAIR_only_old_footprint_and_connection.png')
lock=~rr;Image.fromarray((lock*255).astype('uint8')).save(o/'masks/LOCK_everything_else.png')
roi=(350,420,720,800)
for name,p in [('d12_preplace_local',o/'references/d12_preplace_full_1670x942.png'),('target_hand_fruit_PROTECT_local',o/'masks/target_hand_fruit_PROTECT.png'),('REPAIR_local',o/'masks/REPAIR_only_old_footprint_and_connection.png')]:Image.open(p).crop(roi).save(o/'references'/f'{name}.png')
# QA visualizations only, never used as the delivered cel.
base=Image.new('RGBA',im.size,(232,232,232,255));base.alpha_composite(Image.fromarray(pre));overlay=Image.new('RGBA',im.size);oa=np.array(overlay);oa[rr]=[255,170,0,90];oa[tm]=[0,180,100,65];overlay=Image.fromarray(oa);qa=Image.alpha_composite(base,overlay);qa.crop(roi).resize((740,760)).save(o/'qa/mask_map_2x.png')
base.crop(roi).resize((740,760)).save(o/'qa/preplace_local_2x.png');Image.new('RGBA',im.size,(210,130,160,255))
iso=Image.new('RGBA',im.size,(210,130,160,255));iso.alpha_composite(Image.fromarray(cut));iso.crop((370,450,550,660)).resize((720,840)).save(o/'qa/source_isolated_4x.png')
red=(a[:,:,0]>150)&(a[:,:,1]<110)&(a[:,:,2]<110)&(a[:,:,3]>220);red[:300]=False;red[:,:350]=False;red[:,550:]=False;yy,xx=np.where(red);newred=(pre[:,:,0]>150)&(pre[:,:,1]<110)&(pre[:,:,2]<110)&(pre[:,:,3]>220);newred[:300]=False;newred[:,:350]=False;newred[:,650:]=False;ny,nx=np.where(newred)
info={'status':'PREPLACE_ONLY_NOT_GENERATED_OR_FINAL','source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'size':[W,H],'translation_xy':[dx,dy],'roi_xyxy':list(roi),'local_size':[370,380],'source_guard_polygon':poly,'contact_row_limits_y_x':knots,'mask_method':'Original alpha within hand-traced body-contact guard plus row-by-row contour; exclude definite blue/white blouse pixels at seam; white mask pixels select exact unresampled source RGBA. No image-generation yet.','protected_pixels':int(tm.sum()),'repair_pixels':int(rr.sum()),'translated_foreground_exact_RGBA_equal':bool(np.array_equal(foreground[ys+dy,xs+dx],a[ys,xs])),'preplace_compositing':'Old source cleared first, then original RGBA foreground alpha-composited at exact +38,+28; AA edges correctly reveal destination background. Exact original RGBA foreground is separately saved.','outside_source_and_target_unchanged':bool(np.array_equal(pre[~(m|tm)],a[~(m|tm)])),'protected_repair_overlap_px':int((rr&tm).sum()),'source_red_centroid':[float(xx.mean()),float(yy.mean())],'target_red_centroid':[float(nx.mean()),float(ny.mean())],'target_red_bbox':[int(nx.min()),int(ny.min()),int(nx.max()),int(ny.max())],'target_wrist_from_source_same_shift':[525,662],'seeds_and_bite':'All source hand/fruit pixels retained; review masks for segmentation edge before freezing.','reintegrate':'Only generated REPAIR mask pixels may replace preplace; all target protection and all pixels outside REPAIR remain exact preplace pixels. Replacement, not transparent alpha-over.','approval_gate':'Wait coordinator/independent visual review before project call21'}
(o/'logs/preplace_manifest.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
