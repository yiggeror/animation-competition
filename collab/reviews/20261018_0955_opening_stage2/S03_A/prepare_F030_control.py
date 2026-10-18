from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json
r=Path(__file__).resolve().parent
im=Image.open(r/'originals/S03_F030_call07.png').convert('RGBA');guide=im.copy();W,H=im.size
def maskpoly(pts):
 m=Image.new('L',im.size);ImageDraw.Draw(m).polygon(pts,fill=255);return m
# Exact masks isolate generated material for positional guide; this is not the delivered cel.
lmask=maskpoly([(565,627),(587,614),(618,593),(641,588),(671,599),(700,616),(721,652),(723,675),(702,690),(671,706),(636,705),(600,694),(566,684)])
pmask=maskpoly([(702,661),(726,675),(751,692),(777,718),(795,738),(787,748),(756,742),(729,726),(709,704),(699,678)])
rmask=maskpoly([(886,738),(918,706),(949,689),(978,687),(1015,704),(1051,710),(1088,712),(1111,735),(1108,781),(1090,813),(1050,817),(1017,800),(978,809),(943,815),(913,806),(883,784)])
for m in [lmask,pmask,rmask]:guide.paste((0,0,0,0),(0,0,W,H),m)
left=Image.new('RGBA',im.size);left.paste(im,(0,0),lmask);guide.alpha_composite(left,(40,60))
# Resize actual generated empty-shell pixels uniformly about the contact endpoint.
pr=im.crop((699,661,797,749));pm=pmask.crop((699,661,797,749));pr.putalpha(pm);pr=pr.resize((69,62),Image.Resampling.LANCZOS);guide.alpha_composite(pr,(740,727))
right=Image.new('RGBA',im.size);right.paste(im,(0,0),rmask);guide.alpha_composite(right,(-25,10))
box=(400,530,1250,820);guide.crop(box).save(r/'local_refs/F030_positioned_generated_hands_guide.png')
for n,m in [('left',lmask),('pod',pmask),('right',rmask)]:m.save(r/f'masks/F030_control_{n}_source.png')
(r/'local_refs/F030_control_manifest.json').write_text(json.dumps({'not_deliverable':True,'source':'originals/S03_F030_call07.png','crop_bounds':box,'left_hand_translation':[40,60],'right_hand_translation':[-25,10],'pod_source_box':[699,661,797,749],'pod_output_size':[69,62],'pod_paste':[740,727],'purpose':'Real generated hand and empty pod positioned inside accepted endpoint interval; imagegen must redraw local forearm connections, erase remnants and fill exposed shirt only.'},indent=2))
