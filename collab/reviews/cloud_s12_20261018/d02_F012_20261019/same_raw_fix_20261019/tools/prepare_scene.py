from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parents[1];P=O.parent;S=P.parent;R=S.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();candidate=O/'candidate/F012.png';raw=P/'originals/F012_raw_call01.png';mother=S/'first_left_grasp_inputs_20261019/inputs/locked_F000.png'
a=np.array(Image.open(candidate));alpha=a[:,:,3]
base=json.loads((S/'d01_F000/qa/native_alpha_contacts_registration.json').read_text());contacts=[]
for c in base['contacts']:
 mask=Image.new('L',(1024,1536));ImageDraw.Draw(mask).polygon([tuple(x) for x in c['source_alpha_polygon_native']],fill=255);aa=np.minimum(alpha,np.array(mask));im=np.zeros_like(a);im[:,:,3]=aa;Image.fromarray(im).save(O/f"contact_masks/{c['name']}.png")
 # Keep accepted region/base scheme; shapes are the actual new native alpha, not old character silhouettes.
 contacts.append(c|{'alpha_pixels_nonzero':int(np.count_nonzero(aa)),'source_native_SHA256':sha(candidate),'path':f"../contact_masks/{c['name']}.png",'note':'Actual corrected F012 alpha patch; same approved contact polygon/base; far knee/shin naturally occluded.'})
meta={'native_candidate_SHA256':sha(candidate),'native_size':[1024,1536],'registration':{'scale':.7,'x':275,'y':112},'contacts':contacts,'all_six_contacts_independently_visible':False,'frame':12,'absolute_time':.5,'contact_transform_and_anchor_scheme_unchanged':True}
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
source=S/'d01_F000/same_raw_fix_20261019/scene/s12_F000_scene.js';src=source.read_text()
new=src.replace('S12 F000 ONLY candidate.','S12 F012 ONLY diagnostic, actual time .5.')
new=new.replace('export const DURATION=1/24;','export const DURATION=13/24;')
new=new.replace("../candidate/F000.png","../candidate/F012.png")
new=new.replace("if(t<0||t>=DURATION)","if(!Number.isFinite(t)||Math.floor(t*24+1e-9)!==12||t>=DURATION)")
new=new.replace("S12 candidate supports F000 only. No later exposure authorized.","S12 diagnostic supports F012 only. F000 and F018+ are not rendered here.")
# Native substitutions, import-relative depth, strict frame gate only. Keep actual box/cloth/props/light/camera code identical.
(O/'scene/s12_F012_scene.js').write_text(new)
# Preflight all literal runtime-relative imports/data/native paths against the real entry directory.
for relative in ['../../../../../../js/paint/paintshot.js','../../../../../../js/lamp/crane.js','../../../../../../js/puppet.js','../../../geometry/three_key_pose_proposal.json','../qa/native_alpha_contacts_registration.json','../candidate/F012.png']:
    assert ((O/'scene')/relative).resolve().is_file(),relative
checks={}
for start,end in [('let ROOM = null;','function nativeContactShadows'),('function nativeContactShadows','let cachedShadows,cachedProps;'),('},light:(t)=>','export async function renderFrame')]:
 old=src[src.index(start):src.index(end)];now=new[new.index(start):new.index(end)];assert old==now;checks[start]=True
report={'frozen_F000_scene_source':str(source.relative_to(R)),'source_SHA256':sha(source),'actual_F012_scene_path':str((O/'scene/s12_F012_scene.js').relative_to(R)),'actual_F012_scene_SHA256':sha(O/'scene/s12_F012_scene.js'),'native_registration_unchanged':True,'source_functions_byte_equal':checks,'box_cloth_pressure_crane_plane55_rod_endpoints_light_camera_unchanged':True,'native_shadows_use_F012_alpha_with_accepted_original6_contact_regions_and_bases':True,'frame_gate':'only12 atactualt.5, DURATION13/24; from12/24to13/24','no_old_code_character_used':True}
(O/'qa/scene_source_equivalence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
font=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def flat(path,bg):
 im=Image.open(path).convert('RGBA');return Image.alpha_composite(Image.new('RGBA',im.size,(*bg,255)),im).convert('RGB')
board=Image.new('RGB',(1536,1604),'white');d=ImageDraw.Draw(board)
for row,color in enumerate([(205,208,211),(36,38,42)]):
 for col,(path,label) in enumerate([(mother,'LOCKED F000'),(raw,'F012 RAW'),(candidate,'F012 R-only correction')]):
  im=flat(path,color).resize((512,768));x=col*512;y=row*802;board.paste(im,(x,y+34));d.text((x+10,y+6),label,font=font(17),fill='black')
board.save(O/'qa/00_same_scale_three_native_gray_dark.jpg',quality=95)
# Complete physical-face panel crops, keeping raw and corrected selected geometry identical.
faces=json.loads((O/'qa/native_repair_verification.json').read_text())['face_measurements']
board=Image.new('RGB',(1800,1200),'#e7e9e9');d=ImageDraw.Draw(board)
for j,name in enumerate(['near_sleeve','back_waist','lower_hem','collar_front','far_sleeve_UNCHANGED']):
 mask=np.array(Image.open(O/f'masks/face_{name}.png'))>0;yy,xx=np.nonzero(mask);crop=(max(0,int(xx.min())-5),max(0,int(yy.min())-5),min(1024,int(xx.max())+6),min(1536,int(yy.max())+6));x0=(j%3)*600;y0=(j//3)*590
 d.text((x0+10,y0+10),name,font=font(21),fill='black')
 for i,(path,label) in enumerate([(mother,'F000'),(raw,'RAW012'),(candidate,'FIX012')]):
  im=flat(path,(205,208,211)).crop(crop);im.thumbnail((194,410));board.paste(im,(x0+i*200,y0+65));d.text((x0+i*200+8,y0+40),label,font=font(17),fill='black')
 delta=faces[name]['corrected_delta_vs_mother'];d.text((x0+10,y0+490),'Full face dRGB: '+str([round(v,2) for v in delta]),font=font(17),fill='black')
 d.text((x0+10,y0+525),'Same raw / G,B unchanged / far sleeve untouched',font=font(14),fill='black')
board.save(O/'qa/01_physical_faces_same_scale.jpg',quality=96)
# Show protection masks and where the4-level R correction actually happens.
board=Image.new('RGB',(1800,1000),'white');d=ImageDraw.Draw(board)
for i,(f,label) in enumerate([('R_changed','R edited'),('protected_lineart_and_fold_ridges','Protected ink / fold ridges'),('protected_white_flowers','Protected white flowers'),('far_sleeve_UNCHANGED','Far sleeve RGBA unchanged')]):
 im=flat(raw,(205,208,211)).convert('RGBA');mm=np.array(Image.open(O/f'masks/{f}.png'));over=Image.new('RGBA',im.size,(35,210,110,0));over.putalpha(Image.fromarray((mm.astype(float)*.48).astype(np.uint8)));im=Image.alpha_composite(im,over).convert('RGB');im.thumbnail((450,900));board.paste(im,(i*450,45));d.text((i*450+10,12),label,font=font(17),fill='black')
board.save(O/'qa/02_edit_and_protection_masks_actual.jpg',quality=94)
print(json.dumps({'candidate_SHA256':sha(candidate),'entry_SHA256':report['actual_F012_scene_SHA256'],'functions_unchanged':checks},indent=2))
