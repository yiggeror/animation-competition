from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageFilter,ImageFont
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'F005_input_gate';G=R/'F003_input_gate';src=R/'F003_FINAL_LOCKED/S08_F003_grandma_match_box_RGBA.png';a=Image.open(src).convert('RGBA');origfar=Image.open(R/'F000_FINAL_LOCKED/S08_F000_grandma_match_box_RGBA.png').convert('RGBA');fm=Image.open(G/'masks/F003_far_hand_box_jade_protected.png').convert('L')
# Derive every visible moved near hand pixel from the unique locked F003, using the already verified real hand alpha footprint.
actual=Image.new('RGBA',a.size,0);actual.alpha_composite(Image.open(G/'inputs/F003_source_hand_match_clean_cut_RGBA.png').convert('RGBA'),(48,-9));hmask=actual.getchannel('A');near=a.copy();na=np.array(near);aa=np.array(actual);edge=(aa[:,:,3]>0)&(aa[:,:,3]<255);na[edge,:3]=aa[edge,:3];near=Image.fromarray(na,'RGBA');near.putalpha(hmask);
# Exclude a tiny detached alpha island to the right of the true match head, not its actual antialiased outline.
na=np.array(near);na[744:766,1134:1143,3]=0;near=Image.fromarray(na,'RGBA');hmask=near.getchannel('A');near.save(O/'inputs/F005_source_from_LOCKED_F003_hand_match_RGBA.png');hmask.save(O/'masks/F003_actual_hand_match_source_alpha.png')
# Exact motion from approved F003: head1124,755 ->1074,782; all hand/match pixels rigidly(-50,+27).
delta=(-50,27);placed=Image.new('RGBA',a.size,0);placed.alpha_composite(near,delta);placed.save(O/'inputs/F005_preplaced_hand_match_RGBA.png')
# Remove old near arm and near hand only. Overscan includes the old upper hand rim so no narrow sleeve skin stripe gets frozen.
old=Image.new('L',a.size,0);ImageDraw.Draw(old).polygon([(648,824),(732,787),(796,886),(978,813),(1036,778),(1093,777),(1116,802),(1114,849),(1085,873),(1000,879),(803,985),(775,997),(746,985),(713,950)],fill=255);old=ImageChops.lighter(old,hmask)
pre=np.array(a);pre[np.array(old)>0]=0;pre=Image.fromarray(pre,'RGBA')
# The unchanged far hand was partly occluded by003. Restore its already approved original pixels, not invented fingers.
far=origfar.copy();far.putalpha(ImageChops.multiply(origfar.getchannel('A'),fm));pre.alpha_composite(far);pre.alpha_composite(placed);pre.save(O/'inputs/F005_scene_preplaced_RGBA.png')
white=old.filter(ImageFilter.MaxFilter(7));d=ImageDraw.Draw(white);d.polygon([(643,778),(734,768),(756,805),(801,902),(943,837),(981,863),(971,895),(794,998),(752,997),(719,958),(650,834)],fill=255)
w=np.array(white);actual_protect=np.array(placed.getchannel('A'))>0;w[actual_protect]=0
# Wrist seam only: connects to preserved palm, without regenerating any fingers or grip.
collar=Image.new('L',a.size,0);ImageDraw.Draw(collar).polygon([(941,842),(949,839),(959,890),(950,895),(942,889)],fill=255);w[np.array(collar)>0]=255
w[np.array(fm)>0]=0
# Match protection moves from the F003 exact donor, not from a fresh guessed length.
pm3=Image.open(G/'masks/F003_match_protected.png').convert('L');pm5=Image.new('L',a.size,0);pm5.paste(pm3,delta);w[np.array(pm5)>0]=0
white=Image.fromarray(w);white.save(O/'masks/F005_scene_white_allowed_black_frozen.png');placed.getchannel('A').save(O/'masks/F005_preplaced_hand_match_protected.png');fm.save(O/'masks/F005_far_hand_box_jade_protected.png');pm5.save(O/'masks/F005_match_protected.png')
box=(585,615,1235,1045);pre.crop(box).resize((1300,860),Image.Resampling.LANCZOS).save(O/'inputs/F005_arm_separation_crop_2x_RGBA.png');white.crop(box).resize((1300,860),Image.Resampling.NEAREST).save(O/'inputs/F005_arm_separation_crop_2x_WHITE_MASK.png')
context=Image.new('RGBA',a.size,(244,242,237,255));context.alpha_composite(a);context=Image.blend(Image.new('RGBA',a.size,(244,242,237,255)),context,.32);context.alpha_composite(far);context.alpha_composite(placed);d=ImageDraw.Draw(context);chain=[(668,683),(695,813),(760,951),(951,866)];d.line(chain,fill=(203,60,42,255),width=3)
for x,y in chain:d.ellipse((x-4,y-4,x+4,y+4),fill=(203,60,42,255))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15);d.text((593,624),'STRUCTURE ONLY: after real side scrape, match has separated DOWN-LEFT',fill='black',font=font);d.line([(1124,730),(1092,730),(1074,748)],fill=(203,60,42,255),width=2);d.polygon([(1074,748),(1082,744),(1078,740)],fill=(203,60,42,255));context.crop(box).resize((1300,860),Image.Resampling.LANCZOS).convert('RGB').save(O/'inputs/F005_chain_CONTEXT_ONLY.png')
for label,col in [('light',(244,242,237,255)),('dark',(34,42,53,255))]:
 bg=Image.new('RGBA',a.size,col);bg.alpha_composite(pre)
 for name,bb,z in [('preplaced',box,2),('contact',(925,725,1220,920),4)]:
  q=bg.crop(bb);q.resize((q.width*z,q.height*z),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'{name}_{label}.png')
 ov=np.zeros((1080,1920,4),dtype='uint8');ov[w>0]=[90,225,90,105];bg.alpha_composite(Image.fromarray(ov));bg.crop(box).resize((1300,860),Image.Resampling.LANCZOS).convert('RGB').save(O/'qa'/f'mask_overlay_{label}.png')
contract={'status':'F005_INPUT_GATE_ONLY_NOT_CALLED','actual_native_calls_total_before_F005':4,'source_locked_F003':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'crop_scene_box':box,'uniform_enlargement':2,'whole_hand_match_translation_from_F003':delta,'head_scene':[1074,782],'grip_scene':[1046,819],'wrist_scene':[951,866],'unchanged_visible_match_length':46.4,'edge_extraction':'The unique003 placed layer supplies known foreground colors on fractional alpha edges, avoiding the box color baked under the touching head. Explicit detached island at source1134:1143,744:766 removed; no alpha-threshold trimming of the real contour.','stroke':'F0031124,755 -> edge1092,755 contact32px -> F0051074,782 fully separated left/down','far_hand_reveal':'Restore only same approved F000 far hand/box/jade pixels that F003 near hand temporarily covered; no new far hand invention. Body/near arm source is unique locked F003.','chain_guide':chain,'chain_warning':'Projected targets only, not3D bones or compulsory exact lengths. Preserve natural complete chain and real wrist location.','hard_protection':'Preplaced real near hand/match except wrist seam; full real far hand/box/jade; all black pixels.','allowed':'Near arm/cuff-to-wrist plus old occupancy restoration to blouse/far upperarm/transparent air. No flame baked; later code owns fire/light.'};(O/'geometry/contract.json').write_text(json.dumps(contract,indent=2));print(json.dumps(contract,indent=2))
